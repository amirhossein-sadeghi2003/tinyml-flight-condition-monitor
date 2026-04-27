import os
import joblib

from sklearn.tree import export_text


MODEL_PATH = "models/decision_tree_model.joblib"
RESULTS_DIR = "results"
RULES_PATH = os.path.join(RESULTS_DIR, "tree_rules.txt")

FEATURE_COLUMNS = [
    "temperature_c",
    "pressure_hpa",
    "humidity_percent",
    "light_lux",
    "distance_cm",
    "object_detected",
]


def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model not found at {MODEL_PATH}. Run ml/train_model.py first."
        )

    return joblib.load(MODEL_PATH)


def export_tree_rules():
    model = load_model()

    rules = export_text(
        model,
        feature_names=FEATURE_COLUMNS,
    )

    os.makedirs(RESULTS_DIR, exist_ok=True)

    with open(RULES_PATH, "w", encoding="utf-8") as file:
        file.write("Decision Tree Rules\n")
        file.write("===================\n\n")
        file.write(rules)

    print(f"Tree rules exported to: {RULES_PATH}")


if __name__ == "__main__":
    export_tree_rules()
