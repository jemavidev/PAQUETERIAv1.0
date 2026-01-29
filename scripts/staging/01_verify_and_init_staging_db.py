#!/usr/bin/env python3
"""
Script para verificar y preparar la base de datos paqueteria_staging
"""
import psycopg2
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno de staging
load_dotenv('.env.staging')

# Configuración
DB_HOST = os.getenv('POSTGRES_HOST')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
STAGING_DB = 'paqueteria_staging'
PROD_DB = 'paqueteria_v4'

print('=' * 80)
print('🔧 VERIFICACIÓN Y PREPARACIÓN DE BASE DE DATOS STAGING')
print('=' * 80)
print(f'📡 Host: {DB_HOST}')
print(f'👤 Usuario: {DB_USER}')
print(f'🗄️  Base de datos staging: {STAGING_DB}')
print('=' * 80)
print()

try:
    # Conectar a postgres para verificar/crear la base de datos
    print('📌 Paso 1: Conectando al servidor PostgreSQL...')
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database='postgres'
    )
    conn.autocommit = True
    cursor = conn.cursor()
    print('✅ Conectado exitosamente')
    print()
    
    # Verificar si la base de datos staging existe
    print(f'📌 Paso 2: Verificando si {STAGING_DB} existe...')
    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname='{STAGING_DB}'")
    exists = cursor.fetchone()
    
    if exists:
        print(f'✅ La base de datos {STAGING_DB} ya existe')
    else:
        print(f'⚠️  La base de datos {STAGING_DB} NO existe')
        print(f'📝 Creando {STAGING_DB}...')
        cursor.execute(f'CREATE DATABASE {STAGING_DB} OWNER {DB_USER}')
        print(f'✅ Base de datos {STAGING_DB} creada exitosamente')
    print()
    
    # Listar bases de datos del proyecto
    print('📌 Paso 3: Listando bases de datos del proyecto...')
    cursor.execute(f"""
        SELECT 
            datname,
            pg_size_pretty(pg_database_size(datname)) as size,
            (SELECT count(*) FROM pg_stat_activity WHERE datname = d.datname) as connections
        FROM pg_database d
        WHERE datname IN ('{PROD_DB}', '{STAGING_DB}')
        ORDER BY datname
    """)
    databases = cursor.fetchall()
    
    print(f'{"Base de Datos":<25} {"Tamaño":<15} {"Conexiones"}')
    print('-' * 60)
    for db_name, size, connections in databases:
        marker = '🟢' if db_name == STAGING_DB else '🔵'
        print(f'{marker} {db_name:<23} {size:<15} {connections}')
    print()
    
    cursor.close()
    conn.close()
    
    # Conectar a staging para verificar esquema
    print(f'📌 Paso 4: Verificando esquema de {STAGING_DB}...')
    conn_staging = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=STAGING_DB
    )
    cursor_staging = conn_staging.cursor()
    
    # Contar tablas
    cursor_staging.execute("""
        SELECT count(*) 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
    """)
    table_count = cursor_staging.fetchone()[0]
    
    print(f'📊 Tablas encontradas: {table_count}')
    
    if table_count == 0:
        print()
        print('⚠️  La base de datos está VACÍA (sin tablas)')
        print()
        print('📝 OPCIONES:')
        print('   1. Ejecutar migraciones de Alembic:')
        print('      cd CODE && alembic upgrade head')
        print()
        print('   2. Copiar esquema desde producción:')
        print('      python scripts/staging/02_copy_schema_from_prod.py')
        print()
        print('   3. Sincronizar datos completos desde producción:')
        print('      python scripts/staging/03_sync_from_production.py')
        print()
    else:
        print('✅ La base de datos tiene tablas')
        print()
        
        # Listar algunas tablas principales
        cursor_staging.execute("""
            SELECT table_name,
                   pg_size_pretty(pg_total_relation_size(quote_ident(table_name)::regclass)) as size
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY pg_total_relation_size(quote_ident(table_name)::regclass) DESC
            LIMIT 10
        """)
        tables = cursor_staging.fetchall()
        
        print('📋 Top 10 tablas más grandes:')
        print(f'{"Tabla":<40} {"Tamaño"}')
        print('-' * 60)
        for table_name, size in tables:
            print(f'   {table_name:<38} {size}')
        print()
        
        # Contar registros en tablas principales
        main_tables = ['users', 'customers', 'packages', 'invoices', 'supplier_invoices']
        print('📊 Registros en tablas principales:')
        print(f'{"Tabla":<30} {"Registros"}')
        print('-' * 50)
        
        for table in main_tables:
            try:
                cursor_staging.execute(f"SELECT count(*) FROM {table}")
                count = cursor_staging.fetchone()[0]
                print(f'   {table:<28} {count:>10,}')
            except:
                print(f'   {table:<28} {"N/A":>10}')
        print()
    
    cursor_staging.close()
    conn_staging.close()
    
    print('=' * 80)
    print('✅ VERIFICACIÓN COMPLETADA')
    print('=' * 80)
    print()
    print('🚀 PRÓXIMOS PASOS:')
    print()
    
    if table_count == 0:
        print('   1. Inicializar esquema (elegir una opción):')
        print('      • Migraciones: cd CODE && alembic upgrade head')
        print('      • Copiar de prod: python scripts/staging/02_copy_schema_from_prod.py')
        print()
        print('   2. Sincronizar datos:')
        print('      python scripts/staging/03_sync_from_production.py')
    else:
        print('   1. Sincronizar datos desde producción (opcional):')
        print('      python scripts/staging/03_sync_from_production.py')
    
    print()
    print('   2. Levantar servidor staging:')
    print('      docker-compose -f docker-compose.staging.yml up -d')
    print()
    print('   3. Verificar que funciona:')
    print('      curl http://localhost:8001/health')
    print()
    
except psycopg2.Error as e:
    print(f'❌ Error de PostgreSQL:')
    print(f'   Código: {e.pgcode}')
    print(f'   Mensaje: {e.pgerror}')
    sys.exit(1)
    
except Exception as e:
    print(f'❌ Error inesperado: {e}')
    sys.exit(1)
