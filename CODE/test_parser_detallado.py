#!/usr/bin/env python3
"""
Test detallado del parser para ver qué líneas no se capturan
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

cufe = '7569152b6d0396f9e5079cbac6bc56df5b0cd68fb260984838efb60f74d3f5ad1c33a597f92eed3e2318402d2eb418d2'

factura = db.query(InvoiceV2).filter_by(cufe=cufe).first()
file_bytes = s3_service.download_file(factura.archivo_dian_s3_key)

with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
    tmp_file.write(file_bytes)
    tmp_path = tmp_file.name

text = parser.extract_text_from_pdf(tmp_path, max_pages=999)

# Buscar sección de productos
pattern = r'(?:Detalles de [Pp]roductos|Detalle de Ítems|DETALLE DE PRODUCTOS|DETALLE)([\s\S]+?)(?:Notas [Ff]inales|Datos [Tt]otales|TOTAL ITEMS|Observaciones|OBSERVACIONES)'
match = re.search(pattern, text, re.IGNORECASE)
productos_section = match.group(1)

lines = productos_section.split('\n')

print('=' * 80)
print('ANÁLISIS LÍNEA POR LÍNEA')
print('=' * 80)

# Contar líneas que parecen productos (empiezan con número)
lineas_producto = []
for i, line in enumerate(lines):
    line = line.strip()
    if re.match(r'^\d{1,3}\s+', line):
        lineas_producto.append((i, line))

print(f'\nTotal de líneas que empiezan con número: {len(lineas_producto)}')
print(f'\nPrimeras 20 líneas de la sección de productos (RAW):\n')
for i, line in enumerate(lines[:20]):
    print(f'{i:3d}: [{line}]')

print(f'\nPrimeras 60 líneas que parecen productos:\n')

for i, (idx, line) in enumerate(lineas_producto[:60]):
    # Verificar si tiene código + unidad + cantidad + precio
    has_codigo = bool(re.search(r'\d{1,13}\s+(?:\d{2}|EA|PC|UN|UND|NIU|PK|BX)', line))
    has_precio = bool(re.search(r'\$\s*[0-9.,]+', line))
    
    status = '✅' if (has_codigo and has_precio) else '❌'
    print(f'{status} {i+1:2d}. Línea {idx:3d}: {line[:80]}')

os.unlink(tmp_path)
db.close()
