import os
import pandas as pd


DATA_DIR = "data"
OUTPUT_PATH = os.path.join(DATA_DIR, "real_labeled_sensor_data.csv")

SCENARIO_FILES = [
    {
        "path": os.path.join(DATA_DIR, "real_normal_baseline_log.csv"),
        "label": "normal",
        "scenario": "normal_baseline",
    },
    {
        "path": os.path.join(DATA_DIR, "real_warning_distance_log.csv"),
        "label": "warning",
        "scenario": "warning_distance",
    },
    {
        "path": os.path.join(DATA_DIR, "real_critical_close_distance_log.csv"),
        "label": "critical",
        "scenario": "critical_close_distance",
    },
    {
        "path": os.path.join(DATA_DIR, "real_warning_low_light_log.csv"),
        "label": "warning",
        "scenario": "warning_low_light",
    },
    {
        "path": os.path.join(DATA_DIR, "real_critical_dark_log.csv"),
        "label": "critical",
        "scenario": "critical_dark",
    },
    {
        "path": os.path.join(DATA_DIR, "real_bright_light_log.csv"),
        "label": "normal",
        "scenario": "bright_light_observation",
    },
    {
        "path": os.path.join(DATA_DIR, "real_warm_humid_log.csv"),
        "label": "warning",
        "scenario": "warm_humid",
    },
]


FEATURE_COLUMNS = [
    "temperature_c",
    "pressure_hpa",
    "humidity_percent",
    "light_lux",
    "distance_cm",
    "object_detected",
]


def load_scenario_file(file_info):
    path = file_info["path"]

    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing scenario file: {path}")

    df = pd.read_csv(path)

    df["label"] = file_info["label"]
    df["scenario"] = file_info["scenario"]

    return df


def clean_data(df):
    initial_count = len(df)

    # Remove invalid light sensor readings.
    df = df[df["light_lux"] >= 0].copy()

    # Keep only valid object detection flags.
    df = df[df["object_detected"].isin([0, 1])].copy()

    # Remove rows with missing feature values.
    df = df.dropna(subset=FEATURE_COLUMNS + ["label", "scenario"])

    removed_count = initial_count - len(df)

    if removed_count > 0:
        print(f"Removed {removed_count} invalid rows during cleaning.")

    return df


def build_dataset():
    frames = []

    for file_info in SCENARIO_FILES:
        df = load_scenario_file(file_info)
        frames.append(df)

        print(
            f"Loaded {len(df):3d} rows from "
            f"{os.path.basename(file_info['path'])} "
            f"as label={file_info['label']}, "
            f"scenario={file_info['scenario']}"
        )

    combined = pd.concat(frames, ignore_index=True)
    combined = clean_data(combined)

    column_order = [
        "timestamp",
        "temperature_c",
        "pressure_hpa",
        "humidity_percent",
        "light_lux",
        "distance_cm",
        "object_detected",
        "label",
        "scenario",
    ]

    combined = combined[column_order]

    combined.to_csv(OUTPUT_PATH, index=False)

    print()
    print(f"Saved labeled real dataset to: {OUTPUT_PATH}")
    print()
    print("Label distribution:")
    print(combined["label"].value_counts())
    print()
    print("Scenario distribution:")
    print(combined["scenario"].value_counts())


if __name__ == "__main__":
    build_dataset()

