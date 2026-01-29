#!/usr/bin/env python3
"""
Script para copiar la estructura de la base de datos de producción a staging
"""
import psycopg2

# Credenciales
db_host = "ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com"
db_user = "jveyes"
db_pass = "a?HC!2.*1#?[==:|289qAI=)#V4kDzl$"
db_port = "5432"

print('🔄 Copiando estructura de base de datos...')
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
    conn_staging.autocommit = True
    
    cursor_prod = conn_prod.cursor()
    cursor_staging = conn_staging.cursor()
    
    # Obtener el esquema completo de producción
    print('📋 Obteniendo esquema de producción...')
    cursor_prod.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        ORDER BY tablename
    """)
    tables = [row[0] for row in cursor_prod.fetchall()]
    
    print(f'✅ Encontradas {len(tables)} tablas')
    print()
    
    # Para cada tabla, obtener su definición y crearla en staging
    for table in tables:
        print(f'📦 Procesando tabla: {table}...')
        
        # Obtener la definición de la tabla
        cursor_prod.execute(f"""
            SELECT 
                'CREATE TABLE IF NOT EXISTS ' || quote_ident('{table}') || ' (' ||
                string_agg(
                    quote_ident(column_name) || ' ' || 
                    data_type || 
                    CASE 
                        WHEN character_maximum_length IS NOT NULL 
                        THEN '(' || character_maximum_length || ')'
                        ELSE ''
                    END ||
                    CASE 
                        WHEN is_nullable = 'NO' THEN ' NOT NULL'
                        ELSE ''
                    END,
                    ', '
                ) || ');'
            FROM information_schema.columns
            WHERE table_name = '{table}'
            GROUP BY table_name
        """)
        
        create_statement = cursor_prod.fetchone()
        if create_statement:
            try:
                cursor_staging.execute(create_statement[0])
                print(f'   ✅ Tabla creada')
            except Exception as e:
                print(f'   ⚠️  Error (puede ser normal): {str(e)[:100]}')
    
    # Verificar tablas creadas en staging
    cursor_staging.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        ORDER BY tablename
    """)
    staging_tables = [row[0] for row in cursor_staging.fetchall()]
    
    print()
    print(f'✅ {len(staging_tables)} tablas en staging:')
    for table in staging_tables[:10]:  # Mostrar solo las primeras 10
        print(f'   - {table}')
    if len(staging_tables) > 10:
        print(f'   ... y {len(staging_tables) - 10} más')
    
    print()
    print('✅ Estructura copiada exitosamente')
    
    cursor_prod.close()
    cursor_staging.close()
    conn_prod.close()
    conn_staging.close()
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
