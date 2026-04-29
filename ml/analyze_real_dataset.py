
import os
import pandas as pd
import matplotlib.pyplot as plt


DATA_PATH = "data/real_labeled_sensor_data.csv"
RESULTS_DIR = "results"

FEATURE_COLUMNS = [
    "temperature_c",
    "pressure_hpa",
    "humidity_percent",
    "light_lux",
    "distance_cm",
    "object_detected",
]


def load_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"Dataset not found at {DATA_PATH}. Run ml/build_real_dataset.py first."
        )

    return pd.read_csv(DATA_PATH)


def plot_label_distribution(df):
    os.makedirs(RESULTS_DIR, exist_ok=True)

    counts = df["label"].value_counts()

    plt.figure(figsize=(7, 5))
    counts.plot(kind="bar")
    plt.title("Real Dataset Label Distribution")
    plt.xlabel("Label")
    plt.ylabel("Number of Samples")
    plt.tight_layout()

    output_path = os.path.join(RESULTS_DIR, "real_label_distribution.png")
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Saved label distribution plot to: {output_path}")


def plot_scenario_distribution(df):
    os.makedirs(RESULTS_DIR, exist_ok=True)

    counts = df["scenario"].value_counts().sort_values(ascending=True)

    plt.figure(figsize=(9, 5))
    counts.plot(kind="barh")
    plt.title("Real Dataset Scenario Distribution")
    plt.xlabel("Number of Samples")
    plt.ylabel("Scenario")
    plt.tight_layout()

    output_path = os.path.join(RESULTS_DIR, "real_scenario_distribution.png")
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Saved scenario distribution plot to: {output_path}")


def plot_feature_ranges(df):
    os.makedirs(RESULTS_DIR, exist_ok=True)

    summary = df.groupby("label")[FEATURE_COLUMNS].mean()

    plt.figure(figsize=(10, 6))
    summary.plot(kind="bar")
    plt.title("Mean Feature Values by Label in Real Dataset")
    plt.xlabel("Label")
    plt.ylabel("Mean Value")
    plt.tight_layout()

    output_path = os.path.join(RESULTS_DIR, "real_feature_ranges.png")
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Saved feature range plot to: {output_path}")


def print_summary(df):
    print("Real Dataset Summary")
    print("--------------------")
    print(f"Total samples: {len(df)}")
    print()

    print("Label distribution:")
    print(df["label"].value_counts())
    print()

    print("Scenario distribution:")
    print(df["scenario"].value_counts())
    print()

    print("Feature summary:")
    print(df[FEATURE_COLUMNS].describe())


def analyze_real_dataset():
    df = load_data()

    print_summary(df)
    plot_label_distribution(df)
    plot_scenario_distribution(df)
    plot_feature_ranges(df)


if __name__ == "__main__":
    analyze_real_dataset()

