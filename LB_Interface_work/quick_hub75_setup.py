#!/usr/bin/env python3
"""
Quick setup for HUB75 with rgbmatrix library
Just copy this ONE file to your Pi and run it
"""

import os
import subprocess

print("=== Quick HUB75 Setup ===")

# First, check if rgbmatrix is installed
try:
    import rgbmatrix
    print("✓ rgbmatrix already installed")
except ImportError:
    print("Installing rgbmatrix library...")
    print("This will take 10-15 minutes...")
    
    # Download and run Adafruit installer
    os.system("curl https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/main/rgb-matrix.sh > rgb-matrix.sh")
    os.system("sudo bash rgb-matrix.sh")

# Create a simple test
print("\nCreating test animation...")

test_code = '''#!/usr/bin/env python3
from rgbmatrix import RGBMatrix, RGBMatrixOptions
import time
import math

# Setup
options = RGBMatrixOptions()
options.rows = 64
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'
options.gpio_slowdown = 4
options.brightness = 80
options.pwm_bits = 11

matrix = RGBMatrix(options=options)
canvas = matrix.CreateFrameCanvas()

print("Running smooth test... Press Ctrl+C to stop")
frame = 0
try:
    while True:
        for x in range(64):
            for y in range(64):
                hue = ((x + y) / 128.0 + math.sin(frame * 0.01) * 0.2) * 6
                if hue < 1: r, g, b = 1, hue, 0
                elif hue < 2: r, g, b = 2-hue, 1, 0
                elif hue < 3: r, g, b = 0, 1, hue-2
                elif hue < 4: r, g, b = 0, 4-hue, 1
                elif hue < 5: r, g, b = hue-4, 0, 1
                else: r, g, b = 1, 0, 6-hue
                canvas.SetPixel(x, y, int(r*255), int(g*255), int(b*255))
        canvas = matrix.SwapOnVSync(canvas)
        frame += 1
except KeyboardInterrupt:
    matrix.Clear()
'''

with open("hub75_test.py", "w") as f:
    f.write(test_code)

os.chmod("hub75_test.py", 0o755)

print("\n✅ Setup complete!")
print("\nRun the test with:")
print("  sudo python3 hub75_test.py")
print("\nIf you see smooth colors, hardware acceleration is working!")