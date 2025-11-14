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

# ----------- LOAD ARTIFACTS -----------
try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    final_features = joblib.load(FEATURE_PATH)
    subgrade_map = joblib.load(SUBGRADE_MAP_PATH)

    logging.info("✔ Loaded model, scaler, feature list, and sub-grade mapping.")

except Exception as e:
    logging.error(f"🔥 ERROR loading ML artifacts: {e}")
    raise RuntimeError(f"Failed to load required model files: {e}")

# ----------- PREPROCESSING -----------
def preprocess_input(data: dict):
    df = pd.DataFrame([data])

    # Convert sub_grade string → numerical encoded
    raw_subgrade = df.loc[0, "sub_grade"]

    if raw_subgrade not in subgrade_map:
        raise ValueError(
            f"Invalid sub_grade '{raw_subgrade}'. Allowed values: {list(subgrade_map.keys())}"
        )

    df["sub_grade"] = subgrade_map[raw_subgrade]

    # DO NOT create derived features — model was NOT trained on them
    # NO: credit_utilization_ratio
    # NO: loan_to_income_ratio

    # Add missing one-hot columns
    for col in final_features:
        if col not in df.columns:
            df[col] = 0

    # Reorder columns exactly as model expects
    df = df[final_features]

    # Ensure numeric
    df = df.apply(pd.to_numeric, errors="coerce").fillna(0)

    return df


# ----------- PREDICTION ----------
def predict_default_probability(data: dict) -> float:
    try:
        df = preprocess_input(data)
        scaled_data = scaler.transform(df)
        prob = model.predict_proba(scaled_data)[0][1]
        return float(prob)

    except Exception as e:
        raise RuntimeError(f"Prediction failed: {e}")
