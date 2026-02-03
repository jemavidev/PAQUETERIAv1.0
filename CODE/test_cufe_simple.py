#!/usr/bin/env python3
"""
Script de prueba simplificado para la extracción de CUFE
No requiere dependencias externas
"""
import re
from typing import Optional

def extract_cufe(text: str) -> Optional[str]:
    """
    Extrae el código CUFE/CUDE/CUDS (96 caracteres hexadecimales)
    MEJORADO: Maneja CUFEs divididos en múltiples líneas (1, 2, 3 o 4 líneas)
    """
    CUFE_PATTERN = r'[0-9a-fA-F]{96}'
    
    # Estrategia 1: Buscar CUFE completo en una sola línea
    matches = re.findall(CUFE_PATTERN, text, re.IGNORECASE)
    if matches:
        cufe = matches[0].strip().replace('\n', '').replace(' ', '').replace('\r', '')
        if len(cufe) == 96:
            return cufe.lower()
    
    # Estrategia 2: CUFE dividido en múltiples líneas
    # Buscar palabras clave que indican que viene el CUFE
    cufe_keywords = [
        r'(?:CUFE|CUDE|CUDS|Código\s+CUFE|Codigo\s+CUFE)[\s:]*\n?',
        r'(?:Código\s+único|Codigo\s+unico)[\s:]*\n?',
        r'(?:Hash)[\s:]*\n?',
    ]
    
    for keyword_pattern in cufe_keywords:
        # Buscar la palabra clave
        match = re.search(keyword_pattern, text, re.IGNORECASE)
        if match:
            # Extraer las siguientes 500 caracteres después de la palabra clave
            start_pos = match.end()
            section = text[start_pos:start_pos + 500]
            
            # Extraer todos los caracteres hexadecimales (ignorando espacios y saltos de línea)
            hex_chars = re.findall(r'[0-9a-fA-F]', section)
            
            # Unir los primeros 96 caracteres hexadecimales
            if len(hex_chars) >= 96:
                cufe = ''.join(hex_chars[:96])
                return cufe.lower()
    
    # Estrategia 3: Buscar secuencias largas de caracteres hexadecimales
    # Limpiar el texto: eliminar espacios, saltos de línea, guiones
    cleaned_text = text.replace(' ', '').replace('\n', '').replace('\r', '').replace('-', '').replace('_', '')
    
    # Buscar secuencias de 96 caracteres hexadecimales consecutivos
    matches = re.findall(r'[0-9a-fA-F]{96}', cleaned_text, re.IGNORECASE)
    if matches:
        return matches[0].lower()
    
    # Estrategia 4: Buscar líneas consecutivas con solo caracteres hexadecimales
    lines = text.split('\n')
    hex_buffer = []
    
    for line in lines:
        # Limpiar la línea
        cleaned_line = line.strip().replace(' ', '').replace('-', '').replace('_', '')
        
        # Si la línea tiene solo caracteres hexadecimales (mínimo 10 caracteres)
        if len(cleaned_line) >= 10 and re.match(r'^[0-9a-fA-F]+$', cleaned_line):
            hex_buffer.append(cleaned_line)
            
            # Unir el buffer
            combined = ''.join(hex_buffer)
            
            # Si llegamos a 96 caracteres, tenemos el CUFE
            if len(combined) >= 96:
                return combined[:96].lower()
        else:
            # Si la línea no es hexadecimal, resetear el buffer
            # PERO solo si el buffer está vacío o tiene menos de 20 caracteres
            if len(''.join(hex_buffer)) < 20:
                hex_buffer = []
    
    # Estrategia 5: Buscar fragmentos de 20+ caracteres hex consecutivos
    # y unirlos si están cerca
    fragments = re.findall(r'[0-9a-fA-F]{20,}', text, re.IGNORECASE)
    if fragments:
        # Limpiar fragmentos
        cleaned_fragments = []
        for frag in fragments:
            cleaned = frag.replace(' ', '').replace('\n', '').replace('\r', '')
            if len(cleaned) >= 20:
                cleaned_fragments.append(cleaned)
        
        # Intentar unir los primeros fragmentos hasta llegar a 96
        combined = ''.join(cleaned_fragments)
        if len(combined) >= 96:
            return combined[:96].lower()
    
    return None

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
            "name": "CUFE en mayúsculas",
            "text": f"CUFE: {cufe_real.upper()}",
            "expected": cufe_real
        },
        {
            "name": "CUFE dividido con espacios en cada línea",
            "text": f"""CUFE:
{cufe_real[:24]} {cufe_real[24:48]}
{cufe_real[48:72]} {cufe_real[72:]}""",
            "expected": cufe_real
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['name']}")
        print("-" * 80)
        
        # Extraer CUFE
        extracted = extract_cufe(test['text'])
        
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
    import sys
    sys.exit(test_cufe_extraction())
