#!/usr/bin/env python3
"""
Script para limpiar TODAS las facturas y datos relacionados
ADVERTENCIA: Esta operación es IRREVERSIBLE
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.database import SessionLocal, engine
from app.models.invoice import (
    Invoice, InvoiceItem, InvoiceIrregularity, 
    Supplier, InvoiceRejectedFile
)

def limpiar_archivos_pdf():
    """Elimina todos los archivos PDF de facturas"""
    pdf_directory = "/app/src/uploads/invoices"
    
    if not os.path.exists(pdf_directory):
        print(f"✓ Directorio {pdf_directory} no existe")
        return 0
    
    archivos_eliminados = 0
    for archivo in os.listdir(pdf_directory):
        if archivo.endswith('.pdf'):
            ruta_completa = os.path.join(pdf_directory, archivo)
            try:
                os.remove(ruta_completa)
                archivos_eliminados += 1
            except Exception as e:
                print(f"✗ Error eliminando {archivo}: {e}")
    
    print(f"✓ {archivos_eliminados} archivos PDF eliminados")
    return archivos_eliminados

def limpiar_base_datos():
    """Elimina todos los registros de las tablas de facturas"""
    db = SessionLocal()
    
    try:
        print("\n=== LIMPIEZA DE BASE DE DATOS ===\n")
        
        # 1. Irregularidades
        count_irregularities = db.query(InvoiceIrregularity).count()
        db.query(InvoiceIrregularity).delete()
        print(f"✓ {count_irregularities} irregularidades eliminadas")
        
        # 2. Items de facturas
        count_items = db.query(InvoiceItem).count()
        db.query(InvoiceItem).delete()
        print(f"✓ {count_items} items de facturas eliminados")
        
        # 3. Facturas
        count_invoices = db.query(Invoice).count()
        db.query(Invoice).delete()
        print(f"✓ {count_invoices} facturas eliminadas")
        
        # 4. Proveedores
        count_suppliers = db.query(Supplier).count()
        db.query(Supplier).delete()
        print(f"✓ {count_suppliers} proveedores eliminados")
        
        # 5. Archivos rechazados
        count_rejected = db.query(InvoiceRejectedFile).count()
        db.query(InvoiceRejectedFile).delete()
        print(f"✓ {count_rejected} archivos rechazados eliminados")
        
        # Commit de todos los cambios
        db.commit()
        print("\n✓ Todos los cambios guardados en la base de datos")
        
        return {
            'irregularities': count_irregularities,
            'items': count_items,
            'invoices': count_invoices,
            'suppliers': count_suppliers,
            'rejected': count_rejected
        }
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ ERROR: {e}")
        raise
    finally:
        db.close()

def resetear_secuencias():
    """Resetea las secuencias de IDs a 1"""
    db = SessionLocal()
    
    try:
        print("\n=== RESETEO DE SECUENCIAS ===\n")
        
        tablas = [
            'invoice_irregularities',
            'invoice_items',
            'invoices',
            'suppliers',
            'invoice_rejected_files'
        ]
        
        for tabla in tablas:
            try:
                db.execute(text(f"ALTER SEQUENCE {tabla}_id_seq RESTART WITH 1"))
                print(f"✓ Secuencia de {tabla} reseteada")
            except Exception as e:
                print(f"⚠ No se pudo resetear {tabla}: {e}")
        
        db.commit()
        print("\n✓ Secuencias reseteadas")
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ ERROR reseteando secuencias: {e}")
    finally:
        db.close()

def main():
    print("=" * 60)
    print("LIMPIEZA COMPLETA DE FACTURAS")
    print("=" * 60)
    print("\n⚠️  ADVERTENCIA: Esta operación eliminará:")
    print("   - Todas las facturas")
    print("   - Todos los items de facturas")
    print("   - Todas las irregularidades")
    print("   - Todos los proveedores")
    print("   - Todos los archivos rechazados")
    print("   - Todos los archivos PDF")
    print("\n⚠️  ESTA OPERACIÓN ES IRREVERSIBLE\n")
    
    respuesta = input("¿Estás seguro de continuar? (escribe 'SI' para confirmar): ")
    
    if respuesta.strip().upper() != 'SI':
        print("\n✗ Operación cancelada")
        return
    
    print("\n🚀 Iniciando limpieza...\n")
    
    # Limpiar base de datos
    stats = limpiar_base_datos()
    
    # Resetear secuencias
    resetear_secuencias()
    
    # Limpiar archivos
    print("\n=== LIMPIEZA DE ARCHIVOS ===\n")
    archivos = limpiar_archivos_pdf()
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE LIMPIEZA")
    print("=" * 60)
    print(f"Irregularidades eliminadas: {stats['irregularities']}")
    print(f"Items eliminados: {stats['items']}")
    print(f"Facturas eliminadas: {stats['invoices']}")
    print(f"Proveedores eliminados: {stats['suppliers']}")
    print(f"Archivos rechazados eliminados: {stats['rejected']}")
    print(f"Archivos PDF eliminados: {archivos}")
    print("=" * 60)
    print("\n✅ Limpieza completada exitosamente")
    print("   Ahora puedes importar las facturas nuevamente\n")

if __name__ == "__main__":
    main()
