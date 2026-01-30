# 🌆 Urban Environmental Intelligence Platform – Proof of Concept

## Overview

This repository contains a **Proof of Concept (PoC)** for an **Integrated Urban Environmental Intelligence Platform** inspired by global initiatives such as Singapore’s **Integrated Environmental Modeller (IEM)** and contextualised for **Indian cities**.

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

---

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
git clone https://github.com/<your-username>/<repo-name>.git
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

