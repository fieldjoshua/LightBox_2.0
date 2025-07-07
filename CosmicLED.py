#!/usr/bin/env python3
"""
CosmicLED - Main animation engine for WS2811/NeoPixel LED matrix
Supports multiple animation programs with real-time parameter control
"""

import time
import json
import os
import sys
import threading
import importlib.util
from datetime import datetime
import board
import neopixel
from config import Config
from webgui.app import create_app

class CosmicLED:
    def __init__(self):
        self.config = Config()
        self.running = True
        self.current_program = "cosmic"
        self.programs = {}
        self.stats = {
            "fps": 0,
            "frame_count": 0,
            "uptime": 0,
            "current_program": self.current_program,
            "last_update": datetime.now().isoformat()
        }
        
        # Initialize LED strip
        self.pixels = neopixel.NeoPixel(
            board.D12,  # GPIO12
            self.config.LED_COUNT,
            brightness=self.config.BRIGHTNESS,
            auto_write=False,
            pixel_order=neopixel.GRB
        )
        
        # Load available programs
        self.load_programs()
        
        # Start stats writer thread
        self.stats_thread = threading.Thread(target=self.stats_writer, daemon=True)
        self.stats_thread.start()
        
    def load_programs(self):
        """Load all animation programs from scripts folder"""
        scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
        
        # Built-in cosmic animation
        self.programs['cosmic'] = self.cosmic_animation
        
        # Load external scripts
        if os.path.exists(scripts_dir):
            for filename in os.listdir(scripts_dir):
                if filename.endswith('.py') and not filename.startswith('__'):
                    program_name = filename[:-3]
                    try:
                        spec = importlib.util.spec_from_file_location(
                            program_name, 
                            os.path.join(scripts_dir, filename)
                        )
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        if hasattr(module, 'animate'):
                            self.programs[program_name] = module.animate
                            print(f"Loaded program: {program_name}")
                    except Exception as e:
                        print(f"Error loading {filename}: {e}")
    
    def cosmic_animation(self, pixels, config, frame):
        """Default cosmic animation with flowing colors"""
        import math
        
        for i in range(config.LED_COUNT):
            # Create flowing wave pattern
            hue = (frame * config.SPEED + i * 360 / config.LED_COUNT) % 360
            
            # Add some variation
            brightness_mod = (math.sin(frame * 0.01 + i * 0.1) + 1) / 2
            brightness = config.BRIGHTNESS * brightness_mod
            
            # Convert HSV to RGB
            rgb = self.hsv_to_rgb(hue / 360, 1.0, brightness)
            
            # Apply gamma correction
            rgb = tuple(int(self.gamma_correct(c, config.GAMMA)) for c in rgb)
            
            pixels[i] = rgb
            
    def hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB color space"""
        import colorsys
        rgb = colorsys.hsv_to_rgb(h, s, v)
        return tuple(int(c * 255) for c in rgb)
    
    def gamma_correct(self, value, gamma):
        """Apply gamma correction to color value"""
        return 255 * pow(value / 255, gamma)
    
    def stats_writer(self):
        """Write runtime stats to JSON file"""
        start_time = time.time()
        
        while self.running:
            self.stats["uptime"] = int(time.time() - start_time)
            self.stats["last_update"] = datetime.now().isoformat()
            
            try:
                with open('/tmp/cosmic_stats.json', 'w') as f:
                    json.dump(self.stats, f)
            except Exception as e:
                print(f"Error writing stats: {e}")
                
            time.sleep(1)
    
    def switch_program(self, program_name):
        """Switch to a different animation program"""
        if program_name in self.programs:
            self.current_program = program_name
            self.stats["current_program"] = program_name
            return True
        return False
    
    def update_config(self, new_config):
        """Update configuration parameters"""
        for key, value in new_config.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                
        # Update pixel brightness
        self.pixels.brightness = self.config.BRIGHTNESS
    
    def run(self):
        """Main animation loop"""
        frame = 0
        last_time = time.time()
        frame_times = []
        
        try:
            while self.running:
                frame_start = time.time()
                
                # Run current animation program
                if self.current_program in self.programs:
                    self.programs[self.current_program](
                        self.pixels, self.config, frame
                    )
                
                # Show the pixels
                self.pixels.show()
                
                # Calculate FPS
                frame_time = time.time() - frame_start
                frame_times.append(frame_time)
                
                if len(frame_times) > 30:
                    frame_times.pop(0)
                    
                if time.time() - last_time > 1:
                    avg_frame_time = sum(frame_times) / len(frame_times)
                    self.stats["fps"] = round(1 / avg_frame_time, 1) if avg_frame_time > 0 else 0
                    last_time = time.time()
                
                self.stats["frame_count"] = frame
                frame += 1
                
                # Frame rate limiting
                target_frame_time = 1 / 60  # 60 FPS target
                sleep_time = target_frame_time - frame_time
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        self.pixels.fill((0, 0, 0))
        self.pixels.show()
        self.pixels.deinit()

def main():
    # Check if running as root (required for GPIO)
    if os.geteuid() != 0:
        print("This script must be run with sudo for GPIO access")
        sys.exit(1)
    
    # Create LED controller
    controller = CosmicLED()
    
    # Start web GUI in separate thread
    app, socketio = create_app(controller)
    web_thread = threading.Thread(
        target=lambda: socketio.run(app, host='0.0.0.0', port=5000, debug=False),
        daemon=True
    )
    web_thread.start()
    
    print("CosmicLED started!")
    print("Web GUI available at http://localhost:5000")
    
    # Run main animation loop
    controller.run()

if __name__ == "__main__":
    main()