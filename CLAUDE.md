# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## AICheck Integration

Claude should follow the rules specified in `.aicheck/RULES.md` and use AICheck commands:

- `./aicheck action new ActionName` - Create a new action 
- `./aicheck action set ActionName` - Set the current active action
- `./aicheck action complete [ActionName]` - Complete an action with dependency verification
- `./aicheck exec` - Toggle exec mode for system maintenance
- `./aicheck status` - Show the current action status
- `./aicheck dependency add NAME VERSION JUSTIFICATION [ACTION]` - Add external dependency
- `./aicheck dependency internal DEP_ACTION ACTION TYPE [DESCRIPTION]` - Add internal dependency
- `./aicheck todo` - Manage todo lists (your claude to do)

## Project Rules

Claude should follow the rules specified in `.aicheck/RULES.md` with focus on documentation-first approach and adherence to language-specific best practices.

## AICheck Procedures

1. Always check the current action with `./aicheck status` at the start of a session
2. Follow the active action's plan when implementing
3. Create tests before implementation code
4. Document all Claude interactions in supporting_docs/claude-interactions/
5. Only work within the scope of the active action
6. Document all dependencies before completing an action
7. Immediately respond to git hook suggestions before continuing work

## Development Commands

- **Run LED controller**: `sudo python3 LightBox/CosmicLED.py` (requires root for GPIO access)
- **Enhanced version**: `sudo python3 LightBox/LB_Interface/LightBox/Conductor.py`
- **Optimized version**: `sudo python3 lightbox.py` (latest, recommended)
- **Simulation mode**: `python3 LightBox/run_simulation.py` (no hardware required)
- **Web interface**: Access at <http://localhost:5001> when running
- **Install dependencies**: `pip install -r LightBox/requirements.txt` or `pip install -r requirements-optimized.txt`
- **Testing**: `pytest` or `python3 test_optimized.py`
- **Hardware test**: `python3 LightBox/scripts/matrix_test.py` to verify LED wiring
- **Diagnostics**: `python3 LightBox/diagnose_gpio.py` for GPIO troubleshooting
- **SSH to production**: `ssh fieldjoshua@192.168.0.222` (Pi Zero W) or `ssh joshuafield@192.168.0.98` (Pi 3B+)

### HUB75 Specific Commands

- **Install RGB Matrix Library**: `sudo bash LightBox/scripts/install_rgb_matrix.sh`
- **Migrate to HUB75**: `python3 LightBox/scripts/migrate_to_hub75.py`
- **Test HUB75 Panel**: `sudo python3 test_hub75.py`
- **Run HUB75 Tests**: `python3 -m pytest tests/test_hub75_driver.py tests/test_hub75_integration.py`
- **Transfer to Pi**: `python3 -m http.server 8000` (then wget from Pi)

## Architecture Overview

### Core Components

- **CosmicLED.py**: Original animation engine that manages LED strip control
- **Conductor.py**: Enhanced animation engine with improved architecture (LB_Interface/LightBox/)
- **lightbox.py**: Optimized entry point using modular architecture (core/, drivers/, web/)
- **config.py**: Configuration management with settings persistence, color palettes, and matrix coordinate mapping
- **webgui/app.py**: Flask web interface providing REST API for remote control and real-time monitoring
- **matrix_driver.py**: Low-level LED matrix driver with error handling

### Animation System

The project uses a plugin-based animation system:

- Animation programs are Python files in `LightBox/scripts/` or `animations/` with an `animate(pixels, config, frame)` function
- Programs receive pixel array, configuration object, and frame counter
- Built-in cosmic animation provides default flowing color patterns
- Dynamic program loading allows hot-swapping animations without restart

### Hardware Integration

- **LED Matrix**: 10x10 WS2811/NeoPixel matrix with serpentine wiring support OR 64x64 HUB75 panel
- **LED Data Pin**: GPIO12 (Pin 32) for WS2811
- **Power Requirements**: 5V external supply (60W+ recommended for full brightness)
- **GPIO Buttons**: Physical controls for mode switching, brightness, and speed (hardware/buttons.py)
  - Mode: GPIO23, Brightness: GPIO24/25, Speed: GPIO8/7, Preset: GPIO12
- **OLED Display**: Status display integration (hardware/oled.py)
- **Supported Hardware**: 
  - Pi Zero W: Best for string lights (100 LEDs)
  - Pi 3B+: Optimized for HUB75 panels (4096 pixels)
  - Pi 4: Maximum performance

### Configuration Management

- **settings.json**: Persistent storage for user preferences
- **Matrix mapping**: xy_to_index() handles serpentine vs progressive wiring patterns
- **Color palettes**: Predefined color schemes with interpolation support
- **Presets**: Save/load complete configuration states

### Web API Architecture

Flask app provides RESTful endpoints:

- `/api/status` - System status and current configuration
- `/api/config` - Update animation parameters
- `/api/program` - Switch animation programs
- `/api/upload` - Upload new animation scripts
- `/api/palette` - Color palette management
- `/api/presets` - Configuration preset management

## Dependency Management

When adding external libraries or frameworks:

1. Document with `./aicheck dependency add NAME VERSION JUSTIFICATION`
2. Include specific version requirements
3. Provide clear justification for adding the dependency

When creating dependencies between actions:

1. Document with `./aicheck dependency internal DEP_ACTION ACTION TYPE DESCRIPTION`
2. Specify the type of dependency (data, function, service, etc.)
3. Add detailed description of the dependency relationship

## Claude Workflow

When the user requests work:

1. Check if it fits within the current action (if not, suggest creating a new action)
2. Consult the action plan for guidance
3. Follow test-driven development practices
4. Document your thought process
5. Document all dependencies
6. Implement according to the plan
7. Verify your implementation against the success criteria

## Development Notes

- Animation programs must handle frame-based timing and use config parameters for customization
- Hardware components require root privileges for GPIO access on Raspberry Pi
- Web interface runs on separate thread to avoid blocking LED animation loop
- Matrix coordinate system uses (0,0) at top-left with configurable wiring patterns
- All settings changes are persisted to settings.json automatically
- Three project versions exist: original (CosmicLED.py), enhanced (LB_Interface/Conductor.py), optimized (lightbox.py)
- When developing animations, use `config.xy_to_index(x, y)` for coordinate mapping
- Production systems run at 192.168.0.222:5001 (Pi Zero W) and 192.168.0.98:5001 (Pi 3B+)

## Performance Optimization Notes

The optimized version includes significant performance improvements:

- **Gamma correction lookup tables**: 40% performance improvement by eliminating pow() calculations
- **Serpentine index caching**: Pre-calculated index mappings for LED addressing
- **HSV to RGB caching**: LRU cache for color conversions
- **Frame buffer pooling**: Reduced memory allocations
- **Platform-specific optimizations**: Automatic detection and optimization for Pi Zero W vs Pi 3B+/4

### Platform-Specific Settings

**Pi Zero W (String Lights)**:
- Target: 20-25 FPS
- Use minimal dependencies
- Disable heavy features like numpy if not needed
- Consider using original CosmicLED.py for simplicity

**Pi 3B+ (Matrices/HUB75)**:
- Target: 60 FPS (WS2811) or 130+ Hz (HUB75)
- Enable CPU isolation: Add `isolcpus=3` to `/boot/cmdline.txt`
- For HUB75: Hardware PWM via GPIO4-GPIO18 jumper
- Set performance governor for all CPU cores

## Current Known Issues

- Platform detection may incorrectly identify Pi 3B+ as Pi Zero W (use settings.json override)
- Import errors if running without proper virtual environment activation
- Some tests may pass in simulation but fail on actual hardware
- HUB75 may flicker without hardware PWM modification