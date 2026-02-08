#!/usr/bin/env python3
"""
Listar todas las facturas en la BD
"""
import sys
sys.path.insert(0, 'src')
from app.database import SessionLocal
from app.models.invoice_v2 import InvoiceV2, InvoiceProductV2

db = SessionLocal()

print('=' * 80)
print('TODAS LAS FACTURAS EN LA BASE DE DATOS')
print('=' * 80)

facturas = db.query(InvoiceV2).all()

print(f'\nTotal de facturas: {len(facturas)}\n')

for factura in facturas:
    productos_count = len(factura.productos)
    print(f'📄 {factura.numero_factura or "SIN NUMERO"}')
    print(f'   CUFE: {factura.cufe[:20]}...{factura.cufe[-20:]}')
    print(f'   Productos: {productos_count}')
    print(f'   Emisor: {factura.dian_emisor_razon_social or "N/A"}')
    print(f'   Fecha: {factura.fecha_emision}')
    if factura.archivo_dian_s3_key:
        print(f'   DIAN S3: {factura.archivo_dian_s3_key}')
    print()

# Total de productos
total_productos = db.query(InvoiceProductV2).count()
print('=' * 80)
print(f'TOTAL DE PRODUCTOS EN BD: {total_productos}')
print('=' * 80)

db.close()
