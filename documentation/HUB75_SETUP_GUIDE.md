# HUB75 LED Matrix Setup Guide for LightBox

## Overview

This guide covers setting up HUB75 64x64 RGB LED matrix panels with the LightBox system on Raspberry Pi. HUB75 panels offer higher resolution and better performance compared to WS2811 strips, making them ideal for detailed animations and displays.

## Hardware Requirements

### Required Components

1. **Raspberry Pi** (Recommended: Pi 3B+ or Pi 4)
   - Pi Zero W is compatible but may have performance limitations
   - 2GB+ RAM recommended for smooth animations

2. **HUB75 LED Panel**
   - Supported sizes: 32x32, 64x64, 64x32
   - Common pitch: P2, P2.5, P3, P4, P5
   - Indoor or outdoor panels supported

3. **RGB Matrix HAT/Bonnet**
   - Adafruit RGB Matrix HAT (recommended)
   - Adafruit RGB Matrix Bonnet (for Pi Zero)
   - Or compatible HAT with HUB75 connectors

4. **Power Supply**
   - 5V switching power supply
   - Current calculation: (Width × Height × 0.06A) × Safety Factor
   - For 64x64 panel: 5V 15-20A minimum
   - Use thick gauge wires for power connections

5. **Cables and Connectors**
   - HUB75 ribbon cable (usually included with panel)
   - Power terminals or barrel jack adapter
   - Optional: GPIO4-GPIO18 jumper wire for hardware PWM

## Software Installation

### 1. Install RGB Matrix Library

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y git python3-dev python3-pillow

# Clone and build the RGB matrix library
cd ~
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
cd rpi-rgb-led-matrix
make build-python PYTHON=$(which python3)
sudo make install-python PYTHON=$(which python3)

# Alternative: Use Adafruit's installer script
curl https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/main/rgb-matrix.sh > rgb-matrix.sh
sudo bash rgb-matrix.sh
```

### 2. Configure Raspberry Pi

Edit `/boot/config.txt`:

```bash
sudo nano /boot/config.txt
```

Add or modify these lines:

```
# Disable audio (conflicts with PWM)
dtparam=audio=off

# Reduce GPU memory split
gpu_mem=16

# Optional: Disable onboard Bluetooth (Pi 3/4)
dtoverlay=disable-bt

# Optional: Increase SPI buffer
dtparam=spi=on
```

### 3. Performance Optimizations

For best performance, add to `/boot/cmdline.txt`:

```
isolcpus=3
```

This isolates CPU core 3 for the LED update thread.

## Hardware Setup

### 1. Mount the RGB Matrix HAT

1. Power off the Raspberry Pi
2. Align the HAT with the GPIO pins
3. Press down firmly to seat the connector
4. Secure with standoffs if provided

### 2. Connect the LED Panel

1. Locate the input connector on the panel (usually marked "IN")
2. Connect the ribbon cable from HAT's output to panel's input
3. Ensure the red stripe aligns with the pin 1 marker

### 3. Wire Power Connections

**IMPORTANT**: Never power the panel through the HAT alone!

1. Connect 5V power supply positive to panel's VCC/+5V terminals
2. Connect power supply negative to panel's GND terminals
3. Connect a ground wire between Pi and panel for common ground

### 4. Hardware PWM Modification (Optional but Recommended)

For flicker-free operation, solder a jumper between GPIO4 and GPIO18:

1. Locate GPIO4 (pin 7) and GPIO18 (pin 12) on the HAT
2. Solder a small wire between these pins
3. This enables hardware PWM mode

## LightBox Configuration

### 1. Update Configuration File

Edit `settings.json` to enable HUB75:

```json
{
  "matrix_type": "HUB75",
  "matrix_width": 64,
  "matrix_height": 64,
  "brightness": 0.75,
  "fps": 30,
  "hub75_settings": {
    "rows": 64,
    "cols": 64,
    "chain_length": 1,
    "parallel": 1,
    "pwm_bits": 11,
    "gpio_slowdown": 4,
    "hardware_mapping": "adafruit-hat",
    "disable_hardware_pulsing": false
  }
}
```

### 2. Configuration Parameters

#### Display Settings
- `rows`: Physical rows per panel (32 or 64)
- `cols`: Physical columns per panel (32 or 64)
- `chain_length`: Number of panels chained together
- `parallel`: Number of parallel chains (1 for single panel)

#### Performance Tuning
- `pwm_bits`: Color depth (1-11, higher = better color, lower = less flicker)
- `gpio_slowdown`: Timing adjustment (0-5, increase if you see glitches)
- `limit_refresh`: Maximum refresh rate in Hz (0 = unlimited)
- `pwm_lsb_nanoseconds`: Fine-tune PWM timing (default: 130)

#### Hardware Mapping
- `"regular"`: Generic pinout
- `"adafruit-hat"`: Adafruit RGB Matrix HAT
- `"adafruit-hat-pwm"`: Adafruit HAT with PWM modification

## Running LightBox with HUB75

### 1. Test the Setup

```bash
cd ~/LightBox
sudo python3 LightBox/scripts/matrix_test.py
```

This should display a test pattern on your panel.

### 2. Start LightBox

```bash
sudo python3 LightBox/LB_Interface/LightBox/Conductor.py
```

### 3. Access Web Interface

Open browser to: `http://<pi-ip>:5001`

- Select "HUB75 Panel" in the Matrix Type selector
- Adjust performance settings as needed
- Monitor FPS in the performance panel

## Troubleshooting

### Common Issues and Solutions

#### 1. Panel Shows Nothing
- Check power connections (panel needs separate 5V supply)
- Verify ribbon cable orientation
- Ensure you're running with `sudo`
- Check if audio is disabled in `/boot/config.txt`

#### 2. Flickering or Glitches
- Increase `gpio_slowdown` value (try 2, 3, 4, or 5)
- Reduce `pwm_bits` to 7 or 9
- Enable hardware PWM with GPIO4-GPIO18 jumper
- Try different `hardware_mapping` option

#### 3. Wrong Colors
- Check `led_rgb_sequence` setting (try "RGB", "RBG", "GRB", etc.)
- Some panels need `inverse_colors: true`

#### 4. Poor Performance
- Ensure CPU isolation is enabled (`isolcpus=3`)
- Reduce panel brightness
- Lower the FPS target
- Use Pi 3B+ or Pi 4 instead of Pi Zero

#### 5. Partial Display
- Verify `rows` and `cols` match your panel
- Check `multiplexing` setting for your panel type
- Try different `row_address_type` values (0-4)

### Performance Optimization Tips

1. **Hardware PWM**: Always use the GPIO4-GPIO18 jumper for best results
2. **CPU Isolation**: Add `isolcpus=3` to `/boot/cmdline.txt`
3. **Process Priority**: Run with `sudo nice -n -20` for highest priority
4. **Disable Services**: Stop unnecessary services to free resources

```bash
sudo systemctl stop bluetooth
sudo systemctl stop avahi-daemon
```

## Advanced Configuration

### Multiple Panel Setup

For multiple panels in a chain:

```json
{
  "hub75_settings": {
    "rows": 64,
    "cols": 64,
    "chain_length": 2,
    "parallel": 1,
    "pixel_mapper": "U-mapper"
  }
}
```

### Custom Panel Types

For panels with special requirements:

```json
{
  "hub75_settings": {
    "panel_type": "FM6126A",
    "multiplexing": 1,
    "row_address_type": 2
  }
}
```

### Rotation and Mapping

To rotate or remap the display:

```json
{
  "hub75_settings": {
    "pixel_mapper": "Rotate:90"
  }
}
```

## Safety Considerations

1. **Power Requirements**
   - Use appropriate gauge wire for current capacity
   - Include inline fuses for safety
   - Ensure proper ventilation for power supply

2. **Heat Management**
   - Panels can get warm during operation
   - Ensure adequate airflow
   - Monitor temperature in enclosed installations

3. **Eye Safety**
   - These panels are bright!
   - Avoid staring directly at full brightness
   - Consider diffusion material for comfort

## Next Steps

1. Try different animation programs optimized for HUB75
2. Adjust performance settings for your specific setup
3. Create custom animations using the 64x64 resolution
4. Experiment with chaining multiple panels

## Additional Resources

- [RGB LED Matrix Library Documentation](https://github.com/hzeller/rpi-rgb-led-matrix)
- [Adafruit RGB Matrix HAT Guide](https://learn.adafruit.com/adafruit-rgb-matrix-hat-for-raspberry-pi)
- [HUB75 Panel Specifications](https://www.sparkfun.com/sparkx/blog/2650)

## Support

For LightBox-specific HUB75 issues:
1. Check the troubleshooting section above
2. Review logs in `logs/hardware.log`
3. Visit the LightBox GitHub repository

Remember: HUB75 panels require more power and processing than WS2811 strips, but offer superior resolution and refresh rates when properly configured!