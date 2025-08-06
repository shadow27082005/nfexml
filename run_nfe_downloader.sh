#!/bin/bash

echo "🚀 NFe Downloader Pro v2.0 - Launcher"
echo "====================================="

# Check if we're in WSL
if grep -qi microsoft /proc/version; then
    echo "📱 WSL environment detected"
    
    # Check if X11 is available
    if ! command -v xdpyinfo &> /dev/null; then
        echo "⚠️  X11 tools not found. Installing..."
        sudo apt update && sudo apt install -y x11-utils
    fi
    
    # Set DISPLAY if not set
    if [ -z "$DISPLAY" ]; then
        export DISPLAY=:0
        echo "📺 DISPLAY set to :0"
    fi
    
    echo "💡 Make sure X11 forwarding is enabled in your WSL setup"
    echo "   Or use VcXsrv/Xming on Windows"
fi

# Check if virtual environment exists
if [ ! -d "nfe_downloader_pro/.venv" ]; then
    echo "📦 Creating virtual environment..."
    cd nfe_downloader_pro
    python3 -m venv .venv
    cd ..
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source nfe_downloader_pro/.venv/bin/activate

# Check system dependencies
echo "🔍 Checking system dependencies..."

# Check tkinter
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📋 Installing tkinter..."
    sudo apt update && sudo apt install -y python3-tk python3-dev
fi

# Check Tesseract OCR (optional)
if ! command -v tesseract &> /dev/null; then
    echo "⚠️  Tesseract OCR not found (optional for better detection)"
    echo "💡 To install: sudo apt install tesseract-ocr tesseract-ocr-por"
    echo "   This will improve automatic button detection accuracy"
else
    echo "✅ Tesseract OCR found!"
fi

# Install/update requirements
echo "📥 Installing/updating requirements..."
pip install -r nfe_downloader_pro/requirements.txt

# Run the application
echo "🎯 Starting NFe Downloader Pro..."
echo ""
echo "⌨️  Global Hotkeys:"
echo "   F9  - Start automation"
echo "   F10 - Pause/Resume"
echo "   F8  - Stop automation"  
echo "   ESC - Emergency stop"
echo ""

cd nfe_downloader_pro
python3 src/main.py

echo ""
echo "👋 NFe Downloader Pro closed"