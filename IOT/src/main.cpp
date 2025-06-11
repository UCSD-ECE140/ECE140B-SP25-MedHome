#include "WiFi.h"
#include "MAX30105.h"
#include "HX711.h"
#include "heartRate.h"
#include <AutoConnect.h>
#include "spo2_algorithm.h"
#include <HTTPClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Alice has device with serial number 1
#define WIFI_TIMEOUT_MS 20000
#define BUTTON_PIN 13
#define HX711_DT 12
#define HX711_SCK 14
#define BP_BUTTON 27
#define SAMPLE_BLOCK 100
#define TOTAL_SAMPLES 500
#define DISPLAY_TIME 2000
#define theZero 53791880.00
#define theRatio 300170.35

String SERIAL_NUMBER = "MH-830B35DF"; 
uint32_t irBuffer[SAMPLE_BLOCK];
uint32_t redBuffer[SAMPLE_BLOCK];
int pressed = 0;

LiquidCrystal_I2C lcd(0x27, 16, 2); 

MAX30105 particleSensor;
HX711 theScale; 

AutoConnect portal;
AutoConnectConfig config;

bool connectToWiFi() {
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
    return true; 
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
      return true; 
    } else {
      Serial.println("Failed to connect to WiFi");
      return false; 
    }
  }
}

bool postRequest(int avgHR, int avgSpO2, float weight, int bpS, int bpD) {
  const char* serverURL = "https://medhome.onrender.com/avgHRavgSpO2weightbpSbpD";

  HTTPClient http;
  http.begin(serverURL);
  http.addHeader("Content-Type", "application/json");

  // Create JSON payload
  String jsonData = "{";
  jsonData += "\"serial_num\": \"" + String(SERIAL_NUMBER) + "\","; 
  jsonData += "\"avgHR\":" + String(avgHR) + ",";
  jsonData += "\"avgSpO2\":" + String(avgSpO2) + ",";
  jsonData += "\"weight\":" + String(weight) + ",";
  jsonData += "\"bpS\":" + String(bpS) + ",";
  jsonData += "\"bpD\":" + String(bpD);
  jsonData += "}";
  Serial.println(jsonData); 
  // Send POST request
  int httpResponseCode = http.POST(jsonData);

  Serial.println(httpResponseCode); 

  if(httpResponseCode != 200) {
    http.end(); 
    return false;  
  }

  else {
    // Print the response
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);
    String response = http.getString();
    Serial.println(response);
    delay(750);

    http.end();

    return true; 
  }
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
    // Serial.println(totalValue);  
    delay(10); 
  }

  weight = (totalValue - theZero)/theRatio; 
  Serial.println(weight); 
}

void readBP(int &bpS, int &bpD) {
    digitalWrite(BP_BUTTON, HIGH); 
    delay(500); 
    digitalWrite(BP_BUTTON, LOW); 
    delay(1000 * 60); // Wait a minute

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
  delay(1000); 
  Serial.begin(115200);
  delay(1000); 
  Wire.begin(); // SDA, SCK 
  // checkAddress(); 
  LCDSetup(); 
  delay(1000); 

  lcd.setCursor(0, 0);
  lcd.print("Connecting to");
  lcd.setCursor(0, 1);
  lcd.print("WiFi...");

  while(!connectToWiFi()); 
  delay(DISPLAY_TIME);
  lcd.clear();

  Serial.begin(115200);
  pinMode(BUTTON_PIN, INPUT); // Active LOW button
  pinMode(BP_BUTTON, OUTPUT); 

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
  delay(DISPLAY_TIME);
  lcd.clear();

  lcd.setCursor(0, 0);
  lcd.print("Press button");
  lcd.setCursor(0, 1);
  lcd.print("to begin."); 
}

void loop() {
  pressed = digitalRead(BUTTON_PIN); 

  if (pressed == HIGH) {
    lcd.clear(); 
    int avgHR = 0, avgSpO2 = 0, bpS = 0, bpD = 0;
    float weight = 0; 
    Serial.println("Beginning Analysis");
    lcd.setCursor(0, 0);
    lcd.print("Beginning");
    lcd.setCursor(0, 1); 
    lcd.print("Analysis"); 
    delay(DISPLAY_TIME);
    lcd.clear();

    lcd.setCursor(0, 0);
    lcd.print("Reading Oxygen");
    Serial.println("Reading Heartrate");
    lcd.setCursor(0, 1);
    lcd.print("and Heartrate");
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
    delay(DISPLAY_TIME);
    lcd.clear();

    lcd.setCursor(0, 0);
    lcd.print("Avg SpO2: ");
    Serial.print("Average SpO₂ (%): ");
    lcd.print(avgSpO2);
    Serial.println(avgSpO2);
    delay(DISPLAY_TIME);
    lcd.clear();

    lcd.setCursor(0, 0);
    lcd.print("Weight: ");
    Serial.print("Weight: ");
    lcd.print(weight);
    Serial.println(weight);
    delay(DISPLAY_TIME);
    lcd.clear();

    lcd.setCursor(0, 0);
    lcd.print("Blood Pressure: ");
    lcd.setCursor(0, 1); 
    lcd.print(bpS); 
    lcd.print("/"); 
    lcd.print(bpD); 
    Serial.print("Blood Pressure: ");
    delay(DISPLAY_TIME); 
    lcd.clear(); 
 
    bool checkPost = postRequest(avgHR, avgSpO2, weight, bpS, bpD);

    int attemptCount = 0; 
    while(!checkPost) {
      Serial.println("Data sent unsuccessfully."); 
      lcd.setCursor(0, 0); 
      lcd.print("Data failed"); 
      lcd.setCursor(0, 1); 
      lcd.print("to send."); 
      delay(DISPLAY_TIME); 
      lcd.clear(); 

      lcd.setCursor(0, 0); 
      lcd.print("Trying to"); 
      lcd.setCursor(0, 1); 
      lcd.print("send again."); 
      delay(DISPLAY_TIME); 
      lcd.clear(); 

      checkPost = postRequest(avgHR, avgSpO2, weight, bpS, bpD);

      attemptCount++; 
      if (attemptCount > 10) {
        Serial.println("Succesfully sent data to server."); 
        lcd.setCursor(0, 0); 
        lcd.print("Timeout, please"); 
        lcd.setCursor(0, 1); 
        lcd.print("restart device."); 
        delay(DISPLAY_TIME); 
        while(1); 
      }
    }

    Serial.println("Succesfully sent data to server."); 
    lcd.setCursor(0, 0); 
    lcd.print("Data sent"); 
    lcd.setCursor(0, 1); 
    lcd.print("succesfully!"); 
    delay(DISPLAY_TIME); 

    delay(1000);
  } 
 
}
