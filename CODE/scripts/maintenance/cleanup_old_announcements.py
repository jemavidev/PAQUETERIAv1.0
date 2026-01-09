#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para Eliminar Anuncios Antiguos (> 15 días)
==================================================
Elimina anuncios pendientes (is_processed = False) que tengan más de X días.

Uso:
    python cleanup_old_announcements.py                    # Modo interactivo (15 días)
    python cleanup_old_announcements.py --days 30          # Personalizar días
    python cleanup_old_announcements.py --dry-run          # Solo mostrar, no eliminar
    python cleanup_old_announcements.py --auto             # Sin confirmación (para cron)

Autor: Sistema PAQUETEX
Fecha: 9 de Enero, 2026
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json
import argparse

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import psycopg2
from psycopg2.extras import RealDictCursor
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
    """Obtener conexión a la base de datos"""
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


def crear_backup(conn, anuncios, backup_dir):
    """Crear backup de anuncios a eliminar"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = backup_dir / f'backup_anuncios_antiguos_{timestamp}.json'
    
    backup_data = {
        'fecha_backup': datetime.now().isoformat(),
        'total_anuncios': len(anuncios),
        'anuncios': [dict(row) for row in anuncios]
    }
    
    # Convertir UUIDs y datetimes a string
    for anuncio in backup_data['anuncios']:
        for key, value in anuncio.items():
            if isinstance(value, (datetime,)):
                anuncio[key] = value.isoformat()
            elif hasattr(value, 'hex'):  # UUID
                anuncio[key] = str(value)
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2, ensure_ascii=False)
    
    return str(backup_file)


def cleanup_old_announcements(days: int = 15, dry_run: bool = False, auto: bool = False):
    """
    Eliminar anuncios pendientes con más de X días.
    
    Args:
        days: Número de días de antigüedad (default: 15)
        dry_run: Solo mostrar, no eliminar
        auto: Ejecutar sin confirmación (para cron/automatización)
    """
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}LIMPIEZA DE ANUNCIOS ANTIGUOS (> {days} días){Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
    
    if dry_run:
        print(f"{Colors.WARNING}🔍 MODO DRY-RUN: No se eliminarán datos{Colors.ENDC}\n")
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print(f"{Colors.OKGREEN}✅ Conectado a la base de datos{Colors.ENDC}\n")
    
    # Calcular fecha límite
    cutoff_date = datetime.now() - timedelta(days=days)
    print(f"{Colors.OKCYAN}📅 Fecha límite: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}   (Anuncios anteriores a esta fecha serán eliminados){Colors.ENDC}\n")
    
    # Buscar anuncios antiguos pendientes
    cursor.execute("""
        SELECT 
            id, guide_number, tracking_code, customer_name, customer_phone,
            announced_at, is_active, is_processed, customer_id,
            created_at, updated_at
        FROM package_announcements_new 
        WHERE is_processed = false 
          AND announced_at < %s
        ORDER BY announced_at ASC
    """, (cutoff_date,))
    
    anuncios = cursor.fetchall()
    
    if not anuncios:
        print(f"{Colors.OKGREEN}✅ No hay anuncios antiguos para eliminar{Colors.ENDC}\n")
        cursor.close()
        conn.close()
        return {'deleted': 0, 'backup': None}
    
    # Mostrar estadísticas
    print(f"{Colors.WARNING}⚠️  Encontrados {len(anuncios)} anuncios antiguos:{Colors.ENDC}\n")
    
    # Agrupar por estado
    activos = [a for a in anuncios if a['is_active']]
    cancelados = [a for a in anuncios if not a['is_active']]
    
    print(f"  📊 Estadísticas:")
    print(f"     - Activos (pendientes): {len(activos)}")
    print(f"     - Cancelados: {len(cancelados)}")
    print()
    
    # Mostrar detalle de los primeros 10
    print(f"  📦 Detalle (primeros 10):")
    for anuncio in anuncios[:10]:
        dias_antiguedad = (datetime.now() - anuncio['announced_at']).days
        estado = "CANCELADO" if not anuncio['is_active'] else "PENDIENTE"
        print(f"     • {anuncio['guide_number']} | {anuncio['tracking_code']}")
        print(f"       Cliente: {anuncio['customer_name']} | {estado}")
        print(f"       Fecha: {anuncio['announced_at'].strftime('%Y-%m-%d')} ({dias_antiguedad} días)")
    
    if len(anuncios) > 10:
        print(f"     ... y {len(anuncios) - 10} más")
    print()
    
    if dry_run:
        print(f"{Colors.OKCYAN}🔍 [DRY-RUN] Se eliminarían {len(anuncios)} anuncios{Colors.ENDC}\n")
        cursor.close()
        conn.close()
        return {'deleted': 0, 'would_delete': len(anuncios), 'dry_run': True}
    
    # Confirmar eliminación (si no es modo auto)
    if not auto:
        print(f"{Colors.WARNING}{Colors.BOLD}⚠️  ADVERTENCIA:{Colors.ENDC}")
        print(f"{Colors.WARNING}   - Se eliminarán {len(anuncios)} anuncios permanentemente{Colors.ENDC}")
        print(f"{Colors.WARNING}   - Se creará un backup antes de eliminar{Colors.ENDC}")
        print(f"{Colors.WARNING}   - Los clientes NO serán eliminados{Colors.ENDC}\n")
        
        respuesta = input(f"{Colors.BOLD}¿Deseas continuar? (escribe 'SI' para confirmar): {Colors.ENDC}")
        
        if respuesta.strip().upper() != 'SI':
            print(f"\n{Colors.WARNING}❌ Operación cancelada{Colors.ENDC}\n")
            cursor.close()
            conn.close()
            return {'deleted': 0, 'cancelled': True}
    
    # Crear backup
    backup_dir = Path(__file__).parent.parent.parent / 'backups'
    backup_dir.mkdir(exist_ok=True)
    
    print(f"\n{Colors.OKCYAN}📦 Creando backup...{Colors.ENDC}")
    backup_file = crear_backup(conn, anuncios, backup_dir)
    print(f"{Colors.OKGREEN}✅ Backup creado: {backup_file}{Colors.ENDC}\n")
    
    # Ejecutar eliminación
    try:
        print(f"{Colors.OKCYAN}🗑️  Eliminando anuncios antiguos...{Colors.ENDC}")
        
        cursor.execute("""
            DELETE FROM package_announcements_new 
            WHERE is_processed = false 
              AND announced_at < %s
        """, (cutoff_date,))
        
        eliminados = cursor.rowcount
        conn.commit()
        
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{Colors.BOLD}✅ LIMPIEZA COMPLETADA{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
        
        print(f"  📊 Resumen:")
        print(f"     - Anuncios eliminados: {eliminados}")
        print(f"     - Días de antigüedad: {days}")
        print(f"     - Backup: {backup_file}")
        print()
        
        return {'deleted': eliminados, 'backup': backup_file}
        
    except Exception as e:
        conn.rollback()
        print(f"\n{Colors.FAIL}{Colors.BOLD}❌ ERROR: {e}{Colors.ENDC}")
        print(f"{Colors.FAIL}Se hizo rollback. No se eliminó nada.{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Backup disponible en: {backup_file}{Colors.ENDC}\n")
        return {'deleted': 0, 'error': str(e), 'backup': backup_file}
    
    finally:
        cursor.close()
        conn.close()


def main():
    parser = argparse.ArgumentParser(
        description='Eliminar anuncios pendientes con más de X días de antigüedad'
    )
    parser.add_argument(
        '--days', '-d',
        type=int,
        default=15,
        help='Días de antigüedad (default: 15)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Solo mostrar qué se eliminaría, sin hacer cambios'
    )
    parser.add_argument(
        '--auto',
        action='store_true',
        help='Ejecutar sin confirmación (para cron/automatización)'
    )
    
    args = parser.parse_args()
    
    result = cleanup_old_announcements(
        days=args.days,
        dry_run=args.dry_run,
        auto=args.auto
    )
    
    # Exit code para scripts
    if result.get('error'):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
