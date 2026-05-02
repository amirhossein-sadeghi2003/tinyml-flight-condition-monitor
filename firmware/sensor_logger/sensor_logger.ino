#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <BH1750.h>
#include <Adafruit_VL53L0X.h>
#include <Adafruit_NeoPixel.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

Adafruit_BME280 bme;
BH1750 lightMeter;
Adafruit_VL53L0X lox = Adafruit_VL53L0X();

const float NO_OBJECT_DISTANCE_CM = 100.0;
const float OBJECT_DETECTION_THRESHOLD_CM = 50.0;

#define NEOPIXEL_PIN 27
#define NEOPIXEL_COUNT 3

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define OLED_ADDRESS 0x3C

Adafruit_NeoPixel pixels(
  NEOPIXEL_COUNT,
  NEOPIXEL_PIN,
  NEO_GRB + NEO_KHZ800
);

Adafruit_SSD1306 display(
  SCREEN_WIDTH,
  SCREEN_HEIGHT,
  &Wire,
  OLED_RESET
);

String predictCondition(
  float humidity_percent,
  float light_lux,
  float distance_cm,
  int object_detected
) {
  // Embedded safety-prioritized inference logic
  // Based on Round2 decision tree rules, with proximity prioritized for firmware use.

  if (object_detected == 1) {
    if (distance_cm <= 28.75) {
      return "critical";
    } else if (distance_cm <= 50.00) {
      return "warning";
    }
  }

  if (light_lux <= 10.00) {
    return "critical";
  }

  if (light_lux <= 35.00) {
    return "warning";
  }

  if (humidity_percent > 29.50) {
    return "warning";
  }

  return "normal";
}

void setNeoPixelStatus(String condition) {
  uint32_t color;

  if (condition == "normal") {
    color = pixels.Color(0, 80, 0);      // green
  } else if (condition == "warning") {
    color = pixels.Color(80, 45, 0);     // yellow/orange
  } else if (condition == "critical") {
    color = pixels.Color(100, 0, 0);     // red
  } else {
    color = pixels.Color(0, 0, 0);       // off
  }

  for (int i = 0; i < NEOPIXEL_COUNT; i++) {
    pixels.setPixelColor(i, color);
  }

  pixels.show();
}

void showStatusOnOLED(
  String condition,
  float temperature_c,
  float humidity_percent,
  float light_lux,
  float distance_cm,
  int object_detected
) {
  display.clearDisplay();

  display.setTextColor(SSD1306_WHITE);

  display.setTextSize(1);
  display.setCursor(0, 0);
  display.print("Flight Cond Monitor");

  display.drawLine(0, 10, 127, 10, SSD1306_WHITE);

  display.setTextSize(2);
  display.setCursor(0, 16);

  if (condition == "normal") {
    display.print("NORMAL");
  } else if (condition == "warning") {
    display.print("WARNING");
  } else if (condition == "critical") {
    display.print("CRITICAL");
  } else {
    display.print("UNKNOWN");
  }

  display.setTextSize(1);

  display.setCursor(0, 40);
  display.print("L:");
  display.print(light_lux, 0);
  display.print("lx ");

  display.print("D:");
  display.print(distance_cm, 1);
  display.print("cm");

  display.setCursor(0, 52);
  display.print("H:");
  display.print(humidity_percent, 1);
  display.print("% ");

  display.print("Obj:");
  display.print(object_detected);

  display.display();
}

void showStartupOnOLED() {
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);

  display.setTextSize(1);
  display.setCursor(0, 0);
  display.print("TinyML Flight");

  display.setCursor(0, 12);
  display.print("Condition Monitor");

  display.setCursor(0, 32);
  display.print("Initializing...");

  display.display();
}

void showErrorOnOLED(String errorMessage) {
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);

  display.setTextSize(1);
  display.setCursor(0, 0);
  display.print("SENSOR ERROR");

  display.drawLine(0, 10, 127, 10, SSD1306_WHITE);

  display.setCursor(0, 20);
  display.print(errorMessage);

  display.setCursor(0, 44);
  display.print("Check wiring/I2C");

  display.display();
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  Wire.begin(21, 22);

  pixels.begin();
  pixels.setBrightness(40);
  pixels.clear();
  pixels.show();

  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDRESS)) {
    Serial.println("ERROR: SSD1306 OLED not found at 0x3C");
    setNeoPixelStatus("critical");
    while (1) {
      delay(1000);
    }
  }

  showStartupOnOLED();

  Serial.println("Initializing sensors...");

  if (!bme.begin(0x76)) {
    Serial.println("ERROR: BME280 not found at 0x76");
    setNeoPixelStatus("critical");
    showErrorOnOLED("BME280 not found");
    while (1) {
      delay(1000);
    }
  }

  if (!lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE, 0x23, &Wire)) {
    Serial.println("ERROR: BH1750 not found at 0x23");
    setNeoPixelStatus("critical");
    showErrorOnOLED("BH1750 not found");
    while (1) {
      delay(1000);
    }
  }

  if (!lox.begin(0x29, false, &Wire)) {
    Serial.println("ERROR: VL53LDK/VL53L0X not found at 0x29");
    setNeoPixelStatus("critical");
    showErrorOnOLED("VL53L0X not found");
    while (1) {
      delay(1000);
    }
  }

  Serial.println("Sensors initialized successfully");
  Serial.println("temperature_c,pressure_hpa,humidity_percent,light_lux,distance_cm,object_detected,predicted_condition");

  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.print("Sensors OK");
  display.setCursor(0, 16);
  display.print("Starting inference...");
  display.display();

  delay(1000);
}

void loop() {
  float temperature_c = bme.readTemperature();
  float pressure_hpa = bme.readPressure() / 100.0;
  float humidity_percent = bme.readHumidity();

  float light_lux = lightMeter.readLightLevel();

  VL53L0X_RangingMeasurementData_t measure;
  lox.rangingTest(&measure, false);

  float distance_cm = NO_OBJECT_DISTANCE_CM;
  int object_detected = 0;

  if (measure.RangeStatus != 4) {
    float measured_distance_cm = measure.RangeMilliMeter / 10.0;

    if (measured_distance_cm > 0 && measured_distance_cm <= OBJECT_DETECTION_THRESHOLD_CM) {
      distance_cm = measured_distance_cm;
      object_detected = 1;
    }
  }

  String predicted_condition = predictCondition(
    humidity_percent,
    light_lux,
    distance_cm,
    object_detected
  );

  setNeoPixelStatus(predicted_condition);

  showStatusOnOLED(
    predicted_condition,
    temperature_c,
    humidity_percent,
    light_lux,
    distance_cm,
    object_detected
  );

  Serial.print(temperature_c, 2);
  Serial.print(",");
  Serial.print(pressure_hpa, 2);
  Serial.print(",");
  Serial.print(humidity_percent, 2);
  Serial.print(",");
  Serial.print(light_lux, 2);
  Serial.print(",");
  Serial.print(distance_cm, 2);
  Serial.print(",");
  Serial.print(object_detected);
  Serial.print(",");
  Serial.println(predicted_condition);

  delay(1000);
}