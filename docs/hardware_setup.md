# Hardware Setup

## Overview

This project uses an ESP32-based embedded sensor node for an educational TinyML / Embedded AI condition monitoring prototype inspired by aerospace-style monitoring systems.

The hardware collects environmental, ambient light, and short-range proximity data, runs lightweight embedded inference on the ESP32, and provides local feedback using:

- OLED display
- NeoPixel LEDs
- buzzer alert

The current hardware prototype has been built and tested with real sensors.

---

## Hardware Components

| Component | Purpose |
|---|---|
| ESP32 DevKit / ESP-WROOM-32 | Main microcontroller and embedded inference target |
| BME280 | Measures temperature, pressure, and humidity |
| BH1750 | Measures ambient light intensity in lux |
| VL53LDK / VL53L0X-compatible ToF sensor | Measures short-range distance and object proximity |
| SSD1306 OLED display | Shows live status, cause, and sensor readings |
| NeoPixel LEDs | Shows visual condition status |
| Buzzer | Provides audible alert for critical condition |
| Breadboard and jumper wires | Prototype wiring |
| External breadboard power rail/module | Used for powering the hardware setup |

---

## Pin Mapping Summary

| Component | Signal | ESP32 Pin | Notes |
|---|---:|---:|---|
| BME280 | SDA | GPIO 21 | Shared I2C bus |
| BME280 | SCL | GPIO 22 | Shared I2C bus |
| BH1750 | SDA | GPIO 21 | Shared I2C bus |
| BH1750 | SCL | GPIO 22 | Shared I2C bus |
| VL53LDK / VL53L0X | SDA | GPIO 21 | Shared I2C bus |
| VL53LDK / VL53L0X | SCL | GPIO 22 | Shared I2C bus |
| SSD1306 OLED | SDA | GPIO 21 | Shared I2C bus |
| SSD1306 OLED | SCL | GPIO 22 | Shared I2C bus |
| NeoPixel LEDs | DIN | GPIO 27 | 3 LEDs used |
| Buzzer | Signal | GPIO 23 | Beeps only for critical condition |
| All modules | GND | ESP32 GND | Common ground required |
| Sensor modules | VCC | 3.3V | Depending on module rating |
| NeoPixel LEDs | VCC | External rail / suitable supply | Common GND with ESP32 required |

---

## I2C Bus

The BME280, BH1750, VL53LDK / VL53L0X, and OLED display share the same I2C bus.

```text
SDA: GPIO 21
SCL: GPIO 22
```

I2C addresses used in the current firmware:

| Device | I2C Address |
|---|---:|
| BME280 | `0x76` |
| BH1750 | `0x23` |
| VL53LDK / VL53L0X | `0x29` |
| SSD1306 OLED | `0x3C` |

---

## Sensor Roles

### BME280

The BME280 provides:

- temperature in Celsius
- pressure in hPa
- relative humidity in percent

In the final embedded-friendly inference logic, humidity is the main BME280 feature used directly by the ESP32 threshold rules.

Related feature:

```text
humidity_percent
```

Temperature and pressure are still logged and displayed, but they are not part of the final embedded-friendly Round2 model.

---

### BH1750

The BH1750 measures ambient light intensity in lux.

Related feature:

```text
light_lux
```

Light is used to detect low-light and very-low-light conditions.

Approximate interpretation during testing:

| Lux Range | Meaning |
|---:|---|
| 0–10 lux | Very dark |
| 10–35 lux | Low light |
| 30–100 lux | Dim / medium indoor light |
| 100–300 lux | Brighter indoor light |

---

### VL53LDK / VL53L0X Distance Sensor

The distance sensor is used as a short-range proximity sensor.

Related features:

```text
distance_cm
object_detected
```

The firmware uses an `object_detected` flag to avoid treating invalid or out-of-range measurements as real object distances.

Example interpretation:

| Sensor Situation | `object_detected` | `distance_cm` |
|---|---:|---:|
| No valid object detected | 0 | 100 |
| Object around 45 cm | 1 | 45 |
| Object around 20 cm | 1 | 20 |

In the final embedded inference logic:

| Condition | Interpretation |
|---|---|
| object detected and distance `<= 28.75 cm` | critical |
| object detected and distance `<= 50.00 cm` | warning |

---

## Output Devices

### SSD1306 OLED Display

The OLED display shows:

- project header
- predicted condition
- cause/reason for warning or critical state
- live sensor values

Final displayed status behavior:

| Condition | OLED Message |
|---|---|
| `normal` | `System stable` |
| `warning` | `Cause:<reason>` |
| `critical` | `Cause:<reason>` |

The OLED used in this prototype is a two-color SSD1306 display:

- top band: yellow
- lower area: blue

Because of this display layout, the final firmware moves the main `STATUS` line lower on the screen to avoid unwanted yellow tint.

---

### NeoPixel LEDs

The prototype uses 3 NeoPixel LEDs.

NeoPixel data pin:

```text
GPIO 27
```

Status colors:

| Condition | NeoPixel Color |
|---|---|
| `normal` | Green |
| `warning` | Yellow / orange |
| `critical` | Red |

Only 3 LEDs are used because they clearly show the system state while keeping current consumption lower.

Important: NeoPixel GND must be connected to ESP32 GND.

---

### Buzzer

The buzzer signal pin is connected to:

```text
GPIO 23
```

The buzzer is used only for the `critical` condition.

| Condition | Buzzer |
|---|---|
| `normal` | Off |
| `warning` | Off |
| `critical` | Beep alert |

---

## Embedded Inference Logic

The firmware uses safety-prioritized embedded threshold logic derived from the trained Round2 decision tree rules.

Final firmware logic:

```cpp
if (object_detected == 1) {
  if (distance_cm <= 28.75) {
    predicted_condition = "critical";
    prediction_reason = "Close Object";
    return;
  } else if (distance_cm <= 50.00) {
    predicted_condition = "warning";
    prediction_reason = "Medium Dist";
    return;
  }
}

if (light_lux <= 10.00) {
  predicted_condition = "critical";
  prediction_reason = "Very Low Light";
  return;
}

if (light_lux <= 35.00) {
  predicted_condition = "warning";
  prediction_reason = "Low Light";
  return;
}

if (humidity_percent > 29.50) {
  predicted_condition = "warning";
  prediction_reason = "High Humidity";
  return;
}

predicted_condition = "normal";
prediction_reason = "Safe";
```

The firmware intentionally prioritizes proximity before light and humidity so that close-object detection has immediate priority in the embedded demo.

---

## Serial Output

The firmware outputs live CSV-style rows over Serial.

Columns:

```text
temperature_c,pressure_hpa,humidity_percent,light_lux,distance_cm,object_detected,predicted_condition,prediction_reason
```

Example:

```text
27.14,840.60,15.87,155.00,6.20,1,critical,Close Object
```

---

## Firmware File

Main firmware file:

```text
firmware/sensor_logger/sensor_logger.ino
```

The firmware includes:

- BME280 reading
- BH1750 reading
- VL53LDK / VL53L0X distance reading
- embedded condition prediction
- prediction reason
- Serial CSV output
- OLED live status display
- NeoPixel status colors
- buzzer alert for critical condition

---

## Required Arduino Libraries

Required Arduino libraries:

- Adafruit BME280 Library
- Adafruit Unified Sensor
- BH1750
- Adafruit VL53L0X
- Adafruit NeoPixel
- Adafruit GFX Library
- Adafruit SSD1306

Firmware includes:

```cpp
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <BH1750.h>
#include <Adafruit_VL53L0X.h>
#include <Adafruit_NeoPixel.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
```

---

## Common Ground Requirement

All modules must share a common ground with the ESP32.

This is especially important when using:

- external breadboard power rail
- NeoPixel LEDs
- buzzer
- sensor modules

Without common ground, signal pins may behave unpredictably even if each module appears to be powered.

---

## Arduino Sketch Folder Note

Arduino IDE compiles all `.ino` files inside the same sketch folder.

Do not keep backup `.ino` files inside:

```text
firmware/sensor_logger/
```

Otherwise, Arduino IDE may produce duplicate definition errors such as:

```text
redefinition of 'void setup()'
redefinition of 'void loop()'
redefinition of 'Adafruit_BME280 bme'
```

Recommended options:

- move backup firmware files outside the sketch folder
- rename backups with a non-`.ino` extension
- place old versions under a separate archive folder

---

## Hardware Demo Photos

Hardware demo photos are stored in:

```text
assets/hardware/
```

Current photos:

```text
assets/hardware/full_setup.jpg
assets/hardware/oled_normal.jpg
assets/hardware/oled_warning.jpg
assets/hardware/oled_critical.jpg
assets/hardware/neopixel_critical.jpg
```

These photos show the physical ESP32 prototype, OLED status output, and NeoPixel critical alert behavior.

---

## Safety Note

This project is not a real aircraft safety or flight control system.

It is an educational embedded AI prototype inspired by aerospace-style condition monitoring, designed to demonstrate:

- sensor data collection
- TinyML-style model development
- real hardware deployment
- interpretable embedded inference
- local visual and audible feedback
