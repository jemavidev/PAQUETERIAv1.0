#!/usr/bin/env python3
"""
Script para sincronizar datos de producción a staging
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Credenciales
db_host = "ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com"
db_user = "jveyes"
db_pass = "a?HC!2.*1#?[==:|289qAI=)#V4kDzl$"
db_port = "5432"

print('🔄 Iniciando sincronización de datos...')
print(f'📊 Origen: paqueteria_v4')
print(f'📊 Destino: paqueteria_staging')
print()

try:
    # Conectar a producción
    print('🔌 Conectando a producción...')
    conn_prod = psycopg2.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_pass,
        database='paqueteria_v4'
    )
    
    # Conectar a staging
    print('🔌 Conectando a staging...')
    conn_staging = psycopg2.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_pass,
        database='paqueteria_staging'
    )
    conn_staging.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    cursor_prod = conn_prod.cursor()
    cursor_staging = conn_staging.cursor()
    
    # Obtener lista de tablas
    print('📋 Obteniendo lista de tablas...')
    cursor_prod.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        ORDER BY tablename
    """)
    tables = [row[0] for row in cursor_fetchall()]
    
    print(f'✅ Encontradas {len(tables)} tablas')
    print()
    
    # Copiar cada tabla
    for table in tables:
        print(f'📦 Copiando tabla: {table}...')
        
        # Obtener estructura de la tabla
        cursor_prod.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table}' 
            ORDER BY ordinal_position
        """)
        columns = cursor_prod.fetchall()
        
        # Crear tabla en staging si no existe
        cursor_prod.execute(f"SELECT * FROM {table} LIMIT 0")
        colnames = [desc[0] for desc in cursor_prod.description]
        
        # Obtener datos
        cursor_prod.execute(f"SELECT * FROM {table}")
        rows = cursor_prod.fetchall()
        
        if rows:
            # Insertar datos
            placeholders = ','.join(['%s'] * len(colnames))
            insert_query = f"INSERT INTO {table} ({','.join(colnames)}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
            
            cursor_staging.executemany(insert_query, rows)
            print(f'   ✅ {len(rows)} registros copiados')
        else:
            print(f'   ℹ️  Tabla vacía')
    
    print()
    print('✅ Sincronización completada exitosamente')
    
    cursor_prod.close()
    cursor_staging.close()
    conn_prod.close()
    conn_staging.close()
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
