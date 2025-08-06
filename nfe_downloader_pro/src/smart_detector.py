"""
Smart Button Detector for NFe Downloader Pro
Sistema inteligente de detecção automática de botões e elementos na tela
"""

import cv2
import numpy as np
import pyautogui
import time
from typing import Optional, Tuple, List, Dict
from PIL import Image, ImageEnhance, ImageFilter
import re

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False
    print("⚠️ pytesseract não disponível - OCR desabilitado")


class SmartButtonDetector:
    """Sistema inteligente de detecção de botões - versão avançada integrada"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Configurações de cores dos botões NFe (HSV format)
        self.button_colors = {
            'orange': {
                'lower': np.array([10, 100, 100]),   # Laranja claro
                'upper': np.array([25, 255, 255])    # Laranja escuro
            },
            'green': {
                'lower': np.array([40, 100, 150]),   # Verde claro
                'upper': np.array([80, 255, 220])    # Verde escuro
            },
            'blue': {
                'lower': np.array([100, 150, 50]),   # Azul claro
                'upper': np.array([130, 255, 150])   # Azul escuro
            }
        }
        
        # Textos esperados nos botões (para OCR)
        self.button_texts = {
            'CAMPO_CHAVE': ['chave', 'acesso', 'nf-e', 'código'],
            'CAPTCHA_CHECKBOX': ['humano', 'robô', 'verificação', 'captcha'],
            'BOTAO_CONTINUAR': ['continuar', 'prosseguir', 'avançar', 'consulta'],
            'BOTAO_DOWNLOAD': ['download', 'baixar', 'documento', 'xml'],
            'BOTAO_OK_CERT': ['ok', 'confirmar', 'certificado', 'selecionar'],
            'BOTAO_NOVA_CONSULTA': ['nova', 'consulta', 'novo', 'voltar']
        }
    
    def log(self, message):
        """Log com callback ou print"""
        if self.logger:
            self.logger(message)
        else:
            print(message)
    
    def take_screenshot(self) -> np.ndarray:
        """Captura screenshot da tela"""
        screenshot = pyautogui.screenshot()
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    def detect_orange_buttons(self) -> List[Dict]:
        """Detecta botões laranja na tela (botões principais da NFe)"""
        screenshot = self.take_screenshot()
        
        # Converte para HSV para melhor detecção de cor
        hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        
        # Cria máscara para cor laranja
        orange_range = self.button_colors['orange']
        mask = cv2.inRange(hsv, orange_range['lower'], orange_range['upper'])
        
        # Encontra contornos
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        buttons = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000:  # Filtra por tamanho mínimo
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                
                if 0.5 < aspect_ratio < 6:  # Proporção de botão
                    center_x = x + w // 2
                    center_y = y + h // 2
                    
                    buttons.append({
                        'type': 'orange_button',
                        'position': (center_x, center_y),
                        'bbox': (x, y, w, h),
                        'area': area,
                        'confidence': min(area / 2000, 1.0)
                    })
        
        # Ordena por posição horizontal (esquerda para direita)
        buttons.sort(key=lambda b: b['position'][0])
        return buttons
    
    def find_input_field(self) -> Optional[Tuple[int, int]]:
        """Encontra campo de input (campo da chave) usando detecção de bordas"""
        screenshot = self.take_screenshot()
        
        # Converte para escala de cinza
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
        # Detecta bordas
        edges = cv2.Canny(gray, 50, 150)
        
        # Encontra contornos retangulares
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        candidates = []
        
        for contour in contours:
            # Aproxima o contorno
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Se é aproximadamente retangular
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                area = w * h
                
                # Campo de input: largo e baixo, tamanho médio
                if 3 < aspect_ratio < 15 and 2000 < area < 20000:
                    center_x = x + w // 2
                    center_y = y + h // 2
                    
                    # Verifica se está na região esperada (centro da tela)
                    if (0.2 * self.screen_width < center_x < 0.8 * self.screen_width and
                        0.3 * self.screen_height < center_y < 0.7 * self.screen_height):
                        
                        # Calcula score baseado em posição e tamanho
                        position_score = self._calculate_position_score('CAMPO_CHAVE', (center_x, center_y))
                        size_score = min(area / 10000, 1.0)
                        total_score = (position_score * 0.7) + (size_score * 0.3)
                        
                        candidates.append({
                            'position': (center_x, center_y),
                            'score': total_score,
                            'area': area
                        })
        
        if candidates:
            best = max(candidates, key=lambda x: x['score'])
            return best['position']
        
        return None
    
    def find_captcha_checkbox(self) -> Optional[Tuple[int, int]]:
        """Encontra checkbox do CAPTCHA usando detecção de formas"""
        screenshot = self.take_screenshot()
        
        # Converte para escala de cinza
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
        # Detecta formas quadradas pequenas (checkboxes)
        contours, _ = cv2.findContours(
            cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)[1], 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        candidates = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 100 < area < 2000:  # Tamanho típico de checkbox
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                
                if 0.7 < aspect_ratio < 1.3:  # Aproximadamente quadrado
                    center_x = x + w // 2
                    center_y = y + h // 2
                    
                    # Verifica se está na região inferior (onde fica o CAPTCHA)
                    if center_y > 0.5 * self.screen_height:
                        
                        # OCR na região ao redor se disponível
                        text_score = 0
                        if PYTESSERACT_AVAILABLE:
                            text_score = self._check_text_around_position(screenshot, center_x, center_y, 
                                                                        self.button_texts['CAPTCHA_CHECKBOX'])
                        
                        position_score = self._calculate_position_score('CAPTCHA_CHECKBOX', (center_x, center_y))
                        total_score = (position_score * 0.6) + (text_score * 0.4)
                        
                        candidates.append({
                            'position': (center_x, center_y),
                            'score': total_score
                        })
        
        if candidates:
            best = max(candidates, key=lambda x: x['score'])
            return best['position']
        
        return None
    
    def detect_button_by_text_and_color(self, button_name: str) -> Optional[Tuple[int, int]]:
        """Detecta botão específico por texto e cor combinados"""
        screenshot = self.take_screenshot()
        
        # Detecta botões por cor
        color_buttons = self.detect_orange_buttons()
        
        candidates = []
        expected_texts = self.button_texts.get(button_name, [])
        
        for button in color_buttons:
            x, y = button['position']
            
            # Score baseado em texto (se OCR disponível)
            text_score = 0
            if PYTESSERACT_AVAILABLE and expected_texts:
                text_score = self._check_text_around_position(screenshot, x, y, expected_texts)
            else:
                text_score = 0.5  # Score neutro se OCR não disponível
            
            # Score baseado em posição esperada
            position_score = self._calculate_position_score(button_name, (x, y))
            
            # Score baseado em confiança da detecção de cor
            color_score = button['confidence']
            
            # Score total ponderado
            total_score = (text_score * 0.4) + (position_score * 0.4) + (color_score * 0.2)
            
            candidates.append({
                'position': (x, y),
                'score': total_score,
                'button_info': button
            })
        
        if candidates:
            best = max(candidates, key=lambda x: x['score'])
            return best['position']
        
        return None
    
    def _check_text_around_position(self, screenshot: np.ndarray, x: int, y: int, expected_texts: List[str]) -> float:
        """Verifica texto ao redor de uma posição usando OCR"""
        if not PYTESSERACT_AVAILABLE:
            return 0.5
        
        try:
            # Define região ao redor do ponto
            region_size = 100
            region_x = max(0, x - region_size//2)
            region_y = max(0, y - region_size//2)
            region_w = min(screenshot.shape[1] - region_x, region_size)
            region_h = min(screenshot.shape[0] - region_y, region_size)
            
            # Extrai região
            region = screenshot[region_y:region_y+region_h, region_x:region_x+region_w]
            
            # Converte para PIL e melhora qualidade
            pil_image = Image.fromarray(cv2.cvtColor(region, cv2.COLOR_BGR2RGB))
            pil_image = pil_image.resize((region_w*2, region_h*2), Image.LANCZOS)
            
            # Melhora contraste
            enhancer = ImageEnhance.Contrast(pil_image)
            pil_image = enhancer.enhance(2.0)
            
            # OCR
            text = pytesseract.image_to_string(pil_image, config='--psm 8').strip().lower()
            
            # Verifica se algum texto esperado está presente
            matches = sum(1 for expected in expected_texts if expected in text)
            return min(matches / len(expected_texts), 1.0) if expected_texts else 0.5
            
        except Exception as e:
            return 0.5
    
    def _calculate_position_score(self, button_name: str, position: Tuple[int, int]) -> float:
        """Calcula pontuação baseada na posição esperada do botão na tela"""
        x, y = position
        screen_w, screen_h = self.screen_width, self.screen_height
        
        # Posições esperadas relativas (0-1)
        expected_positions = {
            'CAMPO_CHAVE': (0.4, 0.4),        # Centro-esquerda
            'CAPTCHA_CHECKBOX': (0.3, 0.65),  # Esquerda-baixo
            'BOTAO_CONTINUAR': (0.4, 0.7),    # Centro-baixo
            'BOTAO_DOWNLOAD': (0.6, 0.7),     # Direita-baixo
            'BOTAO_OK_CERT': (0.5, 0.3),      # Centro-cima (popup)
            'BOTAO_NOVA_CONSULTA': (0.2, 0.7) # Esquerda-baixo
        }
        
        if button_name in expected_positions:
            expected_x, expected_y = expected_positions[button_name]
            expected_x *= screen_w
            expected_y *= screen_h
            
            # Calcula distância euclidiana
            distance = np.sqrt((x - expected_x)**2 + (y - expected_y)**2)
            max_distance = np.sqrt(screen_w**2 + screen_h**2)
            
            # Converte para score normalizado (mais perto = melhor)
            return max(0, 1.0 - (distance / max_distance))
        
        return 0.5  # Score neutro se posição desconhecida
    
    def smart_detect_all_elements(self) -> Dict[str, Optional[Tuple[int, int]]]:
        """Detecta todos os elementos de forma inteligente"""
        self.log("🤖 Iniciando detecção inteligente avançada...")
        
        results = {}
        
        # 1. Campo de chave (método específico)
        self.log("🔍 Procurando campo de chave...")
        campo_chave = self.find_input_field()
        results['CAMPO_CHAVE'] = campo_chave
        
        if campo_chave:
            self.log(f"✅ Campo chave encontrado: {campo_chave}")
        else:
            self.log("❌ Campo chave não encontrado")
        
        # 2. Checkbox CAPTCHA (método específico)
        self.log("🔍 Procurando checkbox CAPTCHA...")
        captcha_box = self.find_captcha_checkbox()
        results['CAPTCHA_CHECKBOX'] = captcha_box
        
        if captcha_box:
            self.log(f"✅ CAPTCHA encontrado: {captcha_box}")
        else:
            self.log("❌ CAPTCHA não encontrado")
        
        # 3. Botões laranja por cor + texto
        self.log("🔍 Procurando botões laranja...")
        orange_buttons = self.detect_orange_buttons()
        
        if len(orange_buttons) >= 2:
            # Mapeia botões por posição e contexto
            if len(orange_buttons) == 2:
                # Configuração típica: Nova Consulta + Download
                left_button = min(orange_buttons, key=lambda b: b['position'][0])
                right_button = max(orange_buttons, key=lambda b: b['position'][0])
                
                results['BOTAO_NOVA_CONSULTA'] = left_button['position']
                results['BOTAO_DOWNLOAD'] = right_button['position']
                results['BOTAO_CONTINUAR'] = right_button['position']  # Mesmo que download inicialmente
                
            elif len(orange_buttons) >= 3:
                # Configuração completa: Nova Consulta + Continuar + Download
                sorted_buttons = sorted(orange_buttons, key=lambda b: b['position'][0])
                
                results['BOTAO_NOVA_CONSULTA'] = sorted_buttons[0]['position']
                results['BOTAO_CONTINUAR'] = sorted_buttons[1]['position']
                results['BOTAO_DOWNLOAD'] = sorted_buttons[-1]['position']  # Último (mais à direita)
            
            # Log dos botões encontrados
            for i, btn in enumerate(orange_buttons):
                self.log(f"✅ Botão laranja {i+1}: {btn['position']} (área: {btn['area']})")
        
        else:
            self.log("❌ Botões laranja insuficientes encontrados")
            
            # Fallback: tenta detectar individualmente
            for btn_name in ['BOTAO_CONTINUAR', 'BOTAO_DOWNLOAD', 'BOTAO_NOVA_CONSULTA']:
                pos = self.detect_button_by_text_and_color(btn_name)
                results[btn_name] = pos
                if pos:
                    self.log(f"✅ {btn_name} encontrado individualmente: {pos}")
        
        # 4. Botão de certificado (estimativa no centro para popups)
        results['BOTAO_OK_CERT'] = (self.screen_width // 2, self.screen_height // 2)
        self.log(f"📍 Certificado (estimativa central): {results['BOTAO_OK_CERT']}")
        
        # Estatísticas finais
        encontrados = sum(1 for pos in results.values() if pos is not None)
        total = len(results)
        self.log(f"📊 Detecção concluída: {encontrados}/{total} elementos encontrados")
        
        return results
    
    def save_detection_image(self, results: Dict[str, Optional[Tuple[int, int]]], 
                           filename: str = "detection_debug.png"):
        """Salva imagem com marcações de detecção para debug"""
        try:
            screenshot = self.take_screenshot()
            
            # Marca os elementos encontrados
            colors = {
                'CAMPO_CHAVE': (0, 255, 0),        # Verde
                'CAPTCHA_CHECKBOX': (255, 0, 0),   # Vermelho
                'BOTAO_CONTINUAR': (0, 0, 255),    # Azul
                'BOTAO_DOWNLOAD': (255, 255, 0),   # Ciano
                'BOTAO_OK_CERT': (255, 0, 255),    # Magenta
                'BOTAO_NOVA_CONSULTA': (0, 255, 255) # Amarelo
            }
            
            for element_name, position in results.items():
                if position:
                    x, y = position
                    color = colors.get(element_name, (128, 128, 128))
                    
                    # Desenha círculo
                    cv2.circle(screenshot, (x, y), 15, color, 3)
                    
                    # Adiciona texto
                    label = element_name.replace('_', ' ').replace('BOTAO', '').strip()
                    cv2.putText(screenshot, label, (x+20, y), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Salva imagem
            cv2.imwrite(filename, screenshot)
            self.log(f"🖼️ Imagem de debug salva: {filename}")
            
        except Exception as e:
            self.log(f"❌ Erro ao salvar imagem: {e}")
    
    def test_detection(self):
        """Testa sistema de detecção e salva resultado visual"""
        self.log("🧪 Executando teste de detecção...")
        
        # Executa detecção completa
        results = self.smart_detect_all_elements()
        
        # Salva imagem de debug
        self.save_detection_image(results)
        
        # Retorna resultados
        return results


# Exemplo de uso standalone
if __name__ == "__main__":
    def simple_logger(msg):
        print(f"[{time.strftime('%H:%M:%S')}] {msg}")
    
    detector = SmartButtonDetector(logger=simple_logger)
    
    print("🚀 Testando detecção automática inteligente de botões...")
    print("Posicione o navegador na página da NFe e pressione Enter...")
    input()
    
    # Testa detecção
    results = detector.test_detection()
    
    # Mostra resultados
    print("\n📊 RESULTADOS FINAIS:")
    for name, pos in results.items():
        status = f"✅ {pos}" if pos else "❌ Não encontrado"
        print(f"  {name}: {status}")
    
    print(f"\n🖼️ Imagem de debug salva: detection_debug.png")
    print("🎉 Teste concluído!")