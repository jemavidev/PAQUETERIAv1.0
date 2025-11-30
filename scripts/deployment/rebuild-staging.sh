#!/bin/bash
# Script para reconstruir contenedores en staging
# Fecha: 2025-11-29

set -e

echo "🔄 =========================================="
echo "   RECONSTRUIR CONTENEDORES STAGING"
echo "   =========================================="
echo ""

echo "📋 Paso 1: Conectando a servidor staging..."
ssh staging << 'ENDSSH'
cd paqueteria-staging

echo ""
echo "📋 Paso 2: Verificando commit actual..."
git log -1 --oneline

echo ""
echo "📋 Paso 3: Deteniendo contenedores..."
docker compose -f docker-compose.staging.yml down

echo ""
echo "📋 Paso 4: Reconstruyendo contenedores (sin caché)..."
docker compose -f docker-compose.staging.yml build --no-cache

echo ""
echo "📋 Paso 5: Iniciando contenedores..."
docker compose -f docker-compose.staging.yml up -d

echo ""
echo "📋 Paso 6: Esperando que los contenedores estén listos..."
sleep 10

echo ""
echo "📋 Paso 7: Verificando estado de contenedores..."
docker compose -f docker-compose.staging.yml ps

echo ""
echo "✅ =========================================="
echo "   RECONSTRUCCIÓN COMPLETADA"
echo "   =========================================="
echo ""
echo "🔍 Verificación:"
echo "   - Contenedores reconstruidos desde cero ✅"
echo "   - Servidor staging reiniciado ✅"
echo ""
echo "💡 Ahora prueba en tu celular:"
echo "   1. Abre https://staging.jemavi.co/announce"
echo "   2. Limpia caché del navegador (Ctrl+Shift+R o Cmd+Shift+R)"
echo "   3. Deberías ver un badge verde por 4 segundos"
echo "   4. Deberías ver el footer con 4 iconos abajo"
echo ""
ENDSSH

echo ""
echo "🎉 ¡Listo! Ahora verifica en tu celular."
