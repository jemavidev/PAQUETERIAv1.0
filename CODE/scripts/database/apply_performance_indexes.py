#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para aplicar índices de rendimiento a la base de datos
Ejecutar: python apply_performance_indexes.py
"""

import os
import sys

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from sqlalchemy import text
from app.database import SessionLocal, engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lista de índices a crear
INDEXES = [
    # Packages
    ("idx_packages_customer_id", "packages", "customer_id"),
    ("idx_packages_status", "packages", "status"),
    ("idx_packages_created_at", "packages", "created_at DESC"),
    ("idx_packages_updated_at", "packages", "updated_at DESC"),
    ("idx_packages_tracking_number", "packages", "tracking_number"),
    ("idx_packages_guide_number", "packages", "guide_number"),
    
    # Customers
    ("idx_customers_phone", "customers", "phone"),
    ("idx_customers_full_name", "customers", "full_name"),
    ("idx_customers_is_active", "customers", "is_active"),
    
    # Messages
    ("idx_messages_package_id", "messages", "package_id"),
    ("idx_messages_customer_id", "messages", "customer_id"),
    ("idx_messages_status", "messages", "status"),
    ("idx_messages_created_at", "messages", "created_at DESC"),
    
    # Notifications
    ("idx_notifications_package_id", "notifications", "package_id"),
    ("idx_notifications_customer_id", "notifications", "customer_id"),
    ("idx_notifications_is_read", "notifications", "is_read"),
    
    # Package History
    ("idx_package_history_package_id", "package_history", "package_id"),
    ("idx_package_history_changed_at", "package_history", "changed_at DESC"),
    
    # Announcements
    ("idx_announcements_customer_id", "package_announcements_new", "customer_id"),
    ("idx_announcements_is_processed", "package_announcements_new", "is_processed"),
    ("idx_announcements_tracking_code", "package_announcements_new", "tracking_code"),
    ("idx_announcements_is_active", "package_announcements_new", "is_active"),
]

def create_index_safe(db, index_name: str, table: str, columns: str):
    """Crear índice de forma segura (si no existe)"""
    try:
        # Verificar si el índice ya existe
        check_query = text("""
            SELECT 1 FROM pg_indexes 
            WHERE indexname = :index_name
        """)
        result = db.execute(check_query, {"index_name": index_name}).fetchone()
        
        if result:
            logger.info(f"  ⏭️  Índice {index_name} ya existe")
            return False
        
        # Crear el índice
        create_query = text(f"""
            CREATE INDEX {index_name} ON {table}({columns})
        """)
        db.execute(create_query)
        db.commit()
        logger.info(f"  ✅ Índice {index_name} creado")
        return True
        
    except Exception as e:
        logger.warning(f"  ⚠️  Error creando {index_name}: {str(e)}")
        db.rollback()
        return False

def main():
    logger.info("=" * 50)
    logger.info("🚀 Aplicando índices de rendimiento")
    logger.info("=" * 50)
    
    db = SessionLocal()
    created = 0
    skipped = 0
    errors = 0
    
    try:
        for index_name, table, columns in INDEXES:
            if create_index_safe(db, index_name, table, columns):
                created += 1
            else:
                skipped += 1
        
        # Actualizar estadísticas
        logger.info("\n📊 Actualizando estadísticas...")
        tables = ["packages", "customers", "messages", "notifications", "package_history", "package_announcements_new"]
        for table in tables:
            try:
                db.execute(text(f"ANALYZE {table}"))
                db.commit()
                logger.info(f"  ✅ ANALYZE {table}")
            except Exception as e:
                logger.warning(f"  ⚠️  Error en ANALYZE {table}: {str(e)}")
                db.rollback()
        
        logger.info("\n" + "=" * 50)
        logger.info(f"✅ Índices creados: {created}")
        logger.info(f"⏭️  Índices existentes: {skipped}")
        logger.info("=" * 50)
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
