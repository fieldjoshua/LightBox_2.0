#!/usr/bin/env python3
"""
Migration script to transition to the optimized LightBox implementation.
This script helps migrate settings and configurations from the old structure.
"""

import json
import os
import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def find_settings_files():
    """Find all settings.json files in the project."""
    settings_files = []
    
    # Common locations for settings files
    search_paths = [
        Path("."),
        Path("LightBox"),
        Path("LB_Interface/LightBox"),
        Path("LB_Interface/LB_Interface_work"),
    ]
    
    for base_path in search_paths:
        if base_path.exists():
            for settings_file in base_path.rglob("settings.json"):
                settings_files.append(settings_file)
    
    return settings_files


def merge_settings(settings_files):
    """Merge settings from multiple files, preferring newer/more complete ones."""
    merged = {}
    
    for settings_file in settings_files:
        try:
            with open(settings_file, 'r') as f:
                data = json.load(f)
                
            # Get file modification time
            mtime = os.path.getmtime(settings_file)
            
            logger.info(f"Found settings in {settings_file} (modified: {mtime})")
            
            # Merge with priority to newer files
            if not merged or mtime > merged.get('_mtime', 0):
                merged.update(data)
                merged['_mtime'] = mtime
                
        except Exception as e:
            logger.error(f"Error reading {settings_file}: {e}")
    
    # Remove internal metadata
    merged.pop('_mtime', None)
    
    return merged


def migrate_animations():
    """Copy animation scripts to the new location."""
    animation_sources = [
        Path("scripts"),
        Path("LightBox/scripts"),
        Path("LB_Interface/LightBox/scripts"),
    ]
    
    target_dir = Path("animations")
    target_dir.mkdir(exist_ok=True)
    
    copied = 0
    for source_dir in animation_sources:
        if source_dir.exists():
            for script in source_dir.glob("*.py"):
                if not script.name.startswith("_"):
                    target_file = target_dir / script.name
                    if not target_file.exists():
                        shutil.copy2(script, target_file)
                        logger.info(f"Copied animation: {script.name}")
                        copied += 1
    
    return copied


def create_systemd_service():
    """Create an updated systemd service file."""
    service_content = """[Unit]
Description=LightBox LED Matrix Controller (Optimized)
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/LightBox
ExecStart=/usr/bin/python3 /home/pi/LightBox/lightbox.py
Restart=always
RestartSec=10

# Performance optimizations
CPUSchedulingPolicy=fifo
CPUSchedulingPriority=80
Nice=-10

[Install]
WantedBy=multi-user.target
"""
    
    service_file = Path("lightbox-optimized.service")
    with open(service_file, 'w') as f:
        f.write(service_content)
    
    logger.info(f"Created {service_file}")
    logger.info("To install: sudo cp lightbox-optimized.service /etc/systemd/system/")
    logger.info("Then: sudo systemctl enable lightbox-optimized && sudo systemctl start lightbox-optimized")


def check_dependencies():
    """Check if required dependencies are installed."""
    required = {
        'adafruit-circuitpython-neopixel': 'WS2811 support',
        'flask': 'Web interface',
        'flask-socketio': 'Real-time updates',
        'psutil': 'Performance monitoring',
        'pillow': 'Image processing'
    }
    
    optional = {
        'rgbmatrix': 'HUB75 support (install with install_rgb_matrix.sh)',
        'numpy': 'Advanced animations',
        'eventlet': 'Production web server'
    }
    
    logger.info("\nChecking dependencies...")
    
    missing_required = []
    missing_optional = []
    
    for package, description in required.items():
        try:
            __import__(package.replace('-', '_'))
            logger.info(f"✓ {package} - {description}")
        except ImportError:
            missing_required.append(package)
            logger.warning(f"✗ {package} - {description}")
    
    for package, description in optional.items():
        try:
            __import__(package)
            logger.info(f"✓ {package} - {description}")
        except ImportError:
            missing_optional.append(package)
            logger.info(f"○ {package} - {description} (optional)")
    
    return missing_required, missing_optional


def main():
    """Run the migration process."""
    logger.info("=== LightBox Optimization Migration ===\n")
    
    # Check dependencies
    missing_req, missing_opt = check_dependencies()
    
    if missing_req:
        logger.error("\nMissing required dependencies!")
        logger.error(f"Install with: pip install {' '.join(missing_req)}")
        return 1
    
    # Find and merge settings
    logger.info("\nSearching for existing settings...")
    settings_files = find_settings_files()
    
    if settings_files:
        logger.info(f"Found {len(settings_files)} settings file(s)")
        merged_settings = merge_settings(settings_files)
        
        # Save merged settings
        output_file = Path("settings.json")
        with open(output_file, 'w') as f:
            json.dump(merged_settings, f, indent=2)
        
        logger.info(f"Saved merged settings to {output_file}")
    else:
        logger.warning("No existing settings found, using defaults")
    
    # Migrate animations
    logger.info("\nMigrating animation scripts...")
    anim_count = migrate_animations()
    logger.info(f"Migrated {anim_count} animation(s)")
    
    # Create systemd service
    logger.info("\nCreating systemd service file...")
    create_systemd_service()
    
    # Platform-specific recommendations
    logger.info("\n=== Platform-Specific Setup ===")
    
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            
        if 'BCM2835' in cpuinfo:
            logger.info("Detected: Raspberry Pi Zero W")
            logger.info("Recommended: Use lower FPS target (15-20)")
            logger.info("Edit settings.json and set 'target_fps': 20")
            
        elif 'BCM2837' in cpuinfo:
            logger.info("Detected: Raspberry Pi 3B+")
            logger.info("Recommended optimizations:")
            logger.info("1. Add 'isolcpus=3' to /boot/cmdline.txt")
            logger.info("2. Add 'gpu_mem=16' to /boot/config.txt")
            logger.info("3. For HUB75: Solder GPIO4-GPIO18 jumper")
            
        elif 'BCM2711' in cpuinfo:
            logger.info("Detected: Raspberry Pi 4")
            logger.info("Full performance available!")
            logger.info("Consider using HUB75 panels for best results")
            
    except:
        logger.info("Could not detect platform")
    
    # Final instructions
    logger.info("\n=== Migration Complete ===")
    logger.info("\nTo run the optimized version:")
    logger.info("  sudo python3 lightbox.py")
    logger.info("\nTo run in development mode:")
    logger.info("  python3 lightbox.py")
    logger.info("\nAccess web interface at: http://localhost:5001")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())