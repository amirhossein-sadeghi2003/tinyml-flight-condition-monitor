import os
import joblib
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import accuracy_score, classification_report, ConfusionMatrixDisplay
from sklearn.model_selection import train_test_split


REAL_DATA_PATH = "data/real_labeled_sensor_data.csv"

SYNTHETIC_MODEL_PATH = "models/decision_tree_model.joblib"
REAL_MODEL_PATH = "models/real_decision_tree_model.joblib"

RESULTS_DIR = "results"

SYNTHETIC_ON_REAL_CM_PATH = os.path.join(
    RESULTS_DIR,
    "synthetic_model_on_real_confusion_matrix.png",
)

REAL_ON_REAL_CM_PATH = os.path.join(
    RESULTS_DIR,
    "real_model_on_real_confusion_matrix.png",
)

FEATURE_COLUMNS = [
    "temperature_c",
    "pressure_hpa",
    "humidity_percent",
    "light_lux",
    "distance_cm",
    "object_detected",
]

LABEL_COLUMN = "label"

TEST_SIZE = 0.25
RANDOM_STATE = 42


def load_real_data():
    if not os.path.exists(REAL_DATA_PATH):
        raise FileNotFoundError(
            f"Real labeled dataset not found at {REAL_DATA_PATH}. "
            "Run ml/build_real_dataset.py first."
        )

    return pd.read_csv(REAL_DATA_PATH)


def create_real_holdout(df):
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


def load_model(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model not found at {path}")

    return joblib.load(path)


def evaluate_model(model, X, y, model_name):
    y_pred = model.predict(X)
    accuracy = accuracy_score(y, y_pred)

    print()
    print("=" * 70)
    print(model_name)
    print("=" * 70)
    print(f"Shared real holdout samples: {len(y)}")
    print(f"Accuracy: {accuracy:.4f}")
    print()
    print("Classification Report:")
    print(classification_report(y, y_pred, zero_division=0))

    return y_pred, accuracy


def save_confusion_matrix(y_true, y_pred, title, output_path):
    os.makedirs(RESULTS_DIR, exist_ok=True)

    display = ConfusionMatrixDisplay.from_predictions(
        y_true,
        y_pred,
        cmap="Blues",
    )

    display.ax_.set_title(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Saved confusion matrix to: {output_path}")


def compare_models():
    df = load_real_data()
    X_test, y_test = create_real_holdout(df)

    synthetic_model = load_model(SYNTHETIC_MODEL_PATH)
    real_model = load_model(REAL_MODEL_PATH)

    synthetic_pred, synthetic_accuracy = evaluate_model(
        synthetic_model,
        X_test,
        y_test,
        "Synthetic-trained Decision Tree on shared real holdout",
    )

    real_pred, real_accuracy = evaluate_model(
        real_model,
        X_test,
        y_test,
        "Real-trained Decision Tree on shared real holdout",
    )

    save_confusion_matrix(
        y_test,
        synthetic_pred,
        "Synthetic-trained Model on Shared Real Holdout",
        SYNTHETIC_ON_REAL_CM_PATH,
    )

    save_confusion_matrix(
        y_test,
        real_pred,
        "Real-trained Model on Shared Real Holdout",
        REAL_ON_REAL_CM_PATH,
    )

    print()
    print("Summary")
    print("-------")
    print(f"Evaluation samples:                       {len(y_test)}")
    print(f"Synthetic-trained model on real holdout: {synthetic_accuracy:.4f}")
    print(f"Real-trained model on real holdout:      {real_accuracy:.4f}")

    if synthetic_accuracy < real_accuracy:
        print()
        print(
            "The real-trained model performs better on the shared real holdout. "
            "This indicates that the synthetic data distribution does not fully "
            "match the collected real sensor scenarios."
        )


if __name__ == "__main__":
    compare_models()
