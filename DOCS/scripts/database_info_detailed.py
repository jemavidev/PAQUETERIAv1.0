#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Script de Información Detallada de Base de Datos
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo

Este script obtiene información detallada sobre:
- Tipo y versión de PostgreSQL
- Fechas de acceso y modificación
- Estadísticas de uso
- Información de la instancia RDS
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
        logging.FileHandler('logs/database_info_detailed.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatabaseInfoDetailed:
    """Clase para obtener información detallada de la base de datos"""
    
    def __init__(self):
        """Inicializar conexión a la base de datos AWS RDS"""
        self.connection = None
        self.cursor = None
        
        # Configuración de AWS RDS
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
    
    def get_database_version(self):
        """Obtener versión de PostgreSQL"""
        try:
            self.cursor.execute("SELECT version()")
            version = self.cursor.fetchone()['version']
            logger.info(f"📊 Versión de PostgreSQL: {version}")
            return version
        except Exception as e:
            logger.error(f"❌ Error al obtener versión: {e}")
            return None
    
    def get_database_info(self):
        """Obtener información básica de la base de datos"""
        try:
            # Información de la base de datos actual
            self.cursor.execute("""
                SELECT 
                    current_database() as database_name,
                    current_user as current_user,
                    inet_server_addr() as server_ip,
                    inet_server_port() as server_port,
                    current_setting('server_version') as server_version,
                    current_setting('server_version_num') as server_version_num,
                    current_setting('timezone') as timezone,
                    current_setting('lc_collate') as collation,
                    current_setting('lc_ctype') as ctype
            """)
            info = self.cursor.fetchone()
            logger.info("📊 Información de la base de datos obtenida")
            return info
        except Exception as e:
            logger.error(f"❌ Error al obtener información de BD: {e}")
            return None
    
    def get_database_size(self):
        """Obtener tamaño de la base de datos"""
        try:
            self.cursor.execute("""
                SELECT 
                    pg_size_pretty(pg_database_size(current_database())) as database_size,
                    pg_database_size(current_database()) as database_size_bytes
            """)
            size_info = self.cursor.fetchone()
            logger.info(f"📊 Tamaño de la base de datos: {size_info['database_size']}")
            return size_info
        except Exception as e:
            logger.error(f"❌ Error al obtener tamaño de BD: {e}")
            return None
    
    def get_table_info(self):
        """Obtener información detallada de las tablas"""
        try:
            self.cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    tableowner,
                    hasindexes,
                    hasrules,
                    hastriggers,
                    rowsecurity
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY tablename
            """)
            tables = self.cursor.fetchall()
            logger.info(f"📊 Información de {len(tables)} tablas obtenida")
            return tables
        except Exception as e:
            logger.error(f"❌ Error al obtener información de tablas: {e}")
            return []
    
    def get_table_sizes(self):
        """Obtener tamaños de las tablas"""
        try:
            self.cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes,
                    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
                    pg_size_pretty(pg_indexes_size(schemaname||'.'||tablename)) as indexes_size
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            """)
            sizes = self.cursor.fetchall()
            logger.info(f"📊 Tamaños de {len(sizes)} tablas obtenidos")
            return sizes
        except Exception as e:
            logger.error(f"❌ Error al obtener tamaños de tablas: {e}")
            return []
    
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
    
    def get_connection_info(self):
        """Obtener información de conexiones activas"""
        try:
            self.cursor.execute("""
                SELECT 
                    pid,
                    usename,
                    application_name,
                    client_addr,
                    client_port,
                    backend_start,
                    state,
                    query_start,
                    state_change
                FROM pg_stat_activity 
                WHERE datname = current_database()
                ORDER BY backend_start DESC
            """)
            connections = self.cursor.fetchall()
            logger.info(f"📊 {len(connections)} conexiones activas encontradas")
            return connections
        except Exception as e:
            logger.error(f"❌ Error al obtener información de conexiones: {e}")
            return []
    
    def get_database_activity(self):
        """Obtener actividad reciente de la base de datos"""
        try:
            self.cursor.execute("""
                SELECT 
                    datname,
                    numbackends,
                    xact_commit,
                    xact_rollback,
                    blks_read,
                    blks_hit,
                    tup_returned,
                    tup_fetched,
                    tup_inserted,
                    tup_updated,
                    tup_deleted,
                    stats_reset
                FROM pg_stat_database 
                WHERE datname = current_database()
            """)
            activity = self.cursor.fetchone()
            logger.info("📊 Actividad de la base de datos obtenida")
            return activity
        except Exception as e:
            logger.error(f"❌ Error al obtener actividad de BD: {e}")
            return None
    
    def get_last_access_dates(self):
        """Obtener fechas de último acceso a las tablas"""
        try:
            self.cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    n_tup_ins as inserts,
                    n_tup_upd as updates,
                    n_tup_del as deletes,
                    last_vacuum,
                    last_autovacuum,
                    last_analyze,
                    last_autoanalyze
                FROM pg_stat_user_tables 
                WHERE schemaname = 'public'
                ORDER BY tablename
            """)
            access_info = self.cursor.fetchall()
            logger.info(f"📊 Fechas de acceso de {len(access_info)} tablas obtenidas")
            return access_info
        except Exception as e:
            logger.error(f"❌ Error al obtener fechas de acceso: {e}")
            return []
    
    def close(self):
        """Cerrar conexión a la base de datos"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

def main():
    """Función principal"""
    print("🚀 PAQUETES EL CLUB v4.0 - Información Detallada de Base de Datos AWS RDS")
    print("="*80)
    
    # Verificar que estamos en el directorio correcto
    if not (Path.cwd() / "CODE" / "LOCAL").exists():
        print("❌ Error: Ejecutar este script desde la raíz del proyecto")
        print("💡 Ejecuta: python SCRIPTS/database/database_info_detailed.py")
        sys.exit(1)
    
    # Inicializar análisis
    db_info = DatabaseInfoDetailed()
    
    try:
        print("\n🔍 INFORMACIÓN DE LA BASE DE DATOS")
        print("="*50)
        
        # Versión de PostgreSQL
        version = db_info.get_database_version()
        if version:
            print(f"📊 Versión: {version}")
        
        # Información básica
        basic_info = db_info.get_database_info()
        if basic_info:
            print(f"📊 Base de datos: {basic_info['database_name']}")
            print(f"📊 Usuario actual: {basic_info['current_user']}")
            print(f"📊 Servidor IP: {basic_info['server_ip']}")
            print(f"📊 Puerto: {basic_info['server_port']}")
            print(f"📊 Zona horaria: {basic_info['timezone']}")
            print(f"📊 Collation: {basic_info['collation']}")
        
        # Tamaño de la base de datos
        size_info = db_info.get_database_size()
        if size_info:
            print(f"📊 Tamaño total: {size_info['database_size']}")
        
        print("\n📊 INFORMACIÓN DE TABLAS")
        print("="*50)
        
        # Información de tablas
        tables = db_info.get_table_info()
        if tables:
            print(f"📊 Total de tablas: {len(tables)}")
            for table in tables:
                print(f"  • {table['tablename']} (Owner: {table['tableowner']})")
        
        # Tamaños de tablas
        table_sizes = db_info.get_table_sizes()
        if table_sizes:
            print(f"\n📊 TAMAÑOS DE TABLAS")
            print("-" * 30)
            for table in table_sizes:
                print(f"  • {table['tablename']}: {table['size']} (Tabla: {table['table_size']}, Índices: {table['indexes_size']})")
        
        # Conteo de registros
        counts = db_info.get_table_counts()
        if counts:
            print(f"\n📊 REGISTROS POR TABLA")
            print("-" * 30)
            total_records = 0
            for table, count in counts.items():
                print(f"  • {table}: {count:,} registros")
                total_records += count
            print(f"  • TOTAL: {total_records:,} registros")
        
        print("\n🔍 ACTIVIDAD DE LA BASE DE DATOS")
        print("="*50)
        
        # Actividad de la base de datos
        activity = db_info.get_database_activity()
        if activity:
            print(f"📊 Conexiones activas: {activity['numbackends']}")
            print(f"📊 Transacciones commit: {activity['xact_commit']:,}")
            print(f"📊 Transacciones rollback: {activity['xact_rollback']:,}")
            print(f"📊 Bloqueos leídos: {activity['blks_read']:,}")
            print(f"📊 Bloqueos en cache: {activity['blks_hit']:,}")
            print(f"📊 Tuplas insertadas: {activity['tup_inserted']:,}")
            print(f"📊 Tuplas actualizadas: {activity['tup_updated']:,}")
            print(f"📊 Tuplas eliminadas: {activity['tup_deleted']:,}")
            if activity['stats_reset']:
                print(f"📊 Estadísticas reseteadas: {activity['stats_reset']}")
        
        # Conexiones activas
        connections = db_info.get_connection_info()
        if connections:
            print(f"\n📊 CONEXIONES ACTIVAS ({len(connections)})")
            print("-" * 40)
            for conn in connections:
                print(f"  • PID: {conn['pid']}, Usuario: {conn['usename']}, Estado: {conn['state']}")
                print(f"    Inicio: {conn['backend_start']}, IP: {conn['client_addr']}")
        
        # Fechas de último acceso
        access_dates = db_info.get_last_access_dates()
        if access_dates:
            print(f"\n📊 FECHAS DE ÚLTIMO ACCESO A TABLAS")
            print("-" * 50)
            for table in access_dates:
                print(f"  • {table['tablename']}:")
                print(f"    - Inserts: {table['inserts']:,}")
                print(f"    - Updates: {table['updates']:,}")
                print(f"    - Deletes: {table['deletes']:,}")
                if table['last_vacuum']:
                    print(f"    - Último vacuum: {table['last_vacuum']}")
                if table['last_analyze']:
                    print(f"    - Último analyze: {table['last_analyze']}")
        
        print(f"\n✅ Análisis completado exitosamente")
        print(f"📝 Revisa el archivo logs/database_info_detailed.log para más detalles")
    
    except Exception as e:
        logger.error(f"❌ Error durante el análisis: {e}")
        print(f"\n❌ Error durante el análisis: {e}")
        sys.exit(1)
    
    finally:
        db_info.close()

if __name__ == "__main__":
    main()
