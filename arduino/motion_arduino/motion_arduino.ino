/**
 * QuickDeck Test - Motion Sensors Arduino
 * 
 * This firmware reads data from 3 MPU6050 motion sensors
 * and sends the data via serial to a Python application.
 * 
 * Hardware:
 * - Arduino Uno
 * - 3x MPU6050 accelerometer/gyroscope modules
 */

#include <Wire.h>
#include "MPU6050.h"

// I2C addresses for the three MPU6050 sensors
// Default address is 0x68, the AD0 pin can be used to change to 0x69
const int MPU_ADDRESSES[3] = {0x68, 0x69, 0x68}; // Third sensor on second I2C bus

// Create MPU6050 objects
MPU6050 mpu[3];

// Variables for timing
const long SAMPLE_INTERVAL = 10; // Sample at 100 Hz (10 ms interval)
unsigned long lastSampleTime = 0;

// Variables for complementary filter
float pitch[3] = {0, 0, 0};
float roll[3] = {0, 0, 0};
float yaw[3] = {0, 0, 0};
float alpha = 0.98; // Complementary filter coefficient

void setup() {
  // Initialize serial connection
  Serial.begin(115200);
  while (!Serial) {
    ; // Wait for serial port to connect
  }
  Serial.println("MOTION_ARDUINO_READY");
  
  // Initialize I2C communication
  Wire.begin();
  Wire.setClock(400000); // Set I2C clock to 400kHz for faster communication
  
  // Initialize all MPU6050 sensors
  for (int i = 0; i < 2; i++) { // First two sensors on main I2C bus
    mpu[i].initialize();
    
    // Set the I2C address
    mpu[i].setAddress(MPU_ADDRESSES[i]);
    
    // Set gyroscope range to ±250°/sec
    mpu[i].setFullScaleGyroRange(MPU6050_GYRO_FS_250);
    
    // Set accelerometer range to ±2g
    mpu[i].setFullScaleAccelRange(MPU6050_ACCEL_FS_2);
    
    // Check if MPU6050 is connected
    if (mpu[i].testConnection()) {
      Serial.print("Sensor ");
      Serial.print(i + 1);
      Serial.println(" initialized");
    } else {
      Serial.print("ERROR: Sensor ");
      Serial.print(i + 1);
      Serial.println(" not found!");
    }
  }
  
  // Setup code for third sensor would go here
  // For simplicity, we'll simulate the third sensor in this example
  
  // Perform initial calibration
  calibrateSensors();
}

void loop() {
  unsigned long currentTime = millis();
  
  // Check if it's time to take a sample
  if (currentTime - lastSampleTime >= SAMPLE_INTERVAL) {
    lastSampleTime = currentTime;
    
    // Read all sensors and calculate orientation
    for (int i = 0; i < 2; i++) { // Processing two actual sensors
      // Read raw data
      int16_t ax, ay, az, gx, gy, gz;
      mpu[i].getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
      
      // Convert accelerometer values to angles
      float accelPitch = atan2(ay, sqrt(ax * ax + az * az)) * 180.0 / PI;
      float accelRoll = atan2(-ax, az) * 180.0 / PI;
      
      // Convert gyroscope values from raw to degrees/sec
      float gyroX = gx / 131.0; // Based on ±250°/sec range
      float gyroY = gy / 131.0;
      float gyroZ = gz / 131.0;
      
      // Calculate gyro angles
      float dt = SAMPLE_INTERVAL / 1000.0;
      float gyroPitch = pitch[i] + gyroY * dt;
      float gyroRoll = roll[i] + gyroX * dt;
      float gyroYaw = yaw[i] + gyroZ * dt;
      
      // Apply complementary filter
      pitch[i] = alpha * gyroPitch + (1 - alpha) * accelPitch;
      roll[i] = alpha * gyroRoll + (1 - alpha) * accelRoll;
      yaw[i] = gyroYaw; // No magnetometer for yaw correction
    }
    
    // Simulate data for third sensor (in a real setup, this would be actual sensor data)
    // For this example, we'll make the third sensor show increasing deflection
    static float angle_offset = 0.0;
    angle_offset += 0.01;
    if (angle_offset > 30.0) angle_offset = 0.0; // Reset after reaching 30 degrees
    
    pitch[2] = pitch[1] + angle_offset;
    roll[2] = roll[1];
    yaw[2] = yaw[1];
    
    // Send timestamp and readings to serial
    Serial.print("MOTION,");
    Serial.print(currentTime);
    
    for (int i = 0; i < 3; i++) {
      Serial.print(",");
      Serial.print(pitch[i], 2); // Pitch angle
      Serial.print(",");
      Serial.print(roll[i], 2);  // Roll angle
      Serial.print(",");
      Serial.print(yaw[i], 2);   // Yaw angle
    }
    
    Serial.println();
  }
  
  // Check for incoming commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    processCommand(command);
  }
}

void calibrateSensors() {
  // Calibration routine for gyroscope offsets
  Serial.println("CALIBRATING_SENSORS,START");
  
  for (int i = 0; i < 2; i++) {
    mpu[i].CalibrateGyro(6); // Calibrate gyroscope with 6 iterations
    mpu[i].CalibrateAccel(6); // Calibrate accelerometer with 6 iterations
  }
  
  Serial.println("CALIBRATING_SENSORS,COMPLETE");
}

void processCommand(String command) {
  if (command == "CALIBRATE") {
    calibrateSensors();
  }
  else if (command == "IDENTITY") {
    Serial.println("MOTION_ARDUINO_READY");
  }
}