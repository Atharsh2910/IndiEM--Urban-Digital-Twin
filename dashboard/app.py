import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import os
import json
import pandas as pd
import requests

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(
    page_title="Chennai City – Urban Intelligence Platform",
    layout="wide"
)

st.title("🗺️ Chennai City – Urban Environmental Digital Twin")

# -------------------------------------------------
# Paths & Config
# -------------------------------------------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
API_URL = "http://localhost:5000/api/predictions"
IT_PARK_PATH = os.path.join(ROOT_DIR, "data", "processed", "it_park_impact.csv")

# -------------------------------------------------
# Sidebar controls
# -------------------------------------------------
st.sidebar.header("Controls")

feature = st.sidebar.selectbox(
    "Feature Layer",
    ["Heat Risk", "Traffic", "PM2.5", "Temperature"]
)

year = st.sidebar.slider(
    "Year",
    min_value=2025,
    max_value=2040,
    step=5,
    value=2025
)

scenario_slider = st.sidebar.slider(
    "Construction Scenario",
    min_value=0,
    max_value=1,
    value=0,
    help="0 = Before construction | 1 = After construction"
)

scenario = "After" if scenario_slider == 1 else "Before"

view_mode = st.sidebar.radio(
    "View Mode",
    ["2D Map", "3D Digital Twin"]
)

# -------------------------------------------------
# Load data from API
# -------------------------------------------------
@st.cache_data(ttl=60) # Cache for 60 seconds to avoid spamming the API on every interaction that doesn't change params
def fetch_data(year, scenario):
    try:
        response = requests.get(API_URL, params={"year": year, "scenario": scenario})
        if response.status_code == 200:
            return gpd.read_file(response.text, driver="GeoJSON")
        else:
            st.error(f"Error fetching data: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Backend not reachable. Please run `python backend/app.py`.")
        return None

surface = fetch_data(year, scenario)

if surface is None:
    st.stop()

# -------------------------------------------------
# Load IT Park Data (Static for boundary)
# -------------------------------------------------
# We still load this for the boundary visualization, though we could/should arguably extract this from the API too 
# if we wanted to be 100% clean, but for now we keep the hybrid approach to minimize regression risk on the overlay.
it_df = pd.read_csv(IT_PARK_PATH)
it_park = gpd.GeoDataFrame(
    it_df,
    geometry=gpd.points_from_xy(it_df.lon, it_df.lat),
    crs="EPSG:4326"
)
it_park_boundary = it_park.unary_union.convex_hull

# -------------------------------------------------
# Metric selection
# -------------------------------------------------
# API returns current state in standard columns, so we don't need "heat_2030" style columns anymore.
# The API returns 'heat_risk_index', 'traffic', 'pm25', 'temperature' adjusted for the year.
if feature == "Heat Risk":
    metric = "heat_risk_index"
elif feature == "Traffic":
    metric = "traffic"
elif feature == "PM2.5":
    metric = "pm25"
else:
    metric = "temperature"

# -------------------------------------------------
# Prepare 3D height (Z dimension)
# -------------------------------------------------
surface_3d = surface.copy()

min_v = surface_3d[metric].min()
max_v = surface_3d[metric].max()

surface_3d["height"] = (
    (surface_3d[metric] - min_v) / (max_v - min_v + 1e-6)
) * 300  # meters

CESIUM_DIR = os.path.join(ROOT_DIR, "dashboard", "cesium_data")
os.makedirs(CESIUM_DIR, exist_ok=True)

# For Cesium, we need to save the file locally as the HTML file reads it relative
# We will overwrite this file based on current selection
surface_3d["height"] = surface_3d[metric]
surface_3d.to_file(
    os.path.join(CESIUM_DIR, "heat_surface.geojson"),
    driver="GeoJSON"
)

# IT park boundary
it_gdf = gpd.GeoDataFrame(
    {"name": ["IT Park"]},
    geometry=[it_park_boundary],
    crs="EPSG:4326"
)

it_gdf.to_file(
    os.path.join(CESIUM_DIR, "it_park_boundary.geojson"),
    driver="GeoJSON"
)

if view_mode == "3D Digital Twin":
    st.subheader(f"🌍 3D Urban Digital Twin (Year: {year} | {scenario})")
    st.info("The 3D view consumes the generated GeoJSON. Refresh browser if Cesium doesn't update immediately.")

    cesium_html_path = os.path.join(
        ROOT_DIR, "dashboard", "cesium_view.html"
    )

    with open(cesium_html_path, "r", encoding="utf-8") as f:
        cesium_html = f.read()

    st.components.v1.html(
        cesium_html,
        height=750,
        scrolling=False
    )


# -------------------------------------------------
# 2D MAP VIEW (FOLIUM)
# -------------------------------------------------
else:
    st.subheader(f"🌆 Spatial Impact Map ({year} | {scenario})")

    center_lat = surface.geometry.centroid.y.mean()
    center_lon = surface.geometry.centroid.x.mean()

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles="OpenStreetMap"
    )

    # Quantile thresholds
    q20 = surface[metric].quantile(0.20)
    q40 = surface[metric].quantile(0.40)
    q60 = surface[metric].quantile(0.60)
    q80 = surface[metric].quantile(0.80)

    def style_function(feature_json):
        v = feature_json["properties"][metric]

        if v <= q20:
            color = "#2ECC71"
        elif v <= q40:
            color = "#F1C40F"
        elif v <= q60:
            color = "#E67E22"
        elif v <= q80:
            color = "#E74C3C"
        else:
            color = "#7B241C"

        return {
            "fillColor": color,
            "color": None,
            "weight": 0,
            "fillOpacity": 0.05
        }

    folium.GeoJson(
        surface,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=[metric],
            aliases=[feature]
        )
    ).add_to(m)

    if scenario == "After":
        folium.GeoJson(
            it_park_boundary,
            style_function=lambda _: {
                "fillColor": "#000000",
                "color": "#000000",
                "weight": 4,
                "fillOpacity": 0.80
            },
            tooltip="Proposed 5-Acre IT Park Boundary"
        ).add_to(m)

        for _, row in it_park.iterrows():
            folium.Circle(
                location=[row.geometry.y, row.geometry.x],
                radius=500,
                color="green",
                fill=True,
                fill_opacity=0.50,
                popup="Policy: Green buffer & tree plantation"
            ).add_to(m)

            folium.Circle(
                location=[row.geometry.y, row.geometry.x],
                radius=300,
                color="blue",
                fill=True,
                fill_opacity=0.50,
                popup="Policy: Traffic demand management"
            ).add_to(m)

    legend_html = f"""
    <div style="
    position: fixed;
    bottom: 30px;
    left: 30px;
    width: 280px;
    background-color: white;
    color: black;
    padding: 14px;
    border-radius: 8px;
    box-shadow: 3px 3px 10px rgba(0,0,0,0.4);
    z-index:9999;
    font-size:14px;
    ">
    <b>{feature} – Comparative Scale</b><br><br>
    <span style="color:#2ECC71;">■</span> Low (≤20%)<br>
    <span style="color:#F1C40F;">■</span> Moderate (20–40%)<br>
    <span style="color:#E67E22;">■</span> Elevated (40–60%)<br>
    <span style="color:#E74C3C;">■</span> High (60–80%)<br>
    <span style="color:#7B241C;">■</span> Extreme (>80%)<br>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    st_folium(m, width=1400, height=720)

# -------------------------------------------------
# AI Impact Analysis & Suggestions
# -------------------------------------------------
st.subheader("🤖 AI-Driven Impact Analysis & Policy Recommendations")

ANALYSIS_API_URL = "http://localhost:5000/api/impact-analysis"

if scenario == "After":
    # Fetch AI Analysis
    try:
        res = requests.get(ANALYSIS_API_URL, params={"year": year})
        if res.status_code == 200:
            analysis = res.json()
            
            # --- 1. Display Delta Metrics ---
            metrics = analysis["delta_metrics"]
            
            if metrics:
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Temp Rise (IT Park)", f"+{metrics['temperature_rise']} °C", delta_color="inverse")
                c2.metric("Traffic Surge", f"+{metrics['traffic_increase']} vehicles", delta_color="inverse")
                c3.metric("PM2.5 Worsening", f"+{metrics['pm25_worsening']} µg/m³", delta_color="inverse")
                c4.metric("Green Cover Loss", f"-{metrics['green_cover_loss']} %", delta_color="inverse")
            
            st.divider()
            
            # --- 2. Display Severity & Suggestions ---
            severity = analysis["severity"]
            
            if "High Impact" in severity:
                st.error(f"**Impact Level: {severity}**")
            elif "Moderate" in severity:
                st.warning(f"**Impact Level: {severity}**")
            else:
                st.info(f"**Impact Level: {severity}**")
            
            st.markdown("### 📋 Generated Mitigation Strategies")
            
            for rec in analysis["recommendations"]:
                st.info(f"🔹 {rec}")
                
        else:
            st.error(f"Failed to fetch analysis: {res.text}")
            
    except Exception as e:
        st.error(f"Error connecting to AI engine: {e}")

else:
    st.info("Switch to **After Construction** to view the AI-generated impact analysis.")

st.success(
    "IndiEM – A digital twin–driven urban intelligence platform enabling "
    "data-backed, predictive, and climate-resilient planning decisions."
)
