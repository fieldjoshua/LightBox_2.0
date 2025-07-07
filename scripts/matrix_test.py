"""
Matrix test animation - shows the serpentine wiring pattern
Useful for verifying correct pixel mapping
"""

import math

def animate(pixels, config, frame):
    """Test pattern to verify serpentine wiring"""
    
    # Different test modes based on frame count
    mode = (frame // 300) % 4  # Change mode every 5 seconds at 60fps
    
    if mode == 0:
        # Horizontal sweep - shows how rows are wired
        sweep_pos = (frame % config.MATRIX_WIDTH)
        
        for y in range(config.MATRIX_HEIGHT):
            for x in range(config.MATRIX_WIDTH):
                i = config.xy_to_index(x, y)
                if i is None:
                    continue
                
                if x == sweep_pos:
                    # Bright white for current column
                    pixels[i] = (255, 255, 255)
                else:
                    # Dim color showing row number
                    row_color = int(20 + (y * 20))
                    pixels[i] = (row_color, 0, 0)
    
    elif mode == 1:
        # Vertical sweep
        sweep_pos = (frame % config.MATRIX_HEIGHT)
        
        for y in range(config.MATRIX_HEIGHT):
            for x in range(config.MATRIX_WIDTH):
                i = config.xy_to_index(x, y)
                if i is None:
                    continue
                
                if y == sweep_pos:
                    # Bright white for current row
                    pixels[i] = (255, 255, 255)
                else:
                    # Dim color showing column number
                    col_color = int(20 + (x * 20))
                    pixels[i] = (0, col_color, 0)
    
    elif mode == 2:
        # Corner indicators - helps identify orientation
        for y in range(config.MATRIX_HEIGHT):
            for x in range(config.MATRIX_WIDTH):
                i = config.xy_to_index(x, y)
                if i is None:
                    continue
                
                # Top-left: Red
                if x == 0 and y == 0:
                    pixels[i] = (255, 0, 0)
                # Top-right: Green
                elif x == config.MATRIX_WIDTH - 1 and y == 0:
                    pixels[i] = (0, 255, 0)
                # Bottom-left: Blue
                elif x == 0 and y == config.MATRIX_HEIGHT - 1:
                    pixels[i] = (0, 0, 255)
                # Bottom-right: White
                elif x == config.MATRIX_WIDTH - 1 and y == config.MATRIX_HEIGHT - 1:
                    pixels[i] = (255, 255, 255)
                else:
                    # Gradient based on position
                    r = int((x / config.MATRIX_WIDTH) * 50)
                    g = int((y / config.MATRIX_HEIGHT) * 50)
                    pixels[i] = (r, g, 30)
    
    else:
        # Sequential fill - shows physical LED order
        fill_count = frame % config.LED_COUNT
        
        for i in range(config.LED_COUNT):
            if i <= fill_count:
                # Rainbow color based on position
                hue = (i / config.LED_COUNT) * 360
                color = config.interpolate_palette(hue / 360)
                pixels[i] = color
            else:
                pixels[i] = (0, 0, 0)
    
    # Apply brightness and gamma
    for i in range(config.LED_COUNT):
        r, g, b = pixels[i]
        r = int(r * config.BRIGHTNESS)
        g = int(g * config.BRIGHTNESS)
        b = int(b * config.BRIGHTNESS)
        
        # Gamma correction
        r = int(255 * pow(r / 255, config.GAMMA))
        g = int(255 * pow(g / 255, config.GAMMA))
        b = int(255 * pow(b / 255, config.GAMMA))
        
        pixels[i] = (r, g, b)