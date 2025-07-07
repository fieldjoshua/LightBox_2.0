"""
Waves animation - creates flowing wave patterns across the LED matrix
"""

import math

def animate(pixels, config, frame):
    """Create flowing wave patterns"""
    
    for y in range(config.MATRIX_HEIGHT):
        for x in range(config.MATRIX_WIDTH):
            # Get the correct pixel index for serpentine wiring
            i = config.xy_to_index(x, y)
            if i is None:
                continue
            
            # Create multiple wave components
            wave1 = math.sin(x * 0.3 * config.SCALE + frame * 0.03 * config.SPEED)
            wave2 = math.sin(y * 0.3 * config.SCALE + frame * 0.04 * config.SPEED)
            wave3 = math.sin((x + y) * 0.2 * config.SCALE + frame * 0.02 * config.SPEED)
            
            # Combine waves
            combined = (wave1 + wave2 + wave3) / 3
            
            # Map to palette
            palette_pos = (combined + 1) / 2
            color = config.interpolate_palette(palette_pos)
            
            # Apply settings
            r = int(color[0] * config.BRIGHTNESS * config.INTENSITY)
            g = int(color[1] * config.BRIGHTNESS * config.INTENSITY)
            b = int(color[2] * config.BRIGHTNESS * config.INTENSITY)
            
            # Gamma correction
            r = int(255 * pow(r / 255, config.GAMMA))
            g = int(255 * pow(g / 255, config.GAMMA))
            b = int(255 * pow(b / 255, config.GAMMA))
            
            pixels[i] = (r, g, b)