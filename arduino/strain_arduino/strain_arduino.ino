/**
 * QuickDeck Test - Strain Measurement Arduino
 * 
 * This firmware reads data from 8 strain gauges via HX711 amplifiers
 * and sends the data via serial to a Python application.
 * 
 * Hardware:
 * - Arduino Uno
 * - 8x HX711 amplifier modules
 * - 8x KFH-3-120-D17-11L1M2S strain gauges
 */

#include "HX711.h"

// Define pins for each HX711 amplifier
// Format: {DATA_PIN, CLOCK_PIN}
const int HX711_PINS[8][2] = {
  {2, 3},   // Channel 1
  {4, 5},   // Channel 2
  {6, 7},   // Channel 3
  {8, 9},   // Channel 4
  {10, 11}, // Channel 5
  {12, 13}, // Channel 6
  {A0, A1}, // Channel 7
  {A2, A3}  // Channel 8
};

// Create HX711 objects
HX711 scale[8];

// Variables for timing
const long SAMPLE_INTERVAL = 100; // Sample at 10 Hz (100 ms interval)
unsigned long lastSampleTime = 0;

// Buffer for storing readings
float readings[8];

void setup() {
  // Initialize serial connection
  Serial.begin(115200);
  while (!Serial) {
    ; // Wait for serial port to connect
  }
  Serial.println("STRAIN_ARDUINO_READY");
  
  // Initialize all HX711 amplifiers
  for (int i = 0; i < 8; i++) {
    scale[i].begin(HX711_PINS[i][0], HX711_PINS[i][1]);
    scale[i].set_gain(64);  // Use channel A with gain of 64
    
    // Check if HX711 is ready
    if (scale[i].is_ready()) {
      scale[i].tare();  // Reset scale to zero
      Serial.print("Channel ");
      Serial.print(i + 1);
      Serial.println(" initialized");
    } else {
      Serial.print("ERROR: Channel ");
      Serial.print(i + 1);
      Serial.println(" not found!");
    }
  }
}

void loop() {
  unsigned long currentTime = millis();
  
  // Check if it's time to take a sample
  if (currentTime - lastSampleTime >= SAMPLE_INTERVAL) {
    lastSampleTime = currentTime;
    
    // Read all channels
    for (int i = 0; i < 8; i++) {
      if (scale[i].is_ready()) {
        readings[i] = scale[i].get_value();
      } else {
        readings[i] = 0; // Indicate error with zero value
      }
    }
    
    // Send timestamp and readings to serial
    Serial.print("STRAIN,");
    Serial.print(currentTime);
    
    for (int i = 0; i < 8; i++) {
      Serial.print(",");
      Serial.print(readings[i], 6); // 6 decimal places precision
    }
    
    Serial.println();
  }
  
  // Check for incoming commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    processCommand(command);
  }
}

void processCommand(String command) {
  if (command.startsWith("TARE")) {
    // Tare all scales
    for (int i = 0; i < 8; i++) {
      scale[i].tare();
    }
    Serial.println("TARE_COMPLETE");
  } 
  else if (command.startsWith("CALIBRATE")) {
    // Format: CALIBRATE,channel,factor
    int commaIndex = command.indexOf(',', 10);
    if (commaIndex > 0) {
      int channel = command.substring(10, commaIndex).toInt();
      float factor = command.substring(commaIndex + 1).toFloat();
      
      if (channel >= 1 && channel <= 8) {
        scale[channel - 1].set_scale(factor);
        Serial.print("CALIBRATION_SET,");
        Serial.print(channel);
        Serial.print(",");
        Serial.println(factor, 6);
      }
    }
  }
  else if (command == "IDENTITY") {
    Serial.println("STRAIN_ARDUINO_READY");
  }
}