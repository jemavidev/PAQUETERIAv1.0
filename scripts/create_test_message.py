#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear un mensaje de prueba en la base de datos
PAQUETEX - Sistema de Gestión de Paquetes
Fecha: 2024-12-17
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from datetime import datetime

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

def get_package_id(cursor, tracking_number):
    """Obtener el ID de un paquete por su tracking number"""
    cursor.execute("""
        SELECT id FROM packages WHERE tracking_number = %s
    """, (tracking_number,))
    result = cursor.fetchone()
    return result['id'] if result else None

def create_test_message(cursor, tracking_number='SVC5'):
    """Crear un mensaje de prueba"""
    
    # Obtener el ID del paquete
    package_id = get_package_id(cursor, tracking_number)
    
    if not package_id:
        print(f"⚠️  Paquete con tracking {tracking_number} no encontrado")
        print("Creando mensaje sin paquete asociado...")
    
    # Crear el mensaje
    cursor.execute("""
        INSERT INTO messages (
            subject,
            content,
            message_type,
            priority,
            status,
            is_read,
            package_id,
            sender_name,
            sender_email,
            sender_phone,
            tracking_code,
            created_at,
            updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) RETURNING id
    """, (
        f'PAQUETE {tracking_number}',
        f'Hola, quisiera saber el estado de mi paquete {tracking_number}. ¿Cuándo llegará?',
        'CONSULTA',
        'MEDIA',
        'ABIERTO',
        False,
        package_id,
        'Juan Pérez',
        'juan.perez@example.com',
        '3001234567',
        tracking_number,
        datetime.now(),
        datetime.now()
    ))
    
    result = cursor.fetchone()
    message_id = result[0] if result else None
    return message_id

def main():
    """Función principal"""
    print("=" * 80)
    print("📝 CREACIÓN DE MENSAJE DE PRUEBA")
    print("=" * 80)
    print()
    
    # Conectar a la base de datos
    try:
        conn = connect_to_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ Conectado a la base de datos RDS")
        print()
        
        # Preguntar qué tracking number usar
        print("Paquetes disponibles: SVC5, MBBW, 9IBC")
        tracking_number = input("Ingresa el tracking number del paquete (o presiona Enter para SVC5): ").strip().upper()
        
        if not tracking_number:
            tracking_number = 'SVC5'
        
        print()
        print(f"📦 Creando mensaje para paquete {tracking_number}...")
        
        # Crear mensaje
        message_id = create_test_message(cursor, tracking_number)
        
        # Commit
        conn.commit()
        
        print(f"✅ Mensaje creado exitosamente con ID: {message_id}")
        print()
        
        # Mostrar el mensaje creado
        cursor.execute("""
            SELECT 
                id,
                subject,
                content,
                status,
                tracking_code,
                sender_name,
                sender_phone,
                created_at
            FROM messages
            WHERE id = %s
        """, (message_id,))
        
        message = cursor.fetchone()
        
        print("📋 DETALLE DEL MENSAJE CREADO:")
        print("-" * 80)
        print(f"ID: {message['id']}")
        print(f"Asunto: {message['subject']}")
        print(f"Contenido: {message['content']}")
        print(f"Estado: {message['status']}")
        print(f"Tracking: {message['tracking_code']}")
        print(f"Cliente: {message['sender_name']}")
        print(f"Teléfono: {message['sender_phone']}")
        print(f"Fecha: {message['created_at']}")
        print()
        
        print("=" * 80)
        print("✅ PROCESO COMPLETADO")
        print("=" * 80)
        print()
        print(f"🌐 Puedes ver el mensaje en: https://staging.jemavi.co/messages")
        print(f"🔍 ID del mensaje: {message_id}")
        
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
