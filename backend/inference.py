# inference.py
import joblib
import pandas as pd
from pathlib import Path
import logging

# Logging Setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

MODEL_DIR = Path("models")

MODEL_PATH = MODEL_DIR / "model_lgbm_tuned.pkl"
SCALER_PATH = MODEL_DIR / "scaler.pkl"
FEATURES_PATH = MODEL_DIR / "final_features.pkl"
SUBGRADE_MAP_PATH = MODEL_DIR / "subgrade_mapping.pkl"

# -------------------- LOAD ARTIFACTS --------------------
try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    final_features = joblib.load(FEATURES_PATH)
    subgrade_map = joblib.load(SUBGRADE_MAP_PATH)

    logging.info("✔ Loaded LightGBM model, scaler, features, and sub-grade mapping.")

except Exception as e:
    logging.error(f"🔥 ERROR loading model artifacts: {e}")
    raise RuntimeError(f"Failed to load required model files: {e}")


# -------------------- PREPROCESS INPUT --------------------
def preprocess_input(data: dict):
    df = pd.DataFrame([data])

    # Validate sub_grade
    sg = df.loc[0, "sub_grade"]
    if sg not in subgrade_map:
        raise ValueError(
            f"Invalid sub_grade '{sg}'. Allowed values: {list(subgrade_map.keys())}"
        )

    df["sub_grade"] = subgrade_map[sg]

    # Derived features (must match training logic)
    df["credit_utilization_ratio"] = df["revol_util"] / 100.0
    df["loan_to_income_ratio"] = df["loan_amnt"] / (df["annual_inc"] + 1)

    # Ensure all final_features exist
    for col in final_features:
        if col not in df.columns:
            df[col] = 0

    df = df[final_features]

    df = df.apply(pd.to_numeric, errors="coerce").fillna(0)

    return df


# -------------------- PREDICT PROBABILITY --------------------
def predict_default_probability(data: dict) -> float:
    try:
        df = preprocess_input(data)
        scaled = scaler.transform(df)
        prob = model.predict_proba(scaled)[0][1]
        return float(prob)

    except Exception as e:
        raise RuntimeError(f"Prediction failed: {e}")
