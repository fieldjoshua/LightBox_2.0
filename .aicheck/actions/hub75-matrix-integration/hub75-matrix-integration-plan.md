# ACTION: HUB75MatrixIntegration

**Version:** 1.0  
**Last Updated:** 2025-01-05  
**Status:** ActiveAction  
**Progress:** 0%

## Objective

Integrate comprehensive HUB75 64x64 LED matrix support into the LightBox system, ensuring compatibility with Henner Zeller's rpi-rgb-led-matrix library and the Adafruit RGB Matrix HAT. This includes updating the existing implementations to follow best practices, adding proper GUI controls, and ensuring smooth animation performance.

## Background

The LightBox project already has partial HUB75 support scattered across multiple implementations. This action will consolidate and enhance this support to provide:
- Full integration with the main Conductor.py system
- Proper hardware acceleration using rpi-rgb-led-matrix library
- Web GUI controls for HUB75-specific settings
- Performance optimizations for smooth animations
- Comprehensive testing and documentation

## Success Criteria

1. **Driver Integration**
   - [ ] Consolidated HUB75 driver using rpi-rgb-led-matrix library
   - [ ] Support for 64x64 matrices with Adafruit HAT
   - [ ] Double buffering implementation using SwapOnVSync()
   - [ ] Hardware PWM mode support (GPIO4 to GPIO18 jumper)
   - [ ] Configurable refresh rates and PWM settings

2. **GUI Enhancement**
   - [ ] Matrix type selection (WS2811 vs HUB75)
   - [ ] HUB75-specific configuration controls
   - [ ] Real-time parameter adjustment
   - [ ] Performance monitoring display
   - [ ] Panel chain configuration support

3. **Performance Optimization**
   - [ ] Implement all recommended performance tweaks
   - [ ] CPU isolation support (isolcpus=3)
   - [ ] Fixed frame timing options
   - [ ] GPIO slowdown configuration
   - [ ] Target 30-150 Hz refresh rates

4. **Testing**
   - [ ] Unit tests for HUB75 driver
   - [ ] Integration tests with animations
   - [ ] Performance benchmarks
   - [ ] Hardware verification tests
   - [ ] Simulation mode for development

5. **Documentation**
   - [ ] Setup guide for Pi 3B+ with Adafruit HAT
   - [ ] Configuration parameter reference
   - [ ] Animation development guide
   - [ ] Troubleshooting guide
   - [ ] Migration guide from WS2811

## Technical Approach

### Phase 1: Analysis and Design
1. Review existing HUB75 implementations
2. Analyze rpi-rgb-led-matrix library integration points
3. Design unified driver architecture
4. Plan GUI enhancement structure

### Phase 2: Driver Implementation
1. Create consolidated HUB75 driver class
2. Implement double buffering with SwapOnVSync()
3. Add hardware PWM support detection
4. Integrate with existing matrix_driver.py abstraction
5. Add configuration management

### Phase 3: GUI Enhancement
1. Add matrix type selection to web interface
2. Create HUB75 configuration panel
3. Implement real-time parameter updates
4. Add performance monitoring widgets
5. Update API endpoints for HUB75 control

### Phase 4: Performance Optimization
1. Implement recommended performance tweaks
2. Add CPU isolation configuration
3. Configure fixed frame timing
4. Optimize animation loops
5. Benchmark performance improvements

### Phase 5: Testing and Documentation
1. Write comprehensive test suite
2. Perform hardware verification
3. Create setup documentation
4. Write troubleshooting guide
5. Update CLAUDE.md with HUB75 commands

## Implementation Details

### HUB75 Driver Architecture
```python
class HUB75MatrixDriver:
    def __init__(self, config):
        self.options = RGBMatrixOptions()
        self.options.rows = config.rows
        self.options.cols = config.cols
        self.options.chain_length = config.chain_length
        self.options.parallel = config.parallel
        self.options.hardware_mapping = config.hardware_mapping
        self.options.gpio_slowdown = config.gpio_slowdown
        self.options.pwm_bits = config.pwm_bits
        self.options.pwm_lsb_nanoseconds = config.pwm_lsb_nanoseconds
        
        self.matrix = RGBMatrix(options=self.options)
        self.canvas = self.matrix.CreateFrameCanvas()
    
    def update(self, pixels):
        # Convert pixel data to canvas
        # Use SwapOnVSync for smooth updates
        pass
```

### GUI Configuration Schema
```json
{
  "matrix_type": "hub75",
  "hub75_config": {
    "rows": 64,
    "cols": 64,
    "chain_length": 1,
    "parallel": 1,
    "hardware_mapping": "adafruit-hat",
    "gpio_slowdown": 4,
    "pwm_bits": 11,
    "pwm_lsb_nanoseconds": 130,
    "brightness": 100,
    "limit_refresh": 0,
    "hardware_pwm": false
  }
}
```

### Performance Configuration
- Enable hardware PWM by detecting GPIO4-GPIO18 jumper
- Set isolcpus=3 in boot parameters for CPU isolation
- Configure --led-limit-refresh for stable frame rates
- Use --led-pwm-bits=11 for optimal color depth
- Apply --led-gpio-slowdown=4 for Pi 3B+ timing

## Dependencies

### External Dependencies
- rgbmatrix (from rpi-rgb-led-matrix library)
- Pillow >= 8.0.0 (for image processing)
- numpy >= 1.19.0 (for matrix operations)

### Internal Dependencies
- matrix_driver.py (base abstraction)
- config.py (configuration management)
- webgui/app.py (web interface)

## Testing Strategy

### Unit Tests
- HUB75 driver initialization
- Configuration validation
- Pixel format conversion
- Double buffer operations

### Integration Tests
- Animation playback
- GUI control responsiveness
- Configuration persistence
- Hardware detection

### Performance Tests
- Frame rate measurement
- CPU usage monitoring
- Memory usage tracking
- Latency testing

### Hardware Tests
- Panel initialization
- Brightness control
- Color accuracy
- Chain configuration

## Risk Mitigation

1. **Hardware Compatibility**
   - Test with multiple Pi models
   - Verify HAT/Bonnet compatibility
   - Document GPIO conflicts

2. **Performance Issues**
   - Implement fallback modes
   - Add FPS limiting options
   - Monitor resource usage

3. **Library Dependencies**
   - Pin library versions
   - Test upgrade paths
   - Document build process

## Timeline

- Phase 1: 1 day (Analysis and Design)
- Phase 2: 2 days (Driver Implementation)
- Phase 3: 2 days (GUI Enhancement)
- Phase 4: 1 day (Performance Optimization)
- Phase 5: 2 days (Testing and Documentation)

Total estimated time: 8 days

## Notes

- Priority on maintaining backward compatibility with WS2811
- Focus on smooth animation performance (30+ FPS)
- Ensure easy setup process for new users
- Consider future support for multiple panel chains