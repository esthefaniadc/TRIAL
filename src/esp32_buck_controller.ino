#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <driver/ledc.h>

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Cloud API configuration
const char* apiEndpoint = "http://your-cloud-api.com/api/telemetry";

// Pin definitions
const int PWM_PIN = 25;           // PWM output for buck converter
const int FEEDBACK_PIN = 34;     // ADC input for voltage feedback
const int LED_PIN = 2;           // Status LED

// PWM configuration
const int PWM_FREQ = 1000;       // 1kHz switching frequency
const int PWM_CHANNEL = 0;
const int PWM_RESOLUTION = 12;   // 12-bit resolution (0-4095)
const int PWM_MAX = 4095;

// Control system parameters
const float TARGET_VOLTAGE = 2.0;  // Target output voltage (V)
const float VCC = 3.3;             // ADC reference voltage
const float ADC_MAX = 4095.0;      // 12-bit ADC max value

// Voltage divider for feedback (if needed)
const float VOLTAGE_DIVIDER_RATIO = 1.0; // Adjust based on your circuit

// PID controller parameters
float kp = 100.0;    // Proportional gain
float ki = 50.0;     // Integral gain  
float kd = 10.0;     // Derivative gain

// PID variables
float previous_error = 0;
float integral = 0;
float derivative = 0;
float output = 0;

// Data collection
struct TelemetryData {
  unsigned long timestamp;
  float target_voltage;
  float actual_voltage;
  float error;
  float duty_cycle;
  float pwm_output;
};

// Timing variables
unsigned long lastControlUpdate = 0;
unsigned long lastDataSend = 0;
const unsigned long CONTROL_INTERVAL = 10;    // 10ms control loop (100Hz)
const unsigned long DATA_SEND_INTERVAL = 1000; // Send data every 1 second

void setup() {
  Serial.begin(115200);
  Serial.println("ESP32 Buck Converter Controller Starting...");
  
  // Initialize pins
  pinMode(LED_PIN, OUTPUT);
  pinMode(FEEDBACK_PIN, INPUT);
  
  // Configure PWM
  ledcSetup(PWM_CHANNEL, PWM_FREQ, PWM_RESOLUTION);
  ledcAttachPin(PWM_PIN, PWM_CHANNEL);
  
  // Initialize with 50% duty cycle
  ledcWrite(PWM_CHANNEL, PWM_MAX / 2);
  
  // Connect to WiFi
  connectToWiFi();
  
  // Initialize ADC
  analogReadResolution(12);
  analogSetAttenuation(ADC_11db); // For 3.3V range
  
  Serial.println("System initialized. Starting control loop...");
}

void loop() {
  unsigned long currentTime = millis();
  
  // Control loop - runs at 100Hz
  if (currentTime - lastControlUpdate >= CONTROL_INTERVAL) {
    runControlLoop();
    lastControlUpdate = currentTime;
  }
  
  // Data transmission - runs every second
  if (currentTime - lastDataSend >= DATA_SEND_INTERVAL) {
    sendTelemetryData();
    lastDataSend = currentTime;
  }
  
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    connectToWiFi();
  }
  
  delay(1); // Small delay to prevent watchdog issues
}

void connectToWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.println("WiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    digitalWrite(LED_PIN, HIGH);
  } else {
    Serial.println();
    Serial.println("WiFi connection failed!");
    digitalWrite(LED_PIN, LOW);
  }
}

void runControlLoop() {
  // Read feedback voltage
  int adcValue = analogRead(FEEDBACK_PIN);
  float actualVoltage = (adcValue / ADC_MAX) * VCC * VOLTAGE_DIVIDER_RATIO;
  
  // Calculate error
  float error = TARGET_VOLTAGE - actualVoltage;
  
  // PID calculation
  integral += error * (CONTROL_INTERVAL / 1000.0);
  derivative = (error - previous_error) / (CONTROL_INTERVAL / 1000.0);
  
  output = (kp * error) + (ki * integral) + (kd * derivative);
  
  // Convert PID output to duty cycle (0-100%)
  float dutyCycle = constrain(output + 60.6, 0, 100); // 60.6% is theoretical duty cycle
  
  // Convert duty cycle to PWM value
  int pwmValue = (dutyCycle / 100.0) * PWM_MAX;
  pwmValue = constrain(pwmValue, 0, PWM_MAX);
  
  // Apply PWM
  ledcWrite(PWM_CHANNEL, pwmValue);
  
  // Store for next iteration
  previous_error = error;
  
  // Debug output
  if (millis() % 100 == 0) { // Print every 100ms
    Serial.printf("Target: %.3fV, Actual: %.3fV, Error: %.3fV, Duty: %.1f%%, PWM: %d\n",
                  TARGET_VOLTAGE, actualVoltage, error, dutyCycle, pwmValue);
  }
}

void sendTelemetryData() {
  if (WiFi.status() != WL_CONNECTED) {
    return;
  }
  
  // Read current values
  int adcValue = analogRead(FEEDBACK_PIN);
  float actualVoltage = (adcValue / ADC_MAX) * VCC * VOLTAGE_DIVIDER_RATIO;
  float error = TARGET_VOLTAGE - actualVoltage;
  float dutyCycle = (output + 60.6);
  dutyCycle = constrain(dutyCycle, 0, 100);
  
  // Create telemetry data
  TelemetryData data;
  data.timestamp = millis();
  data.target_voltage = TARGET_VOLTAGE;
  data.actual_voltage = actualVoltage;
  data.error = error;
  data.duty_cycle = dutyCycle;
  data.pwm_output = (dutyCycle / 100.0) * PWM_MAX;
  
  // Create JSON payload
  DynamicJsonDocument doc(512);
  doc["timestamp"] = data.timestamp;
  doc["target_voltage"] = data.target_voltage;
  doc["actual_voltage"] = data.actual_voltage;
  doc["error"] = data.error;
  doc["duty_cycle"] = data.duty_cycle;
  doc["pwm_output"] = data.pwm_output;
  doc["device_id"] = WiFi.macAddress();
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  // Send HTTP POST request
  HTTPClient http;
  http.begin(apiEndpoint);
  http.addHeader("Content-Type", "application/json");
  
  int httpResponseCode = http.POST(jsonString);
  
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.printf("Data sent successfully. Response code: %d\n", httpResponseCode);
  } else {
    Serial.printf("Error sending data. HTTP code: %d\n", httpResponseCode);
  }
  
  http.end();
}

// Function to update PID parameters via serial commands
void updatePIDParameters() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command.startsWith("KP=")) {
      kp = command.substring(3).toFloat();
      Serial.printf("Kp updated to: %.2f\n", kp);
    } else if (command.startsWith("KI=")) {
      ki = command.substring(3).toFloat();
      Serial.printf("Ki updated to: %.2f\n", ki);
    } else if (command.startsWith("KD=")) {
      kd = command.substring(3).toFloat();
      Serial.printf("Kd updated to: %.2f\n", kd);
    } else if (command == "STATUS") {
      Serial.printf("Current PID: Kp=%.2f, Ki=%.2f, Kd=%.2f\n", kp, ki, kd);
      Serial.printf("WiFi Status: %s\n", WiFi.status() == WL_CONNECTED ? "Connected" : "Disconnected");
    }
  }
}