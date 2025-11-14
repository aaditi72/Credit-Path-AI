# inference.py
import joblib
import pandas as pd
from pathlib import Path
import logging

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Paths
MODEL_DIR = Path("models")

MODEL_PATH = MODEL_DIR / "xgb_grid_tuned_v1.pkl"
SCALER_PATH = MODEL_DIR / "scaler_v1.pkl"
FEATURE_PATH = MODEL_DIR / "final_features_63.pkl"
SUBGRADE_MAP_PATH = MODEL_DIR / "sub_grade_mapping.pkl"


# ===========================================================
# Load artifacts
# ===========================================================
try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    final_features = joblib.load(FEATURE_PATH)
    subgrade_map = joblib.load(SUBGRADE_MAP_PATH)

    logging.info("✔ Loaded model, scaler, feature list, and sub-grade mapping.")

except Exception as e:
    logging.error(f"🔥 ERROR loading ML artifacts: {e}")
    raise RuntimeError(f"Failed to load ML model files: {e}")


# ===========================================================
# Preprocessing function
# ===========================================================
def preprocess_input(data: dict):
    df = pd.DataFrame([data])

    # Convert sub-grade (string → number)
    raw_subgrade = df.loc[0, "sub_grade"]
    if raw_subgrade not in subgrade_map:
        raise ValueError(
            f"Invalid sub_grade '{raw_subgrade}'. Allowed: {list(subgrade_map.keys())}"
        )
    df["sub_grade"] = subgrade_map[raw_subgrade]

    # Add derived features
    df["credit_utilization_ratio"] = df["revol_util"] / 100.0
    df["loan_to_income_ratio"] = df["loan_amnt"] / (df["annual_inc"] + 1)

    # Make sure all final features exist
    for col in final_features:
        if col not in df.columns:
            df[col] = 0

    # Select correct feature order
    df = df[final_features]

    # Convert numeric
    df = df.apply(pd.to_numeric, errors="coerce").fillna(0)

    return df


# ===========================================================
# Predict default probability
# ===========================================================
def predict_default_probability(data: dict) -> float:
    """
    Takes raw input JSON → preprocess → scale → predict.
    Returns probability of default as float.
    """
    try:
        df = preprocess_input(data)
        scaled = scaler.transform(df)
        prob = model.predict_proba(scaled)[0][1]
        return float(prob)

    except Exception as e:
        logging.error(f"🔥 Prediction error: {e}")
        raise RuntimeError(f"Prediction failed: {e}")
