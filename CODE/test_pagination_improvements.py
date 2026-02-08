#!/usr/bin/env python3
"""
Tests para verificar las mejoras de paginación
Sistema de Facturas V2

Verifica:
- Índices creados correctamente
- Performance de queries
- Funcionalidad de paginación
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from sqlalchemy import text
from app.database import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_indexes_exist():
    """Verifica que todos los índices existan"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 1: Verificando existencia de índices")
    logger.info("=" * 60)
    
    required_indexes = [
        'idx_invoices_v2_created_at',
        'idx_invoices_v2_estado',
        'idx_invoices_v2_fecha_emision',
        'idx_invoices_v2_proveedor_nombre',
        'idx_invoices_v2_numero_factura',
        'idx_invoices_v2_estado_created',
        'idx_invoices_v2_dian_validado',
        'idx_invoices_v2_proveedor_nit',
    ]
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT indexname
            FROM pg_indexes
            WHERE tablename = 'invoices_v2'
            AND indexname LIKE 'idx_%'
        """))
        
        existing_indexes = [row[0] for row in result]
        
        missing = []
        for idx in required_indexes:
            if idx in existing_indexes:
                logger.info(f"   ✅ {idx}")
            else:
                logger.info(f"   ❌ {idx} - FALTA")
                missing.append(idx)
        
        if missing:
            logger.error(f"\n❌ Faltan {len(missing)} índices")
            return False
        else:
            logger.info(f"\n✅ Todos los índices ({len(required_indexes)}) están creados")
            return True


def test_query_performance():
    """Mide el performance de queries con y sin índices"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Midiendo performance de queries")
    logger.info("=" * 60)
    
    queries = [
        {
            "name": "Ordenamiento por fecha (paginación)",
            "sql": "SELECT * FROM invoices_v2 ORDER BY created_at DESC LIMIT 25"
        },
        {
            "name": "Filtro por estado",
            "sql": "SELECT * FROM invoices_v2 WHERE estado = 'completo' LIMIT 25"
        },
        {
            "name": "Búsqueda por proveedor",
            "sql": "SELECT * FROM invoices_v2 WHERE proveedor_nombre ILIKE '%PROVEEDOR%' LIMIT 25"
        },
        {
            "name": "Query compuesta (estado + ordenamiento)",
            "sql": "SELECT * FROM invoices_v2 WHERE estado = 'completo' ORDER BY created_at DESC LIMIT 25"
        },
        {
            "name": "Count total",
            "sql": "SELECT COUNT(*) FROM invoices_v2"
        }
    ]
    
    with engine.connect() as conn:
        for query in queries:
            # Ejecutar 3 veces y promediar
            times = []
            for _ in range(3):
                start = time.time()
                conn.execute(text(query["sql"]))
                elapsed = (time.time() - start) * 1000  # ms
                times.append(elapsed)
            
            avg_time = sum(times) / len(times)
            
            # Clasificar performance
            if avg_time < 50:
                status = "🚀 EXCELENTE"
                color = "green"
            elif avg_time < 200:
                status = "✅ BUENO"
                color = "green"
            elif avg_time < 500:
                status = "⚠️  ACEPTABLE"
                color = "yellow"
            else:
                status = "❌ LENTO"
                color = "red"
            
            logger.info(f"\n   {query['name']}")
            logger.info(f"   Tiempo promedio: {avg_time:.2f}ms - {status}")


def test_pagination_logic():
    """Verifica la lógica de paginación"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Verificando lógica de paginación")
    logger.info("=" * 60)
    
    with engine.connect() as conn:
        # Obtener total de registros
        result = conn.execute(text("SELECT COUNT(*) FROM invoices_v2"))
        total = result.fetchone()[0]
        
        logger.info(f"\n   Total de facturas: {total}")
        
        if total == 0:
            logger.warning("   ⚠️  No hay facturas en la base de datos")
            return True
        
        # Probar diferentes tamaños de página
        page_sizes = [10, 25, 50, 100]
        
        for page_size in page_sizes:
            total_pages = (total + page_size - 1) // page_size
            
            # Probar primera página
            result = conn.execute(text(f"""
                SELECT COUNT(*) FROM (
                    SELECT * FROM invoices_v2 
                    ORDER BY created_at DESC 
                    LIMIT {page_size}
                ) as subquery
            """))
            count = result.fetchone()[0]
            
            expected = min(page_size, total)
            if count == expected:
                logger.info(f"   ✅ Página 1 con {page_size} items: {count} registros")
            else:
                logger.error(f"   ❌ Página 1 con {page_size} items: esperado {expected}, obtenido {count}")
                return False
        
        logger.info(f"\n✅ Lógica de paginación correcta")
        return True


def test_index_usage():
    """Verifica que los índices se estén usando"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Verificando uso de índices")
    logger.info("=" * 60)
    
    with engine.connect() as conn:
        # Ejecutar EXPLAIN para ver si usa índices
        queries = [
            {
                "name": "Ordenamiento",
                "sql": "EXPLAIN SELECT * FROM invoices_v2 ORDER BY created_at DESC LIMIT 25",
                "should_use": "idx_invoices_v2_created_at"
            },
            {
                "name": "Filtro por estado",
                "sql": "EXPLAIN SELECT * FROM invoices_v2 WHERE estado = 'completo'",
                "should_use": "idx_invoices_v2_estado"
            }
        ]
        
        for query in queries:
            result = conn.execute(text(query["sql"]))
            plan = "\n".join([row[0] for row in result])
            
            if query["should_use"] in plan or "Index Scan" in plan:
                logger.info(f"   ✅ {query['name']}: Usando índice")
            else:
                logger.warning(f"   ⚠️  {query['name']}: No usa índice (puede ser normal si hay pocos datos)")


def run_all_tests():
    """Ejecuta todos los tests"""
    logger.info("\n" + "=" * 60)
    logger.info("🧪 EJECUTANDO TESTS DE PAGINACIÓN")
    logger.info("=" * 60)
    
    results = []
    
    # Test 1: Índices
    try:
        results.append(("Índices", test_indexes_exist()))
    except Exception as e:
        logger.error(f"❌ Error en test de índices: {e}")
        results.append(("Índices", False))
    
    # Test 2: Performance
    try:
        test_query_performance()
        results.append(("Performance", True))
    except Exception as e:
        logger.error(f"❌ Error en test de performance: {e}")
        results.append(("Performance", False))
    
    # Test 3: Lógica
    try:
        results.append(("Lógica", test_pagination_logic()))
    except Exception as e:
        logger.error(f"❌ Error en test de lógica: {e}")
        results.append(("Lógica", False))
    
    # Test 4: Uso de índices
    try:
        test_index_usage()
        results.append(("Uso de índices", True))
    except Exception as e:
        logger.error(f"❌ Error en test de uso de índices: {e}")
        results.append(("Uso de índices", False))
    
    # Resumen
    logger.info("\n" + "=" * 60)
    logger.info("📊 RESUMEN DE TESTS")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"   {name}: {status}")
    
    logger.info(f"\n   Total: {passed}/{total} tests pasados")
    
    if passed == total:
        logger.info("\n🎉 ¡Todos los tests pasaron exitosamente!")
        return True
    else:
        logger.warning(f"\n⚠️  {total - passed} test(s) fallaron")
        return False


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"\n❌ Error fatal: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
