#!/usr/bin/env python3
"""
Verifica el estado de las facturas de proveedor recién subidas
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.models import SupplierInvoice
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

print("\n" + "="*80)
print("📊 ESTADO DE FACTURAS DE PROVEEDOR")
print("="*80 + "\n")

# Obtener todas las facturas
invoices = db.query(SupplierInvoice).order_by(SupplierInvoice.id.desc()).all()

if not invoices:
    print("❌ No hay facturas en la base de datos\n")
    sys.exit(0)

print(f"Total de facturas: {len(invoices)}\n")

for invoice in invoices:
    print(f"ID: {invoice.id}")
    print(f"  Archivo: {invoice.original_filename}")
    print(f"  Hash: {invoice.original_file_hash}")
    print(f"  Path guardado: {invoice.original_file_path or 'NO GUARDADO ❌'}")
    print(f"  CUFE: {invoice.cufe or 'Sin CUFE'}")
    print(f"  Fecha: {invoice.created_at}")
    
    # Verificar si existe en S3 o localmente
    if invoice.original_file_path:
        if invoice.original_file_path.startswith('supplier-invoices/'):
            print(f"  ✅ Path S3 correcto")
        else:
            print(f"  ⚠️ Path S3 incorrecto: {invoice.original_file_path}")
    
    # Verificar archivo local
    local_path = f"/app/src/uploads/supplier-invoices/{invoice.original_file_hash}.pdf"
    if os.path.exists(local_path):
        size = os.path.getsize(local_path)
        print(f"  ✅ Archivo local existe ({size} bytes)")
    else:
        print(f"  ❌ Archivo local NO existe")
    
    print()

print("="*80)
print("\n💡 RECOMENDACIÓN:")
print()

# Contar facturas sin path
sin_path = sum(1 for inv in invoices if not inv.original_file_path)
if sin_path > 0:
    print(f"⚠️ Hay {sin_path} facturas sin PDF guardado")
    print()
    print("SOLUCIÓN:")
    print("1. Eliminar estas facturas:")
    print("   cd CODE")
    print("   python3 reparar_pdfs_supplier_invoices.py")
    print()
    print("2. Reiniciar el servidor:")
    print("   docker-compose restart web")
    print()
    print("3. Re-subir las facturas desde el navegador")
else:
    print("✅ Todas las facturas tienen path guardado")
    print()
    print("Si aún tienes error 404, verifica:")
    print("1. Que el servidor esté corriendo")
    print("2. Que S3 esté habilitado en .env")
    print("3. Los logs del servidor al subir")

print()
