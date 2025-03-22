#!/usr/bin/env python3
"""
QuickDeck Test - Visualization Module

This module handles real-time plotting of strain and motion data.
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import threading
import collections
import time

class DataVisualizer:
    """Handles real-time visualization of test data"""
    
    def __init__(self, maxlen=500):
        """Initialize the data visualizer"""
        # Store data in deques (fixed length)
        self.timestamps = collections.deque(maxlen=maxlen)
        
        # Strain data (8 channels)
        self.strain_data = [collections.deque(maxlen=maxlen) for _ in range(8)]
        
        # Motion data (pitch angles for 3 sensors)
        self.pitch_data = [collections.deque(maxlen=maxlen) for _ in range(3)]
        
        # Max values observed (for scaling)
        self.max_strain = 0.1  # Default small value
        self.max_deflection = 0.1  # Default small value
        
        # Setup figures
        self.strain_fig = None
        self.motion_fig = None
        
        # Plot references
        self.strain_lines = None
        self.motion_lines = None
        
        # Animation objects
        self.strain_animation = None
        self.motion_animation = None
        
        # Locks for thread safety
        self.strain_lock = threading.Lock()
        self.motion_lock = threading.Lock()
        
        # Flag to indicate if visualization is running
        self.running = False
    
    def update_strain_data(self, timestamp, values):
        """Update strain data buffers"""
        with self.strain_lock:
            self.timestamps.append(timestamp / 1000.0)  # Convert to seconds
            
            for i, value in enumerate(values):
                self.strain_data[i].append(value)
                self.max_strain = max(self.max_strain, abs(value))
    
    def update_motion_data(self, timestamp, values):
        """Update motion data buffers"""
        with self.motion_lock:
            # We're only using pitch values (every 3rd value starting from index 0)
            # values format is [pitch1, roll1, yaw1, pitch2, roll2, yaw2, pitch3, roll3, yaw3]
            pitch_values = [values[i] for i in range(0, len(values), 3)]
            
            for i, value in enumerate(pitch_values):
                if i < len(self.pitch_data):
                    self.pitch_data[i].append(value)
                    self.max_deflection = max(self.max_deflection, abs(value))
    
    def create_strain_figure(self, parent=None):
        """Create the strain visualization figure"""
        # Create figure
        self.strain_fig = Figure(figsize=(8, 5), dpi=100)
        ax = self.strain_fig.add_subplot(111)
        
        # Style the plot
        ax.set_title('Strain Gauge Readings')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Strain')
        ax.grid(True)
        
        # Create empty lines
        self.strain_lines = []
        colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'orange']
        
        for i in range(8):
            line, = ax.plot([], [], label=f'Channel {i+1}', color=colors[i])
            self.strain_lines.append(line)
        
        # Add legend
        ax.legend(loc='upper right')
        
        # Return the figure for embedding in GUI
        if parent:
            canvas = FigureCanvasTkAgg(self.strain_fig, master=parent)
            canvas.draw()
            return canvas.get_tk_widget()
        else:
            return self.strain_fig
    
    def create_motion_figure(self, parent=None):
        """Create the motion visualization figure"""
        # Create figure
        self.motion_fig = Figure(figsize=(8, 5), dpi=100)
        ax = self.motion_fig.add_subplot(111)
        
        # Style the plot
        ax.set_title('Angular Deflection')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Angle (degrees)')
        ax.grid(True)
        
        # Create empty lines
        self.motion_lines = []
        colors = ['r', 'g', 'b']
        labels = ['Connection Point', 'Mid-span', 'End Point']
        
        for i in range(3):
            line, = ax.plot([], [], label=labels[i], color=colors[i])
            self.motion_lines.append(line)
        
        # Add legend
        ax.legend(loc='upper right')
        
        # Return the figure for embedding in GUI
        if parent:
            canvas = FigureCanvasTkAgg(self.motion_fig, master=parent)
            canvas.draw()
            return canvas.get_tk_widget()
        else:
            return self.motion_fig
    
    def _update_strain_plot(self, frame):
        """Update function for strain animation"""
        with self.strain_lock:
            # Convert deques to lists for plotting
            x = list(self.timestamps)
            
            if not x:  # If no data yet, return
                return self.strain_lines
            
            # Update y-axis limit based on max value
            ax = self.strain_fig.axes[0]
            ax.set_ylim(-self.max_strain * 1.1, self.max_strain * 1.1)
            
            # Set x-axis to show last 60 seconds of data
            if x:
                current_time = x[-1]
                ax.set_xlim(max(0, current_time - 60), current_time + 1)
            
            # Update each line
            for i, line in enumerate(self.strain_lines):
                y = list(self.strain_data[i])
                if x and y:  # Only update if we have data
                    line.set_data(x, y)
        
        return self.strain_lines
    
    def _update_motion_plot(self, frame):
        """Update function for motion animation"""
        with self.motion_lock:
            # Convert deques to lists for plotting
            x = list(self.timestamps)
            
            if not x:  # If no data yet, return
                return self.motion_lines
            
            # Update y-axis limit based on max value
            ax = self.motion_fig.axes[0]
            ax.set_ylim(-self.max_deflection * 1.1, self.max_deflection * 1.1)
            
            # Set x-axis to show last 60 seconds of data
            if x:
                current_time = x[-1]
                ax.set_xlim(max(0, current_time - 60), current_time + 1)
            
            # Update each line
            for i, line in enumerate(self.motion_lines):
                y = list(self.pitch_data[i])
                if x and y:  # Only update if we have data
                    line.set_data(x, y)
        
        return self.motion_lines
    
    def start_visualization(self):
        """Start the real-time visualization"""
        if not self.strain_fig or not self.motion_fig:
            raise ValueError("Figures must be created before starting visualization")
        
        # Create animations
        self.strain_animation = animation.FuncAnimation(
            self.strain_fig, self._update_strain_plot, interval=100, blit=True)
        
        self.motion_animation = animation.FuncAnimation(
            self.motion_fig, self._update_motion_plot, interval=100, blit=True)
        
        self.running = True
    
    def stop_visualization(self):
        """Stop the real-time visualization"""
        if self.strain_animation:
            self.strain_animation.event_source.stop()
        
        if self.motion_animation:
            self.motion_animation.event_source.stop()
        
        self.running = False
    
    def clear_data(self):
        """Clear all stored data"""
        with self.strain_lock:
            self.timestamps.clear()
            for data in self.strain_data:
                data.clear()
            self.max_strain = 0.1
        
        with self.motion_lock:
            for data in self.pitch_data:
                data.clear()
            self.max_deflection = 0.1

# Simple test code
if __name__ == "__main__":
    import numpy as np
    
    # Create visualizer
    visualizer = DataVisualizer()
    
    # Create figures
    plt.ion()  # Turn on interactive mode
    visualizer.create_strain_figure()
    visualizer.create_motion_figure()
    
    # Start visualization
    visualizer.start_visualization()
    
    # Generate some test data
    start_time = time.time() * 1000  # Current time in milliseconds
    
    try:
        for i in range(1000):
            # Create simulated timestamp
            timestamp = start_time + i * 100  # 10 Hz data
            
            # Create simulated strain data
            strain_values = [np.sin(i * 0.1 + j * 0.5) * 100 for j in range(8)]
            
            # Create simulated motion data (pitch, roll, yaw for 3 sensors)
            motion_values = []
            for j in range(3):
                # Increasing amplitude with sensor position
                pitch = np.sin(i * 0.1) * (j + 1) * 5
                roll = np.cos(i * 0.1) * (j + 1) * 2
                yaw = np.sin(i * 0.05) * (j + 1) * 1
                motion_values.extend([pitch, roll, yaw])
            
            # Update visualizer
            visualizer.update_strain_data(timestamp, strain_values)
            visualizer.update_motion_data(timestamp, motion_values)
            
            # Pause to simulate real-time data
            plt.pause(0.1)
    
    except KeyboardInterrupt:
        print("Test interrupted by user")
    
    # Stop visualization
    visualizer.stop_visualization()
    
    print("Test complete")