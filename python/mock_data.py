#!/usr/bin/env python3
"""
Mock data generator for testing the QuickDeck data system without hardware
"""

import time
import threading
import math
import random

class MockDataGenerator:
    """Generates simulated strain and motion data"""
    
    def __init__(self, strain_callback=None, motion_callback=None):
        """Initialize the mock data generator"""
        # Callback functions
        self.strain_callback = strain_callback
        self.motion_callback = motion_callback
        
        # Thread for generating data
        self.thread = None
        
        # Thread control flag
        self.running = False
        
        # Time trackers
        self.start_time = 0
        self.strain_last_time = 0
        self.motion_last_time = 0
        
        # Sample rates
        self.strain_interval = 0.1  # 10 Hz
        self.motion_interval = 0.01  # 100 Hz
        
        # Simulated load parameters
        self.current_load = 0
        self.target_load = 0
        self.load_step = 50  # N per step
        self.max_load = 2000  # N
    
    def start(self):
        """Start generating mock data"""
        self.running = True
        self.start_time = time.time() * 1000  # ms
        self.strain_last_time = self.start_time
        self.motion_last_time = self.start_time
        
        # Start data generation thread
        self.thread = threading.Thread(target=self._generate_data)
        self.thread.daemon = True
        self.thread.start()
        
        return True
    
    def stop(self):
        """Stop generating mock data"""
        self.running = False
        
        # Wait for thread to terminate
        if self.thread and self.thread.is_alive():
            self.thread.join(2.0)
        
        return True
    
    def increase_load(self):
        """Increase the simulated load"""
        self.target_load = min(self.target_load + self.load_step, self.max_load)
        print(f"Increasing load to {self.target_load} N")
    
    def decrease_load(self):
        """Decrease the simulated load"""
        self.target_load = max(self.target_load - self.load_step, 0)
        print(f"Decreasing load to {self.target_load} N")
    
    def _generate_data(self):
        """Thread function for generating mock data"""
        while self.running:
            current_time = time.time() * 1000  # ms
            
            # Gradually adjust current load towards target
            if self.current_load < self.target_load:
                self.current_load = min(self.current_load + 1, self.target_load)
            elif self.current_load > self.target_load:
                self.current_load = max(self.current_load - 1, self.target_load)
            
            # Generate strain data at 10 Hz
            if current_time - self.strain_last_time >= self.strain_interval * 1000:
                self.strain_last_time = current_time
                
                # Create simulated strain data based on current load
                # Each channel has slightly different response
                strain_values = [
                    self.current_load * 0.05 * (1 + 0.1 * math.sin(current_time * 0.001)),  # Channel 1
                    self.current_load * 0.045 * (1 + 0.08 * math.sin(current_time * 0.002)),  # Channel 2
                    self.current_load * 0.055 * (1 + 0.12 * math.sin(current_time * 0.0015)),  # Channel 3
                    self.current_load * 0.06 * (1 + 0.07 * math.sin(current_time * 0.0025)),  # Channel 4
                    self.current_load * 0.04 * (1 + 0.09 * math.sin(current_time * 0.0012)),  # Channel 5
                    self.current_load * 0.05 * (1 + 0.11 * math.sin(current_time * 0.0018)),  # Channel 6
                    self.current_load * 0.065 * (1 + 0.06 * math.sin(current_time * 0.0022)),  # Channel 7
                    self.current_load * 0.047 * (1 + 0.13 * math.sin(current_time * 0.0014))   # Channel 8
                ]
                
                # Add some random noise
                strain_values = [value * (1 + random.uniform(-0.01, 0.01)) for value in strain_values]
                
                # Create data packet
                data = {
                    'timestamp': int(current_time),
                    'values': strain_values
                }
                
                # Call callback if defined
                if self.strain_callback:
                    self.strain_callback(data)
            
            # Generate motion data at 100 Hz
            if current_time - self.motion_last_time >= self.motion_interval * 1000:
                self.motion_last_time = current_time
                
                # Calculate deflection angle based on load (simplified beam model)
                # Angle increases with distance from fixed end
                base_angle = self.current_load * 0.01  # degrees per 1 N load
                
                # Angles for each sensor location
                angles = [
                    base_angle * 0.2,  # Near fixed end
                    base_angle * 0.6,  # Middle
                    base_angle  # End
                ]
                
                # Add some oscillation and noise
                motion_values = []
                for i, angle in enumerate(angles):
                    # Main pitch angle (direction of loading)
                    pitch = angle * (1 + 0.05 * math.sin(current_time * 0.002))
                    
                    # Small roll and yaw components (lateral motion)
                    roll = angle * 0.1 * math.sin(current_time * 0.0015)
                    yaw = angle * 0.05 * math.sin(current_time * 0.001)
                    
                    # Add noise
                    pitch += random.uniform(-0.02, 0.02) * angle
                    roll += random.uniform(-0.01, 0.01) * angle
                    yaw += random.uniform(-0.01, 0.01) * angle
                    
                    # Add to values list
                    motion_values.extend([pitch, roll, yaw])
                
                # Create data packet
                data = {
                    'timestamp': int(current_time),
                    'values': motion_values
                }
                
                # Call callback if defined
                if self.motion_callback:
                    self.motion_callback(data)
            
            # Small delay to prevent CPU hogging
            time.sleep(0.001)
        
    def set_callbacks(self, strain_callback=None, motion_callback=None):
        """Set the callback functions"""
        if strain_callback:
            self.strain_callback = strain_callback
        
        if motion_callback:
            self.motion_callback = motion_callback
