import joblib
import pandas as pd
from pathlib import Path
import logging

# Configure basic logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Paths to stored ML artifacts
MODEL_DIR = Path("models")
MODEL_PATH = MODEL_DIR / "xgb_hypertuned_all_features.pkl"
SCALER_PATH = MODEL_DIR / "scaler_all_features.pkl"
FEATURE_PATH = MODEL_DIR / "feature_names_all.pkl"

# Load model, scaler, and feature names at startup
try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    feature_names = joblib.load(FEATURE_PATH)
    logging.info("ML model, scaler, and feature names loaded successfully.")
except FileNotFoundError as e:
    logging.error(f"Missing model artifact: {e}. Please ensure '{MODEL_DIR.resolve()}' contains all required files.")
    raise RuntimeError(f"Error loading model artifacts: {e}. One or more files not found.")
except Exception as e:
    logging.error(f"Error loading model artifacts: {e}")
    raise RuntimeError(f"Error loading model artifacts: {e}")

def predict_default_probability(data: dict) -> float:
    """
    Takes borrower input, aligns features, scales data, and predicts default probability.
    Auto-caps ratio fields to valid ranges for model input and logs warnings.
    """

    # --- Step 0️⃣: Auto-normalize and cap ratios ---
    ratio_fields_to_cap = {
        "loan_to_income_ratio": {"min": 0.0, "max": 1.0},
        "credit_utilization_ratio": {"min": 0.0, "max": 1.0},
        "dti": {"min": 0.0, "max": 100.0}, # DTI usually not >1, but can be high
        "revol_util": {"min": 0.0, "max": 100.0}
    }

    for field, limits in ratio_fields_to_cap.items():
        if field in data and data[field] is not None:
            original_value = data[field]
            if original_value > limits["max"]:
                logging.warning(f"Field '{field}' with value {original_value} was capped at {limits['max']} (was above max).")
                data[field] = limits["max"]
            elif original_value < limits["min"]:
                logging.warning(f"Field '{field}' with value {original_value} was floored at {limits['min']} (was below min).")
                data[field] = limits["min"]

    # Step 1️⃣: Convert to DataFrame
    df = pd.DataFrame([data])

    # Step 2️⃣: Ensure all model features exist and are in the correct order
    # Fill missing columns with 0.0, as expected by the model for unseen features or defaults.
    for col in feature_names:
        if col not in df.columns:
            df[col] = 0.0
    df = df.reindex(columns=feature_names) # Reorder columns to match training data

    # Step 3️⃣: Scale features
    scaled_data = scaler.transform(df)

    # Step 4️⃣: Predict probability using model
    probability = model.predict_proba(scaled_data)[:, 1][0]

    return float(probability)