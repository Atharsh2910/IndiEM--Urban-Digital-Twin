# IndiEM -- Urban Digital Twin – Proof of Concept

## Overview

This repository contains a **Proof of Concept (PoC)** for the **IndiEM Platform** A unified, predictive urban intelligence platform that integrates physics-based environmental simulations, machine learning, and spatial digital twins to enable climate-resilient, evidence-driven urban planning at city and national scales.

The PoC demonstrates how **machine learning, predictive analytics, spatial modelling, and urban digital twin concepts** can be combined to simulate, analyse, and visualise urban environmental impacts—specifically focusing on **heat risk, air pollution, traffic, and development-induced stress**.

The system enables **scenario-based planning**, allowing users to compare environmental conditions **before and after a proposed development (5-acre IT park)** and across future time horizons.

---

## Key Features

- **Machine Learning–Based Heat Risk Prediction**  
  Trained ML models predict urban heat risk using environmental and mobility features.

- **Predictive Scenario Analysis**  
  Simulation of environmental impacts caused by a proposed IT park under future scenarios.

- **Continuous Spatial Surface Modelling**  
  Uniform, AQI-style spatial heat surfaces without point-based artefacts.

- **Urban Digital Twin (2D Spatial Representation)**  
  City represented as a spatial grid mapped to geographic coordinates.

- **Interactive GIS Dashboard (OpenStreetMap-Based)**  
  - Feature-specific layers (Heat Risk, Traffic, PM2.5, Temperature)  
  - Year slider (2025–2040)  
  - Scenario slider (Before vs After construction)  
  - AQI-style comparative legend  
  - IT park boundary footprint  
  - Policy recommendation overlays  

- **Decision-Support–Oriented Visualisation**  
  Designed to support planners, policymakers, and urban designers.

---

## Project Structure

```text
.
├── dashboard/
│   └── app.py
│
├── data/
│   ├── raw/
│   │   └── city_grid_raw.csv
│   └── processed/
│       ├── city_with_heat_risk.csv
│       ├── it_park_impact.csv
│       └── heat_surface.geojson
│
├── models/
│   └── heat_risk_model.pkl
│
├── src/
│   ├── generate_data.py
│   ├── train_models.py
│   ├── simulate_it_park.py
│   ├── add_latlon.py
│   ├── build_surface.py
│   └── utils.py
│
├── requirements.txt
└── README.md



```
## Technology Stack

- **Programming & Analytics**: Python, NumPy, Pandas  
- **Machine Learning**: Scikit-learn, Joblib  
- **Geospatial & GIS**: GeoPandas, Shapely, PyProj, Fiona  
- **Visualization & Mapping**: Folium, OpenStreetMap  
- **Web Application**: Streamlit, streamlit-folium  
- **Data Formats**: CSV, GeoJSON  

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Atharsh2910/IndiEM--Urban-Digital-Twin.git
cd <repo-name>

python -m venv venv
source venv/bin/activate  # Linux / macOS
venv\Scripts\activate     # Windows

pip install -r requirements.txt

python src/generate_data.py
python src/train_models.py
python src/simulate_it_park.py
python src/add_latlon.py
python src/build_surface.py
streamlit run dashboard/app.py

## Using the Dashboard

Once the application is launched, the dashboard provides the following controls
and visualisations:

- **Feature Selector**  
  Choose between Heat Risk, Traffic, PM2.5, or Temperature layers.

- **Year Slider**  
  Explore future scenarios from **2025 to 2040**.

- **Scenario Slider**  
  Toggle between **Before Construction** and **After Construction** conditions.

- **Map View**  
  OpenStreetMap-based GIS view with a continuous, AQI-style surface.

- **Overlays**
  - IT park boundary footprint
  - Policy recommendation zones

- **Legend**  
  Percentile-based comparative colour scale (Green → Yellow → Orange → Red → Dark Red)

## Future Enhancements

The following enhancements are planned for future iterations of the platform:

- 3D urban digital twin integration for volumetric analysis
- Flood and monsoon risk modelling using hydrological simulations
- Real-time IoT sensor ingestion and streaming analytics
- Physics-based CFD simulations for airflow and pollutant dispersion
- Multi-city and regional-scale deployment framework
- Policy impact scoring and automated compliance reporting
