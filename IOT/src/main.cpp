#include "WiFi.h"
#include "MAX30105.h"
#include "heartRate.h"
#include <AutoConnect.h>
#include "spo2_algorithm.h"
#include <HTTPClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

#define WIFI_TIMEOUT_MS 20000
#define BUTTON_PIN 4
#define SAMPLE_BLOCK 100
#define TOTAL_SAMPLES 500

uint32_t irBuffer[SAMPLE_BLOCK];
uint32_t redBuffer[SAMPLE_BLOCK];
int pressed = 0;

LiquidCrystal_I2C lcd(0x27, 16, 2);

MAX30105 particleSensor;

AutoConnect portal;
AutoConnectConfig config;

void connectToWiFi() {
  delay(100);
  Serial.print("Connecting to WiFi");
  config.autoReconnect = true;
  config.apid = "ESP32_Setup";
  config.psk = "12345678";
  portal.config(config);
  portal.begin();
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("Connected to " + WiFi.SSID());
    Serial.println(WiFi.localIP());
  }
  else {
    portal.begin();
    Serial.println("Connecting to WiFi...");
    unsigned long startTime = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - startTime < WIFI_TIMEOUT_MS) {
      delay(1000);
      Serial.print(".");
    }
    if (WiFi.status() == WL_CONNECTED) {
      Serial.println("Connected to " + WiFi.SSID());
      Serial.println(WiFi.localIP());
    } else {
      Serial.println("Failed to connect to WiFi");
    }
  }
}

void postRequest(int avgHR, int avgSpO2, int weight, int bpS, int bpD) {
  const char* serverURL = "https://ece140b-sp25-medhome.onrender.com/tempdata";

  HTTPClient http;
  http.begin(serverURL);
  http.addHeader("Content-Type", "application/json");

  // Create JSON payload
  String jsonData = "{";
  jsonData += "\"heart_rate\":" + String(avgHR) + ",";
  jsonData += "\"spo2\":" + String(avgSpO2) + ",";
  jsonData += "\"weight\":" + String(weight) + ",";
  jsonData += "\"bp_systolic\":" + String(bpS) + ",";
  jsonData += "\"bp_diastolic\":" + String(bpD);
  jsonData += "}";

  // Send POST request
  int httpResponseCode = http.POST(jsonData);

  // Print the response
  Serial.print("HTTP Response code: ");
  Serial.println(httpResponseCode);
  String response = http.getString();
  lcd.setCursor(0, 0);
  lcd.print(response);
  Serial.println(response);
  delay(750);

  http.end();
}

void getRequest() {
  const char* serverURL = "https://ece140b-sp25-medhome.onrender.com/hello";

  HTTPClient http;
  http.begin(serverURL);
    
  int httpResponseCode = http.GET();

  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.println("Response:");
    Serial.println(response);
  } else {
    Serial.print("Error on GET: ");
    Serial.println(httpResponseCode);
  }

  http.end();
}

void LCDSetup() {
  lcd.init();
  lcd.backlight();
  lcd.clear();
}

// === FUNCTION: Reads 500 samples and returns average HR and SpO2 ===
void readVitalsAverage(int &averageHR, int &averageSpO2) {
  int32_t heartRate, spo2;
  int8_t validHR, validSpO2;

  int hrSum = 0, spo2Sum = 0, validCount = 0;

  for (int batch = 0; batch < TOTAL_SAMPLES / SAMPLE_BLOCK; batch++) {
    for (int i = 0; i < SAMPLE_BLOCK; i++) {
      while (!particleSensor.available()) {
        particleSensor.check();
      }
      redBuffer[i] = particleSensor.getRed();
      irBuffer[i] = particleSensor.getIR();
      particleSensor.nextSample();
    }

    maxim_heart_rate_and_oxygen_saturation(irBuffer, SAMPLE_BLOCK, redBuffer,
                                           &spo2, &validSpO2, &heartRate, &validHR);

    if (validHR && validSpO2 && heartRate > 30 && heartRate < 180 && spo2 > 80 && spo2 <= 100) {
      hrSum += heartRate;
      spo2Sum += spo2;
      validCount++;
    }

    delay(50); // brief delay between chunks
  }

  if (validCount > 0) {
    averageHR = hrSum / validCount;
    averageSpO2 = spo2Sum / validCount;
  } else {
    averageHR = -1;
    averageSpO2 = -1;
  }
}

void readWeight(int &weight) {
  Serial.println("200 KG");
  weight = 200;
}

void readBP(int &bpS, int &bpD) {
    Serial.println("120 / 80");
    bpS = 120;
    bpD = 80;
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  connectToWiFi();
  LCDSetup();
  Serial.begin(115200);
  pinMode(BUTTON_PIN, INPUT_PULLUP); // Active LOW button

  if (!particleSensor.begin(Wire, I2C_SPEED_STANDARD)) {
    Serial.println("MAX30102 not found. Check wiring.");
    while (1);
  }
  particleSensor.setup(); // Recommended defaults
  
}

void loop() {
  
  if (digitalRead(4) == HIGH) {
    int avgHR = 0, avgSpO2 = 0, weight, bpS, bpD;
    Serial.println("Beginning Analysis");
    lcd.setCursor(0, 0);
    lcd.print("Beginning Analysis");
    delay(1000);
    lcd.clear();

    lcd.setCursor(0, 0);
    lcd.print("Reading Vitals...");
    Serial.println("Reading Vitals...");
    delay(1000);
    readVitalsAverage(avgHR, avgSpO2);
    lcd.clear();

    lcd.setCursor(0, 0);
    lcd.print("Reading Weight...");
    Serial.println("Reading Weight...");
    delay(1000);
    readWeight(weight);
    lcd.clear();

    lcd.setCursor(0, 0);
    lcd.print("Reading BP...");
    Serial.println("Reading Blood Pressure...");
    delay(1000);
    readBP(bpS, bpD);
    lcd.clear();

    lcd.setCursor(0, 0);
    lcd.print("Avg HR: ");
    Serial.print("Average Heart Rate (BPM): ");
    lcd.print(avgHR);
    Serial.println(avgHR);
    delay(1000);
    lcd.clear();

    lcd.setCursor(0, 0);
    lcd.print("Avg SpO2: ");
    Serial.print("Average SpO₂ (%): ");
    lcd.print(avgSpO2);
    Serial.println(avgSpO2);
    delay(1000);
    lcd.clear();

    lcd.setCursor(0, 0);
    lcd.print("Weight: ");
    Serial.print("Weight: ");
    lcd.print(weight);
    Serial.println(weight);
    delay(1000);
    lcd.clear();

    lcd.setCursor(0, 0);
    lcd.print("Blood Pressure: ");
    Serial.print("Blood Pressure: ");

    lcd.setCursor(0, 1);
    lcd.print(bpS);
    lcd.print("/");
    lcd.print(bpD);
    Serial.print(bpS);
    Serial.print("/");
    Serial.println(bpD);
    delay(1000);
    lcd.clear();
    
    postRequest(avgHR, avgSpO2, weight, bpS, bpD);

    delay(1000);
  } 
  
  else if (pressed == 0) {
    Serial.println("Press the button to start vitals measurement...");
    pressed = 1;
  } 
  
  else if (pressed == 1) {
    delay(10);
  }
  
}
