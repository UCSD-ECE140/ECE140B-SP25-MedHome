#include "WiFi.h"
#include "MAX30105.h"
#include "HX711.h"
#include "heartRate.h"
#include <AutoConnect.h>
#include "spo2_algorithm.h"
#include <HTTPClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

#define SERIAL_NUMBER 1 
// Alice has device with serial number 1
#define WIFI_TIMEOUT_MS 20000
#define BUTTON_PIN 13
#define HX711_DT 12
#define HX711_SCK 14
#define SAMPLE_BLOCK 100
#define TOTAL_SAMPLES 500
#define theSlope 1365.92567568
#define theOffset 197995.84

uint32_t irBuffer[SAMPLE_BLOCK];
uint32_t redBuffer[SAMPLE_BLOCK];
int pressed = 0;

LiquidCrystal_I2C lcd(0x27, 16, 2); 

MAX30105 particleSensor;
HX711 theScale; 

AutoConnect portal;
AutoConnectConfig config;

void connectToWiFi() {
  delay(100);
  Serial.print("Connecting to WiFi");
  config.autoReconnect = true;
  config.apid = "MedHome_WIFI_Setup";
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

void postRequest(int avgHR, int avgSpO2, float weight, int bpS, int bpD) {
  const char* serverURL = "https://medhome.onrender.com/avgHRavgSpO2weightbpSbpD";

  HTTPClient http;
  http.begin(serverURL);
  http.addHeader("Content-Type", "application/json");

  // Create JSON payload
  String jsonData = "{";
  jsonData += "\"serial_number\":" + String(SERIAL_NUMBER) + ","; 
  jsonData += "\"avgHR\":" + String(avgHR) + ",";
  jsonData += "\"avgSpO2\":" + String(avgSpO2) + ",";
  jsonData += "\"weight\":" + String(weight) + ",";
  jsonData += "\"bpS\":" + String(bpS) + ",";
  jsonData += "\"bpD\":" + String(bpD);
  jsonData += "}";

  // Send POST request
  int httpResponseCode = http.POST(jsonData);

  // Print the response
  Serial.print("HTTP Response code: ");
  Serial.println(httpResponseCode);
  String response = http.getString();
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

void readWeight(float &weight) {
  weight = 0; 
  float totalValue = 0; 
  float theReading = 0;
  int sampleRate = TOTAL_SAMPLES / 2;  

  for(int i = 0; i <= sampleRate; i++) { // Read weight scale until reached sample count, TOTAL_SAMPLES
    theReading = theScale.read(); 
    totalValue += abs(theReading);
    Serial.println(totalValue);  
    delay(10); 
  }

  weight = ((totalValue/sampleRate) - theOffset) / theSlope; 
}

void readBP(int &bpS, int &bpD) {
    Serial.println("120 / 80");
    bpS = 120;
    bpD = 80;
}

void checkAddress() {
  Serial.println("Scanning for devices!");

  for (int anAddress = 1; anAddress < 256; anAddress++) {
    Wire.beginTransmission(anAddress);

    if (Wire.endTransmission() == 0) {
      Serial.print("Found Address: ");
      Serial.println(anAddress);
    }
  }
}

void setup() {
  // put your setup code here, to run once:
  delay(2000); 
  Serial.begin(115200);
  Wire.begin(); // SDA, SCK 
  // checkAddress(); 
  connectToWiFi();
  LCDSetup(); 
  delay(500); 
  Serial.begin(115200);
  pinMode(BUTTON_PIN, INPUT); // Active LOW button

  if (!particleSensor.begin(Wire, I2C_SPEED_STANDARD)) {
    Serial.println("MAX30102 not found. Check wiring."); 
  }
  particleSensor.setup(); // Recommended defaults

  theScale.begin(HX711_DT, HX711_SCK); 
  delay(500);  
  Serial.println("Setup Complete."); 

  lcd.setCursor(0, 0);
  lcd.print("Device Setup ");
  lcd.setCursor(0, 1);
  lcd.print("Completed.");
  delay(1000);
  lcd.clear();
}

void loop() {
  pressed = digitalRead(BUTTON_PIN); 
  
  if (pressed == HIGH) {
    int avgHR = 0, avgSpO2 = 0, bpS = 0, bpD = 0;
    float weight = 0; 
    Serial.println("Beginning Analysis");
    lcd.setCursor(0, 0);
    lcd.print("Beginning Analysis");
    delay(1000);
    lcd.clear();

    lcd.setCursor(0, 0);
    lcd.print("Reading Heartrate");
    Serial.println("Reading Heartrate");
    lcd.setCursor(0, 1);
    lcd.print("Reading Oxygen");
    Serial.println("Reading Oxygen");
    delay(1000);
    readVitalsAverage(avgHR, avgSpO2);
    lcd.clear();

    lcd.setCursor(0, 0);
    lcd.print("Reading Weight");
    Serial.println("Reading Weight");
    delay(1000);
    readWeight(weight);
    lcd.clear();

    lcd.setCursor(0, 0);
    lcd.print("Reading Blood"); 
    lcd.setCursor(0, 1);
    lcd.print("Pressure"); 
    Serial.println("Reading Blood Pressure");
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
 
    postRequest(avgHR, avgSpO2, weight, bpS, bpD);

    delay(1000);
  } 
 
}
