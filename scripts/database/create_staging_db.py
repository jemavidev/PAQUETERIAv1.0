#!/usr/bin/env python3
"""
Script para crear la base de datos paqueteria_staging
"""
import os
import psycopg2

# Credenciales
db_host = "ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com"
db_user = "jveyes"
db_pass = "a?HC!2.*1#?[==:|289qAI=)#V4kDzl$"
db_port = "5432"

print(f'🔍 Conectando a: {db_host}')
print(f'👤 Usuario: {db_user}')

try:
    # Conectar a la base de datos postgres (default)
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_pass,
        database='postgres'
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Verificar si la base de datos ya existe
    cursor.execute("SELECT 1 FROM pg_database WHERE datname='paqueteria_staging'")
    exists = cursor.fetchone()
    
    if exists:
        print('⚠️  La base de datos paqueteria_staging ya existe')
    else:
        # Crear la base de datos
        cursor.execute('CREATE DATABASE paqueteria_staging OWNER jveyes')
        print('✅ Base de datos paqueteria_staging creada exitosamente')
    
    # Listar bases de datos
    cursor.execute("SELECT datname, pg_size_pretty(pg_database_size(datname)) as size FROM pg_database WHERE datname IN ('paqueteria_v4', 'paqueteria_staging') ORDER BY datname")
    databases = cursor.fetchall()
    print('\n📊 Bases de datos:')
    for db in databases:
        print(f'   - {db[0]}: {db[1]}')
    
    cursor.close()
    conn.close()
    print('\n✅ Operación completada')
    
except Exception as e:
    print(f'❌ Error: {e}')
    exit(1)
