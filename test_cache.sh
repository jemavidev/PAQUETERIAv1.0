#!/bin/bash
# ========================================
# Script de verificación de cache
# ========================================

echo "=========================================="
echo "🧪 VERIFICACIÓN DE CACHE"
echo "=========================================="
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para medir tiempo
measure_time() {
    local url=$1
    local name=$2
    
    echo "📊 Test: $name"
    echo "------------------------------------------"
    
    # Primera llamada (cache miss)
    echo -n "Primera llamada (CACHE MISS): "
    time1=$(curl -o /dev/null -s -w '%{time_total}\n' "$url")
    echo "${time1}s"
    
    # Esperar un poco
    sleep 0.5
    
    # Segunda llamada (cache hit)
    echo -n "Segunda llamada (CACHE HIT):  "
    time2=$(curl -o /dev/null -s -w '%{time_total}\n' "$url")
    echo "${time2}s"
    
    # Calcular mejora
    improvement=$(echo "scale=2; (($time1 - $time2) / $time1) * 100" | bc)
    echo -e "${GREEN}🚀 Mejora: ${improvement}%${NC}"
    echo ""
}

# URL base (cambiar según entorno)
BASE_URL="${1:-http://localhost:8000}"

# Detectar si es staging
if [[ "$BASE_URL" == *"staging.jemavi.co"* ]]; then
    IS_STAGING=true
    SSH_HOST="staging"
else
    IS_STAGING=false
    SSH_HOST=""
fi

echo "URL Base: $BASE_URL"
echo ""

# Test 1: Health check
echo "1️⃣  Health Check"
echo "------------------------------------------"
curl -s "$BASE_URL/health" | python3 -m json.tool
echo ""
echo ""

# Test 2: Verificar Redis
echo "2️⃣  Verificar Redis"
echo "------------------------------------------"
if [ "$IS_STAGING" = true ]; then
    # Ejecutar en servidor staging remoto
    ssh staging "docker exec paqueteria_staging_app python -c '
from app.cache_manager import cache_manager
import json
print(\"Redis Status:\", \"OK\" if cache_manager.redis_client else \"ERROR\")
stats = cache_manager.get_cache_stats()
print(json.dumps(stats, indent=2))
'" 2>/dev/null || echo -e "${YELLOW}⚠️  No se pudo conectar al servidor staging${NC}"
elif command -v docker &> /dev/null; then
    # Ejecutar localmente
    docker exec paqueteria_staging_app python -c "
from app.cache_manager import cache_manager
import json
print('Redis Status:', 'OK' if cache_manager.redis_client else 'ERROR')
stats = cache_manager.get_cache_stats()
print(json.dumps(stats, indent=2))
" 2>/dev/null || echo -e "${YELLOW}⚠️  No se pudo conectar al contenedor${NC}"
else
    echo -e "${YELLOW}⚠️  Docker no disponible${NC}"
fi
echo ""
echo ""

# Test 3: Búsqueda de paquetes
measure_time "$BASE_URL/api/packages?limit=10" "Búsqueda de paquetes"

# Test 4: Estadísticas (si tienes autenticación, agregar headers)
# measure_time "$BASE_URL/api/admin/dashboard" "Estadísticas de dashboard"

echo "=========================================="
echo "✅ VERIFICACIÓN COMPLETADA"
echo "=========================================="
echo ""
echo "💡 Notas:"
echo "   - Cache HIT debe ser significativamente más rápido"
echo "   - Mejora esperada: >80%"
echo "   - Si no hay mejora, verificar Redis"
echo ""
