import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import os
import json
import pandas as pd

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(
    page_title="Chennai City – Urban Intelligence Platform",
    layout="wide"
)

st.title("🗺️ Chennai City – Urban Environmental Digital Twin")

# -------------------------------------------------
# Paths
# -------------------------------------------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SURFACE_PATH = os.path.join(ROOT_DIR, "data", "processed", "heat_surface.geojson")
IT_PARK_PATH = os.path.join(ROOT_DIR, "data", "processed", "it_park_impact.csv")

# -------------------------------------------------
# Load data
# -------------------------------------------------
surface = gpd.read_file(SURFACE_PATH)

it_df = pd.read_csv(IT_PARK_PATH)
it_park = gpd.GeoDataFrame(
    it_df,
    geometry=gpd.points_from_xy(it_df.lon, it_df.lat),
    crs="EPSG:4326"
)

# Precompute IT park boundary ONCE
it_park_boundary = it_park.unary_union.convex_hull

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
# Metric selection
# -------------------------------------------------
if feature == "Heat Risk":
    metric = metric = f"heat_{year}"

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
    st.subheader("🌍 3D Urban Digital Twin (CesiumJS)")

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
    st.subheader(f"🌆 Spatial Impact Map ({scenario} Construction)")

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
            "fillOpacity": 0.65
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
                "fillOpacity": 0.05
            },
            tooltip="Proposed 5-Acre IT Park Boundary"
        ).add_to(m)

        for _, row in it_park.iterrows():
            folium.Circle(
                location=[row.geometry.y, row.geometry.x],
                radius=500,
                color="green",
                fill=True,
                fill_opacity=0.15,
                popup="Policy: Green buffer & tree plantation"
            ).add_to(m)

            folium.Circle(
                location=[row.geometry.y, row.geometry.x],
                radius=300,
                color="blue",
                fill=True,
                fill_opacity=0.12,
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
# Summary & Conclusion
# -------------------------------------------------
st.subheader("📌 Policy Recommendations")

if scenario == "After":
    st.markdown("""
    **Recommended Interventions:**
    - 🌳 Establish green buffers around the IT park
    - 🚦 Implement traffic demand management
    - 🏢 Encourage reflective roofing & passive cooling
    - 🌬️ Improve ventilation corridors
    """)
else:
    st.info("Switch to **After Construction** to view policy interventions.")

st.success(
    "IndiEM – A digital twin–driven urban intelligence platform enabling "
    "data-backed, predictive, and climate-resilient planning decisions."
)
