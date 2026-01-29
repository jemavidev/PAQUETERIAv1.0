#!/usr/bin/env python3
"""
Script para reprocesar facturas de proveedores existentes
y extraer correctamente los datos (proveedor, fecha, número)
"""

import sys
import os
sys.path.insert(0, 'CODE/src')

from app.database import SessionLocal
from app.models.invoice import SupplierInvoice
from app.services.supplier_invoice_service import SupplierInvoiceService

def reprocesar_facturas():
    """Reprocesa todas las facturas de proveedores para extraer datos"""
    print("=" * 70)
    print("🔄 REPROCESANDO FACTURAS DE PROVEEDORES")
    print("=" * 70)
    
    db = SessionLocal()
    service = SupplierInvoiceService(db)
    
    try:
        # Obtener todas las facturas
        facturas = db.query(SupplierInvoice).all()
        total = len(facturas)
        
        print(f"\n📊 Total de facturas a reprocesar: {total}\n")
        
        actualizadas = 0
        errores = 0
        
        for i, factura in enumerate(facturas, 1):
            print(f"[{i}/{total}] Procesando factura ID {factura.id}: {factura.original_filename}")
            
            try:
                # Buscar el PDF
                pdf_paths = [
                    f"/app/src/uploads/supplier-invoices/{factura.original_file_hash}.pdf",
                    f"/app/src/uploads/invoices/{factura.original_file_hash}.pdf",
                ]
                
                pdf_path = None
                for path in pdf_paths:
                    if os.path.exists(path):
                        pdf_path = path
                        break
                
                if not pdf_path:
                    print(f"  ⚠️  PDF no encontrado")
                    errores += 1
                    continue
                
                # Extraer información
                info = service.extract_basic_info_from_pdf(pdf_path)
                
                # Actualizar solo si hay cambios
                cambios = []
                
                if info.get('supplier_name') and info['supplier_name'] != factura.supplier_name:
                    factura.supplier_name = info['supplier_name']
                    cambios.append(f"Proveedor: {info['supplier_name']}")
                
                if info.get('supplier_nit') and info['supplier_nit'] != factura.supplier_nit:
                    factura.supplier_nit = info['supplier_nit']
                    cambios.append(f"NIT: {info['supplier_nit']}")
                
                if info.get('invoice_number') and info['invoice_number'] != factura.invoice_number:
                    factura.invoice_number = info['invoice_number']
                    cambios.append(f"Número: {info['invoice_number']}")
                
                if info.get('invoice_date') and info['invoice_date'] != factura.invoice_date:
                    factura.invoice_date = info['invoice_date']
                    cambios.append(f"Fecha: {info['invoice_date'].strftime('%Y-%m-%d')}")
                
                if info.get('total_amount') and info['total_amount'] != factura.total_amount:
                    factura.total_amount = info['total_amount']
                    cambios.append(f"Total: ${info['total_amount']:,}")
                
                if cambios:
                    db.commit()
                    actualizadas += 1
                    print(f"  ✅ Actualizada: {', '.join(cambios)}")
                else:
                    print(f"  ℹ️  Sin cambios")
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                errores += 1
                db.rollback()
                continue
        
        print("\n" + "=" * 70)
        print(f"✅ Proceso completado")
        print(f"   Total procesadas: {total}")
        print(f"   Actualizadas: {actualizadas}")
        print(f"   Errores: {errores}")
        print(f"   Sin cambios: {total - actualizadas - errores}")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    reprocesar_facturas()
