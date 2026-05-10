# Embedded Inference Explanation

## Overview

This document explains how the trained Decision Tree model is converted into embedded inference logic for the ESP32 firmware.

The goal of the embedded inference stage is to run lightweight condition classification directly on the microcontroller using real sensor readings.

The firmware classifies each sensor state into one of three conditions:

- `normal`
- `warning`
- `critical`

The ESP32 then uses the predicted condition to update:

- Serial output
- OLED display
- NeoPixel LEDs
- buzzer alert

---

## Why a Decision Tree?

A Decision Tree was selected for the deployed model because it is:

- lightweight
- interpretable
- easy to export as readable rules
- suitable for small embedded datasets
- easy to convert into `if-else` logic for microcontroller firmware

This makes it more appropriate for a small ESP32 prototype than a larger black-box model.

---

## Embedded Input Features

The full data logging pipeline records:

- `temperature_c`
- `pressure_hpa`
- `humidity_percent`
- `light_lux`
- `distance_cm`
- `object_detected`

The final embedded-friendly inference logic uses:

- `humidity_percent`
- `light_lux`
- `distance_cm`
- `object_detected`

Temperature and pressure are still logged and displayed, but they are not part of the final embedded-friendly inference logic because they can drift with room and environmental conditions.

---

## Exported Round2 Decision Tree Rules

The Round2 embedded-friendly Decision Tree rules are exported in:

```text
results/real_embedded_tree_rules_round2.txt
```

The exported tree mainly uses:

- ambient light
- distance
- humidity

A simplified view of the learned logic is:

```text
light_lux <= 10        → critical
distance_cm <= 28.75   → critical
humidity high          → warning
otherwise              → normal or warning depending on thresholds
```

These rules provide the basis for the embedded firmware logic.

---

## Why the Firmware Logic Is Safety-Prioritized

The final ESP32 firmware does not blindly copy the exported tree line by line.

Instead, the learned thresholds are adapted into safety-prioritized embedded logic.

In the exported tree, the first split is based on `light_lux`. This is valid for the collected Round2 dataset, but in a real hardware demo it can create an undesirable behavior:

```text
A close object under high light could be hidden by the light-based branch.
```

For a physical monitoring prototype, close-object proximity is more safety-critical than ambient light. Therefore, the firmware checks proximity first.

The firmware inference order is:

```text
1. If object is detected and distance <= 28.75 cm → critical
2. Else if object is detected and distance <= 50.00 cm → warning
3. Else if light_lux <= 10.00 → critical
4. Else if light_lux <= 35.00 → warning
5. Else if humidity_percent > 29.50 → warning
6. Else → normal
```

This preserves the main learned thresholds while making the embedded behavior more robust and intuitive during real hardware testing.

---

## Firmware Inference Function

The embedded inference logic is implemented in:

```text
firmware/sensor_logger/sensor_logger.ino
```

Main function:

```text
predictCondition(...)
```

The function receives:

```text
humidity_percent
light_lux
distance_cm
object_detected
```

It outputs:

```text
predicted_condition
prediction_reason
```

Example output conditions and reasons:

| Condition | Example Reason |
|---|---|
| `normal` | `Safe` |
| `warning` | `Medium Dist` |
| `warning` | `Low Light` |
| `warning` | `High Humidity` |
| `critical` | `Close Object` |
| `critical` | `Very Low Light` |

---

## Output Behavior

After prediction, the firmware updates local feedback devices.

| Condition | OLED | NeoPixel | Buzzer |
|---|---|---|---|
| `normal` | Shows stable status | Green | Off |
| `warning` | Shows warning cause | Yellow / orange | Off |
| `critical` | Shows critical cause | Red | Beep alert |

This gives immediate local feedback without requiring a laptop or cloud connection.

---

## Difference Between ML Model and Firmware Logic

The trained Decision Tree is used as the source of the thresholds and as the basis for understanding the decision structure.

The firmware logic is an embedded engineering adaptation of that model.

This distinction is intentional:

- the ML model learns useful thresholds from real sensor data
- the exported rules make the model interpretable
- the firmware applies those thresholds in a safety-prioritized order
- the final behavior is easier to test, explain, and demonstrate on hardware

This is a common embedded AI tradeoff: the deployed logic should be faithful to the model's useful thresholds while also respecting real-world system priorities.

---

## Limitations

The embedded inference logic is designed for this specific prototype and dataset.

Current limitations:

- it is not a certified safety system
- thresholds are based on controlled lab-style data collection
- the model uses a small number of scenarios
- the firmware logic is manually adapted from the learned tree
- the system has not been tested across broad environmental conditions
- distance readings depend on object surface, angle, and sensor behavior

These limitations are acceptable for an educational TinyML / Embedded AI prototype, but they should be considered before applying similar logic to real safety-critical systems.

---

## Summary

The embedded inference stage converts a trained, interpretable Decision Tree workflow into practical ESP32 firmware behavior.

The final firmware uses real sensor readings, safety-prioritized threshold logic, OLED status display, NeoPixel visual feedback, and buzzer alerts.

This demonstrates the full path from:

```text
real sensor data → trained interpretable model → exported rules → embedded inference → hardware feedback
```
