Overview:
This repository contains a Proof of Concept (PoC) for an Integrated Urban Environmental Intelligence Platform inspired by global initiatives such as Singapore’s Integrated Environmental Modeller (IEM), and contextualised for Indian cities.

The PoC demonstrates how machine learning, predictive analytics, spatial modelling, and digital twin concepts can be combined to simulate, analyse, and visualise urban environmental impacts—specifically focusing on heat risk, air pollution, traffic, and development-induced stress.

The system enables scenario-based planning, allowing users to compare conditions before and after a proposed development (5-acre IT park) and across future time horizons.

Key Features


Machine Learning–Based Heat Risk Prediction
Trained ML models predict urban heat risk using environmental and mobility features.

Predictive Scenario Analysis
Simulates environmental impacts of a proposed IT park under future scenarios.

Continuous Spatial Surface Modelling
Uniform, AQI-style spatial heat surfaces (no point-based artifacts).

Urban Digital Twin (2D Spatial)
City represented as a spatial grid mapped to geographic coordinates.

Interactive GIS Dashboard (OpenStreetMap)

Feature-specific layers (Heat Risk, Traffic, PM2.5, Temperature)

Year slider (2025–2040)

Scenario slider (Before vs After construction)

Clear AQI-style legend

IT park boundary footprint

Policy recommendation overlays

Decision-Support Oriented Visualisation
Designed for planners, policymakers, and urban designers

Project Structure
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

Technology Stack

Programming & Analytics: Python, NumPy, Pandas

Machine Learning: Scikit-learn, Joblib

Geospatial & GIS: GeoPandas, Shapely, PyProj, Fiona

Visualization & Mapping: Folium, OpenStreetMap

Web Application: Streamlit, streamlit-folium

Data Formats: CSV, GeoJSON
