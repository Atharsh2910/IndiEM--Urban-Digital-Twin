import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import box

# ---------------------------------
# Load city data
# ---------------------------------
df = pd.read_csv("data/processed/city_with_heat_risk.csv")

# ---------------------------------
# Grid resolution (AQI-like)
# Smaller = smoother (but heavier)
# ---------------------------------
GRID_SIZE = 0.005  # ~500m

lat_min, lat_max = df.lat.min(), df.lat.max()
lon_min, lon_max = df.lon.min(), df.lon.max()

# ---------------------------------
# Create grid cells
# ---------------------------------
cells = []
for lat in np.arange(lat_min, lat_max, GRID_SIZE):
    for lon in np.arange(lon_min, lon_max, GRID_SIZE):
        cells.append(box(lon, lat, lon+GRID_SIZE, lat+GRID_SIZE))

grid = gpd.GeoDataFrame(geometry=cells, crs="EPSG:4326")

# ---------------------------------
# Inverse Distance Weighting (IDW)
# ---------------------------------
def idw(x, y, values, xi, yi, power=2):
    dist = np.sqrt((x-xi)**2 + (y-yi)**2)
    dist[dist == 0] = 1e-6
    weights = 1 / dist**power
    return np.sum(weights * values) / np.sum(weights)

# ---------------------------------
# Compute values for multiple years
# ---------------------------------
years = [2025, 2030, 2035]

for year in years:
    factor = 1 + 0.02 * (year - 2025) / 5  # gradual increase
    grid[f"heat_{year}"] = grid.centroid.apply(
        lambda p: idw(
            df.lon.values,
            df.lat.values,
            df.predicted_heat_risk.values * factor,
            p.x, p.y
        )
    )

# ---------------------------------
# Save GeoJSON
# ---------------------------------
grid.to_file("data/processed/heat_surface.geojson", driver="GeoJSON")
print("Continuous heat surface generated")
