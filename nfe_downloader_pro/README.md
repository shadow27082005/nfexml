# 🚀 NFe Downloader Pro v2.0

**Aplicativo desktop profissional para automação de downloads de XML da Receita Federal**

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Mac-lightgrey.svg)

## 📋 Visão Geral

O NFe Downloader Pro é uma solução completa e profissional para automatizar o processo de download de XMLs de Notas Fiscais Eletrônicas do site da Receita Federal. Com interface moderna, sistema inteligente de automação e recursos avançados de monitoramento.

### ✨ Principais Recursos

- 🖥️ **Interface Gráfica Moderna**: 4 abas organizadas para máxima produtividade
- 🗂️ **Gerenciamento Inteligente de Chaves**: Validação automática e remoção de duplicatas
- 🤖 **Detecção Automática de Botões**: Sistema avançado com OpenCV e OCR
- 🎯 **Sistema de Coordenadas**: Captura manual ou automática de elementos
- 🧠 **Automação Inteligente**: Detecção automática de CAPTCHA e retry inteligente  
- 📊 **Logging Detalhado**: Monitoramento em tempo real com filtros e exportação
- ⌨️ **Controles Globais**: Teclas de atalho para controle total
- 💾 **Configuração Persistente**: Salva automaticamente todas as configurações

## 🔧 Instalação

### Método 1: Instalação Automática (Recomendado)

1. **Clone ou baixe o projeto:**
   ```bash
   git clone https://github.com/nfedownloaderpro/nfe-downloader-pro.git
   cd nfe-downloader-pro
   ```

2. **Execute o instalador:**
   ```batch
   # Windows
   scripts\install.bat
   ```
   
   ```bash
   # Linux/Mac
   chmod +x scripts/install.sh
   ./scripts/install.sh
   ```

### Método 2: Instalação Manual

1. **Instale Python 3.7+:**
   - Download de [python.org](https://python.org)
   - Marque "Add Python to PATH" durante a instalação

2. **Crie ambiente virtual:**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac  
   source venv/bin/activate
   ```

3. **Instale dependências:**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Uso

### Inicialização Rápida

```batch
# Windows - Execute o launcher
scripts\run.bat
```

```bash
# Linux/Mac
python src/main.py
```

### Passo a Passo

#### 1. 📋 Aba "Chaves XML"
- Cole as chaves NFe (uma por linha) no campo de texto
- Use **"Carregar Arquivo"** para importar de .txt
- O sistema valida automaticamente e mostra estatísticas
- Chaves inválidas são identificadas e destacadas

#### 2. 🎯 Aba "Coordenadas" ou 🤖 **NOVO: Detecção Automática**

**Método Automático (Recomendado):**
- Abra o site da Receita Federal no navegador
- Na aba "Automação", clique **"🤖 Detecção Automática Inteligente"**
- O sistema detecta todos os botões automaticamente usando OpenCV + OCR
- Clique **"🖼️ Salvar Imagem Debug"** para verificar a detecção

**Método Manual (Tradicional):**
- Para cada elemento, clique **"Capturar"**
- Posicione o mouse sobre o elemento e pressione **ESPAÇO**
- Teste as coordenadas com **"Testar"**
- Salve a configuração

#### 3. 🤖 Aba "Automação"
- Verifique o status da configuração
- Ajuste atrasos e tentativas de retry
- Clique **"Iniciar Automação"** ou pressione **F9**
- Monitore o progresso em tempo real

#### 4. 📊 Aba "Log"
- Acompanhe todas as atividades em tempo real
- Filtre por tipo de evento (Info, Success, Warning, Error)
- Salve logs para análise posterior
- Configure auto-scroll

## ⌨️ Teclas de Atalho Globais

| Tecla | Função |
|-------|--------|
| **F9** | Iniciar automação |
| **F10** | Pausar/Retomar automação |
| **F8** | Parar automação |
| **ESC** | Parada de emergência |

## 📁 Estrutura do Projeto

```
📂 nfe_downloader_pro/
├── 📂 src/                    # Código fonte
│   ├── 📄 main.py            # Aplicativo principal
│   ├── 📄 gui.py             # Interface gráfica
│   ├── 📄 automation.py      # Sistema de automação
│   ├── 📄 config.py          # Gerenciamento de configuração
│   └── 📄 utils.py           # Utilitários
├── 📂 assets/                # Recursos (ícones, imagens)
├── 📂 scripts/               # Scripts de instalação/execução
│   ├── 📄 install.bat        # Instalador Windows
│   ├── 📄 run.bat            # Executor Windows
│   └── 📄 build.bat          # Builder executável
├── 📂 data/                  # Dados do usuário
├── 📂 logs/                  # Arquivos de log
├── 📄 requirements.txt       # Dependências
├── 📄 setup.py               # Configuração do pacote
└── 📄 README.md              # Documentação
```

## 🔧 Configuração Avançada

### Personalização de Delays

```python
# Em src/config.py - ou pela interface
config.set('delay_between_actions', 2.0)  # segundos entre ações
config.set('retry_attempts', 3)           # tentativas de retry
config.set('captcha_timeout', 30)         # timeout do CAPTCHA
```

### Teclas de Atalho Personalizadas

```json
{
  "hotkeys": {
    "start_automation": "F9",
    "pause_automation": "F10", 
    "stop_automation": "F8",
    "emergency_stop": "Esc"
  }
}
```

## 🤖 Sistema de Automação

### Detecção Inteligente de CAPTCHA

O sistema detecta automaticamente dois tipos de CAPTCHA:

1. **CAPTCHA Textual**: Tentativa de resolução automática
2. **CAPTCHA com Imagem**: Pausa para intervenção manual

### Fluxo de Automação

1. **Inserção da Chave**: Campo NFe preenchido automaticamente
2. **Resolução de CAPTCHA**: Detecção e tratamento inteligente
3. **Navegação**: Cliques automáticos nos botões
4. **Download**: Aguarda e confirma o download
5. **Nova Consulta**: Prepara para próxima chave
6. **Retry Inteligente**: Repetição em caso de falha

## 📊 Monitoramento e Logs

### Níveis de Log

- **Info** ℹ️: Operações normais
- **Success** ✅: Operações bem-sucedidas
- **Warning** ⚠️: Alertas importantes
- **Error** ❌: Erros e falhas

### Estatísticas em Tempo Real

- Total de chaves processadas
- Taxa de sucesso
- Tempo decorrido
- CAPTCHAs resolvidos
- Falhas e recuperações

## 🏗️ Compilação para Executável

### Criar Executável Standalone

```bash
# Instalar PyInstaller
pip install pyinstaller

# Executar build script
scripts\build.bat

# Ou manualmente
pyinstaller --windowed --onefile src/main.py
```

### Distribuição

O build script cria uma pasta `dist/` com:
- Executável `NFe Downloader Pro.exe`
- Todas as dependências incluídas
- Scripts de instalação automática
- Documentação completa

## 🛠️ Desenvolvimento

### Setup de Desenvolvimento

```bash
# Clone do repositório
git clone https://github.com/nfedownloaderpro/nfe-downloader-pro.git
cd nfe-downloader-pro

# Ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Dependências de desenvolvimento
pip install -r requirements.txt
pip install pytest black flake8  # Ferramentas de dev
```

### Testes

```bash
# Executar testes
python -m pytest tests/

# Cobertura de código
python -m pytest --cov=src tests/
```

### Contribuição

1. Fork do projeto
2. Crie feature branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit das mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para branch (`git push origin feature/nova-funcionalidade`)
5. Crie Pull Request

## ❓ Solução de Problemas

### Problemas Comuns

**❌ "Python não encontrado"**
- Instale Python 3.7+ de [python.org](https://python.org)
- Certifique-se de marcar "Add Python to PATH"

**❌ "Erro ao instalar dependências"**
- Atualize pip: `python -m pip install --upgrade pip`
- Instale Visual C++ Build Tools (Windows)
- Use ambiente virtual limpo

**❌ "Coordenadas não funcionam"**
- Recapture as coordenadas
- Verifique resolução da tela
- Teste as coordenadas individualmente

**❌ "Automação não inicia"**
- Verifique se todas as coordenadas estão configuradas
- Confirme que há chaves válidas carregadas
- Verifique logs para erros específicos

### Logs de Debug

Os logs são salvos automaticamente em:
- **Windows**: `logs/nfe_downloader_YYYYMMDD.log`
- **Linux/Mac**: `~/.nfe_downloader_pro/logs/`

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Suporte

- **Issues**: [GitHub Issues](https://github.com/nfedownloaderpro/nfe-downloader-pro/issues)
- **Discussões**: [GitHub Discussions](https://github.com/nfedownloaderpro/nfe-downloader-pro/discussions)
- **Email**: contact@nfedownloaderpro.com

## 🙏 Agradecimentos

- Comunidade Python pela excelente documentação
- Contribuidores do PyAutoGUI e OpenCV
- Usuários que forneceram feedback e sugestões

---

**⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!**

## 📈 Roadmap

### Versão 2.1 (Próxima)
- [ ] Integração com OCR para resolução automática de CAPTCHA
- [ ] Suporte a múltiplos certificados digitais
- [ ] Interface web opcional
- [ ] API REST para integração

### Versão 2.2 (Futuro)
- [ ] Processamento em lote otimizado
- [ ] Dashboard de estatísticas avançadas
- [ ] Integração com bancos de dados
- [ ] Notificações push

---

*Desenvolvido com ❤️ para a comunidade brasileira*