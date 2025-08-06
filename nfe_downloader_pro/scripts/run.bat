@echo off
title NFe Downloader Pro v2.0

echo ========================================
echo  🚀 NFe Downloader Pro v2.0
echo ========================================
echo.

REM Verificar se o ambiente virtual existe
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Ambiente virtual nao encontrado!
    echo Execute install.bat primeiro para instalar o aplicativo
    echo.
    pause
    exit /b 1
)

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Verificar se main.py existe
if not exist "src\main.py" (
    echo ❌ Arquivo principal nao encontrado!
    echo Verifique se o arquivo src\main.py existe
    echo.
    pause
    exit /b 1
)

echo ✅ Iniciando NFe Downloader Pro...
echo.
echo 💡 Dica: Configure as coordenadas antes de iniciar a automacao
echo.
echo ⌨️ Teclas de atalho globais:
echo   F9  - Iniciar automacao
echo   F10 - Pausar/Retomar
echo   F8  - Parar automacao  
echo   ESC - Parada de emergencia
echo.

REM Executar o aplicativo
python src\main.py

REM Se chegou aqui, o aplicativo foi fechado
echo.
echo ========================================
echo 👋 NFe Downloader Pro finalizado
echo ========================================

REM Pausa apenas se houve erro
if errorlevel 1 (
    echo.
    echo ❌ O aplicativo foi fechado com erro
    pause
)

REM Desativar ambiente virtual
deactivate