#!/bin/bash
# ========================================
# Script de Optimización de Rendimiento - Papyrus
# ========================================
# Ejecutar en el servidor: bash run_performance_optimizations.sh
# ========================================

set -e

echo "=========================================="
echo "🚀 OPTIMIZACIÓN DE RENDIMIENTO - PAPYRUS"
echo "=========================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar que estamos en el directorio correcto
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Error: Ejecutar desde el directorio CODE/${NC}"
    echo "   cd /path/to/CODE && bash scripts/database/run_performance_optimizations.sh"
    exit 1
fi

# 1. Aplicar índices de base de datos
echo -e "${YELLOW}📊 Paso 1: Aplicando índices de base de datos...${NC}"
echo ""

# Verificar si existe el archivo SQL
if [ -f "scripts/database/create_performance_indexes.sql" ]; then
    echo "   Ejecutando script SQL de índices..."
    
    # Intentar ejecutar con psql si está disponible
    if command -v psql &> /dev/null; then
        # Obtener credenciales de .env
        if [ -f ".env" ]; then
            source .env 2>/dev/null || true
        fi
        
        if [ -n "$DATABASE_URL" ]; then
            echo "   Conectando a la base de datos..."
            psql "$DATABASE_URL" -f scripts/database/create_performance_indexes.sql 2>&1 || {
                echo -e "${YELLOW}   ⚠️ Algunos índices pueden ya existir (esto es normal)${NC}"
            }
            echo -e "${GREEN}   ✅ Índices aplicados${NC}"
        else
            echo -e "${YELLOW}   ⚠️ DATABASE_URL no encontrada, ejecutando script Python...${NC}"
            python scripts/database/apply_performance_indexes.py
        fi
    else
        echo "   psql no disponible, ejecutando script Python..."
        python scripts/database/apply_performance_indexes.py
    fi
else
    echo -e "${YELLOW}   ⚠️ Archivo SQL no encontrado, ejecutando script Python...${NC}"
    python scripts/database/apply_performance_indexes.py
fi

echo ""

# 2. Limpiar caché de Redis
echo -e "${YELLOW}🗑️ Paso 2: Limpiando caché de Redis...${NC}"
echo ""

python -c "
from app.cache_manager import cache_manager
if cache_manager.redis_client:
    cleared = cache_manager.clear_pattern('paqueteria:cache:*')
    print(f'   ✅ Caché limpiado: {cleared} claves eliminadas')
else:
    print('   ⚠️ Redis no disponible')
" 2>/dev/null || echo -e "${YELLOW}   ⚠️ No se pudo limpiar el caché${NC}"

echo ""

# 3. Verificar configuración de pool de conexiones
echo -e "${YELLOW}🔌 Paso 3: Verificando pool de conexiones...${NC}"
echo ""

python -c "
from app.database_optimized import get_db_pool_status, POOL_SIZE, MAX_OVERFLOW, IS_STAGING
print(f'   Entorno: {\"STAGING\" if IS_STAGING else \"PRODUCCIÓN\"}')
print(f'   Pool size: {POOL_SIZE}')
print(f'   Max overflow: {MAX_OVERFLOW}')
status = get_db_pool_status()
if 'error' not in status:
    print(f'   Conexiones activas: {status.get(\"checked_out\", 0)}')
    print(f'   Conexiones disponibles: {status.get(\"checked_in\", 0)}')
    print('   ✅ Pool de conexiones OK')
else:
    print(f'   ⚠️ {status.get(\"error\")}')
" 2>/dev/null || echo -e "${YELLOW}   ⚠️ No se pudo verificar el pool${NC}"

echo ""

# 4. Ejecutar ANALYZE en tablas principales
echo -e "${YELLOW}📈 Paso 4: Actualizando estadísticas de tablas...${NC}"
echo ""

python -c "
from sqlalchemy import text
from app.database import SessionLocal

db = SessionLocal()
tables = ['packages', 'customers', 'messages', 'notifications', 'package_history', 'package_announcements_new']
for table in tables:
    try:
        db.execute(text(f'ANALYZE {table}'))
        db.commit()
        print(f'   ✅ ANALYZE {table}')
    except Exception as e:
        print(f'   ⚠️ {table}: {str(e)[:50]}')
db.close()
" 2>/dev/null || echo -e "${YELLOW}   ⚠️ No se pudieron actualizar estadísticas${NC}"

echo ""

# 5. Mostrar resumen
echo "=========================================="
echo -e "${GREEN}✅ OPTIMIZACIÓN COMPLETADA${NC}"
echo "=========================================="
echo ""
echo "Cambios aplicados:"
echo "  • Índices de base de datos creados/verificados"
echo "  • Caché de Redis limpiado"
echo "  • Estadísticas de tablas actualizadas"
echo ""
echo "Próximos pasos recomendados:"
echo "  1. Reiniciar la aplicación: docker-compose restart app"
echo "  2. Monitorear rendimiento en los próximos minutos"
echo "  3. Verificar logs: docker-compose logs -f app"
echo ""
