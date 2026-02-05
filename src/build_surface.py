import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
import os

# -----------------------------
# Paths
# -----------------------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INPUT_CSV = os.path.join(ROOT_DIR, "data", "processed", "city_with_heat_risk.csv")
OUTPUT_GEOJSON = os.path.join(ROOT_DIR, "data", "processed", "heat_surface.geojson")

# -----------------------------
# Load data
# -----------------------------
df = pd.read_csv(INPUT_CSV)

# -----------------------------
# Year projections (synthetic)
# -----------------------------
BASE_YEAR = 2025
YEARS = [2025, 2030, 2035, 2040]

for year in YEARS:
    growth_factor = 1 + (year - BASE_YEAR) * 0.03
    df[f"heat_{year}"] = df["heat_risk_index"] * growth_factor

# -----------------------------
# Grid size (degrees)
# -----------------------------
GRID_SIZE = 0.02  # ~2 km

polygons = []

for _, row in df.iterrows():
    lat = row["lat"]
    lon = row["lon"]

    polygon = Polygon([
        (lon - GRID_SIZE / 2, lat - GRID_SIZE / 2),
        (lon + GRID_SIZE / 2, lat - GRID_SIZE / 2),
        (lon + GRID_SIZE / 2, lat + GRID_SIZE / 2),
        (lon - GRID_SIZE / 2, lat + GRID_SIZE / 2)
    ])

    polygons.append(polygon)

# -----------------------------
# Create GeoDataFrame
# -----------------------------
gdf = gpd.GeoDataFrame(
    df,
    geometry=polygons,
    crs="EPSG:4326"
)

# -----------------------------
# Save GeoJSON
# -----------------------------
os.makedirs(os.path.dirname(OUTPUT_GEOJSON), exist_ok=True)
gdf.to_file(OUTPUT_GEOJSON, driver="GeoJSON")

print("✅ heat_surface.geojson created with year-wise attributes")
