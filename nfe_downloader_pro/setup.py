"""
Setup script for NFe Downloader Pro
Creates distributable package and executable
"""

from setuptools import setup, find_packages
import os
import sys
from pathlib import Path

# Read version from main.py
version = "2.0"

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    with open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    with open(requirements_path, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f.readlines() 
                       if line.strip() and not line.startswith('#')]

setup(
    name="nfe-downloader-pro",
    version=version,
    description="Aplicativo desktop profissional para automação de downloads de XML da Receita Federal",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="NFe Downloader Pro Team",
    author_email="contact@nfedownloaderpro.com",
    url="https://github.com/nfedownloaderpro/nfe-downloader-pro",
    packages=find_packages(),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial",
        "Topic :: Utilities",
    ],
    keywords="nfe xml receita federal automation download brasil",
    entry_points={
        'console_scripts': [
            'nfe-downloader=main:main',
        ],
        'gui_scripts': [
            'nfe-downloader-gui=main:main',
        ]
    },
    package_data={
        '': ['*.txt', '*.md', '*.json', '*.ico', '*.png', '*.jpg'],
    },
    data_files=[
        ('assets', ['assets/icon.ico'] if os.path.exists('assets/icon.ico') else []),
        ('scripts', [
            'scripts/install.bat',
            'scripts/run.bat',
            'scripts/build.bat'
        ] if os.path.exists('scripts') else []),
    ],
    zip_safe=False,
    options={
        'build_exe': {
            'packages': [
                'tkinter', 'PIL', 'cv2', 'numpy', 'pyautogui',
                'keyboard', 'pynput', 'requests', 'configparser'
            ],
            'include_files': [
                ('assets/', 'assets/'),
                ('data/', 'data/'),
                ('logs/', 'logs/'),
            ] if os.path.exists('assets') else [],
            'excludes': [
                'test', 'unittest', 'distutils', 'email', 'html',
                'http', 'urllib', 'xml', 'pydoc_data'
            ],
            'optimize': 2,
        }
    }
)

# PyInstaller spec for creating standalone executable
pyinstaller_spec = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['src/main.py'],
             pathex=['.'],
             binaries=[],
             datas=[('assets', 'assets'), ('data', 'data')],
             hiddenimports=['PIL._tkinter_finder'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='NFe Downloader Pro',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon='assets/icon.ico')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='NFe Downloader Pro')
"""

# Write PyInstaller spec file
if __name__ == "__main__":
    with open("NFe_Downloader_Pro.spec", "w", encoding="utf-8") as f:
        f.write(pyinstaller_spec)
    
    print("✅ Setup script completed!")
    print("📦 To build executable, run:")
    print("   pyinstaller NFe_Downloader_Pro.spec")
    print("📦 To create wheel package, run:")
    print("   python setup.py bdist_wheel")