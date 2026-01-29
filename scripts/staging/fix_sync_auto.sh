#!/bin/bash
# Fix automático para sincronización - Detecta docker-compose o docker compose

echo "🔧 Fix Automático: Sincronización"
echo "=================================="
echo ""

# Detectar comando docker compose
echo "🔍 Detectando comando Docker Compose..."
DOCKER_COMPOSE=""

if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
    echo "✅ Encontrado: docker-compose"
elif docker compose version &> /dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
    echo "✅ Encontrado: docker compose"
else
    echo "❌ ERROR: No se encontró docker-compose"
    echo ""
    echo "Soluciones:"
    echo "1. Instalar docker-compose:"
    echo "   sudo yum install docker-compose"
    echo ""
    echo "2. O usar Docker Compose v2:"
    echo "   sudo yum install docker-compose-plugin"
    echo ""
    exit 1
fi
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f ~/paqueteria-staging/docker-compose.staging.yml ]; then
    echo "❌ ERROR: No se encuentra docker-compose.staging.yml"
    echo "   Directorio esperado: ~/paqueteria-staging/"
    echo ""
    echo "¿Dónde está el archivo?"
    ls -la ~/paqueteria-staging/ 2>/dev/null || echo "El directorio no existe"
    exit 1
fi

cd ~/paqueteria-staging

echo "📋 Paso 1: Verificar archivo docker-compose.staging.yml"
if grep -q "/tmp:/tmp" docker-compose.staging.yml; then
    echo "✅ El volumen /tmp ya está configurado"
    echo "   No es necesario modificar el archivo"
else
    echo "⚠️  El volumen /tmp NO está configurado"
    echo "   Necesitas subir el archivo actualizado desde tu máquina local:"
    echo ""
    echo "   scp docker-compose.staging.yml staging:~/paqueteria-staging/"
    echo ""
    read -p "¿Ya subiste el archivo actualizado? (s/n): " respuesta
    if [ "$respuesta" != "s" ]; then
        echo "Por favor sube el archivo y ejecuta este script de nuevo"
        exit 1
    fi
fi
echo ""

echo "📋 Paso 2: Detener contenedor"
$DOCKER_COMPOSE -f docker-compose.staging.yml down app
echo "✅ Contenedor detenido"
echo ""

echo "📋 Paso 3: Iniciar contenedor con nueva configuración"
$DOCKER_COMPOSE -f docker-compose.staging.yml up -d app
echo "✅ Contenedor iniciado"
echo ""

echo "📋 Paso 4: Esperar a que el contenedor esté listo..."
sleep 5
echo ""

echo "📋 Paso 5: Verificar que está corriendo"
if docker ps | grep -q paqueteria_staging_app; then
    echo "✅ Contenedor corriendo"
    docker ps | grep paqueteria_staging_app
else
    echo "❌ Contenedor NO está corriendo"
    echo "Ver logs:"
    docker logs paqueteria_staging_app
    exit 1
fi
echo ""

echo "📋 Paso 6: Probar comunicación host-contenedor"
echo "test_sync" > /tmp/test_sync_fix
if docker exec paqueteria_staging_app cat /tmp/test_sync_fix &> /dev/null; then
    echo "✅ El contenedor puede ver archivos en /tmp del host"
    rm /tmp/test_sync_fix
else
    echo "❌ El contenedor NO puede ver archivos en /tmp del host"
    echo "   El volumen /tmp:/tmp no está montado correctamente"
    echo ""
    echo "Verificar configuración:"
    docker inspect paqueteria_staging_app | grep -A 5 "Mounts"
    exit 1
fi
echo ""

echo "=================================="
echo "✅ Fix aplicado exitosamente"
echo ""
echo "📝 Próximos pasos:"
echo "   1. Abrir staging en el navegador"
echo "   2. Click en '🔄 Sincronizar'"
echo "   3. Confirmar y esperar"
echo ""
echo "🔍 Para ver logs en tiempo real:"
echo "   sudo journalctl -u staging-sync-monitor -f"
echo ""
