#!/usr/bin/env python3
"""
Script para aplicar índices de optimización de paginación
Sistema de Facturas V2

Mejora el performance de:
- Paginación en TAB FACTURAS
- Búsqueda y filtros
- Ordenamiento por fecha
- Consultas en TAB CUFE y PRODUCTOS

Uso:
    python apply_pagination_indexes.py
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sqlalchemy import text, create_engine
from app.database import get_db, engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def apply_indexes():
    """Aplica todos los índices de optimización"""
    
    indexes = [
        # Índices principales para paginación
        {
            "name": "idx_invoices_v2_created_at",
            "sql": "CREATE INDEX IF NOT EXISTS idx_invoices_v2_created_at ON invoices_v2(created_at DESC)",
            "description": "Ordenamiento por fecha de creación (paginación)"
        },
        {
            "name": "idx_invoices_v2_estado",
            "sql": "CREATE INDEX IF NOT EXISTS idx_invoices_v2_estado ON invoices_v2(estado)",
            "description": "Filtro por estado"
        },
        {
            "name": "idx_invoices_v2_fecha_emision",
            "sql": "CREATE INDEX IF NOT EXISTS idx_invoices_v2_fecha_emision ON invoices_v2(fecha_emision)",
            "description": "Filtro por fecha de emisión"
        },
        {
            "name": "idx_invoices_v2_proveedor_nombre",
            "sql": "CREATE INDEX IF NOT EXISTS idx_invoices_v2_proveedor_nombre ON invoices_v2(proveedor_nombre)",
            "description": "Búsqueda por proveedor"
        },
        {
            "name": "idx_invoices_v2_numero_factura",
            "sql": "CREATE INDEX IF NOT EXISTS idx_invoices_v2_numero_factura ON invoices_v2(numero_factura)",
            "description": "Búsqueda por número de factura"
        },
        
        # Índices compuestos para queries complejas
        {
            "name": "idx_invoices_v2_estado_created",
            "sql": "CREATE INDEX IF NOT EXISTS idx_invoices_v2_estado_created ON invoices_v2(estado, created_at DESC)",
            "description": "Filtro por estado + ordenamiento (query compuesta)"
        },
        {
            "name": "idx_invoices_v2_dian_validado",
            "sql": "CREATE INDEX IF NOT EXISTS idx_invoices_v2_dian_validado ON invoices_v2(dian_validado)",
            "description": "Filtro por validación DIAN (TAB CUFE)"
        },
        {
            "name": "idx_invoices_v2_proveedor_nit",
            "sql": "CREATE INDEX IF NOT EXISTS idx_invoices_v2_proveedor_nit ON invoices_v2(proveedor_nit)",
            "description": "Búsqueda por NIT de proveedor"
        },
        
        # Índices para productos
        {
            "name": "idx_invoice_products_v2_codigo",
            "sql": "CREATE INDEX IF NOT EXISTS idx_invoice_products_v2_codigo ON invoice_products_v2(codigo_producto)",
            "description": "Búsqueda por código de producto"
        },
        {
            "name": "idx_invoice_products_v2_descripcion",
            "sql": "CREATE INDEX IF NOT EXISTS idx_invoice_products_v2_descripcion ON invoice_products_v2(descripcion)",
            "description": "Búsqueda por descripción de producto"
        },
        {
            "name": "idx_invoice_products_v2_fecha",
            "sql": "CREATE INDEX IF NOT EXISTS idx_invoice_products_v2_fecha ON invoice_products_v2(fecha_compra)",
            "description": "Filtro por fecha de compra"
        },
        {
            "name": "idx_invoice_products_v2_cufe_linea",
            "sql": "CREATE INDEX IF NOT EXISTS idx_invoice_products_v2_cufe_linea ON invoice_products_v2(cufe, linea_numero)",
            "description": "Búsqueda de productos por factura"
        },
    ]
    
    logger.info("=" * 60)
    logger.info("APLICANDO ÍNDICES DE OPTIMIZACIÓN DE PAGINACIÓN")
    logger.info("=" * 60)
    
    with engine.connect() as conn:
        success_count = 0
        error_count = 0
        
        for idx in indexes:
            try:
                logger.info(f"\n📊 Creando índice: {idx['name']}")
                logger.info(f"   Descripción: {idx['description']}")
                
                conn.execute(text(idx['sql']))
                conn.commit()
                
                logger.info(f"   ✅ Índice creado exitosamente")
                success_count += 1
                
            except Exception as e:
                logger.error(f"   ❌ Error creando índice: {e}")
                error_count += 1
        
        # Analizar tablas para actualizar estadísticas
        logger.info("\n" + "=" * 60)
        logger.info("ANALIZANDO TABLAS (actualizando estadísticas del optimizador)")
        logger.info("=" * 60)
        
        try:
            logger.info("\n📈 Analizando tabla invoices_v2...")
            conn.execute(text("ANALYZE invoices_v2"))
            conn.commit()
            logger.info("   ✅ Análisis completado")
            
            logger.info("\n📈 Analizando tabla invoice_products_v2...")
            conn.execute(text("ANALYZE invoice_products_v2"))
            conn.commit()
            logger.info("   ✅ Análisis completado")
            
        except Exception as e:
            logger.error(f"   ❌ Error analizando tablas: {e}")
    
    # Resumen
    logger.info("\n" + "=" * 60)
    logger.info("RESUMEN")
    logger.info("=" * 60)
    logger.info(f"✅ Índices creados exitosamente: {success_count}")
    if error_count > 0:
        logger.info(f"❌ Errores: {error_count}")
    logger.info("\n🚀 Optimización completada!")
    logger.info("   El sistema de paginación ahora debería ser mucho más rápido.")
    logger.info("=" * 60)


def verify_indexes():
    """Verifica que los índices se hayan creado correctamente"""
    
    logger.info("\n" + "=" * 60)
    logger.info("VERIFICANDO ÍNDICES CREADOS")
    logger.info("=" * 60)
    
    with engine.connect() as conn:
        # Verificar índices de invoices_v2
        result = conn.execute(text("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'invoices_v2'
            AND indexname LIKE 'idx_%'
            ORDER BY indexname
        """))
        
        logger.info("\n📋 Índices en tabla invoices_v2:")
        for row in result:
            logger.info(f"   • {row[0]}")
        
        # Verificar índices de invoice_products_v2
        result = conn.execute(text("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'invoice_products_v2'
            AND indexname LIKE 'idx_%'
            ORDER BY indexname
        """))
        
        logger.info("\n📋 Índices en tabla invoice_products_v2:")
        for row in result:
            logger.info(f"   • {row[0]}")
        
        # Mostrar tamaño de índices
        result = conn.execute(text("""
            SELECT
                tablename,
                indexname,
                pg_size_pretty(pg_relation_size(indexrelid)) as index_size
            FROM pg_stat_user_indexes
            WHERE tablename IN ('invoices_v2', 'invoice_products_v2')
            ORDER BY pg_relation_size(indexrelid) DESC
        """))
        
        logger.info("\n💾 Tamaño de índices:")
        for row in result:
            logger.info(f"   • {row[1]}: {row[2]}")


if __name__ == "__main__":
    try:
        logger.info("🚀 Iniciando aplicación de índices de optimización...\n")
        
        apply_indexes()
        verify_indexes()
        
        logger.info("\n✅ Proceso completado exitosamente!")
        logger.info("\n💡 Recomendaciones:")
        logger.info("   1. Reinicia el servidor para que los cambios tengan efecto completo")
        logger.info("   2. Prueba la paginación y verifica la mejora en velocidad")
        logger.info("   3. Monitorea el uso de índices con el script de estadísticas")
        
    except Exception as e:
        logger.error(f"\n❌ Error fatal: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
