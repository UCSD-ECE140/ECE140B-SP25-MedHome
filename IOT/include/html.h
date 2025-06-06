static const char MAIN_page[] = R"==(
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MedHome Device and Wifi Registration</title>
</head>
<body>
  <h1>MedHome Device and Wifi Registration</h1>
  <p>To register your MedHome device, please follow the instructions below:</p>

  <h2>Step 1: Connect to the MedHome Device</h2>
  <p>Ensure that your device is powered on and connected to the same network as your computer.</p>

  <h2>Step 2: Access the Registration Page</h2>
  <p>Open a web browser and enter the following URL: <a href="https://ece140b-sp25-medhome.onrender.com/register">https://ece140b-sp25-medhome.onrender.com/register</a></p>
  <p>You should see a registration form similar to the one below:</p>
  <pre>
    <code>
      <form action="/register" method="POST">
        <label for="device_id">Device ID:</label>
        <input type="text" id="device_id" name="device_id" required>
        
        <label for="wifi_ssid">WiFi SSID:</label>
        <input type="text" id="wifi_ssid" name="wifi_ssid" required>
        
        <label for="wifi_password">WiFi Password:</label>
        <input type="password" id="wifi_password" name="wifi_password" required>
        
        <button type="submit">Register</button>
      </form>
    </code>
  </pre>
  <h2>Step 3: Fill in the Registration Form</h2>
  <p>Enter the following information in the form:</p>
  <ul>
    <li><strong>Device ID:</strong> The unique identifier for your MedHome device.</li>
    <li><strong>WiFi SSID:</strong> The name of the WiFi network you want to connect to.</li>
    <li><strong>WiFi Password:</strong> The password for the WiFi network.</li>
  </ul>
  <h2>Step 4: Submit the Form</h2>
  <p>After filling in the form, click the "Register" button to submit your information.</p>
  <h2>Step 5: Confirmation</h2>
  <p>You should see a confirmation message indicating that your device has been successfully registered.</p>
  <h2>Troubleshooting</h2>
  <p>If you encounter any issues during the registration process, please check the following:</p>
  <ul>
    <li>Ensure that your device is powered on and connected to the same network as your computer.</li>
    <li>Double-check the WiFi SSID and password for any typos.</li>
    <li>If you continue to experience issues, please contact MedHome support for assistance.</li>
  </ul>
  <h2>Contact Support</h2>
  <p>If you need further assistance, please reach out to our support team:</p>
  <ul>
    <li>Email: nathanieleh@gmail.com</li>
  </ul>
  <p>Thank you for choosing MedHome!</p>
</body>
</html>
)==";