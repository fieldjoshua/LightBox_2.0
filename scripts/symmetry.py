"""
Symmetry animation - creates mirrored patterns on the LED matrix
"""

import math

def animate(pixels, config, frame):
    """Create symmetrical patterns"""
    
    center_x = config.MATRIX_WIDTH / 2
    center_y = config.MATRIX_HEIGHT / 2
    
    for y in range(config.MATRIX_HEIGHT):
        for x in range(config.MATRIX_WIDTH):
            # Get the correct pixel index for serpentine wiring
            i = config.xy_to_index(x, y)
            if i is None:
                continue
            
            # Calculate distance from center
            dx = abs(x - center_x + 0.5)
            dy = abs(y - center_y + 0.5)
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Create radial wave pattern
            wave = math.sin(distance * config.SCALE - frame * 0.05 * config.SPEED)
            
            # Map wave to palette position
            palette_pos = (wave + 1) / 2
            color = config.interpolate_palette(palette_pos)
            
            # Apply brightness and intensity
            r = int(color[0] * config.BRIGHTNESS * config.INTENSITY)
            g = int(color[1] * config.BRIGHTNESS * config.INTENSITY)
            b = int(color[2] * config.BRIGHTNESS * config.INTENSITY)
            
            # Gamma correction
            r = int(255 * pow(r / 255, config.GAMMA))
            g = int(255 * pow(g / 255, config.GAMMA))
            b = int(255 * pow(b / 255, config.GAMMA))
            
            pixels[i] = (r, g, b)