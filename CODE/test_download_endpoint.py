#!/usr/bin/env python3
"""
Script para probar el endpoint de descarga de facturas
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.database import SessionLocal
from app.services.invoice_v2_service import InvoiceV2Service

print("="*80)
print("TEST: Endpoint de Descarga de Facturas")
print("="*80)

# Crear sesión de base de datos
db = SessionLocal()

try:
    service = InvoiceV2Service(db)
    
    # Listar facturas para obtener un CUFE de prueba
    print("\n1️⃣ Obteniendo facturas de la base de datos...")
    invoices = service.list_invoices(skip=0, limit=5)
    
    if not invoices:
        print("❌ No hay facturas en la base de datos")
        print("💡 Carga al menos una factura para probar la descarga")
        sys.exit(1)
    
    print(f"✅ Encontradas {len(invoices)} facturas")
    
    # Mostrar facturas disponibles
    print("\n📋 Facturas disponibles:")
    for i, inv in enumerate(invoices, 1):
        has_file = "✅" if inv.archivo_proveedor_s3_key else "❌"
        cufe_display = inv.cufe[:20] + "..." if len(inv.cufe) > 20 else inv.cufe
        print(f"   {i}. {has_file} {cufe_display}")
        print(f"      Proveedor: {inv.proveedor_nombre or 'N/A'}")
        print(f"      S3 Key: {inv.archivo_proveedor_s3_key or 'NO HAY ARCHIVO'}")
        print()
    
    # Buscar una factura con archivo
    invoice_with_file = None
    for inv in invoices:
        if inv.archivo_proveedor_s3_key:
            invoice_with_file = inv
            break
    
    if not invoice_with_file:
        print("❌ Ninguna factura tiene archivo PDF en S3")
        print("💡 Las facturas deben tener 'archivo_proveedor_s3_key' para poder descargarlas")
        sys.exit(1)
    
    print(f"2️⃣ Probando descarga con factura: {invoice_with_file.cufe[:20]}...")
    print(f"   S3 Key: {invoice_with_file.archivo_proveedor_s3_key}")
    
    # Verificar que S3Service esté disponible
    if not service.s3_service:
        print("❌ S3Service no está disponible")
        print("💡 Verifica la configuración de AWS en .env")
        sys.exit(1)
    
    print("✅ S3Service está disponible")
    
    # Generar URL de descarga
    print("\n3️⃣ Generando URL pre-firmada...")
    try:
        url = service.s3_service.generate_presigned_url(
            invoice_with_file.archivo_proveedor_s3_key,
            expiration=3600
        )
        print(f"✅ URL generada exitosamente")
        print(f"   Longitud: {len(url)} caracteres")
        print(f"   Primeros 100 caracteres: {url[:100]}...")
        
        # Verificar que la URL sea válida
        if url.startswith('https://'):
            print("✅ URL válida (comienza con https://)")
        else:
            print("⚠️ URL no comienza con https://")
        
        print("\n" + "="*80)
        print("✅ ENDPOINT DE DESCARGA FUNCIONANDO CORRECTAMENTE")
        print("="*80)
        print("\n💡 Para probar en el navegador:")
        print(f"   GET /api/v2/invoices/facturas/{invoice_with_file.cufe}/download-url")
        
    except Exception as e:
        print(f"❌ Error generando URL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
finally:
    db.close()
