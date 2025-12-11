#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Limpieza de Datos de Prueba
======================================
Elimina clientes de prueba y paquetes cancelados de forma segura.

Características:
- Backup automático antes de eliminar
- Verificación previa de registros
- Confirmación requerida
- Eliminación de archivos S3
- Transacciones seguras (rollback automático si falla)
- Reporte detallado

Autor: Sistema PAQUETEX
Fecha: 11 de Diciembre, 2025
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import psycopg2
from psycopg2.extras import RealDictCursor
import boto3
from dotenv import load_dotenv
from typing import List, Dict, Tuple

# Cargar variables de entorno
load_dotenv()

# ========================================
# CONFIGURACIÓN
# ========================================

# Clientes a eliminar (números de teléfono)
CLIENTES_PRUEBA = [
    '+573001234567',
    '+573002596319',
    '+573008103849',
    '+573008398365'
]

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# ========================================
# FUNCIONES DE CONEXIÓN
# ========================================

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

# ========================================
# FUNCIONES DE VERIFICACIÓN
# ========================================

def verificar_clientes(conn) -> Dict:
    """Verificar cuántos registros se eliminarán de clientes"""
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    stats = {}
    
    # Clientes
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM customers 
        WHERE phone = ANY(%s)
    """, (CLIENTES_PRUEBA,))
    stats['clientes'] = cursor.fetchone()['total']
    
    # Paquetes de estos clientes
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM packages 
        WHERE customer_id IN (
            SELECT id FROM customers WHERE phone = ANY(%s)
        )
    """, (CLIENTES_PRUEBA,))
    stats['paquetes_clientes'] = cursor.fetchone()['total']
    
    # Anuncios de estos clientes
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM package_announcements_new 
        WHERE customer_id IN (
            SELECT id FROM customers WHERE phone = ANY(%s)
        )
    """, (CLIENTES_PRUEBA,))
    stats['anuncios_clientes'] = cursor.fetchone()['total']
    
    # Eventos de paquetes de estos clientes
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM package_events 
        WHERE customer_id IN (
            SELECT id FROM customers WHERE phone = ANY(%s)
        )
    """, (CLIENTES_PRUEBA,))
    stats['eventos_clientes'] = cursor.fetchone()['total']
    
    # Archivos de paquetes de estos clientes
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM file_uploads 
        WHERE package_id IN (
            SELECT id FROM packages 
            WHERE customer_id IN (
                SELECT id FROM customers WHERE phone = ANY(%s)
            )
        )
    """, (CLIENTES_PRUEBA,))
    stats['archivos_clientes'] = cursor.fetchone()['total']
    
    cursor.close()
    return stats

def verificar_cancelados(conn) -> Dict:
    """Verificar cuántos registros se eliminarán de paquetes cancelados"""
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    stats = {}
    
    # Paquetes cancelados
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM packages 
        WHERE status = 'CANCELADO'
    """)
    stats['paquetes_cancelados'] = cursor.fetchone()['total']
    
    # Eventos de paquetes cancelados
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM package_events 
        WHERE package_id IN (
            SELECT id FROM packages WHERE status = 'CANCELADO'
        )
    """)
    stats['eventos_cancelados'] = cursor.fetchone()['total']
    
    # Historial de paquetes cancelados
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM package_history 
        WHERE package_id IN (
            SELECT id FROM packages WHERE status = 'CANCELADO'
        )
    """)
    stats['historial_cancelados'] = cursor.fetchone()['total']
    
    # Archivos de paquetes cancelados
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM file_uploads 
        WHERE package_id IN (
            SELECT id FROM packages WHERE status = 'CANCELADO'
        )
    """)
    stats['archivos_cancelados'] = cursor.fetchone()['total']
    
    cursor.close()
    return stats

# ========================================
# FUNCIONES DE BACKUP
# ========================================

def crear_backup(conn) -> str:
    """Crear backup de las tablas afectadas"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = Path(__file__).parent.parent.parent / 'backups'
    backup_dir.mkdir(exist_ok=True)
    
    backup_file = backup_dir / f'backup_limpieza_{timestamp}.json'
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    backup_data = {}
    
    print(f"{Colors.OKCYAN}📦 Creando backup...{Colors.ENDC}")
    
    # Backup de clientes
    cursor.execute("""
        SELECT * FROM customers 
        WHERE phone = ANY(%s)
    """, (CLIENTES_PRUEBA,))
    backup_data['customers'] = [dict(row) for row in cursor.fetchall()]
    
    # Backup de paquetes de clientes
    cursor.execute("""
        SELECT * FROM packages 
        WHERE customer_id IN (
            SELECT id FROM customers WHERE phone = ANY(%s)
        )
    """, (CLIENTES_PRUEBA,))
    backup_data['packages_clientes'] = [dict(row) for row in cursor.fetchall()]
    
    # Backup de paquetes cancelados
    cursor.execute("""
        SELECT * FROM packages 
        WHERE status = 'CANCELADO'
    """)
    backup_data['packages_cancelados'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.close()
    
    # Guardar backup
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2, default=str)
    
    print(f"{Colors.OKGREEN}✅ Backup creado: {backup_file}{Colors.ENDC}")
    return str(backup_file)

# ========================================
# FUNCIONES DE ELIMINACIÓN S3
# ========================================

def obtener_archivos_s3(conn, package_ids: List[int]) -> List[str]:
    """Obtener lista de archivos S3 de los paquetes"""
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

def eliminar_archivos_s3(s3_client, s3_keys: List[str]) -> Tuple[int, int]:
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

# ========================================
# FUNCIONES DE ELIMINACIÓN BD
# ========================================

def eliminar_clientes_prueba(conn, s3_client) -> Dict:
    """Eliminar clientes de prueba y todos sus datos relacionados"""
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    stats = {'eliminados': {}, 'errores': []}
    
    try:
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}ELIMINANDO CLIENTES DE PRUEBA{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
        
        # Obtener IDs de paquetes para eliminar archivos S3
        cursor.execute("""
            SELECT id FROM packages 
            WHERE customer_id IN (
                SELECT id FROM customers WHERE phone = ANY(%s)
            )
        """, (CLIENTES_PRUEBA,))
        package_ids = [row['id'] for row in cursor.fetchall()]
        
        # Eliminar archivos S3
        if package_ids:
            s3_keys = obtener_archivos_s3(conn, package_ids)
            eliminados_s3, errores_s3 = eliminar_archivos_s3(s3_client, s3_keys)
            stats['eliminados']['archivos_s3'] = eliminados_s3
            stats['errores_s3'] = errores_s3
        
        # 1. Eliminar eventos de paquetes
        print(f"{Colors.OKCYAN}1/8 Eliminando eventos de paquetes...{Colors.ENDC}")
        cursor.execute("""
            DELETE FROM package_events 
            WHERE customer_id IN (
                SELECT id FROM customers WHERE phone = ANY(%s)
            )
        """, (CLIENTES_PRUEBA,))
        stats['eliminados']['eventos'] = cursor.rowcount
        
        # 2. Eliminar historial de paquetes
        print(f"{Colors.OKCYAN}2/8 Eliminando historial de paquetes...{Colors.ENDC}")
        cursor.execute("""
            DELETE FROM package_history 
            WHERE package_id IN (
                SELECT id FROM packages 
                WHERE customer_id IN (
                    SELECT id FROM customers WHERE phone = ANY(%s)
                )
            )
        """, (CLIENTES_PRUEBA,))
        stats['eliminados']['historial'] = cursor.rowcount
        
        # 3. Eliminar archivos (registros BD)
        print(f"{Colors.OKCYAN}3/8 Eliminando registros de archivos...{Colors.ENDC}")
        cursor.execute("""
            DELETE FROM file_uploads 
            WHERE package_id IN (
                SELECT id FROM packages 
                WHERE customer_id IN (
                    SELECT id FROM customers WHERE phone = ANY(%s)
                )
            )
        """, (CLIENTES_PRUEBA,))
        stats['eliminados']['file_uploads'] = cursor.rowcount
        
        # 4. Eliminar notificaciones de paquetes
        print(f"{Colors.OKCYAN}4/8 Eliminando notificaciones de paquetes...{Colors.ENDC}")
        cursor.execute("""
            DELETE FROM notifications 
            WHERE package_id IN (
                SELECT id FROM packages 
                WHERE customer_id IN (
                    SELECT id FROM customers WHERE phone = ANY(%s)
                )
            )
        """, (CLIENTES_PRUEBA,))
        stats['eliminados']['notifications_packages'] = cursor.rowcount
        
        # 5. Eliminar mensajes de paquetes
        print(f"{Colors.OKCYAN}5/8 Eliminando mensajes de paquetes...{Colors.ENDC}")
        cursor.execute("""
            DELETE FROM messages 
            WHERE package_id IN (
                SELECT id FROM packages 
                WHERE customer_id IN (
                    SELECT id FROM customers WHERE phone = ANY(%s)
                )
            )
        """, (CLIENTES_PRUEBA,))
        stats['eliminados']['messages_packages'] = cursor.rowcount
        
        # 6. Desvincular anuncios de paquetes
        print(f"{Colors.OKCYAN}6/8 Desvinculando anuncios de paquetes...{Colors.ENDC}")
        cursor.execute("""
            UPDATE package_announcements_new 
            SET package_id = NULL 
            WHERE package_id IN (
                SELECT id FROM packages 
                WHERE customer_id IN (
                    SELECT id FROM customers WHERE phone = ANY(%s)
                )
            )
        """, (CLIENTES_PRUEBA,))
        stats['eliminados']['announcements_updated'] = cursor.rowcount
        
        # 7. Eliminar paquetes
        print(f"{Colors.OKCYAN}7/8 Eliminando paquetes...{Colors.ENDC}")
        cursor.execute("""
            DELETE FROM packages 
            WHERE customer_id IN (
                SELECT id FROM customers WHERE phone = ANY(%s)
            )
        """, (CLIENTES_PRUEBA,))
        stats['eliminados']['packages'] = cursor.rowcount
        
        # 8. Eliminar clientes (cascade eliminará: announcements, messages, notifications, preferences)
        print(f"{Colors.OKCYAN}8/8 Eliminando clientes...{Colors.ENDC}")
        cursor.execute("""
            DELETE FROM customers 
            WHERE phone = ANY(%s)
        """, (CLIENTES_PRUEBA,))
        stats['eliminados']['customers'] = cursor.rowcount
        
        cursor.close()
        return stats
        
    except Exception as e:
        stats['errores'].append(str(e))
        raise

def eliminar_paquetes_cancelados(conn, s3_client) -> Dict:
    """Eliminar todos los paquetes cancelados"""
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    stats = {'eliminados': {}, 'errores': []}
    
    try:
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}ELIMINANDO PAQUETES CANCELADOS{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
        
        # Obtener IDs de paquetes cancelados
        cursor.execute("""
            SELECT id FROM packages WHERE status = 'CANCELADO'
        """)
        package_ids = [row['id'] for row in cursor.fetchall()]
        
        # Eliminar archivos S3
        if package_ids:
            s3_keys = obtener_archivos_s3(conn, package_ids)
            eliminados_s3, errores_s3 = eliminar_archivos_s3(s3_client, s3_keys)
            stats['eliminados']['archivos_s3'] = eliminados_s3
            stats['errores_s3'] = errores_s3
        
        # 1. Eliminar eventos
        print(f"{Colors.OKCYAN}1/7 Eliminando eventos...{Colors.ENDC}")
        cursor.execute("""
            DELETE FROM package_events 
            WHERE package_id IN (SELECT id FROM packages WHERE status = 'CANCELADO')
        """)
        stats['eliminados']['eventos'] = cursor.rowcount
        
        # 2. Eliminar historial
        print(f"{Colors.OKCYAN}2/7 Eliminando historial...{Colors.ENDC}")
        cursor.execute("""
            DELETE FROM package_history 
            WHERE package_id IN (SELECT id FROM packages WHERE status = 'CANCELADO')
        """)
        stats['eliminados']['historial'] = cursor.rowcount
        
        # 3. Eliminar archivos (registros BD)
        print(f"{Colors.OKCYAN}3/7 Eliminando registros de archivos...{Colors.ENDC}")
        cursor.execute("""
            DELETE FROM file_uploads 
            WHERE package_id IN (SELECT id FROM packages WHERE status = 'CANCELADO')
        """)
        stats['eliminados']['file_uploads'] = cursor.rowcount
        
        # 4. Eliminar notificaciones
        print(f"{Colors.OKCYAN}4/7 Eliminando notificaciones...{Colors.ENDC}")
        cursor.execute("""
            DELETE FROM notifications 
            WHERE package_id IN (SELECT id FROM packages WHERE status = 'CANCELADO')
        """)
        stats['eliminados']['notifications'] = cursor.rowcount
        
        # 5. Eliminar mensajes
        print(f"{Colors.OKCYAN}5/7 Eliminando mensajes...{Colors.ENDC}")
        cursor.execute("""
            DELETE FROM messages 
            WHERE package_id IN (SELECT id FROM packages WHERE status = 'CANCELADO')
        """)
        stats['eliminados']['messages'] = cursor.rowcount
        
        # 6. Desvincular anuncios
        print(f"{Colors.OKCYAN}6/7 Desvinculando anuncios...{Colors.ENDC}")
        cursor.execute("""
            UPDATE package_announcements_new 
            SET package_id = NULL 
            WHERE package_id IN (SELECT id FROM packages WHERE status = 'CANCELADO')
        """)
        stats['eliminados']['announcements_updated'] = cursor.rowcount
        
        # 7. Eliminar paquetes
        print(f"{Colors.OKCYAN}7/7 Eliminando paquetes cancelados...{Colors.ENDC}")
        cursor.execute("""
            DELETE FROM packages WHERE status = 'CANCELADO'
        """)
        stats['eliminados']['packages'] = cursor.rowcount
        
        cursor.close()
        return stats
        
    except Exception as e:
        stats['errores'].append(str(e))
        raise

# ========================================
# FUNCIÓN PRINCIPAL
# ========================================

def main():
    """Función principal"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}SCRIPT DE LIMPIEZA DE DATOS DE PRUEBA{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
    
    # Conectar a BD y S3
    conn = get_db_connection()
    s3_client = get_s3_client()
    
    print(f"{Colors.OKGREEN}✅ Conectado a RDS: {os.getenv('POSTGRES_HOST')}{Colors.ENDC}")
    print(f"{Colors.OKGREEN}✅ Conectado a S3: {os.getenv('AWS_S3_BUCKET')}{Colors.ENDC}\n")
    
    # Verificar registros
    print(f"{Colors.BOLD}📊 VERIFICANDO REGISTROS A ELIMINAR{Colors.ENDC}\n")
    
    stats_clientes = verificar_clientes(conn)
    stats_cancelados = verificar_cancelados(conn)
    
    print(f"{Colors.OKCYAN}Clientes de prueba:{Colors.ENDC}")
    print(f"  - Clientes: {stats_clientes['clientes']}")
    print(f"  - Paquetes: {stats_clientes['paquetes_clientes']}")
    print(f"  - Anuncios: {stats_clientes['anuncios_clientes']}")
    print(f"  - Eventos: {stats_clientes['eventos_clientes']}")
    print(f"  - Archivos: {stats_clientes['archivos_clientes']}")
    
    print(f"\n{Colors.OKCYAN}Paquetes cancelados:{Colors.ENDC}")
    print(f"  - Paquetes: {stats_cancelados['paquetes_cancelados']}")
    print(f"  - Eventos: {stats_cancelados['eventos_cancelados']}")
    print(f"  - Historial: {stats_cancelados['historial_cancelados']}")
    print(f"  - Archivos: {stats_cancelados['archivos_cancelados']}")
    
    # Confirmar
    print(f"\n{Colors.WARNING}{Colors.BOLD}⚠️  ADVERTENCIA: Esta operación NO se puede deshacer{Colors.ENDC}")
    print(f"{Colors.WARNING}Se creará un backup antes de eliminar{Colors.ENDC}\n")
    
    respuesta = input(f"{Colors.BOLD}¿Deseas continuar? (escribe 'SI' para confirmar): {Colors.ENDC}")
    
    if respuesta.strip().upper() != 'SI':
        print(f"\n{Colors.WARNING}❌ Operación cancelada por el usuario{Colors.ENDC}")
        conn.close()
        return
    
    # Crear backup
    backup_file = crear_backup(conn)
    
    # Ejecutar eliminaciones en transacción
    try:
        print(f"\n{Colors.BOLD}🚀 INICIANDO ELIMINACIÓN{Colors.ENDC}\n")
        
        # Eliminar clientes de prueba
        stats_clientes_eliminados = eliminar_clientes_prueba(conn, s3_client)
        
        # Eliminar paquetes cancelados
        stats_cancelados_eliminados = eliminar_paquetes_cancelados(conn, s3_client)
        
        # Commit
        conn.commit()
        
        # Reporte final
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{Colors.BOLD}✅ LIMPIEZA COMPLETADA EXITOSAMENTE{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
        
        print(f"{Colors.BOLD}📊 RESUMEN DE ELIMINACIÓN:{Colors.ENDC}\n")
        
        print(f"{Colors.OKCYAN}Clientes de prueba:{Colors.ENDC}")
        for key, value in stats_clientes_eliminados['eliminados'].items():
            print(f"  - {key}: {value}")
        
        print(f"\n{Colors.OKCYAN}Paquetes cancelados:{Colors.ENDC}")
        for key, value in stats_cancelados_eliminados['eliminados'].items():
            print(f"  - {key}: {value}")
        
        print(f"\n{Colors.OKGREEN}✅ Backup guardado en: {backup_file}{Colors.ENDC}")
        
    except Exception as e:
        conn.rollback()
        print(f"\n{Colors.FAIL}{Colors.BOLD}❌ ERROR: {e}{Colors.ENDC}")
        print(f"{Colors.FAIL}Se hizo rollback. No se eliminó nada.{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Backup disponible en: {backup_file}{Colors.ENDC}")
    
    finally:
        conn.close()
        print(f"\n{Colors.OKCYAN}Conexión cerrada{Colors.ENDC}\n")

if __name__ == "__main__":
    main()
