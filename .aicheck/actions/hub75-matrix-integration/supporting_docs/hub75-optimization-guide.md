# HUB75 64x64 Matrix Optimization Guide

## Libraries and Tools for 64×64 HUB75 Matrices

A popular choice is Henner Zeller's rpi-rgb-led-matrix library, which provides C++ control and Python bindings for HUB75 panels. It supports Pi 3B+ (and earlier Pi versions) with up to three chains of 64×64 panels. Adafruit's installer script even pulls this library for the RGB Matrix HAT setup. Once installed, you can use Python scripts (e.g. from bindings/python/samples) to draw graphics or text. For example, Adafruit's tutorial shows running a scrolling text demo via:

```bash
sudo python runtext.py -m=adafruit-hat --led-rows=32 --led-cols=64 --led-slowdown-gpio=4
```

The library supports double-buffering (using CreateFrameCanvas() and SwapOnVSync()) for smooth updates. It also includes C++ tools (led-image-viewer, demo, etc.) and a Python module (rgbmatrix) installed by the HAT script.

Another Python option is Pixil LED Matrix – a custom scripting framework for 64×64 matrices. Pixil comes with 75+ built-in animations (bouncing balls, fire, etc.) and its own command-line interpreter. After installing via pip install -r requirements.txt, you simply run:

```bash
sudo python Pixil.py scripts/3D_perspective -q
```

(or any other script in scripts/). This framework abstracts away low-level details and uses optimized C++ under the hood, yielding smooth visuals on a Raspberry Pi.

Beyond these, Adafruit's HAT can also be driven by the CircuitPython rgbmatrix library (on e.g. Pi Pico or Matrix Portal), but on the Pi it's more common to use the above or similar libraries. Adafruit's older fork of the matrix library exists, but they now recommend Zeller's code for new projects.

## Example Animations and Code

Popular smooth effects include scrolling text, bouncing shapes, wave or particle simulations, etc. For instance, the Python sample runtext.py (part of the bindings) scrolls a line of text across the display using double-buffering. A typical Python snippet might look like:

```python
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
# Configure a single 64×64 matrix on the Adafruit HAT
options = RGBMatrixOptions()
options.rows = 64
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'
matrix = RGBMatrix(options=options)
canvas = matrix.CreateFrameCanvas()
font = graphics.Font()
font.LoadFont("../../../fonts/7x13.bdf")
color = graphics.Color(255, 255, 0)
text = "Hello, world!"
pos = canvas.width
while True:
    canvas.Clear()
    length = graphics.DrawText(canvas, font, pos, 32, color, text)
    pos -= 1
    if pos + length < 0:
        pos = canvas.width
    canvas = matrix.SwapOnVSync(canvas)  # double-buffer update
    time.sleep(0.03)
```

This uses the graphics module and SwapOnVSync for flicker-free animation. Adafruit's guides also show examples like a "Times Square" clock or web-controlled sign using similar code. The Pixil framework scripts (e.g. 3D_perspective, starfield, particle effects) are Python and can be used directly to demonstrate complex animations (see Pixil's scripts/ directory).

## Setup Guides (Pi 3B+ + Adafruit HAT)

Adafruit provides a detailed learning guide for the RGB Matrix HAT (Pi 3B+ compatible). Key steps include physically mounting the HAT and panel, then installing software via their installer script. For example, the guide instructs:

```bash
curl https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/main/rgb-matrix.sh > rgb-matrix.sh
sudo bash rgb-matrix.sh
```

This fetches and builds Zeller's RGB matrix library and its Python bindings tailored for the HAT. You can choose "convenience" mode for Adafruit HAT support; it sets --led-gpio-mapping=adafruit-hat. After installation, verify with examples (the guide suggests running demo and Python samples) to ensure the matrix lights up. Adafruit also notes that you should set gpu_mem=16 in /boot/config.txt (their installer does this) and can run on Raspbian/RasPi OS Lite for best performance.

## Performance Tweaks for Smooth Animation

### Double-buffering
Always draw on an off-screen canvas and use SwapOnVSync() (or PIL Image offscreen) to update the panel. This avoids tearing and is explicitly recommended for smooth playback.

### Hardware PWM hack
Solder a jumper between GPIO4 and GPIO18 on the HAT/Bonnet, enabling "hardware pulses" mode. This converts the HAT's software PWM into hardware pulses, eliminating the random horizontal line artifacts seen in Python mode. Adafruit and Zeller both stress this trick to reduce flicker.

### CPU Isolation
On a multi-core Pi (e.g. Pi 3B+), dedicate one core to the matrix update by using the boot option isolcpus=3. Zeller notes the Pi 3's four cores can give one core fully to the display thread, improving refresh stability. (The Pi Zero's single core is ~10× slower, so Pi 3 is strongly recommended for heavy animations.)

### Compile-time frame fix
Rebuilding the library with FIXED_FRAME_MICROSECONDS (or using the newer --led-limit-refresh runtime flag) forces a fixed refresh period to suppress flicker. This can stabilize animations under load but may reduce overall FPS.

### Other GPIO flags
Some Python demos use --led-slowdown-gpio (like 4 for the default Pi frequency) to fine-tune timing. Also set --led-pwm-bits (e.g. 11) and --led-pwm-lsb-nanoseconds for brightness/colour depth. These are documented in the rpi-rgb-led-matrix README and examples (the Adafruit guide illustrates using --led-slowdown-gpio=4 on a 3B+).

## Performance Results

In practice, these tweaks yield very smooth 30–150 Hz animations on a 64×64 panel. Zeller reports that with double-buffering and PWM fix, a Pi 3B+ can achieve ~130 Hz refresh running Python loops. For maximum speed or complex scenes, using the C++ API or CLI tools (led-image-viewer, content-streamer, etc.) can help – but Python on a Pi 3B+ is often "good enough" for striking effects.

## Sources

Established libraries and guides were used, including Henner Zeller's rpi-rgb-led-matrix (with Python bindings), Adafruit's RGB Matrix HAT tutorial, and the Pixil LED Matrix framework. Performance notes come from the library's author and forums. These cover compatibility with the Pi 3B+ + Adafruit HAT setup and offer example code usage for smooth animations.