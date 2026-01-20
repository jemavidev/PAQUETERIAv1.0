#!/usr/bin/env python3
"""
Script para eliminar facturas problemáticas directamente
"""
import sys
import os
sys.path.insert(0, '/app/src')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models.invoice import Invoice, InvoiceItem, InvoiceIrregularity
from app.models.cufe import CufeRecord

# Configuración de base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://paqueteria_user:paqueteria_pass@db:5432/paqueteria_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# CUFEs problemáticos
CUFES_PROBLEMATICOS = [
    "468eb25da77268708c18f8c5020bd9d61dd135582f387a9d6583a6c63b0ab8ce4eac4dd524878b39a8296181f88d2816",
    "88f565e6a165010edd2680ea0f37c2453f3d2a11e2b58fcff298241c760f260cafef0dbed0b6214df2e67a3895ea6132"
]

def eliminar_facturas():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("ELIMINANDO FACTURAS PROBLEMÁTICAS")
        print("=" * 60)
        
        for cufe in CUFES_PROBLEMATICOS:
            print(f"\n🔍 Buscando CUFE: {cufe[:20]}...")
            
            # Buscar factura (activa o inactiva)
            factura = db.query(Invoice).filter(Invoice.cufe_cude == cufe).first()
            if factura:
                print(f"   ✓ Factura encontrada: ID={factura.id}, Número={factura.numero_documento}")
                print(f"     Proveedor: {factura.supplier.razon_social if factura.supplier else 'N/A'}")
                print(f"     Activa: {factura.is_active}")
                
                # Eliminar items de factura
                items_count = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == factura.id).delete()
                print(f"     → {items_count} items eliminados")
                
                # Eliminar irregularidades
                irreg_count = db.query(InvoiceIrregularity).filter(InvoiceIrregularity.invoice_id == factura.id).delete()
                print(f"     → {irreg_count} irregularidades eliminadas")
                
                # Eliminar factura
                db.delete(factura)
                print(f"     → Factura eliminada")
            else:
                print(f"   ✗ No se encontró factura con este CUFE")
            
            # Buscar y eliminar registro CUFE
            cufe_record = db.query(CufeRecord).filter(CufeRecord.cufe == cufe).first()
            if cufe_record:
                print(f"   ✓ Registro CUFE encontrado: ID={cufe_record.id}, Status={cufe_record.status}")
                db.delete(cufe_record)
                print(f"     → Registro CUFE eliminado")
            else:
                print(f"   ✗ No se encontró registro CUFE")
        
        # Commit de todos los cambios
        db.commit()
        
        print("\n" + "=" * 60)
        print("✅ LIMPIEZA COMPLETADA")
        print("=" * 60)
        print("\nAhora puedes subir los PDFs nuevamente desde cero.")
        
        # Verificar que se eliminaron
        verificacion = db.query(Invoice).filter(Invoice.cufe_cude.in_(CUFES_PROBLEMATICOS)).count()
        if verificacion == 0:
            print("✅ Verificación: Todas las facturas fueron eliminadas correctamente")
        else:
            print(f"⚠️ Advertencia: Aún quedan {verificacion} facturas en la base de datos")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    eliminar_facturas()
