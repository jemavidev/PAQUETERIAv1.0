#!/usr/bin/env python3
"""
Analiza en detalle los archivos con formato DESCONOCIDO
"""
import os
import sys
import re
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import pdfplumber
except ImportError:
    print("❌ Error: pdfplumber no está instalado")
    sys.exit(1)

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extrae texto de un PDF"""
    try:
        text_parts = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return '\n'.join(text_parts)
    except Exception as e:
        return f"ERROR: {e}"

def find_products_section(text: str) -> str:
    """Encuentra la sección de productos"""
    patterns = [
        r'Detalles de [Pp]roductos([\s\S]{0,3000})(?:Datos [Tt]otales|Notas|Observaciones)',
        r'DETALLE([\s\S]{0,3000})(?:Subtotal|SUBTOTAL)',
        r'Descripción([\s\S]{0,3000})(?:Subtotal|Total|TOTAL)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def main():
    cufe_dir = Path("/home/stk/Downloads/INVOICES FULL/CUFE")
    
    # Lista de archivos DESCONOCIDOS (primeros 5 para análisis)
    archivos_desconocidos = [
        "12-02-2025 - SABELUX DISTRIBUCIONES S.A.S - FESD-628.pdf",
        "20-03-2025 - SABELUX DISTRIBUCIONES S.A.S - FESD-694.pdf",
        "24-05-2025 - COMERCIALIZADORA RACOPI S.A.S. - FE-25426.pdf",
        "09-05-2025 - SOLUCIONES MAF SAS - 18239.pdf",
        "19-03-2025 - SOLUCIONES MAF SAS - 1801-13166.pdf",
    ]
    
    print("=" * 100)
    print("🔍 ANÁLISIS DETALLADO DE FORMATOS DESCONOCIDOS")
    print("=" * 100)
    
    for i, filename in enumerate(archivos_desconocidos, 1):
        pdf_path = cufe_dir / filename
        
        if not pdf_path.exists():
            print(f"\n❌ Archivo {i}: No encontrado - {filename}")
            continue
        
        print(f"\n{'='*100}")
        print(f"📄 ARCHIVO {i}/5: {filename[:70]}...")
        print(f"{'='*100}")
        
        text = extract_text_from_pdf(str(pdf_path))
        if text.startswith("ERROR"):
            print(f"❌ {text}")
            continue
        
        section = find_products_section(text)
        if not section:
            print("❌ No se encontró sección de productos")
            # Mostrar primeras líneas del texto para debug
            print("\n📝 Primeras 50 líneas del documento:")
            lines = text.split('\n')
            for j, line in enumerate(lines[:50], 1):
                if line.strip():
                    print(f"{j:2d}: {line[:90]}")
            continue
        
        lines = section.split('\n')
        
        print(f"\n📝 Primeras 40 líneas de la sección de productos:")
        print("-" * 100)
        
        for j, line in enumerate(lines[:40], 1):
            if line.strip():
                # Marcar líneas que parecen productos
                marker = ""
                if re.match(r'^\d{1,3}\s+', line):
                    marker = "🔹"
                elif re.match(r'^[A-ZÁÉÍÓÚÑ]', line) and len(line) > 10:
                    marker = "📝"
                
                print(f"{j:2d} {marker:2s} {line[:95]}")
        
        print("-" * 100)
    
    print("\n" + "=" * 100)
    print("✅ Análisis completado")
    print("=" * 100)

if __name__ == '__main__':
    main()
