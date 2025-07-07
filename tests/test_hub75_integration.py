#!/usr/bin/env python3
"""
Integration tests for HUB75 matrix functionality
Tests the complete integration of HUB75 driver with web GUI and animations
"""

import unittest
import sys
import os
import json
import tempfile
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'LB_Interface', 'LightBox'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'LB_Interface', 'LightBox', 'webgui'))

from config_enhanced import Config, HUB75Settings
from matrix_driver_enhanced import create_matrix_driver, HUB75Driver
from app_enhanced import create_app


class TestHUB75WebIntegration(unittest.TestCase):
    """Test HUB75 integration with web interface"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = Config()
        self.config.matrix_type = "HUB75"
        
        # Mock matrix for testing
        self.mock_matrix = MagicMock()
        self.mock_matrix.running = False
        self.mock_matrix.driver = MagicMock()
        
        # Create Flask test app
        self.app = create_app(matrix=self.mock_matrix, config=self.config)
        self.client = self.app.test_client()
        
    def test_matrix_type_endpoint(self):
        """Test matrix type GET and POST endpoints"""
        # Test GET
        response = self.client.get('/api/matrix-type')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['type'], 'HUB75')
        
        # Test POST - switch to WS2811
        response = self.client.post('/api/matrix-type',
                                  json={'type': 'WS2811'},
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(self.config.matrix_type, 'WS2811')
        
        # Test POST - switch back to HUB75
        response = self.client.post('/api/matrix-type',
                                  json={'type': 'HUB75'},
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.config.matrix_type, 'HUB75')
        
        # Test invalid matrix type
        response = self.client.post('/api/matrix-type',
                                  json={'type': 'INVALID'},
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
    def test_hub75_config_endpoint(self):
        """Test HUB75 configuration GET and POST endpoints"""
        # Test GET
        response = self.client.get('/api/hub75-config')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['pwm_bits'], 11)
        self.assertEqual(data['gpio_slowdown'], 4)
        
        # Test POST - update configuration
        new_config = {
            'pwm_bits': 9,
            'gpio_slowdown': 2,
            'hardware_mapping': 'regular'
        }
        response = self.client.post('/api/hub75-config',
                                  json=new_config,
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # Verify changes
        self.assertEqual(self.config.hub75_settings.pwm_bits, 9)
        self.assertEqual(self.config.hub75_settings.gpio_slowdown, 2)
        self.assertEqual(self.config.hub75_settings.hardware_mapping, 'regular')
        
    def test_performance_stats_endpoint(self):
        """Test performance statistics endpoint"""
        # Mock performance stats
        self.mock_matrix.driver.get_performance_stats.return_value = {
            'fps': 29.8,
            'avg_fps': 30.1,
            'frame_count': 1234,
            'uptime': 120.5
        }
        
        response = self.client.get('/api/performance-stats')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertAlmostEqual(data['fps'], 29.8, places=1)
        self.assertAlmostEqual(data['avg_fps'], 30.1, places=1)
        self.assertEqual(data['frame_count'], 1234)
        
    def test_config_persistence(self):
        """Test configuration persistence across restarts"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
            
        try:
            # Save current config
            self.config.save_settings(temp_file)
            
            # Create new config and load
            config2 = Config()
            config2.load_settings(temp_file)
            
            # Verify HUB75 settings persisted
            self.assertEqual(config2.matrix_type, 'HUB75')
            self.assertEqual(config2.hub75_settings.pwm_bits, 
                           self.config.hub75_settings.pwm_bits)
            
        finally:
            os.unlink(temp_file)


class TestHUB75AnimationIntegration(unittest.TestCase):
    """Test HUB75 with animation system"""
    
    @patch('matrix_driver_enhanced.HUB75Driver.init_hardware')
    def test_animation_compatibility(self, mock_init):
        """Test that animations work with HUB75 driver"""
        mock_init.return_value = True
        
        # Create config and driver
        config = Config()
        config.set_matrix_type("HUB75")
        driver = HUB75Driver(config)
        
        # Mock the matrix and canvas
        driver.matrix = MagicMock()
        driver.offscreen_canvas = MagicMock()
        
        # Simulate animation frame
        total_pixels = 64 * 64
        pixels = [(0, 0, 0)] * total_pixels
        
        # Create test pattern
        for i in range(total_pixels):
            x = i % 64
            y = i // 64
            pixels[i] = (x * 4, y * 4, 128)
        
        # Test bulk pixel update
        driver.set_pixels_bulk(pixels)
        
        # Verify pixels were set
        self.assertEqual(driver.offscreen_canvas.SetPixel.call_count, total_pixels)
        
        # Test show/update
        driver.show()
        driver.matrix.SwapOnVSync.assert_called_once()
        
    def test_matrix_type_switching(self):
        """Test switching between WS2811 and HUB75 during runtime"""
        config = Config()
        
        # Start with WS2811
        config.set_matrix_type("WS2811")
        driver1 = create_matrix_driver(config, force_simulation=True)
        self.assertEqual(driver1.__class__.__name__, 'SimulationDriver')
        
        # Switch to HUB75
        config.set_matrix_type("HUB75")
        driver2 = create_matrix_driver(config, force_simulation=True)
        self.assertEqual(driver2.__class__.__name__, 'SimulationDriver')
        
        # Verify dimensions changed
        self.assertEqual(driver1.width, 10)
        self.assertEqual(driver1.height, 10)
        self.assertEqual(driver2.width, 64)
        self.assertEqual(driver2.height, 64)


class TestHUB75PerformanceOptimizations(unittest.TestCase):
    """Test performance optimization features"""
    
    @patch('RPi.GPIO')
    @patch('matrix_driver_enhanced.HUB75Driver._create_optimized_options')
    def test_hardware_pwm_detection(self, mock_create_options, mock_gpio):
        """Test hardware PWM jumper detection"""
        # Mock GPIO for hardware PWM detection
        mock_gpio.setmode.return_value = None
        mock_gpio.setup.return_value = None
        mock_gpio.input.side_effect = [1, 1]  # Both pins read same = jumper installed
        mock_gpio.cleanup.return_value = None
        
        config = Config()
        config.matrix_type = "HUB75"
        driver = HUB75Driver(config)
        
        # Test detection
        result = driver._detect_hardware_pwm()
        self.assertTrue(result)
        self.assertTrue(driver.hardware_pwm_enabled)
        
    def test_performance_monitoring(self):
        """Test performance monitoring functionality"""
        from matrix_driver_enhanced import PerformanceMonitor
        
        monitor = PerformanceMonitor()
        
        # Simulate frames
        import time
        for i in range(10):
            monitor.update()
            time.sleep(0.033)  # ~30 FPS
            
        stats = monitor.get_stats()
        
        # Check stats
        self.assertEqual(stats['frame_count'], 10)
        self.assertGreater(stats['fps'], 20)
        self.assertLess(stats['fps'], 40)
        self.assertGreater(stats['avg_fps'], 20)
        self.assertLess(stats['avg_fps'], 40)
        self.assertGreater(stats['uptime'], 0.3)
        
    def test_configuration_limits(self):
        """Test configuration parameter validation"""
        settings = HUB75Settings()
        
        # Test valid ranges
        settings.pwm_bits = 11
        self.assertEqual(settings.pwm_bits, 11)
        
        settings.gpio_slowdown = 5
        self.assertEqual(settings.gpio_slowdown, 5)
        
        # Test serialization with all options
        data = settings.to_dict()
        self.assertIn('pwm_bits', data)
        self.assertIn('gpio_slowdown', data)
        self.assertIn('hardware_mapping', data)
        self.assertIn('disable_hardware_pulsing', data)


class TestMigrationScript(unittest.TestCase):
    """Test migration script functionality"""
    
    def test_config_migration(self):
        """Test configuration migration for HUB75 support"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            # Write old-style config
            old_config = {
                "matrix_width": 10,
                "matrix_height": 10,
                "brightness": 0.5,
                "current_program": "rainbow"
            }
            json.dump(old_config, f)
            temp_file = f.name
            
        try:
            # Import migration function
            from migrate_to_hub75 import migrate_config
            from pathlib import Path
            
            # Run migration
            result = migrate_config(Path(temp_file))
            self.assertTrue(result)
            
            # Load migrated config
            with open(temp_file, 'r') as f:
                migrated = json.load(f)
                
            # Verify migration
            self.assertIn('hub75_settings', migrated)
            self.assertIn('matrix_type', migrated)
            self.assertEqual(migrated['matrix_type'], 'WS2811')  # Default to existing
            self.assertEqual(migrated['hub75_settings']['rows'], 64)
            self.assertEqual(migrated['hub75_settings']['cols'], 64)
            
        finally:
            os.unlink(temp_file)


if __name__ == '__main__':
    unittest.main()