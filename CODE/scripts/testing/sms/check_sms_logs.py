#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar los logs de SMS enviados
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Cargar variables de entorno
env_path = Path(__file__).parent.parent.parent.parent / '.env'
load_dotenv(env_path)

# Configuración de base de datos
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST'),
    'port': os.getenv('POSTGRES_PORT', 5432),
    'database': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD')
}

def check_sms_for_number(phone_number):
    """Verifica los SMS enviados a un número específico"""
    
    print("=" * 70)
    print(f"VERIFICACIÓN DE SMS PARA: {phone_number}")
    print("=" * 70)
    
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Buscar en la tabla de notificaciones
        print(f"\n🔍 Buscando notificaciones SMS...")
        
        # Primero, verificar qué tablas existen
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%notif%' OR table_name LIKE '%sms%'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"\n📋 Tablas relacionadas con notificaciones/SMS:")
        for table in tables:
            print(f"   • {table['table_name']}")
        
        # Intentar buscar en la tabla notifications
        if any(t['table_name'] == 'notifications' for t in tables):
            print(f"\n📊 Consultando tabla 'notifications'...")
            
            # Primero ver la estructura de la tabla
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'notifications'
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            print(f"\n📋 Columnas de la tabla 'notifications':")
            for col in columns:
                print(f"   • {col['column_name']} ({col['data_type']})")
            
            # Buscar notificaciones del número (últimos 7 días)
            cursor.execute("""
                SELECT *
                FROM notifications
                WHERE recipient LIKE %s
                AND created_at >= NOW() - INTERVAL '7 days'
                ORDER BY created_at DESC
                LIMIT 20;
            """, (f'%{phone_number}%',))
            
            notifications = cursor.fetchall()
            
            if notifications:
                print(f"\n✅ Se encontraron {len(notifications)} notificaciones:")
                print("=" * 70)
                
                for notif in notifications:
                    print(f"\n📱 Notificación ID: {notif.get('id')}")
                    print(f"   • Destinatario: {notif.get('recipient')}")
                    print(f"   • Tipo: {notif.get('notification_type', notif.get('event_type', 'N/A'))}")
                    print(f"   • Estado: {notif.get('status')}")
                    print(f"   • Mensaje: {notif.get('message_preview', notif.get('message', 'N/A'))}")
                    if notif.get('error_message'):
                        print(f"   • ❌ Error: {notif['error_message']}")
                    print(f"   • Enviado: {notif.get('sent_at', 'N/A')}")
                    print(f"   • Creado: {notif.get('created_at')}")
                    print("-" * 70)
            else:
                print(f"\n⚠️  No se encontraron notificaciones para {phone_number}")
                
                # Buscar el cliente en la tabla de clientes
                print(f"\n🔍 Buscando cliente en la base de datos...")
                
                # Ver estructura de customers
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'customers'
                    ORDER BY ordinal_position;
                """)
                
                cust_columns = cursor.fetchall()
                print(f"\n📋 Columnas de la tabla 'customers':")
                for col in cust_columns:
                    print(f"   • {col['column_name']} ({col['data_type']})")
                
                cursor.execute("""
                    SELECT *
                    FROM customers
                    WHERE phone LIKE %s
                    LIMIT 5;
                """, (f'%{phone_number}%',))
                
                customers = cursor.fetchall()
                if customers:
                    print(f"\n✅ Cliente encontrado:")
                    for customer in customers:
                        print(f"   • ID: {customer.get('id')}")
                        print(f"   • Nombre: {customer.get('full_name', customer.get('name', 'N/A'))}")
                        print(f"   • Teléfono: {customer.get('phone')}")
                        print(f"   • Email: {customer.get('email')}")
                        print(f"   • Registrado: {customer.get('created_at')}")
                else:
                    print(f"\n⚠️  Cliente no encontrado en la base de datos")
        
        # Buscar paquetes del cliente
        print(f"\n📦 Buscando paquetes del cliente...")
        cursor.execute("""
            SELECT 
                p.id,
                p.tracking_number,
                p.status,
                p.created_at,
                p.updated_at,
                c.full_name as customer_name,
                c.phone as customer_phone
            FROM packages p
            JOIN customers c ON p.customer_id = c.id
            WHERE c.phone LIKE %s
            ORDER BY p.created_at DESC
            LIMIT 10;
        """, (f'%{phone_number}%',))
        
        packages = cursor.fetchall()
        if packages:
            print(f"\n✅ Se encontraron {len(packages)} paquetes:")
            for pkg in packages:
                print(f"\n📦 Paquete ID: {pkg['id']}")
                print(f"   • Tracking: {pkg['tracking_number']}")
                print(f"   • Estado: {pkg['status']}")
                print(f"   • Cliente: {pkg['customer_name']}")
                print(f"   • Teléfono: {pkg['customer_phone']}")
                print(f"   • Creado: {pkg['created_at']}")
                print(f"   • Actualizado: {pkg['updated_at']}")
        else:
            print(f"\n⚠️  No se encontraron paquetes para este cliente")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """Función principal"""
    
    # Número a verificar
    PHONE_NUMBER = "3008103849"
    
    print(f"\n🔧 Conectando a la base de datos...")
    print(f"   • Host: {DB_CONFIG['host']}")
    print(f"   • Database: {DB_CONFIG['database']}")
    print(f"   • User: {DB_CONFIG['user']}")
    
    check_sms_for_number(PHONE_NUMBER)
    
    print("\n" + "=" * 70)
    print("VERIFICACIÓN COMPLETADA")
    print("=" * 70)

if __name__ == "__main__":
    main()
