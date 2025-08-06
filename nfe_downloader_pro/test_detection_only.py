#!/usr/bin/env python3
"""
🤖 NFe Downloader Pro - Teste de Detecção Automática
Testa apenas o sistema de detecção inteligente sem GUI
"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_smart_detection():
    """Testa sistema de detecção automática"""
    
    print("╔═══════════════════════════════════════════════════════╗")
    print("║        🤖 NFe Downloader Pro - Teste de Detecção     ║")
    print("║                Sistema Inteligente                    ║")
    print("╚═══════════════════════════════════════════════════════╝")
    print()
    
    try:
        from smart_detector import SmartButtonDetector
        print("✅ Módulo de detecção importado com sucesso!")
        
    except ImportError as e:
        print(f"❌ Erro ao importar módulo: {e}")
        print()
        print("📋 Instale as dependências:")
        print("pip install opencv-python numpy pillow pytesseract")
        return False
    
    # Logger personalizado
    def logger(msg):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {msg}")
    
    print()
    print("📋 INSTRUÇÕES PARA O TESTE:")
    print("1. 🌐 Abra o navegador na página da NFe")
    print("2. 📍 Navegue para a consulta de NFe")
    print("3. 👀 Certifique-se que a página está visível")
    print("4. ⌨️ Pressione Enter quando estiver pronto")
    print()
    
    input("Pressione Enter para iniciar o teste...")
    print()
    
    # Criar detector
    logger("Inicializando detector inteligente...")
    detector = SmartButtonDetector(logger=logger)
    
    print("🔍 EXECUTANDO DETECÇÃO AUTOMÁTICA...")
    print("=" * 50)
    
    # Executar detecção
    start_time = time.time()
    results = detector.smart_detect_all_elements()
    detection_time = time.time() - start_time
    
    print()
    print("📊 RESULTADOS DA DETECÇÃO:")
    print("=" * 30)
    
    found_count = 0
    total_count = len(results)
    
    # Mapear nomes para descrições
    element_descriptions = {
        'CAMPO_CHAVE': 'Campo de Chave NFe',
        'CAPTCHA_CHECKBOX': 'Checkbox CAPTCHA',
        'BOTAO_CONTINUAR': 'Botão Continuar',
        'BOTAO_DOWNLOAD': 'Botão Download',
        'BOTAO_OK_CERT': 'Botão OK Certificado',
        'BOTAO_NOVA_CONSULTA': 'Botão Nova Consulta'
    }
    
    for element_name, position in results.items():
        description = element_descriptions.get(element_name, element_name)
        
        if position:
            found_count += 1
            status = f"✅ Encontrado em {position}"
            print(f"{description:20}: {status}")
        else:
            status = "❌ Não encontrado"
            print(f"{description:20}: {status}")
    
    print()
    print("📈 ESTATÍSTICAS DO TESTE:")
    print(f"  • Elementos encontrados: {found_count}/{total_count}")
    print(f"  • Taxa de sucesso: {(found_count/total_count)*100:.1f}%")
    print(f"  • Tempo de detecção: {detection_time:.2f}s")
    
    # Salvar imagem debug
    try:
        debug_filename = f"detection_test_{time.strftime('%H%M%S')}.png"
        detector.save_detection_image(results, debug_filename)
        print(f"  • Imagem debug: {debug_filename}")
    except Exception as e:
        print(f"  • Erro na imagem debug: {e}")
    
    print()
    
    # Avaliação do resultado
    if found_count >= 5:
        print("🎉 TESTE EXCELENTE!")
        print("   Sistema de detecção funcionando perfeitamente.")
        print("   Pronto para automação completa!")
        
    elif found_count >= 3:
        print("✅ TESTE BOM!")
        print("   Maioria dos elementos detectados.")
        print("   Automação deve funcionar bem.")
        
    elif found_count >= 2:
        print("⚠️ TESTE PARCIAL")
        print("   Alguns elementos detectados.")
        print("   Verifique se a página está carregada completamente.")
        
    else:
        print("❌ TESTE RUIM")
        print("   Poucos elementos detectados.")
        print("   Verifique se está na página correta da NFe.")
    
    print()
    print("💡 DICAS PARA MELHORAR A DETECÇÃO:")
    print("  • Maximize o navegador (F11)")
    print("  • Defina zoom para 100% (Ctrl+0)")
    print("  • Use resolução 1080p ou superior")
    print("  • Certifique-se que a página NFe está completamente carregada")
    print("  • Feche popups ou notificações que possam estar sobrepostas")
    
    # Teste de dependências opcionais
    print()
    print("🔍 VERIFICANDO DEPENDÊNCIAS OPCIONAIS:")
    
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"  ✅ Tesseract OCR: v{version}")
        
        try:
            langs = pytesseract.get_languages()
            if 'por' in langs:
                print("  ✅ Idioma português: Disponível")
            else:
                print("  ⚠️ Idioma português: Não encontrado")
        except:
            print("  ⚠️ Não foi possível verificar idiomas")
            
    except ImportError:
        print("  ⚠️ Tesseract OCR: Não instalado (opcional)")
        print("     Para melhor precisão, instale: pip install pytesseract")
    except Exception as e:
        print(f"  ⚠️ Tesseract OCR: Erro - {e}")
    
    try:
        import cv2
        print(f"  ✅ OpenCV: v{cv2.__version__}")
    except ImportError:
        print("  ❌ OpenCV: Não instalado (obrigatório)")
    
    try:
        import numpy as np
        print(f"  ✅ NumPy: v{np.__version__}")
    except ImportError:
        print("  ❌ NumPy: Não instalado (obrigatório)")
    
    print()
    return found_count >= 3


if __name__ == "__main__":
    try:
        success = test_smart_detection()
        
        print()
        if success:
            print("🚀 SISTEMA PRONTO PARA USO!")
            print("Execute o aplicativo principal: python src/main.py")
        else:
            print("🔧 AJUSTES NECESSÁRIOS")
            print("Consulte as dicas acima e tente novamente.")
            
        print()
        print("👋 Teste concluído!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Teste interrompido pelo usuário")
        
    except Exception as e:
        print(f"\n❌ Erro durante teste: {e}")
        print("Verifique as dependências e tente novamente.")
        
    finally:
        print("\n📝 Para relatórios de bugs ou sugestões:")
        print("   Inclua a imagem debug gerada pelo teste")