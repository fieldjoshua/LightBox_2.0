"""
Shimmer animation - creates a sparkling effect across the LED matrix
"""

import random
import math

def animate(pixels, config, frame):
    """Create shimmering sparkle effect"""
    
    # Base color from palette
    base_color = config.interpolate_palette(0.5)
    
    for i in range(config.LED_COUNT):
        # Create random shimmer pattern
        shimmer = random.random()
        
        # Add wave component for flowing effect
        wave = (math.sin(frame * 0.05 * config.SPEED + i * 0.1) + 1) / 2
        
        # Combine shimmer and wave
        brightness = (shimmer * 0.7 + wave * 0.3) * config.INTENSITY
        
        # Apply to base color
        r = int(base_color[0] * brightness * config.BRIGHTNESS)
        g = int(base_color[1] * brightness * config.BRIGHTNESS)
        b = int(base_color[2] * brightness * config.BRIGHTNESS)
        
        # Gamma correction
        r = int(255 * pow(r / 255, config.GAMMA))
        g = int(255 * pow(g / 255, config.GAMMA))
        b = int(255 * pow(b / 255, config.GAMMA))
        
        pixels[i] = (r, g, b)