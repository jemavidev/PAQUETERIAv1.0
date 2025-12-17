#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para eliminar TODOS los mensajes directamente desde la base de datos RDS
PAQUETEX - Sistema de Gestión de Paquetes
Fecha: 2024-12-17

⚠️ ADVERTENCIA: Este script eliminará TODOS los mensajes de forma permanente
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def connect_to_db():
    """Conectar a la base de datos RDS"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT', 5432),
            database=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD')
        )
        return conn
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos: {str(e)}")
        raise

def show_messages_stats(cursor):
    """Mostrar estadísticas de mensajes"""
    print("📊 ESTADÍSTICAS DE MENSAJES:")
    print("-" * 80)
    
    # Contar total
    cursor.execute("SELECT COUNT(*) as total FROM messages")
    total = cursor.fetchone()['total']
    
    if total == 0:
        print("✅ No hay mensajes en la base de datos")
        return False
    
    print(f"Total de mensajes: {total}")
    
    # Contar por estado
    cursor.execute("""
        SELECT 
            status,
            COUNT(*) as count
        FROM messages
        GROUP BY status
        ORDER BY status
    """)
    
    estados = cursor.fetchall()
    for estado in estados:
        print(f"  - {estado['status']}: {estado['count']}")
    
    print()
    return True

def show_messages_detail(cursor):
    """Mostrar detalle de cada mensaje"""
    print("📋 DETALLE DE MENSAJES:")
    print("-" * 80)
    
    cursor.execute("""
        SELECT 
            m.id,
            m.subject,
            m.status,
            m.tracking_code,
            m.created_at
        FROM messages m
        ORDER BY m.created_at DESC
    """)
    
    messages = cursor.fetchall()
    for msg in messages:
        tracking = msg['tracking_code'] or 'N/A'
        subject = msg['subject'][:40] if msg['subject'] else 'Sin asunto'
        print(f"  ID: {msg['id']:3d} | Estado: {msg['status']:12s} | Tracking: {tracking:10s} | Asunto: {subject}")
    
    print()

def delete_all_messages(cursor):
    """Eliminar todos los mensajes"""
    print("🗑️  Eliminando mensajes...")
    
    cursor.execute("DELETE FROM messages")
    deleted_count = cursor.rowcount
    
    print(f"✅ Se eliminaron {deleted_count} mensajes exitosamente")
    return deleted_count

def verify_deletion(cursor):
    """Verificar que se eliminaron todos los mensajes"""
    cursor.execute("SELECT COUNT(*) as remaining FROM messages")
    remaining = cursor.fetchone()['remaining']
    
    print()
    print(f"📊 Mensajes restantes en la base de datos: {remaining}")
    
    if remaining == 0:
        print("✅ Todos los mensajes fueron eliminados correctamente")
        return True
    else:
        print(f"⚠️  Advertencia: Aún quedan {remaining} mensajes en la base de datos")
        return False

def main():
    """Función principal"""
    print("=" * 80)
    print("🗑️  ELIMINACIÓN DE TODOS LOS MENSAJES - CONEXIÓN DIRECTA A RDS")
    print("=" * 80)
    print()
    
    # Conectar a la base de datos
    try:
        conn = connect_to_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ Conectado a la base de datos RDS")
        print()
        
        # Mostrar estadísticas
        has_messages = show_messages_stats(cursor)
        
        if not has_messages:
            cursor.close()
            conn.close()
            return
        
        # Mostrar detalle
        show_messages_detail(cursor)
        
        # Confirmar eliminación
        print("⚠️  ADVERTENCIA: Esta operación NO se puede deshacer")
        print()
        respuesta = input("¿Estás seguro de que deseas eliminar TODOS los mensajes? (escribe 'SI' para confirmar): ")
        
        if respuesta.strip().upper() != "SI":
            print("❌ Operación cancelada")
            cursor.close()
            conn.close()
            return
        
        print()
        
        # Eliminar mensajes
        deleted_count = delete_all_messages(cursor)
        
        # Commit de la transacción
        conn.commit()
        
        # Verificar eliminación
        verify_deletion(cursor)
        
        print()
        print("=" * 80)
        print("✅ PROCESO COMPLETADO")
        print("=" * 80)
        
        # Cerrar conexión
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        raise

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operación cancelada por el usuario")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        exit(1)
