# inference.py
import joblib
import pandas as pd
from pathlib import Path
import logging

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ------------------------------
# Correct Model Folder
# ------------------------------
MODEL_DIR = Path("models")

MODEL_PATH = MODEL_DIR / "xgb_grid_tuned_v1.pkl"
SCALER_PATH = MODEL_DIR / "scaler_v1.pkl"
FEATURE_PATH = MODEL_DIR / "final_features_63.pkl"
SUBGRADE_MAP_PATH = MODEL_DIR / "sub_grade_mapping.pkl"


# ------------------------------
# Load Artifacts
# ------------------------------
try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    final_features = joblib.load(FEATURE_PATH)
    subgrade_map = joblib.load(SUBGRADE_MAP_PATH)

    logging.info("✔ Loaded model, scaler, feature list, and sub-grade mapping.")

except Exception as e:
    logging.error(f"🔥 ERROR loading ML artifacts: {e}")
    raise RuntimeError(f"Failed to load required model files: {e}")


# ------------------------------
# Preprocessing Function
# ------------------------------
def preprocess_input(data: dict):
    df = pd.DataFrame([data])

    # ---- Map Sub-grade ----
    raw_subgrade = str(df.loc[0, "sub_grade"]).strip().upper()

    if raw_subgrade not in subgrade_map:
        raise ValueError(
            f"Invalid sub_grade '{raw_subgrade}'. Allowed: {list(subgrade_map.keys())}"
        )

    df["sub_grade"] = subgrade_map[raw_subgrade]

    # ---- Derived Feature: credit utilization ----
    df["credit_utilization_ratio"] = df["revol_util"].astype(float) / 100.0

    # ---- Derived Feature: loan-to-income ----
    inc = df["annual_inc"].astype(float)
    loan = df["loan_amnt"].astype(float)
    df["loan_to_income_ratio"] = (loan / (inc.replace(0, 1))).round(4)

    # ---- Add missing model-required features ----
    for col in final_features:
        if col not in df.columns:
            df[col] = 0

    # ---- Reorder columns EXACTLY like training ----
    df = df[final_features]

    # ---- Ensure numeric ----
    df = df.apply(pd.to_numeric, errors="coerce").fillna(0)

    return df


# ------------------------------
# Prediction Function
# ------------------------------
def predict_default_probability(data: dict) -> float:
    df = preprocess_input(data)

    # Scale
    scaled = scaler.transform(df)

    # Predict
    prob = model.predict_proba(scaled)[0][1]

    return float(prob)
