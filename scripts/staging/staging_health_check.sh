#!/bin/bash
# Script rápido para verificar el estado de staging

echo "╔════════════════════════════════════════════════════════╗"
echo "║       VERIFICACIÓN DE SALUD - STAGING                  ║"
echo "╚════════════════════════════════════════════════════════╝"

echo -e "\n📦 Estado de contenedores:"
ssh -o ConnectTimeout=10 staging 'timeout 5 docker ps --format "table {{.Names}}\t{{.Status}}" 2>&1' || echo "❌ Error al obtener estado"

echo -e "\n🏥 Health Check (interno - puerto 8001):"
HEALTH=$(ssh -o ConnectTimeout=10 staging 'timeout 3 curl -s http://localhost:8001/health 2>&1')
if echo "$HEALTH" | grep -q "healthy"; then
    echo "✅ $HEALTH"
else
    echo "❌ FAILED: $HEALTH"
fi

echo -e "\n🌐 Health Check (externo - HTTPS):"
EXTERNAL=$(ssh -o ConnectTimeout=10 staging 'timeout 3 curl -s https://staging.jemavi.co/health 2>&1')
if echo "$EXTERNAL" | grep -q "healthy"; then
    echo "✅ $EXTERNAL"
else
    echo "❌ FAILED: $EXTERNAL"
fi

echo -e "\n📊 Últimas 10 líneas de logs:"
ssh -o ConnectTimeout=10 staging 'timeout 5 docker logs --tail 10 paqueteria_staging_app 2>&1'

echo -e "\n╔════════════════════════════════════════════════════════╗"
echo "║       VERIFICACIÓN COMPLETADA                          ║"
echo "╚════════════════════════════════════════════════════════╝"
