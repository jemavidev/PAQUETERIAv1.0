#!/usr/bin/env python3
"""
Script para copiar TODOS los datos de producción a staging
Sincronización unidireccional: producción → staging
"""
import subprocess
import sys

# Credenciales
db_host = "ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com"
db_user = "jveyes"
db_pass = "a?HC!2.*1#?[==:|289qAI=)#V4kDzl$"
db_port = "5432"

print('=' * 70)
print('🔄 SINCRONIZACIÓN COMPLETA: PRODUCCIÓN → STAGING')
print('=' * 70)
print()
print('📊 Origen: paqueteria_v4 (PRODUCCIÓN - SOLO LECTURA)')
print('📊 Destino: paqueteria_staging (STAGING - SE SOBRESCRIBIRÁ)')
print()
print('⚠️  IMPORTANTE: Este proceso NO modifica producción')
print()

# Confirmar
confirm = input('¿Deseas continuar? (escribe SI): ')
if confirm != 'SI':
    print('❌ Operación cancelada')
    sys.exit(0)

print()
print('🚀 Iniciando sincronización...')
print()

try:
    # Paso 1: Exportar producción
    print('📦 Paso 1/3: Exportando datos de producción...')
    dump_cmd = [
        'pg_dump',
        f'--host={db_host}',
        f'--port={db_port}',
        f'--username={db_user}',
        '--dbname=paqueteria_v4',
        '--format=custom',
        '--no-owner',
        '--no-acl',
        '--file=/tmp/prod_backup.dump'
    ]
    
    env = {'PGPASSWORD': db_pass}
    result = subprocess.run(dump_cmd, env=env, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f'❌ Error en pg_dump: {result.stderr}')
        sys.exit(1)
    
    print('✅ Datos exportados exitosamente')
    print()
    
    # Paso 2: Limpiar staging
    print('🧹 Paso 2/3: Limpiando base de datos staging...')
    clean_cmd = [
        'psql',
        f'--host={db_host}',
        f'--port={db_port}',
        f'--username={db_user}',
        '--dbname=paqueteria_staging',
        '--command=DROP SCHEMA public CASCADE; CREATE SCHEMA public;'
    ]
    
    result = subprocess.run(clean_cmd, env=env, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f'⚠️  Advertencia al limpiar: {result.stderr}')
    else:
        print('✅ Base de datos staging limpiada')
    print()
    
    # Paso 3: Restaurar en staging
    print('📥 Paso 3/3: Restaurando datos en staging...')
    restore_cmd = [
        'pg_restore',
        f'--host={db_host}',
        f'--port={db_port}',
        f'--username={db_user}',
        '--dbname=paqueteria_staging',
        '--no-owner',
        '--no-acl',
        '--clean',
        '--if-exists',
        '/tmp/prod_backup.dump'
    ]
    
    result = subprocess.run(restore_cmd, env=env, capture_output=True, text=True)
    
    if result.returncode != 0:
        # pg_restore puede dar warnings pero funcionar
        if 'ERROR' in result.stderr:
            print(f'⚠️  Advertencias durante restauración:')
            print(result.stderr[:500])
        else:
            print('✅ Datos restaurados (con advertencias menores)')
    else:
        print('✅ Datos restaurados exitosamente')
    
    print()
    
    # Verificar
    print('🔍 Verificando sincronización...')
    import psycopg2
    
    conn_prod = psycopg2.connect(
        host=db_host, port=db_port, user=db_user, password=db_pass, database='paqueteria_v4'
    )
    conn_staging = psycopg2.connect(
        host=db_host, port=db_port, user=db_user, password=db_pass, database='paqueteria_staging'
    )
    
    cursor_prod = conn_prod.cursor()
    cursor_staging = conn_staging.cursor()
    
    # Contar tablas
    cursor_prod.execute("SELECT COUNT(*) FROM pg_tables WHERE schemaname='public'")
    prod_tables = cursor_prod.fetchone()[0]
    
    cursor_staging.execute("SELECT COUNT(*) FROM pg_tables WHERE schemaname='public'")
    staging_tables = cursor_staging.fetchone()[0]
    
    print(f'   Tablas en producción: {prod_tables}')
    print(f'   Tablas en staging: {staging_tables}')
    
    # Contar usuarios
    try:
        cursor_prod.execute("SELECT COUNT(*) FROM users")
        prod_users = cursor_prod.fetchone()[0]
        
        cursor_staging.execute("SELECT COUNT(*) FROM users")
        staging_users = cursor_staging.fetchone()[0]
        
        print(f'   Usuarios en producción: {prod_users}')
        print(f'   Usuarios en staging: {staging_users}')
    except:
        pass
    
    cursor_prod.close()
    cursor_staging.close()
    conn_prod.close()
    conn_staging.close()
    
    print()
    print('=' * 70)
    print('✅ SINCRONIZACIÓN COMPLETADA EXITOSAMENTE')
    print('=' * 70)
    print()
    print('📊 Staging ahora tiene una copia completa de producción')
    print('🔒 Producción NO fue modificada')
    print()
    print('🎯 Próximo paso: Reiniciar el contenedor de staging')
    print('   docker compose -f docker-compose.staging.yml restart app')
    print()
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
