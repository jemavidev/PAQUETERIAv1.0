#!/usr/bin/env python3
"""
Sincronización completa de datos: producción → staging
Copia tabla por tabla con todos los datos
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

db_host = "ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com"
db_user = "jveyes"
db_pass = "a?HC!2.*1#?[==:|289qAI=)#V4kDzl$"

print('=' * 70)
print('🔄 SINCRONIZACIÓN COMPLETA DE DATOS')
print('=' * 70)
print('\n📊 Producción → Staging (solo lectura en producción)\n')

try:
    # Conectar
    print('🔌 Conectando a las bases de datos...')
    conn_prod = psycopg2.connect(
        host=db_host, port=5432, user=db_user, password=db_pass, database='paqueteria_v4'
    )
    conn_staging = psycopg2.connect(
        host=db_host, port=5432, user=db_user, password=db_pass, database='paqueteria_staging'
    )
    conn_staging.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    cur_prod = conn_prod.cursor()
    cur_stg = conn_staging.cursor()
    
    # Obtener todas las tablas de producción
    print('📋 Obteniendo lista de tablas...')
    cur_prod.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        ORDER BY tablename
    """)
    tables = [row[0] for row in cur_prod.fetchall()]
    print(f'✅ {len(tables)} tablas encontradas\n')
    
    # Primero, copiar el esquema completo
    print('🏗️  Copiando esquema (estructura de tablas)...')
    
    # Obtener y ejecutar CREATE TABLE statements
    for table in tables:
        try:
            # Obtener la definición completa de la tabla desde producción
            cur_prod.execute(f"""
                SELECT 
                    'CREATE TABLE IF NOT EXISTS ' || quote_ident(tablename) || ' (' ||
                    string_agg(column_def, ', ') || 
                    COALESCE(', ' || constraints, '') || ');'
                FROM (
                    SELECT 
                        t.tablename,
                        quote_ident(c.column_name) || ' ' || c.data_type ||
                        CASE 
                            WHEN c.character_maximum_length IS NOT NULL 
                            THEN '(' || c.character_maximum_length || ')'
                            WHEN c.numeric_precision IS NOT NULL
                            THEN '(' || c.numeric_precision || ',' || COALESCE(c.numeric_scale, 0) || ')'
                            ELSE ''
                        END ||
                        CASE WHEN c.is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END ||
                        CASE WHEN c.column_default IS NOT NULL THEN ' DEFAULT ' || c.column_default ELSE '' END
                        as column_def
                    FROM information_schema.columns c
                    JOIN pg_tables t ON c.table_name = t.tablename
                    WHERE t.tablename = '{table}' AND t.schemaname = 'public'
                    ORDER BY c.ordinal_position
                ) cols
                LEFT JOIN (
                    SELECT 
                        conrelid::regclass::text as tablename,
                        string_agg('CONSTRAINT ' || conname || ' ' || pg_get_constraintdef(oid), ', ') as constraints
                    FROM pg_constraint
                    WHERE conrelid::regclass::text = '{table}'
                    GROUP BY conrelid
                ) cons ON cols.tablename = cons.tablename
                GROUP BY cols.tablename, cons.constraints
            """)
            
            create_stmt = cur_prod.fetchone()
            if create_stmt and create_stmt[0]:
                cur_stg.execute(create_stmt[0])
                print(f'   ✅ {table}')
        except Exception as e:
            print(f'   ⚠️  {table}: {str(e)[:80]}')
    
    print('\n📦 Copiando datos...\n')
    
    # Ahora copiar los datos
    total_rows = 0
    for table in tables:
        try:
            # Contar registros
            cur_prod.execute(f'SELECT COUNT(*) FROM {table}')
            count = cur_prod.fetchone()[0]
            
            if count == 0:
                print(f'   ⚪ {table}: vacía')
                continue
            
            # Obtener nombres de columnas
            cur_prod.execute(f'SELECT * FROM {table} LIMIT 0')
            columns = [desc[0] for desc in cur_prod.description]
            
            # Limpiar tabla en staging
            cur_stg.execute(f'TRUNCATE TABLE {table} CASCADE')
            
            # Copiar datos en lotes
            cur_prod.execute(f'SELECT * FROM {table}')
            rows = cur_prod.fetchall()
            
            if rows:
                placeholders = ','.join(['%s'] * len(columns))
                insert_query = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
                cur_stg.executemany(insert_query, rows)
                total_rows += len(rows)
                print(f'   ✅ {table}: {len(rows)} registros')
            
        except Exception as e:
            print(f'   ❌ {table}: {str(e)[:100]}')
    
    print(f'\n✅ Total de registros copiados: {total_rows:,}')
    
    cur_prod.close()
    cur_stg.close()
    conn_prod.close()
    conn_staging.close()
    
    print('\n' + '=' * 70)
    print('✅ SINCRONIZACIÓN COMPLETADA')
    print('=' * 70)
    print('\n🎯 Reinicia el contenedor de staging:')
    print('   docker compose -f docker-compose.staging.yml restart app\n')
    
except Exception as e:
    print(f'\n❌ Error: {e}')
    import traceback
    traceback.print_exc()
