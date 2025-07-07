"""
Parametric Waves - Advanced wave animation with configurable parameters
Demonstrates the program parameter system
"""

# PARAM: wave_count|int|3|1|8|Number of simultaneous wave patterns
# PARAM: wave_amplitude|float|1.0|0.1|3.0|Wave amplitude multiplier
# PARAM: phase_shift|float|0.5|0.0|2.0|Phase shift between waves
# PARAM: color_shift|float|1.0|0.1|5.0|Speed of color cycling
# PARAM: interference|float|0.3|0.0|1.0|Wave interference strength

import math

def animate(pixels, config, frame):
    """Create parametric wave patterns with configurable parameters"""
    
    # Default parameter values (used if parameters not set)
    wave_count = getattr(config, 'wave_count', 3)
    wave_amplitude = getattr(config, 'wave_amplitude', 1.0)
    phase_shift = getattr(config, 'phase_shift', 0.5)
    color_shift = getattr(config, 'color_shift', 1.0)
    interference = getattr(config, 'interference', 0.3)
    
    for y in range(config.MATRIX_HEIGHT):
        for x in range(config.MATRIX_WIDTH):
            i = config.xy_to_index(x, y)
            if i is None:
                continue
            
            # Calculate multiple wave components
            wave_sum = 0
            for w in range(int(wave_count)):
                # Different wave patterns
                wave_freq = 0.2 + (w * 0.1)
                phase = w * phase_shift * math.pi
                
                # Horizontal wave
                h_wave = math.sin(x * wave_freq * config.SCALE + frame * 0.02 * config.SPEED + phase)
                
                # Vertical wave
                v_wave = math.sin(y * wave_freq * config.SCALE + frame * 0.03 * config.SPEED + phase)
                
                # Diagonal wave
                d_wave = math.sin((x + y) * wave_freq * 0.7 * config.SCALE + frame * 0.025 * config.SPEED + phase)
                
                # Combine with interference
                wave_component = (h_wave + v_wave + d_wave * interference) / (2 + interference)
                wave_sum += wave_component * wave_amplitude
            
            # Normalize the combined wave
            combined_wave = wave_sum / wave_count
            
            # Add time-based color shifting
            color_time = frame * 0.01 * color_shift
            hue_offset = math.sin(color_time) * 0.3
            
            # Map to palette with color shifting
            palette_pos = (combined_wave + 1) / 2 + hue_offset
            palette_pos = max(0, min(1, palette_pos))  # Clamp to [0,1]
            
            color = config.interpolate_palette(palette_pos)
            
            # Apply brightness and intensity
            r = int(color[0] * config.BRIGHTNESS * config.INTENSITY)
            g = int(color[1] * config.BRIGHTNESS * config.INTENSITY)
            b = int(color[2] * config.BRIGHTNESS * config.INTENSITY)
            
            # Gamma correction
            r = int(255 * pow(max(0, min(255, r)) / 255, config.GAMMA))
            g = int(255 * pow(max(0, min(255, g)) / 255, config.GAMMA))
            b = int(255 * pow(max(0, min(255, b)) / 255, config.GAMMA))
            
            pixels[i] = (r, g, b)