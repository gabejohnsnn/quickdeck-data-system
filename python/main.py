#!/usr/bin/env python3
"""
QuickDeck Test - Main Application

This is the main entry point for the QuickDeck testing software.
It creates a GUI for controlling the test and visualizing data.
"""

import os
import sys
import time
import serial
import threading
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Import our modules
from data_acquisition import DataAcquisition
from visualization import DataVisualizer
from data_storage import DataStorage
from mock_data import MockDataGenerator

class QuickDeckApp:
    """Main application class for QuickDeck testing"""
    
    def __init__(self, root):
        """Initialize the application"""
        self.root = root
        self.root.title("QuickDeck Testing System")
        self.root.geometry("1200x800")
        
        # Create components
        self.data_acquisition = DataAcquisition(
            strain_data_callback=self.on_strain_data,
            motion_data_callback=self.on_motion_data
        )
        
        # Create mock data generator
        self.mock_data = MockDataGenerator(
            strain_callback=self.on_strain_data,
            motion_callback=self.on_motion_data
        )
        
        self.visualizer = DataVisualizer()
        self.data_storage = DataStorage()
        
        # Current test name
        self.current_test = None
        
        # Status variables
        self.strain_connected = False
        self.motion_connected = False
        self.acquisition_running = False
        
        # Create GUI
        self.create_gui()
        
        # Update available ports list periodically
        self.update_ports()
        
    def create_gui(self):
        """Create the GUI interface"""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create control panel on the left
        control_frame = ttk.LabelFrame(main_frame, text="Control Panel", padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Simulation toggle
        sim_frame = ttk.Frame(control_frame)
        sim_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.simulation_var = tk.BooleanVar(value=True)  # Default to simulation mode
        simulation_check = ttk.Checkbutton(sim_frame, text="Simulation Mode (No Hardware Required)", 
                                         variable=self.simulation_var)
        simulation_check.pack(fill=tk.X, padx=5, pady=5)
        
        # Connection section
        conn_frame = ttk.LabelFrame(control_frame, text="Connection", padding=10)
        conn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Strain Arduino selection
        ttk.Label(conn_frame, text="Strain Arduino:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.strain_port_var = tk.StringVar()
        self.strain_port_combo = ttk.Combobox(conn_frame, textvariable=self.strain_port_var, width=30)
        self.strain_port_combo.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        # Motion Arduino selection
        ttk.Label(conn_frame, text="Motion Arduino:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.motion_port_var = tk.StringVar()
        self.motion_port_combo = ttk.Combobox(conn_frame, textvariable=self.motion_port_var, width=30)
        self.motion_port_combo.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # Connect buttons
        self.strain_connect_btn = ttk.Button(conn_frame, text="Connect", command=self.connect_strain)
        self.strain_connect_btn.grid(row=0, column=2, padx=5, pady=2)
        
        self.motion_connect_btn = ttk.Button(conn_frame, text="Connect", command=self.connect_motion)
        self.motion_connect_btn.grid(row=1, column=2, padx=5, pady=2)
        
        # Refresh ports button
        refresh_btn = ttk.Button(conn_frame, text="Refresh Ports", command=self.update_ports)
        refresh_btn.grid(row=2, column=1, pady=5)
        
        # Test control section
        test_frame = ttk.LabelFrame(control_frame, text="Test Control", padding=10)
        test_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Test name input
        ttk.Label(test_frame, text="Test Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.test_name_var = tk.StringVar()
        self.test_name_var.set(f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        test_name_entry = ttk.Entry(test_frame, textvariable=self.test_name_var, width=30)
        test_name_entry.grid(row=0, column=1, columnspan=2, sticky=tk.W, pady=2)
        
        # Start/Stop buttons
        self.start_btn = ttk.Button(test_frame, text="Start Test", command=self.start_test)
        self.start_btn.grid(row=1, column=0, pady=10)
        
        self.stop_btn = ttk.Button(test_frame, text="Stop Test", command=self.stop_test, state=tk.DISABLED)
        self.stop_btn.grid(row=1, column=1, pady=10)
        
        # Calibration button
        self.calibrate_btn = ttk.Button(test_frame, text="Calibrate Sensors", command=self.calibrate_sensors)
        self.calibrate_btn.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Simulation load control (initially hidden)
        sim_btn_frame = ttk.Frame(test_frame)
        sim_btn_frame.grid(row=3, column=0, columnspan=2, pady=5)
        
        inc_load_btn = ttk.Button(sim_btn_frame, text="Increase Load", 
                                 command=self.increase_simulated_load)
        inc_load_btn.pack(side=tk.LEFT, padx=5)
        
        dec_load_btn = ttk.Button(sim_btn_frame, text="Decrease Load", 
                                 command=self.decrease_simulated_load)
        dec_load_btn.pack(side=tk.LEFT, padx=5)
        
        # Status indicators
        status_frame = ttk.LabelFrame(control_frame, text="Status", padding=10)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Status labels
        ttk.Label(status_frame, text="Strain Arduino:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.strain_status_var = tk.StringVar(value="Disconnected")
        ttk.Label(status_frame, textvariable=self.strain_status_var).grid(row=0, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(status_frame, text="Motion Arduino:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.motion_status_var = tk.StringVar(value="Disconnected")
        ttk.Label(status_frame, textvariable=self.motion_status_var).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(status_frame, text="Test Status:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.test_status_var = tk.StringVar(value="Idle")
        ttk.Label(status_frame, textvariable=self.test_status_var).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Data management section
        data_frame = ttk.LabelFrame(control_frame, text="Data Management", padding=10)
        data_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # View previous tests button
        view_btn = ttk.Button(data_frame, text="View Previous Tests", command=self.view_previous_tests)
        view_btn.pack(fill=tk.X, pady=5)
        
        # Export data button
        export_btn = ttk.Button(data_frame, text="Export Current Test to Excel", command=self.export_data)
        export_btn.pack(fill=tk.X, pady=5)
        
        # Create right side for visualizations
        viz_frame = ttk.Frame(main_frame)
        viz_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(viz_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Strain visualization tab
        strain_tab = ttk.Frame(notebook)
        notebook.add(strain_tab, text="Strain Gauges")
        
        # Create strain visualization
        self.strain_canvas = self.visualizer.create_strain_figure(strain_tab)
        self.strain_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Motion visualization tab
        motion_tab = ttk.Frame(notebook)
        notebook.add(motion_tab, text="Angular Deflection")
        
        # Create motion visualization
        self.motion_canvas = self.visualizer.create_motion_figure(motion_tab)
        self.motion_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Start visualization
        self.visualizer.start_visualization()
        
        # Status bar at bottom
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def update_ports(self):
        """Update the list of available serial ports"""
        # Get available ports
        ports = self.data_acquisition.get_available_ports()
        
        # Format port strings
        port_strings = [f"{port['device']} - {port['description']}" for port in ports]
        
        # Update comboboxes
        self.strain_port_combo['values'] = port_strings
        self.motion_port_combo['values'] = port_strings
        
        # Select first port if available and not already connected
        if port_strings and not self.strain_connected:
            self.strain_port_combo.current(0)
        
        if port_strings and not self.motion_connected and len(port_strings) > 1:
            self.motion_port_combo.current(1)
        elif port_strings and not self.motion_connected:
            self.motion_port_combo.current(0)
        
        # Schedule next update
        self.root.after(5000, self.update_ports)
    
    def connect_strain(self):
        """Connect to the strain Arduino"""
        if self.simulation_var.get():
            messagebox.showinfo("Simulation Mode", "You are in simulation mode. No hardware connection needed.")
            return
            
        if self.strain_connected:
            # Already connected, so disconnect
            self.data_acquisition.disconnect()
            self.strain_connected = False
            self.strain_status_var.set("Disconnected")
            self.strain_connect_btn.configure(text="Connect")
            
            # Update status
            self.status_bar.configure(text="Disconnected from strain Arduino")
            
            return
        
        # Get selected port
        port_string = self.strain_port_var.get()
        if not port_string:
            messagebox.showerror("Error", "No port selected")
            return
        
        # Extract device name from string
        port = port_string.split(" - ")[0]
        
        # Try to connect
        if self.data_acquisition.connect_strain_arduino(port):
            self.strain_connected = True
            self.strain_status_var.set("Connected")
            self.strain_connect_btn.configure(text="Disconnect")
            
            # Update status
            self.status_bar.configure(text=f"Connected to strain Arduino on {port}")
        else:
            messagebox.showerror("Connection Error", f"Failed to connect to strain Arduino on {port}")
    
    def connect_motion(self):
        """Connect to the motion Arduino"""
        if self.simulation_var.get():
            messagebox.showinfo("Simulation Mode", "You are in simulation mode. No hardware connection needed.")
            return
            
        if self.motion_connected:
            # Already connected, so disconnect
            self.data_acquisition.disconnect()
            self.motion_connected = False
            self.motion_status_var.set("Disconnected")
            self.motion_connect_btn.configure(text="Connect")
            
            # Update status
            self.status_bar.configure(text="Disconnected from motion Arduino")
            
            return
        
        # Get selected port
        port_string = self.motion_port_var.get()
        if not port_string:
            messagebox.showerror("Error", "No port selected")
            return
        
        # Extract device name from string
        port = port_string.split(" - ")[0]
        
        # Try to connect
        if self.data_acquisition.connect_motion_arduino(port):
            self.motion_connected = True
            self.motion_status_var.set("Connected")
            self.motion_connect_btn.configure(text="Disconnect")
            
            # Update status
            self.status_bar.configure(text=f"Connected to motion Arduino on {port}")
        else:
            messagebox.showerror("Connection Error", f"Failed to connect to motion Arduino on {port}")
    
    def start_test(self):
        """Start data acquisition and test"""
        if self.simulation_var.get():
            # Use mock data generator
            test_name = self.test_name_var.get()
            if not test_name:
                test_name = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self.test_name_var.set(test_name)
            
            # Create test directory
            self.data_storage.create_test_directory(test_name)
            
            # Start mock data generation
            if self.mock_data.start():
                self.acquisition_running = True
                self.test_status_var.set("Running (Simulation)")
                
                # Update button states
                self.start_btn.configure(state=tk.DISABLED)
                self.stop_btn.configure(state=tk.NORMAL)
                
                # Reset visualizer
                self.visualizer.clear_data()
                
                # Update status
                self.status_bar.configure(text=f"Simulated test '{test_name}' started")
                
                # Store current test name
                self.current_test = test_name
            else:
                messagebox.showerror("Error", "Failed to start mock data generation")
        else:
            # Original code for hardware testing
            if not (self.strain_connected and self.motion_connected):
                messagebox.showerror("Error", "Both Arduinos must be connected before starting test")
                return
            
            # Get test name
            test_name = self.test_name_var.get()
            if not test_name:
                test_name = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self.test_name_var.set(test_name)
            
            # Create test directory
            self.data_storage.create_test_directory(test_name)
            
            # Start data acquisition
            if self.data_acquisition.start_acquisition(test_name):
                self.acquisition_running = True
                self.test_status_var.set("Running")
                
                # Update button states
                self.start_btn.configure(state=tk.DISABLED)
                self.stop_btn.configure(state=tk.NORMAL)
                
                # Reset visualizer
                self.visualizer.clear_data()
                
                # Update status
                self.status_bar.configure(text=f"Test '{test_name}' started")
                
                # Store current test name
                self.current_test = test_name
            else:
                messagebox.showerror("Error", "Failed to start data acquisition")
    
    def stop_test(self):
        """Stop data acquisition and finalize test"""
        if not self.acquisition_running:
            return
        
        # Stop data acquisition based on mode
        if self.simulation_var.get():
            self.mock_data.stop()
        else:
            self.data_acquisition.stop_acquisition()
            
        self.acquisition_running = False
        
        # Finalize test in data storage
        if self.current_test:
            self.data_storage.finalize_test()
        
        # Update status
        self.test_status_var.set("Completed")
        
        # Update button states
        self.start_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)
        
        # Generate new test name for next test
        new_test_name = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.test_name_var.set(new_test_name)
        
        # Update status
        self.status_bar.configure(text=f"Test '{self.current_test}' completed")
        
        # Offer to view results
        if messagebox.askyesno("Test Completed", f"Test '{self.current_test}' has completed. View results?"):
            self.view_test_results(self.current_test)
    
    def increase_simulated_load(self):
        """Increase the simulated load"""
        if self.acquisition_running and self.simulation_var.get():
            self.mock_data.increase_load()
            self.status_bar.configure(text="Simulated load increased")
        else:
            if not self.simulation_var.get():
                messagebox.showinfo("Hardware Mode", "Load control is only available in simulation mode")
            else:
                messagebox.showinfo("Not Running", "Start a test first to control the load")
    
    def decrease_simulated_load(self):
        """Decrease the simulated load"""
        if self.acquisition_running and self.simulation_var.get():
            self.mock_data.decrease_load()
            self.status_bar.configure(text="Simulated load decreased")
        else:
            if not self.simulation_var.get():
                messagebox.showinfo("Hardware Mode", "Load control is only available in simulation mode")
            else:
                messagebox.showinfo("Not Running", "Start a test first to control the load")
    
    def calibrate_sensors(self):
        """Calibrate sensors on both Arduinos"""
        if self.simulation_var.get():
            messagebox.showinfo("Simulation Mode", "Calibration not needed in simulation mode")
            return
            
        if not (self.strain_connected and self.motion_connected):
            messagebox.showerror("Error", "Both Arduinos must be connected before calibration")
            return
        
        # Send calibration commands
        self.data_acquisition.send_command_to_strain("TARE")
        self.data_acquisition.send_command_to_motion("CALIBRATE")
        
        # Update status
        self.status_bar.configure(text="Sensors calibrated")
        
        messagebox.showinfo("Calibration", "Sensors have been calibrated.")
    
    def view_previous_tests(self):
        """View list of previous tests"""
        tests = self.data_storage.list_tests()
        
        if not tests:
            messagebox.showinfo("Tests", "No previous tests found")
            return
        
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Previous Tests")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create listbox with tests
        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Select a test to view:").pack(anchor=tk.W)
        
        listbox = tk.Listbox(frame, width=60, height=15)
        listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Add tests to listbox
        for test in tests:
            listbox.insert(tk.END, f"{test['name']} - {test['start_time']}")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(listbox, orient=tk.VERTICAL, command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.configure(yscrollcommand=scrollbar.set)
        
        # Button frame
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        # View button
        def view_selected():
            selection = listbox.curselection()
            if selection:
                index = selection[0]
                test_name = tests[index]['name']
                dialog.destroy()
                self.view_test_results(test_name)
        
        view_btn = ttk.Button(btn_frame, text="View Selected Test", command=view_selected)
        view_btn.pack(side=tk.LEFT, padx=5)
        
        # Export button
        def export_selected():
            selection = listbox.curselection()
            if selection:
                index = selection[0]
                test_name = tests[index]['name']
                dialog.destroy()
                self.export_test_data(test_name)
        
        export_btn = ttk.Button(btn_frame, text="Export to Excel", command=export_selected)
        export_btn.pack(side=tk.LEFT, padx=5)
        
        # Close button
        close_btn = ttk.Button(btn_frame, text="Close", command=dialog.destroy)
        close_btn.pack(side=tk.RIGHT, padx=5)
    
    def view_test_results(self, test_name):
        """View results of a specific test"""
        # Load test data
        try:
            data = self.data_storage.load_test_data(test_name)
            
            # Create dialog
            dialog = tk.Toplevel(self.root)
            dialog.title(f"Test Results: {test_name}")
            dialog.geometry("800x600")
            dialog.transient(self.root)
            
            # Create notebook for tabs
            notebook = ttk.Notebook(dialog)
            notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Info tab
            info_tab = ttk.Frame(notebook)
            notebook.add(info_tab, text="Test Info")
            
            info_frame = ttk.Frame(info_tab, padding=10)
            info_frame.pack(fill=tk.BOTH, expand=True)
            
            # Test metadata
            ttk.Label(info_frame, text="Test Information", font=("TkDefaultFont", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
            
            row = 1
            for key, value in data.get("metadata", {}).items():
                if isinstance(value, dict):
                    continue  # Skip nested dictionaries
                
                ttk.Label(info_frame, text=f"{key}:").grid(row=row, column=0, sticky=tk.W, pady=2)
                ttk.Label(info_frame, text=str(value)).grid(row=row, column=1, sticky=tk.W, pady=2)
                row += 1
            
            # Test summary
            if "summary" in data:
                ttk.Label(info_frame, text="Summary", font=("TkDefaultFont", 12, "bold")).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
                row += 1
                
                for key, value in data["summary"].items():
                    if isinstance(value, dict):
                        continue  # Skip nested dictionaries
                    
                    ttk.Label(info_frame, text=f"{key}:").grid(row=row, column=0, sticky=tk.W, pady=2)
                    ttk.Label(info_frame, text=str(value)).grid(row=row, column=1, sticky=tk.W, pady=2)
                    row += 1
            
            # Add export button
            export_btn = ttk.Button(info_frame, text="Export to Excel", 
                                   command=lambda: self.export_test_data(test_name))
            export_btn.grid(row=row, column=0, columnspan=2, pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load test data: {str(e)}")
    
    def export_data(self):
        """Export current test data to Excel"""
        if self.current_test:
            self.export_test_data(self.current_test)
        else:
            messagebox.showerror("Error", "No current test to export")
    
    def export_test_data(self, test_name):
        """Export specific test data to Excel"""
        try:
            # Export data
            excel_path = self.data_storage.export_to_excel(test_name)
            
            # Show success message with path
            messagebox.showinfo("Export Successful", 
                               f"Test data exported to:\n{excel_path}")
            
            # Ask if user wants to open the file
            if messagebox.askyesno("Open File", "Do you want to open the exported file?"):
                # Open the file with default application
                if sys.platform == 'win32':
                    os.startfile(excel_path)
                elif sys.platform == 'darwin':  # macOS
                    os.system(f"open '{excel_path}'")
                else:  # Linux
                    os.system(f"xdg-open '{excel_path}'")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")
    
    def on_strain_data(self, data):
        """Handle new strain data"""
        if self.acquisition_running:
            # Update visualizer
            self.visualizer.update_strain_data(data['timestamp'], data['values'])
    
    def on_motion_data(self, data):
        """Handle new motion data"""
        if self.acquisition_running:
            # Update visualizer
            self.visualizer.update_motion_data(data['timestamp'], data['values'])
    
    def on_closing(self):
        """Handle window close event"""
        if self.acquisition_running:
            if not messagebox.askyesno("Quit", "A test is currently running. Are you sure you want to quit?"):
                return
            
            # Stop acquisition
            self.stop_test()
        
        # Stop visualization
        self.visualizer.stop_visualization()
        
        # Disconnect from Arduino
        self.data_acquisition.disconnect()
        
        # Destroy window
        self.root.destroy()

def main():
    """Main entry point"""
    # Create root window
    root = tk.Tk()
    
    # Create application
    app = QuickDeckApp(root)
    
    # Set up close handler
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Start main loop
    root.mainloop()

if __name__ == "__main__":
    main()