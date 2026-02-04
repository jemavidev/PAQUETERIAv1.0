#!/usr/bin/env python3
"""
Estrategias mejoradas para extraer CUFE de PDFs difíciles
"""
import re
from typing import Optional

def extract_cufe_mejorado(text: str) -> Optional[str]:
    """
    Extrae CUFE con estrategias múltiples y más agresivas
    """
    if not text:
        return None
    
    print(f"\n🔍 Probando estrategias de extracción...")
    
    # ESTRATEGIA 1: Patrón estándar (96 caracteres consecutivos)
    print("   1️⃣ Estrategia estándar (96 caracteres consecutivos)...")
    matches = re.findall(r'[0-9a-fA-F]{96}', text, re.IGNORECASE)
    if matches:
        cufe = matches[0].strip().replace('\n', '').replace(' ', '').lower()
        if len(cufe) == 96:
            print(f"      ✅ CUFE encontrado: {cufe[:20]}...")
            return cufe
    
    # ESTRATEGIA 2: CUFE con espacios (eliminar espacios y unir)
    print("   2️⃣ Estrategia con espacios...")
    # Buscar secuencias de hex con espacios opcionales
    pattern = r'([0-9a-fA-F\s]{100,200})'
    matches = re.findall(pattern, text, re.IGNORECASE)
    for match in matches:
        cleaned = match.replace(' ', '').replace('\n', '').replace('\t', '').strip()
        if len(cleaned) == 96 and re.match(r'^[0-9a-fA-F]{96}$', cleaned):
            print(f"      ✅ CUFE encontrado (con espacios): {cleaned[:20]}...")
            return cleaned.lower()
    
    # ESTRATEGIA 3: CUFE después de palabras clave
    print("   3️⃣ Estrategia con palabras clave...")
    keywords = ['CUFE', 'CUDE', 'CUDS', 'Código', 'codigo', 'Hash']
    for keyword in keywords:
        # Buscar keyword seguido de : o espacio, luego 96 caracteres hex
        pattern = rf'{keyword}[\s:]+([0-9a-fA-F\s]{{96,200}})'
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            cleaned = match.replace(' ', '').replace('\n', '').replace('\t', '').strip()
            if len(cleaned) == 96 and re.match(r'^[0-9a-fA-F]{96}$', cleaned):
                print(f"      ✅ CUFE encontrado (después de '{keyword}'): {cleaned[:20]}...")
                return cleaned.lower()
    
    # ESTRATEGIA 4: CUFE en múltiples líneas
    print("   4️⃣ Estrategia multi-línea...")
    lines = text.split('\n')
    for i in range(len(lines) - 3):
        # Unir hasta 4 líneas consecutivas
        combined = ''.join(lines[i:i+4])
        cleaned = combined.replace(' ', '').replace('\t', '').strip()
        # Buscar 96 caracteres hex en el texto combinado
        matches = re.findall(r'[0-9a-fA-F]{96}', cleaned, re.IGNORECASE)
        if matches:
            cufe = matches[0].lower()
            print(f"      ✅ CUFE encontrado (multi-línea): {cufe[:20]}...")
            return cufe
    
    # ESTRATEGIA 5: CUFE con guiones o separadores
    print("   5️⃣ Estrategia con separadores...")
    # Buscar patrones con guiones, puntos, etc.
    pattern = r'([0-9a-fA-F\-\.\s]{100,200})'
    matches = re.findall(pattern, text, re.IGNORECASE)
    for match in matches:
        cleaned = re.sub(r'[^0-9a-fA-F]', '', match)
        if len(cleaned) == 96 and re.match(r'^[0-9a-fA-F]{96}$', cleaned):
            print(f"      ✅ CUFE encontrado (con separadores): {cleaned[:20]}...")
            return cleaned.lower()
    
    # ESTRATEGIA 6: Buscar el patrón más largo de caracteres hex
    print("   6️⃣ Estrategia patrón más largo...")
    matches = re.findall(r'[0-9a-fA-F]{32,}', text, re.IGNORECASE)
    if matches:
        # Ordenar por longitud
        matches_sorted = sorted(matches, key=len, reverse=True)
        print(f"      Encontrados {len(matches)} patrones hex")
        print(f"      Más largo: {len(matches_sorted[0])} caracteres")
        
        # Si el más largo tiene 96 caracteres
        if len(matches_sorted[0]) == 96:
            cufe = matches_sorted[0].lower()
            print(f"      ✅ CUFE encontrado (patrón más largo): {cufe[:20]}...")
            return cufe
        
        # Si hay patrones cercanos a 96, intentar combinarlos
        for i in range(len(matches_sorted) - 1):
            combined = matches_sorted[i] + matches_sorted[i+1]
            cleaned = combined.replace(' ', '').replace('\n', '')
            if len(cleaned) == 96:
                print(f"      ✅ CUFE encontrado (combinando patrones): {cleaned[:20]}...")
                return cleaned.lower()
    
    print("   ❌ No se pudo extraer CUFE con ninguna estrategia")
    return None


# Test
if __name__ == "__main__":
    # Casos de prueba
    test_cases = [
        # Caso 1: CUFE estándar
        ("CUFE: 7569152b6d0396f9e5079cbac6bc56df5b0cd68fb260984838efb60f74d3f5ad1c33a597f92eed3e2318402d2eb418d2", True),
        
        # Caso 2: CUFE con espacios
        ("CUFE: 7569152b 6d0396f9 e5079cba c6bc56df 5b0cd68f b2609848 38efb60f 74d3f5ad 1c33a597 f92eed3e 2318402d 2eb418d2", True),
        
        # Caso 3: CUFE en múltiples líneas
        ("CUFE:\n7569152b6d0396f9e5079cbac6bc56df5b0cd68fb260984838efb60f74d3f5ad\n1c33a597f92eed3e2318402d2eb418d2", True),
        
        # Caso 4: CUFE con guiones
        ("Código: 7569152b-6d0396f9-e5079cba-c6bc56df-5b0cd68f-b2609848-38efb60f-74d3f5ad-1c33a597-f92eed3e-2318402d-2eb418d2", True),
    ]
    
    print("="*80)
    print("🧪 PROBANDO ESTRATEGIAS MEJORADAS")
    print("="*80)
    
    for i, (text, expected) in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}: {text[:60]}...")
        print(f"{'='*80}")
        
        cufe = extract_cufe_mejorado(text)
        
        if cufe and expected:
            print(f"\n✅ TEST PASADO")
        elif not cufe and not expected:
            print(f"\n✅ TEST PASADO (correctamente no encontró CUFE)")
        else:
            print(f"\n❌ TEST FALLIDO")
