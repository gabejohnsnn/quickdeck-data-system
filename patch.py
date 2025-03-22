#!/usr/bin/env python3
"""
QuickDeck Data System - Compatibility Patch

This script provides compatibility fixes for newer Python versions (3.12+)
where some libraries might use deprecated functionality.
"""

import sys
import os
import pkgutil
import importlib.machinery

print("QuickDeck Data System - Compatibility Patch")
print("------------------------------------------")
print(f"Python version: {sys.version}")

# Check if ImpImporter is missing (removed in newer Python versions)
if not hasattr(pkgutil, 'ImpImporter'):
    print("Applying patch: Adding compatibility shim for pkgutil.ImpImporter")
    
    # Create compatibility shim
    class ImpImporter:
        def find_module(self, fullname, path=None):
            try:
                return importlib.machinery.PathFinder.find_spec(fullname, path)
            except (AttributeError, ImportError):
                return None
    
    # Patch pkgutil
    pkgutil.ImpImporter = ImpImporter
    print("✓ Patch applied successfully")

# Add the project path to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
    print(f"✓ Added {current_dir} to Python path")

print("Starting application...\n")

# Import and start the application
from python.main import main
main()
