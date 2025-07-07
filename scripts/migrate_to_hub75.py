#!/usr/bin/env python3
"""
Migration script to upgrade LightBox configuration for HUB75 support
Safely migrates existing WS2811 configurations to support both matrix types
"""

import json
import shutil
import sys
import os
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'LB_Interface', 'LightBox'))

def backup_config(config_path):
    """Create a backup of the current configuration"""
    if config_path.exists():
        backup_name = f"settings_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        backup_path = config_path.parent / backup_name
        shutil.copy2(config_path, backup_path)
        print(f"✅ Created backup: {backup_path}")
        return True
    return False

def migrate_config(config_path):
    """Migrate configuration to support HUB75"""
    try:
        # Load existing config
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            print("❌ No existing configuration found")
            config = {}
        
        # Check if already migrated
        if 'hub75_settings' in config:
            print("ℹ️  Configuration already supports HUB75")
            return True
        
        # Add HUB75 settings
        config['hub75_settings'] = {
            "rows": 64,
            "cols": 64,
            "chain_length": 1,
            "parallel": 1,
            "pwm_bits": 11,
            "pwm_lsb_nanoseconds": 130,
            "gpio_slowdown": 4,
            "limit_refresh": 0,
            "hardware_mapping": "adafruit-hat",
            "pixel_mapper": "",
            "panel_type": "",
            "multiplexing": 0,
            "row_address_type": 0,
            "disable_hardware_pulsing": False,
            "show_refresh_rate": False,
            "inverse_colors": False,
            "led_rgb_sequence": "RGB",
            "scan_mode": 0,
            "drop_privileges": True
        }
        
        # Ensure matrix_type is set
        if 'matrix_type' not in config:
            config['matrix_type'] = 'WS2811'  # Default to existing type
            
        # Save migrated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        print("✅ Configuration migrated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def update_imports():
    """Update Python files to use enhanced modules"""
    updates = [
        {
            'file': 'LB_Interface/LightBox/Conductor.py',
            'old': 'from matrix_driver import',
            'new': 'from matrix_driver_enhanced import',
            'description': 'Conductor matrix driver import'
        },
        {
            'file': 'LB_Interface/LightBox/Conductor.py', 
            'old': 'from config import',
            'new': 'from config_enhanced import',
            'description': 'Conductor config import'
        },
        {
            'file': 'LB_Interface/LightBox/webgui/app.py',
            'old': 'from app import',
            'new': 'from app_enhanced import',
            'description': 'Web GUI app import'
        }
    ]
    
    print("\n📝 Updating imports...")
    
    for update in updates:
        file_path = Path(update['file'])
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                if update['old'] in content:
                    # Backup original
                    backup_path = file_path.with_suffix('.bak')
                    shutil.copy2(file_path, backup_path)
                    
                    # Update import
                    content = content.replace(update['old'], update['new'])
                    
                    with open(file_path, 'w') as f:
                        f.write(content)
                        
                    print(f"  ✅ Updated {update['description']}")
                else:
                    print(f"  ℹ️  {update['description']} already updated or not found")
                    
            except Exception as e:
                print(f"  ❌ Failed to update {update['file']}: {e}")
        else:
            print(f"  ⚠️  File not found: {update['file']}")

def verify_dependencies():
    """Check if required dependencies are installed"""
    print("\n🔍 Checking dependencies...")
    
    dependencies_ok = True
    
    # Check for rgbmatrix library
    try:
        import rgbmatrix
        print("  ✅ rgbmatrix library installed")
    except ImportError:
        print("  ❌ rgbmatrix library not found")
        print("     Run: sudo bash install_rgb_matrix.sh")
        dependencies_ok = False
    
    # Check for enhanced modules
    enhanced_modules = [
        'matrix_driver_enhanced.py',
        'config_enhanced.py',
        'webgui/app_enhanced.py'
    ]
    
    for module in enhanced_modules:
        module_path = Path('LB_Interface/LightBox') / module
        if module_path.exists():
            print(f"  ✅ {module} found")
        else:
            print(f"  ❌ {module} not found")
            dependencies_ok = False
    
    return dependencies_ok

def create_test_script():
    """Create a HUB75 test script"""
    test_script = '''#!/usr/bin/env python3
"""
HUB75 Test Script - Verify your panel is working correctly
"""

import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'LB_Interface', 'LightBox'))

from config_enhanced import Config
from matrix_driver_enhanced import create_matrix_driver

def test_hub75():
    """Run HUB75 test patterns"""
    print("🧪 HUB75 Test Script")
    print("=" * 40)
    
    # Create config
    config = Config()
    config.set_matrix_type("HUB75")
    
    # Create driver
    driver = create_matrix_driver(config)
    
    if not driver:
        print("❌ Failed to create driver")
        return
    
    print("✅ Driver initialized")
    
    try:
        # Test 1: Fill colors
        print("\\nTest 1: Fill colors")
        colors = [
            ("Red", 255, 0, 0),
            ("Green", 0, 255, 0),
            ("Blue", 0, 0, 255),
            ("White", 255, 255, 255)
        ]
        
        for name, r, g, b in colors:
            print(f"  Showing {name}...")
            driver.fill(r, g, b)
            driver.show()
            time.sleep(1)
        
        # Test 2: Gradient
        print("\\nTest 2: Gradient pattern")
        for y in range(config.matrix_height):
            for x in range(config.matrix_width):
                r = int(255 * x / config.matrix_width)
                g = int(255 * y / config.matrix_height)
                b = 128
                driver.set_pixel(x, y, r, g, b)
        driver.show()
        time.sleep(2)
        
        # Test 3: Moving pixel
        print("\\nTest 3: Moving pixel")
        driver.clear()
        for i in range(config.matrix_width):
            driver.clear()
            driver.set_pixel(i, config.matrix_height // 2, 255, 255, 255)
            driver.show()
            time.sleep(0.05)
        
        print("\\n✅ All tests completed!")
        
    except KeyboardInterrupt:
        print("\\n⚠️  Test interrupted")
    finally:
        driver.cleanup()
        print("\\nTest finished")

if __name__ == "__main__":
    test_hub75()
'''
    
    test_path = Path('test_hub75.py')
    with open(test_path, 'w') as f:
        f.write(test_script)
    
    # Make executable
    test_path.chmod(0o755)
    
    print(f"\n✅ Created test script: {test_path}")
    print("   Run with: sudo python3 test_hub75.py")

def main():
    """Main migration process"""
    print("🚀 LightBox HUB75 Migration Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path('LightBox').exists():
        print("❌ Please run this script from the LightBox project root")
        sys.exit(1)
    
    # Step 1: Backup configuration
    print("\n📦 Step 1: Backing up configuration...")
    config_path = Path('LightBox/settings.json')
    if not backup_config(config_path):
        print("⚠️  No existing configuration to backup")
    
    # Step 2: Migrate configuration
    print("\n🔧 Step 2: Migrating configuration...")
    if not migrate_config(config_path):
        print("❌ Migration failed")
        sys.exit(1)
    
    # Step 3: Verify dependencies
    if not verify_dependencies():
        print("\n⚠️  Some dependencies are missing")
        print("Please install missing components before proceeding")
    
    # Step 4: Update imports (optional)
    response = input("\n📝 Update imports to use enhanced modules? (y/N): ")
    if response.lower() == 'y':
        update_imports()
    
    # Step 5: Create test script
    print("\n🧪 Creating HUB75 test script...")
    create_test_script()
    
    # Summary
    print("\n" + "=" * 50)
    print("✅ Migration completed!")
    print("\nNext steps:")
    print("1. Install rgbmatrix library if not already installed:")
    print("   sudo bash LightBox/scripts/install_rgb_matrix.sh")
    print("2. Connect your HUB75 panel and power supply")
    print("3. Run the test script:")
    print("   sudo python3 test_hub75.py")
    print("4. Start LightBox and select HUB75 in the web interface")
    print("\nFor detailed setup instructions, see:")
    print("   documentation/HUB75_SETUP_GUIDE.md")

if __name__ == "__main__":
    main()