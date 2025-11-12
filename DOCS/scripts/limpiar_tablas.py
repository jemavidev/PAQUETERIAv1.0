#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Script de Limpieza de Tablas
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo

Este script limpia las tablas de la base de datos paqueteria_v4
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import sys

# Configuración de la base de datos
db_config = {
    'host': 'ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com',
    'port': 5432,
    'database': 'paqueteria_v4',
    'user': 'jveyes',
    'password': 'a?HC!2.*1#?[==:|289qAI=)#V4kDzl$***'
}

def limpiar_tablas():
    """Limpiar todas las tablas de la base de datos"""
    try:
        # Conectar a la base de datos
        connection = psycopg2.connect(**db_config)
        connection.autocommit = True
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        print("✅ Conexión exitosa a la base de datos")
        
        # Verificar estado actual
        print("\n📊 Estado actual de las tablas:")
        cursor.execute("""
            SELECT tablename, n_tup_ins as inserts 
            FROM pg_stat_user_tables 
            WHERE schemaname = 'public' 
            ORDER BY tablename
        """)
        tables = cursor.fetchall()
        
        for table in tables:
            print(f"  • {table['tablename']}: {table['inserts']} registros")
        
        # Limpiar tablas en orden correcto
        print("\n🗑️ Limpiando tablas...")
        
        cleanup_queries = [
            "DELETE FROM file_uploads",
            "DELETE FROM messages", 
            "DELETE FROM package_history",
            "DELETE FROM package_announcements_new",
            "DELETE FROM packages",
            "DELETE FROM customers"
        ]
        
        total_deleted = 0
        for query in cleanup_queries:
            table_name = query.split()[-1]
            try:
                cursor.execute(query)
                deleted_count = cursor.rowcount
                total_deleted += deleted_count
                print(f"  ✅ {table_name}: {deleted_count} registros eliminados")
            except Exception as e:
                print(f"  ⚠️ Error en {table_name}: {e}")
        
        # Resetear secuencias
        print("\n🔄 Reseteando secuencias...")
        sequences = [
            'packages_id_seq',
            'messages_id_seq', 
            'file_uploads_id_seq',
            'customers_id_seq'
        ]
        
        for sequence in sequences:
            try:
                cursor.execute(f"ALTER SEQUENCE {sequence} RESTART WITH 1")
                print(f"  ✅ {sequence} reseteada")
            except Exception as e:
                print(f"  ⚠️ Error en {sequence}: {e}")
        
        # Verificar limpieza
        print("\n✅ Verificando limpieza...")
        cursor.execute("""
            SELECT tablename, n_tup_ins as inserts 
            FROM pg_stat_user_tables 
            WHERE schemaname = 'public' 
            ORDER BY tablename
        """)
        tables_after = cursor.fetchall()
        
        all_empty = True
        for table in tables_after:
            if table['inserts'] > 0:
                print(f"  ⚠️ {table['tablename']}: {table['inserts']} registros restantes")
                all_empty = False
            else:
                print(f"  ✅ {table['tablename']}: vacía")
        
        if all_empty:
            print(f"\n🎉 Limpieza completada exitosamente!")
            print(f"📊 Total de registros eliminados: {total_deleted}")
        else:
            print(f"\n⚠️ Algunas tablas no se limpiaron completamente")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 PAQUETES EL CLUB v1.0 - Limpieza de Tablas")
    print("="*50)
    limpiar_tablas()
