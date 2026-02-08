#!/usr/bin/env python3
"""
Verificar estado actual de productos por factura
"""
import sys
sys.path.insert(0, 'src')
from app.database import SessionLocal
from app.models.invoice_v2 import InvoiceV2, InvoiceProductV2

db = SessionLocal()

# Facturas objetivo
facturas = [
    ('006D-611', '6ee372e238cc82c3d95fa44faa0869cd5c6e0e45d51cef31b9828697aad65af8f2e3a89ff13f799961ad968c89503f8e', 20),
    ('2FE-438', '42b379089d6248bdf017653a109b885604f84cee6818f5dd0cfb249017825ed566d56b025aa3fa88bd10629e6a4bb62f', 10),
    ('FE-15778', '21bb002f269805b73ac22c5966cd9c91c3f13eacb76844986fd9b88c86f0305da41f432151997d3db36d96dfb0b10c13', 58),
    ('FELN-1141', '871b8264b3046ff36431c35dd57f97bb5d7d5c7fb4791571429b00ead6259a06f391ada28aed868c5de11c18614b27f31', 2),
]

print('=' * 80)
print('ESTADO ACTUAL DE PRODUCTOS POR FACTURA')
print('=' * 80)

total_actual = 0
total_esperado = 0

for numero, cufe, esperado in facturas:
    factura = db.query(InvoiceV2).filter_by(cufe=cufe).first()
    if factura:
        actual = len(factura.productos)
        total_actual += actual
        total_esperado += esperado
        status = '✅' if actual == esperado else '❌'
        print(f'{status} {numero}: {actual}/{esperado} productos')
        if factura.archivo_dian_s3_key:
            print(f'   S3: {factura.archivo_dian_s3_key}')
        if factura.archivo_dian_url:
            print(f'   URL: {factura.archivo_dian_url}')
    else:
        print(f'❌ {numero}: Factura no encontrada en BD')

print('=' * 80)
print(f'TOTAL: {total_actual}/{total_esperado} productos')
print(f'Faltantes: {total_esperado - total_actual}')
print('=' * 80)

db.close()
