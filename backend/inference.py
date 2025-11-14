# inference.py
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
import logging

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Correct model directory
MODEL_DIR = Path("models")

# Load the **CORRECT** artifacts created during training
MODEL_PATH = MODEL_DIR / "xgb_grid_tuned_v1.pkl"
SCALER_PATH = MODEL_DIR / "scaler_v1.pkl"
FEATURE_PATH = MODEL_DIR / "final_features_v1.pkl"
SUBGRADE_ENCODER_PATH = MODEL_DIR / "sub_grade_encoder.pkl"

# Load artifacts
try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    final_features = joblib.load(FEATURE_PATH)
    subgrade_encoder = joblib.load(SUBGRADE_ENCODER_PATH)

    logging.info("✅ Loaded model, scaler, final_features, and sub_grade encoder")

except Exception as e:
    logging.error(f"🔥 ERROR loading ML artifacts: {e}")
    raise RuntimeError(f"Failed to load required model files: {e}")


def preprocess_input(data: dict) -> pd.DataFrame:
    """
    Preprocess incoming borrower JSON exactly like training.
    """

    df = pd.DataFrame([data])

    # --- Derived Features (must match training EXACTLY) ---
    df["credit_utilization_ratio"] = df["revol_util"] / 100.0
    df["loan_to_income_ratio"] = df["loan_amnt"] / (df["annual_inc"] + 1)

    # --- Encode sub_grade using saved encoder ---
    df["sub_grade"] = subgrade_encoder.transform(df["sub_grade"])

    # --- Add missing columns ---
    for col in final_features:
        if col not in df.columns:
            df[col] = 0

    # --- Reorder to match training order ---
    df = df[final_features]

    # --- Ensure numeric ---
    df = df.apply(pd.to_numeric, errors="coerce").fillna(0)

    return df


def predict_default_probability(data: dict) -> float:
    """
    Preprocess → Scale → Predict probability
    """
    df = preprocess_input(data)

    scaled = scaler.transform(df)
    prob = model.predict_proba(scaled)[0][1]

    return float(prob)
