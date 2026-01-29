import joblib
import pandas as pd

# -------------------------------------------------
# Global feature definition (DO NOT CHANGE)
# -------------------------------------------------
FEATURES = ["temperature", "traffic", "pm25", "green_cover"]

# -------------------------------------------------
# Load trained ML model
# -------------------------------------------------
def load_model(model_path: str):
    """
    Load trained heat risk model from disk.
    """
    return joblib.load(model_path)

# -------------------------------------------------
# Build feature matrix safely
# -------------------------------------------------
def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure correct feature names and order
    for ML prediction.
    """
    return df[FEATURES]

# -------------------------------------------------
# Predict heat risk index
# -------------------------------------------------
def predict_heat_risk(model, df: pd.DataFrame):
    """
    Predict heat risk index using trained model.
    """
    X = build_feature_matrix(df)
    return model.predict(X)

# -------------------------------------------------
# Risk classification helper
# -------------------------------------------------
def classify_risk(value, low_threshold, high_threshold):
    if value >= high_threshold:
        return "High"
    elif value >= low_threshold:
        return "Medium"
    else:
        return "Low"
