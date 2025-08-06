"""
Config module for NFe Downloader Pro
Handles all configuration settings and file management
"""

import json
import os
from typing import Dict, Any, Optional


class Config:
    def __init__(self):
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.config_file = os.path.join(self.config_dir, 'config.json')
        self.coordinates_file = os.path.join(self.config_dir, 'coordinates.json')
        self.keys_file = os.path.join(self.config_dir, 'chaves.txt')
        
        # Create directories if they don't exist
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs'), exist_ok=True)
        
        self.default_config = {
            "window_size": "1200x800",
            "theme": "light",
            "auto_save": True,
            "retry_attempts": 3,
            "delay_between_actions": 2.0,
            "captcha_timeout": 30,
            "screenshot_path": os.path.join(self.config_dir, "screenshots"),
            "last_used_coordinates": {},
            "hotkeys": {
                "start_automation": "F9",
                "pause_automation": "F10",
                "stop_automation": "F8",
                "emergency_stop": "Esc"
            }
        }
        
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    merged_config = self.default_config.copy()
                    merged_config.update(loaded_config)
                    return merged_config
        except Exception as e:
            print(f"Error loading config: {e}")
        
        return self.default_config.copy()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value
        if self.config.get("auto_save", True):
            self.save_config()
    
    def load_coordinates(self) -> Dict[str, Dict[str, int]]:
        """Load coordinates from file"""
        try:
            if os.path.exists(self.coordinates_file):
                with open(self.coordinates_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading coordinates: {e}")
        
        return {
            "campo_chave": {"x": 0, "y": 0},
            "captcha": {"x": 0, "y": 0},
            "continuar": {"x": 0, "y": 0},
            "download": {"x": 0, "y": 0},
            "certificado": {"x": 0, "y": 0},
            "nova_consulta": {"x": 0, "y": 0}
        }
    
    def save_coordinates(self, coordinates: Dict[str, Dict[str, int]]):
        """Save coordinates to file"""
        try:
            with open(self.coordinates_file, 'w', encoding='utf-8') as f:
                json.dump(coordinates, f, indent=4)
        except Exception as e:
            print(f"Error saving coordinates: {e}")
    
    def load_keys(self) -> list:
        """Load XML keys from file"""
        try:
            if os.path.exists(self.keys_file):
                with open(self.keys_file, 'r', encoding='utf-8') as f:
                    keys = [line.strip() for line in f.readlines() if line.strip()]
                    return keys
        except Exception as e:
            print(f"Error loading keys: {e}")
        
        return []
    
    def save_keys(self, keys: list):
        """Save XML keys to file"""
        try:
            with open(self.keys_file, 'w', encoding='utf-8') as f:
                for key in keys:
                    if key.strip():
                        f.write(key.strip() + '\n')
        except Exception as e:
            print(f"Error saving keys: {e}")
    
    def get_log_file(self) -> str:
        """Get current log file path"""
        from datetime import datetime
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        timestamp = datetime.now().strftime("%Y%m%d")
        return os.path.join(log_dir, f"nfe_downloader_{timestamp}.log")


# Global config instance
config = Config()