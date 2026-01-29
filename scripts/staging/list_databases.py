#!/usr/bin/env python3
"""
Script para listar todas las bases de datos en el servidor AWS RDS
"""
import psycopg2
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('.env.production')

# Configuración de conexión
DB_HOST = os.getenv('POSTGRES_HOST')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')

print('=' * 80)
print('🔍 LISTANDO BASES DE DATOS EN AWS RDS')
print('=' * 80)
print(f'📡 Host: {DB_HOST}')
print(f'👤 Usuario: {DB_USER}')
print(f'🔌 Puerto: {DB_PORT}')
print('=' * 80)
print()

try:
    # Conectar a la base de datos postgres (base de datos por defecto)
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database='postgres'  # Base de datos por defecto para listar otras
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Listar todas las bases de datos con información detallada
    query = """
    SELECT 
        datname as database_name,
        pg_size_pretty(pg_database_size(datname)) as size,
        pg_database_size(datname) as size_bytes,
        datcollate as collation,
        datctype as ctype,
        (SELECT count(*) FROM pg_stat_activity WHERE datname = d.datname) as active_connections
    FROM pg_database d
    WHERE datistemplate = false
    ORDER BY pg_database_size(datname) DESC;
    """
    
    cursor.execute(query)
    databases = cursor.fetchall()
    
    print('📊 BASES DE DATOS ENCONTRADAS:')
    print('=' * 80)
    print(f'{"Base de Datos":<30} {"Tamaño":<15} {"Conexiones":<15} {"Collation":<20}')
    print('-' * 80)
    
    total_size = 0
    for db in databases:
        db_name, size, size_bytes, collation, ctype, connections = db
        total_size += size_bytes
        
        # Marcar bases de datos del proyecto
        marker = ''
        if 'paqueteria' in db_name.lower():
            marker = '⭐'
        
        print(f'{marker} {db_name:<28} {size:<15} {connections:<15} {collation:<20}')
    
    print('-' * 80)
    print(f'{"TOTAL":<30} {pg_size_pretty(total_size):<15}')
    print('=' * 80)
    print()
    
    # Información específica de bases de datos del proyecto
    print('🎯 BASES DE DATOS DEL PROYECTO PAQUETEX:')
    print('=' * 80)
    
    project_dbs = [db for db in databases if 'paqueteria' in db[0].lower()]
    
    if project_dbs:
        for db in project_dbs:
            db_name, size, size_bytes, collation, ctype, connections = db
            print(f'\n📦 {db_name}')
            print(f'   Tamaño: {size}')
            print(f'   Conexiones activas: {connections}')
            
            # Obtener información de tablas
            try:
                conn_db = psycopg2.connect(
                    host=DB_HOST,
                    port=DB_PORT,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    database=db_name
                )
                cur_db = conn_db.cursor()
                
                # Contar tablas
                cur_db.execute("""
                    SELECT count(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_type = 'BASE TABLE'
                """)
                table_count = cur_db.fetchone()[0]
                print(f'   Tablas: {table_count}')
                
                # Obtener algunas tablas principales
                cur_db.execute("""
                    SELECT table_name, 
                           pg_size_pretty(pg_total_relation_size(quote_ident(table_name)::regclass)) as size
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_type = 'BASE TABLE'
                    ORDER BY pg_total_relation_size(quote_ident(table_name)::regclass) DESC
                    LIMIT 5
                """)
                tables = cur_db.fetchall()
                
                if tables:
                    print(f'   Top 5 tablas más grandes:')
                    for table_name, table_size in tables:
                        print(f'      - {table_name}: {table_size}')
                
                cur_db.close()
                conn_db.close()
                
            except Exception as e:
                print(f'   ⚠️  No se pudo obtener información de tablas: {e}')
    else:
        print('⚠️  No se encontraron bases de datos del proyecto')
    
    print()
    print('=' * 80)
    print('✅ Consulta completada exitosamente')
    print('=' * 80)
    
    cursor.close()
    conn.close()

except psycopg2.Error as e:
    print(f'❌ Error de conexión a PostgreSQL:')
    print(f'   Código: {e.pgcode}')
    print(f'   Mensaje: {e.pgerror}')
    print()
    print('💡 Verifica:')
    print('   1. Las credenciales en .env.production')
    print('   2. La conectividad al servidor RDS')
    print('   3. Los permisos del usuario')
    
except Exception as e:
    print(f'❌ Error inesperado: {e}')

def pg_size_pretty(size_bytes):
    """Convertir bytes a formato legible"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"
