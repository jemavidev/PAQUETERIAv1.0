#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Script de Limpieza de Base de Datos
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

# Agregar el directorio src al path para importar los modelos
current_dir = Path(__file__).parent
src_dir = current_dir.parent.parent / "LOCAL" / "src"
sys.path.insert(0, str(src_dir))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.database import get_database_url
from app.models import (
    Package, PackageHistory, PackageAnnouncementNew, 
    Message, FileUpload, Customer
)

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/database_cleanup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatabaseCleanup:
    """Clase para manejar la limpieza de la base de datos"""
    
    def __init__(self):
        """Inicializar conexión a la base de datos"""
        try:
            self.database_url = get_database_url()
            self.engine = create_engine(self.database_url)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            logger.info("✅ Conexión a base de datos establecida correctamente")
        except Exception as e:
            logger.error(f"❌ Error al conectar con la base de datos: {e}")
            sys.exit(1)
    
    def get_table_counts(self):
        """Obtener conteo de registros en cada tabla"""
        counts = {}
        with self.engine.connect() as conn:
            tables = [
                'packages', 'package_history', 'package_announcements_new',
                'messages', 'file_uploads', 'customers'
            ]
            
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
    
    def cleanup_tables(self):
        """Limpiar todas las tablas en el orden correcto"""
        session = self.SessionLocal()
        
        try:
            logger.info("🧹 Iniciando limpieza de base de datos...")
            
            # Orden de eliminación (respetando foreign keys):
            # 1. Tablas dependientes primero
            # 2. Tablas principales después
            
            cleanup_order = [
                ('file_uploads', FileUpload),
                ('messages', Message),
                ('package_history', PackageHistory),
                ('package_announcements_new', PackageAnnouncementNew),
                ('packages', Package),
                ('customers', Customer)
            ]
            
            total_deleted = 0
            
            for table_name, model_class in cleanup_order:
                try:
                    # Contar registros antes de eliminar
                    count_before = session.query(model_class).count()
                    
                    if count_before > 0:
                        # Eliminar todos los registros
                        deleted_count = session.query(model_class).delete()
                        session.commit()
                        
                        total_deleted += deleted_count
                        logger.info(f"🗑️ {table_name}: {deleted_count} registros eliminados")
                    else:
                        logger.info(f"✅ {table_name}: Ya está vacía")
                        
                except Exception as e:
                    logger.error(f"❌ Error al limpiar {table_name}: {e}")
                    session.rollback()
                    raise
            
            logger.info(f"🎉 Limpieza completada. Total de registros eliminados: {total_deleted}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error durante la limpieza: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def reset_sequences(self):
        """Resetear secuencias de auto-incremento"""
        try:
            with self.engine.connect() as conn:
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
    
    def verify_cleanup(self):
        """Verificar que la limpieza fue exitosa"""
        logger.info("🔍 Verificando limpieza...")
        counts = self.get_table_counts()
        
        all_empty = True
        for table, count in counts.items():
            if count > 0:
                logger.warning(f"⚠️ {table} aún tiene {count} registros")
                all_empty = False
            else:
                logger.info(f"✅ {table} está vacía")
        
        if all_empty:
            logger.info("🎉 Verificación exitosa: Todas las tablas están vacías")
        else:
            logger.warning("⚠️ Algunas tablas no se limpiaron completamente")
        
        return all_empty

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
        sys.exit(1)
    
    # Crear directorio de logs si no existe
    os.makedirs("logs", exist_ok=True)
    
    # Mostrar conteo actual
    cleanup = DatabaseCleanup()
    print("\n📊 Estado actual de la base de datos:")
    counts = cleanup.get_table_counts()
    
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
    success = cleanup.cleanup_tables()
    
    if success:
        # Resetear secuencias
        cleanup.reset_sequences()
        
        # Verificar limpieza
        cleanup.verify_cleanup()
        
        print("\n✅ Limpieza completada exitosamente")
        print("📝 Revisa el archivo logs/database_cleanup.log para más detalles")
    else:
        print("\n❌ Error durante la limpieza")
        print("📝 Revisa el archivo logs/database_cleanup.log para más detalles")
        sys.exit(1)

if __name__ == "__main__":
    main()
