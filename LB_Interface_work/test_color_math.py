#!/usr/bin/env python3
"""Test the color calculations before deploying"""

import math

# Test the color calculation
frame = 0
errors = []

for frame in range(100):
    for x in range(0, 64, 10):  # Sample some pixels
        for y in range(0, 64, 10):
            hue = ((x + y) / 128.0 + math.sin(frame * 0.01) * 0.2) * 6
            
            # Original broken code
            try:
                if hue < 1: r, g, b = 1, hue, 0
                elif hue < 2: r, g, b = 2-hue, 1, 0
                elif hue < 3: r, g, b = 0, 1, hue-2
                elif hue < 4: r, g, b = 0, 4-hue, 1
                elif hue < 5: r, g, b = hue-4, 0, 1
                else: r, g, b = 1, 0, 6-hue
                
                # Check for negative values
                if r < 0 or g < 0 or b < 0:
                    errors.append(f"Negative at frame {frame}, x={x}, y={y}: r={r}, g={g}, b={b}, hue={hue}")
                
                # Check for values > 1
                if r > 1 or g > 1 or b > 1:
                    errors.append(f"Too large at frame {frame}, x={x}, y={y}: r={r}, g={g}, b={b}, hue={hue}")
                    
            except Exception as e:
                errors.append(f"Error at frame {frame}, x={x}, y={y}: {e}")

print(f"Found {len(errors)} errors")
if errors:
    for err in errors[:10]:  # Show first 10
        print(err)

print("\n--- Testing fixed version ---")

# Fixed version
def hsv_to_rgb(h, s, v):
    """Convert HSV to RGB (h in degrees 0-360)"""
    h = h % 360
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    
    return int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)

# Test fixed version
for frame in range(10):
    x, y = 32, 32  # Center pixel
    hue = ((x + y) / 128.0 + math.sin(frame * 0.01) * 0.2) * 360
    r, g, b = hsv_to_rgb(hue, 1.0, 1.0)
    print(f"Frame {frame}: RGB = ({r}, {g}, {b})")