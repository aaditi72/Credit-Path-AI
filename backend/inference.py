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
def predict_default_probability(data: dict) -> dict:
    """
    Returns a dictionary with:
      - probability: float -> probability of the 'default' class (as detected)
      - class_probability_map: dict -> mapping { str(class_label) : probability }
      - classes: list -> the model.classes_ list
      - raw_probs: list -> original predict_proba probabilities (in same order as classes)
      - default_label: the class label chosen as representing 'default'
    This is robust to models whose positive class is NOT the 'default' label.
    """
    try:
        df = preprocess_input(data)
        scaled = scaler.transform(df)
        probs = model.predict_proba(scaled)[0]  # e.g. [prob_of_class0, prob_of_class1, ...]
        classes = list(model.classes_)

        # Heuristic list of labels that commonly mean "default / bad"
        default_candidates = {
            "charged off", "charged_off", "charged-off",
            "default", "defaulted", "late", "late (31-120 days)",
            "1", "true", "yes", "bad"
        }

        chosen_index = None
        for i, c in enumerate(classes):
            try:
                label_norm = str(c).strip().lower()
            except Exception:
                label_norm = ""
            if label_norm in default_candidates:
                chosen_index = i
                default_label = c
                break

        # If not found, prefer numeric 1 (common encoding), else fallback to index 1 if exists
        if chosen_index is None:
            if 1 in classes:
                chosen_index = classes.index(1)
                default_label = 1
            elif "1" in [str(x) for x in classes]:
                chosen_index = [str(x) for x in classes].index("1")
                default_label = classes[chosen_index]
            else:
                # Fallback: choose the class with higher average risk indicators?
                # We'll pick index 1 if binary, else index 0 — but we also return class map so you can inspect.
                chosen_index = 1 if len(classes) > 1 else 0
                default_label = classes[chosen_index]

        prob_default = float(probs[chosen_index])

        # Build label->prob mapping (string keys for JSON safety)
        class_probability_map = { str(classes[i]): float(probs[i]) for i in range(len(classes)) }

        return {
            "probability": prob_default,
            "class_probability_map": class_probability_map,
            "classes": classes,
            "raw_probs": probs.tolist(),
            "default_label": default_label,
            "default_index": chosen_index
        }

    except Exception as e:
        raise RuntimeError(f"Prediction failed: {e}")
