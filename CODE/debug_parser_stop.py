#!/usr/bin/env python3
"""
Debug: ver dónde se detiene el parser
"""
import sys
sys.path.insert(0, 'src')

from app.database import SessionLocal
from app.models.invoice_v2 import InvoiceV2
from app.services.s3_service import S3Service
from app.services.pdf_parser_service import PDFParserService
import tempfile
import re

db = SessionLocal()
s3_service = S3Service()
parser = PDFParserService()

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

print(f'Longitud de la sección: {len(productos_section)} caracteres')
print(f'Total de líneas: {len(productos_section.split(chr(10)))}')

lines = productos_section.split('\n')

# Contar líneas que empiezan con número
lineas_con_numero = [l for l in lines if re.match(r'^\d{1,3}\s+', l.strip())]
print(f'Líneas que empiezan con número: {len(lineas_con_numero)}')

print('\nBuscando marcadores de STOP en la sección de productos...\n')

marcadores = ['TOTAL ITEMS', 'Datos Totales', 'Notas Finales', 'T O T A L', 'DETALLE DE VALORES', 'INFORMACION TRIBUTARIA']

for i, line in enumerate(lines):
    for marker in marcadores:
        if marker in line:
            print(f'❌ STOP en línea {i}: "{marker}" encontrado')
            print(f'   Línea completa: {line}')
            print(f'   Contexto (líneas {max(0,i-2)} a {min(len(lines),i+3)}):')
            for j in range(max(0, i-2), min(len(lines), i+3)):
                prefix = '>>>' if j == i else '   '
                print(f'   {prefix} {j}: {lines[j]}')
            print()

import os
os.unlink(tmp_path)
db.close()
