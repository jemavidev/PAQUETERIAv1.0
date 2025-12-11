#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Verificación Previa - Solo Consulta
==============================================
Muestra qué se eliminará SIN eliminar nada.
Útil para verificar antes de ejecutar la limpieza real.

Autor: Sistema PAQUETEX
Fecha: 11 de Diciembre, 2025
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Clientes a verificar
CLIENTES_PRUEBA = [
    '+573001234567',
    '+573002596319',
    '+573008103849',
    '+573008398365'
]

def get_db_connection():
    """Obtener conexión a la base de datos RDS"""
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
        print(f"❌ Error conectando a la base de datos: {e}")
        sys.exit(1)

def main():
    """Función principal"""
    print("\n" + "="*60)
    print("VERIFICACIÓN PREVIA - DATOS A ELIMINAR")
    print("="*60 + "\n")
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print(f"✅ Conectado a: {os.getenv('POSTGRES_HOST')}\n")
    
    # ========================================
    # CLIENTES DE PRUEBA
    # ========================================
    print("📊 CLIENTES DE PRUEBA")
    print("-" * 60)
    
    # Listar clientes
    cursor.execute("""
        SELECT id, phone, full_name, email, 
               total_packages_received, total_packages_delivered
        FROM customers 
        WHERE phone = ANY(%s)
        ORDER BY phone
    """, (CLIENTES_PRUEBA,))
    
    clientes = cursor.fetchall()
    print(f"\n🔍 Clientes encontrados: {len(clientes)}\n")
    
    for cliente in clientes:
        print(f"  📱 {cliente['phone']}")
        print(f"     Nombre: {cliente['full_name']}")
        print(f"     Email: {cliente['email'] or 'N/A'}")
        print(f"     Paquetes recibidos: {cliente['total_packages_received']}")
        print(f"     Paquetes entregados: {cliente['total_packages_delivered']}")
        print()
    
    # Paquetes por estado
    cursor.execute("""
        SELECT status, COUNT(*) as total
        FROM packages 
        WHERE customer_id IN (
            SELECT id FROM customers WHERE phone = ANY(%s)
        )
        GROUP BY status
        ORDER BY status
    """, (CLIENTES_PRUEBA,))
    
    paquetes_por_estado = cursor.fetchall()
    print("📦 Paquetes de estos clientes por estado:")
    total_paquetes = 0
    for row in paquetes_por_estado:
        print(f"  - {row['status']}: {row['total']}")
        total_paquetes += row['total']
    print(f"  TOTAL: {total_paquetes}\n")
    
    # Anuncios
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM package_announcements_new 
        WHERE customer_id IN (
            SELECT id FROM customers WHERE phone = ANY(%s)
        )
    """, (CLIENTES_PRUEBA,))
    total_anuncios = cursor.fetchone()['total']
    print(f"📢 Anuncios: {total_anuncios}")
    
    # Eventos
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM package_events 
        WHERE customer_id IN (
            SELECT id FROM customers WHERE phone = ANY(%s)
        )
    """, (CLIENTES_PRUEBA,))
    total_eventos = cursor.fetchone()['total']
    print(f"📝 Eventos: {total_eventos}")
    
    # Archivos
    cursor.execute("""
        SELECT COUNT(*) as total, 
               COUNT(CASE WHEN s3_key IS NOT NULL THEN 1 END) as en_s3
        FROM file_uploads 
        WHERE package_id IN (
            SELECT id FROM packages 
            WHERE customer_id IN (
                SELECT id FROM customers WHERE phone = ANY(%s)
            )
        )
    """, (CLIENTES_PRUEBA,))
    archivos = cursor.fetchone()
    print(f"📁 Archivos: {archivos['total']} (en S3: {archivos['en_s3']})")
    
    # Mensajes
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM messages 
        WHERE customer_id IN (
            SELECT id FROM customers WHERE phone = ANY(%s)
        ) OR package_id IN (
            SELECT id FROM packages 
            WHERE customer_id IN (
                SELECT id FROM customers WHERE phone = ANY(%s)
            )
        )
    """, (CLIENTES_PRUEBA, CLIENTES_PRUEBA))
    total_mensajes = cursor.fetchone()['total']
    print(f"💬 Mensajes: {total_mensajes}")
    
    # Notificaciones
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM notifications 
        WHERE customer_id IN (
            SELECT id FROM customers WHERE phone = ANY(%s)
        ) OR package_id IN (
            SELECT id FROM packages 
            WHERE customer_id IN (
                SELECT id FROM customers WHERE phone = ANY(%s)
            )
        )
    """, (CLIENTES_PRUEBA, CLIENTES_PRUEBA))
    total_notificaciones = cursor.fetchone()['total']
    print(f"🔔 Notificaciones: {total_notificaciones}")
    
    # ========================================
    # PAQUETES CANCELADOS
    # ========================================
    print("\n" + "="*60)
    print("📊 PAQUETES CANCELADOS")
    print("-" * 60 + "\n")
    
    # Total cancelados
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM packages 
        WHERE status = 'CANCELADO'
    """)
    total_cancelados = cursor.fetchone()['total']
    print(f"📦 Paquetes cancelados: {total_cancelados}")
    
    # Eventos de cancelados
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM package_events 
        WHERE package_id IN (
            SELECT id FROM packages WHERE status = 'CANCELADO'
        )
    """)
    eventos_cancelados = cursor.fetchone()['total']
    print(f"📝 Eventos: {eventos_cancelados}")
    
    # Historial de cancelados
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM package_history 
        WHERE package_id IN (
            SELECT id FROM packages WHERE status = 'CANCELADO'
        )
    """)
    historial_cancelados = cursor.fetchone()['total']
    print(f"📚 Historial: {historial_cancelados}")
    
    # Archivos de cancelados
    cursor.execute("""
        SELECT COUNT(*) as total,
               COUNT(CASE WHEN s3_key IS NOT NULL THEN 1 END) as en_s3
        FROM file_uploads 
        WHERE package_id IN (
            SELECT id FROM packages WHERE status = 'CANCELADO'
        )
    """)
    archivos_cancelados = cursor.fetchone()
    print(f"📁 Archivos: {archivos_cancelados['total']} (en S3: {archivos_cancelados['en_s3']})")
    
    # Algunos ejemplos de paquetes cancelados
    cursor.execute("""
        SELECT tracking_number, guide_number, cancelled_at
        FROM packages 
        WHERE status = 'CANCELADO'
        ORDER BY cancelled_at DESC
        LIMIT 5
    """)
    ejemplos = cursor.fetchall()
    
    if ejemplos:
        print(f"\n🔍 Ejemplos de paquetes cancelados (últimos 5):")
        for pkg in ejemplos:
            print(f"  - {pkg['tracking_number']} | Guía: {pkg['guide_number']} | Cancelado: {pkg['cancelled_at']}")
    
    # ========================================
    # RESUMEN TOTAL
    # ========================================
    print("\n" + "="*60)
    print("📊 RESUMEN TOTAL A ELIMINAR")
    print("="*60 + "\n")
    
    print(f"👥 Clientes: {len(clientes)}")
    print(f"📦 Paquetes (clientes): {total_paquetes}")
    print(f"📦 Paquetes (cancelados): {total_cancelados}")
    print(f"📦 TOTAL PAQUETES: {total_paquetes + total_cancelados}")
    print(f"📢 Anuncios: {total_anuncios}")
    print(f"📝 Eventos: {total_eventos + eventos_cancelados}")
    print(f"📚 Historial: {historial_cancelados}")
    print(f"📁 Archivos BD: {archivos['total'] + archivos_cancelados['total']}")
    print(f"☁️  Archivos S3: {archivos['en_s3'] + archivos_cancelados['en_s3']}")
    print(f"💬 Mensajes: {total_mensajes}")
    print(f"🔔 Notificaciones: {total_notificaciones}")
    
    print("\n" + "="*60)
    print("✅ Verificación completada")
    print("="*60 + "\n")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
