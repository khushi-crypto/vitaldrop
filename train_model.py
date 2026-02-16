import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os

# ---------- Paths ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "transfusion.csv")
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

# ---------- Load dataset ----------
df = pd.read_csv(DATA_PATH)

# Clean column names (remove extra spaces)
df.columns = df.columns.str.strip()

# Rename columns if CSV has original long names
rename_map = {
    "Recency (months)": "Recency",
    "Frequency (times)": "Frequency",
    "Monetary (c.c. blood)": "Monetary",
    "Time (months)": "Time",
    "whether he/she donated blood in March 2007": "Target",
}
df = df.rename(columns=rename_map)

# If still not renamed, print columns for debugging
required_cols = {"Recency", "Frequency", "Monetary", "Time", "Target"}
missing = required_cols - set(df.columns)

if missing:
    print("❌ Missing columns:", missing)
    print("✅ Found columns:", df.columns.tolist())
    raise SystemExit("Fix your CSV header names (see above).")

# ---------- Features and Target ----------
X = df[["Recency", "Frequency", "Monetary", "Time"]]
y = df["Target"]

# ---------- Split ----------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ---------- Train model ----------
model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    class_weight="balanced"
)
model.fit(X_train, y_train)

# ---------- Evaluate ----------
pred = model.predict(X_test)
acc = accuracy_score(y_test, pred)

print("✅ Model Accuracy:", round(acc * 100, 2), "%")
print("\n✅ Classification Report:\n", classification_report(y_test, pred))

# ---------- Save model ----------
with open(MODEL_PATH, "wb") as f:
    pickle.dump(model, f)

print(f"\n✅ Model saved as: {MODEL_PATH}")

