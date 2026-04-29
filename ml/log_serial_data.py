import argparse
import csv
import os
import time
from datetime import datetime

import serial


DEFAULT_OUTPUT_PATH = "data/real_sensor_log.csv"

CSV_COLUMNS = [
    "timestamp",
    "temperature_c",
    "pressure_hpa",
    "humidity_percent",
    "light_lux",
    "distance_cm",
    "object_detected",
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Log ESP32 serial sensor data to a CSV file."
    )

    parser.add_argument(
        "--port",
        required=True,
        help="Serial port, for example /dev/ttyUSB0",
    )

    parser.add_argument(
        "--baud",
        type=int,
        default=115200,
        help="Serial baud rate",
    )

    parser.add_argument(
        "--samples",
        type=int,
        default=30,
        help="Number of valid samples to collect",
    )

    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT_PATH,
        help="Output CSV file path",
    )

    return parser.parse_args()


def parse_sensor_line(line):
    parts = line.split(",")

    if len(parts) != 6:
        return None

    try:
        temperature_c = float(parts[0])
        pressure_hpa = float(parts[1])
        humidity_percent = float(parts[2])
        light_lux = float(parts[3])
        distance_cm = float(parts[4])
        object_detected = int(parts[5])
    except ValueError:
        return None

    return [
        datetime.now().isoformat(timespec="seconds"),
        temperature_c,
        pressure_hpa,
        humidity_percent,
        light_lux,
        distance_cm,
        object_detected,
    ]


def main():
    args = parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    file_exists = os.path.exists(args.output)

    print(f"Opening serial port: {args.port}")
    print(f"Saving to: {args.output}")
    print(f"Samples: {args.samples}")
    print()

    collected = 0

    with serial.Serial(args.port, args.baud, timeout=2) as ser:
        time.sleep(2)

        with open(args.output, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            if not file_exists:
                writer.writerow(CSV_COLUMNS)

            while collected < args.samples:
                line = ser.readline().decode("utf-8", errors="ignore").strip()

                if not line:
                    continue

                if line.startswith("temperature_c"):
                    print(f"Skipping header: {line}")
                    continue

                row = parse_sensor_line(line)

                if row is None:
                    print(f"Skipping invalid line: {line}")
                    continue

                writer.writerow(row)
                file.flush()

                collected += 1
                print(f"[{collected}/{args.samples}] {row}")

    print()
    print("Logging completed.")


if __name__ == "__main__":
    main()

