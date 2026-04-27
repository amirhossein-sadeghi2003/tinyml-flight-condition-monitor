import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report


DATA_PATH = "data/synthetic_sensor_data.csv"
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "decision_tree_model.joblib")


FEATURE_COLUMNS = [
    "temperature_c",
    "pressure_hpa",
    "humidity_percent",
    "light_lux",
    "distance_cm",
    "object_detected",
]

LABEL_COLUMN = "label"


def load_data(path):
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Dataset not found at {path}. Run ml/generate_synthetic_data.py first."
        )

    return pd.read_csv(path)


def train_model():
    df = load_data(DATA_PATH)

    X = df[FEATURE_COLUMNS]
    y = df[LABEL_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    model = DecisionTreeClassifier(
        max_depth=None,
        random_state=42,
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)

    print("Decision Tree Classification Results")
    print("------------------------------------")
    print(f"Accuracy: {accuracy:.4f}")
    print()
    print("Classification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print(f"Model saved to: {MODEL_PATH}")


if __name__ == "__main__":
    train_model()

