#!/usr/bin/env python3
"""
Diagnosticar por qué no se extraen todos los productos
"""
import sys
import os
sys.path.insert(0, 'src')

from app.database import SessionLocal
from app.models.invoice_v2 import InvoiceV2
from app.services.pdf_parser_service import PDFParserService
from app.services.s3_service import S3Service
import tempfile
import re

db = SessionLocal()
parser = PDFParserService()
s3_service = S3Service()

# Factura a diagnosticar
cufe = '7569152b6d0396f9e5079cbac6bc56df5b0cd68fb260984838efb60f74d3f5ad1c33a597f92eed3e2318402d2eb418d2'
numero = 'FE-15778'

print('=' * 80)
print(f'DIAGNÓSTICO: {numero}')
print('=' * 80)

factura = db.query(InvoiceV2).filter_by(cufe=cufe).first()
if not factura:
    print('❌ Factura no encontrada')
    sys.exit(1)

print(f'✅ Factura encontrada')
print(f'   Productos actuales: {len(factura.productos)}')
print(f'   S3 Key: {factura.archivo_dian_s3_key}')

# Descargar PDF
print(f'\n📥 Descargando PDF...')
file_bytes = s3_service.download_file(factura.archivo_dian_s3_key)

with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
    tmp_file.write(file_bytes)
    tmp_path = tmp_file.name

print(f'✅ PDF descargado: {tmp_path}')

# Extraer texto completo
print(f'\n📄 Extrayendo texto del PDF...')
text = parser.extract_text_from_pdf(tmp_path, max_pages=999)

print(f'✅ Texto extraído: {len(text)} caracteres')

# Buscar sección de productos
print(f'\n🔍 Buscando sección de productos...')

patterns = [
    r'(?:Detalles de [Pp]roductos|Detalle de Ítems|DETALLE DE PRODUCTOS|DETALLE)([\s\S]+?)(?:Notas [Ff]inales|Datos [Tt]otales|TOTAL ITEMS|Observaciones|OBSERVACIONES)',
    r'(?:DESCRIPCIÓN|DESCRIPCION|Descripción del Producto)([\s\S]+?)(?:Notas [Ff]inales|Datos [Tt]otales|TOTAL ITEMS|Observaciones)',
]

productos_section = None
for i, pattern in enumerate(patterns):
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        productos_section = match.group(1)
        print(f'✅ Sección encontrada con patrón {i+1}')
        print(f'   Longitud: {len(productos_section)} caracteres')
        break

if not productos_section:
    print('❌ No se encontró sección de productos')
    print('\n📝 Primeros 2000 caracteres del texto:')
    print(text[:2000])
    os.unlink(tmp_path)
    sys.exit(1)

# Mostrar primeras 100 líneas de la sección
print(f'\n📋 Primeras 100 líneas de la sección de productos:')
print('=' * 80)
lines = productos_section.split('\n')
for i, line in enumerate(lines[:100]):
    if line.strip():
        print(f'{i+1:3d}: {line}')

# Buscar marcadores de fin
print(f'\n🛑 Buscando marcadores de fin en el texto completo...')
marcadores = ['Datos Totales', 'Notas Finales', 'TOTAL ITEMS', 'Observaciones', 'OBSERVACIONES']
for marcador in marcadores:
    if marcador in text:
        idx = text.find(marcador)
        print(f'✅ Encontrado "{marcador}" en posición {idx}')
        # Mostrar contexto
        start = max(0, idx - 100)
        end = min(len(text), idx + 100)
        print(f'   Contexto: ...{text[start:end]}...')

# Parsear productos
print(f'\n📦 Parseando productos...')
data = parser.parse_dian_document(tmp_path)
productos = data.get('productos', [])

print(f'✅ Productos extraídos: {len(productos)}')
print(f'\n📋 Lista de productos:')
for i, prod in enumerate(productos):
    print(f'{i+1:3d}. {prod.get("codigo_producto", "N/A"):15s} - {prod.get("descripcion", "N/A")[:60]}')

os.unlink(tmp_path)
db.close()
