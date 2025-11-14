import joblib
import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

MODEL_DIR = Path("models")

MODEL_PATH = MODEL_DIR / "xgb_grid_tuned_v1.pkl"
SCALER_PATH = MODEL_DIR / "scaler_v1.pkl"
FEATURE_PATH = MODEL_DIR / "final_features_63.pkl"
SUBGRADE_MAP_PATH = MODEL_DIR / "sub_grade_mapping.pkl"

# Load artifacts
try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    final_features: list = joblib.load(FEATURE_PATH)
    subgrade_map: dict = joblib.load(SUBGRADE_MAP_PATH)

    logging.info("✔ Loaded model, scaler, feature list, and sub-grade mapping.")

except Exception as e:
    logging.error(f"🔥 ERROR loading ML artifacts: {e}")
    raise RuntimeError(f"Failed to load required model files: {e}")


def preprocess_input(data: dict):
    df = pd.DataFrame([data])

    # Convert sub_grade string → numeric
    raw_sub = df.loc[0, "sub_grade"]

    if raw_sub not in subgrade_map:
        raise ValueError(f"Invalid sub_grade '{raw_sub}'. Allowed: {list(subgrade_map.keys())}")

    df["sub_grade"] = subgrade_map[raw_sub]

    # ===== DERIVED FEATURES (MUST ALWAYS EXIST) =====
    df["credit_utilization_ratio"] = df["revol_util"].astype(float) / 100.0
    df["loan_to_income_ratio"] = df["loan_amnt"].astype(float) / (df["annual_inc"].astype(float) + 1)

    # ===== ENSURE final_features contains derived columns =====
    if "credit_utilization_ratio" not in final_features:
        final_features.append("credit_utilization_ratio")

    if "loan_to_income_ratio" not in final_features:
        final_features.append("loan_to_income_ratio")

    # ===== ADD ANY MISSING REQUIRED COLUMNS =====
    for col in final_features:
        if col not in df.columns:
            df[col] = 0

    # ===== REORDER COLUMNS =====
    df = df[final_features]

    # Ensure numeric
    df = df.apply(pd.to_numeric, errors="coerce").fillna(0)

    return df


def predict_default_probability(data: dict) -> float:
    df = preprocess_input(data)
    scaled = scaler.transform(df)
    prob = model.predict_proba(scaled)[0][1]
    return float(prob)
