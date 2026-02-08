#!/usr/bin/env python3
"""
Script para verificar que los productos se puedan consultar desde el servicio
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.invoice_v2_service import InvoiceV2Service

def main():
    print("=" * 80)
    print("🔍 VERIFICACIÓN DE PRODUCTOS VÍA SERVICIO")
    print("=" * 80)
    print()
    
    db = SessionLocal()
    
    try:
        service = InvoiceV2Service(db)
        
        # Obtener productos
        print("📦 Consultando productos...")
        productos = service.list_products(skip=0, limit=100)
        
        print(f"✅ Productos encontrados: {len(productos)}")
        print()
        
        if productos:
            print("📋 LISTA DE PRODUCTOS:")
            print("-" * 80)
            for i, prod in enumerate(productos[:20], 1):
                codigo = prod.codigo_producto or 'N/A'
                desc = (prod.descripcion or 'N/A')[:45]
                cant = prod.cantidad or 0
                precio = prod.precio_unitario or 0
                
                # Obtener datos de la factura
                proveedor = prod.factura.proveedor_nombre if prod.factura else 'N/A'
                numero = prod.factura.numero_factura if prod.factura else 'N/A'
                
                print(f"  {i:2d}. {codigo:15s} | {desc:45s} | {proveedor[:20]:20s} | {numero:15s}")
            
            if len(productos) > 20:
                print(f"\n  ... y {len(productos) - 20} productos más")
        else:
            print("⚠️  No se encontraron productos")
        
        print()
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    main()
