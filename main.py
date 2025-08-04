import pyautogui
import pyperclip
import time

# --- CONFIGURAR AQUI ---
COORD_CAMPO_CHAVE = (600, 300)     # Onde clicar para colar a chave
COORD_BOTAO_CONSULTAR = (700, 400) # Botão "Consultar"
COORD_BOTAO_DOWNLOAD = (800, 500)  # Botão "Download de Documentos"

TEMPO_CAPTCHA = 12     # Tempo para você resolver o CAPTCHA
TEMPO_PAGINA = 5       # Tempo para carregar a consulta
TEMPO_DOWNLOAD = 3     # Tempo para baixar e confirmar certificado

# ------------------------

print("Você tem 5 segundos para posicionar o navegador...")
time.sleep(5)

# Lê chaves do arquivo
with open("chaves.txt", "r") as arquivo:
    chaves = [linha.strip() for linha in arquivo if linha.strip().isdigit()]

for chave in chaves:
    print(f"🔑 Processando chave: {chave}")

    # 1. Clica no campo e cola
    pyautogui.click(*COORD_CAMPO_CHAVE)
    time.sleep(0.5)
    pyperclip.copy(chave)
    pyautogui.hotkey('ctrl', 'v')

    # 2. Espera você resolver o CAPTCHA
    print("⏳ Aguarde e resolva o CAPTCHA manualmente...")
    time.sleep(TEMPO_CAPTCHA)

    # 3. Clica em "Consultar"
    pyautogui.click(*COORD_BOTAO_CONSULTAR)
    time.sleep(TEMPO_PAGINA)

    # 4. Clica em "Download de Documentos"
    pyautogui.click(*COORD_BOTAO_DOWNLOAD)
    time.sleep(1)

    # 5. Confirma certificado (ENTER)
    pyautogui.press('enter')
    time.sleep(TEMPO_DOWNLOAD)

    # 6. Voltar para nova chave
    pyautogui.hotkey('alt', 'left')
    time.sleep(2)

print("✅ Finalizado com sucesso.")
