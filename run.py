#!/usr/bin/env python3
"""
QuickDeck Data System Launcher

Simple wrapper script to start the QuickDeck data acquisition application.
"""

import sys
import os

# Add the python directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'python'))

# Import the main module
from python.main import main

if __name__ == "__main__":
    # Start the application
    main()
