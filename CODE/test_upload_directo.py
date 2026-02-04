#!/usr/bin/env python3
"""
Test directo de subida de factura con S3
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from io import BytesIO
from app.database import SessionLocal
from app.services.invoice_v2_service import InvoiceV2Service

print("="*80)
print("🧪 TEST: Subida Directa de Factura con S3")
print("="*80)

# Usar un PDF de ejemplo
pdf_path = "CUFE/FACTURAS/FE15778.pdf"

if not os.path.exists(pdf_path):
    print(f"❌ PDF de prueba no encontrado: {pdf_path}")
    sys.exit(1)

print(f"\n📄 Usando PDF de prueba: {pdf_path}")

# Leer el PDF
with open(pdf_path, 'rb') as f:
    pdf_content = f.read()

print(f"   Tamaño: {len(pdf_content)} bytes")

# Crear BytesIO
file_obj = BytesIO(pdf_content)
file_obj.name = "test_factura.pdf"

print(f"\n✅ BytesIO creado correctamente")
print(f"   Posición inicial: {file_obj.tell()}")
print(f"   Tamaño: {len(file_obj.getvalue())} bytes")

# Crear servicio
db = SessionLocal()
try:
    service = InvoiceV2Service(db)
    
    print(f"\n🔧 Servicio creado")
    print(f"   S3Service disponible: {'✅' if service.s3_service else '❌'}")
    
    if not service.s3_service:
        print("❌ S3Service no está disponible")
        sys.exit(1)
    
    # Intentar crear factura
    print(f"\n📤 Creando factura con archivo...")
    
    invoice = service.create_invoice_from_provider_pdf(
        pdf_path,
        file_obj=file_obj,
        allow_without_cufe=True,
        overwrite=False
    )
    
    print(f"\n✅ Factura creada exitosamente!")
    print(f"   CUFE: {invoice.cufe[:30]}...")
    print(f"   Proveedor: {invoice.proveedor_nombre}")
    print(f"   Estado: {invoice.estado}")
    print(f"   S3 Key: {invoice.archivo_proveedor_s3_key or '❌ NO SUBIDO'}")
    print(f"   S3 URL: {invoice.archivo_proveedor_url[:80] if invoice.archivo_proveedor_url else '❌ NO GENERADA'}...")
    
    if invoice.archivo_proveedor_s3_key:
        print(f"\n🎉 ¡ÉXITO! El archivo se subió a S3 correctamente")
    else:
        print(f"\n❌ PROBLEMA: El archivo NO se subió a S3")
        print(f"   Revisa los logs arriba para ver el error")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
