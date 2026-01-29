import os
import numpy as np
import pandas as pd
import joblib
import shutil

from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

BASE_PATH = "/kaggle/working"

RAW_DATA_PATH = f"{BASE_PATH}/data/raw/city_grid_raw.csv"
MODEL_DIR = f"{BASE_PATH}/models"
PROCESSED_DIR = f"{BASE_PATH}/data/processed"

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

df = pd.read_csv(RAW_DATA_PATH)

df["heat_risk_index"] = (
    0.45 * df["temperature"] +
    0.25 * (df["traffic"] / df["traffic"].max()) +
    0.20 * (df["pm25"] / df["pm25"].max()) -
    0.30 * (df["green_cover"] / df["green_cover"].max()) +
    np.random.normal(0, 0.05, len(df))
)

FEATURES = ["temperature", "traffic", "pm25", "green_cover"]

X = df[FEATURES]
y = df["heat_risk_index"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

model = GradientBoostingRegressor(
    n_estimators=500,
    learning_rate=0.04,
    max_depth=3,
    subsample=0.8,
    random_state=42
)

model.fit(X_train, y_train)

from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np

# Predictions
y_pred = model.predict(X_test)

# Metrics (Kaggle-safe)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("FINAL MODEL EVALUATION\n")
print(f"MSE  : {mse:.3f}")
print(f"RMSE : {rmse:.3f}")
print(f"MAE  : {mae:.3f}")
print(f"R²   : {r2:.3f}")

print("FINAL MODEL EVALUATION\n")
print(f"RMSE : {rmse:.3f}")
print(f"MAE  : {mae:.3f}")
print(f"R²   : {r2:.3f}")

# Predict for full city
df["predicted_heat_risk"] = model.predict(X)

# Save model
joblib.dump(
    model,
    f"{MODEL_DIR}/heat_risk_model.pkl"
)

# Save processed dataset
df.to_csv(
    f"{PROCESSED_DIR}/city_with_heat_risk.csv",
    index=False
)

print("\nModel and processed dataset saved")
