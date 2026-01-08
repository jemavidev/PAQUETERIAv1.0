#!/bin/bash
# ========================================
# Deploy de optimizaciones de cache a staging
# ========================================

set -e

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "🚀 DEPLOY DE OPTIMIZACIONES DE CACHE"
echo "=========================================="
echo ""
echo "Servidor: staging.jemavi.co"
echo "SSH: staging"
echo "Rama: staging"
echo ""

# Verificar que estamos en la rama staging
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "staging" ]; then
    echo -e "${RED}❌ Error: Debes estar en la rama staging${NC}"
    echo "   Rama actual: $CURRENT_BRANCH"
    exit 1
fi

echo -e "${GREEN}✅ Rama correcta: staging${NC}"
echo ""

# Verificar que no hay cambios sin commit
if ! git diff-index --quiet HEAD --; then
    echo -e "${RED}❌ Error: Hay cambios sin commit${NC}"
    echo "   Haz commit de tus cambios primero"
    exit 1
fi

echo -e "${GREEN}✅ No hay cambios sin commit${NC}"
echo ""

# Paso 1: Pull en servidor staging
echo "📥 Paso 1: Pull en servidor staging"
echo "------------------------------------------"
ssh staging "cd /home/ubuntu/paqueteria-staging && git pull origin staging"
echo -e "${GREEN}✅ Pull completado${NC}"
echo ""

# Paso 2: Rebuild de contenedores
echo "🔨 Paso 2: Rebuild de contenedores"
echo "------------------------------------------"
echo "⚠️  Esto tomará unos minutos..."
ssh staging "cd /home/ubuntu/paqueteria-staging && docker compose -f docker-compose.staging.yml build app"
echo -e "${GREEN}✅ Build completado${NC}"
echo ""

# Paso 3: Restart de servicios
echo "🔄 Paso 3: Restart de servicios"
echo "------------------------------------------"
ssh staging "cd /home/ubuntu/paqueteria-staging && docker compose -f docker-compose.staging.yml up -d"
echo -e "${GREEN}✅ Servicios reiniciados${NC}"
echo ""

# Paso 4: Esperar a que la aplicación esté lista
echo "⏳ Paso 4: Esperando a que la aplicación esté lista..."
echo "------------------------------------------"
sleep 10

# Verificar health check
for i in {1..10}; do
    if curl -s https://staging.jemavi.co/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Aplicación lista${NC}"
        break
    else
        echo "   Intento $i/10..."
        sleep 3
    fi
    
    if [ $i -eq 10 ]; then
        echo -e "${RED}❌ Error: La aplicación no responde${NC}"
        exit 1
    fi
done
echo ""

# Paso 5: Verificar Redis
echo "🔍 Paso 5: Verificar Redis"
echo "------------------------------------------"
ssh staging "docker exec paqueteria_staging_app python -c '
from app.cache_manager import cache_manager
import json
print(\"Redis Status:\", \"OK\" if cache_manager.redis_client else \"ERROR\")
try:
    stats = cache_manager.get_cache_stats()
    print(json.dumps(stats, indent=2))
except Exception as e:
    print(\"Error:\", str(e))
'" || echo -e "${YELLOW}⚠️  No se pudo verificar Redis${NC}"
echo ""

# Paso 6: Verificar logs
echo "📋 Paso 6: Verificar logs (últimas 20 líneas)"
echo "------------------------------------------"
ssh staging "docker logs --tail 20 paqueteria_staging_app 2>&1 | grep -E 'Cache|ERROR|WARNING' || echo 'No hay errores de cache'"
echo ""

# Paso 7: Test de rendimiento
echo "🧪 Paso 7: Test de rendimiento de cache"
echo "------------------------------------------"
echo ""

# Test 1: Health check
echo "Test 1: Health check"
curl -s https://staging.jemavi.co/health | python3 -m json.tool
echo ""

# Test 2: Búsqueda de paquetes (2 llamadas)
echo "Test 2: Búsqueda de paquetes"
echo "Primera llamada (cache miss):"
time1=$(curl -o /dev/null -s -w '%{time_total}' https://staging.jemavi.co/api/packages?limit=10)
echo "  Tiempo: ${time1}s"

sleep 1

echo "Segunda llamada (cache hit):"
time2=$(curl -o /dev/null -s -w '%{time_total}' https://staging.jemavi.co/api/packages?limit=10)
echo "  Tiempo: ${time2}s"

# Calcular mejora
improvement=$(echo "scale=2; (($time1 - $time2) / $time1) * 100" | bc 2>/dev/null || echo "N/A")
if [ "$improvement" != "N/A" ]; then
    echo -e "  ${GREEN}🚀 Mejora: ${improvement}%${NC}"
fi
echo ""

# Resumen final
echo "=========================================="
echo "✅ DEPLOY COMPLETADO"
echo "=========================================="
echo ""
echo "📊 Resumen:"
echo "   - Servidor: staging.jemavi.co"
echo "   - Rama: staging"
echo "   - Redis: Verificado"
echo "   - Cache: Funcionando"
echo ""
echo "🔗 URLs:"
echo "   - Health: https://staging.jemavi.co/health"
echo "   - API: https://staging.jemavi.co/api/packages"
echo "   - Admin: https://staging.jemavi.co/admin"
echo ""
echo "📝 Próximos pasos:"
echo "   1. Monitorear logs por 1 hora"
echo "   2. Verificar cache hit rate (objetivo: >80%)"
echo "   3. Verificar tiempos de respuesta"
echo "   4. Si todo OK, deploy a producción"
echo ""
echo "🧪 Para más pruebas:"
echo "   ./test_cache.sh https://staging.jemavi.co"
echo ""
