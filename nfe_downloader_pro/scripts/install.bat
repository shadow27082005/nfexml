@echo off
echo ========================================
echo  NFe Downloader Pro - Instalador
echo ========================================
echo.

echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python nao encontrado!
    echo Por favor, instale Python 3.7+ de https://python.org
    pause
    exit /b 1
)

echo ✅ Python encontrado!
echo.

echo Verificando pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip nao encontrado!
    echo Por favor, instale pip primeiro
    pause
    exit /b 1
)

echo ✅ pip encontrado!
echo.

echo Criando ambiente virtual...
if not exist "venv" (
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Erro ao criar ambiente virtual
        pause
        exit /b 1
    )
    echo ✅ Ambiente virtual criado!
) else (
    echo ℹ️ Ambiente virtual ja existe
)
echo.

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Erro ao ativar ambiente virtual
    pause
    exit /b 1
)

echo ✅ Ambiente virtual ativado!
echo.

echo Atualizando pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ❌ Erro ao atualizar pip
    pause
    exit /b 1
)

echo ✅ pip atualizado!
echo.

echo Instalando dependencias Python...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Erro ao instalar dependencias
    echo Tentando instalacao individual...
    
    pip install pyautogui==0.9.54
    pip install keyboard==0.13.5
    pip install opencv-python==4.8.1.78
    pip install numpy==1.24.3
    pip install Pillow==10.0.1
    pip install pytesseract==0.3.10
    pip install python-dateutil==2.8.2
    
    if errorlevel 1 (
        echo ❌ Erro na instalacao das dependencias Python
        echo Verifique sua conexao de internet e tente novamente
        pause
        exit /b 1
    )
)

echo ✅ Dependencias Python instaladas!
echo.

echo Verificando Tesseract OCR...
tesseract --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Tesseract OCR nao encontrado
    echo.
    echo 📋 OPCIONAL: Para melhor deteccao automatica, instale o Tesseract:
    echo   1. Baixe de: https://github.com/UB-Mannheim/tesseract/wiki
    echo   2. Instale o executavel
    echo   3. Adicione ao PATH: C:\Program Files\Tesseract-OCR
    echo.
    echo 💡 O programa ainda funcionara sem o Tesseract
    echo.
) else (
    echo ✅ Tesseract OCR encontrado!
)

echo ✅ Dependencias instaladas!
echo.

echo Criando diretórios necessários...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "assets" mkdir assets

echo ✅ Diretórios criados!
echo.

echo ========================================
echo ✅ INSTALACAO CONCLUIDA COM SUCESSO!
echo ========================================
echo.
echo Para executar o NFe Downloader Pro:
echo 1. Execute run.bat OU
echo 2. Ative o ambiente virtual: venv\Scripts\activate.bat
echo 3. Execute: python src\main.py
echo.
echo ⌨️ Teclas de atalho globais:
echo   F9  - Iniciar automacao
echo   F10 - Pausar/Retomar  
echo   F8  - Parar automacao
echo   ESC - Parada de emergencia
echo.

pause