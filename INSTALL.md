# QuickDeck Data System - Installation Guide

This guide provides step-by-step instructions for setting up the QuickDeck testing system.

## Python Version Compatibility

- **Recommended**: Python 3.7 to 3.11
- **Python 3.12-3.13**: Works with the included patch file (see [Using with Newer Python Versions](#using-with-newer-python-versions))
- **Minimum**: Python 3.7

## Installation Options

### Option 1: Simple Installation (Simulation Mode Only)

If you just want to test the system using simulation mode without physical hardware:

1. Clone this repository:
   ```
   git clone https://github.com/gabejohnsnn/quickdeck-data-system.git
   cd quickdeck-data-system
   ```

2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install required Python packages:
   ```
   pip install -r requirements.txt
   ```

5. Run the application:
   ```
   python run.py
   ```

### Option 2: Full Installation (With Hardware Support)

Follow these steps if you plan to connect to physical Arduino hardware:

## Prerequisites

- Arduino IDE (version 1.8.x or later)
- Python 3.7 or higher
- 2x Arduino Uno microcontrollers
- 8x HX711 load cell amplifiers
- 8x KFH-3-120-D17-11L1M2S strain gauges
- 3x MPU6050 accelerometer/gyroscope modules
- USB cables for Arduino connections

## Software Installation

### 1. Arduino Libraries

Install the following libraries through the Arduino Library Manager:

1. Open Arduino IDE
2. Go to Sketch > Include Library > Manage Libraries
3. Search for and install:
   - "HX711" by Bogdan Necula
   - "MPU6050" by Electronic Cats

### 2. Python Environment

1. Clone this repository:
   ```
   git clone https://github.com/gabejohnsnn/quickdeck-data-system.git
   cd quickdeck-data-system
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install required Python packages:
   ```
   pip install -r requirements.txt
   ```

## Hardware Setup

### Strain Gauge Arduino

1. Connect each HX711 amplifier to the Arduino Uno using the following pin mappings:
   - HX711 #1: DATA = Pin 2, CLOCK = Pin 3
   - HX711 #2: DATA = Pin 4, CLOCK = Pin 5
   - HX711 #3: DATA = Pin 6, CLOCK = Pin 7
   - HX711 #4: DATA = Pin 8, CLOCK = Pin 9
   - HX711 #5: DATA = Pin 10, CLOCK = Pin 11
   - HX711 #6: DATA = Pin 12, CLOCK = Pin 13
   - HX711 #7: DATA = Pin A0, CLOCK = Pin A1
   - HX711 #8: DATA = Pin A2, CLOCK = Pin A3

2. Power the HX711 modules with 5V and GND from the Arduino.

3. Connect the strain gauges to the HX711 modules according to the strain gauge placement diagram in the instrumentation plan.

### Motion Sensor Arduino

1. Connect two MPU6050 sensors to the Arduino Uno via I2C:
   - Both sensors: SCL = Arduino SCL (A5), SDA = Arduino SDA (A4)
   - First sensor: AD0 pin connected to GND (I2C address 0x68)
   - Second sensor: AD0 pin connected to 5V (I2C address 0x69)

2. Power the MPU6050 modules with 3.3V or 5V (depending on the module) and GND from the Arduino.

3. For the third sensor (if using), you'll need to implement a software I2C solution or use an I2C multiplexer.

## Uploading Firmware

1. Connect the strain measurement Arduino to your computer via USB.

2. Open the Arduino IDE and load the `arduino/strain_arduino/strain_arduino.ino` sketch.

3. Select the correct board (Arduino Uno) and port from the Tools menu.

4. Click the Upload button to program the Arduino.

5. Repeat steps 1-4 for the motion sensor Arduino using the `arduino/motion_arduino/motion_arduino.ino` sketch.

## Running the Application

1. Make sure both Arduinos are connected to your computer via USB.

2. Activate your Python virtual environment if you created one.

3. Run the application:
   ```
   python run.py
   ```

4. Use the GUI to connect to both Arduinos, calibrate the sensors, and start data acquisition.

## Using with Newer Python Versions

If you're using Python 3.12 or newer (such as Python 3.13) and encounter compatibility errors:

1. Run the application using our patch file instead:
   ```
   python patch.py
   ```

2. The patch file adds compatibility fixes for newer Python versions that may have removed features used by some dependencies.

3. If you still encounter issues, try using Python 3.10, which is known to work well with all dependencies:
   ```
   # Create a Python 3.10 virtual environment
   python3.10 -m venv venv_py310
   source venv_py310/bin/activate  # On Windows: venv_py310\Scripts\activate
   pip install -r requirements.txt
   python run.py
   ```

## Troubleshooting

- **Serial Port Not Found**: Ensure both Arduinos are properly connected and that the correct drivers are installed.

- **No Data Received**: Check the serial port settings (baud rate should be 115200) and verify that the correct firmware is uploaded to each Arduino.

- **Strain Gauge Not Working**: Verify connections between the strain gauge, HX711 module, and Arduino. Check that the strain gauge is properly attached to the test specimen.

- **Motion Sensor Not Working**: Check I2C connections and addresses. Ensure that the MPU6050 sensors are properly powered.

- **Python Compatibility Issues**: Use the patch file or switch to Python 3.10 for maximum compatibility.

For more detailed information, refer to the technical documentation in the instrumentation plan.