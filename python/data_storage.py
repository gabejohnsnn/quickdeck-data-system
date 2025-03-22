#!/usr/bin/env python3
"""
QuickDeck Test - Data Storage Module

This module handles saving test data and metadata to disk.
"""

import os
import csv
import json
from datetime import datetime
import pandas as pd
import numpy as np

class DataStorage:
    """Handles data storage and retrieval for test data"""
    
    def __init__(self, base_dir="data"):
        """Initialize data storage with base directory"""
        self.base_dir = base_dir
        
        # Create base directory if it doesn't exist
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
        
        # Current test directory
        self.current_test_dir = None
        
        # Current test metadata
        self.metadata = {}
    
    def create_test_directory(self, test_name=None):
        """Create a directory for a new test"""
        if test_name is None:
            # Generate test name from current timestamp
            test_name = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create test directory
        test_dir = os.path.join(self.base_dir, test_name)
        os.makedirs(test_dir, exist_ok=True)
        
        # Store current test directory
        self.current_test_dir = test_dir
        
        # Initialize metadata
        self.metadata = {
            "test_name": test_name,
            "start_time": datetime.now().isoformat(),
            "strain_channels": 8,
            "motion_sensors": 3,
            "sample_rate_strain": 10,  # Hz
            "sample_rate_motion": 100  # Hz
        }
        
        # Save initial metadata
        self.save_metadata()
        
        return test_dir
    
    def save_metadata(self, additional_data=None):
        """Save metadata to test directory"""
        if self.current_test_dir is None:
            raise ValueError("No active test. Call create_test_directory first.")
        
        # Update metadata with additional data
        if additional_data:
            self.metadata.update(additional_data)
        
        # Write metadata to file
        metadata_path = os.path.join(self.current_test_dir, "metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=4)
    
    def finalize_test(self, additional_data=None):
        """Finalize test by updating metadata and saving summary"""
        if self.current_test_dir is None:
            raise ValueError("No active test to finalize.")
        
        # Update metadata with end time and any additional data
        end_metadata = {
            "end_time": datetime.now().isoformat()
        }
        
        if additional_data:
            end_metadata.update(additional_data)
        
        # Save final metadata
        self.save_metadata(end_metadata)
        
        # Generate and save summary if data files exist
        self.generate_summary()
        
        # Return test directory for reference
        test_dir = self.current_test_dir
        self.current_test_dir = None
        return test_dir
    
    def generate_summary(self):
        """Generate and save summary statistics of test data"""
        if self.current_test_dir is None:
            raise ValueError("No active test for summary generation.")
        
        # Check if data files exist
        strain_path = os.path.join(self.current_test_dir, "strain_data.csv")
        motion_path = os.path.join(self.current_test_dir, "motion_data.csv")
        
        summary = {}
        
        # Process strain data if file exists
        if os.path.exists(strain_path):
            try:
                strain_df = pd.read_csv(strain_path)
                
                # Calculate basic statistics for each strain channel
                strain_stats = {}
                for i in range(1, 9):
                    col = f"strain{i}"
                    if col in strain_df.columns:
                        strain_stats[col] = {
                            "min": strain_df[col].min(),
                            "max": strain_df[col].max(),
                            "mean": strain_df[col].mean(),
                            "std": strain_df[col].std()
                        }
                
                summary["strain_statistics"] = strain_stats
                
                # Calculate test duration
                if len(strain_df) > 1:
                    start_time = strain_df["timestamp"].iloc[0]
                    end_time = strain_df["timestamp"].iloc[-1]
                    duration_ms = end_time - start_time
                    summary["duration_seconds"] = duration_ms / 1000
                
            except Exception as e:
                print(f"Error generating strain summary: {e}")
        
        # Process motion data if file exists
        if os.path.exists(motion_path):
            try:
                motion_df = pd.read_csv(motion_path)
                
                # Calculate basic statistics for each pitch angle
                motion_stats = {}
                for i in range(1, 4):
                    col = f"sensor{i}_pitch"
                    if col in motion_df.columns:
                        motion_stats[col] = {
                            "min": motion_df[col].min(),
                            "max": motion_df[col].max(),
                            "mean": motion_df[col].mean(),
                            "std": motion_df[col].std()
                        }
                
                summary["motion_statistics"] = motion_stats
                
                # Calculate maximum deflection angle
                for i in range(1, 4):
                    col = f"sensor{i}_pitch"
                    if col in motion_df.columns:
                        max_angle = motion_df[col].abs().max()
                        summary[f"max_angle_sensor{i}"] = max_angle
                
            except Exception as e:
                print(f"Error generating motion summary: {e}")
        
        # Save summary to file
        if summary:
            summary_path = os.path.join(self.current_test_dir, "summary.json")
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=4)
            
            # Update metadata with summary
            self.metadata["summary"] = summary
            self.save_metadata()
        
        return summary
    
    def list_tests(self):
        """List all available tests in the base directory"""
        tests = []
        
        # Check each subdirectory for metadata file
        for item in os.listdir(self.base_dir):
            dir_path = os.path.join(self.base_dir, item)
            metadata_path = os.path.join(dir_path, "metadata.json")
            
            if os.path.isdir(dir_path) and os.path.exists(metadata_path):
                try:
                    # Load metadata
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                    
                    # Extract key information
                    test_info = {
                        "name": item,
                        "start_time": metadata.get("start_time", "Unknown"),
                        "end_time": metadata.get("end_time", "Unknown"),
                        "directory": dir_path
                    }
                    
                    tests.append(test_info)
                
                except Exception as e:
                    print(f"Error reading metadata for {item}: {e}")
        
        # Sort by start time (newest first)
        tests.sort(key=lambda x: x["start_time"], reverse=True)
        
        return tests
    
    def load_test_data(self, test_name):
        """Load data from a previous test"""
        test_dir = os.path.join(self.base_dir, test_name)
        
        if not os.path.exists(test_dir):
            raise ValueError(f"Test directory not found: {test_dir}")
        
        data = {}
        
        # Load metadata
        metadata_path = os.path.join(test_dir, "metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                data["metadata"] = json.load(f)
        
        # Load strain data
        strain_path = os.path.join(test_dir, "strain_data.csv")
        if os.path.exists(strain_path):
            data["strain_data"] = pd.read_csv(strain_path)
        
        # Load motion data
        motion_path = os.path.join(test_dir, "motion_data.csv")
        if os.path.exists(motion_path):
            data["motion_data"] = pd.read_csv(motion_path)
        
        # Load summary
        summary_path = os.path.join(test_dir, "summary.json")
        if os.path.exists(summary_path):
            with open(summary_path, 'r') as f:
                data["summary"] = json.load(f)
        
        return data
    
    def export_to_excel(self, test_name):
        """Export test data to Excel format"""
        # Load test data
        data = self.load_test_data(test_name)
        
        if not data:
            raise ValueError(f"No data found for test: {test_name}")
        
        # Create Excel file path
        excel_path = os.path.join(self.base_dir, f"{test_name}.xlsx")
        
        # Create Excel writer
        with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
            # Write strain data
            if "strain_data" in data:
                data["strain_data"].to_excel(writer, sheet_name="Strain Data", index=False)
            
            # Write motion data
            if "motion_data" in data:
                data["motion_data"].to_excel(writer, sheet_name="Motion Data", index=False)
            
            # Write metadata and summary
            if "metadata" in data or "summary" in data:
                # Convert to DataFrame for Excel
                metadata_df = pd.DataFrame(columns=["Key", "Value"])
                
                if "metadata" in data:
                    for key, value in data["metadata"].items():
                        if not isinstance(value, dict):  # Skip nested dictionaries
                            metadata_df = pd.concat([metadata_df, pd.DataFrame({"Key": [key], "Value": [value]})], ignore_index=True)
                
                if "summary" in data:
                    metadata_df = pd.concat([metadata_df, pd.DataFrame({"Key": [""], "Value": [""]}), pd.DataFrame({"Key": ["SUMMARY"], "Value": [""]})], ignore_index=True)
                    
                    for key, value in data["summary"].items():
                        if not isinstance(value, dict):  # Skip nested dictionaries
                            metadata_df = pd.concat([metadata_df, pd.DataFrame({"Key": [key], "Value": [value]})], ignore_index=True)
                
                metadata_df.to_excel(writer, sheet_name="Metadata", index=False)
        
        return excel_path

# Simple test code
if __name__ == "__main__":
    # Create data storage
    storage = DataStorage()
    
    # Create a test directory
    test_dir = storage.create_test_directory()
    print(f"Created test directory: {test_dir}")
    
    # Generate some sample data
    strain_data_path = os.path.join(test_dir, "strain_data.csv")
    motion_data_path = os.path.join(test_dir, "motion_data.csv")
    
    # Create sample strain data
    with open(strain_data_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'strain1', 'strain2', 'strain3', 'strain4', 'strain5', 'strain6', 'strain7', 'strain8'])
        
        for i in range(100):
            timestamp = 1000 + i * 100  # Starting at 1 second, 10 Hz
            strain_values = [np.sin(i * 0.1 + j * 0.5) * 100 for j in range(8)]
            writer.writerow([timestamp] + strain_values)
    
    # Create sample motion data
    with open(motion_data_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'sensor1_pitch', 'sensor1_roll', 'sensor1_yaw', 'sensor2_pitch', 'sensor2_roll', 'sensor2_yaw', 'sensor3_pitch', 'sensor3_roll', 'sensor3_yaw'])
        
        for i in range(1000):  # 100 Hz
            timestamp = 1000 + i * 10
            motion_values = []
            for j in range(3):
                pitch = np.sin(i * 0.01) * (j + 1) * 5
                roll = np.cos(i * 0.01) * (j + 1) * 2
                yaw = np.sin(i * 0.005) * (j + 1) * 1
                motion_values.extend([pitch, roll, yaw])
            
            writer.writerow([timestamp] + motion_values)
    
    # Add some metadata
    storage.save_metadata({
        "load_applied": 500,  # Example: 500 kg
        "test_operator": "Test Engineer",
        "test_description": "Initial validation test"
    })
    
    # Finalize the test
    storage.finalize_test({
        "test_result": "PASS",
        "notes": "Maximum deflection within acceptable range"
    })
    
    # List available tests
    tests = storage.list_tests()
    print(f"Available tests: {len(tests)}")
    for test in tests:
        print(f"- {test['name']} ({test['start_time']})")
    
    # Export to Excel
    if tests:
        excel_path = storage.export_to_excel(tests[0]["name"])
        print(f"Exported test data to: {excel_path}")
    
    print("Test complete")