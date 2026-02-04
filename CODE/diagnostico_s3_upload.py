#!/usr/bin/env python3
"""
Diagnóstico: Por qué los archivos no se suben a S3
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("="*80)
print("🔍 DIAGNÓSTICO: Subida de Archivos a S3")
print("="*80)

# 1. Verificar configuración de AWS
print("\n1️⃣ Verificando configuración de AWS...")
from app.config import settings

print(f"   AWS_ACCESS_KEY_ID: {'✅ Configurado' if settings.aws_access_key_id else '❌ NO configurado'}")
print(f"   AWS_SECRET_ACCESS_KEY: {'✅ Configurado' if settings.aws_secret_access_key else '❌ NO configurado'}")
print(f"   AWS_S3_BUCKET: {settings.aws_s3_bucket}")
print(f"   AWS_REGION: {settings.aws_region}")

if not settings.aws_access_key_id or not settings.aws_secret_access_key:
    print("\n❌ PROBLEMA: Credenciales de AWS no configuradas")
    print("💡 Solución: Configura las credenciales en .env:")
    print("   AWS_ACCESS_KEY_ID=tu-access-key")
    print("   AWS_SECRET_ACCESS_KEY=tu-secret-key")
    sys.exit(1)

# 2. Verificar que S3Service se pueda inicializar
print("\n2️⃣ Verificando S3Service...")
try:
    from app.services.s3_service import S3Service
    s3_service = S3Service()
    print("✅ S3Service inicializado correctamente")
except Exception as e:
    print(f"❌ Error inicializando S3Service: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. Probar conexión a S3
print("\n3️⃣ Probando conexión a S3...")
try:
    if s3_service.test_connection():
        print("✅ Conexión a S3 exitosa")
    else:
        print("❌ Conexión a S3 falló")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error probando conexión: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 4. Probar subida de archivo de prueba
print("\n4️⃣ Probando subida de archivo de prueba...")
try:
    test_content = b"Test file content for invoice upload"
    test_key = "invoices/provider/TEST_diagnostico.pdf"
    
    print(f"   Subiendo archivo de prueba: {test_key}")
    url = s3_service.upload_file(test_content, test_key, content_type='application/pdf')
    print(f"✅ Archivo de prueba subido exitosamente")
    print(f"   URL: {url[:100]}...")
    
    # Limpiar archivo de prueba
    print("\n   Limpiando archivo de prueba...")
    s3_service.delete_file(test_key)
    print("✅ Archivo de prueba eliminado")
    
except Exception as e:
    print(f"❌ Error subiendo archivo de prueba: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 5. Verificar InvoiceV2Service
print("\n5️⃣ Verificando InvoiceV2Service...")
from app.database import SessionLocal
from app.services.invoice_v2_service import InvoiceV2Service

db = SessionLocal()
try:
    service = InvoiceV2Service(db)
    
    if service.s3_service:
        print("✅ InvoiceV2Service tiene S3Service disponible")
    else:
        print("❌ InvoiceV2Service NO tiene S3Service disponible")
        print("💡 Esto causará que los archivos no se suban a S3")
        sys.exit(1)
        
finally:
    db.close()

# 6. Verificar facturas existentes
print("\n6️⃣ Verificando facturas en base de datos...")
db = SessionLocal()
try:
    invoices = service.list_invoices(skip=0, limit=5)
    
    print(f"   Total de facturas: {len(invoices)}")
    
    with_s3 = sum(1 for inv in invoices if inv.archivo_proveedor_s3_key)
    without_s3 = len(invoices) - with_s3
    
    print(f"   Con archivo en S3: {with_s3}")
    print(f"   Sin archivo en S3: {without_s3}")
    
    if without_s3 > 0:
        print(f"\n⚠️ Hay {without_s3} facturas sin archivo en S3")
        print("   Esto puede ser porque:")
        print("   1. Se cargaron antes de configurar S3")
        print("   2. Hubo un error durante la subida")
        print("   3. El file_obj no se pasó correctamente")
        
finally:
    db.close()

print("\n" + "="*80)
print("✅ DIAGNÓSTICO COMPLETADO")
print("="*80)
print("\n💡 Si todo está ✅ pero las facturas nuevas no se suben:")
print("   1. Revisa los logs del servidor durante la carga")
print("   2. Busca mensajes: '📤 Intentando subir archivo a S3...'")
print("   3. Verifica que el file_obj se esté pasando correctamente")
print("\n📝 Para ver logs en tiempo real:")
print("   docker-compose logs -f app | grep -E '(📤|S3|subir)'")
