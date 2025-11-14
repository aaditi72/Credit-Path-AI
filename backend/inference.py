# inference.py
import joblib
import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

MODEL_DIR = Path(__file__).resolve().parent / "models"

MODEL_PATH = MODEL_DIR / "xgb_grid_tuned_v1.pkl"
SCALER_PATH = MODEL_DIR / "scaler_v1.pkl"
FEATURE_PATH = MODEL_DIR / "final_features_63.pkl"
SUBGRADE_MAP_PATH = MODEL_DIR / "sub_grade_mapping.pkl"

# ----- LOAD MODEL FILES -----
try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    final_features = joblib.load(FEATURE_PATH)
    subgrade_map = joblib.load(SUBGRADE_MAP_PATH)

    logging.info("✔ Loaded model, scaler, feature list, and sub-grade mapping.")

except Exception as e:
    logging.error(f"🔥 ERROR loading ML artifacts: {e}")
    raise RuntimeError(f"Failed to load required model files: {e}")


# ----- PREPROCESSING -----
def preprocess_input(data: dict):
    df = pd.DataFrame([data])

    # Convert sub_grade (string) → numeric
    raw_sub_grade = df.loc[0, "sub_grade"]

    if raw_sub_grade not in subgrade_map:
        raise ValueError(f"Invalid sub_grade '{raw_sub_grade}'. Allowed: {list(subgrade_map.keys())}")

    df["sub_grade"] = subgrade_map[raw_sub_grade]

    # ❌ REMOVE derived features — NOT trained in model
    # ❌ Remove credit_utilization_ratio
    # ❌ Remove loan_to_income_ratio

    # Add all missing columns as 0
    for col in final_features:
        if col not in df.columns:
            df[col] = 0

    # Reorder columns
    df = df[final_features]

    # Convert numeric
    df = df.apply(pd.to_numeric, errors="coerce").fillna(0)

    return df


# ----- PREDICT -----
def predict_default_probability(data: dict) -> float:
    try:
        df = preprocess_input(data)
    except Exception as e:
        raise RuntimeError(f"Preprocessing failed: {e}")

    try:
        scaled = scaler.transform(df)
        prob = model.predict_proba(scaled)[0][1]
        return float(prob)
    except Exception as e:
        raise RuntimeError(f"Prediction failed: {e}")
