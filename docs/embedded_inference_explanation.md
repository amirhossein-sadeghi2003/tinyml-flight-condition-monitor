# Embedded Inference Explanation

## Overview

This document explains how the trained Decision Tree model informs the manually adapted condition logic used by the ESP32 firmware.

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

These rules provide one basis for the embedded firmware logic. The firmware is not a direct tree export: some warning boundaries, including the medium-distance and low-light ranges, also reflect the controlled scenario definitions used during data collection.

---

## Why the Firmware Logic Is Manually Adapted

The final ESP32 firmware does not copy the exported tree line by line.

Instead, the firmware uses manually adapted threshold logic informed by the learned tree and the controlled scenario definitions.

In the exported tree, the first split is based on `light_lux`. This is valid for the collected Round2 dataset, but the firmware uses a different priority order for the physical demo:

```text
A close detected object is evaluated before light or humidity conditions.
```

For this physical monitoring demo, close-object proximity was intentionally given higher priority than ambient light. Therefore, the firmware checks proximity first.

The firmware inference order is:

```text
1. If object is detected and distance <= 28.75 cm → critical
2. Else if object is detected and distance <= 50.00 cm → warning
3. Else if light_lux <= 10.00 → critical
4. Else if light_lux <= 35.00 → warning
5. Else if humidity_percent > 29.50 → warning
6. Else → normal
```

This keeps the model-informed thresholds visible while making the firmware's manual priority order explicit during hardware testing.

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

The trained Decision Tree is used as a source of useful thresholds and as the basis for understanding the decision structure.

The firmware logic is an embedded engineering adaptation of that model rather than an identical deployment.

This distinction is intentional:

- the ML model learns useful thresholds from real sensor data
- the exported rules make the model interpretable
- the firmware combines model-informed thresholds with a manually chosen proximity-first order
- the medium-distance and low-light warning ranges also reflect controlled data-collection scenarios
- the final behavior remains easy to inspect and test on hardware

For this prototype, the adaptation keeps the relationship to the trained model inspectable while making the manually chosen firmware behavior explicit.

---

## Evaluation Context

The saved Round2 Decision Tree is evaluated with:

```text
ml/evaluate_real_embedded_model_round2.py
```

The committed result is:

```text
Holdout samples: 453
Accuracy: 0.9934
```

Artifacts:

```text
results/round2_embedded_metrics.txt
results/round2_embedded_confusion_matrix.png
```

This is a stratified row-level holdout from the same curated Round2 dataset used during training. It is not independent recording-session or environment validation.

The `0.9934` score applies to the saved Decision Tree model. It is not a direct accuracy measurement of the manually adapted firmware logic, because the firmware rules are not identical to the trained tree.

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
- firmware accuracy has not been measured on an independent recording session

These limitations should be considered before applying similar logic outside this controlled educational prototype.

---

## Summary

The embedded inference stage connects a trained, interpretable Decision Tree workflow to practical ESP32 firmware behavior while keeping the model-to-firmware adaptation explicit.

The final firmware uses real sensor readings, manually adapted threshold logic, OLED status display, NeoPixel visual feedback, and buzzer alerts.

The full path is:

```text
real sensor data → trained interpretable model → exported rules → manual firmware adaptation → hardware feedback
```
