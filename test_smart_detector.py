#!/usr/bin/env python3
"""
Test script for Smart Button Detector
Testa o sistema de detecção automática de botões
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join('nfe_downloader_pro', 'src'))

try:
    from smart_detector import SmartButtonDetector
    import time
    
    def simple_logger(msg):
        print(f"[{time.strftime('%H:%M:%S')}] {msg}")
    
    print("🤖 NFe Downloader Pro - Teste do Detector Inteligente")
    print("=" * 60)
    print()
    
    # Create detector
    detector = SmartButtonDetector(logger=simple_logger)
    
    print("📋 Instruções:")
    print("1. Abra o navegador na página da NFe")
    print("2. Certifique-se que a página está totalmente carregada")
    print("3. Pressione Enter para iniciar o teste")
    print()
    
    input("Pressione Enter para continuar...")
    print()
    
    print("🔍 Executando teste de detecção...")
    print("-" * 40)
    
    # Execute detection test
    results = detector.test_detection()
    
    print()
    print("📊 RESULTADOS DO TESTE:")
    print("=" * 30)
    
    found_count = 0
    total_count = len(results)
    
    for element_name, position in results.items():
        if position:
            found_count += 1
            status = f"✅ {position}"
            print(f"{element_name:20}: {status}")
        else:
            status = "❌ Não encontrado"
            print(f"{element_name:20}: {status}")
    
    print()
    print("📈 ESTATÍSTICAS:")
    print(f"  • Elementos encontrados: {found_count}/{total_count}")
    print(f"  • Taxa de sucesso: {(found_count/total_count)*100:.1f}%")
    print(f"  • Imagem de debug: detection_debug.png")
    
    print()
    if found_count >= 4:
        print("🎉 TESTE BEM-SUCEDIDO!")
        print("   A detecção automática está funcionando corretamente.")
        print("   Você pode usar a automação com confiança.")
    elif found_count >= 2:
        print("⚠️ TESTE PARCIAL")
        print("   Alguns elementos foram encontrados, mas não todos.")
        print("   Verifique se a página está carregada corretamente.")
    else:
        print("❌ TESTE FALHOU")
        print("   Poucos elementos foram detectados.")
        print("   Verifique se você está na página correta da NFe.")
    
    print()
    print("💡 DICAS:")
    print("  • Certifique-se que a página da NFe está completamente visível")
    print("  • Não sobreponha outras janelas sobre o navegador")
    print("  • A detecção funciona melhor em resolução 1080p ou superior")
    print("  • Verifique a imagem 'detection_debug.png' para ver o que foi detectado")

except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print()
    print("Certifique-se de que todas as dependências estão instaladas:")
    print("pip install -r nfe_downloader_pro/requirements.txt")
    
except Exception as e:
    print(f"❌ Erro durante teste: {e}")
    print()
    print("Verifique se:")
    print("  • As dependências estão instaladas corretamente")
    print("  • O ambiente gráfico está funcionando (X11)")
    print("  • Você tem permissões para capturar a tela")

print()
print("👋 Teste concluído!")