#!/usr/bin/env python3
"""
Script de prueba para verificar la integración Fase 1
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import inspect
from app.database import engine

def test_database_schema():
    """Verifica que las nuevas columnas existan en la base de datos"""
    inspector = inspect(engine)
    
    print("=" * 60)
    print("VERIFICACIÓN DE ESQUEMA DE BASE DE DATOS")
    print("=" * 60)
    
    # Verificar columnas en invoices
    print("\n✓ Verificando tabla 'invoices'...")
    invoices_columns = [col['name'] for col in inspector.get_columns('invoices')]
    
    expected_invoice_columns = [
        'buyer_nit',
        'buyer_razon_social',
        'buyer_direccion',
        'is_papyrus_buyer',
        'supplier_invoice_id'
    ]
    
    for col in expected_invoice_columns:
        if col in invoices_columns:
            print(f"  ✅ {col}")
        else:
            print(f"  ❌ {col} - NO ENCONTRADA")
    
    # Verificar columnas en invoice_items
    print("\n✓ Verificando tabla 'invoice_items'...")
    items_columns = [col['name'] for col in inspector.get_columns('invoice_items')]
    
    expected_items_columns = [
        'product_id',
        'matched_with_catalog',
        'match_confidence',
        'match_method'
    ]
    
    for col in expected_items_columns:
        if col in items_columns:
            print(f"  ✅ {col}")
        else:
            print(f"  ❌ {col} - NO ENCONTRADA")
    
    # Verificar foreign keys
    print("\n✓ Verificando foreign keys...")
    invoice_fks = inspector.get_foreign_keys('invoices')
    items_fks = inspector.get_foreign_keys('invoice_items')
    
    has_supplier_invoice_fk = any(
        'supplier_invoice_id' in fk['constrained_columns'] 
        for fk in invoice_fks
    )
    
    has_product_fk = any(
        'product_id' in fk['constrained_columns'] 
        for fk in items_fks
    )
    
    if has_supplier_invoice_fk:
        print("  ✅ FK invoices.supplier_invoice_id → supplier_invoices.id")
    else:
        print("  ❌ FK invoices.supplier_invoice_id NO ENCONTRADA")
    
    if has_product_fk:
        print("  ✅ FK invoice_items.product_id → products.id")
    else:
        print("  ❌ FK invoice_items.product_id NO ENCONTRADA")
    
    print("\n" + "=" * 60)
    print("VERIFICACIÓN COMPLETADA")
    print("=" * 60)


def test_models():
    """Verifica que los modelos se puedan importar correctamente"""
    print("\n" + "=" * 60)
    print("VERIFICACIÓN DE MODELOS")
    print("=" * 60)
    
    try:
        from app.models.invoice import Invoice, InvoiceItem, SupplierInvoice, IrregularityType
        print("\n✅ Modelos importados correctamente")
        
        # Verificar que los nuevos campos existan en los modelos
        print("\n✓ Verificando atributos del modelo Invoice...")
        invoice_attrs = ['buyer_nit', 'buyer_razon_social', 'is_papyrus_buyer', 'supplier_invoice_id']
        for attr in invoice_attrs:
            if hasattr(Invoice, attr):
                print(f"  ✅ {attr}")
            else:
                print(f"  ❌ {attr} - NO ENCONTRADO")
        
        print("\n✓ Verificando atributos del modelo InvoiceItem...")
        item_attrs = ['product_id', 'matched_with_catalog', 'match_confidence', 'match_method']
        for attr in item_attrs:
            if hasattr(InvoiceItem, attr):
                print(f"  ✅ {attr}")
            else:
                print(f"  ❌ {attr} - NO ENCONTRADO")
        
        print("\n✓ Verificando nuevos tipos de irregularidades...")
        new_types = ['COMPRADOR_NO_ES_PAPYRUS', 'PRODUCTO_NO_EN_CATALOGO', 'PRECIO_COMPRA_MAYOR_VENTA']
        for irr_type in new_types:
            if hasattr(IrregularityType, irr_type):
                print(f"  ✅ {irr_type}")
            else:
                print(f"  ❌ {irr_type} - NO ENCONTRADO")
        
    except Exception as e:
        print(f"\n❌ Error importando modelos: {e}")
        return False
    
    print("\n" + "=" * 60)
    return True


def test_s3_service():
    """Verifica que el servicio de S3 tenga los nuevos métodos"""
    print("\n" + "=" * 60)
    print("VERIFICACIÓN DE SERVICIO S3")
    print("=" * 60)
    
    try:
        from app.services.s3_storage_service import S3StorageService
        service = S3StorageService()
        
        print("\n✅ S3StorageService importado correctamente")
        
        # Verificar firma del método generate_presigned_url
        import inspect
        sig = inspect.signature(service.generate_presigned_url)
        params = list(sig.parameters.keys())
        
        print("\n✓ Verificando método generate_presigned_url...")
        if 'is_full_key' in params:
            print("  ✅ Parámetro 'is_full_key' agregado")
        else:
            print("  ❌ Parámetro 'is_full_key' NO ENCONTRADO")
        
        # Verificar firma del método download_pdf
        sig = inspect.signature(service.download_pdf)
        params = list(sig.parameters.keys())
        
        print("\n✓ Verificando método download_pdf...")
        if 'prefix' in params:
            print("  ✅ Parámetro 'prefix' agregado")
        else:
            print("  ❌ Parámetro 'prefix' NO ENCONTRADO")
        
    except Exception as e:
        print(f"\n❌ Error verificando S3Service: {e}")
        return False
    
    print("\n" + "=" * 60)
    return True


if __name__ == "__main__":
    print("\n🔍 INICIANDO PRUEBAS DE INTEGRACIÓN FASE 1\n")
    
    # Test 1: Verificar esquema de BD
    try:
        test_database_schema()
    except Exception as e:
        print(f"\n❌ Error en test de esquema: {e}")
        print("\n⚠️  Probablemente necesitas ejecutar: alembic upgrade head")
    
    # Test 2: Verificar modelos
    if not test_models():
        sys.exit(1)
    
    # Test 3: Verificar servicio S3
    if not test_s3_service():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ TODAS LAS PRUEBAS COMPLETADAS")
    print("=" * 60)
    print("\n📋 PRÓXIMOS PASOS:")
    print("  1. Ejecutar: cd CODE && alembic upgrade head")
    print("  2. Reiniciar el servidor")
    print("  3. Probar acceso a PDFs en /invoices/supplier-invoices")
    print("\n")
