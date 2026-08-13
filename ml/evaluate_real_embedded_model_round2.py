import os

import joblib
import matplotlib.pyplot as plt
import pandas as pd

from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
)
from sklearn.model_selection import train_test_split


DATA_PATH = "data/real_labeled_sensor_data_round2.csv"
MODEL_PATH = "models/real_embedded_decision_tree_model_round2.joblib"

RESULTS_DIR = "results"
CONFUSION_MATRIX_PATH = os.path.join(
    RESULTS_DIR,
    "round2_embedded_confusion_matrix.png",
)
METRICS_PATH = os.path.join(
    RESULTS_DIR,
    "round2_embedded_metrics.txt",
)

FEATURE_COLUMNS = [
    "humidity_percent",
    "light_lux",
    "distance_cm",
    "object_detected",
]

LABEL_COLUMN = "label"

TEST_SIZE = 0.25
RANDOM_STATE = 42


def load_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"Round2 real labeled dataset not found at {DATA_PATH}. "
            "Run ml/build_real_dataset_round2.py first."
        )

    return pd.read_csv(DATA_PATH)


def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Round2 embedded model not found at {MODEL_PATH}. "
            "Run ml/train_real_embedded_model_round2.py first."
        )

    return joblib.load(MODEL_PATH)


def create_holdout(df):
    X = df[FEATURE_COLUMNS]
    y = df[LABEL_COLUMN]

    _, X_test, _, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    return X_test, y_test


def save_confusion_matrix(y_true, y_pred):
    os.makedirs(RESULTS_DIR, exist_ok=True)

    display = ConfusionMatrixDisplay.from_predictions(
        y_true,
        y_pred,
        cmap="Blues",
    )

    display.ax_.set_title(
        "Round2 Decision Tree - Stratified Row-Level Holdout"
    )

    plt.tight_layout()
    plt.savefig(CONFUSION_MATRIX_PATH, dpi=300)
    plt.close()

    print(f"Saved confusion matrix to: {CONFUSION_MATRIX_PATH}")


def save_metrics(y_true, y_pred):
    os.makedirs(RESULTS_DIR, exist_ok=True)

    accuracy = accuracy_score(y_true, y_pred)
    report = classification_report(
        y_true,
        y_pred,
        zero_division=0,
        digits=4,
    )

    text = (
        "Round2 Embedded Decision Tree Evaluation\n"
        "========================================\n\n"
        f"Dataset: {DATA_PATH}\n"
        f"Features: {FEATURE_COLUMNS}\n"
        f"Test size: {TEST_SIZE}\n"
        f"Random state: {RANDOM_STATE}\n"
        f"Holdout samples: {len(y_true)}\n"
        f"Accuracy: {accuracy:.4f}\n\n"
        "Evaluation protocol:\n"
        "Stratified row-level holdout reconstructed from the same curated "
        "Round2 dataset used during training.\n\n"
        "Limitation:\n"
        "This is a within-dataset holdout evaluation. It is not an "
        "independent recording-session or environment validation.\n\n"
        "Classification Report:\n"
        f"{report}"
    )

    with open(METRICS_PATH, "w", encoding="utf-8") as file:
        file.write(text)

    print()
    print(text)
    print(f"Saved metrics to: {METRICS_PATH}")


def evaluate_round2_model():
    df = load_data()
    model = load_model()

    X_test, y_test = create_holdout(df)
    y_pred = model.predict(X_test)

    save_metrics(y_test, y_pred)
    save_confusion_matrix(y_test, y_pred)


if __name__ == "__main__":
    evaluate_round2_model()
