# Project Report: TinyML Embedded Condition Monitor

## 1. Project Goal

TinyML Embedded Condition Monitor is an educational embedded AI prototype for sensor-based condition monitoring.

The goal of the project is to demonstrate an end-to-end workflow where sensor data is collected, processed, used for lightweight machine learning, and finally deployed back onto an ESP32-based embedded system.

The system classifies the current sensor state into one of three conditions:

- `normal`
- `warning`
- `critical`

This is not a real safety-critical monitoring, navigation, or control system. It is an educational prototype combining embedded AI, TinyML-style model development, real sensor data collection, and interpretable microcontroller firmware.

---

## 2. Motivation

Many cyber-physical monitoring systems need to make decisions close to the physical system they observe. Sending all data to a cloud system is not always ideal because embedded systems may have constraints such as:

- limited power
- limited bandwidth
- limited compute resources
- need for local response
- need for interpretable behavior

This project explores a small embedded monitoring pipeline where an ESP32 reads sensor data, performs local classification, and provides immediate visual and audible feedback.

The project is designed to show the connection between:

```text
sensor data → machine learning model → interpretable rules → embedded firmware → hardware feedback
```

---

## 3. Hardware System

The hardware prototype is built around an ESP32-based sensor node.

Main components:

- ESP32 DevKit / ESP-WROOM-32
- BME280 temperature, pressure, and humidity sensor
- BH1750 light sensor
- VL53L0X-compatible Time-of-Flight distance sensor
- SSD1306 OLED display
- NeoPixel LEDs
- buzzer
- breadboard and jumper wires

The ESP32 reads sensor values over I2C and uses output devices to show the predicted condition.

Output behavior:

| Condition | OLED | NeoPixel | Buzzer |
|---|---|---|---|
| `normal` | Shows stable status | Green | Off |
| `warning` | Shows warning cause | Yellow / orange | Off |
| `critical` | Shows critical cause | Red | Beep alert |

Detailed wiring information is documented in:

```text
docs/hardware_setup.md
```

---

## 4. Sensor Features

The full data pipeline logs the following features:

| Feature | Source | Description |
|---|---|---|
| `temperature_c` | BME280 | Temperature in Celsius |
| `pressure_hpa` | BME280 | Atmospheric pressure in hPa |
| `humidity_percent` | BME280 | Relative humidity percentage |
| `light_lux` | BH1750 | Ambient light intensity |
| `distance_cm` | VL53L0X-compatible sensor | Short-range distance |
| `object_detected` | Derived from distance reading | Binary valid-object flag |

The final embedded-friendly model uses:

```text
humidity_percent
light_lux
distance_cm
object_detected
```

Temperature and pressure are still logged, but they are not used in the final embedded-friendly firmware logic because they can drift with room and environmental conditions.

---

## 5. Machine Learning Workflow

The project started with a synthetic machine learning pipeline.

The synthetic stage included:

1. generating synthetic sensor data
2. training a Decision Tree classifier
3. evaluating the model
4. generating confusion matrix and feature importance plots
5. exporting readable decision rules

This stage was useful because it created the full software structure before the real hardware data was available.

Main synthetic files:

```text
data/synthetic_sensor_data.csv
ml/generate_synthetic_data.py
ml/train_model.py
ml/evaluate_model.py
ml/export_rules.py
models/decision_tree_model.joblib
results/confusion_matrix.png
results/feature_importance.png
results/tree_rules.txt
```

However, synthetic data was only the first step. The project later showed that a model trained only on synthetic data did not transfer well to real sensor measurements.

---

## 6. Real Sensor Data Collection

After the synthetic pipeline was working, real sensor data was collected from the ESP32 hardware prototype.

A Python serial logging script was used to save ESP32 Serial output into CSV files:

```text
ml/log_serial_data.py
```

The initial real dataset was created from controlled scenario logs, including:

- normal baseline
- warning distance
- critical close distance
- warning low light
- critical dark
- bright light
- warm/humid condition

These logs were merged into:

```text
data/real_labeled_sensor_data.csv
```

The real dataset included both sensor features and labels:

- `normal`
- `warning`
- `critical`

This moved the project from a simulated ML workflow to a real hardware-data workflow.

---

## 7. Synthetic-to-Real Gap

One of the most important findings of the project was the difference between synthetic sensor data and real sensor behavior.

The synthetic-trained model and initial real-trained model were evaluated on the same 25% stratified holdout from the initial real sensor dataset.

Comparison result:

```text
Evaluation samples: 53
Synthetic-trained model accuracy: 0.2830
Real-trained model accuracy:      1.0000
```

This showed that the synthetic data was useful for building the pipeline, but it did not fully represent the collected ESP32 sensor distribution.

This is an important engineering lesson from the project:

```text
A synthetic dataset can help build the workflow, but its distribution should be checked against real sensor data before drawing conclusions about hardware behavior.
```

The comparison is documented through:

```text
ml/compare_synthetic_real_models.py
results/synthetic_model_on_real_confusion_matrix.png
results/real_model_on_real_confusion_matrix.png
```

The real-trained `1.0000` score is a within-dataset holdout result and should not be interpreted as independent recording-session or environment validation.

---

## 8. Round2 Real Dataset

To improve the quality of the real-data workflow, a second round of real sensor data was collected.

The Round2 data was collected in a shorter time window and under more controlled conditions to reduce environmental drift.

Round2 dataset output:

```text
data/real_labeled_sensor_data_round2.csv
```

Round2 dataset size:

```text
total samples: 1811
normal: 607
warning: 798
critical: 406
```

Approximate feature ranges:

```text
temperature: 26.49 to 30.48 C
pressure: 839.69 to 839.93 hPa
humidity: 19.21 to 78.05 %
light: 1.67 to 293.33 lux
distance: 6.10 to 100.00 cm
```

The Round2 dataset was filtered scenario-specifically to create cleaner embedded-deployment behavior.

Important improvements included:

- keeping warning-distance samples in a medium-distance range
- keeping critical close-distance samples below the critical threshold
- using dark samples for critical low-light behavior
- adding normal medium-light data
- adding warm/humid high-light data

These additions helped prevent the model from over-associating medium light or high light with the wrong class. The scenario-specific filtering also creates relatively clean class boundaries and should be considered when interpreting the model score.

---

## 9. Embedded-Friendly Model

The final embedded-friendly model is a Decision Tree trained on the filtered Round2 real dataset.

Training script:

```text
ml/train_real_embedded_model_round2.py
```

Model output:

```text
models/real_embedded_decision_tree_model_round2.joblib
```

Exported rules:

```text
results/real_embedded_tree_rules_round2.txt
```

Round2 row-level holdout performance:

```text
Holdout samples: 453
Accuracy: 0.9934

critical precision/recall/f1: 1.0000 / 1.0000 / 1.0000
normal precision/recall/f1:   1.0000 / 0.9803 / 0.9900
warning precision/recall/f1:  0.9852 / 1.0000 / 0.9926
```

The evaluation is reproducible with:

```text
ml/evaluate_real_embedded_model_round2.py
results/round2_embedded_metrics.txt
results/round2_embedded_confusion_matrix.png
```

This score comes from a stratified row-level holdout drawn from the same curated Round2 dataset used during training. It is not independent recording-session or environment validation.

The Decision Tree was selected because it is:

- lightweight
- interpretable
- suitable for small real datasets
- easy to debug
- easy to export as readable rules
- easy to convert into embedded `if-else` logic

---

## 10. Learned Rules vs Manually Adapted Embedded Logic

The trained Round2 Decision Tree exported useful thresholds for light, humidity, and distance.

However, the raw learned tree checked `light_lux` before `distance_cm`. This was mathematically valid for the collected dataset, but it was not ideal for the physical embedded demo.

In the hardware demo, close-object proximity was intentionally given immediate priority. For example, if an object is very close to the sensor, the firmware should classify the condition as `critical` even if the light level is high.

Because of this, the ESP32 firmware uses manually adapted threshold logic informed by the learned Decision Tree and the controlled scenario definitions.

The final firmware checks:

1. close object → `critical`
2. medium-distance object → `warning`
3. very low light → `critical`
4. low light → `warning`
5. high humidity → `warning`
6. otherwise → `normal`

This means the firmware is not a direct line-by-line copy of the exported tree. It combines model-informed thresholds with manually chosen scenario boundaries and an explicit proximity-first evaluation order for the hardware demo.

This is documented as:

```text
decision-tree-informed, manually adapted embedded threshold logic
```

This design decision makes the difference between the offline model and the deployed firmware explicit. For this prototype, the rule order is a manual engineering choice rather than a direct export of the trained tree.

---

## 11. ESP32 Deployment

The final firmware is located at:

```text
firmware/sensor_logger/sensor_logger.ino
```

The firmware performs:

- sensor initialization
- BME280 reading
- BH1750 reading
- VL53L0X-compatible distance reading
- embedded condition prediction
- prediction reason generation
- Serial CSV output
- OLED status display
- NeoPixel status colors
- buzzer alert for critical condition

Example Serial output format:

```text
temperature_c,pressure_hpa,humidity_percent,light_lux,distance_cm,object_detected,predicted_condition,prediction_reason
```

Example row:

```text
27.14,840.60,15.87,155.00,6.20,1,critical,Close Object
```

The deployed prototype demonstrates a complete edge-AI loop:

```text
real sensor readings → embedded inference → local visual/audio feedback
```

---

## 12. Why Not Use a Neural Network as the Main Model?

A neural network is not used as the main deployment model because the current dataset is small, controlled, and scenario-based.

For this project stage, a Decision Tree is stronger because it is:

- more interpretable
- easier to validate
- easier to deploy on ESP32
- better aligned with rule export
- easy to inspect and test
- more appropriate for the available real dataset size

A small neural network, such as an MLP, could be added later as an optional comparison baseline. However, it should not replace the Decision Tree as the main embedded deployment model unless more diverse real-world data is collected.

For the current project, the Decision Tree remains the main model.

---

## 13. Limitations

This project has several limitations:

- the system is not a real safety-critical monitoring system
- real data was collected in controlled indoor conditions
- labels are scenario-based
- the dataset is still relatively small
- Round2 filtering intentionally creates cleaner class boundaries
- the Round2 `0.9934` result is a row-level holdout from the same curated dataset used during training
- the system has not been tested across many rooms or sensor placements
- firmware thresholds are tuned to the current prototype and environment
- real-world reliability would require more diverse testing

The strong model scores should be interpreted as controlled prototype results, not as proof of general safety reliability.

---

## 14. Future Work

Possible future improvements:

- collect a small robustness test dataset in a different room or lighting condition
- test the firmware under more varied sensor placements
- add additional demo videos or GIFs under more varied conditions
- improve or rotate/crop OLED photos
- add an optional MLP baseline for comparison only
- document lessons learned from synthetic-to-real transfer
- keep a future recording session fully separate as an independent validation set

The next recommended improvement is a small robustness test rather than retraining the entire pipeline immediately.

---

## 15. Conclusion

TinyML Embedded Condition Monitor demonstrates a complete embedded AI workflow from synthetic data generation to real ESP32 hardware deployment.

The project shows several important engineering ideas:

- synthetic data is useful for pipeline development
- the collected real sensor distribution differed substantially from the synthetic distribution
- interpretable models are valuable for embedded deployment
- learned rules may need deployment-aware adaptation
- local hardware feedback makes the system easier to demonstrate and debug

The final result is an embedded AI prototype that connects machine learning, sensor data, ESP32 firmware, and physical feedback devices into one end-to-end system.

## Hardware Demo Video

A short hardware demonstration video is included in:

`docs/media/tinyml_hardware_demo.mp4`

The video shows the completed ESP32-based TinyML monitoring prototype in operation.

The demo includes the full hardware setup and transitions into warning or critical output states as the controlled conditions are changed. It provides additional evidence that the project was tested as an integrated embedded hardware prototype, not only as a software model.
