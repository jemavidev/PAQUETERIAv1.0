#!/bin/bash
# ========================================
# POST-DEPLOY HOOK - PAPYRUS
# ========================================
# Este script se ejecuta DESPUÉS del deploy en papyrus

echo "🎉 Ejecutando tareas post-deploy..."

# 1. Limpiar caché de Redis
echo "🧹 Limpiando caché de Redis..."
docker exec $(docker ps -qf name=redis) redis-cli FLUSHDB

# 2. Verificar logs por errores
echo "🔍 Verificando logs por errores..."
ERROR_COUNT=$(docker compose logs --tail=100 app | grep -i "error" | wc -l)
if [ "$ERROR_COUNT" -gt 0 ]; then
    echo "⚠️  Se encontraron $ERROR_COUNT errores en los logs"
fi

# 3. Warm-up de caché (opcional)
echo "🔥 Warm-up de caché..."
curl -s http://localhost:8000/api/packages > /dev/null

# 4. Notificar éxito (opcional)
# curl -X POST $SLACK_WEBHOOK -d '{"text":"✅ Deploy completado exitosamente en papyrus"}'

# 5. Mostrar métricas
echo "📊 Métricas post-deploy:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | head -5

echo "✅ Tareas post-deploy completadas"
exit 0
