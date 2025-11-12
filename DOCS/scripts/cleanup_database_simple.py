#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Script Simple de Limpieza de Base de Datos
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo

Este script vacía las siguientes tablas de la base de datos:
- packages
- package_history
- package_announcements_new
- messages
- file_uploads
- customers

IMPORTANTE: Este script elimina TODOS los datos de estas tablas.
Solo usar en desarrollo, NUNCA en producción.
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Agregar el directorio src al path
current_dir = Path(__file__).parent
src_dir = current_dir.parent.parent / "LOCAL" / "src"
sys.path.insert(0, str(src_dir))

try:
    from sqlalchemy import create_engine, text
    from app.core.database import get_database_url
except ImportError as e:
    print(f"❌ Error al importar dependencias: {e}")
    print("💡 Asegúrate de estar en el directorio correcto y tener las dependencias instaladas")
    sys.exit(1)

# Configuración de logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/database_cleanup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_database_connection():
    """Obtener conexión a la base de datos"""
    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        return engine
    except Exception as e:
        logger.error(f"❌ Error al conectar con la base de datos: {e}")
        return None

def get_table_counts(engine):
    """Obtener conteo de registros en cada tabla"""
    counts = {}
    tables = [
        'packages', 'package_history', 'package_announcements_new',
        'messages', 'file_uploads', 'customers'
    ]
    
    with engine.connect() as conn:
        for table in tables:
            try:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                counts[table] = count
                logger.info(f"📊 {table}: {count} registros")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo obtener conteo de {table}: {e}")
                counts[table] = 0
    
    return counts

def cleanup_tables(engine):
    """Limpiar todas las tablas en el orden correcto"""
    # Orden de eliminación (respetando foreign keys)
    cleanup_queries = [
        "DELETE FROM file_uploads",
        "DELETE FROM messages", 
        "DELETE FROM package_history",
        "DELETE FROM package_announcements_new",
        "DELETE FROM packages",
        "DELETE FROM customers"
    ]
    
    total_deleted = 0
    
    with engine.connect() as conn:
        try:
            for query in cleanup_queries:
                table_name = query.split()[-1]
                
                # Contar registros antes de eliminar
                count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count_before = count_result.scalar()
                
                if count_before > 0:
                    # Ejecutar eliminación
                    result = conn.execute(text(query))
                    deleted_count = result.rowcount
                    total_deleted += deleted_count
                    logger.info(f"🗑️ {table_name}: {deleted_count} registros eliminados")
                else:
                    logger.info(f"✅ {table_name}: Ya está vacía")
            
            conn.commit()
            logger.info(f"🎉 Limpieza completada. Total de registros eliminados: {total_deleted}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error durante la limpieza: {e}")
            conn.rollback()
            return False

def reset_sequences(engine):
    """Resetear secuencias de auto-incremento"""
    try:
        with engine.connect() as conn:
            # Resetear secuencias para tablas con ID auto-incremento
            sequences_to_reset = [
                'packages_id_seq',
                'messages_id_seq', 
                'file_uploads_id_seq'
            ]
            
            for sequence in sequences_to_reset:
                try:
                    conn.execute(text(f"ALTER SEQUENCE {sequence} RESTART WITH 1"))
                    logger.info(f"🔄 Secuencia {sequence} reseteada")
                except Exception as e:
                    logger.warning(f"⚠️ No se pudo resetear {sequence}: {e}")
            
            conn.commit()
            logger.info("✅ Secuencias reseteadas correctamente")
            
    except Exception as e:
        logger.error(f"❌ Error al resetear secuencias: {e}")

def confirm_cleanup():
    """Solicitar confirmación del usuario"""
    print("\n" + "="*60)
    print("⚠️  ADVERTENCIA: LIMPIEZA DE BASE DE DATOS  ⚠️")
    print("="*60)
    print("Este script eliminará TODOS los datos de las siguientes tablas:")
    print("• packages")
    print("• package_history") 
    print("• package_announcements_new")
    print("• messages")
    print("• file_uploads")
    print("• customers")
    print("\nEsta acción NO SE PUEDE DESHACER.")
    print("="*60)
    
    while True:
        response = input("\n¿Estás seguro de que quieres continuar? (escribe 'SI' para confirmar): ").strip()
        if response == 'SI':
            return True
        elif response.lower() in ['no', 'n', 'cancel', 'cancelar']:
            print("❌ Operación cancelada por el usuario")
            return False
        else:
            print("❌ Respuesta inválida. Escribe 'SI' para confirmar o 'no' para cancelar")

def main():
    """Función principal"""
    print("🚀 PAQUETES EL CLUB v4.0 - Script de Limpieza de Base de Datos")
    print("="*60)
    
    # Verificar que estamos en el directorio correcto
    if not (Path.cwd() / "CODE" / "LOCAL").exists():
        print("❌ Error: Ejecutar este script desde la raíz del proyecto")
        print("💡 Ejecuta: python SCRIPTS/database/cleanup_database_simple.py")
        sys.exit(1)
    
    # Obtener conexión a la base de datos
    engine = get_database_connection()
    if not engine:
        sys.exit(1)
    
    # Mostrar conteo actual
    print("\n📊 Estado actual de la base de datos:")
    counts = get_table_counts(engine)
    
    total_records = sum(counts.values())
    if total_records == 0:
        print("✅ La base de datos ya está vacía")
        return
    
    print(f"\nTotal de registros a eliminar: {total_records}")
    
    # Solicitar confirmación
    if not confirm_cleanup():
        return
    
    # Ejecutar limpieza
    print("\n🧹 Iniciando limpieza...")
    success = cleanup_tables(engine)
    
    if success:
        # Resetear secuencias
        reset_sequences(engine)
        
        # Verificar limpieza
        print("\n🔍 Verificando limpieza...")
        final_counts = get_table_counts(engine)
        
        all_empty = all(count == 0 for count in final_counts.values())
        if all_empty:
            print("🎉 Verificación exitosa: Todas las tablas están vacías")
        else:
            print("⚠️ Algunas tablas no se limpiaron completamente")
        
        print("\n✅ Limpieza completada exitosamente")
        print("📝 Revisa el archivo logs/database_cleanup.log para más detalles")
    else:
        print("\n❌ Error durante la limpieza")
        print("📝 Revisa el archivo logs/database_cleanup.log para más detalles")
        sys.exit(1)

if __name__ == "__main__":
    main()
