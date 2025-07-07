#!/bin/bash

# LightBox Setup Script for Raspberry Pi
# This script sets up the Python environment and installs dependencies

echo "🎨 LightBox Setup Script"
echo "========================"

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    echo "Some features may not work correctly on other platforms"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
    echo "❌ Python 3.11+ is required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install adafruit-blinka
pip install adafruit-circuitpython-neopixel
pip install RPi.GPIO
pip install flask
pip install pillow
pip install adafruit-circuitpython-ssd1306

# Create required directories
echo "Creating directories..."
mkdir -p scripts
mkdir -p presets
mkdir -p webgui/templates
mkdir -p webgui/static

# Create example preset
echo "Creating example preset..."
cat > presets/default.json << EOF
{
  "name": "default",
  "brightness": 0.5,
  "gamma": 2.2,
  "speed": 1.0,
  "scale": 1.0,
  "intensity": 1.0,
  "current_palette": "rainbow",
  "led_count": 100
}
EOF

# Make main script executable
chmod +x CosmicLED.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run LightBox:"
echo "  sudo ./venv/bin/python3 CosmicLED.py"
echo ""
echo "Web interface will be available at:"
echo "  http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "For auto-start on boot, run:"
echo "  sudo cp lightbox.service /etc/systemd/system/"
echo "  sudo systemctl enable lightbox"
echo "  sudo systemctl start lightbox"