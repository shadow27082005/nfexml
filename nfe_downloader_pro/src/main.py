#!/usr/bin/env python3
"""
NFe Downloader Pro v2.0
Main application entry point

Professional desktop application for automated XML downloads from Receita Federal
Features: GUI interface, coordinate capture, intelligent automation, logging
"""

import sys
import os
import threading
import time
from pathlib import Path

# Add src directory to path for imports
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

try:
    # GUI imports
    import tkinter as tk
    from tkinter import messagebox
    
    # Application modules
    from config import config
    from gui import NFeDownloaderGUI
    from utils import resource_path
    from automation import automation_controller
    
except ImportError as e:
    print(f"❌ Error importing required modules: {e}")
    print("Please install required dependencies with:")
    print("pip install -r requirements.txt")
    sys.exit(1)


class NFEDownloaderApp:
    """Main application class"""
    
    def __init__(self):
        self.app_name = "NFe Downloader Pro"
        self.version = "2.0"
        self.gui = None
        
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are installed"""
        required_modules = [
            'tkinter', 'pyautogui', 'pillow', 'cv2', 'numpy', 
            'requests', 'pynput', 'keyboard'
        ]
        
        missing_modules = []
        
        for module in required_modules:
            try:
                if module == 'cv2':
                    import cv2
                elif module == 'pillow':
                    import PIL
                else:
                    __import__(module)
            except ImportError:
                missing_modules.append(module)
        
        if missing_modules:
            error_msg = f"Missing required modules: {', '.join(missing_modules)}\n\n"
            error_msg += "Please install with:\n"
            error_msg += "pip install -r requirements.txt"
            
            if 'tkinter' not in missing_modules:
                messagebox.showerror("Dependency Error", error_msg)
            else:
                print(f"❌ {error_msg}")
            
            return False
            
        return True
    
    def setup_environment(self):
        """Setup application environment"""
        # Create necessary directories
        dirs_to_create = [
            config.config_dir,
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs'),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets'),
            config.get('screenshot_path', os.path.join(config.config_dir, 'screenshots'))
        ]
        
        for directory in dirs_to_create:
            os.makedirs(directory, exist_ok=True)
        
        # Setup logging
        log_file = config.get_log_file()
        self._setup_logging(log_file)
        
        # Load configuration
        config.load_config()
        
        print(f"✅ {self.app_name} v{self.version} - Environment setup complete")
    
    def _setup_logging(self, log_file: str):
        """Setup application logging"""
        import logging
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # Log startup
        logging.info(f"Starting {self.app_name} v{self.version}")
    
    def run(self):
        """Run the application"""
        try:
            # Check dependencies
            if not self.check_dependencies():
                return 1
            
            # Setup environment
            self.setup_environment()
            
            # Create and run GUI
            print(f"🚀 Starting {self.app_name} GUI...")
            
            self.gui = NFeDownloaderGUI()
            
            # Show startup message
            self._show_startup_message()
            
            # Run main loop
            self.gui.run()
            
            print(f"👋 {self.app_name} closed successfully")
            return 0
            
        except KeyboardInterrupt:
            print(f"\n⏹️ {self.app_name} interrupted by user")
            return 0
            
        except Exception as e:
            error_msg = f"❌ Fatal error in {self.app_name}: {e}"
            print(error_msg)
            
            if self.gui:
                messagebox.showerror("Fatal Error", error_msg)
            
            return 1
    
    def _show_startup_message(self):
        """Show startup message with version info"""
        startup_msg = f"""
🚀 {self.app_name} v{self.version} iniciado com sucesso!

📋 Recursos disponíveis:
• Gerenciamento inteligente de chaves XML
• Sistema de captura de coordenadas
• Automação com detecção de CAPTCHA
• Log detalhado em tempo real
• Controles globais por teclas de atalho

⌨️ Teclas de atalho globais:
• F9 - Iniciar automação
• F10 - Pausar/Retomar
• F8 - Parar automação
• ESC - Parada de emergência

💡 Dica: Configure primeiro as coordenadas na aba "Coordenadas"
antes de iniciar a automação.
"""
        
        # Add to log if GUI is available
        if hasattr(self.gui, 'log_tab'):
            lines = startup_msg.strip().split('\n')
            for line in lines:
                if line.strip():
                    self.gui.log_tab.add_log_entry(line.strip(), "info")


def main():
    """Main entry point"""
    try:
        app = NFEDownloaderApp()
        return app.run()
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        return 1


if __name__ == "__main__":
    # Enable high DPI awareness on Windows
    if sys.platform == "win32":
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
    
    # Run application
    exit_code = main()
    sys.exit(exit_code)