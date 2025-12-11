#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para Eliminar TODOS los Paquetes Cancelados
===================================================
Elimina todos los paquetes con estado CANCELADO y sus datos relacionados.

Autor: Sistema PAQUETEX
Fecha: 11 de Diciembre, 2025
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import psycopg2
from psycopg2.extras import RealDictCursor
import boto3
from dotenv import load_dotenv

load_dotenv()

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

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
        print(f"{Colors.FAIL}❌ Error conectando a la base de datos: {e}{Colors.ENDC}")
        sys.exit(1)

def get_s3_client():
    """Obtener cliente de S3"""
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        return s3_client
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error conectando a S3: {e}{Colors.ENDC}")
        return None

def crear_backup(conn):
    """Crear backup de paquetes cancelados"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = Path(__file__).parent.parent.parent / 'backups'
    backup_dir.mkdir(exist_ok=True)
    
    backup_file = backup_dir / f'backup_cancelados_{timestamp}.json'
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print(f"{Colors.OKCYAN}📦 Creando backup...{Colors.ENDC}")
    
    cursor.execute("""
        SELECT * FROM packages WHERE status = 'CANCELADO'
    """)
    backup_data = {'packages_cancelados': [dict(row) for row in cursor.fetchall()]}
    
    cursor.close()
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2, default=str)
    
    print(f"{Colors.OKGREEN}✅ Backup creado: {backup_file}{Colors.ENDC}")
    return str(backup_file)

def obtener_archivos_s3(conn, package_ids):
    """Obtener lista de archivos S3"""
    if not package_ids:
        return []
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""
        SELECT s3_key 
        FROM file_uploads 
        WHERE package_id = ANY(%s) AND s3_key IS NOT NULL
    """, (package_ids,))
    
    s3_keys = [row['s3_key'] for row in cursor.fetchall()]
    cursor.close()
    return s3_keys

def eliminar_archivos_s3(s3_client, s3_keys):
    """Eliminar archivos de S3"""
    if not s3_client or not s3_keys:
        return 0, 0
    
    bucket = os.getenv('AWS_S3_BUCKET')
    eliminados = 0
    errores = 0
    
    print(f"{Colors.OKCYAN}🗑️  Eliminando {len(s3_keys)} archivos de S3...{Colors.ENDC}")
    
    for s3_key in s3_keys:
        try:
            s3_client.delete_object(Bucket=bucket, Key=s3_key)
            eliminados += 1
            if eliminados % 10 == 0:
                print(f"   Eliminados: {eliminados}/{len(s3_keys)}")
        except Exception as e:
            print(f"{Colors.WARNING}⚠️  Error eliminando {s3_key}: {e}{Colors.ENDC}")
            errores += 1
    
    return eliminados, errores

def main():
    """Función principal"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}ELIMINAR PAQUETES CANCELADOS{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
    
    conn = get_db_connection()
    s3_client = get_s3_client()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print(f"{Colors.OKGREEN}✅ Conectado a RDS{Colors.ENDC}")
    print(f"{Colors.OKGREEN}✅ Conectado a S3{Colors.ENDC}\n")
    
    # Verificar paquetes cancelados
    print(f"{Colors.BOLD}📊 VERIFICANDO PAQUETES CANCELADOS{Colors.ENDC}\n")
    
    cursor.execute("""
        SELECT COUNT(*) as total FROM packages WHERE status = 'CANCELADO'
    """)
    total_cancelados = cursor.fetchone()['total']
    
    if total_cancelados == 0:
        print(f"{Colors.OKGREEN}✅ No hay paquetes cancelados para eliminar{Colors.ENDC}\n")
        cursor.close()
        conn.close()
        return
    
    # Mostrar algunos ejemplos
    cursor.execute("""
        SELECT tracking_number, guide_number, cancelled_at,
               (SELECT full_name FROM customers WHERE id = packages.customer_id) as customer_name
        FROM packages 
        WHERE status = 'CANCELADO'
        ORDER BY cancelled_at DESC
        LIMIT 10
    """)
    
    ejemplos = cursor.fetchall()
    
    print(f"{Colors.WARNING}⚠️  Encontrados {total_cancelados} paquetes cancelados{Colors.ENDC}\n")
    print(f"Ejemplos (últimos 10):\n")
    
    for pkg in ejemplos:
        print(f"  📦 {pkg['tracking_number']} | Guía: {pkg['guide_number']}")
        print(f"     Cliente: {pkg['customer_name'] or 'N/A'}")
        print(f"     Cancelado: {pkg['cancelled_at']}")
        print()
    
    # Contar datos relacionados
    cursor.execute("""
        SELECT COUNT(*) as total FROM package_events 
        WHERE package_id IN (SELECT id FROM packages WHERE status = 'CANCELADO')
    """)
    eventos = cursor.fetchone()['total']
    
    cursor.execute("""
        SELECT COUNT(*) as total FROM package_history 
        WHERE package_id IN (SELECT id FROM packages WHERE status = 'CANCELADO')
    """)
    historial = cursor.fetchone()['total']
    
    cursor.execute("""
        SELECT COUNT(*) as total FROM file_uploads 
        WHERE package_id IN (SELECT id FROM packages WHERE status = 'CANCELADO')
    """)
    archivos = cursor.fetchone()['total']
    
    cursor.execute("""
        SELECT COUNT(*) as total FROM notifications 
        WHERE package_id IN (SELECT id FROM packages WHERE status = 'CANCELADO')
    """)
    notificaciones = cursor.fetchone()['total']
    
    cursor.execute("""
        SELECT COUNT(*) as total FROM messages 
        WHERE package_id IN (SELECT id FROM packages WHERE status = 'CANCELADO')
    """)
    mensajes = cursor.fetchone()['total']
    
    print(f"{Colors.OKCYAN}Datos relacionados a eliminar:{Colors.ENDC}")
    print(f"  - Eventos: {eventos}")
    print(f"  - Historial: {historial}")
    print(f"  - Archivos: {archivos}")
    print(f"  - Notificaciones: {notificaciones}")
    print(f"  - Mensajes: {mensajes}")
    
    # Confirmar
    print(f"\n{Colors.WARNING}{Colors.BOLD}⚠️  ADVERTENCIA: Esta operación NO se puede deshacer{Colors.ENDC}")
    print(f"{Colors.WARNING}Se creará un backup antes de eliminar{Colors.ENDC}\n")
    
    respuesta = input(f"{Colors.BOLD}¿Deseas continuar? (escribe 'SI' para confirmar): {Colors.ENDC}")
    
    if respuesta.strip().upper() != 'SI':
        print(f"\n{Colors.WARNING}❌ Operación cancelada{Colors.ENDC}")
        cursor.close()
        conn.close()
        return
    
    # Crear backup
    backup_file = crear_backup(conn)
    
    # Ejecutar eliminación
    try:
        print(f"\n{Colors.BOLD}🚀 INICIANDO ELIMINACIÓN{Colors.ENDC}\n")
        
        stats = {}
        
        # Obtener IDs de paquetes cancelados
        cursor.execute("""
            SELECT id FROM packages WHERE status = 'CANCELADO'
        """)
        package_ids = [row['id'] for row in cursor.fetchall()]
        
        # Eliminar archivos S3
        if package_ids:
            s3_keys = obtener_archivos_s3(conn, package_ids)
            eliminados_s3, errores_s3 = eliminar_archivos_s3(s3_client, s3_keys)
            stats['archivos_s3'] = eliminados_s3
            stats['errores_s3'] = errores_s3
        
        # 1. Eliminar eventos
        print(f"{Colors.OKCYAN}1/7 Eliminando eventos...{Colors.ENDC}")
        cursor.execute("""
            DELETE FROM package_events 
            WHERE package_id IN (SELECT id FROM packages WHERE status = 'CANCELADO')
        """)
        stats['eventos'] = cursor.rowcount
        
        # 2. Eliminar historial
        print(f"{Colors.OKCYAN}2/7 Eliminando historial...{Colors.ENDC}")
        cursor.execute("""
            DELETE FROM package_history 
            WHERE package_id IN (SELECT id FROM packages WHERE status = 'CANCELADO')
        """)
        stats['historial'] = cursor.rowcount
        
        # 3. Eliminar archivos (registros BD)
        print(f"{Colors.OKCYAN}3/7 Eliminando registros de archivos...{Colors.ENDC}")
        cursor.execute("""
            DELETE FROM file_uploads 
            WHERE package_id IN (SELECT id FROM packages WHERE status = 'CANCELADO')
        """)
        stats['file_uploads'] = cursor.rowcount
        
        # 4. Eliminar notificaciones
        print(f"{Colors.OKCYAN}4/7 Eliminando notificaciones...{Colors.ENDC}")
        cursor.execute("""
            DELETE FROM notifications 
            WHERE package_id IN (SELECT id FROM packages WHERE status = 'CANCELADO')
        """)
        stats['notifications'] = cursor.rowcount
        
        # 5. Eliminar mensajes
        print(f"{Colors.OKCYAN}5/7 Eliminando mensajes...{Colors.ENDC}")
        cursor.execute("""
            DELETE FROM messages 
            WHERE package_id IN (SELECT id FROM packages WHERE status = 'CANCELADO')
        """)
        stats['messages'] = cursor.rowcount
        
        # 6. Desvincular anuncios
        print(f"{Colors.OKCYAN}6/7 Desvinculando anuncios...{Colors.ENDC}")
        cursor.execute("""
            UPDATE package_announcements_new 
            SET package_id = NULL 
            WHERE package_id IN (SELECT id FROM packages WHERE status = 'CANCELADO')
        """)
        stats['announcements_updated'] = cursor.rowcount
        
        # 7. Eliminar paquetes
        print(f"{Colors.OKCYAN}7/7 Eliminando paquetes cancelados...{Colors.ENDC}")
        cursor.execute("""
            DELETE FROM packages WHERE status = 'CANCELADO'
        """)
        stats['packages'] = cursor.rowcount
        
        # Commit
        conn.commit()
        
        # Reporte
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{Colors.BOLD}✅ ELIMINACIÓN COMPLETADA EXITOSAMENTE{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
        
        print(f"{Colors.BOLD}📊 RESUMEN:{Colors.ENDC}\n")
        for key, value in stats.items():
            print(f"  - {key}: {value}")
        
        print(f"\n{Colors.OKGREEN}✅ Backup guardado en: {backup_file}{Colors.ENDC}")
        
    except Exception as e:
        conn.rollback()
        print(f"\n{Colors.FAIL}{Colors.BOLD}❌ ERROR: {e}{Colors.ENDC}")
        print(f"{Colors.FAIL}Se hizo rollback. No se eliminó nada.{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Backup disponible en: {backup_file}{Colors.ENDC}")
    
    finally:
        cursor.close()
        conn.close()
        print(f"\n{Colors.OKCYAN}Conexión cerrada{Colors.ENDC}\n")

if __name__ == "__main__":
    main()
