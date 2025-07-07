# HUB75 Integration Architecture Design

## Executive Summary

This document outlines the architecture for integrating comprehensive HUB75 support into the LightBox system. The design leverages existing infrastructure while adding new capabilities for hardware-accelerated performance and advanced configuration options.

## Design Principles

1. **Backward Compatibility**: Maintain full support for WS2811 matrices
2. **Progressive Enhancement**: Add HUB75 features without breaking existing functionality
3. **Performance First**: Implement all recommended optimizations from research
4. **User Friendly**: Simple setup with advanced options available
5. **Testable**: Clear interfaces for unit and integration testing

## Architecture Overview

```
┌─────────────────────┐
│   Web Interface     │
│  (Enhanced GUI)     │
└──────────┬──────────┘
           │ REST API
┌──────────┴──────────┐
│   Flask App         │
│  (API Endpoints)    │
└──────────┬──────────┘
           │
┌──────────┴──────────┐
│   Conductor         │
│ (Animation Engine)  │
└──────────┬──────────┘
           │
┌──────────┴──────────┐
│  Matrix Driver      │
│   (Abstraction)     │
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    │             │
┌───┴────┐   ┌───┴────┐
│WS2811  │   │ HUB75  │
│Driver  │   │ Driver │
└────────┘   └────────┘
```

## Component Design

### 1. Enhanced HUB75Driver Class

```python
class HUB75Driver(MatrixDriver):
    """Enhanced HUB75 driver with full feature support"""
    
    def __init__(self, config):
        super().__init__(config)
        self.matrix = None
        self.canvas = None
        self.offscreen_canvas = None
        self.graphics = None
        self.hardware_pwm_enabled = False
        self.performance_stats = PerformanceMonitor()
        
    def init_hardware(self):
        """Initialize with all performance optimizations"""
        # Detect hardware PWM jumper
        self.hardware_pwm_enabled = self._detect_hardware_pwm()
        
        # Configure with optimal settings
        options = self._create_optimized_options()
        
        # Initialize matrix
        self.matrix = RGBMatrix(options=options)
        self.canvas = self.matrix.CreateFrameCanvas()
        self.offscreen_canvas = self.matrix.CreateFrameCanvas()
```

### 2. Configuration Schema Enhancement

```python
@dataclass
class HUB75Settings:
    """Comprehensive HUB75 configuration"""
    # Display settings
    rows: int = 64
    cols: int = 64
    chain_length: int = 1
    parallel: int = 1
    
    # Performance settings
    pwm_bits: int = 11
    pwm_lsb_nanoseconds: int = 130
    gpio_slowdown: int = 4
    limit_refresh: int = 0
    
    # Hardware settings
    hardware_mapping: str = 'adafruit-hat'
    pixel_mapper: str = ''
    panel_type: str = ''
    
    # Optimization flags
    hardware_pwm: bool = False
    cpu_isolation: bool = False
    fixed_frame_microseconds: int = 0
```

### 3. Web GUI Enhancements

#### Matrix Type Selection
```html
<div class="control-group">
    <h3>Matrix Type</h3>
    <div class="radio-group">
        <label>
            <input type="radio" name="matrixType" value="ws2811" checked>
            <span>WS2811/NeoPixel</span>
        </label>
        <label>
            <input type="radio" name="matrixType" value="hub75">
            <span>HUB75 RGB Panel</span>
        </label>
    </div>
</div>
```

#### HUB75 Configuration Panel
```html
<div id="hub75Config" class="config-panel" style="display: none;">
    <h3>HUB75 Configuration</h3>
    
    <!-- Basic Settings -->
    <div class="config-section">
        <h4>Display Settings</h4>
        <label>Panel Size:
            <select id="panelSize">
                <option value="32x32">32x32</option>
                <option value="64x64" selected>64x64</option>
                <option value="64x32">64x32</option>
            </select>
        </label>
        
        <label>Hardware Mapping:
            <select id="hardwareMapping">
                <option value="regular">Regular</option>
                <option value="adafruit-hat" selected>Adafruit HAT</option>
                <option value="adafruit-hat-pwm">Adafruit HAT + PWM</option>
            </select>
        </label>
    </div>
    
    <!-- Performance Settings -->
    <div class="config-section">
        <h4>Performance Tuning</h4>
        <label>PWM Bits:
            <input type="range" id="pwmBits" min="1" max="11" value="11">
            <span id="pwmBitsValue">11</span>
        </label>
        
        <label>GPIO Slowdown:
            <input type="range" id="gpioSlowdown" min="0" max="5" value="4">
            <span id="gpioSlowdownValue">4</span>
        </label>
        
        <label>
            <input type="checkbox" id="hardwarePwm">
            Enable Hardware PWM (requires jumper)
        </label>
    </div>
    
    <!-- Performance Monitor -->
    <div class="performance-monitor">
        <h4>Performance</h4>
        <div class="stat">FPS: <span id="currentFps">0</span></div>
        <div class="stat">Refresh Rate: <span id="refreshRate">0</span> Hz</div>
        <div class="stat">CPU Usage: <span id="cpuUsage">0</span>%</div>
    </div>
</div>
```

### 4. API Endpoint Enhancements

```python
@app.route('/api/matrix-type', methods=['GET', 'POST'])
def matrix_type():
    """Get or set matrix type"""
    if request.method == 'POST':
        data = request.json
        matrix_type = data.get('type', 'ws2811')
        
        # Reinitialize driver if type changed
        if matrix_type != config.matrix_type:
            config.matrix_type = matrix_type
            conductor.reinitialize_driver()
            
        return jsonify({'success': True, 'type': matrix_type})
    
    return jsonify({'type': config.matrix_type})

@app.route('/api/hub75-config', methods=['GET', 'POST'])
def hub75_config():
    """Get or set HUB75-specific configuration"""
    if request.method == 'POST':
        data = request.json
        
        # Update HUB75 settings
        for key, value in data.items():
            if hasattr(config.hub75_settings, key):
                setattr(config.hub75_settings, key, value)
        
        # Apply changes
        if config.matrix_type == 'hub75':
            conductor.apply_hub75_settings()
            
        return jsonify({'success': True})
    
    return jsonify(config.hub75_settings.to_dict())

@app.route('/api/performance-stats', methods=['GET'])
def performance_stats():
    """Get real-time performance statistics"""
    stats = conductor.get_performance_stats()
    return jsonify(stats)
```

### 5. Performance Optimization Implementation

```python
class PerformanceOptimizer:
    """Manages HUB75 performance optimizations"""
    
    def apply_optimizations(self, config):
        """Apply all recommended performance tweaks"""
        
        # 1. Hardware PWM detection
        if self._detect_hardware_pwm_jumper():
            config.disable_hardware_pulsing = False
            logging.info("Hardware PWM enabled via GPIO4-GPIO18 jumper")
        
        # 2. CPU isolation check
        if self._check_cpu_isolation():
            # Pin update thread to isolated CPU
            self._set_cpu_affinity(3)
            logging.info("CPU isolation active - using CPU 3")
        
        # 3. Fixed frame timing
        if config.fixed_frame_microseconds > 0:
            # Apply fixed timing for stable refresh
            pass
        
        # 4. Optimal PWM settings for Pi 3B+
        if self._detect_pi_version() == "3B+":
            config.gpio_slowdown = 4
            config.pwm_bits = 11
            config.pwm_lsb_nanoseconds = 130
    
    def _detect_hardware_pwm_jumper(self):
        """Detect if GPIO4-GPIO18 jumper is installed"""
        try:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            
            # If pins are connected, they'll read the same
            result = GPIO.input(4) == GPIO.input(18)
            GPIO.cleanup()
            return result
        except:
            return False
```

## Testing Strategy

### Unit Tests
```python
# test_hub75_driver.py
class TestHUB75Driver:
    def test_initialization(self):
        """Test driver initialization with various configs"""
        
    def test_pixel_operations(self):
        """Test set_pixel, fill, clear operations"""
        
    def test_double_buffering(self):
        """Test SwapOnVSync functionality"""
        
    def test_performance_monitoring(self):
        """Test FPS and refresh rate tracking"""
```

### Integration Tests
```python
# test_hub75_integration.py
class TestHUB75Integration:
    def test_web_api_endpoints(self):
        """Test all HUB75-related API endpoints"""
        
    def test_configuration_persistence(self):
        """Test saving/loading HUB75 settings"""
        
    def test_animation_playback(self):
        """Test running animations on HUB75"""
        
    def test_driver_switching(self):
        """Test switching between WS2811 and HUB75"""
```

## Migration Path

1. **Phase 1**: Update matrix_driver.py with enhanced HUB75Driver
2. **Phase 2**: Add configuration schema and persistence
3. **Phase 3**: Implement web GUI enhancements
4. **Phase 4**: Add performance optimizations
5. **Phase 5**: Create tests and documentation

## Risk Mitigation

1. **Hardware Compatibility**
   - Test on Pi 3B+, Pi 4, Pi Zero W
   - Verify with different HUB75 panels
   - Document known working configurations

2. **Performance Degradation**
   - Implement performance monitoring
   - Add configurable FPS limits
   - Provide optimization presets

3. **User Experience**
   - Default to safe settings
   - Provide clear setup wizard
   - Include troubleshooting guide

## Success Metrics

- Achieve 30-150 Hz refresh rates on Pi 3B+
- Support all rgbmatrix library features
- Maintain backward compatibility
- Pass all integration tests
- Positive user feedback on setup ease