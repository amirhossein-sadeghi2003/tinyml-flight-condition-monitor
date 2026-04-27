# Hardware Setup

## Overview

This project is designed for an ESP32-based embedded sensor node. The hardware collects environmental, ambient light, and short-range distance data, then uses these readings for condition monitoring and future embedded machine learning inference.

The current project stage focuses on the machine learning pipeline using synthetic data. The hardware setup described here represents the planned real sensor system for the next development stages.

---

## Planned Hardware Components

| Component | Purpose |
|---|---|
| ESP32 | Main microcontroller and embedded inference target |
| BME280 | Measures temperature, pressure, and humidity |
| BH1750 | Measures ambient light intensity |
| VL53LDK Time-of-Flight distance sensor | Measures short-range distance and detects nearby objects |
| OLED display | Shows sensor readings and predicted condition |
| NeoPixel LEDs | Provides visual status indication |
| Buzzer | Provides audible alert for critical conditions |

---

## Sensor Roles

### BME280

The BME280 provides three environmental measurements:

- temperature in Celsius
- atmospheric pressure in hPa
- relative humidity in percent

These values are used to monitor environmental changes and detect abnormal operating conditions.

In the current ML feature set, the BME280 contributes:

- `temperature_c`
- `pressure_hpa`
- `humidity_percent`

---

### BH1750

The BH1750 measures ambient light intensity in lux.

Light level is used as an environmental feature in the condition monitoring model. Very low light levels can contribute to `warning` or `critical` conditions in the prototype classification logic.

In the current ML feature set, the BH1750 contributes:

- `light_lux`

---

### VL53LDK Time-of-Flight Distance Sensor

The VL53LDK is used as the short-range distance and proximity sensing module in this project.

In this project, the distance sensor is treated as a short-range proximity-aware sensor rather than an altitude, navigation, or flight control sensor. Its role is to detect whether an object is close to the monitoring node.

The model uses two related features from this sensor:

- `distance_cm`
- `object_detected`

If a valid object distance is detected, `object_detected` is set to `1` and `distance_cm` stores the measured distance.

If no object is detected within the useful range, `object_detected` is set to `0` and `distance_cm` is assigned a placeholder value such as `100`.

This design avoids treating missing distance readings as real continuous distance measurements.

Example interpretation:

- no object detected → `object_detected = 0`, `distance_cm = 100`
- object detected at 45 cm → warning-level proximity
- object detected at 20 cm → critical-level proximity

---

## Output Devices

### OLED Display

The OLED display will be used to show real-time system information such as:

- temperature
- pressure
- humidity
- light level
- distance or object detection state
- predicted condition class

The OLED makes the embedded node easier to debug and demonstrate without requiring a computer connection.

---

### NeoPixel LEDs

NeoPixel LEDs will provide a simple visual status indicator.

Planned status colors:

- green for `normal`
- yellow for `warning`
- red for `critical`

This allows the system condition to be understood quickly without reading numeric values.

---

### Buzzer

The buzzer will be used as an audible alert device.

In the initial embedded version, the buzzer will activate only when the predicted condition is `critical`.

In later versions, the buzzer logic can be extended to support different alert patterns for different severity levels.

---

## Planned I2C Devices

The BME280, BH1750, VL53LDK, and OLED display commonly use I2C communication.

Typical ESP32 I2C pins:

| Signal | ESP32 Pin |
|---|---|
| SDA | GPIO 21 |
| SCL | GPIO 22 |

The exact wiring may be adjusted depending on the specific ESP32 board and sensor modules.

Before writing the final firmware, the I2C addresses of the connected modules should be checked using an I2C scanner sketch.

---

## Planned Output Pins

The exact output pins can be adjusted during firmware development.

A possible initial pin assignment is:

| Device | ESP32 Pin |
|---|---|
| NeoPixel data pin | GPIO 5 |
| Buzzer signal pin | GPIO 18 |

These pins are only planned defaults and may be changed depending on wiring convenience and board constraints.

---

## Planned System Flow

The planned hardware flow is:

`Sensors → ESP32 → Feature Vector → Classifier → OLED / NeoPixel / Buzzer`

The ESP32 will read sensor values, build a feature vector, run lightweight classification logic, and update the output devices based on the predicted condition.

---

## Feature Vector

The embedded classifier is planned to use the same feature structure as the current ML pipeline:

| Feature | Source |
|---|---|
| `temperature_c` | BME280 |
| `pressure_hpa` | BME280 |
| `humidity_percent` | BME280 |
| `light_lux` | BH1750 |
| `distance_cm` | VL53LDK |
| `object_detected` | Derived from VL53LDK reading |

This keeps the synthetic ML pipeline and the future embedded sensor pipeline consistent.

---

## Condition Output Mapping

The predicted class will be mapped to the output devices.

| Predicted Class | OLED | NeoPixel | Buzzer |
|---|---|---|---|
| `normal` | Shows normal status | Green | Off |
| `warning` | Shows warning status | Yellow | Off or short alert |
| `critical` | Shows critical status | Red | On or repeated alert |

---

## Development Stages

### Stage 1: Synthetic ML Prototype

Completed in the current project stage.

The ML pipeline is developed using synthetic sensor data before connecting the real hardware.

Completed components:

- synthetic dataset generation
- decision tree model training
- model evaluation
- confusion matrix generation
- feature importance visualization
- decision rule export

---

### Stage 2: Sensor Logger Firmware

The ESP32 will read real sensor values and send them to a computer over Serial.

The Serial output will include:

- temperature
- pressure
- humidity
- light level
- distance
- object detection state

These readings will later be saved as CSV data on the computer.

---

### Stage 3: Real Dataset Collection

Real sensor readings will be collected under different environmental and proximity scenarios.

This stage will make it possible to compare:

- synthetic sensor data
- real sensor data
- model behavior on real measurements

---

### Stage 4: Embedded Inference

The trained decision tree rules will be converted into embedded logic and deployed on the ESP32.

The first embedded classifier can be implemented as simple `if-else` logic based on the exported decision tree rules.

---

### Stage 5: Output Integration

The final embedded prototype will display the predicted condition using:

- OLED text output
- NeoPixel color status
- buzzer alert for critical states

---

## Notes

This hardware setup is intended for an educational embedded AI prototype.

The project does not claim to implement a real aircraft monitoring, navigation, or safety system. It is an aerospace-inspired condition monitoring prototype designed to demonstrate sensor-based TinyML and embedded inference concepts.
