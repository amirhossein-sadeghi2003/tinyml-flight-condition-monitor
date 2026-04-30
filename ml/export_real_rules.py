import os
import joblib

from sklearn.tree import export_text


MODEL_PATH = "models/real_decision_tree_model.joblib"
RESULTS_DIR = "results"
RULES_PATH = os.path.join(RESULTS_DIR, "real_tree_rules.txt")

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
            f"Real model not found at {MODEL_PATH}. Run ml/train_real_model.py first."
        )

    return joblib.load(MODEL_PATH)


def export_real_tree_rules():
    model = load_model()

    rules = export_text(
        model,
        feature_names=FEATURE_COLUMNS,
    )

    os.makedirs(RESULTS_DIR, exist_ok=True)

    with open(RULES_PATH, "w", encoding="utf-8") as file:
        file.write("Real Decision Tree Rules\n")
        file.write("========================\n\n")
        file.write(rules)

    print(f"Real tree rules exported to: {RULES_PATH}")


if __name__ == "__main__":
    export_real_tree_rules()

