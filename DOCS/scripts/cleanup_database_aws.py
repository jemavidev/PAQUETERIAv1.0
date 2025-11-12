#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Script de Limpieza de Base de Datos AWS RDS
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo

Este script vacía las siguientes tablas de la base de datos AWS RDS:
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

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    print("❌ Error: psycopg2 no está instalado")
    print("💡 Instala con: pip install psycopg2-binary")
    sys.exit(1)

# Configuración de logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/database_cleanup_aws.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatabaseCleanupAWS:
    """Clase para manejar la limpieza de la base de datos AWS RDS"""
    
    def __init__(self):
        """Inicializar conexión a la base de datos AWS RDS"""
        self.connection = None
        self.cursor = None
        
        # Configuración de AWS RDS (extraída de los logs de la aplicación)
        self.db_config = {
            'host': 'ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com',
            'port': 5432,
            'database': 'paqueteria_v4',
            'user': 'jveyes',
            'password': 'a?HC!2.*1#?[==:|289qAI=)#V4kDzl$***'
        }
        
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            logger.info("✅ Conexión a base de datos AWS RDS establecida correctamente")
        except Exception as e:
            logger.error(f"❌ Error al conectar con la base de datos AWS RDS: {e}")
            sys.exit(1)
    
    def get_table_counts(self):
        """Obtener conteo de registros en cada tabla"""
        counts = {}
        tables = [
            'packages', 'package_history', 'package_announcements_new',
            'messages', 'file_uploads', 'customers'
        ]
        
        for table in tables:
            try:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = self.cursor.fetchone()['count']
                counts[table] = count
                logger.info(f"📊 {table}: {count} registros")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo obtener conteo de {table}: {e}")
                counts[table] = 0
        
        return counts
    
    def cleanup_tables(self):
        """Limpiar todas las tablas en el orden correcto"""
        try:
            logger.info("🧹 Iniciando limpieza de base de datos AWS RDS...")
            
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
            
            for query in cleanup_queries:
                table_name = query.split()[-1]
                
                # Contar registros antes de eliminar
                self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count_before = self.cursor.fetchone()['count']
                
                if count_before > 0:
                    # Ejecutar eliminación
                    self.cursor.execute(query)
                    deleted_count = self.cursor.rowcount
                    total_deleted += deleted_count
                    logger.info(f"🗑️ {table_name}: {deleted_count} registros eliminados")
                else:
                    logger.info(f"✅ {table_name}: Ya está vacía")
            
            self.connection.commit()
            logger.info(f"🎉 Limpieza completada. Total de registros eliminados: {total_deleted}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error durante la limpieza: {e}")
            self.connection.rollback()
            return False
    
    def reset_sequences(self):
        """Resetear secuencias de auto-incremento"""
        try:
            sequences_to_reset = [
                'packages_id_seq',
                'messages_id_seq',
                'file_uploads_id_seq'
            ]
            
            for sequence in sequences_to_reset:
                try:
                    self.cursor.execute(f"ALTER SEQUENCE {sequence} RESTART WITH 1")
                    logger.info(f"🔄 Secuencia {sequence} reseteada")
                except Exception as e:
                    logger.warning(f"⚠️ No se pudo resetear {sequence}: {e}")
            
            self.connection.commit()
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
    
    def close(self):
        """Cerrar conexión a la base de datos"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

def confirm_cleanup():
    """Solicitar confirmación del usuario"""
    print("\n" + "="*60)
    print("⚠️  ADVERTENCIA: LIMPIEZA DE BASE DE DATOS AWS RDS  ⚠️")
    print("="*60)
    print("Este script eliminará TODOS los datos de las siguientes tablas:")
    print("• packages")
    print("• package_history") 
    print("• package_announcements_new")
    print("• messages")
    print("• file_uploads")
    print("• customers")
    print("\nBase de datos: AWS RDS (paqueteria_v4)")
    print("Esta acción NO SE PUEDE DESHACER.")
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
    print("🚀 PAQUETES EL CLUB v4.0 - Script de Limpieza de Base de Datos AWS RDS")
    print("="*70)
    
    # Verificar que estamos en el directorio correcto
    if not (Path.cwd() / "CODE" / "LOCAL").exists():
        print("❌ Error: Ejecutar este script desde la raíz del proyecto")
        print("💡 Ejecuta: python SCRIPTS/database/cleanup_database_aws.py")
        sys.exit(1)
    
    # Inicializar limpieza
    cleanup = DatabaseCleanupAWS()
    
    try:
        # Mostrar conteo actual
        print("\n📊 Estado actual de la base de datos AWS RDS:")
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
            print("📝 Revisa el archivo logs/database_cleanup_aws.log para más detalles")
        else:
            print("\n❌ Error durante la limpieza")
            print("📝 Revisa el archivo logs/database_cleanup_aws.log para más detalles")
            sys.exit(1)
    
    finally:
        cleanup.close()

if __name__ == "__main__":
    main()
