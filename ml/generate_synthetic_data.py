import numpy as np
import pandas as pd


def generate_normal_sample():
    return {
        "temperature_c": np.random.normal(25, 2),
        "pressure_hpa": np.random.normal(1013, 5),
        "humidity_percent": np.random.normal(45, 8),
        "light_lux": np.random.normal(500, 120),
        "distance_cm": 100.0,
        "object_detected": 0,
        "label": "normal",
    }


def generate_warning_sample():
    case = np.random.choice(["temperature", "pressure", "light", "distance", "humidity"])

    sample = generate_normal_sample()
    sample["label"] = "warning"

    if case == "temperature":
        sample["temperature_c"] = np.random.uniform(31, 38)

    elif case == "pressure":
        sample["pressure_hpa"] = np.random.uniform(985, 1000)

    elif case == "light":
        sample["light_lux"] = np.random.uniform(120, 250)

    elif case == "distance":
        sample["object_detected"] = 1
        sample["distance_cm"] = np.random.uniform(30, 50)

    elif case == "humidity":
        sample["humidity_percent"] = np.random.uniform(65, 80)

    return sample


def generate_critical_sample():
    case = np.random.choice(["temperature", "pressure", "light", "distance", "humidity"])

    sample = generate_normal_sample()
    sample["label"] = "critical"

    if case == "temperature":
        sample["temperature_c"] = np.random.uniform(39, 50)

    elif case == "pressure":
        sample["pressure_hpa"] = np.random.uniform(930, 980)

    elif case == "light":
        sample["light_lux"] = np.random.uniform(0, 100)

    elif case == "distance":
        sample["object_detected"] = 1
        sample["distance_cm"] = np.random.uniform(5, 30)

    elif case == "humidity":
        sample["humidity_percent"] = np.random.uniform(80, 95)

    return sample


def generate_dataset(samples_per_class=300, output_path="data/synthetic_sensor_data.csv"):
    np.random.seed(42)

    rows = []

    for _ in range(samples_per_class):
        rows.append(generate_normal_sample())

    for _ in range(samples_per_class):
        rows.append(generate_warning_sample())

    for _ in range(samples_per_class):
        rows.append(generate_critical_sample())

    df = pd.DataFrame(rows)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    df.to_csv(output_path, index=False)

    print(f"Dataset saved to {output_path}")
    print(df["label"].value_counts())
    print()
    print(df.head())

    return df


if __name__ == "__main__":
    generate_dataset()
