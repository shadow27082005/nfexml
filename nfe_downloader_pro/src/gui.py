"""
GUI module for NFe Downloader Pro
Modern interface with 4 tabs: Chaves XML, Coordenadas, Automação, Log
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
import threading
import time
from typing import Dict, List, Optional, Callable
from datetime import datetime

from config import config
from utils import (
    validate_nfe_key, format_nfe_key, get_timestamp, 
    run_in_thread, MouseCapture, create_circular_progress
)
from automation import automation_controller, AutomationStatus


class ModernButton(tk.Button):
    """Custom modern button with hover effects"""
    
    def __init__(self, parent, **kwargs):
        # Default styling
        default_config = {
            'relief': 'flat',
            'borderwidth': 0,
            'font': ('Segoe UI', 10, 'bold'),
            'cursor': 'hand2',
            'pady': 8,
            'padx': 20
        }
        
        # Update with user config
        default_config.update(kwargs)
        
        super().__init__(parent, **default_config)
        
        # Store colors
        self.default_bg = default_config.get('bg', '#4CAF50')
        self.hover_bg = self._darken_color(self.default_bg)
        
        # Bind hover events
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        
    def _darken_color(self, color: str) -> str:
        """Darken color for hover effect"""
        if color == '#4CAF50':
            return '#45a049'
        elif color == '#f44336':
            return '#da190b'
        elif color == '#FF9800':
            return '#e68900'
        elif color == '#2196F3':
            return '#0b7dda'
        return color
        
    def _on_enter(self, e):
        """Mouse enter event"""
        self.config(bg=self.hover_bg)
        
    def _on_leave(self, e):
        """Mouse leave event"""
        self.config(bg=self.default_bg)


class StatusBar(tk.Frame):
    """Modern status bar"""
    
    def __init__(self, parent):
        super().__init__(parent, height=30, bg='#f0f0f0')
        self.pack_propagate(False)
        
        # Status label
        self.status_label = tk.Label(
            self, text="Pronto", bg='#f0f0f0',
            font=('Segoe UI', 9), anchor='w'
        )
        self.status_label.pack(side='left', padx=10, pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self, mode='indeterminate', length=150
        )
        self.progress.pack(side='right', padx=10, pady=5)
        
    def set_status(self, text: str, working: bool = False):
        """Update status"""
        self.status_label.config(text=f"{get_timestamp()} - {text}")
        
        if working:
            self.progress.start()
        else:
            self.progress.stop()


class ChavesTab(tk.Frame):
    """Tab for XML keys management"""
    
    def __init__(self, parent, status_callback: Callable[[str, bool], None]):
        super().__init__(parent, bg='white')
        self.status_callback = status_callback
        self.keys = []
        
        self._create_widgets()
        self._load_keys()
        
    def _create_widgets(self):
        """Create tab widgets"""
        # Title
        title_frame = tk.Frame(self, bg='white', height=60)
        title_frame.pack(fill='x', padx=20, pady=10)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, text="🗂️ Gerenciamento de Chaves XML",
            font=('Segoe UI', 16, 'bold'), bg='white', fg='#333'
        )
        title_label.pack(anchor='w')
        
        subtitle_label = tk.Label(
            title_frame, text="Cole as chaves NFe (uma por linha) ou carregue de arquivo",
            font=('Segoe UI', 10), bg='white', fg='#666'
        )
        subtitle_label.pack(anchor='w')
        
        # Main content frame
        content_frame = tk.Frame(self, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20)
        
        # Left frame - Input
        left_frame = tk.LabelFrame(
            content_frame, text=" 📝 Entrada de Chaves ", 
            font=('Segoe UI', 11, 'bold'), bg='white', fg='#333'
        )
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Text area for keys
        self.keys_text = scrolledtext.ScrolledText(
            left_frame, height=15, font=('Consolas', 10),
            wrap='word', relief='solid', borderwidth=1
        )
        self.keys_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Buttons frame
        buttons_frame = tk.Frame(left_frame, bg='white')
        buttons_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        ModernButton(
            buttons_frame, text="📁 Carregar Arquivo",
            bg='#2196F3', fg='white',
            command=self._load_from_file
        ).pack(side='left', padx=(0, 5))
        
        ModernButton(
            buttons_frame, text="💾 Salvar Arquivo",
            bg='#4CAF50', fg='white',
            command=self._save_to_file
        ).pack(side='left', padx=5)
        
        ModernButton(
            buttons_frame, text="🔄 Atualizar Lista",
            bg='#FF9800', fg='white',
            command=self._process_keys
        ).pack(side='left', padx=5)
        
        ModernButton(
            buttons_frame, text="🗑️ Limpar Tudo",
            bg='#f44336', fg='white',
            command=self._clear_all
        ).pack(side='left', padx=5)
        
        # Right frame - Status
        right_frame = tk.LabelFrame(
            content_frame, text=" 📊 Status das Chaves ",
            font=('Segoe UI', 11, 'bold'), bg='white', fg='#333'
        )
        right_frame.pack(side='right', fill='y', padx=(10, 0))
        
        # Statistics frame
        stats_frame = tk.Frame(right_frame, bg='white')
        stats_frame.pack(fill='x', padx=10, pady=10)
        
        # Total keys
        self.total_label = tk.Label(
            stats_frame, text="Total: 0", font=('Segoe UI', 12, 'bold'),
            bg='white', fg='#333'
        )
        self.total_label.pack(anchor='w')
        
        # Valid keys
        self.valid_label = tk.Label(
            stats_frame, text="Válidas: 0", font=('Segoe UI', 10),
            bg='white', fg='#4CAF50'
        )
        self.valid_label.pack(anchor='w')
        
        # Invalid keys
        self.invalid_label = tk.Label(
            stats_frame, text="Inválidas: 0", font=('Segoe UI', 10),
            bg='white', fg='#f44336'
        )
        self.invalid_label.pack(anchor='w')
        
        # Progress circle
        self.canvas = tk.Canvas(right_frame, width=120, height=120, bg='white', highlightthickness=0)
        self.canvas.pack(pady=20)
        
        # Keys list
        list_frame = tk.Frame(right_frame, bg='white')
        list_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        tk.Label(
            list_frame, text="Chaves Válidas:", font=('Segoe UI', 10, 'bold'),
            bg='white', fg='#333'
        ).pack(anchor='w')
        
        self.keys_listbox = tk.Listbox(
            list_frame, height=10, font=('Consolas', 8),
            relief='solid', borderwidth=1
        )
        self.keys_listbox.pack(fill='both', expand=True)
        
        # Bind text change event
        self.keys_text.bind('<KeyRelease>', lambda e: self._on_text_change())
        
    def _load_keys(self):
        """Load keys from config"""
        keys = config.load_keys()
        self.keys_text.delete(1.0, tk.END)
        self.keys_text.insert(1.0, '\n'.join(keys))
        self._process_keys()
        
    def _save_keys(self):
        """Save keys to config"""
        config.save_keys(self.keys)
        
    def _process_keys(self):
        """Process and validate keys"""
        text_content = self.keys_text.get(1.0, tk.END).strip()
        lines = [line.strip() for line in text_content.split('\n') if line.strip()]
        
        self.keys = []
        valid_keys = []
        invalid_count = 0
        
        for line in lines:
            if validate_nfe_key(line):
                formatted_key = format_nfe_key(line)
                if formatted_key not in self.keys:
                    self.keys.append(formatted_key)
                    valid_keys.append(formatted_key)
            else:
                if line:  # Don't count empty lines
                    invalid_count += 1
        
        # Update statistics
        total = len(lines)
        valid = len(valid_keys)
        invalid = invalid_count
        
        self.total_label.config(text=f"Total: {total}")
        self.valid_label.config(text=f"Válidas: {valid}")
        self.invalid_label.config(text=f"Inválidas: {invalid}")
        
        # Update progress circle
        percentage = (valid / total * 100) if total > 0 else 0
        create_circular_progress(self.canvas, 60, 60, 40, percentage)
        
        # Update keys listbox
        self.keys_listbox.delete(0, tk.END)
        for key in valid_keys:
            display_key = f"{key[:4]}...{key[-4:]}"
            self.keys_listbox.insert(tk.END, display_key)
        
        # Save valid keys
        self._save_keys()
        
        self.status_callback(f"Processadas {valid} chaves válidas de {total} total", False)
        
    def _on_text_change(self):
        """Handle text change with debouncing"""
        # Cancel previous timer if exists
        if hasattr(self, '_timer'):
            self.after_cancel(self._timer)
        
        # Set new timer
        self._timer = self.after(1000, self._process_keys)  # 1 second delay
        
    def _load_from_file(self):
        """Load keys from file"""
        file_path = filedialog.askopenfilename(
            title="Carregar Chaves XML",
            filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                current_content = self.keys_text.get(1.0, tk.END).strip()
                if current_content:
                    content = current_content + '\n' + content
                
                self.keys_text.delete(1.0, tk.END)
                self.keys_text.insert(1.0, content)
                self._process_keys()
                
                self.status_callback(f"Arquivo carregado: {os.path.basename(file_path)}", False)
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar arquivo: {e}")
        
    def _save_to_file(self):
        """Save keys to file"""
        if not self.keys:
            messagebox.showwarning("Aviso", "Nenhuma chave válida para salvar")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Salvar Chaves XML",
            defaultextension=".txt",
            filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(self.keys))
                
                self.status_callback(f"Arquivo salvo: {os.path.basename(file_path)}", False)
                messagebox.showinfo("Sucesso", f"Chaves salvas em {file_path}")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar arquivo: {e}")
        
    def _clear_all(self):
        """Clear all keys"""
        if messagebox.askyesno("Confirmar", "Deseja limpar todas as chaves?"):
            self.keys_text.delete(1.0, tk.END)
            self.keys = []
            self._process_keys()
            self.status_callback("Todas as chaves foram removidas", False)
    
    def get_keys(self) -> List[str]:
        """Get valid keys list"""
        return self.keys.copy()
    
    def remove_key(self, key: str):
        """Remove a specific key"""
        if key in self.keys:
            self.keys.remove(key)
            
            # Update text area
            current_text = self.keys_text.get(1.0, tk.END)
            lines = current_text.split('\n')
            new_lines = [line for line in lines if format_nfe_key(line.strip()) != key]
            
            self.keys_text.delete(1.0, tk.END)
            self.keys_text.insert(1.0, '\n'.join(new_lines))
            
            self._process_keys()


class CoordenadasTab(tk.Frame):
    """Tab for coordinates configuration"""
    
    def __init__(self, parent, status_callback: Callable[[str, bool], None]):
        super().__init__(parent, bg='white')
        self.status_callback = status_callback
        self.coordinates = {}
        self.capturing = False
        self.current_capture = None
        
        self._create_widgets()
        self._load_coordinates()
        
    def _create_widgets(self):
        """Create tab widgets"""
        import os
        # Detecta se estamos no WSL
        is_wsl = os.path.exists('/proc/version') and 'microsoft' in open('/proc/version').read().lower()
        
        # Title
        title_frame = tk.Frame(self, bg='white', height=60)
        title_frame.pack(fill='x', padx=20, pady=10)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, text="🎯 Configuração de Coordenadas",
            font=('Segoe UI', 16, 'bold'), bg='white', fg='#333'
        )
        title_label.pack(anchor='w')
        
        subtitle_label = tk.Label(
            title_frame, text="Capture as coordenadas dos elementos na tela para automação",
            font=('Segoe UI', 10), bg='white', fg='#666'
        )
        subtitle_label.pack(anchor='w')
        
        # Instructions frame
        instructions_frame = tk.LabelFrame(
            self, text=" 📋 Instruções ",
            font=('Segoe UI', 11, 'bold'), bg='white', fg='#333'
        )
        instructions_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        if is_wsl:
            instructions_text = """
📋 MODO MANUAL (WSL):
1. Clique no botão "🌐 Abrir Site da NFe" abaixo
2. No navegador Windows que abrir, carregue a página da NFe
3. Volte para este aplicativo no WSL
4. Para cada elemento, clique "Capturar", depois vá até o navegador Windows
5. Posicione o mouse sobre o elemento no Windows e pressione ESPAÇO
6. Repita para todos os elementos necessários
7. Salve as configurações

⚠️ IMPORTANTE: Mantenha ambas as janelas visíveis (app WSL + navegador Windows)
            """.strip()
        else:
            instructions_text = """
1. Abra o site da Receita Federal em seu navegador
2. Navegue até a página de consulta de NFe
3. Clique em "Capturar" para cada elemento
4. Posicione o mouse sobre o elemento e pressione ESPAÇO
5. Verifique se as coordenadas estão corretas
6. Salve as configurações antes de usar a automação
            """.strip()
        
        tk.Label(
            instructions_frame, text=instructions_text,
            font=('Segoe UI', 10), bg='white', fg='#333',
            justify='left'
        ).pack(padx=10, pady=10, anchor='w')
        
        # Auto-detect frame
        detect_frame = tk.LabelFrame(
            self, text=" 🤖 Detecção Automática Inteligente ",
            font=('Segoe UI', 11, 'bold'), bg='white', fg='#333'
        )
        detect_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        # is_wsl já foi definido no início do método
        
        if is_wsl:
            detect_text = "⚠️ WSL DETECTADO: A detecção automática não funciona no WSL pois o navegador abre no Windows. Use a captura manual abaixo:"
        else:
            detect_text = "Use a detecção automática para encontrar os elementos automaticamente na tela:"
        tk.Label(
            detect_frame, text=detect_text,
            font=('Segoe UI', 10), bg='white', fg='#333',
            justify='left'
        ).pack(padx=10, pady=(10, 5), anchor='w')
        
        # Buttons frame inside detect_frame
        detect_buttons_frame = tk.Frame(detect_frame, bg='white')
        detect_buttons_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        # Desabilita detecção automática no WSL
        if is_wsl:
            self.auto_detect_btn = ModernButton(
                detect_buttons_frame, text="🚫 Não Funciona no WSL",
                bg='#666', fg='white', font=('Segoe UI', 11, 'bold'),
                state='disabled'
            )
        else:
            self.auto_detect_btn = ModernButton(
                detect_buttons_frame, text="🤖 Detectar Automaticamente",
                bg='#9b59b6', fg='white', font=('Segoe UI', 11, 'bold'),
                command=self._auto_detect_coordinates
            )
        self.auto_detect_btn.pack(side='left', padx=(0, 10))
        
        ModernButton(
            detect_buttons_frame, text="🌐 Abrir Site da NFe",
            bg='#2196F3', fg='white', font=('Segoe UI', 10),
            command=self._open_nfe_site
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            detect_buttons_frame, text="🖼️ Salvar Debug",
            bg='#f39c12', fg='white', font=('Segoe UI', 9),
            command=self._save_debug_image
        ).pack(side='left')
        
        # Coordinates frame
        coords_frame = tk.LabelFrame(
            self, text=" 🎯 Elementos para Captura ",
            font=('Segoe UI', 11, 'bold'), bg='white', fg='#333'
        )
        coords_frame.pack(fill='both', expand=True, padx=20, pady=(0, 10))
        
        # Create coordinate inputs
        self.coord_entries = {}
        elements = [
            ("campo_chave", "Campo de Chave NFe", "📝"),
            ("captcha", "Campo CAPTCHA", "🔒"),
            ("continuar", "Botão Continuar", "▶️"),
            ("download", "Botão Download", "💾"),
            ("certificado", "Botão Certificado Digital", "🔐"),
            ("nova_consulta", "Botão Nova Consulta", "🔄")
        ]
        
        for i, (key, label, icon) in enumerate(elements):
            row = i // 2
            col = i % 2
            
            element_frame = tk.Frame(coords_frame, bg='white', relief='solid', borderwidth=1)
            element_frame.grid(row=row, column=col, padx=10, pady=5, sticky='ew')
            
            # Configure grid weights
            coords_frame.grid_columnconfigure(col, weight=1)
            
            # Element info
            info_frame = tk.Frame(element_frame, bg='white')
            info_frame.pack(fill='x', padx=10, pady=(10, 5))
            
            tk.Label(
                info_frame, text=f"{icon} {label}",
                font=('Segoe UI', 11, 'bold'), bg='white', fg='#333'
            ).pack(anchor='w')
            
            # Coordinates display
            coord_frame = tk.Frame(element_frame, bg='white')
            coord_frame.pack(fill='x', padx=10, pady=5)
            
            tk.Label(
                coord_frame, text="X:", font=('Segoe UI', 10),
                bg='white', fg='#333'
            ).pack(side='left')
            
            x_entry = tk.Entry(
                coord_frame, width=8, font=('Consolas', 10),
                relief='solid', borderwidth=1
            )
            x_entry.pack(side='left', padx=(5, 10))
            
            tk.Label(
                coord_frame, text="Y:", font=('Segoe UI', 10),
                bg='white', fg='#333'
            ).pack(side='left')
            
            y_entry = tk.Entry(
                coord_frame, width=8, font=('Consolas', 10),
                relief='solid', borderwidth=1
            )
            y_entry.pack(side='left', padx=(5, 10))
            
            # Buttons
            button_frame = tk.Frame(element_frame, bg='white')
            button_frame.pack(fill='x', padx=10, pady=(0, 10))
            
            capture_btn = ModernButton(
                button_frame, text="📹 Capturar",
                bg='#2196F3', fg='white',
                command=lambda k=key: self._start_capture(k)
            )
            capture_btn.pack(side='left', padx=(0, 5))
            
            test_btn = ModernButton(
                button_frame, text="🧪 Testar",
                bg='#4CAF50', fg='white',
                command=lambda k=key: self._test_coordinate(k)
            )
            test_btn.pack(side='left')
            
            self.coord_entries[key] = {
                'x': x_entry,
                'y': y_entry,
                'capture_btn': capture_btn,
                'test_btn': test_btn
            }
        
        # Bottom buttons
        bottom_frame = tk.Frame(self, bg='white')
        bottom_frame.pack(fill='x', padx=20, pady=10)
        
        ModernButton(
            bottom_frame, text="💾 Salvar Coordenadas",
            bg='#4CAF50', fg='white',
            command=self._save_coordinates
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            bottom_frame, text="📁 Carregar Coordenadas",
            bg='#2196F3', fg='white',
            command=self._load_coordinates_dialog
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            bottom_frame, text="🔄 Resetar Tudo",
            bg='#f44336', fg='white',
            command=self._reset_coordinates
        ).pack(side='left')
        
        # Status label
        self.capture_status = tk.Label(
            bottom_frame, text="", font=('Segoe UI', 10, 'italic'),
            bg='white', fg='#666'
        )
        self.capture_status.pack(side='right')
        
        # Bind global keys for capture
        self.bind_all('<space>', self._capture_position)
        self.bind_all('<Escape>', self._cancel_capture)
        
    def _load_coordinates(self):
        """Load coordinates from config"""
        self.coordinates = config.load_coordinates()
        self._update_entries()
        
    def _update_entries(self):
        """Update coordinate entries with loaded values"""
        for key, entries in self.coord_entries.items():
            if key in self.coordinates:
                entries['x'].delete(0, tk.END)
                entries['x'].insert(0, str(self.coordinates[key]['x']))
                entries['y'].delete(0, tk.END)
                entries['y'].insert(0, str(self.coordinates[key]['y']))
        
    def _start_capture(self, element_key: str):
        """Start coordinate capture for element"""
        if self.capturing:
            self._cancel_capture()
            return
            
        self.capturing = True
        self.current_capture = element_key
        
        # Update button text
        self.coord_entries[element_key]['capture_btn'].config(text="⏹️ Parar")
        
        # Show status
        self.capture_status.config(
            text=f"Posicione o mouse e pressione ESPAÇO para capturar '{element_key}'",
            fg='#FF9800'
        )
        
        self.status_callback(f"Capturando coordenadas para {element_key}...", True)
        
        # Change cursor
        self.config(cursor='crosshair')
        
    def _capture_position(self, event):
        """Capture current mouse position"""
        if not self.capturing or not self.current_capture:
            return
            
        try:
            import pyautogui
            x, y = pyautogui.position()
            
            # Update entries
            element_key = self.current_capture
            self.coord_entries[element_key]['x'].delete(0, tk.END)
            self.coord_entries[element_key]['x'].insert(0, str(x))
            self.coord_entries[element_key]['y'].delete(0, tk.END)
            self.coord_entries[element_key]['y'].insert(0, str(y))
            
            # Update coordinates dict
            if element_key not in self.coordinates:
                self.coordinates[element_key] = {}
            self.coordinates[element_key]['x'] = x
            self.coordinates[element_key]['y'] = y
            
            self.status_callback(f"Coordenadas capturadas para {element_key}: ({x}, {y})", False)
            
            # Visual feedback
            self.capture_status.config(
                text=f"✅ Capturado: {element_key} em ({x}, {y})",
                fg='#4CAF50'
            )
            
            # Auto-save
            config.save_coordinates(self.coordinates)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao capturar coordenadas: {e}")
        
        finally:
            self._cancel_capture()
    
    def _cancel_capture(self, event=None):
        """Cancel coordinate capture"""
        if not self.capturing:
            return
            
        self.capturing = False
        
        if self.current_capture:
            # Reset button text
            self.coord_entries[self.current_capture]['capture_btn'].config(text="📹 Capturar")
            self.current_capture = None
        
        # Reset cursor
        self.config(cursor='')
        
        # Clear status
        self.capture_status.config(text="")
        
        self.status_callback("Captura cancelada", False)
    
    def _test_coordinate(self, element_key: str):
        """Test coordinate by moving mouse there"""
        if element_key not in self.coordinates:
            messagebox.showwarning("Aviso", f"Coordenadas não definidas para {element_key}")
            return
        
        try:
            import pyautogui
            x = self.coordinates[element_key]['x']
            y = self.coordinates[element_key]['y']
            
            # Move mouse to position
            pyautogui.moveTo(x, y, duration=1)
            
            self.status_callback(f"Mouse movido para {element_key}: ({x}, {y})", False)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao testar coordenadas: {e}")
    
    def _save_coordinates(self):
        """Save coordinates manually"""
        try:
            # Update coordinates from entries
            for key, entries in self.coord_entries.items():
                x_text = entries['x'].get().strip()
                y_text = entries['y'].get().strip()
                
                if x_text and y_text:
                    if key not in self.coordinates:
                        self.coordinates[key] = {}
                    self.coordinates[key]['x'] = int(x_text)
                    self.coordinates[key]['y'] = int(y_text)
            
            config.save_coordinates(self.coordinates)
            messagebox.showinfo("Sucesso", "Coordenadas salvas com sucesso!")
            self.status_callback("Coordenadas salvas", False)
            
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira valores numéricos válidos")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar coordenadas: {e}")
    
    def _load_coordinates_dialog(self):
        """Load coordinates from file dialog"""
        file_path = filedialog.askopenfilename(
            title="Carregar Coordenadas",
            filetypes=[("Arquivos JSON", "*.json"), ("Todos os Arquivos", "*.*")]
        )
        
        if file_path:
            try:
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.coordinates = json.load(f)
                
                self._update_entries()
                messagebox.showinfo("Sucesso", "Coordenadas carregadas com sucesso!")
                self.status_callback(f"Coordenadas carregadas de {os.path.basename(file_path)}", False)
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar coordenadas: {e}")
    
    def _reset_coordinates(self):
        """Reset all coordinates"""
        if messagebox.askyesno("Confirmar", "Deseja resetar todas as coordenadas?"):
            self.coordinates = {
                key: {"x": 0, "y": 0} for key in self.coord_entries.keys()
            }
            self._update_entries()
            config.save_coordinates(self.coordinates)
            self.status_callback("Coordenadas resetadas", False)
    
    def get_coordinates(self) -> Dict[str, Dict[str, int]]:
        """Get current coordinates"""
        return self.coordinates.copy()
    
    def _auto_detect_coordinates(self):
        """Execute automatic coordinate detection"""
        self.auto_detect_btn.config(state='disabled', text="🔍 Detectando...")
        
        def detect():
            try:
                # Execute detection
                detected_coords = automation_controller.automation.auto_detect_coordinates()
                
                # Update UI in main thread
                self.after(0, lambda: self._finish_auto_detection(detected_coords))
                
            except Exception as e:
                self.after(0, lambda: self._auto_detect_error(str(e)))
        
        # Run in separate thread
        threading.Thread(target=detect, daemon=True).start()
    
    def _finish_auto_detection(self, detected_coords):
        """Finish auto-detection process"""
        self.auto_detect_btn.config(state='normal', text="🤖 Detectar Automaticamente")
        
        # Update coordinates with detected values
        for key, pos in detected_coords.items():
            if pos is not None and key in self.coord_entries:
                x, y = pos
                self.coord_entries[key]['x'].delete(0, tk.END)
                self.coord_entries[key]['x'].insert(0, str(x))
                self.coord_entries[key]['y'].delete(0, tk.END)
                self.coord_entries[key]['y'].insert(0, str(y))
                
                # Update coordinates dict
                if key not in self.coordinates:
                    self.coordinates[key] = {}
                self.coordinates[key]['x'] = x
                self.coordinates[key]['y'] = y
        
        # Save automatically
        config.save_coordinates(self.coordinates)
        
        found_count = sum(1 for pos in detected_coords.values() if pos is not None)
        total_count = len(detected_coords)
        
        if found_count >= 4:
            messagebox.showinfo(
                "Detecção Automática", 
                f"✅ Detecção bem-sucedida!\n\n"
                f"Encontrados: {found_count}/{total_count} elementos\n\n"
                f"As coordenadas foram atualizadas automaticamente."
            )
            self.status_callback("Detecção automática concluída com sucesso", False)
        elif found_count >= 2:
            messagebox.showwarning(
                "Detecção Parcial",
                f"⚠️ Detecção parcial\n\n"
                f"Encontrados: {found_count}/{total_count} elementos\n\n"
                f"Verifique se a página da NFe está carregada corretamente."
            )
            self.status_callback("Detecção parcial - alguns elementos não encontrados", False)
        else:
            messagebox.showerror(
                "Detecção Falhou",
                f"❌ Detecção falhou\n\n"
                f"Apenas {found_count}/{total_count} elementos encontrados\n\n"
                f"Abra a página da NFe no navegador e tente novamente."
            )
            self.status_callback("Detecção automática falhou", False)
    
    def _auto_detect_error(self, error):
        """Handle auto-detection error"""
        self.auto_detect_btn.config(state='normal', text="🤖 Detectar Automaticamente")
        messagebox.showerror("Erro na Detecção", f"Erro durante detecção automática:\n\n{error}")
        self.status_callback("Erro na detecção automática", False)
    
    def _save_debug_image(self):
        """Save debug image with detected elements"""
        try:
            filename = f"detection_debug_{datetime.now().strftime('%H%M%S')}.png"
            automation_controller.automation.save_detection_debug_image(filename)
            
            messagebox.showinfo(
                "Imagem Debug", 
                f"✅ Imagem de debug salva!\n\n"
                f"Arquivo: {filename}\n\n"
                f"Use esta imagem para verificar quais elementos foram detectados."
            )
            self.status_callback(f"Imagem de debug salva: {filename}", False)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar imagem de debug:\n\n{e}")
            self.status_callback("Erro ao salvar imagem de debug", False)
    
    def _open_nfe_site(self):
        """Open NFe website in browser"""
        try:
            import subprocess
            import os
            
            url = "https://www.nfe.fazenda.gov.br/portal/consultaRecaptcha.aspx?tipoConsulta=resumo&tipoConteudo=7PhJ+gAVw2g%3d"
            
            # Try WSL specific method first
            if os.path.exists('/proc/version') and 'microsoft' in open('/proc/version').read().lower():
                # WSL environment - use PowerShell to open URL
                subprocess.run(['powershell.exe', '-c', f'Start-Process "{url}"'], check=True)
            else:
                # Linux environment - try xdg-open
                subprocess.run(['xdg-open', url], check=True)
                
            self.status_callback("Site da NFe aberto no navegador", False)
        except Exception as e:
            # Fallback to webbrowser
            try:
                import webbrowser
                webbrowser.open(url)
                self.status_callback("Site da NFe aberto no navegador", False)
            except Exception as e2:
                messagebox.showwarning(
                    "Link da NFe", 
                    f"Não foi possível abrir automaticamente.\n\n"
                    f"Copie este link e cole no seu navegador:\n\n"
                    f"{url}"
                )
                # Copy to clipboard if possible
                try:
                    import pyperclip
                    pyperclip.copy(url)
                    self.status_callback("Link copiado para a área de transferência", False)
                except:
                    self.status_callback("Erro ao abrir site - use o link manualmente", False)


class AutomacaoTab(tk.Frame):
    """Tab for automation control"""
    
    def __init__(self, parent, status_callback: Callable[[str, bool], None], 
                 get_keys_func: Callable[[], List[str]], 
                 get_coords_func: Callable[[], Dict]):
        super().__init__(parent, bg='white')
        self.status_callback = status_callback
        self.get_keys_func = get_keys_func
        self.get_coords_func = get_coords_func
        self.automation_running = False
        
        self._create_widgets()
        self._update_status_display()
        
        # Start status update timer
        self._start_status_timer()
        
    def _create_widgets(self):
        """Create tab widgets"""
        # Title
        title_frame = tk.Frame(self, bg='white', height=60)
        title_frame.pack(fill='x', padx=20, pady=10)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, text="🤖 Sistema de Automação",
            font=('Segoe UI', 16, 'bold'), bg='white', fg='#333'
        )
        title_label.pack(anchor='w')
        
        subtitle_label = tk.Label(
            title_frame, text="Controle inteligente para download automatizado de XMLs",
            font=('Segoe UI', 10), bg='white', fg='#666'
        )
        subtitle_label.pack(anchor='w')
        
        # Main content
        content_frame = tk.Frame(self, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20)
        
        # Left side - Controls
        left_frame = tk.LabelFrame(
            content_frame, text=" 🎮 Controles ",
            font=('Segoe UI', 11, 'bold'), bg='white', fg='#333'
        )
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Configuration status
        config_frame = tk.Frame(left_frame, bg='white')
        config_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(
            config_frame, text="📋 Status da Configuração:",
            font=('Segoe UI', 11, 'bold'), bg='white', fg='#333'
        ).pack(anchor='w')
        
        self.keys_status = tk.Label(
            config_frame, text="• Chaves: 0 carregadas",
            font=('Segoe UI', 10), bg='white', fg='#666'
        )
        self.keys_status.pack(anchor='w', padx=10)
        
        self.coords_status = tk.Label(
            config_frame, text="• Coordenadas: 0/6 configuradas",
            font=('Segoe UI', 10), bg='white', fg='#666'
        )
        self.coords_status.pack(anchor='w', padx=10)
        
        # Open NFe Site button
        site_frame = tk.Frame(left_frame, bg='white')
        site_frame.pack(fill='x', padx=10, pady=10)
        
        ModernButton(
            site_frame, text="🌐 Abrir Site da NFe",
            bg='#2196F3', fg='white', font=('Segoe UI', 11, 'bold'),
            command=self._open_nfe_site
        ).pack(fill='x', pady=5)
        
        # Control buttons
        buttons_frame = tk.Frame(left_frame, bg='white')
        buttons_frame.pack(fill='x', padx=10, pady=20)
        
        self.start_btn = ModernButton(
            buttons_frame, text="🚀 Iniciar Automação",
            bg='#4CAF50', fg='white', font=('Segoe UI', 12, 'bold'),
            command=self._start_automation
        )
        self.start_btn.pack(fill='x', pady=5)
        
        self.pause_btn = ModernButton(
            buttons_frame, text="⏸️ Pausar",
            bg='#FF9800', fg='white',
            command=self._pause_automation, state='disabled'
        )
        self.pause_btn.pack(fill='x', pady=5)
        
        self.stop_btn = ModernButton(
            buttons_frame, text="🛑 Parar",
            bg='#f44336', fg='white',
            command=self._stop_automation, state='disabled'
        )
        self.stop_btn.pack(fill='x', pady=5)
        
        # Settings frame
        settings_frame = tk.LabelFrame(
            left_frame, text=" ⚙️ Configurações ",
            font=('Segoe UI', 10, 'bold'), bg='white', fg='#333'
        )
        settings_frame.pack(fill='x', padx=10, pady=(10, 0))
        
        # Delay setting
        delay_frame = tk.Frame(settings_frame, bg='white')
        delay_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(
            delay_frame, text="Atraso entre ações (segundos):",
            font=('Segoe UI', 10), bg='white', fg='#333'
        ).pack(anchor='w')
        
        self.delay_var = tk.DoubleVar(value=config.get('delay_between_actions', 2.0))
        delay_scale = tk.Scale(
            delay_frame, from_=0.5, to=5.0, resolution=0.1,
            variable=self.delay_var, orient='horizontal',
            font=('Segoe UI', 9)
        )
        delay_scale.pack(fill='x', pady=5)
        
        # Retry attempts
        retry_frame = tk.Frame(settings_frame, bg='white')
        retry_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        tk.Label(
            retry_frame, text="Tentativas de retry:",
            font=('Segoe UI', 10), bg='white', fg='#333'
        ).pack(anchor='w')
        
        self.retry_var = tk.IntVar(value=config.get('retry_attempts', 3))
        retry_scale = tk.Scale(
            retry_frame, from_=1, to=10,
            variable=self.retry_var, orient='horizontal',
            font=('Segoe UI', 9)
        )
        retry_scale.pack(fill='x', pady=5)
        
        # Right side - Status and Progress
        right_frame = tk.LabelFrame(
            content_frame, text=" 📊 Status e Progresso ",
            font=('Segoe UI', 11, 'bold'), bg='white', fg='#333'
        )
        right_frame.pack(side='right', fill='y', padx=(10, 0))
        
        # Current status
        status_frame = tk.Frame(right_frame, bg='white')
        status_frame.pack(fill='x', padx=10, pady=10)
        
        self.status_label = tk.Label(
            status_frame, text="Status: Aguardando",
            font=('Segoe UI', 12, 'bold'), bg='white', fg='#333'
        )
        self.status_label.pack(anchor='w')
        
        # Progress circle
        self.progress_canvas = tk.Canvas(right_frame, width=150, height=150, bg='white', highlightthickness=0)
        self.progress_canvas.pack(pady=10)
        
        # Statistics
        stats_frame = tk.Frame(right_frame, bg='white')
        stats_frame.pack(fill='x', padx=10, pady=10)
        
        self.stats_labels = {}
        stats_items = [
            ('total', 'Total de chaves: 0'),
            ('processed', 'Processadas: 0'),
            ('success', 'Sucessos: 0'),
            ('failed', 'Falhas: 0'),
            ('captcha', 'CAPTCHAs: 0'),
            ('elapsed', 'Tempo: 00:00:00')
        ]
        
        for key, text in stats_items:
            label = tk.Label(
                stats_frame, text=text,
                font=('Segoe UI', 10), bg='white', fg='#666'
            )
            label.pack(anchor='w')
            self.stats_labels[key] = label
        
        # Hotkeys info
        hotkeys_frame = tk.LabelFrame(
            right_frame, text=" ⌨️ Teclas de Atalho ",
            font=('Segoe UI', 10, 'bold'), bg='white', fg='#333'
        )
        hotkeys_frame.pack(fill='x', padx=10, pady=10)
        
        hotkeys_text = """F9 - Iniciar automação\nF10 - Pausar/Retomar\nF8 - Parar automação\nESC - Parada de emergência"""
        
        tk.Label(
            hotkeys_frame, text=hotkeys_text,
            font=('Consolas', 9), bg='white', fg='#333',
            justify='left'
        ).pack(padx=10, pady=10)
        
    def _start_automation(self):
        """Start automation"""
        # Get configuration
        keys = self.get_keys_func()
        coordinates = self.get_coords_func()
        
        if not keys:
            messagebox.showerror("Erro", "Nenhuma chave NFe válida encontrada!")
            return
            
        if not self._validate_coordinates(coordinates):
            messagebox.showerror("Erro", "Coordenadas não configuradas corretamente!")
            return
        
        # Update configuration
        config.set('delay_between_actions', self.delay_var.get())
        config.set('retry_attempts', self.retry_var.get())
        
        # Setup and start automation
        automation_controller.setup(coordinates, keys)
        automation_controller.start()
        
        # Update UI
        self.automation_running = True
        self._update_button_states()
        
        self.status_callback("Automação iniciada", True)
        
    def _pause_automation(self):
        """Pause/resume automation"""
        automation_controller.pause()
        self.status_callback("Automação pausada/retomada", False)
        
    def _stop_automation(self):
        """Stop automation"""
        automation_controller.stop()
        self.automation_running = False
        self._update_button_states()
        self.status_callback("Automação parada", False)
        
    def _validate_coordinates(self, coordinates: Dict) -> bool:
        """Validate coordinates configuration"""
        required = ['campo_chave', 'captcha', 'continuar', 'download', 'certificado', 'nova_consulta']
        
        for coord in required:
            if coord not in coordinates:
                return False
            if coordinates[coord].get('x', 0) == 0 or coordinates[coord].get('y', 0) == 0:
                return False
                
        return True
        
    def _update_button_states(self):
        """Update button states based on automation status"""
        status = automation_controller.get_status()
        
        if status == AutomationStatus.IDLE:
            self.start_btn.config(state='normal', text="🚀 Iniciar Automação")
            self.pause_btn.config(state='disabled')
            self.stop_btn.config(state='disabled')
            self.automation_running = False
            
        elif status == AutomationStatus.RUNNING:
            self.start_btn.config(state='disabled')
            self.pause_btn.config(state='normal', text="⏸️ Pausar")
            self.stop_btn.config(state='normal')
            
        elif status == AutomationStatus.PAUSED:
            self.start_btn.config(state='disabled')
            self.pause_btn.config(state='normal', text="▶️ Retomar")
            self.stop_btn.config(state='normal')
            
        elif status == AutomationStatus.STOPPED:
            self.start_btn.config(state='normal', text="🚀 Iniciar Automação")
            self.pause_btn.config(state='disabled')
            self.stop_btn.config(state='disabled')
            self.automation_running = False
        
    def _update_status_display(self):
        """Update status display"""
        # Update configuration status
        keys = self.get_keys_func()
        coordinates = self.get_coords_func()
        
        self.keys_status.config(text=f"• Chaves: {len(keys)} carregadas")
        
        valid_coords = sum(1 for coord in coordinates.values() 
                          if coord.get('x', 0) != 0 and coord.get('y', 0) != 0)
        self.coords_status.config(text=f"• Coordenadas: {valid_coords}/6 configuradas")
        
        # Update automation status
        stats = automation_controller.get_statistics()
        status = automation_controller.get_status()
        
        status_text_map = {
            AutomationStatus.IDLE: "Aguardando",
            AutomationStatus.RUNNING: "Executando",
            AutomationStatus.PAUSED: "Pausado",
            AutomationStatus.STOPPED: "Parado",
            AutomationStatus.ERROR: "Erro"
        }
        
        self.status_label.config(text=f"Status: {status_text_map.get(status, 'Desconhecido')}")
        
        # Update statistics
        self.stats_labels['total'].config(text=f"Total de chaves: {stats.get('total_keys', 0)}")
        self.stats_labels['processed'].config(text=f"Processadas: {stats.get('processed', 0)}")
        self.stats_labels['success'].config(text=f"Sucessos: {stats.get('success', 0)}")
        self.stats_labels['failed'].config(text=f"Falhas: {stats.get('failed', 0)}")
        self.stats_labels['captcha'].config(text=f"CAPTCHAs: {stats.get('captcha_solved', 0)}")
        
        elapsed = stats.get('elapsed_time', '00:00:00')
        self.stats_labels['elapsed'].config(text=f"Tempo: {elapsed}")
        
        # Update progress circle
        total = stats.get('total_keys', 0)
        processed = stats.get('processed', 0)
        percentage = (processed / total * 100) if total > 0 else 0
        
        create_circular_progress(self.progress_canvas, 75, 75, 50, percentage)
        
        # Update button states
        self._update_button_states()
        
    def _start_status_timer(self):
        """Start timer for status updates"""
        self._update_status_display()
        self.after(1000, self._start_status_timer)  # Update every second
    
    def _open_nfe_site(self):
        """Open NFe website in browser"""
        try:
            import subprocess
            import os
            
            url = "https://www.nfe.fazenda.gov.br/portal/consultaRecaptcha.aspx?tipoConsulta=resumo&tipoConteudo=7PhJ+gAVw2g%3d"
            
            # Try WSL specific method first
            if os.path.exists('/proc/version') and 'microsoft' in open('/proc/version').read().lower():
                # WSL environment - use PowerShell to open URL
                subprocess.run(['powershell.exe', '-c', f'Start-Process "{url}"'], check=True)
            else:
                # Linux environment - try xdg-open
                subprocess.run(['xdg-open', url], check=True)
                
            self.status_callback("Site da NFe aberto no navegador", False)
        except Exception as e:
            # Fallback to webbrowser
            try:
                import webbrowser
                webbrowser.open(url)
                self.status_callback("Site da NFe aberto no navegador", False)
            except Exception as e2:
                messagebox.showwarning(
                    "Link da NFe", 
                    f"Não foi possível abrir automaticamente.\n\n"
                    f"Copie este link e cole no seu navegador:\n\n"
                    f"{url}"
                )
                # Copy to clipboard if possible
                try:
                    import pyperclip
                    pyperclip.copy(url)
                    self.status_callback("Link copiado para a área de transferência", False)
                except:
                    self.status_callback("Erro ao abrir site - use o link manualmente", False)


class LogTab(tk.Frame):
    """Tab for logging and monitoring"""
    
    def __init__(self, parent, status_callback: Callable[[str, bool], None]):
        super().__init__(parent, bg='white')
        self.status_callback = status_callback
        self.log_entries = []
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Create tab widgets"""
        # Title
        title_frame = tk.Frame(self, bg='white', height=60)
        title_frame.pack(fill='x', padx=20, pady=10)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, text="📊 Log de Atividades",
            font=('Segoe UI', 16, 'bold'), bg='white', fg='#333'
        )
        title_label.pack(anchor='w')
        
        subtitle_label = tk.Label(
            title_frame, text="Monitor em tempo real das operações de automação",
            font=('Segoe UI', 10), bg='white', fg='#666'
        )
        subtitle_label.pack(anchor='w')
        
        # Toolbar
        toolbar_frame = tk.Frame(self, bg='white')
        toolbar_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        ModernButton(
            toolbar_frame, text="💾 Salvar Log",
            bg='#4CAF50', fg='white',
            command=self._save_log
        ).pack(side='left', padx=(0, 5))
        
        ModernButton(
            toolbar_frame, text="🗑️ Limpar Log",
            bg='#f44336', fg='white',
            command=self._clear_log
        ).pack(side='left', padx=5)
        
        ModernButton(
            toolbar_frame, text="📁 Abrir Pasta de Logs",
            bg='#2196F3', fg='white',
            command=self._open_logs_folder
        ).pack(side='left', padx=5)
        
        # Filter frame
        filter_frame = tk.Frame(toolbar_frame, bg='white')
        filter_frame.pack(side='right')
        
        tk.Label(
            filter_frame, text="Filtro:", font=('Segoe UI', 10),
            bg='white', fg='#333'
        ).pack(side='left', padx=(0, 5))
        
        self.filter_var = tk.StringVar(value="Todos")
        filter_combo = ttk.Combobox(
            filter_frame, textvariable=self.filter_var,
            values=["Todos", "Info", "Success", "Warning", "Error"],
            width=10, state='readonly'
        )
        filter_combo.pack(side='left')
        filter_combo.bind('<<ComboboxSelected>>', self._apply_filter)
        
        # Log display
        log_frame = tk.Frame(self, bg='white')
        log_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Log text with scrollbar
        self.log_text = scrolledtext.ScrolledText(
            log_frame, font=('Consolas', 10), wrap='word',
            relief='solid', borderwidth=1, state='disabled'
        )
        self.log_text.pack(fill='both', expand=True)
        
        # Configure text tags for different log levels
        self.log_text.tag_configure("info", foreground="#333333")
        self.log_text.tag_configure("success", foreground="#4CAF50", font=('Consolas', 10, 'bold'))
        self.log_text.tag_configure("warning", foreground="#FF9800", font=('Consolas', 10, 'bold'))
        self.log_text.tag_configure("error", foreground="#f44336", font=('Consolas', 10, 'bold'))
        
        # Status frame
        status_frame = tk.Frame(self, bg='white')
        status_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        self.entries_label = tk.Label(
            status_frame, text="Entradas: 0", font=('Segoe UI', 10),
            bg='white', fg='#666'
        )
        self.entries_label.pack(side='left')
        
        # Auto-scroll checkbox
        self.auto_scroll_var = tk.BooleanVar(value=True)
        auto_scroll_check = tk.Checkbutton(
            status_frame, text="Auto-scroll", variable=self.auto_scroll_var,
            bg='white', font=('Segoe UI', 10)
        )
        auto_scroll_check.pack(side='right')
        
    def add_log_entry(self, message: str, level: str = "info"):
        """Add log entry with timestamp and level"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        level_icon = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌"
        }.get(level, "ℹ️")
        
        formatted_message = f"[{timestamp}] {level_icon} {message}\n"
        
        # Store entry
        self.log_entries.append({
            'message': formatted_message,
            'level': level,
            'timestamp': timestamp
        })
        
        # Apply filter and update display
        self._apply_filter()
        
        # Update counter
        self.entries_label.config(text=f"Entradas: {len(self.log_entries)}")
        
    def _apply_filter(self, event=None):
        """Apply log level filter"""
        filter_level = self.filter_var.get().lower()
        
        # Clear display
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        
        # Add filtered entries
        for entry in self.log_entries:
            if filter_level == "todos" or entry['level'] == filter_level:
                self.log_text.insert(tk.END, entry['message'], entry['level'])
        
        self.log_text.config(state='disabled')
        
        # Auto-scroll to bottom
        if self.auto_scroll_var.get():
            self.log_text.see(tk.END)
            
    def _save_log(self):
        """Save log to file"""
        if not self.log_entries:
            messagebox.showinfo("Info", "Nenhum log para salvar")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Salvar Log",
            defaultextension=".txt",
            filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"NFe Downloader Pro - Log de Atividades\n")
                    f.write(f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 60 + "\n\n")
                    
                    for entry in self.log_entries:
                        f.write(entry['message'])
                
                messagebox.showinfo("Sucesso", f"Log salvo em {file_path}")
                self.status_callback("Log salvo com sucesso", False)
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar log: {e}")
                
    def _clear_log(self):
        """Clear all log entries"""
        if messagebox.askyesno("Confirmar", "Deseja limpar todo o log?"):
            self.log_entries.clear()
            self.log_text.config(state='normal')
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state='disabled')
            self.entries_label.config(text="Entradas: 0")
            self.status_callback("Log limpo", False)
            
    def _open_logs_folder(self):
        """Open logs folder in file manager"""
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        try:
            if os.name == 'nt':  # Windows
                os.startfile(logs_dir)
            elif os.name == 'posix':  # Linux/Mac
                os.system(f'xdg-open "{logs_dir}"')
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir pasta: {e}")


class NFeDownloaderGUI:
    """Main GUI class"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.create_widgets()
        
    def setup_window(self):
        """Setup main window"""
        self.root.title("NFe Downloader Pro v2.0")
        self.root.geometry(config.get("window_size", "1200x800"))
        self.root.minsize(1000, 600)
        
        # Set icon (if available)
        try:
            icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
    def create_widgets(self):
        """Create main widgets"""
        # Main container
        main_frame = tk.Frame(self.root, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#2196F3', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Logo and title
        title_frame = tk.Frame(header_frame, bg='#2196F3')
        title_frame.pack(expand=True)
        
        tk.Label(
            title_frame, text="🚀 NFe Downloader Pro",
            font=('Segoe UI', 20, 'bold'), bg='#2196F3', fg='white'
        ).pack(pady=15)
        
        tk.Label(
            title_frame, text="Automação Inteligente para Download de XML da Receita Federal",
            font=('Segoe UI', 11), bg='#2196F3', fg='#E3F2FD'
        ).pack()
        
        # Notebook (tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Status bar
        self.status_bar = StatusBar(main_frame)
        self.status_bar.pack(fill='x', side='bottom')
        
        # Create tabs
        self.create_tabs()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_tabs(self):
        """Create all tabs"""
        # Chaves XML tab
        self.chaves_tab = ChavesTab(self.notebook, self.update_status)
        self.notebook.add(self.chaves_tab, text="  📋 Chaves XML  ")
        
        # Coordenadas tab
        self.coordenadas_tab = CoordenadasTab(self.notebook, self.update_status)
        self.notebook.add(self.coordenadas_tab, text="  🎯 Coordenadas  ")
        
        # Automação tab
        self.automacao_tab = AutomacaoTab(self.notebook, self.update_status, 
                                         lambda: self.chaves_tab.get_keys(),
                                         lambda: self.coordenadas_tab.get_coordinates())
        self.notebook.add(self.automacao_tab, text="  🤖 Automação  ")
        
        # Log tab
        self.log_tab = LogTab(self.notebook, self.update_status)
        self.notebook.add(self.log_tab, text="  📊 Log  ")
        
        # Connect automation logging to log tab
        from automation import automation_controller
        automation_controller.log_callback = self.log_tab.add_log_entry
    
    def update_status(self, message: str, working: bool = False):
        """Update status bar"""
        self.status_bar.set_status(message, working)
        
    def on_closing(self):
        """Handle window closing"""
        if messagebox.askokcancel("Sair", "Deseja sair do NFe Downloader Pro?"):
            # Save window size
            geometry = self.root.geometry()
            config.set("window_size", geometry)
            
            # Destroy window
            self.root.quit()
            self.root.destroy()
    
    def run(self):
        """Run the GUI"""
        self.root.mainloop()


def main():
    """Main function to run GUI"""
    app = NFeDownloaderGUI()
    app.run()


if __name__ == "__main__":
    main()