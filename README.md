# ECE142B-SP25-MedHome

### What will the ideal product look like? <br>
The ideal product would look like a medical instrument measurement device that is integrated into a chair. This device would take an oximeter, blood pressure monitor, and scale, to track vitals such as blood pressure, heart rate, oxygen levels, and weight. This data will then be fed into a database along with the user's username and or personal ID so the user will be able to access their vitals and various statistics with graphs to show trends in the user's vitals over time. On the web app This data will then be fed into an AI API that can interpret the trends and find any malignant trends and notifies the user aboout them. The user then will have the option to consult a doctor if there is a serious health issue detected. 


### What will the MVP for a quarter look like? <br>
The minimum value product will be a basic device that uses instruments such as an oximeter, scale, and blood pressure monitor, that communicate to a central microcontroller like an ESP32 as this has WiFi. On the backened we will have a database that stores data like the user information and the health data measurements. On the web application the users can interact with their data to check in on their health.


### What will the required technology look like? <br>
The required technology should be fairly simple. For electronics we need three medical instruments and or sensors if we decide to make our own including an oximeter, scale, and blood pressure monitor. Then we would need a microcontroller preferrably an ESP32 as this has WiFi. We can then use different communication protocols (SPI, I2C, Can Bus, UART) to allow the ESP32 to gather data from the devices. On backened we will have a database to store the health data. Using WiFi we can use MQTT protocol to allow our data to be sent to the database using topics to specifiy what tables in the database we would need to add the data to. We would create a simple web application that allows users to see and interact with their data through graphs. We can use LLM API's to give feedback on the users health data. Users will also have an option to consult with a doctor if they prefer that.


### What market can you reach out to? <br>