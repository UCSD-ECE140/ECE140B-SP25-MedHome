# ECE140B-SP25:
MedHome – Smart Health Chair

<p align="center">
   <img src="https://github.com/user-attachments/assets/33afbcc2-becf-491b-bcc4-d98b475f572d" width=500px/>
</p>

Welcome to **MedHome**, a smart, sensor-integrated chair designed to monitor your vital signs from the comfort of your home or clinic! This project is being developed for UCSD's ECE140B (Spring 2025) and aims to provide accessible, real-time health monitoring with the help of IoT and smart data analysis. 🚀

---

## 🌟 Ideal Product Vision

Imagine a chair that doubles as a medical diagnostic device. The **ideal MedHome system** integrates:

🩸 **Blood Pressure Monitor**  
🧠 **Oximeter (O2 and Heart Rate)**  
⚖️ **Digital Scale**  

All collected data is:

- 📡 Transmitted via WiFi (ESP32)
- 💽 Stored in a backend database
- 📊 Visualized on a sleek web app
- 🧠 Data analytics algorithms for health feedback
- 👨‍⚕️ Used to notify the user and optionally consult a doctor

---

## 🔨 MVP (Minimum Viable Product)

For this quarter, our MVP includes:

### ✅ Hardware
- ESP32 microcontroller
- Connected oximeter, scale, and BP monitor
- Basic portable kit for all devices

### ✅ Software
- ESP32 sends data via RESTfulAPI over WiFi
- Backend stores user & health data
- Web app displays vitals & graphs
- Basic user authentication & login

---

## 🧰 Required Technologies

### 📟 Electronics
- MAX30102 Oximeter
- HX711 Scale
- Blood Pressure Monitor
- ESP32 (for WiFi & sensor integration)
- Communication protocols: I2C

### 🖧 IOT Diagram
![Software_Flow](https://github.com/user-attachments/assets/a7d054f8-ad7b-44a9-a929-303ac8f96739)

### 🌐 Software
- Database (SQL or NoSQL) for storage
- Web App (HTML/CSS/JS, React, or Flask/Node/FastAPI)
- Custom data analytic algorithms to analyze trends
- Optional: Doctor consultation interface

---

## 🎯 Target Market

We aim to help two key groups:

1. 👵 **Elderly or At-Risk Individuals**  
   For remote, consistent vital monitoring — skipping unnecessary clinic trips.

2. 🏥 **Health Clinics with High Patient Volumes**  
   To streamline check-ins and reduce manual vital checks during visits.

---

## 📆 Biweekly Check-In Plan

### 🗓️ Week 2–3
- **Software**:  
  - Create wire frames for the webiste
  - Create landing page for website: user login and signup page, about us page
- **Hardware**:  
  - Draft circuit schematics and wiring plans (Raspberry Pi + sensors)

---

### 🗓️ Week 5–6
- **Software**:  
  - Implement user login authentication system with cookies sessions 
  - Build database schemas
  - Integrate graphing for vitals  
  - Begin WiFi/MQTT testing with ESP32
- **Hardware**:  
  - Test MAX30102 oximeter sensor 
  - Test HX711 sensor load module
  - Extract Blood Pressure Data with I2C bus
  - Once testing complete integrate sensors with ESP32
  - Design kit layout for electronics integration 

---

### 🗓️ Week 7–8
- **Software**:
  - Create schema diagrams, use DrawSQL
  - Enable ESP32 web hosting for device setup/registration 
  - Add data uploading capability 
  - Make webiste look nice with styling sheets 
- **Hardware**: 
  - Consolidate electronics and wiring using perfboard or PCB 
  - Validate blood pressure monitor 
  - Print out kit enclosure, make scale base plate 

---

### 🗓️ Week 9-10
- **Software**:  
  - Get exporting of data feature working
  - Data analysis algorithms for user data
  - Clean up pages to look like proposed wireframes
  - Consolidate all vital measurement code into one script
  - Final testing & deployment of website + ESP32 System
- **Hardware**:
  - Hack I2C bus on new blood pressure monitor, validate data, manipulate buttons
     - Old BPM works but new one could be better
  - Reprint enclosure for final showcase
     - Lid doesn't fit properly had to cut it   
  - Fix up weight base plate make it look nicer
  - Recrimp wire connections, sometimes loose connections cause issues with I2C communication
  - Final debugging of kit set up

---

## 🙌 Contributors

- Carlos Guerrero  
- Anton John Del Mar
- Nathaniel Hernandez

---

# Parts List
<a href = "https://docs.google.com/spreadsheets/d/1Vw-dRWdZHSxFF3NrVBZzRUBWk4LhnQSCr9qGEEaQ7Oo/edit?usp=sharing" target = "_blank">
https://docs.google.com/spreadsheets/d/1Vw-dRWdZHSxFF3NrVBZzRUBWk4LhnQSCr9qGEEaQ7Oo/edit?usp=sharing 
