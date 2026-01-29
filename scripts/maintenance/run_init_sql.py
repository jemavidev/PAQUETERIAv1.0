#!/usr/bin/env python3
"""
Script para ejecutar init_database.sql en staging
"""
import psycopg2

# Credenciales
db_host = "ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com"
db_user = "jveyes"
db_pass = "a?HC!2.*1#?[==:|289qAI=)#V4kDzl$"
db_port = "5432"

print('🔧 Inicializando base de datos staging...')
print(f'📊 Base de datos: paqueteria_staging')
print()

try:
    # Leer el archivo SQL
    with open('/init.sql', 'r') as f:
        sql_script = f.read()
    
    # Conectar a staging
    print('🔌 Conectando a staging...')
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_pass,
        database='paqueteria_staging'
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Ejecutar el script
    print('📋 Ejecutando script de inicialización...')
    cursor.execute(sql_script)
    
    # Verificar tablas creadas
    cursor.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        ORDER BY tablename
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f'✅ {len(tables)} tablas en la base de datos:')
    for table in tables:
        print(f'   - {table}')
    
    # Verificar usuario admin
    cursor.execute("SELECT username, role FROM users WHERE username = 'admin'")
    admin = cursor.fetchone()
    if admin:
        print(f'\n✅ Usuario admin creado: {admin[0]} ({admin[1]})')
    
    cursor.close()
    conn.close()
    
    print('\n✅ Base de datos inicializada correctamente')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
