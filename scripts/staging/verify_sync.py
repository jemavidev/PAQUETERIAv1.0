#!/usr/bin/env python3
import psycopg2

db_host = "ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com"
db_user = "jveyes"
db_pass = "a?HC!2.*1#?[==:|289qAI=)#V4kDzl$"

print('🔍 Verificando sincronización...\n')

try:
    conn_staging = psycopg2.connect(
        host=db_host, port=5432, user=db_user, password=db_pass, database='paqueteria_staging'
    )
    cursor = conn_staging.cursor()
    
    # Contar tablas
    cursor.execute("SELECT COUNT(*) FROM pg_tables WHERE schemaname='public'")
    tables_count = cursor.fetchone()[0]
    print(f'📊 Tablas en staging: {tables_count}')
    
    # Listar algunas tablas
    cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename LIMIT 10")
    tables = cursor.fetchall()
    print('\n📋 Primeras 10 tablas:')
    for table in tables:
        print(f'   - {table[0]}')
    
    # Contar usuarios
    try:
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        print(f'\n👥 Usuarios: {users_count}')
    except Exception as e:
        print(f'\n⚠️  Tabla users: {e}')
    
    # Contar clientes
    try:
        cursor.execute("SELECT COUNT(*) FROM customers")
        customers_count = cursor.fetchone()[0]
        print(f'👤 Clientes: {customers_count}')
    except Exception as e:
        print(f'⚠️  Tabla customers: {e}')
    
    # Contar paquetes
    try:
        cursor.execute("SELECT COUNT(*) FROM packages")
        packages_count = cursor.fetchone()[0]
        print(f'📦 Paquetes: {packages_count}')
    except Exception as e:
        print(f'⚠️  Tabla packages: {e}')
    
    cursor.close()
    conn_staging.close()
    
    print('\n✅ Verificación completada')
    
except Exception as e:
    print(f'❌ Error: {e}')
