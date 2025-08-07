"""
Automation module for NFe Downloader Pro
Handles all automation logic with PyAutoGUI and intelligent CAPTCHA detection
"""

import time
import threading
import os
import cv2
import numpy as np
from typing import Dict, List, Optional, Callable, Tuple
from datetime import datetime
import pyautogui
from PIL import Image
import keyboard
from pynput import mouse, keyboard as pynput_keyboard

from config import config
from utils import (
    validate_nfe_key, safe_click, safe_type, clear_field_and_type,
    wait_for_element, detect_captcha_type, take_screenshot, get_timestamp
)
from smart_detector import SmartButtonDetector


class AutomationStatus:
    """Automation status enumeration"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class CaptchaDetector:
    """Advanced CAPTCHA detection and handling"""
    
    def __init__(self):
        self.captcha_templates = {}
        self.load_captcha_templates()
        
    def load_captcha_templates(self):
        """Load CAPTCHA templates for pattern recognition"""
        templates_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'captcha_templates')
        if os.path.exists(templates_dir):
            for filename in os.listdir(templates_dir):
                if filename.endswith(('.png', '.jpg', '.jpeg')):
                    template_path = os.path.join(templates_dir, filename)
                    self.captcha_templates[filename] = cv2.imread(template_path)
    
    def detect_captcha_type(self, region: tuple) -> str:
        """Detect CAPTCHA type in given region"""
        try:
            screenshot = take_screenshot(region)
            screenshot_np = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Analyze image characteristics
            gray = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)
            
            # Check for text patterns (simple CAPTCHA)
            text_score = self._analyze_text_patterns(gray)
            
            # Check for image patterns (complex CAPTCHA)
            image_score = self._analyze_image_patterns(screenshot_np)
            
            if text_score > image_score:
                return "text"
            elif image_score > 0.3:
                return "image"
            else:
                return "unknown"
                
        except Exception as e:
            print(f"Error detecting CAPTCHA type: {e}")
            return "unknown"
    
    def _analyze_text_patterns(self, gray_image) -> float:
        """Analyze image for text patterns"""
        # Edge detection for text
        edges = cv2.Canny(gray_image, 50, 150)
        
        # Count edge density
        edge_density = np.sum(edges) / (edges.shape[0] * edges.shape[1])
        
        return min(edge_density / 50.0, 1.0)  # Normalize to 0-1
    
    def _analyze_image_patterns(self, color_image) -> float:
        """Analyze image for complex patterns"""
        # Color diversity
        unique_colors = len(np.unique(color_image.reshape(-1, color_image.shape[2]), axis=0))
        color_score = min(unique_colors / 1000.0, 1.0)
        
        # Texture analysis using Local Binary Pattern
        gray = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
        texture_score = self._calculate_texture_score(gray)
        
        return max(color_score, texture_score)
    
    def _calculate_texture_score(self, gray_image) -> float:
        """Calculate texture complexity score"""
        # Simple texture analysis using standard deviation
        return min(np.std(gray_image) / 50.0, 1.0)
    
    def solve_simple_captcha(self, region: tuple) -> Optional[str]:
        """Attempt to solve simple text CAPTCHA"""
        try:
            screenshot = take_screenshot(region)
            
            # Convert to OpenCV format
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Preprocess image
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Noise reduction and enhancement
            denoised = cv2.fastNlMeansDenoising(gray)
            enhanced = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # OCR would go here (requires tesseract)
            # For now, return None to indicate manual intervention needed
            return None
            
        except Exception as e:
            print(f"Error solving CAPTCHA: {e}")
            return None


class NFEAutomation:
    """Main automation class for NFe downloads"""
    
    def __init__(self, log_callback: Optional[Callable[[str, str], None]] = None):
        self.status = AutomationStatus.IDLE
        self.log_callback = log_callback
        self.captcha_detector = CaptchaDetector()
        self.smart_detector = SmartButtonDetector(logger=self._log_for_detector)
        
        # Configuration
        self.coordinates = {}
        self.keys_queue = []
        self.current_key_index = 0
        self.processed_keys = []
        self.failed_keys = []
        
        # Control flags
        self.running = False
        self.paused = False
        self.stop_requested = False
        
        # Statistics
        self.stats = {
            'total_keys': 0,
            'processed': 0,
            'success': 0,
            'failed': 0,
            'captcha_solved': 0,
            'start_time': None,
            'end_time': None
        }
        
        # Setup global hotkeys
        self.setup_hotkeys()
        
        # PyAutoGUI configuration
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = config.get('delay_between_actions', 2.0)
    
    def setup_hotkeys(self):
        """Setup global hotkeys for control"""
        try:
            hotkeys = config.get('hotkeys', {})
            
            keyboard.add_hotkey(hotkeys.get('start_automation', 'F9'), self.start_automation)
            keyboard.add_hotkey(hotkeys.get('pause_automation', 'F10'), self.toggle_pause)
            keyboard.add_hotkey(hotkeys.get('stop_automation', 'F8'), self.stop_automation)
            keyboard.add_hotkey(hotkeys.get('emergency_stop', 'esc'), self.emergency_stop)
            
        except Exception as e:
            self.log(f"Error setting up hotkeys: {e}", "error")
    
    def log(self, message: str, level: str = "info"):
        """Log message with timestamp"""
        timestamp = get_timestamp()
        formatted_message = f"[{timestamp}] {message}"
        
        if self.log_callback:
            self.log_callback(formatted_message, level)
        else:
            print(formatted_message)
    
    def _log_for_detector(self, message: str):
        """Log wrapper for smart detector"""
        self.log(f"🤖 {message}", "info")
    
    def load_configuration(self, coordinates: Dict, keys: List[str]):
        """Load automation configuration"""
        self.coordinates = coordinates.copy()
        self.keys_queue = keys.copy()
        self.stats['total_keys'] = len(keys)
        
        self.log(f"Configuration loaded: {len(keys)} keys, {len(coordinates)} coordinates")
    
    def auto_detect_coordinates(self) -> Dict[str, Optional[Tuple[int, int]]]:
        """Auto-detect coordinates using smart detector"""
        self.log("🤖 Iniciando detecção automática inteligente...", "info")
        
        try:
            # Usa o detector inteligente
            detected_coordinates = self.smart_detector.smart_detect_all_elements()
            
            # Atualiza coordenadas internas
            self.coordinates.update(detected_coordinates)
            
            # Log resultados
            found_count = sum(1 for pos in detected_coordinates.values() if pos is not None)
            total_count = len(detected_coordinates)
            
            if found_count >= 4:  # Mínimo para automação funcionar
                self.log(f"✅ Detecção bem-sucedida: {found_count}/{total_count} elementos encontrados", "success")
            elif found_count >= 2:
                self.log(f"⚠️ Detecção parcial: {found_count}/{total_count} elementos encontrados", "warning")
            else:
                self.log(f"❌ Detecção falhou: apenas {found_count}/{total_count} elementos encontrados", "error")
            
            return detected_coordinates
            
        except Exception as e:
            self.log(f"❌ Erro na detecção automática: {e}", "error")
            return {}
    
    def save_detection_debug_image(self, filename: str = "detection_debug.png"):
        """Salva imagem de debug da detecção"""
        try:
            self.smart_detector.save_detection_image(self.coordinates, filename)
            self.log(f"🖼️ Imagem de debug salva: {filename}", "info")
        except Exception as e:
            self.log(f"❌ Erro ao salvar imagem de debug: {e}", "error")
    
    def validate_configuration(self) -> bool:
        """Validate automation configuration"""
        required_coords = ['campo_chave', 'captcha', 'continuar', 'download', 'certificado', 'nova_consulta']
        
        # Check coordinates
        for coord in required_coords:
            if coord not in self.coordinates:
                self.log(f"Missing coordinate: {coord}", "error")
                return False
            
            if self.coordinates[coord].get('x', 0) == 0 or self.coordinates[coord].get('y', 0) == 0:
                self.log(f"Invalid coordinate for {coord}: (0, 0)", "error")
                return False
        
        # Check keys
        if not self.keys_queue:
            self.log("No keys to process", "error")
            return False
        
        valid_keys = [k for k in self.keys_queue if validate_nfe_key(k)]
        if len(valid_keys) != len(self.keys_queue):
            self.log(f"Found {len(self.keys_queue) - len(valid_keys)} invalid keys", "warning")
        
        return True
    
    def start_automation(self):
        """Start the automation process"""
        if self.status == AutomationStatus.RUNNING:
            self.log("Automation already running", "warning")
            return
        
        if not self.validate_configuration():
            self.log("Configuration validation failed", "error")
            return
        
        self.status = AutomationStatus.RUNNING
        self.running = True
        self.paused = False
        self.stop_requested = False
        self.stats['start_time'] = datetime.now()
        
        self.log("🚀 Starting NFe automation", "info")
        
        # Start automation in separate thread
        automation_thread = threading.Thread(target=self._automation_loop, daemon=True)
        automation_thread.start()
    
    def toggle_pause(self):
        """Toggle pause state"""
        if self.status == AutomationStatus.RUNNING:
            self.paused = not self.paused
            status = "paused" if self.paused else "resumed"
            self.status = AutomationStatus.PAUSED if self.paused else AutomationStatus.RUNNING
            self.log(f"⏸️ Automation {status}", "info")
    
    def stop_automation(self):
        """Stop the automation gracefully"""
        self.stop_requested = True
        self.log("🛑 Stop requested - finishing current key", "info")
    
    def emergency_stop(self):
        """Emergency stop - immediate halt"""
        self.running = False
        self.stop_requested = True
        self.status = AutomationStatus.STOPPED
        self.log("🚨 EMERGENCY STOP - Automation halted immediately", "error")
    
    def _automation_loop(self):
        """Main automation loop"""
        try:
            while self.running and self.current_key_index < len(self.keys_queue) and not self.stop_requested:
                # Check pause state
                while self.paused and not self.stop_requested:
                    time.sleep(0.1)
                
                if self.stop_requested:
                    break
                
                current_key = self.keys_queue[self.current_key_index]
                self.log(f"Processing key {self.current_key_index + 1}/{len(self.keys_queue)}: {current_key[:8]}...", "info")
                
                # Process single key
                success = self._process_single_key(current_key)
                
                if success:
                    self.stats['success'] += 1
                    self.processed_keys.append(current_key)
                    self.log(f"✅ Key processed successfully: {current_key[:8]}...", "success")
                else:
                    self.stats['failed'] += 1
                    self.failed_keys.append(current_key)
                    self.log(f"❌ Key processing failed: {current_key[:8]}...", "error")
                
                self.stats['processed'] += 1
                self.current_key_index += 1
                
                # Delay between keys
                if not self.stop_requested:
                    time.sleep(config.get('delay_between_actions', 2.0))
            
            # Automation completed
            self._finish_automation()
            
        except Exception as e:
            self.log(f"❌ Automation error: {e}", "error")
            self.status = AutomationStatus.ERROR
        
    def _process_single_key(self, key: str) -> bool:
        """Process a single NFe key"""
        try:
            # Step 1: Enter key in field
            if not self._enter_key(key):
                return False
            
            # Step 2: Handle CAPTCHA
            if not self._handle_captcha():
                return False
            
            # Step 3: Click continue
            if not self._click_continue():
                return False
            
            # Step 4: Handle certificate selection
            if not self._handle_certificate():
                return False
            
            # Step 5: Download XML
            if not self._download_xml():
                return False
            
            # Step 6: Prepare for next key
            if not self._prepare_next():
                return False
            
            return True
            
        except Exception as e:
            self.log(f"Error processing key {key}: {e}", "error")
            return False
    
    def _enter_key(self, key: str) -> bool:
        """Enter NFe key in the field"""
        try:
            coord = self.coordinates['campo_chave']
            x, y = coord['x'], coord['y']
            
            self.log(f"Entering key in field at ({x}, {y})", "info")
            
            return clear_field_and_type(x, y, key)
            
        except Exception as e:
            self.log(f"Error entering key: {e}", "error")
            return False
    
    def _handle_captcha(self) -> bool:
        """Handle CAPTCHA solving"""
        try:
            coord = self.coordinates['captcha']
            x, y = coord['x'], coord['y']
            
            # Define CAPTCHA region (approximate)
            region = (x - 50, y - 25, 100, 50)
            
            # Detect CAPTCHA type
            captcha_type = self.captcha_detector.detect_captcha_type(region)
            self.log(f"Detected CAPTCHA type: {captcha_type}", "info")
            
            if captcha_type == "text":
                # Try to solve automatically
                solution = self.captcha_detector.solve_simple_captcha(region)
                if solution:
                    safe_click(x, y)
                    safe_type(solution)
                    self.stats['captcha_solved'] += 1
                    self.log(f"CAPTCHA solved automatically: {solution}", "success")
                    return True
            
            # Manual intervention required
            self.log("⏳ Manual CAPTCHA intervention required", "warning")
            self._wait_for_manual_captcha()
            return True
            
        except Exception as e:
            self.log(f"Error handling CAPTCHA: {e}", "error")
            return False
    
    def _wait_for_manual_captcha(self, timeout: int = 60):
        """Wait for manual CAPTCHA solving"""
        self.log(f"Waiting {timeout}s for manual CAPTCHA solving...", "info")
        
        start_time = time.time()
        while time.time() - start_time < timeout and not self.stop_requested:
            if self.paused:
                time.sleep(0.1)
                continue
            
            # Check if user pressed a key indicating completion
            time.sleep(0.5)
        
        self.log("Manual CAPTCHA wait completed", "info")
    
    def _click_continue(self) -> bool:
        """Click continue button"""
        try:
            coord = self.coordinates['continuar']
            x, y = coord['x'], coord['y']
            
            self.log(f"Clicking continue button at ({x}, {y})", "info")
            return safe_click(x, y, delay=3.0)  # Longer delay for page load
            
        except Exception as e:
            self.log(f"Error clicking continue: {e}", "error")
            return False
    
    def _handle_certificate(self) -> bool:
        """Handle certificate selection if needed"""
        try:
            coord = self.coordinates['certificado']
            x, y = coord['x'], coord['y']
            
            # Wait a bit and check if certificate selection is needed
            time.sleep(2)
            
            # Try clicking certificate button (might not always be visible)
            self.log(f"Checking certificate button at ({x}, {y})", "info")
            safe_click(x, y, delay=1.0)
            
            return True
            
        except Exception as e:
            self.log(f"Error handling certificate: {e}", "error")
            return False
    
    def _download_xml(self) -> bool:
        """Download the XML file"""
        try:
            coord = self.coordinates['download']
            x, y = coord['x'], coord['y']
            
            # Wait for page to load
            time.sleep(3)
            
            self.log(f"Clicking download button at ({x}, {y})", "info")
            return safe_click(x, y, delay=3.0)  # Wait for download
            
        except Exception as e:
            self.log(f"Error downloading XML: {e}", "error")
            return False
    
    def _prepare_next(self) -> bool:
        """Prepare for next key"""
        try:
            coord = self.coordinates['nova_consulta']
            x, y = coord['x'], coord['y']
            
            # Wait for download to complete
            time.sleep(2)
            
            self.log(f"Clicking new query button at ({x}, {y})", "info")
            return safe_click(x, y, delay=2.0)
            
        except Exception as e:
            self.log(f"Error preparing next: {e}", "error")
            return False
    
    def _finish_automation(self):
        """Finish automation and show summary"""
        self.running = False
        self.status = AutomationStatus.IDLE
        self.stats['end_time'] = datetime.now()
        
        # Calculate duration
        if self.stats['start_time']:
            duration = self.stats['end_time'] - self.stats['start_time']
            duration_str = str(duration).split('.')[0]  # Remove microseconds
        else:
            duration_str = "Unknown"
        
        # Log summary
        self.log("🏁 Automation completed!", "success")
        self.log(f"📊 Summary:", "info")
        self.log(f"   • Total keys: {self.stats['total_keys']}", "info")
        self.log(f"   • Processed: {self.stats['processed']}", "info")
        self.log(f"   • Successful: {self.stats['success']}", "info")
        self.log(f"   • Failed: {self.stats['failed']}", "info")
        self.log(f"   • CAPTCHAs solved: {self.stats['captcha_solved']}", "info")
        self.log(f"   • Duration: {duration_str}", "info")
        
        if self.stats['success'] > 0:
            success_rate = (self.stats['success'] / self.stats['processed']) * 100
            self.log(f"   • Success rate: {success_rate:.1f}%", "info")
    
    def get_statistics(self) -> Dict:
        """Get current automation statistics"""
        stats = self.stats.copy()
        stats['status'] = self.status
        stats['current_key_index'] = self.current_key_index
        stats['total_keys'] = len(self.keys_queue)
        
        if stats['start_time'] and self.status == AutomationStatus.RUNNING:
            elapsed = datetime.now() - stats['start_time']
            stats['elapsed_time'] = str(elapsed).split('.')[0]
        
        return stats
    
    def get_failed_keys(self) -> List[str]:
        """Get list of failed keys"""
        return self.failed_keys.copy()
    
    def reset_statistics(self):
        """Reset automation statistics"""
        self.stats = {
            'total_keys': len(self.keys_queue),
            'processed': 0,
            'success': 0,
            'failed': 0,
            'captcha_solved': 0,
            'start_time': None,
            'end_time': None
        }
        self.current_key_index = 0
        self.processed_keys.clear()
        self.failed_keys.clear()


class AutomationController:
    """High-level controller for automation"""
    
    def __init__(self, log_callback: Optional[Callable[[str, str], None]] = None):
        self.automation = NFEAutomation(log_callback)
        self.log_callback = log_callback
        
    def setup(self, coordinates: Dict, keys: List[str]):
        """Setup automation with coordinates and keys"""
        self.automation.load_configuration(coordinates, keys)
        
    def start(self):
        """Start automation"""
        self.automation.start_automation()
        
    def pause(self):
        """Pause/resume automation"""
        self.automation.toggle_pause()
        
    def stop(self):
        """Stop automation"""
        self.automation.stop_automation()
        
    def emergency_stop(self):
        """Emergency stop"""
        self.automation.emergency_stop()
        
    def get_status(self) -> str:
        """Get current status"""
        return self.automation.status
        
    def get_statistics(self) -> Dict:
        """Get statistics"""
        return self.automation.get_statistics()
        
    def get_failed_keys(self) -> List[str]:
        """Get failed keys"""
        return self.automation.get_failed_keys()


# Global automation controller
automation_controller = AutomationController()