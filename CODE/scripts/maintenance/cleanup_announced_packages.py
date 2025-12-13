#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Script de Limpieza de Paquetes ANUNCIADOS
Versión: 1.0.0
Fecha: 2025-12-13
Autor: Equipo de Desarrollo

Este script elimina paquetes con estado ANUNCIADO que tengan más de X días
sin cambiar de estado (por defecto 15 días).
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir / "src"))

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.package import Package, PackageStatus
from app.utils.datetime_utils import get_colombia_now
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def cleanup_old_announced_packages(days_old: int = 15, dry_run: bool = False):
    """
    Eliminar paquetes con estado ANUNCIADO que tengan más de X días sin cambiar de estado.
    
    Args:
        days_old: Número de días para considerar un paquete como antiguo (default: 15)
        dry_run: Si es True, solo muestra qué se eliminaría sin hacer cambios (default: False)
    
    Returns:
        dict: Resultado de la operación con conteo y detalles
    """
    logger.info(f"{'[DRY RUN] ' if dry_run else ''}🧹 Iniciando limpieza de paquetes ANUNCIADOS con más de {days_old} días")
    
    db = SessionLocal()
    try:
        # Calcular fecha límite
        cutoff_date = get_colombia_now() - timedelta(days=days_old)
        logger.info(f"📅 Fecha límite: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Buscar paquetes ANUNCIADOS antiguos (basado en updated_at)
        old_announced_packages = db.query(Package).filter(
            Package.status == PackageStatus.ANUNCIADO,
            Package.updated_at < cutoff_date
        ).all()
        
        logger.info(f"📦 Paquetes encontrados: {len(old_announced_packages)}")
        
        if not old_announced_packages:
            logger.info("✅ No hay paquetes ANUNCIADOS antiguos para eliminar")
            return {
                "deleted_count": 0,
                "deleted_tracking_numbers": [],
                "cutoff_date": cutoff_date.isoformat(),
                "days_old": days_old,
                "dry_run": dry_run
            }
        
        deleted_count = 0
        deleted_tracking_numbers = []
        
        # Mostrar detalles de los paquetes a eliminar
        logger.info("\n" + "="*80)
        logger.info("PAQUETES A ELIMINAR:")
        logger.info("="*80)
        
        for package in old_announced_packages:
            days_since_update = (get_colombia_now() - package.updated_at).days
            logger.info(
                f"  • Tracking: {package.tracking_number} | "
                f"Cliente: {package.customer.full_name if package.customer else 'N/A'} | "
                f"Última actualización: {package.updated_at.strftime('%Y-%m-%d')} "
                f"({days_since_update} días atrás)"
            )
        
        logger.info("="*80 + "\n")
        
        if dry_run:
            logger.info("🔍 [DRY RUN] No se realizarán cambios en la base de datos")
            return {
                "deleted_count": len(old_announced_packages),
                "deleted_tracking_numbers": [p.tracking_number for p in old_announced_packages],
                "cutoff_date": cutoff_date.isoformat(),
                "days_old": days_old,
                "dry_run": True
            }
        
        # Confirmar antes de eliminar
        print("\n⚠️  ¿Deseas continuar con la eliminación? (s/n): ", end="")
        confirmation = input().strip().lower()
        
        if confirmation not in ['s', 'si', 'sí', 'y', 'yes']:
            logger.info("❌ Operación cancelada por el usuario")
            return {
                "deleted_count": 0,
                "deleted_tracking_numbers": [],
                "cutoff_date": cutoff_date.isoformat(),
                "days_old": days_old,
                "cancelled": True
            }
        
        # Proceder con la eliminación
        for package in old_announced_packages:
            try:
                tracking_number = package.tracking_number
                logger.info(f"🗑️  Eliminando paquete: {tracking_number}")
                
                # Eliminar el paquete (las relaciones en cascada se encargarán del resto)
                db.delete(package)
                deleted_count += 1
                deleted_tracking_numbers.append(tracking_number)
                
            except Exception as e:
                logger.error(f"❌ Error eliminando paquete {package.tracking_number}: {str(e)}")
                continue
        
        # Commit de todos los cambios
        db.commit()
        
        result = {
            "deleted_count": deleted_count,
            "deleted_tracking_numbers": deleted_tracking_numbers,
            "cutoff_date": cutoff_date.isoformat(),
            "days_old": days_old,
            "dry_run": False
        }
        
        logger.info(f"\n✅ Limpieza completada: {deleted_count} paquetes ANUNCIADOS eliminados")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error en limpieza de paquetes ANUNCIADOS: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Eliminar paquetes ANUNCIADOS antiguos"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=15,
        help="Número de días para considerar un paquete como antiguo (default: 15)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ejecutar en modo prueba sin hacer cambios"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("🧹 LIMPIEZA DE PAQUETES ANUNCIADOS")
    print("="*80)
    print(f"Días de antigüedad: {args.days}")
    print(f"Modo: {'DRY RUN (sin cambios)' if args.dry_run else 'PRODUCCIÓN (eliminará paquetes)'}")
    print("="*80 + "\n")
    
    try:
        result = cleanup_old_announced_packages(
            days_old=args.days,
            dry_run=args.dry_run
        )
        
        print("\n" + "="*80)
        print("📊 RESUMEN")
        print("="*80)
        print(f"Paquetes eliminados: {result['deleted_count']}")
        print(f"Fecha límite: {result['cutoff_date']}")
        print(f"Días de antigüedad: {result['days_old']}")
        if result.get('cancelled'):
            print("Estado: CANCELADO")
        elif result['dry_run']:
            print("Estado: DRY RUN (sin cambios)")
        else:
            print("Estado: COMPLETADO")
        print("="*80 + "\n")
        
        if result['deleted_tracking_numbers']:
            print("Tracking numbers eliminados:")
            for tn in result['deleted_tracking_numbers']:
                print(f"  • {tn}")
            print()
        
    except Exception as e:
        logger.error(f"Error ejecutando limpieza: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
