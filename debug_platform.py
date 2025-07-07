#!/usr/bin/env python3
"""Debug script to diagnose platform detection and import issues on Pi."""

import os
import sys
import platform
import subprocess

def main():
    print("=== LightBox Platform Debug ===")
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Machine: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    
    # Check environment variables
    print("\n=== Environment Variables ===")
    print(f"LIGHTBOX_SIMULATION: {os.environ.get('LIGHTBOX_SIMULATION', 'Not set')}")
    print(f"LIGHTBOX_PLATFORM: {os.environ.get('LIGHTBOX_PLATFORM', 'Not set')}")
    
    # Check CPU info
    print("\n=== CPU Info ===")
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            # Look for model info
            for line in cpuinfo.split('\n'):
                if 'Model' in line or 'Hardware' in line or 'Revision' in line:
                    print(line)
            
            # Check BCM chip
            if 'BCM2835' in cpuinfo:
                print("Found: BCM2835 (Pi Zero/1/2/3)")
            if 'BCM2836' in cpuinfo:
                print("Found: BCM2836 (Pi 2)")
            if 'BCM2837' in cpuinfo:
                print("Found: BCM2837 (Pi 3/3+)")
            if 'BCM2711' in cpuinfo:
                print("Found: BCM2711 (Pi 4)")
    except FileNotFoundError:
        print("No /proc/cpuinfo found (not running on Pi)")
    
    # Check device tree model
    print("\n=== Device Tree Model ===")
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read().strip()
            print(f"Model: {model}")
    except:
        print("No device tree model found")
    
    # Check GPIO chip
    print("\n=== GPIO Detection ===")
    try:
        result = subprocess.run(['gpio', '-v'], capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout.strip())
    except:
        print("gpio command not found")
    
    # Test imports
    print("\n=== Import Tests ===")
    test_imports = [
        'neopixel',
        'board',
        'rgbmatrix',
        'psutil',
        'flask',
        'numpy'
    ]
    
    for module in test_imports:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
    
    # Check current directory structure
    print("\n=== Directory Structure ===")
    print(f"Current dir: {os.getcwd()}")
    print(f"Script dir: {os.path.dirname(os.path.abspath(__file__))}")
    
    # List key directories
    for dir_name in ['core', 'drivers', 'animations', 'utils', 'web']:
        dir_path = os.path.join(os.path.dirname(__file__), dir_name)
        if os.path.exists(dir_path):
            print(f"✓ {dir_name}/ exists")
        else:
            print(f"✗ {dir_name}/ missing")
    
    # Check settings.json
    print("\n=== Settings File ===")
    settings_path = os.path.join(os.path.dirname(__file__), 'settings.json')
    if os.path.exists(settings_path):
        print(f"✓ settings.json exists")
        try:
            import json
            with open(settings_path, 'r') as f:
                settings = json.load(f)
                if 'platform' in settings:
                    print(f"  Platform setting: {settings['platform']}")
        except Exception as e:
            print(f"  Error reading settings: {e}")
    else:
        print("✗ settings.json missing")
    
    # Test platform detection logic
    print("\n=== Platform Detection Logic ===")
    print("Testing current detection method...")
    
    # Method 1: Check device tree (most reliable)
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read().strip().lower()
            if 'zero' in model:
                print("→ Detected as Pi Zero W (via device tree)")
            elif '3 model b plus' in model or '3b+' in model:
                print("→ Detected as Pi 3B+ (via device tree)")
            elif '3' in model:
                print("→ Detected as Pi 3 (via device tree)")
            elif '4' in model:
                print("→ Detected as Pi 4 (via device tree)")
            else:
                print(f"→ Unknown model: {model}")
    except:
        print("→ Device tree method failed")
    
    # Method 2: Check revision code
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line.startswith('Revision'):
                    revision = line.split(':')[1].strip()
                    print(f"→ Revision code: {revision}")
                    # Pi 3B+ revisions: a020d3, a220d3, a02082
                    # Pi Zero W revisions: 9000c1, 902120
                    if revision in ['a020d3', 'a220d3', 'a02082']:
                        print("  → Pi 3B+ (by revision)")
                    elif revision in ['9000c1', '902120']:
                        print("  → Pi Zero W (by revision)")
                    break
    except:
        print("→ Revision check failed")

if __name__ == "__main__":
    main()