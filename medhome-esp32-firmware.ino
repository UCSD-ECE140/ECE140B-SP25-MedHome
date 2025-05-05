#include "WiFi.h"
#include "MAX30105.h"
#include "heartRate.h"
#include "spo2_algorithm.h"
#include <HTTPClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

#define WIFI_NETWORK "333"
#define WIFI_PASSWORD "Cindy2017"
#define WIFI_TIMEOUT_MS 20000
#define BUTTON_PIN 4
#define SAMPLE_BLOCK 100
#define TOTAL_SAMPLES 500

uint32_t irBuffer[SAMPLE_BLOCK];
uint32_t redBuffer[SAMPLE_BLOCK];
int pressed = 0;

LiquidCrystal_I2C lcd(0x27, 16, 2);

MAX30105 particleSensor;

void connectToWiFi() {
  delay(100);
  Serial.print("Connecting to WiFi");
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_NETWORK, WIFI_PASSWORD);

  unsigned long startAttemptTime = millis();

  while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < WIFI_TIMEOUT_MS) {
    Serial.print(".");
    delay(100);
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Failed To Connect!");
  } 
  else {
    Serial.print("Connected To: ");
    Serial.println(WIFI_NETWORK);
  }
}

void postRequest() {
  const char* serverURL = "https://ece140b-sp25-medhome.onrender.com/tempdata";

  HTTPClient http;
  http.begin(serverURL);
  http.addHeader("Content-Type", "application/json");

    // Create JSON payload
  String jsonData = "{\"temperature\": 24.5}";

    // Send POST request
  int httpResponseCode = http.POST(jsonData);

    // Print the response
  Serial.print("HTTP Response code: ");
  Serial.println(httpResponseCode);
  String response = http.getString();
  Serial.println(response);

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
    Serial.println("Beginning Analysis");
    int avgHR = 0, avgSpO2 = 0, weight, bpS, bpD;
    readVitalsAverage(avgHR, avgSpO2);
    readWeight(weight);
    readBP(bpS, bpD);

    Serial.print("Average Heart Rate (BPM): ");
    Serial.println(avgHR);
    Serial.print("Average SpO₂ (%): ");
    Serial.println(avgSpO2);
    Serial.print("Weight: ");
    Serial.println(weight);
    Serial.print("Blood Pressure: ");
    Serial.print(bpS);
    Serial.print("/");
    Serial.println(bpD);
    
    delay(1000); // Debounce delay
  } else if (pressed == 0) {
    Serial.println("Press the button to start vitals measurement...");
    pressed = 1;
  } else if (pressed == 1) {
    delay(10);
  }
  
}
