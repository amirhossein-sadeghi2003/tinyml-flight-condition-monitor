# TinyML Flight Condition Monitor

Aerospace-inspired embedded machine learning system for monitoring environmental and proximity conditions using ESP32 sensors and lightweight classification.

This project demonstrates a complete TinyML-style pipeline:

`synthetic sensor data generation → model training → evaluation → decision rule export → future ESP32 deployment`

The goal is not to build a real aircraft system, but to prototype an embedded condition monitoring workflow inspired by aerospace and onboard environmental monitoring systems.

---

## Project Overview

This project uses simulated sensor readings to classify system conditions into three states:

- `normal`
- `warning`
- `critical`

The input features are inspired by sensors that can be connected to an ESP32-based embedded monitoring system:

- temperature
- pressure
- humidity
- ambient light
- short-range proximity distance
- object detection flag

A lightweight `DecisionTreeClassifier` is trained on the generated dataset. The trained model is then evaluated and exported as readable decision rules, which can later be translated into embedded logic for ESP32 deployment.

---

## Motivation

Embedded monitoring systems often need to make decisions directly on low-power hardware. Instead of relying on a large cloud-based model, this project focuses on a small and interpretable machine learning model that can eventually run on a microcontroller.

The project is designed around the following themes:

- TinyML
- embedded AI
- sensor-based condition monitoring
- cyber-physical systems
- aerospace-inspired environmental monitoring
- interpretable machine learning for edge devices

---

## Hardware Target

The planned embedded target is an ESP32-based sensor node.

Planned hardware components:

- ESP32
- BME280 temperature, pressure, and humidity sensor
- BH1750 light sensor
- short-range distance or proximity sensor
- OLED display
- buzzer
- NeoPixel LEDs

The current stage focuses on the machine learning pipeline using synthetic data. Real sensor logging and embedded inference will be added in later stages.

---

## Classes

The model predicts one of three condition classes.

### Normal

Stable environmental conditions and no nearby object detected.

Example interpretation:

- normal temperature
- standard atmospheric pressure
- moderate humidity
- normal ambient light
- no object detected in short range

### Warning

Moderately abnormal condition or nearby object detected.

Example interpretation:

- moderately high temperature
- moderately low pressure
- high humidity
- low light
- object detected at medium short range

### Critical

Severely abnormal condition or very close object detected.

Example interpretation:

- very high temperature
- very low pressure
- very high humidity
- very low light
- object detected very close to the sensor

---

## Machine Learning Pipeline

The current ML pipeline includes:

1. Synthetic sensor dataset generation
2. Decision tree training
3. Model evaluation
4. Confusion matrix generation
5. Feature importance visualization
6. Decision rule export

The full pipeline can be executed with:

`python ml/main.py`

Individual scripts can also be run separately:

`python ml/generate_synthetic_data.py`

`python ml/train_model.py`

`python ml/evaluate_model.py`

`python ml/export_rules.py`

---

## Dataset

The initial dataset is synthetically generated using rule-based thresholds.

Output file:

`data/synthetic_sensor_data.csv`

Features:

- `temperature_c`
- `pressure_hpa`
- `humidity_percent`
- `light_lux`
- `distance_cm`
- `object_detected`

Target label:

- `label`

This synthetic dataset is used only to prototype the full embedded ML workflow before collecting real sensor data from the ESP32 hardware.

---

## Model

The current model is a decision tree classifier.

Model file:

`models/decision_tree_model.joblib`

A decision tree was selected because it is:

- lightweight
- interpretable
- suitable for embedded deployment
- easy to convert into rule-based logic
- appropriate for early TinyML prototyping

---

## Results

The current trained model achieves high classification performance on the synthetic test set.

Generated result files:

- `results/confusion_matrix.png`
- `results/feature_importance.png`
- `results/tree_rules.txt`

### Confusion Matrix

![Confusion Matrix](results/confusion_matrix.png)

### Feature Importance

![Feature Importance](results/feature_importance.png)

---

## Decision Rule Export

The trained decision tree is exported as readable rules:

`results/tree_rules.txt`

This step is important because the model can later be converted into embedded `if-else` logic for ESP32 inference.

---

## Repository Structure

- `data/` synthetic dataset
- `docs/` project documentation
- `firmware/` future ESP32 firmware
- `ml/` machine learning pipeline scripts
- `models/` trained model files
- `results/` evaluation plots and exported rules
- `assets/` additional project assets

---

## Setup

Create and activate a virtual environment:

`python3 -m venv venv`

`source venv/bin/activate`

Install dependencies:

`pip install -r requirements.txt`

Run the full ML pipeline:

`python ml/main.py`

---

## Current Status

Completed:

- project structure
- synthetic data generator
- decision tree training pipeline
- model saving
- evaluation plots
- feature importance analysis
- decision rule export
- end-to-end ML pipeline runner

Next steps:

- add ESP32 sensor logger firmware
- collect real sensor data
- train model on real or hybrid data
- implement embedded inference
- show classification output on OLED, NeoPixels, and buzzer

---

## Limitations

This project currently uses synthetic data. The generated labels are based on manually defined threshold rules and are intended for pipeline prototyping.

The current model should not be interpreted as a real aerospace safety system. It is an educational and portfolio-oriented embedded AI prototype inspired by aerospace condition monitoring concepts.

---

## License

This project is released under the MIT License.
