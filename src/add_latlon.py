import pandas as pd

# -----------------------------
# Chennai-like bounding box
# -----------------------------
LAT_MIN, LAT_MAX = 12.90, 13.15
LON_MIN, LON_MAX = 80.10, 80.35

# -----------------------------
# City-wide dataset
# -----------------------------
city = pd.read_csv("data/processed/city_with_heat_risk.csv")

city["lat"] = LAT_MIN + (city["y"] / city["y"].max()) * (LAT_MAX - LAT_MIN)
city["lon"] = LON_MIN + (city["x"] / city["x"].max()) * (LON_MAX - LON_MIN)

city.to_csv("data/processed/city_with_heat_risk.csv", index=False)
print("Lat/Lon added to city dataset")

# -----------------------------
# IT park dataset
# -----------------------------
it = pd.read_csv("data/processed/it_park_impact.csv")

it["lat"] = LAT_MIN + (it["y"] / city["y"].max()) * (LAT_MAX - LAT_MIN)
it["lon"] = LON_MIN + (it["x"] / city["x"].max()) * (LON_MAX - LON_MIN)

it.to_csv("data/processed/it_park_impact.csv", index=False)
print("Lat/Lon added to IT park dataset")
