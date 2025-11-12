#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor

# Configuración de la base de datos (desde el contenedor)
db_config = {
    'host': 'ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com',
    'port': 5432,
    'database': 'paqueteria_v4',
    'user': 'jveyes',
    'password': 'a?HC!2.*1#?[==:|289qAI=)#V4kDzl$***'
}

try:
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor(cursor_factory=RealDictCursor)
    print('✅ Conexión exitosa a AWS RDS')
    
    # Obtener conteo de tablas
    tables = ['packages', 'package_history', 'package_announcements_new', 'messages', 'file_uploads', 'customers']
    total_records = 0
    
    print('📊 Estado actual de la base de datos:')
    for table in tables:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()['count']
            print(f'📊 {table}: {count} registros')
            total_records += count
        except Exception as e:
            print(f'⚠️ Error en {table}: {e}')
    
    print(f'Total de registros: {total_records}')
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f'❌ Error de conexión: {e}')
