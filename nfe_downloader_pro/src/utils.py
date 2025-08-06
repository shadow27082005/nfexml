"""
Utility functions for NFe Downloader Pro
Common functions used across the application
"""

import os
import sys
import time
import re
import threading
from datetime import datetime
from typing import Optional, Tuple, List
import cv2
import numpy as np
import pyautogui
from PIL import Image, ImageTk


def validate_nfe_key(key: str) -> bool:
    """Validate NFe key format (44 digits)"""
    if not key:
        return False
    
    # Remove spaces and special characters
    clean_key = re.sub(r'[^0-9]', '', key)
    
    # Check if it has exactly 44 digits
    return len(clean_key) == 44 and clean_key.isdigit()


def format_nfe_key(key: str) -> str:
    """Format NFe key to standard format"""
    clean_key = re.sub(r'[^0-9]', '', key)
    if len(clean_key) == 44:
        return clean_key
    return key


def get_screen_size() -> Tuple[int, int]:
    """Get screen dimensions"""
    return pyautogui.size()


def take_screenshot(region: Optional[Tuple[int, int, int, int]] = None) -> Image.Image:
    """Take screenshot of screen or region"""
    if region:
        return pyautogui.screenshot(region=region)
    return pyautogui.screenshot()


def find_image_on_screen(template_path: str, confidence: float = 0.8) -> Optional[Tuple[int, int]]:
    """Find image template on screen using OpenCV"""
    try:
        # Take screenshot
        screenshot = pyautogui.screenshot()
        screenshot_np = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # Load template
        template = cv2.imread(template_path)
        if template is None:
            return None
        
        # Template matching
        result = cv2.matchTemplate(screenshot_np, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= confidence)
        
        if len(locations[0]) > 0:
            # Return first match
            y, x = locations[0][0], locations[1][0]
            return (x, y)
            
    except Exception as e:
        print(f"Error finding image: {e}")
    
    return None


def safe_click(x: int, y: int, delay: float = 1.0) -> bool:
    """Safely click at coordinates with error handling"""
    try:
        # Move mouse to position
        pyautogui.moveTo(x, y, duration=0.5)
        time.sleep(0.2)
        
        # Click
        pyautogui.click(x, y)
        time.sleep(delay)
        
        return True
    except Exception as e:
        print(f"Error clicking at ({x}, {y}): {e}")
        return False


def safe_type(text: str, delay: float = 0.1) -> bool:
    """Safely type text with error handling"""
    try:
        pyautogui.typewrite(text, interval=delay)
        return True
    except Exception as e:
        print(f"Error typing text: {e}")
        return False


def clear_field_and_type(x: int, y: int, text: str, delay: float = 1.0) -> bool:
    """Clear field and type new text"""
    try:
        # Click on field
        if not safe_click(x, y, 0.5):
            return False
        
        # Select all and delete
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(0.2)
        
        # Type new text
        return safe_type(text, 0.05)
        
    except Exception as e:
        print(f"Error clearing field and typing: {e}")
        return False


def wait_for_element(x: int, y: int, timeout: int = 10, check_interval: float = 0.5) -> bool:
    """Wait for element to be clickable at coordinates"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            # Take small screenshot around the coordinates
            region = (max(0, x-50), max(0, y-50), 100, 100)
            screenshot = take_screenshot(region)
            
            # If we can take screenshot, element might be there
            return True
            
        except Exception:
            pass
        
        time.sleep(check_interval)
    
    return False


def detect_captcha_type(captcha_region: Tuple[int, int, int, int]) -> str:
    """Detect type of CAPTCHA (text or image)"""
    try:
        screenshot = take_screenshot(captcha_region)
        screenshot_np = np.array(screenshot)
        
        # Simple heuristic: if there are many colors, it's likely an image CAPTCHA
        unique_colors = len(np.unique(screenshot_np.reshape(-1, screenshot_np.shape[2]), axis=0))
        
        if unique_colors > 100:
            return "image"
        else:
            return "text"
            
    except Exception:
        return "unknown"


def get_timestamp() -> str:
    """Get formatted timestamp"""
    return datetime.now().strftime("%H:%M:%S")


def get_date_timestamp() -> str:
    """Get formatted date and time"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


def create_circular_progress(canvas, x: int, y: int, radius: int, percentage: float, color: str = "#4CAF50"):
    """Create circular progress indicator on canvas"""
    # Clear previous
    canvas.delete("progress")
    
    # Background circle
    canvas.create_oval(
        x - radius, y - radius, x + radius, y + radius,
        outline="#E0E0E0", width=8, tags="progress"
    )
    
    # Progress arc
    if percentage > 0:
        extent = int(360 * (percentage / 100))
        canvas.create_arc(
            x - radius, y - radius, x + radius, y + radius,
            start=90, extent=-extent, outline=color, width=8,
            style="arc", tags="progress"
        )
    
    # Percentage text
    canvas.create_text(
        x, y, text=f"{int(percentage)}%",
        font=("Arial", 12, "bold"), fill=color, tags="progress"
    )


def run_in_thread(func, *args, **kwargs):
    """Run function in separate thread"""
    thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
    thread.start()
    return thread


def debounce(wait_time: float):
    """Debounce decorator to prevent rapid successive calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not hasattr(wrapper, 'last_called'):
                wrapper.last_called = 0
            
            now = time.time()
            if now - wrapper.last_called >= wait_time:
                wrapper.last_called = now
                return func(*args, **kwargs)
                
        return wrapper
    return decorator


class MouseCapture:
    """Helper class to capture mouse coordinates"""
    
    def __init__(self, callback=None):
        self.callback = callback
        self.capturing = False
        
    def start_capture(self):
        """Start capturing mouse position"""
        self.capturing = True
        
    def stop_capture(self):
        """Stop capturing"""
        self.capturing = False
        
    def get_current_position(self) -> Tuple[int, int]:
        """Get current mouse position"""
        return pyautogui.position()


# Global mouse capture instance
mouse_capture = MouseCapture()