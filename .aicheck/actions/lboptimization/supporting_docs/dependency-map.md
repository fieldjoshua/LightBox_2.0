# LightBox Component Dependency Map

## Core Component Dependencies

### 1. Main Controllers

#### CosmicLED.py (Original)
```
CosmicLED.py
├── config.py (configuration management)
├── matrix_driver.py (LED control abstraction)
├── hardware/buttons.py (GPIO button input)
├── hardware/oled.py (OLED display)
├── webgui/app.py (Flask web interface)
└── scripts/*.py (animation programs)
```

#### Conductor.py (Enhanced)
```
Conductor.py
├── config.py / config_enhanced.py
├── matrix_driver.py / matrix_driver_enhanced.py
├── hardware/buttons.py
├── hardware/oled.py
├── webgui/app.py / app_hub75_fixed.py
├── scripts/*.py (animations)
└── logging_config.py (enhanced logging)
```

### 2. Matrix Driver Hierarchy

```
MatrixDriver (Abstract Base)
├── WS2811Driver
│   └── adafruit_neopixel library
└── HUB75Driver
    ├── rgbmatrix library (when available)
    └── SimulatedHUB75Driver (fallback)
```

### 3. Configuration System

```
config.py / config_enhanced.py
├── settings.json (persistent storage)
├── presets/*.json (saved configurations)
└── Provides to:
    ├── Conductor/CosmicLED (main settings)
    ├── matrix_driver (hardware config)
    ├── animations (runtime parameters)
    └── webgui (UI state)
```

### 4. Web Interface Dependencies

```
webgui/app.py
├── Flask (web framework)
├── Flask-SocketIO (real-time updates)
├── config.py (settings access)
├── Conductor instance (control interface)
├── static/ (CSS/JS assets)
└── templates/ (HTML templates)
```

### 5. Animation System

```
Animation Scripts (scripts/*.py)
├── Receive from Conductor:
│   ├── pixels[] array
│   ├── config object
│   └── frame counter
└── Return:
    └── Modified pixels[] array
```

### 6. Hardware Integration

```
Hardware Layer
├── GPIO Pins
│   ├── LED Data (GPIO12)
│   ├── Buttons (GPIO 23,24,25,8,7,12)
│   └── I2C (GPIO 2,3)
├── External Power
└── LED Matrix Hardware
    ├── WS2811 (10x10)
    └── HUB75 (64x64)
```

## Critical Dependencies

### External Libraries

1. **WS2811 Path**:
   - adafruit-blinka
   - adafruit-circuitpython-neopixel
   - RPi.GPIO

2. **HUB75 Path**:
   - rgbmatrix (rpi-rgb-led-matrix)
   - Must be compiled/installed separately

3. **Common**:
   - Flask & Flask-SocketIO
   - Pillow (image processing)
   - numpy (calculations)
   - psutil (system monitoring)

### Internal Dependencies

1. **Initialization Order**:
   ```
   1. Load config.py
   2. Initialize matrix_driver
   3. Start hardware interfaces
   4. Launch web server (separate thread)
   5. Begin animation loop
   ```

2. **Data Flow**:
   ```
   User Input → Web API → Config → Conductor → Animation → Matrix Driver → LEDs
                            ↓                      ↓
                       settings.json          Frame Buffer
   ```

3. **Thread Model**:
   - Main Thread: Animation loop
   - Web Thread: Flask server
   - Optional: Hardware monitoring thread

## Consolidation Impact Analysis

### High Risk Dependencies
- **matrix_driver.py** - Core abstraction, all controllers depend on it
- **config.py** - Central settings, breaking changes affect everything
- **rgbmatrix library** - HUB75 support requires this external dependency

### Medium Risk Dependencies
- **webgui/app.py** - User interface, but runs in separate thread
- **Animation scripts** - Many files but simple interface contract
- **Hardware drivers** - Platform specific but well isolated

### Low Risk Dependencies
- **OLED display** - Optional, graceful degradation
- **Button input** - Optional, web interface provides alternative
- **Logging** - Enhanced but not critical

## Recommended Consolidation Order

1. **Start with config system** - Merge config.py and config_enhanced.py
2. **Unify matrix drivers** - Combine best of matrix_driver.py variants
3. **Merge conductors** - Create single Conductor.py with all features
4. **Consolidate web interface** - Merge app.py variants into unified version
5. **Clean up animations** - Remove duplicates, organize by type
6. **Update imports** - Fix all references to use new structure

## Breaking Change Risks

1. **Import Paths** - Moving files will break imports
   - Mitigation: Update systematically with search/replace
   
2. **Configuration Format** - Different config versions may conflict
   - Mitigation: Create migration script for settings.json
   
3. **Animation Interface** - Must maintain animate() signature
   - Mitigation: Keep same function interface
   
4. **Web API** - Endpoints must remain compatible
   - Mitigation: Keep same URL structure

## Testing Requirements

After consolidation, test:
1. Both WS2811 and HUB75 hardware paths
2. All animation scripts still load/run
3. Web interface controls work
4. Settings persist correctly
5. Hardware buttons function
6. Performance metrics unchanged