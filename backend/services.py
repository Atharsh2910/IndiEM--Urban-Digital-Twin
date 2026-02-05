import os
import pandas as pd
import numpy as np
import joblib
import geopandas as gpd
from shapely.geometry import Polygon, Point
import google.generativeai as genai
from dotenv import load_dotenv
from scipy.ndimage import gaussian_filter
import json

# Load env variables (API Key)
load_dotenv()

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "heat_risk_model.pkl")
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "city_with_heat_risk.csv")
IT_PARK_PATH = os.path.join(BASE_DIR, "data", "processed", "it_park_impact.csv")

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class ModelService:
    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            if not os.path.exists(MODEL_PATH):
                raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Please run train_models.py first.")
            cls._model = joblib.load(MODEL_PATH)
        return cls._model

class SimulationEngine:
    def __init__(self):
        self.base_df = pd.read_csv(DATA_PATH)
        self.model = ModelService.get_model()
        self.features = ["temperature", "traffic", "pm25", "green_cover"]
        self.n_lat = self.base_df["y"].nunique()
        self.n_lon = self.base_df["x"].nunique()

    def get_prediction(self, year, scenario_type="Before"):
        df = self.base_df.copy()
        years_passed = max(0, year - 2025)
        
        # --- 1. Projections ---
        # Assumptions
        temp_rate = 0.04
        traffic_rate = 1.5
        pm25_rate = 1.0
        green_loss_rate = 0.5
        
        df["temperature"] = df["temperature"] + (years_passed * temp_rate)
        df["traffic"] = df["traffic"] * (1 + (years_passed * (traffic_rate / 100)))
        df["pm25"] = df["pm25"] * (1 + (years_passed * (pm25_rate / 100)))
        df["green_cover"] = df["green_cover"] * (1 - (years_passed * (green_loss_rate / 100)))

        # --- 2. Scenario Impacts ---
        if scenario_type == "After":
            it_park_mask = (df["x"].between(18, 21)) & (df["y"].between(10, 13))
            df.loc[it_park_mask, "temperature"] += 1.5
            df.loc[it_park_mask, "traffic"] += 900
            df.loc[it_park_mask, "pm25"] *= 1.15
            df.loc[it_park_mask, "green_cover"] -= 20
        
        df["traffic"] = df["traffic"].clip(lower=0)
        df["green_cover"] = df["green_cover"].clip(lower=0)
        
        # --- 3. Physics-Based Smoothing (Diffusion) ---
        # Disabled to match Streamlit exactly as requested
        # df = df.sort_values(by=["y", "x"])
        # smooth_cols = ["temperature", "traffic", "pm25"]
        # sigma = 1.2 
        # for col in smooth_cols: ...

        # --- 4. Run Model Prediction ---
        X = df[self.features]
        df["heat_risk_index"] = self.model.predict(X)
        
        return df

    def to_geojson(self, df):
        grid_size = 0.02
        polygons = []
        
        for _, row in df.iterrows():
            lat, lon = row["lat"], row["lon"]
            polygon = Polygon([
                (lon - grid_size/2, lat - grid_size/2),
                (lon + grid_size/2, lat - grid_size/2),
                (lon + grid_size/2, lat + grid_size/2),
                (lon - grid_size/2, lat + grid_size/2)
            ])
            polygons.append(polygon)
            
        gdf = gpd.GeoDataFrame(df, geometry=polygons, crs="EPSG:4326")
        return gdf.to_json() 

    def get_it_park_geojson(self):
        """Generates GeoJSON containing both the Boundary Polygon AND Points."""
        try:
            if not os.path.exists(IT_PARK_PATH):
                return None
            
            df = pd.read_csv(IT_PARK_PATH)
            
            # 1. Create Points
            geometry_points = [Point(xy) for xy in zip(df.lon, df.lat)]
            gdf_points = gpd.GeoDataFrame(df, geometry=geometry_points, crs="EPSG:4326")
            gdf_points["type"] = "Point" # Tag for frontend identification
            
            # 2. Create Boundary (Convex Hull)
            boundary = gdf_points.unary_union.convex_hull
            gdf_boundary = gpd.GeoDataFrame(geometry=[boundary], crs="EPSG:4326")
            gdf_boundary["type"] = "Boundary"
            gdf_boundary["name"] = "Proposed IT Park"

            # 3. Combine
            combined_gdf = pd.concat([gdf_boundary, gdf_points], ignore_index=True)
            
            return combined_gdf.to_json()
        except Exception as e:
            print(f"Error generating IT Park GeoJSON: {e}")
            return None

class ImpactAnalysisEngine:
    @staticmethod
    def analyze_impact(base_df, future_df):
        mask = (future_df["x"].between(18, 21)) & (future_df["y"].between(10, 13))
        
        if not mask.any():
            return {"delta_metrics": {}, "recommendations": [], "severity": "Low"}

        base_zone = base_df.loc[mask]
        future_zone = future_df.loc[mask]
        
        deltas = {
            "temperature_rise": round(future_zone["temperature"].mean() - base_zone["temperature"].mean(), 2),
            "traffic_increase": round(future_zone["traffic"].mean() - base_zone["traffic"].mean(), 0),
            "pm25_worsening": round(future_zone["pm25"].mean() - base_zone["pm25"].mean(), 2),
            "green_cover_loss": round(base_zone["green_cover"].mean() - future_zone["green_cover"].mean(), 1)
        }

        if GEMINI_API_KEY:
            try:
                model = genai.GenerativeModel('gemini-pro')
                prompt = f"""
                You are a City Planner.
                Data:
                Temp Rise: {deltas['temperature_rise']}C
                Traffic: +{deltas['traffic_increase']}
                PM2.5: +{deltas['pm25_worsening']}
                Green Loss: {deltas['green_cover_loss']}%
                
                Provide:
                1. Severity (Low/Moderate/High/Critical)
                2. 3 short, specific mitigation strategies.
                Output JSON: {{ "severity": "...", "recommendations": [...] }}
                """
                response = model.generate_content(prompt)
                clean_text = response.text.replace("```json", "").replace("```", "").strip()
                result = json.loads(clean_text)
                return {"delta_metrics": deltas, "recommendations": result.get("recommendations", []), "severity": result.get("severity", "Moderate")}
            except:
                pass
        
        return {
            "delta_metrics": deltas,
            "recommendations": ["Green buffers", "Traffic management", "Cool roofs"],
            "severity": "Moderate"
        }
