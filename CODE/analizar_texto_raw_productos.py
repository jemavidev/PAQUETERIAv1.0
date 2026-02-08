#!/usr/bin/env python3
"""
Script para analizar el texto raw de los PDFs y encontrar por qué faltan productos
"""
import sys
import os
sys.path.insert(0, 'src')

from app.services.pdf_parser_service import PDFParserService
import re

parser = PDFParserService()

# Analizar 006D-611 que debería tener 20 productos pero solo extrae 18
cufe = '6ee372e238cc82c3d95fa44faa0869cd5c6e0e45d51cef31b9828697aad65af8f2e3a89ff13f799961ad968c89503f8e'
archivo = f'../CUFE/FACTURAS/{cufe}_20250724151930.pdf'

print('=' * 80)
print('ANÁLISIS DE TEXTO RAW: 006D-611')
print('=' * 80)

# Extraer texto completo
text = parser.extract_text_from_pdf(archivo)

print(f'\nLongitud total del texto: {len(text)} caracteres')
print(f'Número de líneas: {len(text.split(chr(10)))}')

# Buscar la sección de productos
lines = text.split('\n')

# Encontrar donde empieza la tabla de productos
producto_start_idx = None
for i, line in enumerate(lines):
    if 'Detalles de Productos' in line or ('Código' in line and 'Descripción' in line):
        producto_start_idx = i
        print(f'\n✅ Sección de productos encontrada en línea {i}')
        break

if not producto_start_idx:
    print('\n❌ NO SE ENCONTRÓ SECCIÓN DE PRODUCTOS')
    print('\nPRIMERAS 100 LÍNEAS:')
    for i, line in enumerate(lines[:100]):
        print(f'{i:4d}: {line[:120]}')
    sys.exit(1)

# Mostrar líneas alrededor de la sección de productos
print('\n' + '=' * 80)
print('LÍNEAS DE LA SECCIÓN DE PRODUCTOS')
print('=' * 80)

# Buscar líneas que parecen productos (empiezan con número)
productos_encontrados = []
for i in range(producto_start_idx, min(producto_start_idx + 200, len(lines))):
    line = lines[i].strip()
    
    # Buscar líneas que empiezan con número (posibles productos)
    if re.match(r'^\d{1,3}\s+', line):
        productos_encontrados.append((i, line))

print(f'\n📦 Líneas que parecen productos: {len(productos_encontrados)}')
print('\nPRIMERAS 25 LÍNEAS DE PRODUCTOS:')
for idx, (line_num, line) in enumerate(productos_encontrados[:25], 1):
    print(f'{idx:2d}. Línea {line_num:4d}: {line[:100]}')

# Buscar específicamente los productos 19 y 20
print('\n' + '=' * 80)
print('BUSCANDO PRODUCTOS 19 Y 20')
print('=' * 80)

for line_num, line in productos_encontrados:
    if line.startswith('19 ') or line.startswith('20 '):
        print(f'\n✅ ENCONTRADO en línea {line_num}:')
        print(f'   {line}')
        
        # Mostrar contexto (líneas antes y después)
        print(f'\n   Contexto (3 líneas antes y después):')
        for j in range(max(0, line_num-3), min(len(lines), line_num+4)):
            marker = '>>>' if j == line_num else '   '
            print(f'   {marker} {j:4d}: {lines[j][:100]}')

print('\n' + '=' * 80)
print('ANÁLISIS COMPLETADO')
print('=' * 80)
