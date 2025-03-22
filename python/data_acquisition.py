#!/usr/bin/env python3
"""
QuickDeck Test - Data Acquisition Module

This module handles serial communication with the Arduino microcontrollers
and raw data acquisition from strain gauges and motion sensors.
"""

import serial
import serial.tools.list_ports
import threading
import time
import csv
import os
from datetime import datetime

class DataAcquisition:
    """Handles serial communication and data acquisition"""
    
    def __init__(self, strain_data_callback=None, motion_data_callback=None):
        """Initialize the data acquisition module"""
        # Serial connection objects
        self.strain_serial = None
        self.motion_serial = None
        
        # Connection status
        self.strain_connected = False
        self.motion_connected = False
        
        # Serial port settings
        self.baud_rate = 115200
        self.timeout = 1.0
        
        # Data buffers
        self.strain_buffer = []
        self.motion_buffer = []
        
        # Callback functions
        self.strain_data_callback = strain_data_callback
        self.motion_data_callback = motion_data_callback
        
        # Thread for reading data
        self.strain_thread = None
        self.motion_thread = None
        
        # Thread control flags
        self.running = False
        
        # Current test name
        self.test_name = None
        
        # Data storage
        self.strain_file = None
        self.motion_file = None
        self.strain_writer = None
        self.motion_writer = None
    
    def get_available_ports(self):
        """Get list of available serial ports"""
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append({
                'device': port.device,
                'description': port.description
            })
        return ports
    
    def connect_strain_arduino(self, port):
        """Connect to the strain measurement Arduino"""
        try:
            self.strain_serial = serial.Serial(
                port=port,
                baudrate=self.baud_rate,
                timeout=self.timeout
            )
            
            # Wait for Arduino to initialize
            time.sleep(2)
            
            # Check if the correct Arduino is connected
            self.strain_serial.write(b"IDENTITY\n")
            response = self.strain_serial.readline().decode().strip()
            
            if "STRAIN_ARDUINO_READY" in response:
                self.strain_connected = True
                print(f"Connected to strain Arduino on {port}")
                return True
            else:
                self.strain_serial.close()
                self.strain_serial = None
                print(f"Wrong device connected to {port}")
                return False
                
        except serial.SerialException as e:
            print(f"Error connecting to strain Arduino: {str(e)}")
            return False
    
    def connect_motion_arduino(self, port):
        """Connect to the motion sensor Arduino"""
        try:
            self.motion_serial = serial.Serial(
                port=port,
                baudrate=self.baud_rate,
                timeout=self.timeout
            )
            
            # Wait for Arduino to initialize
            time.sleep(2)
            
            # Check if the correct Arduino is connected
            self.motion_serial.write(b"IDENTITY\n")
            response = self.motion_serial.readline().decode().strip()
            
            if "MOTION_ARDUINO_READY" in response:
                self.motion_connected = True
                print(f"Connected to motion Arduino on {port}")
                return True
            else:
                self.motion_serial.close()
                self.motion_serial = None
                print(f"Wrong device connected to {port}")
                return False
                
        except serial.SerialException as e:
            print(f"Error connecting to motion Arduino: {str(e)}")
            return False
    
    def start_acquisition(self, test_name=None):
        """Start data acquisition"""
        if not (self.strain_connected and self.motion_connected):
            print("Both Arduinos must be connected before acquisition")
            return False
        
        # Set test name and create storage files
        if test_name:
            self.test_name = test_name
        else:
            self.test_name = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        os.makedirs(f"data/{self.test_name}", exist_ok=True)
        
        # Create CSV files for strain and motion data
        self.strain_file = open(f"data/{self.test_name}/strain_data.csv", 'w', newline='')
        self.motion_file = open(f"data/{self.test_name}/motion_data.csv", 'w', newline='')
        
        # Create CSV writers
        self.strain_writer = csv.writer(self.strain_file)
        self.motion_writer = csv.writer(self.motion_file)
        
        # Write headers
        self.strain_writer.writerow(['timestamp', 'strain1', 'strain2', 'strain3', 'strain4', 'strain5', 'strain6', 'strain7', 'strain8'])
        self.motion_writer.writerow(['timestamp', 'sensor1_pitch', 'sensor1_roll', 'sensor1_yaw', 'sensor2_pitch', 'sensor2_roll', 'sensor2_yaw', 'sensor3_pitch', 'sensor3_roll', 'sensor3_yaw'])
        
        # Set control flag
        self.running = True
        
        # Start threads
        self.strain_thread = threading.Thread(target=self._strain_reader_thread)
        self.motion_thread = threading.Thread(target=self._motion_reader_thread)
        
        self.strain_thread.daemon = True
        self.motion_thread.daemon = True
        
        self.strain_thread.start()
        self.motion_thread.start()
        
        print(f"Data acquisition started for test: {self.test_name}")
        return True
    
    def stop_acquisition(self):
        """Stop data acquisition"""
        self.running = False
        
        # Wait for threads to terminate
        if self.strain_thread and self.strain_thread.is_alive():
            self.strain_thread.join(2.0)
        
        if self.motion_thread and self.motion_thread.is_alive():
            self.motion_thread.join(2.0)
        
        # Close data files
        if self.strain_file:
            self.strain_file.close()
            self.strain_file = None
        
        if self.motion_file:
            self.motion_file.close()
            self.motion_file = None
        
        print("Data acquisition stopped")
        return True
    
    def _strain_reader_thread(self):
        """Thread function for reading strain data"""
        while self.running and self.strain_connected:
            try:
                if self.strain_serial.in_waiting > 0:
                    line = self.strain_serial.readline().decode().strip()
                    
                    # Process the data
                    if line.startswith("STRAIN,"):
                        parts = line.split(",")
                        if len(parts) == 10:  # Header + timestamp + 8 strain values
                            timestamp = int(parts[1])
                            strain_values = [float(x) for x in parts[2:]]
                            
                            # Create data packet
                            data = {
                                'timestamp': timestamp,
                                'values': strain_values
                            }
                            
                            # Save to CSV
                            if self.strain_writer:
                                self.strain_writer.writerow([timestamp] + strain_values)
                                self.strain_file.flush()  # Ensure data is written immediately
                            
                            # Call callback if defined
                            if self.strain_data_callback:
                                self.strain_data_callback(data)
            
            except Exception as e:
                print(f"Error reading strain data: {str(e)}")
                self.strain_connected = False
                break
            
            # Small delay to prevent CPU hogging
            time.sleep(0.001)
    
    def _motion_reader_thread(self):
        """Thread function for reading motion data"""
        while self.running and self.motion_connected:
            try:
                if self.motion_serial.in_waiting > 0:
                    line = self.motion_serial.readline().decode().strip()
                    
                    # Process the data
                    if line.startswith("MOTION,"):
                        parts = line.split(",")
                        if len(parts) == 11:  # Header + timestamp + 9 values (3 angles for 3 sensors)
                            timestamp = int(parts[1])
                            
                            # Extract all 9 values (pitch, roll, yaw for 3 sensors)
                            motion_values = [float(x) for x in parts[2:]]
                            
                            # Create data packet
                            data = {
                                'timestamp': timestamp,
                                'values': motion_values
                            }
                            
                            # Save to CSV
                            if self.motion_writer:
                                self.motion_writer.writerow([timestamp] + motion_values)
                                self.motion_file.flush()  # Ensure data is written immediately
                            
                            # Call callback if defined
                            if self.motion_data_callback:
                                self.motion_data_callback(data)
            
            except Exception as e:
                print(f"Error reading motion data: {str(e)}")
                self.motion_connected = False
                break
            
            # Small delay to prevent CPU hogging
            time.sleep(0.001)
    
    def send_command_to_strain(self, command):
        """Send command to strain Arduino"""
        if not self.strain_connected:
            print("Strain Arduino not connected")
            return False
        
        try:
            self.strain_serial.write((command + "\n").encode())
            return True
        except Exception as e:
            print(f"Error sending command to strain Arduino: {str(e)}")
            return False
    
    def send_command_to_motion(self, command):
        """Send command to motion Arduino"""
        if not self.motion_connected:
            print("Motion Arduino not connected")
            return False
        
        try:
            self.motion_serial.write((command + "\n").encode())
            return True
        except Exception as e:
            print(f"Error sending command to motion Arduino: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from both Arduinos"""
        # Stop acquisition first
        if self.running:
            self.stop_acquisition()
        
        # Close serial connections
        if self.strain_serial:
            self.strain_serial.close()
            self.strain_serial = None
            self.strain_connected = False
        
        if self.motion_serial:
            self.motion_serial.close()
            self.motion_serial = None
            self.motion_connected = False
        
        print("Disconnected from Arduinos")
        return True

# Simple test code
if __name__ == "__main__":
    # Define simple callback functions
    def strain_callback(data):
        print(f"Strain data: timestamp={data['timestamp']}, values={data['values']}")
    
    def motion_callback(data):
        print(f"Motion data: timestamp={data['timestamp']}, values={data['values']}")
    
    # Create data acquisition object
    data_acq = DataAcquisition(strain_callback, motion_callback)
    
    # Print available ports
    ports = data_acq.get_available_ports()
    print("Available ports:")
    for i, port in enumerate(ports):
        print(f"{i}: {port['device']} - {port['description']}")
    
    # Ask user to select ports
    strain_port_idx = int(input("Select strain Arduino port: "))
    motion_port_idx = int(input("Select motion Arduino port: "))
    
    # Connect to Arduinos
    data_acq.connect_strain_arduino(ports[strain_port_idx]['device'])
    data_acq.connect_motion_arduino(ports[motion_port_idx]['device'])
    
    # Start acquisition
    data_acq.start_acquisition()
    
    # Run for 10 seconds
    print("Collecting data for 10 seconds...")
    try:
        time.sleep(10)
    except KeyboardInterrupt:
        print("Interrupted by user")
    
    # Stop acquisition and disconnect
    data_acq.stop_acquisition()
    data_acq.disconnect()
    
    print("Test complete")