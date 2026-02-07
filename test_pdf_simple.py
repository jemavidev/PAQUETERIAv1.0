#!/usr/bin/env python3
"""
Script simple para probar extracción de fecha sin dependencias
"""
import re
import pdfplumber
from datetime import datetime

def extract_text_from_pdf(pdf_path: str, max_pages: int = 999) -> str:
    """Extrae texto de un PDF"""
    try:
        text_parts = []
        with pdfplumber.open(pdf_path) as pdf:
            pages_to_process = min(len(pdf.pages), max_pages)
            print(f"📄 Procesando {pages_to_process} de {len(pdf.pages)} páginas")
            
            for i in range(pages_to_process):
                page_text = pdf.pages[i].extract_text()
                if page_text:
                    text_parts.append(page_text)
        
        return '\n'.join(text_parts)
    except Exception as e:
        print(f"❌ Error: {e}")
        return ""

def extract_dian_date(text: str):
    """Extrae fecha de documento DIAN"""
    print(f"\n🔍 Buscando fecha en texto de {len(text)} caracteres...\n")
    
    # ESTRATEGIA 1: "Fecha y hora de expedición:"
    print("1️⃣ Buscando 'Fecha y hora de expedición:'...")
    pattern_expedicion = r'Fecha\s+y\s+hora\s+de\s+expedici[oó]n[\s:]+(\d{4})-(\d{1,2})-(\d{1,2})'
    match = re.search(pattern_expedicion, text, re.IGNORECASE)
    if match:
        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
        fecha = datetime(year, month, day)
        print(f"   ✅ ENCONTRADA: {fecha.strftime('%d/%m/%Y')}")
        print(f"   📝 Texto completo: {match.group(0)}")
        return fecha
    else:
        print(f"   ❌ No encontrada")
    
    # ESTRATEGIA 2: "Fecha de Emisión:"
    print("\n2️⃣ Buscando 'Fecha de Emisión:'...")
    patterns_emision = [
        r'Fecha\s+de\s+[Ee]misi[oó]n[\s:]+(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
        r'Fecha\s+de\s+[Ee]misi[oó]n[\s:]+(\d{4})[/-](\d{1,2})[/-](\d{1,2})',
    ]
    
    for pattern in patterns_emision:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            groups = match.groups()
            if len(groups[0]) == 4:  # YYYY-MM-DD
                year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
            else:  # DD-MM-YYYY
                day, month, year = int(groups[0]), int(groups[1]), int(groups[2])
            
            fecha = datetime(year, month, day)
            print(f"   ✅ ENCONTRADA: {fecha.strftime('%d/%m/%Y')}")
            print(f"   📝 Texto completo: {match.group(0)}")
            return fecha
    
    print(f"   ❌ No encontrada")
    
    # ESTRATEGIA 3: "Documento generado el:"
    print("\n3️⃣ Buscando 'Documento generado el:'...")
    patterns_generado = [
        r'Documento\s+generado\s+el[\s:]+(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
        r'Documento\s+generado\s+el[\s:]+(\d{4})[/-](\d{1,2})[/-](\d{1,2})',
    ]
    
    for pattern in patterns_generado:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            groups = match.groups()
            if len(groups[0]) == 4:  # YYYY-MM-DD
                year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
            else:  # DD-MM-YYYY
                day, month, year = int(groups[0]), int(groups[1]), int(groups[2])
            
            fecha = datetime(year, month, day)
            print(f"   ✅ ENCONTRADA: {fecha.strftime('%d/%m/%Y')}")
            print(f"   📝 Texto completo: {match.group(0)}")
            return fecha
    
    print(f"   ❌ No encontrada")
    return None

def test_pdf(pdf_path):
    """Test principal"""
    print(f"\n{'='*80}")
    print(f"🧪 TEST DE EXTRACCIÓN DE FECHA")
    print(f"{'='*80}")
    print(f"📄 Archivo: {pdf_path}")
    print(f"{'='*80}\n")
    
    # Extraer texto
    text = extract_text_from_pdf(pdf_path)
    
    if not text:
        print("❌ No se pudo extraer texto")
        return
    
    # Buscar fecha
    fecha = extract_dian_date(text)
    
    # Resultado final
    print(f"\n{'='*80}")
    print(f"📅 RESULTADO FINAL")
    print(f"{'='*80}")
    if fecha:
        print(f"   ✅ Fecha extraída: {fecha.strftime('%d/%m/%Y')}")
        print(f"   📆 Formato ISO: {fecha.strftime('%Y-%m-%d')}")
        print(f"\n   ✅ Fecha correcta esperada: 21/11/2025")
        if fecha.strftime('%d/%m/%Y') == '21/11/2025':
            print(f"   🎉 ¡CORRECTO! La fecha coincide")
        else:
            print(f"   ⚠️ INCORRECTO - La fecha no coincide")
    else:
        print(f"   ❌ No se pudo extraer la fecha")
    print(f"{'='*80}\n")
    
    # Mostrar primeras líneas del PDF para debugging
    print(f"\n{'='*80}")
    print(f"📝 PRIMERAS 20 LÍNEAS DEL PDF (para debugging)")
    print(f"{'='*80}")
    lines = text.split('\n')[:20]
    for i, line in enumerate(lines, 1):
        print(f"{i:2d}. {line}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python3 test_pdf_simple.py <ruta_al_pdf>")
        sys.exit(1)
    
    test_pdf(sys.argv[1])
