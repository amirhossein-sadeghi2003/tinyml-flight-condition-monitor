import os
import joblib

from sklearn.tree import export_text


MODEL_PATH = "models/real_embedded_decision_tree_model_round2.joblib"
RESULTS_DIR = "results"
RULES_PATH = os.path.join(RESULTS_DIR, "real_embedded_tree_rules_round2.txt")

FEATURE_COLUMNS = [
    "humidity_percent",
    "light_lux",
    "distance_cm",
    "object_detected",
]


def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Round2 embedded-friendly real model not found at {MODEL_PATH}. "
            "Run ml/train_real_embedded_model_round2.py first."
        )

    return joblib.load(MODEL_PATH)


def export_real_embedded_tree_rules_round2():
    model = load_model()

    rules = export_text(
        model,
        feature_names=FEATURE_COLUMNS,
    )

    os.makedirs(RESULTS_DIR, exist_ok=True)

    with open(RULES_PATH, "w", encoding="utf-8") as file:
        file.write("Round2 Embedded-Friendly Real Decision Tree Rules\n")
        file.write("=================================================\n\n")
        file.write(rules)

    print(f"Round2 embedded-friendly real tree rules exported to: {RULES_PATH}")


if __name__ == "__main__":
    export_real_embedded_tree_rules_round2()
