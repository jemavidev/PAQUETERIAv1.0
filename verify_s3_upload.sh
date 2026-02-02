#!/bin/bash

echo "🔍 Verificando facturas con PDF en S3..."
echo ""

ssh ubuntu@staging "docker exec paqueteria_staging_app python -c \"
from src.app.database import SessionLocal
from src.app.models.invoice_v2 import InvoiceV2

db = SessionLocal()
total = db.query(InvoiceV2).count()
con_s3 = db.query(InvoiceV2).filter(InvoiceV2.archivo_proveedor_s3_key.isnot(None)).count()

print(f'📊 Estadísticas:')
print(f'   Total de facturas: {total}')
print(f'   Con PDF en S3: {con_s3}')
print(f'   Sin PDF en S3: {total - con_s3}')
print('')

if con_s3 > 0:
    print('✅ Últimas facturas con PDF en S3:')
    facturas = db.query(InvoiceV2).filter(
        InvoiceV2.archivo_proveedor_s3_key.isnot(None)
    ).order_by(InvoiceV2.created_at.desc()).limit(3).all()
    
    for f in facturas:
        print(f'   - CUFE: {f.cufe[:20]}...')
        print(f'     S3 Key: {f.archivo_proveedor_s3_key}')
        print(f'     Proveedor: {f.proveedor_nombre}')
        print(f'     Fecha: {f.created_at}')
        print('')

db.close()
\"" 2>&1 | grep -v "INFO sqlalchemy"
