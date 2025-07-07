#!/usr/bin/env python3
"""
Unit tests for HUB75 matrix driver functionality
Tests driver initialization, configuration, and performance features
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'LB_Interface', 'LightBox'))

from matrix_driver_enhanced import HUB75Driver, HUB75Settings, PerformanceMonitor
from config_enhanced import Config


class TestHUB75Settings(unittest.TestCase):
    """Test HUB75Settings dataclass"""
    
    def test_default_settings(self):
        """Test default HUB75 settings"""
        settings = HUB75Settings()
        
        self.assertEqual(settings.rows, 64)
        self.assertEqual(settings.cols, 64)
        self.assertEqual(settings.pwm_bits, 11)
        self.assertEqual(settings.gpio_slowdown, 4)
        self.assertEqual(settings.hardware_mapping, 'adafruit-hat')
        
    def test_serialization(self):
        """Test to_dict and from_dict methods"""
        settings = HUB75Settings(
            rows=32,
            cols=32,
            pwm_bits=7,
            hardware_mapping='regular'
        )
        
        # Convert to dict
        data = settings.to_dict()
        self.assertEqual(data['rows'], 32)
        self.assertEqual(data['cols'], 32)
        self.assertEqual(data['pwm_bits'], 7)
        
        # Convert back from dict
        restored = HUB75Settings.from_dict(data)
        self.assertEqual(restored.rows, 32)
        self.assertEqual(restored.cols, 32)
        self.assertEqual(restored.pwm_bits, 7)


class TestHUB75Driver(unittest.TestCase):
    """Test HUB75Driver class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = Config()
        self.config.matrix_type = "HUB75"
        self.config.matrix_width = 64
        self.config.matrix_height = 64
        self.config.brightness = 0.5
        
    @patch('matrix_driver_enhanced.HUB75Driver._detect_hardware_pwm')
    def test_driver_initialization(self, mock_detect_pwm):
        """Test driver initialization without actual hardware"""
        mock_detect_pwm.return_value = False
        
        driver = HUB75Driver(self.config)
        
        self.assertEqual(driver.width, 64)
        self.assertEqual(driver.height, 64)
        self.assertIsNotNone(driver.hub75_settings)
        self.assertIsInstance(driver.performance_monitor, PerformanceMonitor)
        
    @patch('RPi.GPIO')
    def test_hardware_pwm_detection(self, mock_gpio):
        """Test hardware PWM jumper detection"""
        # Mock GPIO module
        mock_gpio.setmode.return_value = None
        mock_gpio.setup.return_value = None
        mock_gpio.cleanup.return_value = None
        
        driver = HUB75Driver(self.config)
        
        # Test when pins are connected (hardware PWM enabled)
        mock_gpio.input.side_effect = [1, 1]  # Both pins read the same
        result = driver._detect_hardware_pwm()
        self.assertTrue(result)
        
        # Test when pins are not connected
        mock_gpio.input.side_effect = [1, 0]  # Pins read different
        result = driver._detect_hardware_pwm()
        self.assertFalse(result)
        
    @patch('matrix_driver_enhanced.RGBMatrix')
    @patch('matrix_driver_enhanced.RGBMatrixOptions')
    def test_create_optimized_options(self, mock_options_class, mock_matrix_class):
        """Test creation of optimized RGB matrix options"""
        mock_options = MagicMock()
        mock_options_class.return_value = mock_options
        
        driver = HUB75Driver(self.config)
        driver.hardware_pwm_enabled = True
        
        # Create options
        options = driver._create_optimized_options()
        
        # Verify options were set correctly
        self.assertEqual(mock_options.rows, 64)
        self.assertEqual(mock_options.cols, 64)
        self.assertEqual(mock_options.pwm_bits, 11)
        self.assertEqual(mock_options.gpio_slowdown, 4)
        self.assertEqual(mock_options.hardware_mapping, 'adafruit-hat')
        self.assertFalse(mock_options.disable_hardware_pulsing)  # Hardware PWM enabled
        
    def test_pixel_operations(self):
        """Test pixel manipulation methods"""
        driver = HUB75Driver(self.config)
        
        # Mock the canvas
        driver.offscreen_canvas = MagicMock()
        
        # Test set_pixel
        driver.set_pixel(10, 20, 255, 128, 64)
        driver.offscreen_canvas.SetPixel.assert_called_once_with(10, 20, 255, 128, 64)
        
        # Test set_pixels_bulk
        pixels = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        driver.set_pixels_bulk(pixels)
        self.assertEqual(driver.offscreen_canvas.SetPixel.call_count, 4)  # 3 new + 1 from before
        
    def test_brightness_control(self):
        """Test brightness adjustment"""
        driver = HUB75Driver(self.config)
        driver.matrix = MagicMock()
        
        # Test brightness setting
        driver.set_brightness(0.75)
        self.assertEqual(driver.matrix.brightness, 75)
        
        # Test boundary values
        driver.set_brightness(0.0)
        self.assertEqual(driver.matrix.brightness, 0)
        
        driver.set_brightness(1.0)
        self.assertEqual(driver.matrix.brightness, 100)


class TestPerformanceMonitor(unittest.TestCase):
    """Test PerformanceMonitor class"""
    
    def test_fps_tracking(self):
        """Test FPS calculation and tracking"""
        monitor = PerformanceMonitor()
        
        # Initial state
        stats = monitor.get_stats()
        self.assertEqual(stats['fps'], 0)
        self.assertEqual(stats['frame_count'], 0)
        
        # Simulate frames
        import time
        for _ in range(5):
            monitor.update()
            time.sleep(0.033)  # ~30 FPS
            
        stats = monitor.get_stats()
        self.assertEqual(stats['frame_count'], 5)
        self.assertGreater(stats['fps'], 20)  # Should be around 30 FPS
        self.assertLess(stats['fps'], 40)
        
    def test_average_fps(self):
        """Test average FPS calculation"""
        monitor = PerformanceMonitor()
        
        # Add some FPS samples
        monitor.fps_samples = [30, 32, 28, 31, 29]
        
        stats = monitor.get_stats()
        self.assertEqual(stats['avg_fps'], 30.0)


class TestConfigIntegration(unittest.TestCase):
    """Test Config class HUB75 integration"""
    
    def test_matrix_type_switching(self):
        """Test switching between WS2811 and HUB75"""
        config = Config()
        
        # Default should be WS2811
        self.assertEqual(config.matrix_type, "WS2811")
        self.assertEqual(config.matrix_width, 10)
        self.assertEqual(config.matrix_height, 10)
        
        # Switch to HUB75
        config.set_matrix_type("HUB75")
        self.assertEqual(config.matrix_type, "HUB75")
        self.assertEqual(config.matrix_width, 64)
        self.assertEqual(config.matrix_height, 64)
        self.assertEqual(config.fps, 30)
        self.assertFalse(config.serpentine_wiring)
        
        # Switch back to WS2811
        config.set_matrix_type("WS2811")
        self.assertEqual(config.matrix_width, 10)
        self.assertEqual(config.matrix_height, 10)
        self.assertEqual(config.fps, 15)
        self.assertTrue(config.serpentine_wiring)
        
    def test_hub75_settings_persistence(self):
        """Test saving and loading HUB75 settings"""
        config = Config()
        config.set_matrix_type("HUB75")
        
        # Modify HUB75 settings
        config.hub75_settings.pwm_bits = 9
        config.hub75_settings.gpio_slowdown = 2
        
        # Save to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
            
        config.save_settings(temp_file)
        
        # Load into new config
        config2 = Config()
        config2.load_settings(temp_file)
        
        # Verify settings were restored
        self.assertEqual(config2.matrix_type, "HUB75")
        self.assertEqual(config2.hub75_settings.pwm_bits, 9)
        self.assertEqual(config2.hub75_settings.gpio_slowdown, 2)
        
        # Clean up
        os.unlink(temp_file)


class TestMatrixCoordinates(unittest.TestCase):
    """Test matrix coordinate conversion"""
    
    def test_hub75_coordinates(self):
        """Test coordinate conversion for HUB75 (progressive wiring)"""
        config = Config()
        config.set_matrix_type("HUB75")
        
        # HUB75 uses progressive wiring
        self.assertFalse(config.serpentine_wiring)
        
        # Test coordinate conversions
        self.assertEqual(config.xy_to_index(0, 0), 0)
        self.assertEqual(config.xy_to_index(63, 0), 63)
        self.assertEqual(config.xy_to_index(0, 1), 64)
        self.assertEqual(config.xy_to_index(63, 63), 4095)
        
        # Test reverse conversion
        self.assertEqual(config.index_to_xy(0), (0, 0))
        self.assertEqual(config.index_to_xy(63), (63, 0))
        self.assertEqual(config.index_to_xy(64), (0, 1))
        self.assertEqual(config.index_to_xy(4095), (63, 63))


if __name__ == '__main__':
    unittest.main()