#!/bin/bash
# Script para diagnosticar problemas con archivos estáticos

echo "========================================="
echo "DIAGNÓSTICO DE ARCHIVOS ESTÁTICOS"
echo "========================================="
echo ""

# Verificar si Docker está corriendo
if ! docker ps &> /dev/null; then
    echo "❌ Docker no está corriendo o no tienes permisos"
    exit 1
fi

# Obtener el contenedor de la app
CONTAINER=$(docker ps --filter "name=paqueteria_app" --format "{{.Names}}" | head -n 1)

if [ -z "$CONTAINER" ]; then
    echo "❌ No se encontró el contenedor de la aplicación"
    echo "Contenedores activos:"
    docker ps --format "table {{.Names}}\t{{.Status}}"
    exit 1
fi

echo "✅ Contenedor encontrado: $CONTAINER"
echo ""

echo "📁 Verificando estructura de directorios en el contenedor:"
echo "-----------------------------------------------------------"
docker exec $CONTAINER ls -la /app/ 2>/dev/null || echo "❌ No se puede acceder a /app/"
echo ""

echo "📁 Verificando /app/src/:"
docker exec $CONTAINER ls -la /app/src/ 2>/dev/null || echo "❌ No existe /app/src/"
echo ""

echo "📁 Verificando /app/src/static/:"
docker exec $CONTAINER ls -la /app/src/static/ 2>/dev/null || echo "❌ No existe /app/src/static/"
echo ""

echo "📁 Verificando /app/src/static/images/:"
docker exec $CONTAINER ls -la /app/src/static/images/ 2>/dev/null || echo "❌ No existe /app/src/static/images/"
echo ""

echo "📁 Verificando /app/static/:"
docker exec $CONTAINER ls -la /app/static/ 2>/dev/null || echo "❌ No existe /app/static/"
echo ""

echo "🔍 Verificando montajes de volúmenes:"
echo "-----------------------------------------------------------"
docker inspect $CONTAINER --format='{{range .Mounts}}{{.Source}} -> {{.Destination}} ({{.Mode}}){{println}}{{end}}'
echo ""

echo "🌐 Probando acceso a archivos estáticos:"
echo "-----------------------------------------------------------"
echo "Probando /static/images/favicon.png..."
curl -I http://localhost:8000/static/images/favicon.png 2>/dev/null | head -n 1 || echo "❌ No se puede acceder"
echo ""

echo "Probando /static/css/main.css..."
curl -I http://localhost:8000/static/css/main.css 2>/dev/null | head -n 1 || echo "❌ No se puede acceder"
echo ""

echo "📋 Logs recientes del contenedor:"
echo "-----------------------------------------------------------"
docker logs $CONTAINER --tail 20
echo ""

echo "========================================="
echo "DIAGNÓSTICO COMPLETADO"
echo "========================================="
