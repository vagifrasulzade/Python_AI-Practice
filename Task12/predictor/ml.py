import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score

# --- 1. Read the Excel file (this file is in predictor/, dataset is inside ml/) ---
BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "ml", "health_risk_dataset.xlsx")

df = pd.read_excel(DATA_PATH)

# --- 2. Convert ExerciseLevel to numbers ---
level_map = {"Low": 0, "Medium": 1, "High": 2}
df["ExerciseLevel"] = df["ExerciseLevel"].map(level_map)

# --- 3. Features (X) and target (y) ---
X = df[["Age", "BMI", "GlucoseLevel", "BloodPressure", "FamilyHistory", "ExerciseLevel"]]
y = df["Outcome"]

# --- 4. Train / test split ---
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# --- 5. Train the three models (once at server startup, kept in memory) ---
tree_model = DecisionTreeClassifier(random_state=42)
tree_model.fit(X_train, y_train)

forest_model = RandomForestClassifier(random_state=42)
forest_model.fit(X_train, y_train)

xgb_model = XGBClassifier(eval_metric="logloss", random_state=42)
xgb_model.fit(X_train, y_train)

# --- 6. Test accuracy (%) ---
tree_acc = round(accuracy_score(y_test, tree_model.predict(X_test)) * 100, 1)
forest_acc = round(accuracy_score(y_test, forest_model.predict(X_test)) * 100, 1)
xgb_acc = round(accuracy_score(y_test, xgb_model.predict(X_test)) * 100, 1)


# --- 7. Prediction function: returns each model's diabetes probability (%) ---
def predict(age, bmi, glucose, bp, family, exercise):
    row = pd.DataFrame(
        [[age, bmi, glucose, bp, family, exercise]],
        columns=["Age", "BMI", "GlucoseLevel", "BloodPressure", "FamilyHistory", "ExerciseLevel"],
    )

    tree_prob = tree_model.predict_proba(row)[0][1] * 100
    forest_prob = forest_model.predict_proba(row)[0][1] * 100
    xgb_prob = xgb_model.predict_proba(row)[0][1] * 100

    return {
        "tree": round(tree_prob, 1),
        "forest": round(forest_prob, 1),
        "xgb": round(xgb_prob, 1),
        "tree_acc": tree_acc,
        "forest_acc": forest_acc,
        "xgb_acc": xgb_acc,
    }
