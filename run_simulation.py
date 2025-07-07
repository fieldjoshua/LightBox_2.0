#!/usr/bin/env python3
"""
Run LightBox in simulation mode for testing without hardware.
"""

import os
import sys

# Force simulation mode
os.environ['LIGHTBOX_SIMULATION'] = '1'

# Import and run the main conductor
from core.conductor import main

if __name__ == "__main__":
    print("Starting LightBox in SIMULATION MODE...")
    print("This allows testing without hardware connected.")
    print("Web interface will be available at http://localhost:5001")
    print("\nPress Ctrl+C to stop.")
    
    sys.exit(main())