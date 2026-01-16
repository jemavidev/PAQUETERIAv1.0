#!/usr/bin/env python3
"""
Script para reparar supplier_invoices que no tienen PDF guardado
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.database import SessionLocal
from app.models.invoice import SupplierInvoice

def main():
    print("\n" + "=" * 70)
    print("🔧 REPARACIÓN DE PDFs DE SUPPLIER INVOICES")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        # Buscar supplier_invoices sin original_file_path
        invoices = db.query(SupplierInvoice).filter(
            SupplierInvoice.original_file_path.is_(None),
            SupplierInvoice.original_file_hash.isnot(None)
        ).all()
        
        print(f"\n📊 Encontradas {len(invoices)} facturas sin PDF guardado")
        
        if not invoices:
            print("\n✅ No hay facturas que reparar")
            return
        
        print("\n⚠️  PROBLEMA IDENTIFICADO:")
        print("   Las facturas fueron subidas pero el PDF no se guardó en S3")
        print("   Esto ocurrió porque el código de subida tenía un bug")
        print("\n📋 SOLUCIÓN:")
        print("   1. El bug ya fue corregido en el código")
        print("   2. Las nuevas facturas se guardarán correctamente")
        print("   3. Para las facturas existentes, necesitas:")
        print("      - Re-subir los PDFs manualmente, O")
        print("      - Eliminar estas facturas y subirlas de nuevo")
        
        print("\n" + "=" * 70)
        print("FACTURAS AFECTADAS:")
        print("=" * 70)
        
        for inv in invoices:
            print(f"\n  ID: {inv.id}")
            print(f"  Archivo: {inv.original_filename}")
            print(f"  Hash: {inv.original_file_hash}")
            print(f"  Fecha: {inv.uploaded_at}")
            print(f"  Estado: {inv.status.value}")
        
        print("\n" + "=" * 70)
        print("OPCIONES:")
        print("=" * 70)
        print("\n1. ELIMINAR estas facturas y re-subirlas")
        print("   - Más fácil y rápido")
        print("   - Perderás el historial de estas facturas")
        print("\n2. Mantenerlas sin PDF")
        print("   - Conservas el registro")
        print("   - Pero no podrás ver el PDF original")
        
        print("\n¿Quieres ELIMINAR estas facturas? (escribe 'SI' para confirmar)")
        confirmacion = input("\n> ").strip().upper()
        
        if confirmacion == "SI":
            for inv in invoices:
                db.delete(inv)
            db.commit()
            print(f"\n✅ {len(invoices)} facturas eliminadas")
            print("   Ahora puedes re-subirlas y se guardarán correctamente")
        else:
            print("\n❌ Operación cancelada")
            print("   Las facturas se mantienen sin PDF")
        
    finally:
        db.close()
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
