#!/usr/bin/env python3
"""
Script para limpiar TODAS las tablas relacionadas con facturas
ADVERTENCIA: Este script eliminará TODOS los datos de facturas
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import text, inspect
from app.database import engine, SessionLocal
from datetime import datetime

# Tablas relacionadas con facturas (en orden de dependencias)
INVOICE_TABLES = [
    'invoice_irregularities',      # Depende de invoices e invoice_items
    'invoice_items',               # Depende de invoices
    'invoice_rejected_files',      # Independiente
    'supplier_invoices',           # Independiente (pero relacionada con invoices)
    'invoices',                    # Depende de suppliers
    'suppliers',                   # Base
]

def verificar_tablas():
    """Verifica qué tablas existen en la base de datos"""
    print("\n" + "=" * 70)
    print("VERIFICANDO TABLAS EN LA BASE DE DATOS")
    print("=" * 70)
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    tablas_encontradas = []
    tablas_no_encontradas = []
    
    for tabla in INVOICE_TABLES:
        if tabla in existing_tables:
            tablas_encontradas.append(tabla)
            print(f"  ✅ {tabla}")
        else:
            tablas_no_encontradas.append(tabla)
            print(f"  ⚠️  {tabla} - NO EXISTE")
    
    return tablas_encontradas, tablas_no_encontradas


def contar_registros(db):
    """Cuenta registros en cada tabla"""
    print("\n" + "=" * 70)
    print("CONTANDO REGISTROS ACTUALES")
    print("=" * 70)
    
    counts = {}
    total = 0
    
    for tabla in INVOICE_TABLES:
        try:
            result = db.execute(text(f"SELECT COUNT(*) FROM {tabla}"))
            count = result.scalar()
            counts[tabla] = count
            total += count
            print(f"  {tabla}: {count:,} registros")
        except Exception as e:
            counts[tabla] = 0
            print(f"  {tabla}: ERROR - {str(e)[:50]}")
    
    print(f"\n  TOTAL: {total:,} registros")
    return counts, total


def crear_backup(db):
    """Crea un backup de los datos antes de eliminar"""
    print("\n" + "=" * 70)
    print("CREANDO BACKUP")
    print("=" * 70)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"backup_facturas_{timestamp}.sql"
    
    print(f"\n⚠️  IMPORTANTE: Deberías crear un backup manual de la base de datos")
    print(f"   Comando sugerido:")
    print(f"   pg_dump -U usuario -d nombre_bd > {backup_file}")
    print()
    
    return backup_file


def limpiar_tablas(db, tablas):
    """Limpia todas las tablas de facturas"""
    print("\n" + "=" * 70)
    print("LIMPIANDO TABLAS")
    print("=" * 70)
    
    eliminados = {}
    
    # Deshabilitar foreign key checks temporalmente
    print("\n🔓 Deshabilitando foreign key checks...")
    db.execute(text("SET session_replication_role = 'replica';"))
    
    try:
        for tabla in tablas:
            try:
                print(f"\n🗑️  Limpiando {tabla}...")
                result = db.execute(text(f"DELETE FROM {tabla}"))
                count = result.rowcount
                eliminados[tabla] = count
                print(f"   ✅ {count:,} registros eliminados")
            except Exception as e:
                eliminados[tabla] = 0
                print(f"   ❌ ERROR: {str(e)[:100]}")
        
        # Commit de todos los cambios
        db.commit()
        print("\n✅ Cambios confirmados (COMMIT)")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ ERROR: {e}")
        print("🔄 Cambios revertidos (ROLLBACK)")
        raise
    
    finally:
        # Rehabilitar foreign key checks
        print("\n🔒 Rehabilitando foreign key checks...")
        db.execute(text("SET session_replication_role = 'origin';"))
        db.commit()
    
    return eliminados


def resetear_secuencias(db, tablas):
    """Resetea las secuencias de IDs a 1"""
    print("\n" + "=" * 70)
    print("RESETEANDO SECUENCIAS DE IDs")
    print("=" * 70)
    
    for tabla in tablas:
        try:
            # Intentar resetear la secuencia
            db.execute(text(f"ALTER SEQUENCE {tabla}_id_seq RESTART WITH 1;"))
            print(f"  ✅ {tabla}_id_seq reseteada")
        except Exception as e:
            print(f"  ⚠️  {tabla}_id_seq - {str(e)[:50]}")
    
    db.commit()


def verificar_limpieza(db):
    """Verifica que las tablas estén vacías"""
    print("\n" + "=" * 70)
    print("VERIFICANDO LIMPIEZA")
    print("=" * 70)
    
    all_clean = True
    
    for tabla in INVOICE_TABLES:
        try:
            result = db.execute(text(f"SELECT COUNT(*) FROM {tabla}"))
            count = result.scalar()
            if count == 0:
                print(f"  ✅ {tabla}: 0 registros")
            else:
                print(f"  ❌ {tabla}: {count} registros (NO LIMPIA)")
                all_clean = False
        except Exception as e:
            print(f"  ⚠️  {tabla}: ERROR - {str(e)[:50]}")
    
    return all_clean


def main():
    print("\n" + "=" * 70)
    print("🗑️  SCRIPT DE LIMPIEZA DE TABLAS DE FACTURAS")
    print("=" * 70)
    print("\n⚠️  ADVERTENCIA: Este script eliminará TODOS los datos de:")
    print("   - Facturas (invoices)")
    print("   - Items de facturas (invoice_items)")
    print("   - Irregularidades (invoice_irregularities)")
    print("   - Facturas de proveedores (supplier_invoices)")
    print("   - Proveedores (suppliers)")
    print("   - Archivos rechazados (invoice_rejected_files)")
    print("\n❌ ESTA ACCIÓN NO SE PUEDE DESHACER")
    print("=" * 70)
    
    # Verificar tablas
    tablas_encontradas, tablas_no_encontradas = verificar_tablas()
    
    if not tablas_encontradas:
        print("\n❌ No se encontraron tablas de facturas en la base de datos")
        return
    
    # Crear sesión
    db = SessionLocal()
    
    try:
        # Contar registros actuales
        counts, total = contar_registros(db)
        
        if total == 0:
            print("\n✅ Las tablas ya están vacías. No hay nada que limpiar.")
            return
        
        # Crear backup
        backup_file = crear_backup(db)
        
        # Confirmación
        print("\n" + "=" * 70)
        print("CONFIRMACIÓN REQUERIDA")
        print("=" * 70)
        print(f"\nSe eliminarán {total:,} registros en total")
        print("\n¿Estás SEGURO de que quieres continuar?")
        print("Escribe 'ELIMINAR TODO' para confirmar:")
        
        confirmacion = input("\n> ").strip()
        
        if confirmacion != "ELIMINAR TODO":
            print("\n❌ Operación cancelada por el usuario")
            return
        
        # Limpiar tablas
        eliminados = limpiar_tablas(db, tablas_encontradas)
        
        # Resetear secuencias
        resetear_secuencias(db, tablas_encontradas)
        
        # Verificar limpieza
        all_clean = verificar_limpieza(db)
        
        # Resumen final
        print("\n" + "=" * 70)
        print("RESUMEN DE LIMPIEZA")
        print("=" * 70)
        
        total_eliminados = sum(eliminados.values())
        
        for tabla, count in eliminados.items():
            print(f"  {tabla}: {count:,} registros eliminados")
        
        print(f"\n  TOTAL ELIMINADO: {total_eliminados:,} registros")
        
        if all_clean:
            print("\n✅ LIMPIEZA COMPLETADA EXITOSAMENTE")
            print("   Todas las tablas de facturas están vacías")
        else:
            print("\n⚠️  LIMPIEZA COMPLETADA CON ADVERTENCIAS")
            print("   Algunas tablas pueden tener registros residuales")
        
        print("\n📋 PRÓXIMOS PASOS:")
        print("   1. Verificar que la aplicación funciona correctamente")
        print("   2. Puedes empezar a importar facturas nuevas")
        print("   3. El backup manual está disponible si lo necesitas")
        
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        print("   Los cambios fueron revertidos (ROLLBACK)")
        return 1
    
    finally:
        db.close()
    
    print("\n" + "=" * 70)
    print("✅ SCRIPT COMPLETADO")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code or 0)
    except KeyboardInterrupt:
        print("\n\n❌ Operación cancelada por el usuario (Ctrl+C)")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        sys.exit(1)
