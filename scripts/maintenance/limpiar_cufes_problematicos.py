#!/usr/bin/env python3
"""
Script para eliminar facturas y registros CUFE problemáticos
"""
import sys
import os
sys.path.insert(0, '/app/src')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models.invoice import Invoice
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

def limpiar_cufes():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("LIMPIEZA DE CUFEs PROBLEMÁTICOS")
        print("=" * 60)
        
        for cufe in CUFES_PROBLEMATICOS:
            print(f"\n🔍 Buscando CUFE: {cufe[:20]}...")
            
            # Buscar factura
            factura = db.query(Invoice).filter(Invoice.cufe_cude == cufe).first()
            if factura:
                print(f"   ✓ Factura encontrada: ID={factura.id}, Número={factura.numero_documento}")
                print(f"     Proveedor: {factura.supplier.razon_social if factura.supplier else 'N/A'}")
                print(f"     Activa: {factura.is_active}")
                
                # Eliminar items de factura
                db.execute(text("DELETE FROM invoice_items WHERE invoice_id = :id"), {"id": factura.id})
                print(f"     → Items eliminados")
                
                # Eliminar irregularidades
                db.execute(text("DELETE FROM invoice_irregularities WHERE invoice_id = :id"), {"id": factura.id})
                print(f"     → Irregularidades eliminadas")
                
                # Eliminar factura
                db.delete(factura)
                print(f"     → Factura eliminada")
            else:
                print(f"   ✗ No se encontró factura con este CUFE")
            
            # Buscar registro CUFE
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
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    limpiar_cufes()
