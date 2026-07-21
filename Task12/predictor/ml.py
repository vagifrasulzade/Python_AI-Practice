import os
import joblib
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")         
import matplotlib.pyplot as plt

import shap


# ---- paths (all relative to this file, so it works on any machine) ----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "model")
IMG_DIR = os.path.join(BASE_DIR, "static", "predictor", "images")

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)


# ---- raw + engineered feature columns (same for train and predict) ----
RAW_COLS = ["Age", "BMI", "GlucoseLevel", "BloodPressure",
            "FamilyHistory", "ExerciseLevel"]

FEATURES = ["Age", "BMI", "GlucoseLevel", "BloodPressure", "FamilyHistory",
            "ExerciseLevel", "BMI_Category", "Glucose_BP_Ratio",
            "Age_Risk", "High_BMI"]

EXERCISE_MAP = {"Low": 1, "Medium": 2, "High": 3}


def engineer(df):
    """Add the engineered columns. Works for a full dataset or one row."""
    df = df.copy()

    if not pd.api.types.is_numeric_dtype(df["ExerciseLevel"]):
        df["ExerciseLevel"] = df["ExerciseLevel"].map(EXERCISE_MAP)

    df["BMI_Category"] = pd.cut(
        df["BMI"], bins=[0, 18.5, 25, 30, 100], labels=[1, 2, 3, 4]
    ).astype(int)
    df["Glucose_BP_Ratio"] = df["GlucoseLevel"] / df["BloodPressure"]
    df["Age_Risk"] = (df["Age"] > 45).astype(int)
    df["High_BMI"] = (df["BMI"] > 30).astype(int)
    return df


# ---- lazy model loading (cached so we only read the files once) ----
_cache = {}


def _load():
    if not _cache:
        _cache["models"] = joblib.load(os.path.join(MODEL_DIR, "models.pkl"))
        _cache["meta"] = joblib.load(os.path.join(MODEL_DIR, "meta.pkl"))
    return _cache["models"], _cache["meta"]


def predict(age, bmi, glucose, bp, family, exercise):
    """Return risk % for all 3 models + their test accuracy/AUC."""
    models, meta = _load()

    row = pd.DataFrame(
        [[age, bmi, glucose, bp, family, exercise]], columns=RAW_COLS
    )
    row = engineer(row)[FEATURES]

    tree = models["tree"].predict_proba(row)[0][1] * 100
    forest = models["forest"].predict_proba(row)[0][1] * 100
    xgb = models["xgb"].predict_proba(row)[0][1] * 100

    return {
        "row": row,
        "tree": round(tree, 1),
        "forest": round(forest, 1),
        "xgb": round(xgb, 1),
        "tree_acc": meta["metrics"]["tree_acc"],
        "forest_acc": meta["metrics"]["forest_acc"],
        "xgb_acc": meta["metrics"]["xgb_acc"],
        "tree_auc": meta["metrics"]["tree_auc"],
        "forest_auc": meta["metrics"]["forest_auc"],
        "xgb_auc": meta["metrics"]["xgb_auc"],
    }


def make_gauge(prob):
    """Draw a half-circle risk gauge (0-100%) into images/user_gauge.png."""
    prob = float(prob)
    color = "#2e7d32" if prob < 40 else "#f9a825" if prob < 70 else "#c62828"

    fig, ax = plt.subplots(figsize=(5, 3), subplot_kw={"aspect": "equal"})

    theta = np.linspace(np.pi, 0, 100)
    ax.plot(np.cos(theta), np.sin(theta), color="#e0e0e0", lw=22, solid_capstyle="round")
    end = np.pi - (prob / 100) * np.pi
    theta2 = np.linspace(np.pi, end, 100)
    ax.plot(np.cos(theta2), np.sin(theta2), color=color, lw=22, solid_capstyle="round")

    ax.text(0, 0.15, f"{prob:.0f}%", ha="center", va="center",
            fontsize=34, fontweight="bold", color=color)
    ax.text(0, -0.15, "Diabetes risk (XGBoost)", ha="center", va="center",
            fontsize=11, color="#555")

    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-0.4, 1.2)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(os.path.join(IMG_DIR, "user_gauge.png"), dpi=110)
    plt.close()


def make_user_shap(row):
    """Explain THIS person's XGBoost prediction into images/user_shap.png."""
    models, _ = _load()
    explainer = shap.TreeExplainer(models["xgb"])
    values = explainer.shap_values(row)[0]      

    order = np.argsort(np.abs(values))
    names = np.array(FEATURES)[order]
    vals = values[order]
    colors = ["#c62828" if v > 0 else "#1565c0" for v in vals]

    plt.figure(figsize=(7, 5))
    plt.barh(names, vals, color=colors)
    plt.axvline(0, color="#888", lw=1)
    plt.title("Why this result?  (red = raises risk, blue = lowers risk)")
    plt.xlabel("SHAP contribution")
    plt.tight_layout()
    plt.savefig(os.path.join(IMG_DIR, "user_shap.png"), dpi=110)
    plt.close()
