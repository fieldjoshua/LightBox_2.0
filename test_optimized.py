#!/usr/bin/env python3
"""
Test script for validating the optimized LightBox implementation.
Runs in simulation mode to verify core functionality without hardware.
"""

import sys
import time
import json
import traceback
from pathlib import Path
import subprocess
import threading
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
from typing import Dict, List, Tuple, Any

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class OptimizedLightBoxTester:
    def __init__(self):
        self.results = []
        self.conductor_process = None
        self.test_start_time = time.time()
        
    def log(self, message: str, status: str = "INFO"):
        """Log a message with color coding."""
        colors = {
            "PASS": GREEN,
            "FAIL": RED,
            "WARN": YELLOW,
            "INFO": BLUE
        }
        color = colors.get(status, RESET)
        print(f"{color}[{status}] {message}{RESET}")
        self.results.append({"message": message, "status": status, "time": time.time()})
    
    def test_imports(self) -> bool:
        """Test that all core modules can be imported."""
        self.log("Testing module imports...", "INFO")
        
        modules_to_test = [
            ("core.config", "Configuration system"),
            ("core.conductor", "Main conductor"),
            ("core.performance", "Performance monitoring"),
            ("drivers.matrix_driver", "Matrix driver base"),
            ("drivers.ws2811_driver", "WS2811 driver"),
            ("drivers.hub75_driver", "HUB75 driver"),
            ("web.app", "Web interface"),
            ("utils.color_utils", "Color utilities"),
            ("utils.frame_utils", "Frame utilities")
        ]
        
        all_passed = True
        for module_name, description in modules_to_test:
            try:
                module = __import__(module_name, fromlist=[''])
                self.log(f"✓ {description} ({module_name})", "PASS")
            except ImportError as e:
                self.log(f"✗ {description} ({module_name}): {e}", "FAIL")
                all_passed = False
            except Exception as e:
                self.log(f"✗ {description} ({module_name}): Unexpected error: {e}", "FAIL")
                all_passed = False
        
        return all_passed
    
    def test_configuration(self) -> bool:
        """Test configuration loading and optimization features."""
        self.log("Testing configuration system...", "INFO")
        
        try:
            from core.config import ConfigManager
            config = ConfigManager()
            
            # Test platform detection
            platform = config.platform
            self.log(f"✓ Platform detected: {platform}", "PASS")
            
            # Test optimization features
            tests = [
                ("Gamma table", hasattr(config, '_gamma_table') and len(config._gamma_table) == 256),
                ("Serpentine map", hasattr(config, '_serpentine_map')),
                ("HSV to RGB function", hasattr(config, 'hsv_to_rgb')),
                ("Platform optimizations", config.get('platform_optimized', False))
            ]
            
            all_passed = True
            for test_name, condition in tests:
                if condition:
                    self.log(f"✓ {test_name} initialized", "PASS")
                else:
                    self.log(f"✗ {test_name} not initialized", "FAIL")
                    all_passed = False
            
            # Test coordinate mapping
            test_coords = [(0, 0), (9, 9), (5, 5)]
            for x, y in test_coords:
                idx = config.xy_to_index(x, y)
                if 0 <= idx < 100:
                    self.log(f"✓ Coordinate mapping ({x},{y}) -> {idx}", "PASS")
                else:
                    self.log(f"✗ Invalid coordinate mapping ({x},{y}) -> {idx}", "FAIL")
                    all_passed = False
            
            # Test color conversion
            test_hsv = (0.5, 1.0, 1.0)  # Cyan
            rgb = config.hsv_to_rgb(*test_hsv)
            if isinstance(rgb, tuple) and len(rgb) == 3:
                self.log(f"✓ HSV to RGB conversion: {test_hsv} -> {rgb}", "PASS")
            else:
                self.log(f"✗ HSV to RGB conversion failed", "FAIL")
                all_passed = False
            
            return all_passed
            
        except Exception as e:
            self.log(f"✗ Configuration test failed: {e}", "FAIL")
            traceback.print_exc()
            return False
    
    def test_drivers(self) -> bool:
        """Test driver initialization in simulation mode."""
        self.log("Testing hardware drivers...", "INFO")
        
        try:
            from core.config import ConfigManager
            from drivers.ws2811_driver import WS2811Driver
            from drivers.hub75_driver import HUB75Driver
            
            config = ConfigManager()
            all_passed = True
            
            # Test WS2811 driver
            try:
                ws_driver = WS2811Driver(config)
                pixels = [(0, 0, 0)] * 100
                ws_driver.update(pixels)
                self.log("✓ WS2811 driver initialized (simulation mode)", "PASS")
            except Exception as e:
                self.log(f"✗ WS2811 driver failed: {e}", "FAIL")
                all_passed = False
            
            # Test HUB75 driver
            try:
                hub_driver = HUB75Driver(config)
                self.log("✓ HUB75 driver initialized (simulation mode)", "PASS")
                
                # Check optimization detection
                if hasattr(hub_driver, 'hardware_pwm_available'):
                    self.log(f"  Hardware PWM: {hub_driver.hardware_pwm_available}", "INFO")
                if hasattr(hub_driver, 'cpu_isolated'):
                    self.log(f"  CPU isolation: {hub_driver.cpu_isolated}", "INFO")
                    
            except Exception as e:
                if "rgbmatrix" in str(e):
                    self.log("⚠ HUB75 driver requires rgbmatrix library (expected in simulation)", "WARN")
                else:
                    self.log(f"✗ HUB75 driver failed: {e}", "FAIL")
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            self.log(f"✗ Driver test failed: {e}", "FAIL")
            traceback.print_exc()
            return False
    
    def test_animations(self) -> bool:
        """Test animation loading and execution."""
        self.log("Testing animation system...", "INFO")
        
        try:
            from core.config import ConfigManager
            from pathlib import Path
            import importlib.util
            
            config = ConfigManager()
            animations_dir = Path("animations")
            
            if not animations_dir.exists():
                self.log("✗ Animations directory not found", "FAIL")
                return False
            
            animation_files = list(animations_dir.glob("*.py"))
            if not animation_files:
                self.log("⚠ No animation files found", "WARN")
                return True
            
            all_passed = True
            pixels = [(0, 0, 0)] * 100
            
            for anim_file in animation_files[:3]:  # Test first 3 animations
                # Skip __init__.py
                if anim_file.name == '__init__.py':
                    continue
                    
                try:
                    # Load animation module
                    spec = importlib.util.spec_from_file_location(
                        anim_file.stem, anim_file
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Test animate function
                    if hasattr(module, 'animate'):
                        # Run a few frames
                        for frame in range(5):
                            module.animate(pixels, config, frame)
                        
                        # Check if pixels were modified
                        if any(p != (0, 0, 0) for p in pixels):
                            self.log(f"✓ Animation '{anim_file.stem}' works", "PASS")
                        else:
                            self.log(f"⚠ Animation '{anim_file.stem}' didn't modify pixels", "WARN")
                    else:
                        self.log(f"✗ Animation '{anim_file.stem}' missing animate() function", "FAIL")
                        all_passed = False
                        
                except Exception as e:
                    self.log(f"✗ Animation '{anim_file.stem}' failed: {e}", "FAIL")
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            self.log(f"✗ Animation test failed: {e}", "FAIL")
            traceback.print_exc()
            return False
    
    def test_performance_monitoring(self) -> bool:
        """Test performance monitoring system."""
        self.log("Testing performance monitoring...", "INFO")
        
        try:
            from core.performance import PerformanceMonitor
            
            monitor = PerformanceMonitor()
            
            # Simulate some frames
            for i in range(10):
                monitor.frame_start()
                time.sleep(0.01)  # Simulate 10ms frame time
                monitor.frame_end()
            
            stats = monitor.get_stats()
            
            # Verify stats structure
            expected_keys = ['fps', 'frame_time_ms', 'cpu_percent', 'memory_mb']
            all_passed = True
            
            for key in expected_keys:
                if key in stats:
                    self.log(f"✓ Performance stat '{key}': {stats[key]}", "PASS")
                else:
                    self.log(f"✗ Missing performance stat '{key}'", "FAIL")
                    all_passed = False
            
            # Check if FPS is reasonable
            if 'fps' in stats and isinstance(stats['fps'], dict):
                fps_current = stats['fps'].get('current', 0)
                if fps_current > 0:
                    self.log(f"✓ FPS calculation working: {fps_current:.1f} FPS", "PASS")
                else:
                    self.log("✗ FPS calculation not working", "FAIL")
                    all_passed = False
            else:
                self.log("✗ FPS data structure incorrect", "FAIL")
                all_passed = False
            
            return all_passed
            
        except Exception as e:
            self.log(f"✗ Performance monitoring test failed: {e}", "FAIL")
            traceback.print_exc()
            return False
    
    def start_conductor(self) -> bool:
        """Start the conductor in a subprocess."""
        self.log("Starting conductor in simulation mode...", "INFO")
        
        try:
            # Start conductor in subprocess
            self.conductor_process = subprocess.Popen(
                [sys.executable, "lightbox.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give it time to start
            time.sleep(3)
            
            # Check if still running
            if self.conductor_process.poll() is None:
                self.log("✓ Conductor started successfully", "PASS")
                return True
            else:
                stdout, stderr = self.conductor_process.communicate()
                self.log(f"✗ Conductor exited early", "FAIL")
                if stderr:
                    self.log(f"  Error: {stderr}", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"✗ Failed to start conductor: {e}", "FAIL")
            return False
    
    def test_web_interface(self) -> bool:
        """Test web interface endpoints."""
        self.log("Testing web interface...", "INFO")
        
        if not HAS_REQUESTS:
            self.log("⚠ requests module not available, skipping web tests", "WARN")
            self.log("  Install with: pip install requests", "INFO")
            return True
        
        if not self.conductor_process or self.conductor_process.poll() is not None:
            self.log("⚠ Conductor not running, skipping web tests", "WARN")
            return True
        
        base_url = "http://localhost:5001"
        endpoints = [
            ("/api/status", "Status endpoint"),
            ("/api/performance", "Performance endpoint"),
            ("/api/programs", "Programs list"),
            ("/api/palettes", "Palettes list")
        ]
        
        all_passed = True
        
        # Wait a bit more for web server to be ready
        time.sleep(2)
        
        for endpoint, description in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    self.log(f"✓ {description} ({endpoint}): {response.status_code}", "PASS")
                    
                    # Verify JSON response
                    try:
                        data = response.json()
                        self.log(f"  Response keys: {list(data.keys())[:5]}...", "INFO")
                    except:
                        self.log("  (Non-JSON response)", "INFO")
                else:
                    self.log(f"✗ {description} ({endpoint}): {response.status_code}", "FAIL")
                    all_passed = False
                    
            except requests.exceptions.RequestException as e:
                self.log(f"✗ {description} ({endpoint}): {type(e).__name__}", "FAIL")
                all_passed = False
        
        return all_passed
    
    def stop_conductor(self):
        """Stop the conductor process."""
        if self.conductor_process:
            self.log("Stopping conductor...", "INFO")
            self.conductor_process.terminate()
            self.conductor_process.wait(timeout=5)
            self.log("✓ Conductor stopped", "PASS")
    
    def run_all_tests(self):
        """Run all tests and generate report."""
        self.log("=== LightBox Optimized Implementation Test Suite ===", "INFO")
        self.log(f"Starting tests at {time.strftime('%Y-%m-%d %H:%M:%S')}", "INFO")
        
        test_results = {
            "Module Imports": self.test_imports(),
            "Configuration System": self.test_configuration(),
            "Hardware Drivers": self.test_drivers(),
            "Animation System": self.test_animations(),
            "Performance Monitoring": self.test_performance_monitoring(),
            "Conductor Launch": self.start_conductor(),
            "Web Interface": self.test_web_interface()
        }
        
        # Cleanup
        self.stop_conductor()
        
        # Generate report
        self.log("\n=== Test Summary ===", "INFO")
        passed = sum(1 for v in test_results.values() if v)
        total = len(test_results)
        
        for test_name, result in test_results.items():
            status = "PASS" if result else "FAIL"
            self.log(f"{test_name}: {status}", status)
        
        self.log(f"\nTotal: {passed}/{total} tests passed", "PASS" if passed == total else "FAIL")
        
        # Performance summary
        test_duration = time.time() - self.test_start_time
        self.log(f"Test duration: {test_duration:.1f} seconds", "INFO")
        
        # Save detailed results
        results_file = Path("test_results_optimized.json")
        with open(results_file, 'w') as f:
            json.dump({
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                "duration": test_duration,
                "summary": test_results,
                "details": self.results
            }, f, indent=2)
        
        self.log(f"\nDetailed results saved to: {results_file}", "INFO")
        
        return passed == total


def main():
    """Main entry point."""
    tester = OptimizedLightBoxTester()
    
    # Check if we're in the right directory
    if not Path("lightbox.py").exists():
        print(f"{RED}Error: lightbox.py not found. Run this from the LightBox directory.{RESET}")
        return 1
    
    # Run tests
    success = tester.run_all_tests()
    
    # Provide next steps
    print(f"\n{BLUE}=== Next Steps ==={RESET}")
    if success:
        print(f"{GREEN}✓ All tests passed! The optimized implementation appears to be working correctly.{RESET}")
        print("\nTo test on hardware:")
        print("1. Transfer code to Raspberry Pi")
        print("2. Run: python3 scripts/migrate_to_optimized.py")
        print("3. Run: sudo python3 lightbox.py")
        print("4. Complete the VERIFICATION_CHECKLIST.md")
        print("5. If all checks pass, run: python3 scripts/cleanup_deprecated.py --execute")
    else:
        print(f"{RED}✗ Some tests failed. Please review the errors above.{RESET}")
        print("\nCommon issues:")
        print("- Missing dependencies: pip install -r requirements-optimized.txt")
        print("- Import errors: Check module structure and __init__.py files")
        print("- Web interface: Ensure port 5001 is available")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())