# System Overview

## TinyML Flight Condition Monitor

This project is an aerospace-inspired embedded condition monitoring prototype built around an ESP32-based sensor node.

The system reads environmental, ambient light, and short-range proximity data, converts the readings into a feature vector, and classifies the current condition as one of three states:

- `normal`
- `warning`
- `critical`

The goal is not to build a real aircraft safety system. The goal is to demonstrate a complete educational Embedded AI / TinyML workflow using real hardware, real sensor data, lightweight machine learning, and embedded deployment.

---

## Project Narrative

The project follows an end-to-end embedded machine learning workflow:

```text
synthetic sensor data generation
→ model training
→ evaluation
→ decision rule export
→ ESP32 sensor logging
→ real sensor dataset collection
→ real model training
→ synthetic-vs-real model comparison
→ filtered Round2 real dataset
→ embedded-friendly decision rules
→ ESP32 embedded inference
→ OLED / NeoPixel / buzzer hardware feedback
```

This makes the project suitable as a portfolio-grade demonstration of:

- cyber-physical systems
- embedded sensor data collection
- TinyML-style model development
- synthetic-to-real data comparison
- interpretable machine learning
- ESP32 deployment
- local hardware feedback

---

## High-Level Architecture

The final system architecture is:

```text
Sensors → ESP32 → Feature Vector → Embedded Classifier → Output Devices
```

The ESP32 reads data from multiple sensors:

- BME280 for temperature, pressure, and humidity
- BH1750 for ambient light intensity
- VL53LDK / VL53L0X-compatible ToF sensor for short-range proximity

The ESP32 then runs embedded threshold logic derived from a trained Decision Tree model.

The predicted condition is shown through:

- Serial CSV output
- OLED live status display
- NeoPixel status colors
- buzzer alert for critical condition

---

## Hardware Feedback

The embedded prototype provides local feedback without requiring a computer connection.

| Condition | OLED | NeoPixel | Buzzer |
|---|---|---|---|
| `normal` | Shows `System stable` | Green | Off |
| `warning` | Shows warning cause | Yellow / orange | Off |
| `critical` | Shows critical cause | Red | Beep alert |

The OLED also displays live sensor readings such as:

- light level
- distance
- humidity
- object detection state

---

## Sensor Inputs and Features

The project logs and processes the following sensor-derived features:

| Feature | Source | Description |
|---|---|---|
| `temperature_c` | BME280 | Temperature in Celsius |
| `pressure_hpa` | BME280 | Atmospheric pressure in hPa |
| `humidity_percent` | BME280 | Relative humidity percentage |
| `light_lux` | BH1750 | Ambient light intensity |
| `distance_cm` | VL53LDK / VL53L0X | Short-range distance measurement |
| `object_detected` | Derived from distance sensor | Binary flag for valid object detection |

The final embedded-friendly Round2 model uses:

```text
humidity_percent
light_lux
distance_cm
object_detected
```

Temperature and pressure are still logged, but they are not used in the final embedded-friendly inference logic because they are more sensitive to environmental drift.

---

## Condition Classes

The system classifies each sensor state into one of three classes.

### Normal

The system is considered normal when environmental conditions are stable and no nearby object is detected.

Typical pattern:

- normal indoor light
- no close object
- humidity within the normal range for the collected environment

### Warning

The system enters warning mode when one or more conditions are moderately abnormal.

Typical warning patterns:

- low light
- object detected at medium short range
- high humidity compared with the collected baseline

### Critical

The system enters critical mode when the sensed condition is severe.

Typical critical patterns:

- very low light
- object detected very close to the sensor

---

## Machine Learning Pipeline

The project includes both synthetic and real-data machine learning stages.

### Synthetic Pipeline

The synthetic pipeline was used first to build the full ML workflow:

1. Generate synthetic sensor data
2. Train a Decision Tree classifier
3. Evaluate the model
4. Generate confusion matrix and feature importance plots
5. Export the trained rules

Main synthetic pipeline command:

```bash
python ml/main.py
```

Important synthetic files:

```text
data/synthetic_sensor_data.csv
models/decision_tree_model.joblib
results/confusion_matrix.png
results/feature_importance.png
results/tree_rules.txt
```

The synthetic pipeline was useful for building the structure of the project, but synthetic data did not fully match real hardware behavior.

---

## Real Sensor Dataset

After the synthetic prototype, real data was collected from the ESP32 sensor node under controlled scenarios.

The initial real dataset was built using:

```bash
python ml/build_real_dataset.py
```

Output:

```text
data/real_labeled_sensor_data.csv
```

Real dataset analysis generated:

```text
results/real_label_distribution.png
results/real_scenario_distribution.png
results/real_feature_ranges.png
```

A real-data Decision Tree model was then trained with:

```bash
python ml/train_real_model.py
python ml/evaluate_real_model.py
```

Important outputs:

```text
models/real_decision_tree_model.joblib
results/real_confusion_matrix_model.png
results/real_model_feature_importance.png
```

The initial real model performed very well on the controlled real dataset, but the result was treated cautiously because the dataset was small and scenario-based.

---

## Synthetic vs Real Comparison

The project explicitly compares a synthetic-trained model against a real-trained model on real sensor data.

Comparison script:

```bash
python ml/compare_synthetic_real_models.py
```

Important outputs:

```text
results/synthetic_model_on_real_confusion_matrix.png
results/real_model_on_real_confusion_matrix.png
```

Result:

```text
Synthetic-trained model accuracy on real data: 0.2871
Real-trained model accuracy on real data: 1.0000
```

This comparison is an important part of the project narrative.

It shows that synthetic data was useful for prototyping the workflow, but real hardware data was necessary for realistic model behavior.

---

## Round2 Real Dataset

A second round of real data was collected in a shorter time window to reduce room and environmental drift.

Round2 dataset output:

```text
data/real_labeled_sensor_data_round2.csv
```

Build script:

```bash
python ml/build_real_dataset_round2.py
```

Final Round2 dataset size:

```text
total samples: 1811
normal: 607
warning: 798
critical: 406
```

Approximate Round2 feature ranges:

```text
temperature: 26.49 to 30.48 C
pressure: 839.69 to 839.93 hPa
humidity: 19.21 to 78.05 %
light: 1.67 to 293.33 lux
distance: 6.10 to 100.00 cm
```

Round2 data was filtered scenario-specifically to create cleaner class boundaries for embedded deployment.

---

## Embedded-Friendly Round2 Model

The final deployment model is an embedded-friendly Decision Tree trained on selected real features.

Training script:

```bash
python ml/train_real_embedded_model_round2.py
```

Model output:

```text
models/real_embedded_decision_tree_model_round2.joblib
```

Exported rules:

```bash
python ml/export_real_embedded_rules_round2.py
```

Rules file:

```text
results/real_embedded_tree_rules_round2.txt
```

Final embedded model performance:

```text
Accuracy: 0.9934

critical precision/recall/f1: 1.00 / 1.00 / 1.00
normal precision/recall/f1: about 1.00 / 0.98 / 0.99
warning precision/recall/f1: about 0.99 / 1.00 / 0.99
```

---

## Embedded Inference on ESP32

The final firmware uses safety-prioritized threshold logic derived from the trained Round2 Decision Tree rules.

The firmware intentionally prioritizes proximity first:

1. close object → critical
2. medium-distance object → warning
3. very low light → critical
4. low light → warning
5. high humidity → warning
6. otherwise normal

This is documented as:

```text
safety-prioritized embedded threshold logic derived from learned rules
```

This design keeps the embedded behavior interpretable and easy to inspect.

Main firmware file:

```text
firmware/sensor_logger/sensor_logger.ino
```

The firmware includes:

- sensor reading
- embedded prediction
- prediction reason
- Serial CSV output
- OLED display
- NeoPixel status colors
- buzzer critical alert

---

## Why Decision Tree?

A Decision Tree is used as the main deployment model because it is:

- lightweight
- interpretable
- easy to debug
- easy to export as rules
- easy to implement as embedded `if-else` logic
- suitable for small real sensor datasets
- appropriate for an ESP32 TinyML-style prototype

A small neural network could be added later as a comparison baseline, but the Decision Tree remains the main deployment model.

---

## Current Project Status

The project currently has a complete end-to-end embedded ML prototype.

Completed:

- synthetic sensor data generation
- synthetic Decision Tree training
- synthetic model evaluation
- decision rule export
- ESP32 real sensor logging
- scenario-based real dataset collection
- real dataset analysis
- real Decision Tree training
- synthetic-vs-real model comparison
- filtered Round2 real dataset
- embedded-friendly Round2 Decision Tree model
- exported embedded rules
- ESP32 embedded inference
- Serial prediction output
- OLED live status display
- NeoPixel status indication
- buzzer critical alert
- hardware demo photos
- README documentation update
- hardware setup documentation update

---

## Repository Structure

Important project directories:

```text
data/       sensor datasets and scenario logs
ml/         Python scripts for data generation, training, evaluation, and rule export
models/     trained model files
results/    plots, confusion matrices, and exported rules
firmware/   ESP32 Arduino firmware
assets/     hardware demo photos
docs/       project documentation
```

---

## Limitations

This project is an educational prototype, not a real aircraft monitoring or safety system.

Current limitations:

- real data was collected in controlled indoor scenarios
- dataset size is still relatively small
- labels are scenario-based rather than from a real operational system
- thresholds are tuned to the current hardware setup and environment
- model performance should not be interpreted as general safety reliability
- the system has not been tested across many rooms, lighting conditions, or sensor placements

---

## Future Improvements

Possible future improvements:

- collect more real data in different rooms and lighting conditions
- add a short demo video or GIF
- improve or crop/rotate OLED photos
- add a small neural network baseline only for comparison
- add a portfolio-style project report
- test robustness under more varied sensor placements

---

## Safety Note

This project should not be interpreted as a real aircraft safety, navigation, or flight control system.

It is an educational embedded AI prototype inspired by aerospace-style condition monitoring concepts.
