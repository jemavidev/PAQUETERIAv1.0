#!/usr/bin/env python3
"""
Script para crear índices optimizados en la base de datos
Mejora el rendimiento de las operaciones CRUD
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy import text
from app.database_optimized import SessionLocal, engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_indexes():
    """Crear todos los índices necesarios para optimizar queries"""
    
    indexes = [
        # Índices para tabla packages (consultas más frecuentes)
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_packages_customer_id ON packages(customer_id)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_packages_status ON packages(status)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_packages_created_at ON packages(created_at DESC)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_packages_tracking_number ON packages(tracking_number)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_packages_guide_number ON packages(guide_number)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_packages_status_created ON packages(status, created_at DESC)",
        
        # Índices para tabla customers
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customers_phone ON customers(phone)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customers_full_name ON customers(full_name)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customers_created_at ON customers(created_at DESC)",
        
        # Índices para tabla messages
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_package_id ON messages(package_id)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_customer_id ON messages(customer_id)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_status ON messages(status)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_created_at ON messages(created_at DESC)",
        
        # Índices para tabla notifications
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_user_id ON notifications(user_id)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_read ON notifications(is_read)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC)",
        
        # Índices para tabla users
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users(email)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_role ON users(role)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_is_active ON users(is_active)",
        
        # Índices para tabla file_uploads
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_file_uploads_package_id ON file_uploads(package_id)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_file_uploads_created_at ON file_uploads(created_at DESC)",
        
        # Índices compuestos para búsquedas complejas
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_packages_customer_status ON packages(customer_id, status)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_package_status ON messages(package_id, status)",
    ]
    
    db = SessionLocal()
    
    try:
        logger.info("🔧 Iniciando creación de índices...")
        logger.info(f"📊 Total de índices a crear: {len(indexes)}")
        
        created = 0
        skipped = 0
        errors = 0
        
        for idx_sql in indexes:
            try:
                # Extraer nombre del índice para logging
                idx_name = idx_sql.split("IF NOT EXISTS ")[1].split(" ON ")[0]
                
                logger.info(f"  Creando: {idx_name}...")
                
                # Ejecutar sin CONCURRENTLY primero para verificar si existe
                check_sql = idx_sql.replace("CONCURRENTLY ", "")
                db.execute(text(check_sql))
                db.commit()
                
                created += 1
                logger.info(f"  ✅ {idx_name} creado")
                
            except Exception as e:
                error_msg = str(e)
                if "already exists" in error_msg:
                    skipped += 1
                    logger.info(f"  ⏭️  {idx_name} ya existe")
                else:
                    errors += 1
                    logger.error(f"  ❌ Error en {idx_name}: {error_msg}")
                db.rollback()
        
        # Optimizar tablas después de crear índices
        logger.info("\n🔧 Optimizando tablas...")
        
        optimize_queries = [
            "ALTER TABLE packages SET (autovacuum_vacuum_scale_factor = 0.05)",
            "ALTER TABLE customers SET (autovacuum_vacuum_scale_factor = 0.05)",
            "ALTER TABLE messages SET (autovacuum_vacuum_scale_factor = 0.1)",
            "ANALYZE packages",
            "ANALYZE customers",
            "ANALYZE messages",
            "ANALYZE notifications",
            "ANALYZE users",
        ]
        
        for query in optimize_queries:
            try:
                db.execute(text(query))
                db.commit()
                logger.info(f"  ✅ {query.split()[0]} {query.split()[1] if len(query.split()) > 1 else ''}")
            except Exception as e:
                logger.warning(f"  ⚠️  {query}: {e}")
                db.rollback()
        
        # Resumen
        logger.info("\n" + "="*60)
        logger.info("📊 RESUMEN DE CREACIÓN DE ÍNDICES")
        logger.info("="*60)
        logger.info(f"✅ Índices creados: {created}")
        logger.info(f"⏭️  Índices existentes: {skipped}")
        logger.info(f"❌ Errores: {errors}")
        logger.info(f"📈 Total procesados: {len(indexes)}")
        logger.info("="*60)
        
        if errors == 0:
            logger.info("✅ Proceso completado exitosamente")
            return True
        else:
            logger.warning("⚠️  Proceso completado con algunos errores")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error general: {e}")
        return False
    finally:
        db.close()


def check_indexes():
    """Verificar índices existentes"""
    db = SessionLocal()
    
    try:
        logger.info("\n📋 ÍNDICES EXISTENTES EN LA BASE DE DATOS")
        logger.info("="*60)
        
        tables = ["packages", "customers", "messages", "notifications", "users", "file_uploads"]
        
        for table in tables:
            result = db.execute(text(f"""
                SELECT indexname, indexdef 
                FROM pg_indexes 
                WHERE tablename = '{table}'
                ORDER BY indexname
            """)).fetchall()
            
            logger.info(f"\n📊 Tabla: {table}")
            logger.info(f"   Total índices: {len(result)}")
            for idx in result:
                logger.info(f"   - {idx[0]}")
        
        logger.info("\n" + "="*60)
        
    except Exception as e:
        logger.error(f"❌ Error verificando índices: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Gestión de índices de base de datos")
    parser.add_argument("--check", action="store_true", help="Solo verificar índices existentes")
    parser.add_argument("--create", action="store_true", help="Crear índices faltantes")
    
    args = parser.parse_args()
    
    if args.check:
        check_indexes()
    elif args.create:
        success = create_indexes()
        sys.exit(0 if success else 1)
    else:
        # Por defecto, verificar y crear
        check_indexes()
        print("\n")
        create_indexes()
