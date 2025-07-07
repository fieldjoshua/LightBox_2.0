#!/usr/bin/env python3
"""
HUB75 LED Matrix Controller with Web GUI
Single file - just download and run!
"""

print("Downloading integrated HUB75 conductor...")
import urllib.request
import os

# Download the integrated conductor
url = "http://192.168.0.103:8000/integrated_hub75_conductor.py"
urllib.request.urlretrieve(url, "integrated_hub75_conductor.py")

# Create scripts directory
os.makedirs("scripts", exist_ok=True)

# Download animations
animations = [
    ("fire_feathered_hub75.py", "fire_animation.py"),
    ("ocean_waves_hub75.py", "ocean_waves.py"),
    ("aurora_hub75.py", "aurora.py"),
    ("hyperspace_120bpm_hub75.py", "hyperspace.py"),
    ("smooth_wave_hub75.py", "smooth_wave.py")
]

for src, dst in animations:
    try:
        url = f"http://192.168.0.103:8000/lightbox_deploy/scripts/{src}"
        urllib.request.urlretrieve(url, f"scripts/{dst}")
        print(f"✓ Downloaded {dst}")
    except:
        print(f"⚠️  Could not download {src}")

print("\nSetup complete!")
print("\nNow run:")
print("  sudo python3 integrated_hub75_conductor.py")
print("\nThen open web browser to:")
print("  http://lightbox.local:5000")