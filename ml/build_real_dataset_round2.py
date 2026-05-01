
import os
import pandas as pd


DATA_DIR = "data"
OUTPUT_PATH = os.path.join(DATA_DIR, "real_labeled_sensor_data_round2.csv")

COLUMNS = [
    "timestamp",
    "temperature_c",
    "pressure_hpa",
    "humidity_percent",
    "light_lux",
    "distance_cm",
    "object_detected",
]

SCENARIOS = [
    {
        "filename": "real_normal_baseline_round2_log.csv",
        "label": "normal",
        "scenario": "normal_baseline_round2",
        "filter": "normal",
    },
    {
        "filename": "real_normal_bright_light_round2_log.csv",
        "label": "normal",
        "scenario": "normal_bright_light_round2",
        "filter": "normal",
    },
    {
        "filename": "real_normal_medium_light_round2_log.csv",
        "label": "normal",
        "scenario": "normal_medium_light_round2",
        "filter": "normal_medium_light",
    },
    {
        "filename": "real_warning_low_light_round2_log.csv",
        "label": "warning",
        "scenario": "warning_low_light_round2",
        "filter": "low_light_warning",
    },
    {
        "filename": "real_critical_dark_round2_log.csv",
        "label": "critical",
        "scenario": "critical_dark_round2",
        "filter": "dark_critical",
    },
    {
        "filename": "real_warning_distance_round2_log.csv",
        "label": "warning",
        "scenario": "warning_distance_round2",
        "filter": "warning_distance",
    },
    {
        "filename": "real_critical_close_distance_round2_log.csv",
        "label": "critical",
        "scenario": "critical_close_distance_round2",
        "filter": "critical_distance",
    },
    {
        "filename": "real_warning_warm_humid_round2_log.csv",
        "label": "warning",
        "scenario": "warning_warm_humid_round2",
        "filter": "warm_humid",
    },
    {
        "filename": "real_warning_warm_humid_high_light_round2_log.csv",
        "label": "warning",
        "scenario": "warning_warm_humid_high_light_round2",
        "filter": "warm_humid_high_light",
    },
]


def apply_filter(df, filter_name):
    original_count = len(df)

    if filter_name == "normal":
        df = df[
            (df["object_detected"] == 0)
            & (df["distance_cm"] >= 90)
            & (df["light_lux"] > 50)
        ]

    elif filter_name == "normal_medium_light":
        df = df[
            (df["object_detected"] == 0)
            & (df["distance_cm"] >= 90)
            & (df["humidity_percent"] < 30)
            & (df["light_lux"] >= 65)
            & (df["light_lux"] <= 90)
        ]

    elif filter_name == "low_light_warning":
        df = df[
            (df["object_detected"] == 0)
            & (df["distance_cm"] >= 90)
            & (df["light_lux"] >= 12)
            & (df["light_lux"] <= 35)
        ]

    elif filter_name == "dark_critical":
        df = df[
            (df["object_detected"] == 0)
            & (df["distance_cm"] >= 90)
            & (df["light_lux"] < 10)
        ]

    elif filter_name == "warning_distance":
        df = df[
            (df["object_detected"] == 1)
            & (df["distance_cm"] >= 30)
            & (df["distance_cm"] <= 50)
        ]

    elif filter_name == "critical_distance":
        df = df[
            (df["object_detected"] == 1)
            & (df["distance_cm"] < 30)
        ]

    elif filter_name == "warm_humid":
        df = df[
            (df["object_detected"] == 0)
            & (df["distance_cm"] >= 90)
            & (df["humidity_percent"] >= 35)
        ]

    elif filter_name == "warm_humid_high_light":
        df = df[
            (df["object_detected"] == 0)
            & (df["distance_cm"] >= 90)
            & (df["humidity_percent"] >= 35)
            & (df["light_lux"] >= 65)
        ]

    else:
        raise ValueError(f"Unknown filter: {filter_name}")

    removed_count = original_count - len(df)
    return df, removed_count


def load_scenario(config):
    path = os.path.join(DATA_DIR, config["filename"])

    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing file: {path}")

    df = pd.read_csv(path)

    for column in COLUMNS:
        if column not in df.columns:
            raise ValueError(f"Missing column '{column}' in {path}")

    df = df[COLUMNS].copy()

    numeric_columns = [
        "temperature_c",
        "pressure_hpa",
        "humidity_percent",
        "light_lux",
        "distance_cm",
        "object_detected",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    before_cleaning = len(df)
    df = df.dropna()
    invalid_removed = before_cleaning - len(df)

    df, filter_removed = apply_filter(df, config["filter"])

    df["label"] = config["label"]
    df["scenario"] = config["scenario"]

    print(
        f"Loaded {len(df):4d} rows from {config['filename']} "
        f"as label={config['label']}, scenario={config['scenario']} "
        f"(removed invalid={invalid_removed}, filtered={filter_removed})"
    )

    return df


def build_dataset():
    frames = []

    for scenario in SCENARIOS:
        frames.append(load_scenario(scenario))

    dataset = pd.concat(frames, ignore_index=True)

    dataset.to_csv(OUTPUT_PATH, index=False)

    print()
    print(f"Saved round2 labeled real dataset to: {OUTPUT_PATH}")

    print()
    print("Label distribution:")
    print(dataset["label"].value_counts())

    print()
    print("Scenario distribution:")
    print(dataset["scenario"].value_counts())

    print()
    print("Feature summary:")
    print(
        dataset[
            [
                "temperature_c",
                "pressure_hpa",
                "humidity_percent",
                "light_lux",
                "distance_cm",
                "object_detected",
            ]
        ].describe()
    )


if __name__ == "__main__":
    build_dataset()

