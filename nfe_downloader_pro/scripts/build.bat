@echo off
title NFe Downloader Pro - Build Script

echo ========================================
echo  📦 NFe Downloader Pro - Build Script
echo ========================================
echo.

echo Verificando PyInstaller...
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo PyInstaller nao encontrado. Instalando...
    pip install pyinstaller
    if errorlevel 1 (
        echo ❌ Erro ao instalar PyInstaller
        pause
        exit /b 1
    )
)

echo ✅ PyInstaller encontrado!
echo.

echo Limpando builds anteriores...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del "*.spec"

echo ✅ Limpeza concluida!
echo.

echo Criando executavel...
pyinstaller ^
    --name "NFe Downloader Pro" ^
    --windowed ^
    --onedir ^
    --icon "assets\icon.ico" ^
    --add-data "assets;assets" ^
    --add-data "data;data" ^
    --hidden-import "PIL._tkinter_finder" ^
    --hidden-import "pynput" ^
    --hidden-import "keyboard" ^
    --exclude-module "test" ^
    --exclude-module "unittest" ^
    --exclude-module "distutils" ^
    src\main.py

if errorlevel 1 (
    echo ❌ Erro ao criar executavel
    pause
    exit /b 1
)

echo ✅ Executavel criado com sucesso!
echo.

echo Criando estrutura de distribuicao...
if not exist "dist\NFe Downloader Pro\data" mkdir "dist\NFe Downloader Pro\data"
if not exist "dist\NFe Downloader Pro\logs" mkdir "dist\NFe Downloader Pro\logs"

echo Copiando arquivos adicionais...
copy "requirements.txt" "dist\NFe Downloader Pro\"
copy "README.md" "dist\NFe Downloader Pro\"
if exist "LICENSA.txt" copy "LICENSA.txt" "dist\NFe Downloader Pro\"

echo ✅ Estrutura de distribuicao criada!
echo.

echo Testando executavel...
cd "dist\NFe Downloader Pro"
timeout 3 >nul
"NFe Downloader Pro.exe" --version >nul 2>&1
cd ..\..

echo Criando arquivo de instalacao...
echo @echo off > "dist\NFe Downloader Pro\Instalar.bat"
echo echo ========================================= >> "dist\NFe Downloader Pro\Instalar.bat"
echo echo  NFe Downloader Pro - Instalacao >> "dist\NFe Downloader Pro\Instalar.bat"
echo echo ========================================= >> "dist\NFe Downloader Pro\Instalar.bat"
echo echo. >> "dist\NFe Downloader Pro\Instalar.bat"
echo echo Criando atalho na area de trabalho... >> "dist\NFe Downloader Pro\Instalar.bat"
echo powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('$Home\Desktop\NFe Downloader Pro.lnk'); $Shortcut.TargetPath = '%cd%\NFe Downloader Pro.exe'; $Shortcut.Save()" >> "dist\NFe Downloader Pro\Instalar.bat"
echo echo ✅ Atalho criado na area de trabalho! >> "dist\NFe Downloader Pro\Instalar.bat"
echo pause >> "dist\NFe Downloader Pro\Instalar.bat"

echo Criando arquivo README para distribuicao...
echo # NFe Downloader Pro v2.0 > "dist\NFe Downloader Pro\LEIA-ME.txt"
echo. >> "dist\NFe Downloader Pro\LEIA-ME.txt"
echo ## Como usar: >> "dist\NFe Downloader Pro\LEIA-ME.txt"
echo 1. Execute "Instalar.bat" para criar atalho na area de trabalho >> "dist\NFe Downloader Pro\LEIA-ME.txt"
echo 2. Execute "NFe Downloader Pro.exe" para iniciar o aplicativo >> "dist\NFe Downloader Pro\LEIA-ME.txt"
echo. >> "dist\NFe Downloader Pro\LEIA-ME.txt"
echo ## Recursos: >> "dist\NFe Downloader Pro\LEIA-ME.txt"
echo - Interface grafica moderna com 4 abas >> "dist\NFe Downloader Pro\LEIA-ME.txt"
echo - Gerenciamento inteligente de chaves XML >> "dist\NFe Downloader Pro\LEIA-ME.txt"
echo - Sistema de captura de coordenadas >> "dist\NFe Downloader Pro\LEIA-ME.txt"
echo - Automacao com deteccao de CAPTCHA >> "dist\NFe Downloader Pro\LEIA-ME.txt"
echo - Log detalhado em tempo real >> "dist\NFe Downloader Pro\LEIA-ME.txt"
echo - Controles globais por teclas de atalho >> "dist\NFe Downloader Pro\LEIA-ME.txt"
echo. >> "dist\NFe Downloader Pro\LEIA-ME.txt"
echo ## Teclas de atalho: >> "dist\NFe Downloader Pro\LEIA-ME.txt"
echo F9  - Iniciar automacao >> "dist\NFe Downloader Pro\LEIA-ME.txt"
echo F10 - Pausar/Retomar >> "dist\NFe Downloader Pro\LEIA-ME.txt"
echo F8  - Parar automacao >> "dist\NFe Downloader Pro\LEIA-ME.txt"
echo ESC - Parada de emergencia >> "dist\NFe Downloader Pro\LEIA-ME.txt"

echo ========================================
echo ✅ BUILD CONCLUIDO COM SUCESSO!
echo ========================================
echo.
echo 📁 Arquivos de distribuicao em: dist\NFe Downloader Pro\
echo 🚀 Execute: "NFe Downloader Pro.exe"
echo 📦 Para instalar: execute "Instalar.bat"
echo.
echo 📊 Tamanho da distribuicao:
dir "dist\NFe Downloader Pro" | find "File(s)"
echo.

pause