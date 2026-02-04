#!/usr/bin/env python3
"""
Verificar estado de las facturas recién cargadas
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.database import SessionLocal
from app.models.invoice_v2 import InvoiceV2

print("="*80)
print("🔍 VERIFICANDO FACTURAS RECIÉN CARGADAS")
print("="*80)

db = SessionLocal()
try:
    # Obtener las últimas 5 facturas
    facturas = db.query(InvoiceV2).order_by(InvoiceV2.created_at.desc()).limit(5).all()
    
    if not facturas:
        print("\n❌ No hay facturas en la base de datos")
        sys.exit(1)
    
    print(f"\n📋 Últimas {len(facturas)} facturas:")
    print()
    
    for i, factura in enumerate(facturas, 1):
        print(f"{i}. CUFE: {factura.cufe[:30]}...")
        print(f"   Proveedor: {factura.proveedor_nombre or 'N/A'}")
        print(f"   Estado: {factura.estado}")
        print(f"   Creada: {factura.created_at}")
        print(f"   📦 archivo_proveedor_s3_key: {factura.archivo_proveedor_s3_key or '❌ NULL'}")
        print(f"   🔗 archivo_proveedor_url: {factura.archivo_proveedor_url[:80] if factura.archivo_proveedor_url else '❌ NULL'}...")
        
        if factura.archivo_proveedor_s3_key:
            print(f"   ✅ TIENE ARCHIVO EN S3 - Botón debería estar VERDE")
        else:
            print(f"   ❌ NO TIENE ARCHIVO EN S3 - Botón estará GRIS")
        print()
    
    # Contar facturas con y sin archivo
    total = len(facturas)
    con_archivo = sum(1 for f in facturas if f.archivo_proveedor_s3_key)
    sin_archivo = total - con_archivo
    
    print("="*80)
    print(f"📊 RESUMEN:")
    print(f"   Total: {total}")
    print(f"   Con archivo S3: {con_archivo} ✅")
    print(f"   Sin archivo S3: {sin_archivo} ❌")
    print("="*80)
    
    if sin_archivo > 0:
        print("\n⚠️ PROBLEMA DETECTADO:")
        print(f"   {sin_archivo} facturas NO tienen archivo en S3")
        print("\n💡 POSIBLES CAUSAS:")
        print("   1. El código actualizado no se está ejecutando")
        print("   2. Hay un error durante la subida a S3")
        print("   3. El file_obj no se está pasando correctamente")
        print("\n🔧 SOLUCIÓN:")
        print("   Revisa los logs del servidor durante la carga:")
        print("   docker logs paquetex_dev_app | grep -A 20 'Subiendo factura'")
    
finally:
    db.close()
