#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Script Rápido de Información de Base de Datos
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo

Este script obtiene información rápida sobre:
- Tipo y versión de PostgreSQL
- Fechas de acceso recientes
- Estado actual de las tablas
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# Configuración de la base de datos AWS RDS
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
    print('✅ Conexión exitosa a AWS RDS PostgreSQL')
    
    # 1. INFORMACIÓN BÁSICA DE LA BASE DE DATOS
    print('\n🔍 INFORMACIÓN BÁSICA')
    print('=' * 50)
    
    # Versión de PostgreSQL
    cursor.execute("SELECT version()")
    version = cursor.fetchone()['version']
    print(f'📊 Tipo: PostgreSQL')
    print(f'📊 Versión: {version}')
    
    # Información de la instancia
    cursor.execute("""
        SELECT 
            current_database() as database_name,
            current_user as current_user,
            inet_server_addr() as server_ip,
            inet_server_port() as server_port,
            current_setting('timezone') as timezone
    """)
    info = cursor.fetchone()
    print(f'📊 Base de datos: {info["database_name"]}')
    print(f'📊 Usuario: {info["current_user"]}')
    print(f'📊 Servidor: {info["server_ip"]}:{info["server_port"]}')
    print(f'📊 Zona horaria: {info["timezone"]}')
    
    # Tamaño de la base de datos
    cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database())) as size")
    size = cursor.fetchone()['size']
    print(f'📊 Tamaño: {size}')
    
    # 2. INFORMACIÓN DE TABLAS
    print('\n📊 INFORMACIÓN DE TABLAS')
    print('=' * 50)
    
    # Listar todas las tablas
    cursor.execute("""
        SELECT tablename, tableowner 
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY tablename
    """)
    tables = cursor.fetchall()
    print(f'📊 Total de tablas: {len(tables)}')
    for table in tables:
        print(f'  • {table["tablename"]} (Owner: {table["tableowner"]})')
    
    # 3. CONTEO DE REGISTROS
    print('\n📊 REGISTROS POR TABLA')
    print('=' * 50)
    
    table_names = ['packages', 'package_history', 'package_announcements_new', 'messages', 'file_uploads', 'customers']
    total_records = 0
    
    for table in table_names:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()['count']
            print(f'📊 {table}: {count:,} registros')
            total_records += count
        except Exception as e:
            print(f'⚠️ {table}: Error - {e}')
    
    print(f'📊 TOTAL: {total_records:,} registros')
    
    # 4. FECHAS DE ÚLTIMO ACCESO
    print('\n🔍 FECHAS DE ÚLTIMO ACCESO')
    print('=' * 50)
    
    cursor.execute("""
        SELECT 
            tablename,
            n_tup_ins as inserts,
            n_tup_upd as updates,
            n_tup_del as deletes,
            last_vacuum,
            last_autovacuum,
            last_analyze,
            last_autoanalyze
        FROM pg_stat_user_tables 
        WHERE schemaname = 'public'
        ORDER BY tablename
    """)
    access_info = cursor.fetchall()
    
    for table in access_info:
        print(f'📊 {table["tablename"]}:')
        print(f'  • Inserts: {table["inserts"]:,}')
        print(f'  • Updates: {table["updates"]:,}')
        print(f'  • Deletes: {table["deletes"]:,}')
        if table['last_vacuum']:
            print(f'  • Último vacuum: {table["last_vacuum"]}')
        if table['last_analyze']:
            print(f'  • Último analyze: {table["last_analyze"]}')
        print()
    
    # 5. CONEXIONES ACTIVAS
    print('🔍 CONEXIONES ACTIVAS')
    print('=' * 50)
    
    cursor.execute("""
        SELECT 
            pid,
            usename,
            application_name,
            client_addr,
            backend_start,
            state
        FROM pg_stat_activity 
        WHERE datname = current_database()
        ORDER BY backend_start DESC
    """)
    connections = cursor.fetchall()
    
    print(f'📊 Conexiones activas: {len(connections)}')
    for conn in connections:
        print(f'  • PID: {conn["pid"]}, Usuario: {conn["usename"]}, Estado: {conn["state"]}')
        print(f'    Inicio: {conn["backend_start"]}, IP: {conn["client_addr"]}')
    
    # 6. ACTIVIDAD DE LA BASE DE DATOS
    print('\n🔍 ACTIVIDAD DE LA BASE DE DATOS')
    print('=' * 50)
    
    cursor.execute("""
        SELECT 
            numbackends,
            xact_commit,
            xact_rollback,
            tup_inserted,
            tup_updated,
            tup_deleted,
            stats_reset
        FROM pg_stat_database 
        WHERE datname = current_database()
    """)
    activity = cursor.fetchone()
    
    print(f'📊 Conexiones activas: {activity["numbackends"]}')
    print(f'📊 Transacciones commit: {activity["xact_commit"]:,}')
    print(f'📊 Transacciones rollback: {activity["xact_rollback"]:,}')
    print(f'📊 Tuplas insertadas: {activity["tup_inserted"]:,}')
    print(f'📊 Tuplas actualizadas: {activity["tup_updated"]:,}')
    print(f'📊 Tuplas eliminadas: {activity["tup_deleted"]:,}')
    if activity['stats_reset']:
        print(f'📊 Estadísticas reseteadas: {activity["stats_reset"]}')
    
    print(f'\n✅ Análisis completado - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f'❌ Error de conexión: {e}')
