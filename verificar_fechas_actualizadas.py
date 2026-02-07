#!/usr/bin/env python3
"""
Script para verificar que las fechas se actualizaron correctamente
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'CODE/src'))

from app.database import SessionLocal
from app.models.invoice_v2 import InvoiceV2

def verificar_fechas():
    """Verifica las fechas actualizadas"""
    print(f"\n{'='*80}")
    print(f"📅 VERIFICACIÓN DE FECHAS ACTUALIZADAS")
    print(f"{'='*80}\n")
    
    db = SessionLocal()
    
    try:
        # Obtener todas las facturas con CUFE
        facturas = db.query(InvoiceV2).filter(InvoiceV2.cufe.isnot(None)).order_by(InvoiceV2.fecha_emision.desc()).all()
        
        print(f"📊 Total de facturas con CUFE: {len(facturas)}\n")
        
        if not facturas:
            print("❌ No se encontraron facturas con CUFE")
            return
        
        print(f"{'CUFE (primeros 16)':<20} {'Proveedor':<30} {'Número':<15} {'Fecha':<12}")
        print(f"{'─'*20} {'─'*30} {'─'*15} {'─'*12}")
        
        for factura in facturas:
            cufe_corto = factura.cufe[:16] if factura.cufe else 'N/A'
            proveedor = (factura.proveedor_nombre or 'N/A')[:28]
            numero = (factura.numero_factura or 'N/A')[:13]
            fecha = factura.fecha_emision.strftime('%d/%m/%Y') if factura.fecha_emision else 'Sin fecha'
            
            print(f"{cufe_corto:<20} {proveedor:<30} {numero:<15} {fecha:<12}")
        
        print(f"\n{'='*80}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    verificar_fechas()
