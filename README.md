# QuickDeck Data System

A simple data collection and visualization system for testing the BrandSafway QuickDeck platform under cantilevered loading conditions.

## Overview

This system collects data from strain gauges and motion sensors to analyze the structural response of QuickDeck components during testing. The system consists of two Arduino programs for data acquisition and a Python application for visualization and storage.

## System Components

### Hardware
- 2x Arduino Uno microcontrollers
- 8x Strain gauges with HX711 amplifiers
- 3x MPU6050 motion sensors
- Computer for running visualization software

### Software
1. **Arduino Firmware**
   - `strain_arduino`: Collects data from strain gauges via HX711 amplifiers
   - `motion_arduino`: Collects data from MPU6050 motion sensors

2. **Python Application**
   - Data acquisition from serial connections
   - Real-time visualization
   - Data storage in CSV format

## Project Structure

```
├── arduino/
│   ├── strain_arduino/
│   │   └── strain_arduino.ino
│   └── motion_arduino/
│       └── motion_arduino.ino
└── python/
    ├── main.py
    ├── data_acquisition.py
    ├── visualization.py
    └── data_storage.py
```

## Setup Instructions

1. Clone this repository
2. Upload the Arduino sketches to their respective microcontrollers
3. Install required Python dependencies: `pip install -r requirements.txt`
4. Run the Python application: `python python/main.py`

## Usage

The application provides a simple interface for:
- Connecting to Arduino devices
- Starting/stopping data collection
- Visualizing real-time strain and deflection data
- Saving test data to CSV files

## Data Format

Data is stored in CSV format with the following structure:

**Strain data:**
```
timestamp,strain1,strain2,strain3,strain4,strain5,strain6,strain7,strain8
```

**Motion data:**
```
timestamp,sensor1_pitch,sensor1_roll,sensor1_yaw,sensor2_pitch,sensor2_roll,sensor2_yaw,sensor3_pitch,sensor3_roll,sensor3_yaw
```