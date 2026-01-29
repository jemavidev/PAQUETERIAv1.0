#!/bin/bash
# Fix para sincronización - Montar /tmp del host en el contenedor

echo "🔧 Fix: Montando /tmp para sincronización"
echo "=========================================="
echo ""

# Detectar comando docker compose
DOCKER_COMPOSE=""
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
    echo "✅ Usando: docker-compose"
elif docker compose version &> /dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
    echo "✅ Usando: docker compose"
else
    echo "❌ ERROR: No se encontró docker-compose ni docker compose"
    exit 1
fi
echo ""

echo "📋 Paso 1: Detener contenedor staging"
cd ~/paqueteria-staging
$DOCKER_COMPOSE -f docker-compose.staging.yml down app
echo "✅ Contenedor detenido"
echo ""

echo "📋 Paso 2: Actualizar docker-compose.staging.yml"
echo "   Agregando volumen: /tmp:/tmp"
echo ""

# Verificar si ya existe el volumen
if grep -q "/tmp:/tmp" docker-compose.staging.yml; then
    echo "✅ El volumen /tmp ya está configurado"
else
    echo "⚠️  El volumen /tmp NO está configurado"
    echo "   Por favor actualiza docker-compose.staging.yml manualmente"
    echo "   O sube el archivo actualizado desde tu máquina local"
fi
echo ""

echo "📋 Paso 3: Reiniciar contenedor"
$DOCKER_COMPOSE -f docker-compose.staging.yml up -d app
echo "✅ Contenedor reiniciado"
echo ""

echo "📋 Paso 4: Verificar que el contenedor está corriendo"
docker ps | grep paqueteria_staging_app
echo ""

echo "📋 Paso 5: Probar creación de archivo en /tmp"
echo "test" > /tmp/test_sync_fix
if docker exec paqueteria_staging_app ls /tmp/test_sync_fix &> /dev/null; then
    echo "✅ El contenedor puede ver archivos en /tmp del host"
    rm /tmp/test_sync_fix
else
    echo "❌ El contenedor NO puede ver archivos en /tmp del host"
    echo "   Verifica que el volumen esté correctamente configurado"
fi
echo ""

echo "=========================================="
echo "✅ Fix aplicado"
echo ""
echo "📝 Próximos pasos:"
echo "   1. Probar sincronización desde el navegador"
echo "   2. Ver logs: sudo journalctl -u staging-sync-monitor -f"
echo "   3. Verificar: ./debug_sync.sh"
