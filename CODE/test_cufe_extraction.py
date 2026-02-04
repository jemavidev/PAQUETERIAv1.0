#!/usr/bin/env python3
"""
Script para diagnosticar por qué no se está extrayendo el CUFE de los PDFs
"""
from src.app.services.pdf_parser_service import PDFParserService
import sys
import re

# Probar con un PDF de ejemplo
pdf_path = '../CUFE/FACTURAS/FE15778.pdf'
parser = PDFParserService()

print('=== EXTRAYENDO TEXTO DEL PDF ===')
text = parser.extract_text_from_pdf(pdf_path, max_pages=2)
print(f'Longitud del texto: {len(text)} caracteres')
print(f'Primeros 500 caracteres:')
print(text[:500])
print()

print('=== BUSCANDO CUFE ===')
cufe = parser.extract_cufe(text)
if cufe:
    print(f'✅ CUFE encontrado: {cufe}')
    print(f'Longitud: {len(cufe)} caracteres')
else:
    print('❌ No se encontró CUFE')
    print()
    print('Buscando patrones de 96 caracteres hex en el texto...')
    matches = re.findall(r'[0-9a-fA-F]{96}', text, re.IGNORECASE)
    if matches:
        print(f'Encontrados {len(matches)} patrones de 96 caracteres hex')
        for i, match in enumerate(matches[:3]):
            print(f'{i+1}. {match[:50]}...')
    else:
        print('No se encontraron patrones de 96 caracteres hex')
        print()
        print('Buscando patrones más cortos (32+ caracteres hex)...')
        matches = re.findall(r'[0-9a-fA-F]{32,}', text, re.IGNORECASE)
        if matches:
            print(f'Encontrados {len(matches)} patrones de 32+ caracteres hex')
            for i, match in enumerate(matches[:5]):
                print(f'{i+1}. {match} (longitud: {len(match)})')
        else:
            print('No se encontraron patrones hexadecimales largos')
            print()
            print('Buscando palabras clave relacionadas con CUFE...')
            keywords = ['CUFE', 'CUDE', 'CUDS', 'Código', 'codigo', 'hash', 'SHA']
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    # Encontrar contexto alrededor de la palabra clave
                    idx = text.lower().find(keyword.lower())
                    context = text[max(0, idx-50):min(len(text), idx+200)]
                    print(f'Encontrado "{keyword}" en posición {idx}:')
                    print(f'  ...{context}...')
                    print()
