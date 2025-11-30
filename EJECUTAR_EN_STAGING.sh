#!/bin/bash
# ============================================
# Script para ejecutar en el servidor staging
# Copia y pega este contenido en tu terminal
# ============================================

echo "🚀 INICIANDO DIAGNÓSTICO Y FIX DEL PORTAL DE CLIENTES"
echo "======================================================"
echo ""

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Verificar que estamos en el directorio correcto
echo "📁 Verificando directorio..."
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ Error: No se encuentra docker-compose.yml${NC}"
    echo "   Por favor, navega al directorio del proyecto"
    exit 1
fi
echo -e "${GREEN}✅ Directorio correcto${NC}"
echo ""

# 2. Verificar que los contenedores estén corriendo
echo "🐳 Verificando contenedores Docker..."
if ! docker-compose ps | grep -q "Up"; then
    echo -e "${RED}❌ Error: Los contenedores no están corriendo${NC}"
    echo "   Ejecuta: docker-compose up -d"
    exit 1
fi
echo -e "${GREEN}✅ Contenedores corriendo${NC}"
echo ""

# 3. Verificar configuración de rutas
echo "🔍 PASO 1: Verificando configuración de rutas..."
echo "------------------------------------------------------"
docker-compose exec -T web python debug_routes.py
ROUTES_CHECK=$?

if [ $ROUTES_CHECK -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Advertencia: Hay problemas en la configuración de rutas${NC}"
else
    echo -e "${GREEN}✅ Configuración de rutas correcta${NC}"
fi
echo ""

# 4. Reiniciar el servidor
echo "🔄 PASO 2: Reiniciando servidor web..."
echo "------------------------------------------------------"
docker-compose restart web

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Servidor reiniciado exitosamente${NC}"
else
    echo -e "${RED}❌ Error al reiniciar el servidor${NC}"
    exit 1
fi
echo ""

# 5. Esperar a que el servidor esté listo
echo "⏳ Esperando que el servidor esté listo..."
sleep 5
echo ""

# 6. Verificar que el servidor esté corriendo
echo "🔍 PASO 3: Verificando estado del servidor..."
echo "------------------------------------------------------"
docker-compose ps web
echo ""

# 7. Verificar logs recientes
echo "📋 Últimos logs del servidor:"
echo "------------------------------------------------------"
docker-compose logs --tail=30 web | grep -E "Started|Uvicorn|Application startup"
echo ""

# 8. Probar la ruta del portal
echo "🧪 PASO 4: Probando acceso al portal..."
echo "------------------------------------------------------"

# Probar con curl si está disponible
if command -v curl &> /dev/null; then
    echo "Probando: https://staging.jemavi.co/customer-portal"
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" https://staging.jemavi.co/customer-portal)
    
    if [ "$RESPONSE" = "200" ]; then
        echo -e "${GREEN}✅ Portal accesible (HTTP $RESPONSE)${NC}"
    elif [ "$RESPONSE" = "302" ] || [ "$RESPONSE" = "301" ]; then
        echo -e "${RED}❌ Portal redirige (HTTP $RESPONSE) - Aún hay problema${NC}"
        echo "   Verificando a dónde redirige..."
        curl -sI https://staging.jemavi.co/customer-portal | grep -i location
    else
        echo -e "${YELLOW}⚠️  Respuesta inesperada (HTTP $RESPONSE)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  curl no disponible, prueba manual en el navegador${NC}"
fi
echo ""

# 9. Resumen final
echo "======================================================"
echo "✅ PROCESO COMPLETADO"
echo "======================================================"
echo ""
echo "🧪 Prueba ahora en tu navegador:"
echo "   https://staging.jemavi.co/customer-portal"
echo ""
echo "📋 Si aún hay problemas:"
echo "   1. Limpia caché del navegador (Ctrl+Shift+Del)"
echo "   2. Prueba en ventana privada/incógnito"
echo "   3. Verifica logs: docker-compose logs -f web | grep customer-portal"
echo ""
echo "🔧 Comandos útiles:"
echo "   Ver logs en tiempo real:"
echo "   → docker-compose logs -f web"
echo ""
echo "   Verificar rutas nuevamente:"
echo "   → docker-compose exec web python debug_routes.py"
echo ""
echo "   Rebuild completo (si nada funciona):"
echo "   → docker-compose down && docker-compose up -d --build"
echo ""
