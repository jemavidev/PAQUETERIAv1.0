#!/usr/bin/env python3
"""
Script de prueba para la extracción de CUFE
Prueba diferentes formatos de CUFE dividido en líneas
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.services.pdf_parser_service import PDFParserService

def test_cufe_extraction():
    """
    Prueba la extracción de CUFE con diferentes formatos
    """
    print("🧪 Test de Extracción de CUFE\n")
    print("="*80)
    
    # CUFE de ejemplo (96 caracteres)
    cufe_real = "8cf8ec5366fa9eaccea38cdffdfa0a7690edbaf31b89adce444ca0a322d19e50a79c86d67e0fbc81609dc9451975f0ad"
    
    # Casos de prueba
    test_cases = [
        {
            "name": "CUFE en una sola línea",
            "text": f"CUFE: {cufe_real}",
            "expected": cufe_real
        },
        {
            "name": "CUFE dividido en 2 líneas (48+48)",
            "text": f"""CUFE:
{cufe_real[:48]}
{cufe_real[48:]}""",
            "expected": cufe_real
        },
        {
            "name": "CUFE dividido en 3 líneas (32+32+32)",
            "text": f"""Código CUFE:
{cufe_real[:32]}
{cufe_real[32:64]}
{cufe_real[64:]}""",
            "expected": cufe_real
        },
        {
            "name": "CUFE dividido en 4 líneas (24+24+24+24)",
            "text": f"""CUFE:
{cufe_real[:24]}
{cufe_real[24:48]}
{cufe_real[48:72]}
{cufe_real[72:]}""",
            "expected": cufe_real
        },
        {
            "name": "CUFE con espacios entre caracteres",
            "text": f"CUFE: {' '.join([cufe_real[i:i+8] for i in range(0, 96, 8)])}",
            "expected": cufe_real
        },
        {
            "name": "CUFE con guiones separadores",
            "text": f"CUFE: {'-'.join([cufe_real[i:i+16] for i in range(0, 96, 16)])}",
            "expected": cufe_real
        },
        {
            "name": "CUFE en medio de texto",
            "text": f"""
Factura Electrónica
Número: FEV-12345
Fecha: 2025-01-15

Código CUFE:
{cufe_real[:32]}
{cufe_real[32:64]}
{cufe_real[64:]}

Total: $24,300
""",
            "expected": cufe_real
        },
        {
            "name": "CUFE sin palabra clave (solo hex)",
            "text": f"""
Factura: 12345
{cufe_real[:48]}
{cufe_real[48:]}
Total: $100
""",
            "expected": cufe_real
        },
        {
            "name": "CUFE con líneas intermedias cortas",
            "text": f"""CUFE:
{cufe_real[:40]}
-
{cufe_real[40:80]}
-
{cufe_real[80:]}""",
            "expected": cufe_real
        },
        {
            "name": "CUFE en mayúsculas",
            "text": f"CUFE: {cufe_real.upper()}",
            "expected": cufe_real
        }
    ]
    
    parser = PDFParserService()
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['name']}")
        print("-" * 80)
        
        # Mostrar el texto de entrada (primeras 200 caracteres)
        print(f"Entrada (primeros 200 chars):")
        print(f"  {repr(test['text'][:200])}")
        
        # Extraer CUFE
        extracted = parser.extract_cufe(test['text'])
        
        # Verificar resultado
        if extracted == test['expected']:
            print(f"✅ PASS - CUFE extraído correctamente")
            print(f"  Extraído: {extracted[:20]}...{extracted[-20:]}")
            passed += 1
        else:
            print(f"❌ FAIL - CUFE no extraído correctamente")
            if extracted:
                print(f"  Esperado: {test['expected'][:20]}...{test['expected'][-20:]}")
                print(f"  Extraído: {extracted[:20]}...{extracted[-20:]}")
                print(f"  Longitud esperada: 96, Longitud extraída: {len(extracted)}")
            else:
                print(f"  Esperado: {test['expected'][:20]}...{test['expected'][-20:]}")
                print(f"  Extraído: None")
            failed += 1
    
    # Resumen
    print("\n" + "="*80)
    print(f"\n📊 RESUMEN:")
    print(f"  ✅ Pasados: {passed}/{len(test_cases)}")
    print(f"  ❌ Fallados: {failed}/{len(test_cases)}")
    print(f"  📈 Tasa de éxito: {(passed/len(test_cases)*100):.1f}%")
    
    if passed == len(test_cases):
        print("\n🎉 ¡TODOS LOS TESTS PASARON!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) fallaron")
        return 1

if __name__ == "__main__":
    sys.exit(test_cufe_extraction())
