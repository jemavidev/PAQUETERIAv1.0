#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para sincronizar productos inicialmente desde DynamiaERP
Ejecutar como administrador
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.product_sync_service import ProductSyncService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def sync_products():
    """Sincronizar productos desde DynamiaERP"""
    db = SessionLocal()
    try:
        logger.info("🔄 Iniciando sincronización de productos desde DynamiaERP...")
        
        sync_service = ProductSyncService(db)
        
        # Sincronizar solo productos activos y vendibles
        filters = {
            'activo': True,
            'vendible': True
        }
        
        result = sync_service.sync_products(filters=filters)
        
        if result['success']:
            logger.info(f"✅ Sincronización completada exitosamente:")
            logger.info(f"   - Nuevos: {result['new']}")
            logger.info(f"   - Actualizados: {result['updated']}")
            logger.info(f"   - Errores: {result['errors']}")
            logger.info(f"   - Total procesados: {result['total']}")
        else:
            logger.error(f"❌ Error en la sincronización: {result.get('message', 'Error desconocido')}")
            
    except Exception as e:
        logger.error(f"❌ Error ejecutando sincronización: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    sync_products()
