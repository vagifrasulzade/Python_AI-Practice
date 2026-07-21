import os
import pandas as pd
import numpy as np
import joblib
import shap
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score, confusion_matrix
from sklearn.metrics import roc_curve, ConfusionMatrixDisplay
from xgboost import XGBClassifier

import matplotlib
matplotlib.use("Agg")          # no window, just save images
import matplotlib.pyplot as plt

os.makedirs("model", exist_ok=True)
os.makedirs("static/predictor/images", exist_ok=True)
IMG = "static/predictor/images/"


# ---------------- data + features ----------------
df = pd.read_excel("health_risk_dataset.xlsx")

df["ExerciseLevel"] = df["ExerciseLevel"].map({"Low": 1, "Medium": 2, "High": 3})
df["BMI_Category"] = pd.cut(df["BMI"], bins=[0, 18.5, 25, 30, 100], labels=[1, 2, 3, 4]).astype(int)
df["Glucose_BP_Ratio"] = df["GlucoseLevel"] / df["BloodPressure"]
df["Age_Risk"] = (df["Age"] > 45).astype(int)
df["High_BMI"] = (df["BMI"] > 30).astype(int)

X = df[["Age", "BMI", "GlucoseLevel", "BloodPressure", "FamilyHistory",
        "ExerciseLevel", "BMI_Category", "Glucose_BP_Ratio", "Age_Risk", "High_BMI"]]
y = df["Outcome"]

feature_cols = X.columns.tolist()

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)


# ---------------- Decision Tree ----------------
dt = DecisionTreeClassifier(max_depth=5, min_samples_split=4, random_state=42)
dt.fit(X_train, y_train)
y_pred = dt.predict(X_test)
y_proba = dt.predict_proba(X_test)[:, 1]

acc = accuracy_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_proba)
cm = confusion_matrix(y_test, y_pred)
print(acc)
print(auc)
print(cm)


# ---------------- Random Forest ----------------
rf = RandomForestClassifier(n_estimators=300, max_depth=8, min_samples_split=4,
                            n_jobs=-1, random_state=42)
rf.fit(X_train, y_train)
y_pred_rf = rf.predict(X_test)
y_proba_rf = rf.predict_proba(X_test)[:, 1]

acc_rf = accuracy_score(y_test, y_pred_rf)
auc_rf = roc_auc_score(y_test, y_proba_rf)
cm_rf = confusion_matrix(y_test, y_pred_rf)
print(acc_rf)
print(auc_rf)
print(cm_rf)


# ---------------- XGBoost ----------------
xgb = XGBClassifier(
    objective="binary:logistic",
    n_estimators=600,
    learning_rate=0.03,
    max_depth=4,
    subsample=0.85,
    colsample_bytree=0.9,
    eval_metric="logloss",
    n_jobs=-1,
    random_state=42
)
xgb.fit(X_train, y_train)
y_pred_xgb = xgb.predict(X_test)
y_proba_xgb = xgb.predict_proba(X_test)[:, 1]

acc_xgb = accuracy_score(y_test, y_pred_xgb)
auc_xgb = roc_auc_score(y_test, y_proba_xgb)
cm_xgb = confusion_matrix(y_test, y_pred_xgb)
print(acc_xgb)
print(auc_xgb)
print(cm_xgb)


# ---------------- save the 3 models + their scores ----------------
joblib.dump({"tree": dt, "forest": rf, "xgb": xgb}, "model/models.pkl")
joblib.dump(
    {"features": feature_cols,
     "metrics": {
         "tree_acc": round(acc * 100, 1),
         "forest_acc": round(acc_rf * 100, 1),
         "xgb_acc": round(acc_xgb * 100, 1),
         "tree_auc": round(auc, 3),
         "forest_auc": round(auc_rf, 3),
         "xgb_auc": round(auc_xgb, 3),
     }},
    "model/meta.pkl"
)


# ---------------- ROC Curve ----------------
fpr, tpr, _ = roc_curve(y_test, y_proba_xgb)

plt.figure(figsize=(6, 5))
plt.plot(fpr, tpr, label=f"AUC = {auc_xgb:.3f}")
plt.plot([0, 1], [0, 1], "--")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve")
plt.legend()
plt.savefig(IMG + "roc_curve.png")
plt.close()


# ---------------- Feature Importance ----------------
importance = pd.Series(xgb.feature_importances_, index=feature_cols).sort_values()

plt.figure(figsize=(8, 5))
importance.plot(kind="barh")
plt.title("Feature Importance")
plt.tight_layout()
plt.savefig(IMG + "feature_importance.png")
plt.close()


# ---------------- Confusion Matrix ----------------
disp = ConfusionMatrixDisplay(confusion_matrix=cm_xgb)
disp.plot()
plt.savefig(IMG + "confusion_matrix.png")
plt.close()


# ---------------- Model Comparison ----------------
models = ["Decision Tree", "Random Forest", "XGBoost"]
accuracy = [acc, acc_rf, acc_xgb]

plt.figure(figsize=(6, 5))
plt.bar(models, accuracy)
plt.ylabel("Accuracy")
plt.title("Model Comparison")
plt.savefig(IMG + "model_comparison.png")
plt.close()


# ---------------- Population Risk ----------------
counts = df["Outcome"].value_counts()

plt.figure(figsize=(5, 5))
plt.pie(counts, labels=["Healthy", "Risk"], autopct="%1.1f%%")
plt.title("Population Risk")
plt.savefig(IMG + "population_risk.png")
plt.close()


# ---------------- Correlation Heatmap ----------------
corr = df[["Age", "BMI", "GlucoseLevel", "BloodPressure",
           "FamilyHistory", "ExerciseLevel", "Outcome"]].corr()

plt.figure(figsize=(8, 6))
plt.imshow(corr, cmap="coolwarm", interpolation="nearest")
plt.colorbar()
plt.xticks(np.arange(len(corr.columns)), corr.columns, rotation=45, ha="right")
plt.yticks(np.arange(len(corr.columns)), corr.columns)
plt.title("Correlation Heatmap")
plt.tight_layout()
plt.savefig(IMG + "correlation_heatmap.png")
plt.close()


# ---------------- Risk Trend (average risk by age) ----------------
trend = df.groupby(pd.cut(df["Age"], bins=range(20, 91, 10)), observed=True)["Outcome"].mean() * 100

plt.figure(figsize=(7, 5))
plt.plot([str(i) for i in trend.index], trend.values, marker="o")
plt.ylabel("Average risk %")
plt.xlabel("Age group")
plt.title("Risk Trend by Age")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(IMG + "risk_trend.png")
plt.close()


# ---------------- SHAP Explanation ----------------
explainer = shap.TreeExplainer(xgb)
shap_values = explainer.shap_values(X_test)

plt.figure(figsize=(10, 6))
shap.summary_plot(shap_values, X_test, feature_names=feature_cols, show=False)
plt.tight_layout()
plt.savefig(IMG + "shap_summary.png")
plt.close()

print("Done. Models + charts saved.")
