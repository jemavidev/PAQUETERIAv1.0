#!/bin/bash
# ========================================
# POST-DEPLOY HOOK - PAPYRUS
# ========================================
# Este script se ejecuta DESPUÉS del deploy en papyrus

echo "🎉 Ejecutando tareas post-deploy..."

# 1. Limpiar caché de Redis
echo "🧹 Limpiando caché de Redis..."
docker compose -f docker-compose.prod.yml exec -T redis redis-cli -a "${REDIS_PASSWORD:-Redis2025!Secure}" FLUSHDB || echo "⚠️  No se pudo limpiar Redis (no crítico)"

# 2. Verificar logs por errores
echo "🔍 Verificando logs por errores..."
ERROR_COUNT=$(docker compose -f docker-compose.prod.yml logs --tail=100 app 2>/dev/null | grep -i "error" | wc -l)
if [ "$ERROR_COUNT" -gt 0 ]; then
    echo "⚠️  Se encontraron $ERROR_COUNT errores en los logs"
else
    echo "✅ No se encontraron errores en los logs"
fi

# 3. Warm-up de caché (opcional)
echo "🔥 Warm-up de caché..."
curl -s -f http://localhost:8000/health > /dev/null 2>&1 && echo "✅ Aplicación respondiendo" || echo "⚠️  Aplicación no responde aún"

# 4. Notificar éxito (opcional)
# curl -X POST $SLACK_WEBHOOK -d '{"text":"✅ Deploy completado exitosamente en papyrus"}'

# 5. Mostrar métricas
echo "📊 Métricas post-deploy:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null | grep "paqueteria_v1_prod" | head -5 || echo "✅ Contenedores corriendo"

echo "✅ Tareas post-deploy completadas"
exit 0
