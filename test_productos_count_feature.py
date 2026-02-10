#!/usr/bin/env python3
"""
Script de prueba para verificar el conteo de productos en facturas
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'CODE', 'src'))

from app.database import SessionLocal
from app.models.invoice_v2 import InvoiceV2, InvoiceProductV2
from sqlalchemy import func

def test_productos_count():
    """Prueba el conteo de productos por factura"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("PRUEBA: Conteo de Productos en Facturas")
        print("=" * 80)
        
        # Obtener facturas con estado 'completo' o 'validado'
        facturas = db.query(InvoiceV2).filter(
            InvoiceV2.estado.in_(['completo', 'validado'])
        ).limit(10).all()
        
        print(f"\n✅ Encontradas {len(facturas)} facturas con estado 'completo' o 'validado'\n")
        
        if not facturas:
            print("⚠️  No hay facturas con estado 'completo' o 'validado' para probar")
            return
        
        # Obtener CUFEs
        cufes = [f.cufe for f in facturas]
        
        # Contar productos por CUFE
        counts = db.query(
            InvoiceProductV2.cufe,
            func.count(InvoiceProductV2.id).label('count')
        ).filter(
            InvoiceProductV2.cufe.in_(cufes)
        ).group_by(InvoiceProductV2.cufe).all()
        
        productos_count = {cufe: count for cufe, count in counts}
        
        print("RESULTADOS:")
        print("-" * 80)
        print(f"{'CUFE':<20} {'Proveedor':<30} {'Estado':<15} {'Productos':<10}")
        print("-" * 80)
        
        for factura in facturas:
            cufe_short = factura.cufe[:16] + "..."
            proveedor = (factura.dian_emisor_razon_social or factura.proveedor_nombre or "N/A")[:28]
            count = productos_count.get(factura.cufe, 0)
            
            print(f"{cufe_short:<20} {proveedor:<30} {factura.estado:<15} {count:<10}")
        
        print("-" * 80)
        print(f"\n✅ Total de facturas analizadas: {len(facturas)}")
        print(f"✅ Facturas con productos: {len([c for c in productos_count.values() if c > 0])}")
        print(f"✅ Total de productos: {sum(productos_count.values())}")
        
        # Verificar que el endpoint devuelve el conteo
        print("\n" + "=" * 80)
        print("VERIFICACIÓN DEL ENDPOINT")
        print("=" * 80)
        
        from app.routes.invoices_v2_routes import list_invoices
        
        # Simular llamada al endpoint
        result = list_invoices(
            skip=0,
            limit=10,
            search=None,
            estado='completo',
            fecha_desde=None,
            fecha_hasta=None,
            db=db
        )
        
        print(f"\n✅ Endpoint devuelve {len(result['items'])} facturas")
        
        for item in result['items'][:5]:  # Mostrar solo las primeras 5
            cufe_short = item['cufe'][:16] + "..."
            proveedor = (item.get('dian_emisor_razon_social') or item.get('proveedor_nombre') or "N/A")[:28]
            count = item.get('productos_count', 'N/A')
            
            print(f"  • {cufe_short} - {proveedor} - {count} productos")
        
        print("\n✅ PRUEBA COMPLETADA EXITOSAMENTE")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_productos_count()
