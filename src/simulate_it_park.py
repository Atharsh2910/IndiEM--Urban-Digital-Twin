import os
import pandas as pd
import numpy as np
import joblib

# -------------------------------
# Paths (Kaggle-safe)
# -------------------------------
BASE_PATH = "/kaggle/working"   # change to "." if running locally

MODEL_PATH = f"{BASE_PATH}/models/heat_risk_model.pkl"
DATA_PATH = f"{BASE_PATH}/data/processed/city_with_heat_risk.csv"
OUTPUT_PATH = f"{BASE_PATH}/data/processed/it_park_impact.csv"

os.makedirs(f"{BASE_PATH}/data/processed", exist_ok=True)

# Load trained model
model = joblib.load(MODEL_PATH)

# Load processed city dataset
df = pd.read_csv(DATA_PATH)

it_park = df[
    (df["x"].between(18, 21)) &
    (df["y"].between(10, 13))
].copy()

# -------------------------------
# Future impact assumptions
# -------------------------------
it_park["future_temperature"] = it_park["temperature"] + 1.5
it_park["future_traffic"] = it_park["traffic"] + 900
it_park["future_pm25"] = it_park["pm25"] * 1.15
it_park["future_green_cover"] = it_park["green_cover"] - 20

FEATURES = ["temperature", "traffic", "pm25", "green_cover"]

X_future = pd.DataFrame({
    "temperature": it_park["future_temperature"],
    "traffic": it_park["future_traffic"],
    "pm25": it_park["future_pm25"],
    "green_cover": it_park["future_green_cover"]
})

# Enforce correct order
X_future = X_future[FEATURES]

it_park["future_heat_risk"] = model.predict(X_future)

print("Model expects :", model.feature_names_in_)
print("Provided data :", X_future.columns.tolist())

HIGH_RISK = df["heat_risk_index"].quantile(0.8)
MED_RISK = df["heat_risk_index"].quantile(0.6)

def planning_decision(row):
    if row["future_heat_risk"] > HIGH_RISK:
        return "High risk – redesign with strong mitigation"
    elif row["future_heat_risk"] > MED_RISK:
        return "Moderate risk – green buffers & traffic control needed"
    else:
        return "Acceptable with standard measures"

it_park["planning_decision"] = it_park.apply(planning_decision, axis=1)

it_park.to_csv(OUTPUT_PATH, index=False)

print("IT Park impact simulation completed successfully")
print(f"Saved to: {OUTPUT_PATH}")
