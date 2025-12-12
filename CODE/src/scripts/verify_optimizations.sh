#!/bin/bash
# Script de verificación de optimizaciones

echo "🔍 VERIFICACIÓN DE OPTIMIZACIONES"
echo "=================================="
echo ""

# 1. Verificar configuración de workers
echo "1️⃣  Configuración de Workers:"
docker exec paqueteria_staging_app python -c "
from uvicorn_config import *
print(f'   Entorno: {ENVIRONMENT}')
print(f'   Workers: {WORKERS}')
print(f'   Concurrency: {LIMIT_CONCURRENCY}')
" 2>/dev/null || echo "   ❌ Error al verificar workers"
echo ""

# 2. Verificar pool de conexiones
echo "2️⃣  Pool de Conexiones:"
docker exec paqueteria_staging_app python -c "
from app.database_optimized import get_db_pool_status, IS_STAGING, POOL_SIZE, MAX_OVERFLOW
import json
print(f'   Entorno: {\"STAGING\" if IS_STAGING else \"PRODUCCIÓN\"}')
print(f'   Pool size: {POOL_SIZE}')
print(f'   Max overflow: {MAX_OVERFLOW}')
status = get_db_pool_status()
print(f'   Conexiones activas: {status[\"checked_out\"]}')
print(f'   Conexiones disponibles: {status[\"checked_in\"]}')
" 2>/dev/null || echo "   ❌ Error al verificar pool"
echo ""

# 3. Verificar memoria del sistema
echo "3️⃣  Uso de Memoria:"
free -h | grep -E "Mem:|Swap:" | awk '{print "   " $0}'
echo ""

# 4. Verificar índices en BD
echo "4️⃣  Índices en Base de Datos:"
docker exec paqueteria_staging_app python -c "
from sqlalchemy import text
from app.database_optimized import SessionLocal

db = SessionLocal()
result = db.execute(text(\"SELECT COUNT(*) FROM pg_indexes WHERE tablename IN ('packages', 'customers', 'messages', 'notifications', 'users', 'file_uploads')\")).fetchone()
db.close()
print(f'   Total índices: {result[0]}')
" 2>/dev/null || echo "   ❌ Error al verificar índices"
echo ""

# 5. Test de tiempo de respuesta
echo "5️⃣  Tiempo de Respuesta:"
TIME=$(curl -w "%{time_total}" -o /dev/null -s http://localhost:8001/health)
echo "   Health endpoint: ${TIME}s"
echo ""

# 6. Verificar logs recientes
echo "6️⃣  Logs Recientes (últimas 5 líneas):"
docker logs --tail 5 paqueteria_staging_app 2>&1 | sed 's/^/   /'
echo ""

echo "=================================="
echo "✅ Verificación completada"
