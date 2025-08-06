# 🔍 Instalação do Tesseract OCR

O NFe Downloader Pro usa **Tesseract OCR** para reconhecimento de texto nos botões, permitindo detecção automática mais precisa.

## 🐧 Linux (Ubuntu/Debian)

```bash
# Instalar Tesseract
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-por

# Verificar instalação
tesseract --version
```

## 🪟 Windows

### Método 1: Instalador Oficial
1. Baixe: https://github.com/UB-Mannheim/tesseract/wiki
2. Execute o instalador
3. Adicione ao PATH: `C:\Program Files\Tesseract-OCR`

### Método 2: Chocolatey
```powershell
# Instalar Chocolatey (se não tiver)
# Depois instalar Tesseract
choco install tesseract
```

## 🍎 macOS

```bash
# Usando Homebrew
brew install tesseract

# Com idioma português
brew install tesseract-lang
```

## ⚙️ Configuração no Python

O `pytesseract` detecta automaticamente o Tesseract na maioria dos casos. 

Se houver problemas, configure manualmente:

```python
import pytesseract

# Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Linux/Mac (geralmente não necessário)
# pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
```

## ✅ Teste da Instalação

Execute este script para testar:

```python
import pytesseract
from PIL import Image

try:
    # Teste básico
    version = pytesseract.get_tesseract_version()
    print(f"✅ Tesseract {version} instalado com sucesso!")
    
    # Idiomas disponíveis
    langs = pytesseract.get_languages()
    print(f"📋 Idiomas: {langs}")
    
    if 'por' in langs:
        print("✅ Português disponível")
    else:
        print("⚠️ Português não encontrado - instale: tesseract-ocr-por")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    print("Instale o Tesseract seguindo as instruções acima")
```

## 🚨 Problemas Comuns

### "TesseractNotFoundError"
- **Windows**: Tesseract não está no PATH
- **Linux**: `sudo apt install tesseract-ocr`
- **macOS**: `brew install tesseract`

### OCR não funciona bem
- Instale idioma português: `tesseract-ocr-por`
- Verifique qualidade da imagem
- Use imagens com bom contraste

### Permissões
- **Linux**: Certifique-se que o usuário tem acesso ao Tesseract
- **Windows**: Execute como administrador se necessário

## 📝 Nota Importante

**O OCR é opcional!** 

Se o Tesseract não estiver instalado, o NFe Downloader Pro ainda funcionará:
- ✅ Detecção por cor e forma ainda funciona
- ✅ Detecção manual de coordenadas funciona
- ⚠️ Precisão da detecção automática pode ser menor

Para máxima precisão, recomendamos instalar o Tesseract.

## 🔧 Versões Testadas

- **Tesseract**: 4.1.1 ou superior
- **pytesseract**: 0.3.10
- **Idiomas**: eng (inglês) + por (português)