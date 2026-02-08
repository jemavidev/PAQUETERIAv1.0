#!/usr/bin/env python3
"""
Script para probar el endpoint de productos directamente
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import SessionLocal
from app.services.invoice_v2_service import InvoiceV2Service

# Crear sesión de BD
db = SessionLocal()

try:
    service = InvoiceV2Service(db)
    
    # Probar el endpoint de productos
    print("=" * 80)
    print("PROBANDO ENDPOINT DE PRODUCTOS")
    print("=" * 80)
    
    # Listar productos (sin filtros)
    productos = service.list_products(skip=0, limit=100)
    
    print(f"\n✅ Total de productos encontrados: {len(productos)}")
    
    if productos:
        print("\n📦 PRIMEROS 5 PRODUCTOS:")
        print("-" * 80)
        for i, prod in enumerate(productos[:5], 1):
            print(f"\n{i}. Código: {prod.codigo_producto or 'SIN CÓDIGO'}")
            print(f"   Descripción: {prod.descripcion[:50] if prod.descripcion else 'N/A'}...")
            print(f"   CUFE: {prod.cufe[:20]}...")
            print(f"   Proveedor (factura): {prod.factura.proveedor_nombre or 'N/A'}")
            print(f"   Precio: ${prod.precio_unitario:,.0f}" if prod.precio_unitario else "   Precio: N/A")
            print(f"   Fecha: {prod.fecha_compra}")
    else:
        print("\n⚠️ NO SE ENCONTRARON PRODUCTOS")
        print("\nVerificando facturas con productos...")
        
        from app.models.invoice_v2 import InvoiceV2
        facturas = db.query(InvoiceV2).all()
        print(f"\nTotal de facturas: {len(facturas)}")
        
        for factura in facturas:
            print(f"\n  - {factura.numero_factura or factura.cufe[:20]}")
            print(f"    Productos: {len(factura.productos)}")
            print(f"    Estado: {factura.estado}")
            print(f"    DIAN validado: {factura.dian_validado}")
    
    print("\n" + "=" * 80)
    print("PRUEBA COMPLETADA")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
