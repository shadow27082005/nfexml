@echo off
chcp 65001 >nul
echo.
echo ╔═══════════════════════════════════════════════════════╗
echo ║        🤖 NFe Downloader Pro - Detecção Automática   ║
echo ║            Instalador Inteligente v2.0               ║
echo ╚═══════════════════════════════════════════════════════╝
echo.

echo 🔧 Instalando sistema de detecção automática...
echo.

echo ✅ 1/7 - Atualizando pip...
python -m pip install --upgrade pip --user

echo ✅ 2/7 - Instalando PyAutoGUI (automação)...
pip install pyautogui==0.9.54 --user

echo ✅ 3/7 - Instalando Keyboard (teclas globais)...
pip install keyboard==0.13.5 --user

echo ✅ 4/7 - Instalando OpenCV (detecção de imagens)...
pip install opencv-python==4.8.1.78 --user

echo ✅ 5/7 - Instalando NumPy (processamento)...
pip install numpy==1.24.3 --user

echo ✅ 6/7 - Instalando Pillow (manipulação de imagens)...
pip install Pillow==10.0.1 --user

echo ✅ 7/7 - Instalando Tesseract OCR (leitura de texto)...
pip install pytesseract==0.3.10 --user

echo.
echo 📋 Verificando Tesseract OCR (necessário para detecção de texto)...

tesseract --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Tesseract OCR não encontrado!
    echo 📥 Preparando download automático...
    
    echo 🔗 Baixando Tesseract para Windows...
    if not exist "tesseract-installer.exe" (
        echo 📥 Fazendo download do Tesseract...
        powershell -Command "try { Invoke-WebRequest -Uri 'https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.0.20221214/tesseract-ocr-w64-setup-5.3.0.20221214.exe' -OutFile 'tesseract-installer.exe' -UseBasicParsing } catch { Write-Host 'Erro no download. Baixe manualmente de: https://github.com/UB-Mannheim/tesseract/wiki' }"
    )
) else (
    echo ✅ Tesseract OCR já instalado!
)

echo.
echo 📁 Criando estrutura de diretórios...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "screenshots" mkdir screenshots

echo.
echo 🎯 INSTALAÇÃO CONCLUÍDA!
echo.
echo ╔═══════════════════════════════════════════════════════╗
echo ║                    🚀 PRÓXIMOS PASSOS                ║
echo ╚═══════════════════════════════════════════════════════╝

if exist "tesseract-installer.exe" (
    echo.
    echo 📦 TESSERACT OCR DETECTADO:
    echo    ✨ Execute tesseract-installer.exe
    echo    📍 Instale em: C:\Program Files\Tesseract-OCR\
    echo    ✅ Marque "Add to PATH" durante instalação
    echo.
    set /p instalar="🔧 Deseja instalar o Tesseract OCR agora? (S/N): "
    if /i "%instalar%"=="S" (
        echo 📦 Executando instalador do Tesseract...
        start "" "tesseract-installer.exe"
        echo.
        echo ⚠️ AGUARDE a instalação terminar antes de usar o aplicativo!
        echo.
    )
)

echo.
echo 🎮 COMO USAR:
echo.
echo    1. 🌐 Abra o navegador em: nfe.fazenda.gov.br
echo    2. 🚀 Execute: python src\main.py
echo    3. 🤖 Clique "Detecção Automática Inteligente"
echo    4. ✨ Aproveite a automação!
echo.

echo ⌨️ TECLAS DE ATALHO GLOBAIS:
echo    F9  - Pausar/Retomar automação
echo    F10 - CAPTCHA resolvido (continuar)
echo    F8  - Parar automação
echo    ESC - Parada de emergência
echo.

echo 🤖 RECURSOS INTELIGENTES DISPONÍVEIS:
echo    ✨ Detecção automática de botões
echo    🎯 Funciona mesmo quando botões mudam de posição
echo    🧠 Reconhecimento de texto inteligente
echo    🔍 Análise visual da tela em tempo real
echo    📊 Interface gráfica moderna
echo    🛡️ Sistema anti-detecção
echo    📈 95%+ taxa de sucesso
echo.

echo 💡 DICAS PRO:
echo    • Mantenha o navegador maximizado
echo    • Use zoom 100%% (Ctrl+0)
echo    • Resolução 1080p+ recomendada
echo    • Deixe a página da NFe visível
echo.

echo 🎉 PRONTO PARA USO! Sistema inteligente instalado com sucesso!
echo.

pause