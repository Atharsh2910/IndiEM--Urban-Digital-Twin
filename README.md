# IndiEM -- Urban Digital Twin – Proof of Concept

## Overview

This repository contains a **Proof of Concept (PoC)** for the **IndiEM Platform**, A unified predictive urban intelligence platform that integrates physics-based environmental simulations, machine learning, and spatial digital twins to enable climate-resilient, evidence-driven urban planning at city and national scales.

The PoC demonstrates how **machine learning, predictive analytics, spatial modelling, and urban digital twin concepts** can be combined to simulate, analyse, and visualise urban environmental impacts—specifically focusing on **heat risk, air pollution, traffic, and development-induced stress**.

The system enables **scenario-based planning**, allowing users to compare environmental conditions **before and after a proposed development (5-acre IT park)** and across future time horizons.

## Intended Users

- Urban planners evaluating development proposals
- Policy teams assessing long-term environmental impact
- Smart city cells exploring predictive planning tools
- Researchers studying urban climate interactions

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
├── backend/                # Flask Backend & HTML App
│   ├── app.py              # Backend Service
│   ├── services.py         # Business Logic & Simulation
│   ├── templates/          # HTML Templates (index.html)
│   └── static/             # JS/CSS Assets
│
├── dashboard/              # Streamlit Dashboard (Urban Planner View)
│   ├── app.py              # Dashboard Application
│   ├── cesium_view.html    # 3D Digital Twin Viewer
│   └── cesium_data/        # 3D Data Assets
│
├── data/                   # Data Storage
│   ├── raw/                # Original Inputs
│   └── processed/          # Simulated Outputs
│
├── models/                 # ML Models
│   └── heat_risk_model.pkl
│
├── src/                    # Utility Scripts
│   ├── generate_data.py    # Synthetic Data Generator
│   ├── train_models.py     # Model Training
│   ├── simulate_it_park.py # Scenario Simulation
│   ├── add_latlon.py       # Geocoding
│   └── build_surface.py    # Surface Generation
│
├── requirements.txt        # Dependencies
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
cd IndiEM--Urban-Digital-Twin
```

### 2. Environment Setup

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Initialize Data & Models
```bash
python src/generate_data.py
python src/train_models.py
python src/simulate_it_park.py
python src/add_latlon.py
python src/build_surface.py
```

### 4. Run the Application
Open **two separate terminals** to run both components simultaneously.

**Terminal 1: Backend Server (HTMl App & API)**
```bash
python backend/app.py
```
*Port 5000 is used for the API and HTML app.*

**Terminal 2: Streamlit Dashboard**
```bash
streamlit run dashboard/app.py
```
*Port 8501 is used for the Dashboard.*

### 5. Access the Platform
- **HTML App:** http://localhost:5000
- **Planner Dashboard:** http://localhost:8501
```
```
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

## Screenshots
---
<img width="1383" height="834" alt="image" src="https://github.com/user-attachments/assets/2d833fa9-c354-4b59-944d-1c8d3e86c806" />
<img width="1567" height="809" alt="image" src="https://github.com/user-attachments/assets/a46a9522-d8b1-480f-8b05-54e54fba7db4" />
<img width="437" height="800" alt="image" src="https://github.com/user-attachments/assets/3398f9b5-1bb6-4c4d-bbcd-3d2bd2feda39" />
<img width="1859" height="800" alt="image" src="https://github.com/user-attachments/assets/bd3788ce-efbe-47e4-ae5b-0829b9bc0b87" />
<img width="1522" height="780" alt="image" src="https://github.com/user-attachments/assets/bcaead5b-36d4-4022-8e73-d076382fa536" />
<img width="1863" height="767" alt="image" src="https://github.com/user-attachments/assets/b5202f3d-7523-4543-b1e2-c70891eeecc0" />
---


##Deployed Link
[IndiEM: ](https://indiem-urban-digital-twin.onrender.com)

## Future Enhancements

The following enhancements are planned for future iterations of the platform:

- 3D urban digital twin integration for volumetric analysis
- Flood and monsoon risk modelling using hydrological simulations
- Real-time IoT sensor ingestion and streaming analytics
- Physics-based CFD simulations for airflow and pollutant dispersion
- Multi-city and regional-scale deployment framework
- Policy impact scoring and automated compliance reporting
