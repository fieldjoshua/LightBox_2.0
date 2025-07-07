# LightBox Unified Architecture Design

## Architecture Overview

The unified LightBox architecture follows a modular, performance-optimized design that supports both WS2811 and HUB75 LED matrices while maintaining clean separation of concerns.

```
┌─────────────────────────────────────────────────────────────┐
│                        Web Interface                         │
│                    (Flask + SocketIO)                        │
└─────────────────────┬───────────────────────────────────────┘
                      │ REST API / WebSocket
┌─────────────────────▼───────────────────────────────────────┐
│                      Core Conductor                          │
│              (Animation Loop Controller)                     │
├─────────────────────────────────────────────────────────────┤
│  Performance    │  Config      │  Animation   │  Hardware   │
│  Monitor        │  Manager     │  Engine      │  Manager    │
└────────┬────────┴──────┬───────┴──────┬──────┴──────┬──────┘
         │               │              │             │
    ┌────▼────┐    ┌─────▼─────┐  ┌────▼────┐  ┌────▼────┐
    │ Metrics │    │ Settings  │  │Animation│  │ Buttons │
    │ Collect │    │   Cache   │  │ Plugins │  │  OLED   │
    └─────────┘    └───────────┘  └─────────┘  └─────────┘
                                        │
                              ┌─────────▼─────────┐
                              │  Matrix Driver   │
                              │   (Abstract)     │
                              └────────┬─────────┘
                     ┌─────────────────┴─────────────────┐
                     │                                   │
               ┌─────▼─────┐                      ┌─────▼─────┐
               │ WS2811    │                      │  HUB75    │
               │ Driver    │                      │  Driver   │
               └─────┬─────┘                      └─────┬─────┘
                     │                                   │
               ┌─────▼─────┐                      ┌─────▼─────┐
               │ NeoPixel  │                      │ RGB Matrix│
               │  Library  │                      │  Library  │
               └───────────┘                      └───────────┘
```

## Module Specifications

### 1. Core Module (`core/`)

#### conductor.py - Main Controller
```python
class Conductor:
    """Unified animation controller with performance optimizations"""
    
    def __init__(self, config_path='config.json'):
        self.config = ConfigManager(config_path)
        self.performance = PerformanceMonitor()
        self.matrix = MatrixDriverFactory.create(self.config)
        self.animation_engine = AnimationEngine(self.config)
        self.hardware = HardwareManager(self.config)
        self.web_server = None
        
        # Performance optimizations
        self._frame_pool = FrameBufferPool()
        self._last_frame_time = 0
        self._target_frame_time = 1.0 / self.config.target_fps
        
    def run(self):
        """Main animation loop with frame rate control"""
        while self.running:
            frame_start = time.perf_counter()
            
            # Get pooled frame buffer
            frame_buffer = self._frame_pool.acquire()
            
            # Run animation
            self.animation_engine.render(frame_buffer)
            
            # Update matrix
            self.matrix.update(frame_buffer)
            
            # Return buffer to pool
            self._frame_pool.release(frame_buffer)
            
            # Frame rate limiting
            self._limit_frame_rate(frame_start)
            
            # Update metrics
            self.performance.update(time.perf_counter() - frame_start)
```

#### config.py - Configuration Management
```python
class ConfigManager:
    """Centralized configuration with caching and performance optimizations"""
    
    def __init__(self, config_path):
        self.config_path = config_path
        self._config = self._load_config()
        self._dirty = False
        
        # Performance optimizations
        self._gamma_table = self._build_gamma_table()
        self._serpentine_map = self._build_serpentine_map()
        self._color_cache = LRUCache(maxsize=1000)
        
        # Settings persistence with debouncing
        self._save_timer = None
        self._save_delay = 5.0  # seconds
        
    @property
    def gamma_table(self):
        """Pre-calculated gamma correction lookup"""
        return self._gamma_table
        
    @property
    def serpentine_map(self):
        """Pre-calculated pixel index mapping"""
        return self._serpentine_map
```

#### performance.py - Performance Monitoring
```python
class PerformanceMonitor:
    """System performance tracking with minimal overhead"""
    
    def __init__(self):
        self.metrics = {
            'fps': RollingAverage(30),
            'frame_time_ms': RollingAverage(30),
            'cpu_percent': RollingAverage(10),
            'memory_mb': RollingAverage(10),
            'dropped_frames': 0
        }
        
        # Background metrics collection
        self._metrics_thread = threading.Thread(
            target=self._collect_system_metrics,
            daemon=True
        )
        self._metrics_thread.start()
```

### 2. Drivers Module (`drivers/`)

#### matrix_driver.py - Abstract Base
```python
class MatrixDriver(ABC):
    """Abstract base class for all matrix drivers"""
    
    @abstractmethod
    def update(self, frame_buffer: FrameBuffer) -> None:
        """Update the physical matrix with frame data"""
        
    @abstractmethod
    def set_brightness(self, brightness: float) -> None:
        """Set global brightness (0.0-1.0)"""
        
    @abstractmethod
    def clear(self) -> None:
        """Clear the matrix"""
        
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources"""
```

#### ws2811_driver.py - WS2811 Implementation
```python
class WS2811Driver(MatrixDriver):
    """Optimized WS2811/NeoPixel driver with double buffering"""
    
    def __init__(self, config):
        self.pixels = neopixel.NeoPixel(
            board.D12,
            config.num_pixels,
            brightness=config.brightness,
            auto_write=False
        )
        
        # Double buffering
        self._front_buffer = self.pixels
        self._back_buffer = [(0, 0, 0)] * config.num_pixels
        
    def update(self, frame_buffer):
        """Update with double buffering"""
        # Render to back buffer
        for i, (r, g, b) in enumerate(frame_buffer):
            # Apply corrections using lookup tables
            r = self.config.gamma_table[r]
            g = self.config.gamma_table[g]
            b = self.config.gamma_table[b]
            self._back_buffer[i] = (r, g, b)
            
        # Swap buffers
        self.pixels[:] = self._back_buffer
        self.pixels.show()
```

#### hub75_driver.py - HUB75 Implementation
```python
class HUB75Driver(MatrixDriver):
    """Hardware-accelerated HUB75 driver with all Zeller optimizations"""
    
    def __init__(self, config):
        # Configure with optimization guide settings from Henner Zeller's library
        options = RGBMatrixOptions()
        options.rows = config.hub75_rows  # 64 for 64x64 panel
        options.cols = config.hub75_cols  # 64 for 64x64 panel
        options.chain_length = config.hub75_chain_length  # 1 for single panel
        options.parallel = config.hub75_parallel  # 1 for single chain
        options.hardware_mapping = 'adafruit-hat'  # Adafruit HAT/Bonnet
        
        # Critical performance settings from optimization guide
        options.gpio_slowdown = 4  # Pi 3B+ optimal value
        options.pwm_bits = 11  # Balance between color depth and speed
        options.pwm_lsb_nanoseconds = 130  # Fine-tune PWM timing
        options.show_refresh_rate = config.show_fps
        
        # Enable hardware PWM if GPIO4-GPIO18 jumper is soldered
        if self._detect_hardware_pwm():
            options.disable_hardware_pulsing = False
            print("Hardware PWM enabled - eliminates flicker!")
            
        # Frame rate limiting for stability
        if config.hub75_limit_refresh > 0:
            options.limit_refresh_rate_hz = config.hub75_limit_refresh
            
        # CPU isolation check (requires isolcpus=3 in boot cmdline)
        if self._check_cpu_isolation():
            print("CPU isolation detected - core 3 dedicated to matrix")
            
        # Additional optimizations
        options.scan_mode = 0  # Progressive scan
        options.row_address_type = 0  # Direct row addressing
        options.multiplexing = 0  # Direct multiplexing
        
        self.matrix = RGBMatrix(options=options)
        self.canvas = self.matrix.CreateFrameCanvas()
        
        # Graphics module for text/shapes (optional)
        try:
            from rgbmatrix import graphics
            self.graphics = graphics
            self.font = graphics.Font()
            # Load default font if available
            self.font.LoadFont("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
        except:
            self.graphics = None
            
    def _detect_hardware_pwm(self):
        """Check if GPIO4-GPIO18 jumper is connected for hardware PWM"""
        try:
            # Check GPIO4 and GPIO18 connection
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(4, GPIO.OUT)
            GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            
            # Test connection
            GPIO.output(4, GPIO.HIGH)
            time.sleep(0.001)
            connected = GPIO.input(18) == GPIO.HIGH
            GPIO.output(4, GPIO.LOW)
            
            GPIO.cleanup([4, 18])
            return connected
        except:
            return False
            
    def _check_cpu_isolation(self):
        """Check if CPU isolation is enabled (isolcpus=3)"""
        try:
            with open('/proc/cmdline', 'r') as f:
                cmdline = f.read()
                return 'isolcpus=3' in cmdline
        except:
            return False
        
    def update(self, frame_buffer):
        """Update using hardware double buffering with SwapOnVSync"""
        # Render to off-screen canvas for flicker-free updates
        for y in range(self.height):
            for x in range(self.width):
                idx = y * self.width + x
                r, g, b = frame_buffer[idx]
                self.canvas.SetPixel(x, y, r, g, b)
                
        # Hardware accelerated buffer swap - key to smooth animation!
        # This is the SwapOnVSync() that ensures tear-free updates
        self.canvas = self.matrix.SwapOnVSync(self.canvas)
        
    def draw_text(self, text, x, y, color=(255, 255, 255)):
        """Draw text using graphics module if available"""
        if self.graphics and self.font:
            text_color = self.graphics.Color(*color)
            return self.graphics.DrawText(self.canvas, self.font, x, y, text_color, text)
        return 0
```

### 3. Animation Module (`animations/`)

#### animation_engine.py
```python
class AnimationEngine:
    """Plugin-based animation system with caching"""
    
    def __init__(self, config):
        self.config = config
        self.animations = {}
        self._current_animation = None
        self._frame_count = 0
        
        # Performance optimizations
        self._animation_cache = {}
        self._math_cache = MathCache()
        
        # Load all animations
        self._load_animations()
        
    def render(self, frame_buffer):
        """Render current animation to frame buffer"""
        if self._current_animation:
            # Pass optimized helpers to animation
            context = AnimationContext(
                config=self.config,
                frame=self._frame_count,
                math_cache=self._math_cache,
                gamma_table=self.config.gamma_table
            )
            
            self._current_animation.animate(frame_buffer, context)
            self._frame_count += 1
```

### 4. Web Module (`web/`)

#### app.py - Unified Web Interface
```python
class LightBoxWebApp:
    """Optimized Flask application with caching and batching"""
    
    def __init__(self, conductor):
        self.conductor = conductor
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, async_mode='threading')
        
        # Performance optimizations
        self._response_cache = TTLCache(maxsize=100, ttl=60)
        self._update_queue = queue.Queue()
        self._batch_timer = None
        
        self._setup_routes()
        self._setup_socketio()
        
    @cached_route('/api/programs')
    def get_programs(self):
        """Cached list of available animations"""
        return jsonify(self.conductor.animation_engine.list_animations())
        
    def run(self, host='0.0.0.0', port=5001):
        """Run with production WSGI server"""
        if self.conductor.config.production_mode:
            # Use gunicorn in production
            return gunicorn_run(self.app, host, port)
        else:
            # Development server
            self.socketio.run(self.app, host=host, port=port)
```

### 5. Hardware Module (`hardware/`)

#### hardware_manager.py
```python
class HardwareManager:
    """Unified hardware interface management"""
    
    def __init__(self, config):
        self.config = config
        self.buttons = None
        self.oled = None
        
        # Initialize hardware with graceful degradation
        self._init_buttons()
        self._init_oled()
        
    def _init_buttons(self):
        """Initialize GPIO buttons with error handling"""
        try:
            from .buttons import ButtonController
            self.buttons = ButtonController(self.config)
        except Exception as e:
            print(f"Buttons unavailable: {e}")
            
    def _init_oled(self):
        """Initialize OLED display with error handling"""
        try:
            from .oled import OLEDDisplay
            self.oled = OLEDDisplay(self.config)
        except Exception as e:
            print(f"OLED unavailable: {e}")
```

### 6. Utils Module (`utils/`)

#### helpers.py - Optimized Helpers
```python
class MathCache:
    """Cached mathematical operations for animations"""
    
    def __init__(self):
        self._sin_cache = {}
        self._cos_cache = {}
        self._hsv_cache = LRUCache(maxsize=500)
        
    def sin(self, angle):
        """Cached sine calculation"""
        key = round(angle, 3)  # 3 decimal precision
        if key not in self._sin_cache:
            self._sin_cache[key] = math.sin(angle)
        return self._sin_cache[key]
        
    def hsv_to_rgb(self, h, s, v):
        """Cached HSV to RGB conversion"""
        key = (round(h, 2), round(s, 2), round(v, 2))
        if key not in self._hsv_cache:
            self._hsv_cache[key] = colorsys.hsv_to_rgb(h, s, v)
        return self._hsv_cache[key]
```

#### frame_buffer.py
```python
class FrameBufferPool:
    """Object pool for frame buffers to reduce allocations"""
    
    def __init__(self, size=3, pixels=4096):
        self._pool = queue.Queue(maxsize=size)
        for _ in range(size):
            self._pool.put(FrameBuffer(pixels))
            
    def acquire(self):
        """Get a frame buffer from pool"""
        try:
            return self._pool.get_nowait()
        except queue.Empty:
            return FrameBuffer(self._pixels)
            
    def release(self, buffer):
        """Return frame buffer to pool"""
        buffer.clear()
        try:
            self._pool.put_nowait(buffer)
        except queue.Full:
            pass  # Discard if pool is full
```

## Key Design Decisions

### 1. Performance Optimizations
- **Lookup Tables**: Gamma correction, serpentine mapping
- **Caching**: Color conversions, math operations, API responses
- **Object Pooling**: Frame buffers to reduce GC pressure
- **Double Buffering**: Both WS2811 and HUB75 implementations
- **Lazy Loading**: Animations and configurations

### 2. Modularity
- **Clear Interfaces**: Abstract base classes for extensibility
- **Dependency Injection**: Configuration passed to all components
- **Plugin Architecture**: Animations as independent modules
- **Graceful Degradation**: Hardware features optional

### 3. Threading Model
- **Main Thread**: Animation loop (highest priority)
- **Web Thread**: Flask/SocketIO server
- **Metrics Thread**: Background performance collection
- **Save Thread**: Debounced configuration persistence

### 4. Error Handling
- **Hardware Failures**: Graceful degradation to simulation
- **Animation Errors**: Fallback to default animation
- **Config Errors**: Use defaults with warnings
- **Network Errors**: Queue updates for retry

## HUB75 System Setup Requirements

### Installing Henner Zeller's RGB Matrix Library

```bash
# Adafruit's installer script (recommended)
curl https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/main/rgb-matrix.sh > rgb-matrix.sh
sudo bash rgb-matrix.sh

# Select "Convenience" mode for Adafruit HAT
# This automatically sets --led-gpio-mapping=adafruit-hat
```

### System Optimizations for HUB75

1. **GPU Memory Reduction** (more RAM for CPU):
   ```bash
   # Add to /boot/config.txt
   gpu_mem=16
   ```

2. **CPU Isolation** (dedicate core 3 to matrix):
   ```bash
   # Add to /boot/cmdline.txt
   isolcpus=3
   ```

3. **Disable Audio** (prevents interference):
   ```bash
   # Add to /boot/config.txt
   dtparam=audio=off
   ```

4. **Hardware PWM Modification**:
   - Solder jumper between GPIO4 and GPIO18 on HAT/Bonnet
   - Eliminates horizontal line artifacts
   - Enables hardware pulse generation

5. **Performance Governor**:
   ```bash
   echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
   ```

### Alternative: Pixil LED Matrix Framework

For rapid prototyping with 75+ built-in animations:
```bash
git clone https://github.com/kklasmeier/pixil-led-matrix.git
cd pixil-led-matrix
pip install -r requirements.txt
sudo python Pixil.py scripts/3D_perspective -q
```

## Configuration Schema

```json
{
  "system": {
    "matrix_type": "hub75|ws2811",
    "target_fps": 30,
    "production_mode": false,
    "enable_metrics": true
  },
  "ws2811": {
    "num_pixels": 100,
    "width": 10,
    "height": 10,
    "serpentine": true,
    "data_pin": "D12"
  },
  "hub75": {
    "rows": 64,
    "cols": 64,
    "chain_length": 1,
    "parallel": 1,
    "pwm_bits": 11,
    "pwm_lsb_nanoseconds": 130,
    "gpio_slowdown": 4,
    "hardware_pwm": "auto",
    "cpu_isolation": true,
    "limit_refresh": 0,
    "scan_mode": 0,
    "row_address_type": 0,
    "multiplexing": 0
  },
  "performance": {
    "enable_caching": true,
    "cache_size": 1000,
    "buffer_pool_size": 3,
    "stats_interval": 10,
    "enable_profiling": false
  },
  "web": {
    "host": "0.0.0.0",
    "port": 5001,
    "enable_cors": false,
    "max_connections": 100,
    "update_batch_ms": 100
  }
}
```

## Migration Path

### Phase 1: Core Infrastructure
1. Create new directory structure
2. Implement base classes
3. Set up configuration system
4. Add performance monitoring

### Phase 2: Driver Migration
1. Port WS2811 driver with optimizations
2. Port HUB75 driver with hardware acceleration
3. Implement driver factory
4. Test both paths

### Phase 3: Feature Integration
1. Migrate animations to new structure
2. Port web interface with optimizations
3. Integrate hardware controls
4. Add system monitoring

### Phase 4: Optimization & Polish
1. Implement all caching strategies
2. Add object pooling
3. Optimize hot paths
4. Performance testing

## Success Metrics

### Performance Targets (Based on Zeller's Benchmarks)

1. **HUB75 on Pi 3B+**:
   - With all optimizations: 30-150 Hz refresh rate
   - Python with double buffering: ~130 Hz achievable
   - Smooth animations without flicker
   - Hardware PWM eliminates artifacts

2. **HUB75 on Pi 4**:
   - Even higher performance (150+ Hz possible)
   - Can drive multiple chained panels
   - Complex animations remain smooth

3. **WS2811 Improvements**:
   - 2x FPS improvement minimum
   - Reduced CPU usage by 40%
   - Consistent frame timing

### System Metrics

1. **Memory**: 50% reduction in allocations
2. **Latency**: <7.7ms frame time for 130 FPS on HUB75
3. **CPU Usage**: Core 3 dedicated to matrix (HUB75)
4. **Reliability**: 99.9% uptime
5. **Code Reduction**: 70% fewer duplicate files

### Quality Indicators

- No horizontal line artifacts (hardware PWM)
- Tear-free animation (SwapOnVSync)
- Consistent color depth (11-bit PWM)
- Stable refresh rate under load