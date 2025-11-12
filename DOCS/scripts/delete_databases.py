#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Script de Eliminación de Bases de Datos
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo

Este script elimina las siguientes bases de datos de AWS RDS:
- dbjveyes
- paqueteria
- paqueteria_prod

IMPORTANTE: Este script elimina bases de datos completas.
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
        logging.FileHandler('logs/delete_databases.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatabaseDeleter:
    """Clase para eliminar bases de datos de AWS RDS"""
    
    def __init__(self):
        """Inicializar conexión a la base de datos AWS RDS"""
        self.connection = None
        self.cursor = None
        
        # Configuración de AWS RDS
        self.db_config = {
            'host': 'ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com',
            'port': 5432,
            'database': 'postgres',  # Conectar a la BD por defecto
            'user': 'jveyes',
            'password': 'a?HC!2.*1#?[==:|289qAI=)#V4kDzl$***'
        }
        
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.connection.autocommit = True  # Necesario para DROP DATABASE
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            logger.info("✅ Conexión a base de datos AWS RDS establecida correctamente")
        except Exception as e:
            logger.error(f"❌ Error al conectar con la base de datos AWS RDS: {e}")
            sys.exit(1)
    
    def list_databases(self):
        """Listar todas las bases de datos disponibles"""
        try:
            self.cursor.execute("""
                SELECT datname, datowner, pg_size_pretty(pg_database_size(datname)) as size
                FROM pg_database 
                WHERE datistemplate = false
                ORDER BY datname
            """)
            databases = self.cursor.fetchall()
            logger.info(f"📊 {len(databases)} bases de datos encontradas")
            return databases
        except Exception as e:
            logger.error(f"❌ Error al listar bases de datos: {e}")
            return []
    
    def check_database_exists(self, db_name):
        """Verificar si una base de datos existe"""
        try:
            self.cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            exists = self.cursor.fetchone() is not None
            logger.info(f"📊 Base de datos '{db_name}': {'Existe' if exists else 'No existe'}")
            return exists
        except Exception as e:
            logger.error(f"❌ Error al verificar existencia de '{db_name}': {e}")
            return False
    
    def get_database_info(self, db_name):
        """Obtener información de una base de datos"""
        try:
            self.cursor.execute("""
                SELECT 
                    datname,
                    datowner,
                    pg_size_pretty(pg_database_size(datname)) as size,
                    pg_database_size(datname) as size_bytes
                FROM pg_database 
                WHERE datname = %s
            """, (db_name,))
            info = self.cursor.fetchone()
            return info
        except Exception as e:
            logger.error(f"❌ Error al obtener información de '{db_name}': {e}")
            return None
    
    def delete_database(self, db_name):
        """Eliminar una base de datos"""
        try:
            # Verificar que existe
            if not self.check_database_exists(db_name):
                logger.warning(f"⚠️ La base de datos '{db_name}' no existe")
                return False
            
            # Obtener información antes de eliminar
            info = self.get_database_info(db_name)
            if info:
                logger.info(f"📊 Eliminando '{db_name}' (Tamaño: {info['size']})")
            
            # Terminar conexiones activas a la base de datos
            self.cursor.execute("""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = %s AND pid <> pg_backend_pid()
            """, (db_name,))
            
            # Eliminar la base de datos
            self.cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
            logger.info(f"✅ Base de datos '{db_name}' eliminada exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error al eliminar '{db_name}': {e}")
            return False
    
    def delete_target_databases(self):
        """Eliminar las bases de datos objetivo"""
        target_databases = ['dbjveyes', 'paqueteria', 'paqueteria_prod']
        deleted_count = 0
        
        logger.info("🗑️ Iniciando eliminación de bases de datos objetivo...")
        
        for db_name in target_databases:
            if self.delete_database(db_name):
                deleted_count += 1
        
        logger.info(f"🎉 Eliminación completada: {deleted_count}/{len(target_databases)} bases de datos eliminadas")
        return deleted_count
    
    def close(self):
        """Cerrar conexión a la base de datos"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

def confirm_deletion():
    """Solicitar confirmación del usuario"""
    print("\n" + "="*60)
    print("⚠️  ADVERTENCIA: ELIMINACIÓN DE BASES DE DATOS AWS RDS  ⚠️")
    print("="*60)
    print("Este script eliminará las siguientes bases de datos:")
    print("• dbjveyes")
    print("• paqueteria")
    print("• paqueteria_prod")
    print("\nBase de datos: AWS RDS PostgreSQL")
    print("Esta acción NO SE PUEDE DESHACER.")
    print("="*60)
    
    while True:
        response = input("\n¿Estás seguro de que quieres continuar? (escribe 'ELIMINAR' para confirmar): ").strip()
        if response == 'ELIMINAR':
            return True
        elif response.lower() in ['no', 'n', 'cancel', 'cancelar']:
            print("❌ Operación cancelada por el usuario")
            return False
        else:
            print("❌ Respuesta inválida. Escribe 'ELIMINAR' para confirmar o 'no' para cancelar")

def main():
    """Función principal"""
    print("🚀 PAQUETES EL CLUB v4.0 - Eliminación de Bases de Datos AWS RDS")
    print("="*70)
    
    # Verificar que estamos en el directorio correcto
    if not (Path.cwd() / "CODE" / "LOCAL").exists():
        print("❌ Error: Ejecutar este script desde la raíz del proyecto")
        print("💡 Ejecuta: python SCRIPTS/database/delete_databases.py")
        sys.exit(1)
    
    # Inicializar eliminador
    deleter = DatabaseDeleter()
    
    try:
        # Listar bases de datos actuales
        print("\n📊 Bases de datos actuales:")
        databases = deleter.list_databases()
        for db in databases:
            print(f"  • {db['datname']} (Tamaño: {db['size']})")
        
        # Verificar bases de datos objetivo
        target_databases = ['dbjveyes', 'paqueteria', 'paqueteria_prod']
        existing_targets = []
        
        print(f"\n🔍 Verificando bases de datos objetivo:")
        for db_name in target_databases:
            if deleter.check_database_exists(db_name):
                info = deleter.get_database_info(db_name)
                if info:
                    print(f"  • {db_name}: Existe (Tamaño: {info['size']})")
                    existing_targets.append(db_name)
                else:
                    print(f"  • {db_name}: Existe (sin información de tamaño)")
                    existing_targets.append(db_name)
            else:
                print(f"  • {db_name}: No existe")
        
        if not existing_targets:
            print("\n✅ No hay bases de datos objetivo para eliminar")
            return
        
        print(f"\n📊 Bases de datos a eliminar: {len(existing_targets)}")
        
        # Solicitar confirmación
        if not confirm_deletion():
            return
        
        # Ejecutar eliminación
        print("\n🗑️ Iniciando eliminación...")
        deleted_count = deleter.delete_target_databases()
        
        # Verificar resultado
        print(f"\n📊 Resultado: {deleted_count} bases de datos eliminadas")
        
        # Listar bases de datos restantes
        print("\n📊 Bases de datos restantes:")
        remaining_databases = deleter.list_databases()
        for db in remaining_databases:
            print(f"  • {db['datname']} (Tamaño: {db['size']})")
        
        print(f"\n✅ Operación completada exitosamente")
        print(f"📝 Revisa el archivo logs/delete_databases.log para más detalles")
    
    except Exception as e:
        logger.error(f"❌ Error durante la eliminación: {e}")
        print(f"\n❌ Error durante la eliminación: {e}")
        sys.exit(1)
    
    finally:
        deleter.close()

if __name__ == "__main__":
    main()
