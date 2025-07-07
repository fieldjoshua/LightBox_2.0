#!/usr/bin/env python3
"""
Test suite for the optimized LightBox implementation.
Used by AICheck auto-iterate to validate fixes.
"""

import pytest
import sys
from pathlib import Path
import importlib

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestModuleImports:
    """Test that all core modules can be imported."""
    
    def test_config_module(self):
        """Test configuration module imports."""
        from core import config
        assert hasattr(config, 'ConfigManager')
    
    def test_conductor_module(self):
        """Test conductor module imports."""
        try:
            from core import conductor
            assert hasattr(conductor, 'main')
        except ImportError as e:
            if 'psutil' in str(e):
                pytest.skip("psutil not installed")
            else:
                raise
    
    def test_performance_module(self):
        """Test performance module imports."""
        try:
            from core import performance
            assert hasattr(performance, 'PerformanceMonitor')
        except ImportError as e:
            if 'psutil' in str(e):
                pytest.skip("psutil not installed")
            else:
                raise
    
    def test_driver_modules(self):
        """Test driver modules import."""
        from drivers import matrix_driver
        assert hasattr(matrix_driver, 'MatrixDriver')
        
        from drivers import ws2811_driver
        assert hasattr(ws2811_driver, 'WS2811Driver')
        
        from drivers import hub75_driver
        assert hasattr(hub75_driver, 'HUB75Driver')
    
    def test_web_module(self):
        """Test web interface module."""
        try:
            from web import app
            assert hasattr(app, 'create_app') or hasattr(app, 'app')
        except ImportError as e:
            if 'flask' in str(e):
                pytest.skip("flask not installed")
            else:
                raise
    
    def test_utils_modules(self):
        """Test utility modules exist."""
        try:
            from utils import color_utils
            assert hasattr(color_utils, 'hsv_to_rgb')
        except ImportError:
            pytest.fail("color_utils module missing")
        
        try:
            from utils import frame_utils
            assert hasattr(frame_utils, 'create_frame')
        except ImportError:
            pytest.fail("frame_utils module missing")


class TestConfiguration:
    """Test configuration system functionality."""
    
    def test_config_manager_creation(self):
        """Test ConfigManager can be created."""
        from core.config import ConfigManager
        config = ConfigManager()
        assert config is not None
    
    def test_config_has_optimizations(self):
        """Test configuration has optimization features."""
        from core.config import ConfigManager
        config = ConfigManager()
        
        # Check for optimization attributes
        assert hasattr(config, '_gamma_table') or hasattr(config, 'gamma_table')
        assert hasattr(config, '_serpentine_map') or hasattr(config, 'serpentine_map')
        assert hasattr(config, 'platform')
    
    def test_coordinate_mapping(self):
        """Test coordinate to index mapping."""
        from core.config import ConfigManager
        config = ConfigManager()
        
        # Test valid coordinates
        assert config.xy_to_index(0, 0) >= 0
        assert config.xy_to_index(9, 9) < 100
        assert config.xy_to_index(5, 5) == 55  # For progressive wiring
    
    def test_color_conversion(self):
        """Test HSV to RGB conversion."""
        from core.config import ConfigManager
        config = ConfigManager()
        
        # Test basic color conversion
        rgb = config.hsv_to_rgb(0.0, 1.0, 1.0)  # Red
        assert isinstance(rgb, tuple)
        assert len(rgb) == 3
        assert all(0 <= c <= 255 for c in rgb)


class TestDrivers:
    """Test hardware driver functionality."""
    
    def test_ws2811_driver_creation(self):
        """Test WS2811 driver can be created."""
        from core.config import ConfigManager
        from drivers.ws2811_driver import WS2811Driver
        
        config = ConfigManager()
        try:
            driver = WS2811Driver(config)
            assert driver is not None
        except Exception as e:
            if "NeoPixel" in str(e) or "GPIO" in str(e):
                pytest.skip("Hardware libraries not available")
            else:
                raise
    
    def test_hub75_driver_creation(self):
        """Test HUB75 driver can be created."""
        from core.config import ConfigManager
        from drivers.hub75_driver import HUB75Driver
        
        config = ConfigManager()
        try:
            driver = HUB75Driver(config)
            assert driver is not None
        except Exception as e:
            if "rgbmatrix" in str(e):
                pytest.skip("rgbmatrix library not available")
            else:
                raise


class TestAnimations:
    """Test animation system."""
    
    def test_animation_loading(self):
        """Test that animations can be loaded."""
        animations_dir = Path("animations")
        assert animations_dir.exists(), "Animations directory missing"
        
        animation_files = list(animations_dir.glob("*.py"))
        assert len(animation_files) > 0, "No animation files found"
    
    def test_animation_execution(self):
        """Test animation function execution."""
        from core.config import ConfigManager
        import importlib.util
        
        config = ConfigManager()
        animations_dir = Path("animations")
        
        # Test first available animation
        for anim_file in animations_dir.glob("*.py"):
            spec = importlib.util.spec_from_file_location(
                anim_file.stem, anim_file
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, 'animate'):
                pixels = [(0, 0, 0)] * 100
                module.animate(pixels, config, 0)
                # Just check it doesn't crash
                assert True
                break


class TestSimulationMode:
    """Test simulation mode functionality."""
    
    def test_simulation_detection(self):
        """Test that simulation mode is properly detected."""
        import os
        os.environ['LIGHTBOX_SIMULATION'] = '1'
        
        from core.config import ConfigManager
        config = ConfigManager()
        
        # Should detect simulation mode
        assert config.get('simulation_mode', False) or \
               'simulation' in str(config.platform).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])