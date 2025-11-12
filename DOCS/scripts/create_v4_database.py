#!/usr/bin/env python3
"""
PAQUETERÍA v4.0 - Script para crear base de datos v4.0 en AWS RDS
"""

import psycopg2
import sys
import os
from datetime import datetime

def create_v4_database():
    """Crear la base de datos paqueteria_v4 en AWS RDS"""

    # Credenciales de conexión (usando las mismas que v3.5 pero conectando a 'postgres' para crear nueva DB)
    db_config = {
        'host': 'ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com',
        'port': 5432,
        'user': 'jveyes',
        'password': 'a?HC!2.*1#?[==:|289qAI=)#V4kDzl$',
        'database': 'postgres'  # Conectar a la base de datos por defecto para crear nueva
    }

    try:
        print("🔄 Conectando a AWS RDS...")
        # Conectar a la base de datos 'postgres' (base de datos por defecto)
        conn = psycopg2.connect(**db_config)
        conn.autocommit = True  # Necesario para crear bases de datos
        cursor = conn.cursor()

        print("✅ Conexión exitosa a AWS RDS")

        # Verificar si la base de datos ya existe
        cursor.execute("SELECT datname FROM pg_database WHERE datname = 'paqueteria_v4'")
        exists = cursor.fetchone()

        if exists:
            print("⚠️  La base de datos 'paqueteria_v4' ya existe")
            response = input("¿Desea eliminarla y crearla nuevamente? (y/N): ")
            if response.lower() == 'y':
                print("🗑️  Eliminando base de datos existente...")
                cursor.execute("DROP DATABASE paqueteria_v4")
                print("✅ Base de datos eliminada")
            else:
                print("ℹ️  Manteniendo base de datos existente")
                cursor.close()
                conn.close()
                return True

        # Crear la nueva base de datos
        print("🏗️  Creando base de datos 'paqueteria_v4'...")
        cursor.execute("CREATE DATABASE paqueteria_v4")

        print("✅ Base de datos 'paqueteria_v4' creada exitosamente")

        # Verificar la creación
        cursor.execute("SELECT datname FROM pg_database WHERE datname = 'paqueteria_v4'")
        result = cursor.fetchone()

        if result:
            print("🎉 Base de datos verificada correctamente")
            print(f"📊 Base de datos: {result[0]}")
        else:
            print("❌ Error: No se pudo verificar la creación de la base de datos")
            return False

        cursor.close()
        conn.close()

        print("\n" + "="*50)
        print("✅ BASE DE DATOS v4.0 CREADA EXITOSAMENTE")
        print("="*50)
        print("📍 Host: ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com")
        print("📍 Puerto: 5432")
        print("📍 Base de datos: paqueteria_v4")
        print("📍 Usuario: jveyes")
        print(f"📅 Creada el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*50)

        return True

    except psycopg2.Error as e:
        print(f"❌ Error de PostgreSQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

def test_v4_connection():
    """Probar conexión a la nueva base de datos v4.0"""

    print("\n🔍 Probando conexión a paqueteria_v4...")

    db_config_v4 = {
        'host': 'ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com',
        'port': 5432,
        'user': 'jveyes',
        'password': 'a?HC!2.*1#?[==:|289qAI=)#V4kDzl$',
        'database': 'paqueteria_v4'
    }

    try:
        conn = psycopg2.connect(**db_config_v4)
        cursor = conn.cursor()

        # Ejecutar una consulta simple
        cursor.execute("SELECT version()")
        version = cursor.fetchone()

        print("✅ Conexión a paqueteria_v4 exitosa")
        print(f"📊 PostgreSQL versión: {version[0][:50]}...")

        cursor.close()
        conn.close()
        return True

    except psycopg2.Error as e:
        print(f"❌ Error conectando a paqueteria_v4: {e}")
        return False

if __name__ == "__main__":
    print("🚀 PAQUETERÍA v4.0 - CREACIÓN DE BASE DE DATOS")
    print("="*50)

    # Crear la base de datos
    success = create_v4_database()

    if success:
        # Probar la conexión
        test_success = test_v4_connection()

        if test_success:
            print("\n🎉 PROCESO COMPLETADO EXITOSAMENTE")
            print("📝 Siguientes pasos:")
            print("   1. Actualizar .env para usar DATABASE_URL con paqueteria_v4")
            print("   2. Ejecutar migraciones: alembic upgrade head")
            print("   3. Verificar que la aplicación funciona")
            sys.exit(0)
        else:
            print("\n❌ Error en la verificación de conexión")
            sys.exit(1)
    else:
        print("\n❌ Error en la creación de la base de datos")
        sys.exit(1)