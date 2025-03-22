# QuickDeck Data System

A data collection and visualization system for testing the BrandSafway QuickDeck platform under cantilevered loading conditions.

## Overview

This system collects and visualizes strain gauge and motion sensor data to analyze the structural response of QuickDeck components during testing. The system includes both hardware support for real testing and a simulation mode for software testing and demonstration.

## Features

- Real-time data visualization of strain measurements and angular deflections
- Support for 8 strain gauge channels and 3 motion sensors
- Built-in simulation mode for testing without hardware
- Automatic data storage and test management
- Excel export for further analysis

## Simulation Mode

The system includes a robust simulation mode that generates realistic test data without requiring any physical hardware:

- **Simulated Load Control**: Increase or decrease the virtual load to see real-time changes in strain and deflection
- **Realistic Data**: The simulation generates strain patterns with appropriate relationships between sensors
- **Live Visualization**: Watch real-time plots respond to load changes exactly as they would in real testing
- **Complete Workflow**: Test the entire data acquisition, visualization, and analysis pipeline

## Installation

### Python Version Compatibility

This software works best with Python 3.7-3.11. Python 3.13 may require additional patches.

### Basic Setup

1. Clone this repository
2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the application:
   ```
   python run.py
   ```

## Using the System

### Simulation Mode

1. Launch the application with `python run.py`
2. Ensure "Simulation Mode" is checked (enabled by default)
3. Enter a test name or use the auto-generated one
4. Click "Start Test" to begin data collection
5. Use the "Increase Load" and "Decrease Load" buttons to control the simulated load
   - Watch how the strain values increase with higher loads
   - Notice how the deflection angles change proportionally to the load
6. Click "Stop Test" when finished
7. Review the test results or export to Excel

### Hardware Mode

When you're ready to use real hardware:

1. Follow the hardware setup in the INSTALL.md file
2. Upload the Arduino firmware to the respective microcontrollers
3. Launch the application and uncheck "Simulation Mode"
4. Select the correct serial ports and connect to both Arduinos
5. Calibrate sensors before starting the test
6. Start data acquisition and monitoring

## Understanding the Data

The system collects and visualizes two main types of data:

1. **Strain Measurements**: Values from 8 strain gauges showing material stress at key locations
   - Higher values indicate more stress in the material
   - Watch for consistent increases with applied load
   - Compare values between channels to understand stress distribution

2. **Angular Deflection**: Pitch, roll, and yaw values from motion sensors
   - Pitch values show the primary deflection angle (visualized in real-time)
   - Angles increase with distance from the fixed support
   - Maximum deflection occurs at the cantilevered end

## Data Management

All test data is automatically saved in the `data/` directory with a unique timestamp. You can:
- View previous test results
- Export data to Excel for further analysis
- Compare multiple tests to evaluate different configurations

## Troubleshooting

- **Python Version Issues**: Use Python 3.10 for best compatibility
- **Serial Port Problems**: Ensure Arduino drivers are installed correctly
- **Display Issues**: Make sure matplotlib and tkinter are properly installed

For more detailed information, refer to the INSTALL.md file.