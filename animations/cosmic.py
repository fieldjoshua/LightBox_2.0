"""
Cosmic animation - flowing colors with optimized performance.
This is the default animation that creates smooth color flows.
"""

import math
from typing import List, Tuple


def animate(pixels: List[Tuple[int, int, int]], config, frame: int):
    """
    Cosmic animation with flowing colors.
    
    Args:
        pixels: List of RGB tuples to modify
        config: Configuration object with settings and optimizations
        frame: Current frame number
    """
    # Get configuration values
    speed = config.get("speed", 1.0)
    brightness = config.get("brightness", 0.8)
    
    # Get dimensions based on matrix type
    if config.get("matrix_type") == "hub75":
        width = config.get("hub75.cols", 64)
        height = config.get("hub75.rows", 64)
    else:
        width = config.get("ws2811.width", 10)
        height = config.get("ws2811.height", 10)
    
    # Animation parameters
    wave_speed = 0.05 * speed
    color_speed = 0.02 * speed
    wave_scale = 0.3
    
    # Current time for animation
    t = frame * wave_speed
    
    # Generate flowing pattern
    for y in range(height):
        for x in range(width):
            # Calculate wave offset
            wave_x = math.sin(t + x * wave_scale) * 0.5 + 0.5
            wave_y = math.cos(t + y * wave_scale) * 0.5 + 0.5
            
            # Combine waves for more complex pattern
            combined = (wave_x + wave_y) * 0.5
            
            # Color cycling
            hue = (combined + frame * color_speed) % 1.0
            
            # Convert HSV to RGB using config's optimized method
            r, g, b = config.hsv_to_rgb(hue, 1.0, brightness)
            
            # Set pixel using config's mapping
            idx = config.xy_to_index(x, y)
            if 0 <= idx < len(pixels):
                pixels[idx] = (r, g, b)


# Animation parameters that can be configured
PARAMS = {
    "wave_speed": {
        "type": "float",
        "min": 0.01,
        "max": 0.5,
        "default": 0.05,
        "description": "Speed of wave movement"
    },
    "color_speed": {
        "type": "float",
        "min": 0.001,
        "max": 0.1,
        "default": 0.02,
        "description": "Speed of color cycling"
    },
    "wave_scale": {
        "type": "float",
        "min": 0.1,
        "max": 1.0,
        "default": 0.3,
        "description": "Scale of wave pattern"
    }
}