#!/usr/bin/env python3
"""
Script para probar los endpoints del dashboard de invoices
"""

import sys
sys.path.insert(0, 'CODE/src')

from app.database import SessionLocal
from app.models.invoice import SupplierInvoice, SupplierInvoiceStatus, Invoice
from sqlalchemy import func

def test_stats():
    """Prueba el endpoint de stats"""
    print("🧪 Probando stats endpoint...")
    db = SessionLocal()
    
    try:
        total = db.query(func.count(SupplierInvoice.id)).scalar() or 0
        print(f"  ✅ Total facturas: {total}")
        
        processed = db.query(func.count(SupplierInvoice.id)).filter(
            SupplierInvoice.status == SupplierInvoiceStatus.PROCESSED
        ).scalar() or 0
        print(f"  ✅ Procesadas: {processed}")
        
        pending = db.query(func.count(SupplierInvoice.id)).filter(
            SupplierInvoice.status.in_([SupplierInvoiceStatus.PENDING, SupplierInvoiceStatus.CUFE_EXTRACTED])
        ).scalar() or 0
        print(f"  ✅ Pendientes: {pending}")
        
        # Calcular valor total
        total_value_raw = db.query(func.sum(Invoice.total_neto)).filter(
            Invoice.id.in_(
                db.query(SupplierInvoice.processed_invoice_id).filter(
                    SupplierInvoice.processed_invoice_id.isnot(None)
                )
            )
        ).scalar()
        
        total_value = int(total_value_raw) if total_value_raw else 0
        print(f"  ✅ Valor total: ${total_value:,}")
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_list():
    """Prueba el endpoint de list"""
    print("\n🧪 Probando list endpoint...")
    db = SessionLocal()
    
    try:
        invoices = db.query(SupplierInvoice).order_by(
            SupplierInvoice.uploaded_at.desc()
        ).limit(5).all()
        
        print(f"  ✅ Encontradas {len(invoices)} facturas")
        
        for inv in invoices[:3]:
            print(f"    - ID: {inv.id}, Status: {inv.status.value}, CUFE: {inv.cufe[:20] if inv.cufe else 'N/A'}...")
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 Probando endpoints del dashboard de invoices")
    print("=" * 60)
    
    stats_ok = test_stats()
    list_ok = test_list()
    
    print("\n" + "=" * 60)
    if stats_ok and list_ok:
        print("✅ Todos los tests pasaron correctamente")
        sys.exit(0)
    else:
        print("❌ Algunos tests fallaron")
        sys.exit(1)
