# System Overview

## TinyML Flight Condition Monitor

This project is an aerospace-inspired embedded condition monitoring prototype. The system is designed around a small ESP32-based sensor node that observes environmental and short-range proximity conditions, extracts sensor features, and classifies the current condition as `normal`, `warning`, or `critical`.

The current implementation focuses on the machine learning pipeline using synthetic sensor data. Future stages will add real sensor logging and embedded inference on ESP32.

---

## High-Level Architecture

The planned system architecture is:

`Sensors → ESP32 → Feature Vector → ML Classifier → Output Devices`

The sensor node collects environmental and proximity measurements, converts them into a feature vector, and uses a lightweight classifier to estimate the current condition.

The output devices then provide feedback:

- OLED display shows the predicted condition
- NeoPixel LEDs indicate system status visually
- buzzer provides an alert for critical conditions

---

## Sensor Inputs

The planned sensor inputs are:

- BME280 for temperature, pressure, and humidity
- BH1750 for ambient light intensity
- short-range distance or proximity sensor
- optional object detection flag derived from distance readings

The machine learning model currently uses the following features:

- `temperature_c`
- `pressure_hpa`
- `humidity_percent`
- `light_lux`
- `distance_cm`
- `object_detected`

---

## Condition Classes

The system classifies each sensor state into one of three classes.

### Normal

The system is considered normal when environmental conditions are stable and no nearby object is detected.

Typical pattern:

- moderate temperature
- standard atmospheric pressure
- moderate humidity
- normal ambient light
- no object detected in short range

### Warning

The system enters warning mode when one or more conditions become moderately abnormal.

Possible warning patterns:

- moderately high temperature
- moderately low pressure
- high humidity
- low ambient light
- object detected at medium short range

### Critical

The system enters critical mode when the sensed condition becomes severe.

Possible critical patterns:

- very high temperature
- very low pressure
- very high humidity
- very low ambient light
- object detected very close to the sensor

---

## Machine Learning Pipeline

The current software pipeline includes:

1. Generate synthetic sensor data
2. Train a decision tree classifier
3. Evaluate the trained model
4. Generate a confusion matrix
5. Generate feature importance plot
6. Export the trained decision tree as readable rules

The complete pipeline can be executed with:

`python ml/main.py`

---

## Why Decision Tree?

A decision tree is used in the current version because it is:

- lightweight
- interpretable
- easy to debug
- suitable for early TinyML prototyping
- easier to convert into embedded `if-else` logic

This makes it a practical first model for ESP32 deployment.

---

## Current Stage

The current project stage is:

`Synthetic ML prototype`

Completed:

- synthetic dataset generation
- model training
- model evaluation
- feature importance analysis
- decision rule export
- end-to-end ML pipeline runner

Not completed yet:

- real sensor logging
- real dataset collection
- embedded inference on ESP32
- OLED, NeoPixel, and buzzer output logic

---

## Future Embedded Flow

The planned embedded inference flow is:

1. ESP32 reads sensor values
2. sensor readings are converted into features
3. trained logic classifies the current state
4. OLED displays the class
5. NeoPixels show green, yellow, or red status
6. buzzer activates for critical conditions

Status mapping:

- `normal` → green LEDs, no buzzer
- `warning` → yellow LEDs, no buzzer or short alert
- `critical` → red LEDs, buzzer alert

---

## Limitations

The current dataset is synthetic and generated from manually designed threshold rules. It is intended for prototyping the machine learning and embedded deployment workflow.

This project should not be interpreted as a real aircraft monitoring or safety system. It is an educational embedded AI prototype inspired by aerospace condition monitoring concepts.
