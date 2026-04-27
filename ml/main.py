import subprocess
import sys


PIPELINE_STEPS = [
    ("Generate synthetic sensor dataset", "ml/generate_synthetic_data.py"),
    ("Train decision tree model", "ml/train_model.py"),
    ("Evaluate trained model", "ml/evaluate_model.py"),
    ("Export decision tree rules", "ml/export_rules.py"),
]


def run_step(description, script_path):
    print()
    print("=" * 70)
    print(description)
    print("=" * 70)

    result = subprocess.run(
        [sys.executable, script_path],
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Pipeline step failed: {script_path}")


def main():
    print("TinyML Flight Condition Monitor Pipeline")

    for description, script_path in PIPELINE_STEPS:
        run_step(description, script_path)

    print()
    print("=" * 70)
    print("Pipeline completed successfully")
    print("=" * 70)


if __name__ == "__main__":
    main()

