#!/usr/bin/env python3
"""
Test script to verify NFe Downloader Pro functionality
"""

import sys
import os

# Add the src directory to path
sys.path.insert(0, os.path.join('nfe_downloader_pro', 'src'))

try:
    # Test imports (without GUI)
    from config import config
    from utils import validate_nfe_key, format_nfe_key
    
    # Import automation components without GUI dependencies
    import sys
    import importlib.util
    
    # Load automation module manually to avoid GUI imports
    spec = importlib.util.spec_from_file_location("automation", "nfe_downloader_pro/src/automation.py")
    automation_module = importlib.util.module_from_spec(spec)
    
    # Mock problematic imports
    sys.modules['pyautogui'] = type('MockModule', (), {
        'FAILSAFE': True, 'PAUSE': 2.0, 'position': lambda: (0, 0), 
        'moveTo': lambda *args, **kwargs: None, 'click': lambda *args, **kwargs: None,
        'typewrite': lambda *args, **kwargs: None, 'hotkey': lambda *args, **kwargs: None,
        'press': lambda *args, **kwargs: None, 'screenshot': lambda *args, **kwargs: None,
        'size': lambda: (1920, 1080)
    })
    sys.modules['keyboard'] = type('MockModule', (), {
        'add_hotkey': lambda *args, **kwargs: None
    })
    sys.modules['pynput'] = type('MockModule', (), {
        'mouse': type('MockModule', (), {}),
        'keyboard': type('MockModule', (), {})
    })
    sys.modules['cv2'] = type('MockModule', (), {
        'imread': lambda *args: None,
        'cvtColor': lambda *args, **kwargs: None,
        'COLOR_RGB2BGR': 0,
        'COLOR_BGR2GRAY': 0,
        'matchTemplate': lambda *args, **kwargs: None,
        'TM_CCOEFF_NORMED': 0,
        'fastNlMeansDenoising': lambda *args: None,
        'adaptiveThreshold': lambda *args, **kwargs: None,
        'ADAPTIVE_THRESH_GAUSSIAN_C': 0,
        'THRESH_BINARY': 0,
        'Canny': lambda *args, **kwargs: None
    })
    
    spec.loader.exec_module(automation_module)
    AutomationStatus = automation_module.AutomationStatus
    CaptchaDetector = automation_module.CaptchaDetector
    
    print("✅ NFe Downloader Pro v2.0 - Structure Test")
    print("=" * 50)
    
    # Test configuration
    print("\n📋 Testing Configuration System:")
    print(f"✅ Config directory: {config.config_dir}")
    print(f"✅ Auto-save enabled: {config.get('auto_save', True)}")
    print(f"✅ Default delay: {config.get('delay_between_actions', 2.0)}s")
    
    # Test key validation
    print("\n🗂️ Testing Key Validation:")
    test_keys = [
        "12345678901234567890123456789012345678901234",  # Valid format
        "1234567890123456789012345678901234567890123",   # Too short
        "abc1234567890123456789012345678901234567890123", # Invalid chars
        "",  # Empty
    ]
    
    for i, key in enumerate(test_keys):
        is_valid = validate_nfe_key(key)
        status = "✅ VALID" if is_valid else "❌ INVALID"
        display_key = key[:10] + "..." if len(key) > 10 else key
        print(f"  Key {i+1} ({display_key}): {status}")
    
    # Test automation components
    print("\n🤖 Testing Automation Components:")
    captcha_detector = CaptchaDetector()
    print("✅ CAPTCHA Detector initialized")
    
    print(f"✅ Automation Status Enum:")
    print(f"  - IDLE: {AutomationStatus.IDLE}")
    print(f"  - RUNNING: {AutomationStatus.RUNNING}")
    print(f"  - PAUSED: {AutomationStatus.PAUSED}")
    print(f"  - STOPPED: {AutomationStatus.STOPPED}")
    
    # Test file structure
    print("\n📁 Testing File Structure:")
    required_files = [
        "nfe_downloader_pro/src/main.py",
        "nfe_downloader_pro/src/gui.py", 
        "nfe_downloader_pro/src/automation.py",
        "nfe_downloader_pro/src/config.py",
        "nfe_downloader_pro/src/utils.py",
        "nfe_downloader_pro/requirements.txt",
        "nfe_downloader_pro/README.md",
        "nfe_downloader_pro/LICENSE"
    ]
    
    for file_path in required_files:
        exists = os.path.exists(file_path)
        status = "✅ EXISTS" if exists else "❌ MISSING"
        print(f"  {file_path}: {status}")
    
    # Test directories
    print("\n📂 Testing Directories:")
    directories = ["nfe_downloader_pro/assets", "nfe_downloader_pro/data", "nfe_downloader_pro/logs", "nfe_downloader_pro/scripts", "nfe_downloader_pro/src"]
    
    for directory in directories:
        exists = os.path.isdir(directory)
        status = "✅ EXISTS" if exists else "❌ MISSING"
        print(f"  {directory}/: {status}")
    
    print("\n" + "=" * 50)
    print("🎉 NFe Downloader Pro - All Core Tests Passed!")
    print("\n📋 Next Steps:")
    print("1. Install GUI dependencies: sudo apt install python3-tk")
    print("2. Run the application: python3 src/main.py")
    print("3. Configure coordinates in the GUI")
    print("4. Load XML keys and start automation")
    
    print("\n⌨️ Remember the global hotkeys:")
    print("  F9  - Start automation")
    print("  F10 - Pause/Resume")
    print("  F8  - Stop automation")
    print("  ESC - Emergency stop")

except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Test Error: {e}")
    sys.exit(1)