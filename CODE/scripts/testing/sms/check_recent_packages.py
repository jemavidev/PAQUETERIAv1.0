#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar paquetes recientes y sus notificaciones
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from pathlib import Path
from dotenv import load_dotenv

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

def check_recent_activity():
    """Verifica la actividad reciente en el sistema"""
    
    print("=" * 70)
    print("VERIFICACIÓN DE ACTIVIDAD RECIENTE")
    print("=" * 70)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Paquetes creados hoy
        print(f"\n📦 Paquetes creados hoy:")
        cursor.execute("""
            SELECT 
                p.id,
                p.tracking_number,
                p.status,
                p.created_at,
                c.full_name,
                c.phone
            FROM packages p
            JOIN customers c ON p.customer_id = c.id
            WHERE p.created_at >= CURRENT_DATE
            ORDER BY p.created_at DESC
            LIMIT 20;
        """)
        
        packages = cursor.fetchall()
        if packages:
            for pkg in packages:
                print(f"\n   • ID: {pkg['id']}")
                print(f"     Tracking: {pkg['tracking_number']}")
                print(f"     Cliente: {pkg['full_name']} ({pkg['phone']})")
                print(f"     Estado: {pkg['status']}")
                print(f"     Creado: {pkg['created_at']}")
        else:
            print("   ⚠️  No hay paquetes creados hoy")
        
        # Notificaciones enviadas hoy
        print(f"\n📱 Notificaciones enviadas hoy:")
        cursor.execute("""
            SELECT 
                id,
                recipient,
                notification_type,
                status,
                message,
                error_message,
                created_at,
                sent_at
            FROM notifications
            WHERE created_at >= CURRENT_DATE
            ORDER BY created_at DESC
            LIMIT 20;
        """)
        
        notifications = cursor.fetchall()
        if notifications:
            for notif in notifications:
                print(f"\n   • ID: {notif['id']}")
                print(f"     Destinatario: {notif['recipient']}")
                print(f"     Estado: {notif['status']}")
                print(f"     Mensaje: {notif['message'][:50]}...")
                if notif['error_message']:
                    print(f"     ❌ Error: {notif['error_message']}")
                print(f"     Creado: {notif['created_at']}")
                print(f"     Enviado: {notif['sent_at']}")
        else:
            print("   ⚠️  No hay notificaciones SMS enviadas hoy")
        
        # Clientes registrados hoy
        print(f"\n👥 Clientes registrados hoy:")
        cursor.execute("""
            SELECT 
                id,
                full_name,
                phone,
                email,
                created_at
            FROM customers
            WHERE created_at >= CURRENT_DATE
            ORDER BY created_at DESC
            LIMIT 10;
        """)
        
        customers = cursor.fetchall()
        if customers:
            for customer in customers:
                print(f"\n   • {customer['full_name']}")
                print(f"     Teléfono: {customer['phone']}")
                print(f"     Email: {customer['email']}")
                print(f"     Registrado: {customer['created_at']}")
        else:
            print("   ⚠️  No hay clientes registrados hoy")
        
        # Configuración de SMS
        print(f"\n⚙️  Configuración de SMS:")
        cursor.execute("""
            SELECT 
                provider,
                account_id,
                enable_test_mode,
                is_active
            FROM sms_configuration
            LIMIT 1;
        """)
        
        config = cursor.fetchone()
        if config:
            print(f"   • Proveedor: {config['provider']}")
            print(f"   • Cuenta: {config['account_id']}")
            print(f"   • Modo prueba: {'SÍ' if config['enable_test_mode'] else 'NO'}")
            print(f"   • Activo: {'SÍ' if config['is_active'] else 'NO'}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    check_recent_activity()
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
