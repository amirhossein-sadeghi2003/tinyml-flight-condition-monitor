
import os
import joblib
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.metrics import ConfusionMatrixDisplay


DATA_PATH = "data/real_labeled_sensor_data.csv"
MODEL_PATH = "models/real_decision_tree_model.joblib"
RESULTS_DIR = "results"

FEATURE_COLUMNS = [
    "temperature_c",
    "pressure_hpa",
    "humidity_percent",
    "light_lux",
    "distance_cm",
    "object_detected",
]

LABEL_COLUMN = "label"


def load_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"Real labeled dataset not found at {DATA_PATH}. "
            "Run ml/build_real_dataset.py first."
        )

    return pd.read_csv(DATA_PATH)


def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Real model not found at {MODEL_PATH}. "
            "Run ml/train_real_model.py first."
        )

    return joblib.load(MODEL_PATH)


def plot_confusion_matrix(model, X_test, y_test):
    os.makedirs(RESULTS_DIR, exist_ok=True)

    display = ConfusionMatrixDisplay.from_estimator(
        model,
        X_test,
        y_test,
        cmap="Blues",
    )

    display.ax_.set_title("Real Dataset Decision Tree Confusion Matrix")
    plt.tight_layout()

    output_path = os.path.join(RESULTS_DIR, "real_confusion_matrix_model.png")
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Saved real confusion matrix to: {output_path}")


def plot_feature_importance(model):
    os.makedirs(RESULTS_DIR, exist_ok=True)

    importance = pd.Series(
        model.feature_importances_,
        index=FEATURE_COLUMNS,
    ).sort_values(ascending=True)

    plt.figure(figsize=(8, 5))
    importance.plot(kind="barh")
    plt.title("Real Dataset Decision Tree Feature Importance")
    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.tight_layout()

    output_path = os.path.join(RESULTS_DIR, "real_model_feature_importance.png")
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Saved real feature importance plot to: {output_path}")


def evaluate_real_model():
    df = load_data()
    model = load_model()

    X = df[FEATURE_COLUMNS]
    y = df[LABEL_COLUMN]

    _, X_test, _, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    plot_confusion_matrix(model, X_test, y_test)
    plot_feature_importance(model)


if __name__ == "__main__":
    evaluate_real_model()

