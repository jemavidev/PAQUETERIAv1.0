#!/usr/bin/env python3
"""
Análisis detallado de formatos de productos en CUFE
Muestra ejemplos reales de cada formato detectado
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
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def main():
    cufe_dir = Path("/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE/CUFE")
    
    # Archivos de muestra para cada formato
    samples = {
        'FORMATO_1': '8a73ab009b4eb0933087c42f46d48309a1ea55b2432f5df449f1dad9c3d3e4cb026cb19f6a82285b0a50ea1c4c8f62d0.pdf',
        'FORMATO_2': '03391745b16d6324d08bb833cbc3f4e531e7c97ee726fc2a962b0c043143d19de8101eb991a1236376eda6a9e0664a13.pdf',
        'FORMATO_5': 'fd7892b8723009bb46c2f065caa325144d76ee5e3eada87cf2dce405dc23b0b4e5938e060c94fa4c3f846220c56dc4e1.pdf',
    }
    
    print("=" * 100)
    print("🔍 ANÁLISIS DETALLADO DE FORMATOS")
    print("=" * 100)
    
    for formato, filename in samples.items():
        pdf_path = cufe_dir / filename
        
        if not pdf_path.exists():
            print(f"\n❌ {formato}: Archivo no encontrado")
            continue
        
        print(f"\n{'='*100}")
        print(f"📄 {formato}")
        print(f"{'='*100}")
        print(f"Archivo: {filename[:70]}...")
        
        text = extract_text_from_pdf(str(pdf_path))
        if text.startswith("ERROR"):
            print(f"❌ {text}")
            continue
        
        section = find_products_section(text)
        if not section:
            print("❌ No se encontró sección de productos")
            continue
        
        lines = section.split('\n')
        
        print(f"\n📝 Primeras 30 líneas de la sección de productos:")
        print("-" * 100)
        
        for i, line in enumerate(lines[:30], 1):
            if line.strip():
                # Marcar líneas que parecen productos
                marker = ""
                if re.match(r'^\d{1,3}\s+', line):
                    marker = "🔹"
                elif re.match(r'^[A-ZÁÉÍÓÚÑ]', line) and len(line) > 10:
                    marker = "📝"
                
                print(f"{i:2d} {marker:2s} {line[:95]}")
        
        print("-" * 100)
    
    print("\n" + "=" * 100)
    print("✅ Análisis completado")
    print("=" * 100)

if __name__ == '__main__':
    main()
