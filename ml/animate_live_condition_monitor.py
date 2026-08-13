from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import Circle

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "real_labeled_sensor_data_round2.csv"
RESULTS_DIR = ROOT / "results"
OUTPUT_GIF = RESULTS_DIR / "live_condition_monitor.gif"

STATUS_COLORS = {
    "normal": "#2E8B57",
    "warning": "#DAA520",
    "critical": "#C62828",
}


def pick_demo_rows(df):
    parts = []

    scenarios = [
        "normal_baseline_round2",
        "warning_distance_round2",
        "critical_close_distance_round2",
        "critical_dark_round2",
        "warning_low_light_round2",
        "normal_bright_light_round2",
    ]

    for scenario in scenarios:
        block = df[df["scenario"] == scenario].copy()
        if len(block) == 0:
            continue
        parts.append(block.iloc[:80])

    if parts:
        demo = pd.concat(parts, ignore_index=True)
    else:
        demo = df.copy()

    demo = demo.reset_index(drop=True)
    demo["sample_id"] = np.arange(len(demo))
    return demo


def main():
    RESULTS_DIR.mkdir(exist_ok=True)

    df = pd.read_csv(DATA_PATH)
    demo = pick_demo_rows(df)

    frame_step = 4
    frames = list(range(0, len(demo), frame_step))
    window = 45

    fig = plt.figure(figsize=(13.5, 7.8))
    grid = fig.add_gridspec(
        3,
        3,
        width_ratios=[1.15, 1.15, 1.0],
        height_ratios=[1.0, 0.60, 0.18],
    )

    ax_temp = fig.add_subplot(grid[0, 0])
    ax_light = fig.add_subplot(grid[0, 1])
    ax_distance = fig.add_subplot(grid[1, 0])
    ax_humidity = fig.add_subplot(grid[1, 1])

    ax_status = fig.add_subplot(grid[0, 2])
    ax_info = fig.add_subplot(grid[1, 2])
    ax_footer = fig.add_subplot(grid[2, 2])

    fig.suptitle("TinyML Embedded Condition Monitor - Recorded Sensor Playback", fontsize=15)

    axes = [ax_temp, ax_light, ax_distance, ax_humidity]
    for ax in axes:
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, window)

    ax_temp.set_title("Temperature")
    ax_temp.set_ylabel("°C")

    ax_light.set_title("Light")
    ax_light.set_ylabel("lux")

    ax_distance.set_title("Distance")
    ax_distance.set_ylabel("cm")
    ax_distance.set_xlabel("recent samples")

    ax_humidity.set_title("Humidity")
    ax_humidity.set_ylabel("%")
    ax_humidity.set_xlabel("recent samples")

    temp_line, = ax_temp.plot([], [], linewidth=2)
    light_line, = ax_light.plot([], [], linewidth=2)
    distance_line, = ax_distance.plot([], [], linewidth=2)
    humidity_line, = ax_humidity.plot([], [], linewidth=2)

    ax_temp.set_ylim(demo["temperature_c"].min() - 1, demo["temperature_c"].max() + 1)
    ax_light.set_ylim(max(0, demo["light_lux"].min() - 20), demo["light_lux"].max() + 20)
    ax_distance.set_ylim(max(0, demo["distance_cm"].min() - 5), demo["distance_cm"].max() + 5)
    ax_humidity.set_ylim(max(0, demo["humidity_percent"].min() - 5), demo["humidity_percent"].max() + 5)

    ax_status.axis("off")
    ax_info.axis("off")
    ax_footer.axis("off")

    status_title = ax_status.text(
        0.5,
        0.88,
        "",
        ha="center",
        va="center",
        fontsize=18,
        weight="bold",
        transform=ax_status.transAxes,
    )

    status_circle = Circle((0.5, 0.52), 0.16, transform=ax_status.transAxes)
    ax_status.add_patch(status_circle)

    status_subtitle = ax_status.text(
        0.5,
        0.18,
        "Recorded scenario label",
        ha="center",
        va="center",
        fontsize=10,
        transform=ax_status.transAxes,
    )

    info_text = ax_info.text(
        0.03,
        0.95,
        "",
        transform=ax_info.transAxes,
        va="top",
        fontsize=11,
        family="monospace",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.95),
    )

    footer_text = ax_footer.text(
        0.03,
        0.65,
        "Recorded ESP32 sensor data → scenario label → status display",
        transform=ax_footer.transAxes,
        va="center",
        fontsize=9,
    )

    def set_recent_line(line, values):
        x = np.arange(len(values))
        line.set_data(x, values)

    def update(frame_index):
        start = max(0, frame_index - window + 1)
        recent = demo.iloc[start : frame_index + 1].copy()
        row = demo.iloc[frame_index]

        set_recent_line(temp_line, recent["temperature_c"].to_numpy())
        set_recent_line(light_line, recent["light_lux"].to_numpy())
        set_recent_line(distance_line, recent["distance_cm"].to_numpy())
        set_recent_line(humidity_line, recent["humidity_percent"].to_numpy())

        label = str(row["label"]).lower()
        scenario = str(row["scenario"])

        color = STATUS_COLORS.get(label, "#607D8B")
        status_circle.set_facecolor(color)
        status_circle.set_edgecolor("black")
        status_circle.set_linewidth(1.5)

        status_title.set_text(label.upper())
        status_title.set_color(color)

        info_text.set_text(
            f"scenario:    {scenario}\n\n"
            f"temperature: {row['temperature_c']:.2f} C\n"
            f"humidity:    {row['humidity_percent']:.2f} %\n"
            f"light:       {row['light_lux']:.2f} lux\n"
            f"distance:    {row['distance_cm']:.2f} cm\n"
            f"object:      {int(row['object_detected'])}\n\n"
            f"sample:      {frame_index + 1}/{len(demo)}"
        )

        return [
            temp_line,
            light_line,
            distance_line,
            humidity_line,
            status_title,
            status_circle,
            status_subtitle,
            info_text,
            footer_text,
        ]

    animation = FuncAnimation(
        fig,
        update,
        frames=frames,
        interval=70,
        blit=False,
    )

    fig.tight_layout()
    animation.save(OUTPUT_GIF, writer=PillowWriter(fps=16))
    plt.close(fig)

    print("Saved:")
    print(OUTPUT_GIF)


if __name__ == "__main__":
    main()
