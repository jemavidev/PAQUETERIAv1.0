#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')

from app.database import SessionLocal
from app.models.invoice_v2 import InvoiceV2
from app.services.s3_service import S3Service
from app.services.pdf_parser_service import PDFParserService
import tempfile
import logging

# Activar logging detallado
logging.basicConfig(level=logging.INFO)

db = SessionLocal()
s3_service = S3Service()
parser = PDFParserService()

cufe = '7569152b6d0396f9e5079cbac6bc56df5b0cd68fb260984838efb60f74d3f5ad1c33a597f92eed3e2318402d2eb418d2'

factura = db.query(InvoiceV2).filter_by(cufe=cufe).first()
file_bytes = s3_service.download_file(factura.archivo_dian_s3_key)

with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
    tmp_file.write(file_bytes)
    tmp_path = tmp_file.name

print('\n' + '=' * 80)
print('PARSEANDO CON LOGGING DETALLADO')
print('=' * 80 + '\n')

data = parser.parse_dian_document(tmp_path)
productos = data.get('productos', [])

print('\n' + '=' * 80)
print(f'RESULTADO: {len(productos)} productos extraídos')
print('=' * 80)

import os
os.unlink(tmp_path)
db.close()
