#!/usr/bin/env python3
"""
Script simple para diagnosticar extracción de CUFE
"""
import re
import sys

try:
    import pdfplumber
except ImportError:
    print("ERROR: pdfplumber no está instalado")
    print("Instalar con: pip install pdfplumber")
    sys.exit(1)

def extract_text_from_pdf(pdf_path, max_pages=5):
    """Extrae texto de un PDF"""
    try:
        text_parts = []
        with pdfplumber.open(pdf_path) as pdf:
            pages_to_process = min(len(pdf.pages), max_pages)
            
            for i in range(pages_to_process):
                page_text = pdf.pages[i].extract_text()
                if page_text:
                    text_parts.append(page_text)
        
        return '\n'.join(text_parts)
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

def extract_cufe(text):
    """Extrae el código CUFE (96 caracteres hexadecimales)"""
    # Buscar patrón de 96 caracteres hex
    matches = re.findall(r'[0-9a-fA-F]{96}', text, re.IGNORECASE)
    
    if matches:
        cufe = matches[0]
        cufe = cufe.strip().replace('\n', '').replace(' ', '')
        
        if len(cufe) == 96:
            return cufe.lower()
    
    return None

# Probar con varios PDFs
pdf_files = [
    'CUFE/FACTURAS/FE15778.pdf',
    'CUFE/FACTURAS/FV09006851640112400000125.pdf',
    'CUFE/FACTURAS/ad00454539650892500016306.pdf',
]

for pdf_file in pdf_files:
    print(f'\n{"="*80}')
    print(f'Analizando: {pdf_file}')
    print(f'{"="*80}')
    
    try:
        text = extract_text_from_pdf(pdf_file, max_pages=2)
        print(f'✓ Texto extraído: {len(text)} caracteres')
        
        # Mostrar primeros 300 caracteres
        print(f'\nPrimeros 300 caracteres:')
        print(text[:300])
        print('...')
        
        # Buscar CUFE
        cufe = extract_cufe(text)
        if cufe:
            print(f'\n✅ CUFE ENCONTRADO: {cufe}')
            print(f'   Longitud: {len(cufe)} caracteres')
        else:
            print(f'\n❌ NO SE ENCONTRÓ CUFE')
            
            # Buscar patrones más cortos
            print('\nBuscando patrones hexadecimales largos (32+ caracteres)...')
            matches = re.findall(r'[0-9a-fA-F]{32,}', text, re.IGNORECASE)
            if matches:
                print(f'Encontrados {len(matches)} patrones:')
                for i, match in enumerate(matches[:5]):
                    print(f'  {i+1}. {match[:60]}... (longitud: {len(match)})')
            else:
                print('No se encontraron patrones hexadecimales largos')
            
            # Buscar palabras clave
            print('\nBuscando palabras clave...')
            keywords = ['CUFE', 'CUDE', 'CUDS', 'Código', 'codigo']
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    idx = text.lower().find(keyword.lower())
                    context = text[max(0, idx-30):min(len(text), idx+150)]
                    print(f'  "{keyword}" encontrado: ...{context}...')
    
    except FileNotFoundError:
        print(f'❌ Archivo no encontrado: {pdf_file}')
    except Exception as e:
        print(f'❌ Error: {e}')

print(f'\n{"="*80}')
print('Análisis completado')
print(f'{"="*80}')
