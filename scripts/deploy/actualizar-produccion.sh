#!/bin/bash
# ========================================
# Script de Actualización en Producción
# ========================================
# Ejecutar este script EN EL SERVIDOR DE PRODUCCIÓN

echo "🚀 ACTUALIZACIÓN DE PRODUCCIÓN - TEMPLATES"
echo "=========================================="
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Hacer pull de los últimos cambios
echo -e "${BLUE}📥 Paso 1: Descargando últimos cambios desde GitHub...${NC}"
echo "--------------------------------------------------------"

git fetch origin main
git pull origin main

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ ERROR: No se pudo hacer pull desde GitHub${NC}"
    echo "Verifica tu conexión y permisos de Git"
    exit 1
fi

echo -e "${GREEN}✅ Cambios descargados correctamente${NC}"
echo ""

# 2. Verificar que los templates existen
echo -e "${BLUE}📁 Paso 2: Verificando templates...${NC}"
echo "-----------------------------------"

if [ ! -f "CODE/src/templates/general/terms.html" ]; then
    echo -e "${RED}❌ ERROR: terms.html no existe después del pull${NC}"
    exit 1
fi

if [ ! -f "CODE/src/templates/general/privacy.html" ]; then
    echo -e "${RED}❌ ERROR: privacy.html no existe después del pull${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Templates verificados${NC}"
echo ""

# 3. Verificar permisos
echo -e "${BLUE}🔐 Paso 3: Verificando permisos...${NC}"
echo "----------------------------------"

chmod 644 CODE/src/templates/general/terms.html
chmod 644 CODE/src/templates/general/privacy.html

echo -e "${GREEN}✅ Permisos configurados${NC}"
echo ""

# 4. Reiniciar contenedor
echo -e "${BLUE}🔄 Paso 4: Reiniciando contenedor de aplicación...${NC}"
echo "--------------------------------------------------"

docker compose -f docker-compose.prod.yml restart app

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ ERROR: No se pudo reiniciar el contenedor${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Contenedor reiniciado${NC}"
echo ""

# 5. Esperar que el contenedor esté listo
echo -e "${BLUE}⏳ Paso 5: Esperando que el contenedor esté listo...${NC}"
echo "---------------------------------------------------"

sleep 10

# Verificar health check
CONTAINER_NAME="paqueteria_v1_prod_app"
for i in {1..30}; do
    if docker inspect --format='{{.State.Health.Status}}' $CONTAINER_NAME 2>/dev/null | grep -q "healthy"; then
        echo -e "${GREEN}✅ Contenedor está saludable${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${YELLOW}⚠️  Timeout esperando health check (continuando de todas formas)${NC}"
    fi
    echo "Esperando health check... ($i/30)"
    sleep 2
done

echo ""

# 6. Verificar sincronización
echo -e "${BLUE}🔍 Paso 6: Verificando sincronización en contenedor...${NC}"
echo "-----------------------------------------------------"

if docker exec $CONTAINER_NAME test -f /app/src/templates/general/terms.html; then
    echo -e "${GREEN}✅ terms.html sincronizado${NC}"
else
    echo -e "${RED}❌ terms.html NO sincronizado${NC}"
fi

if docker exec $CONTAINER_NAME test -f /app/src/templates/general/privacy.html; then
    echo -e "${GREEN}✅ privacy.html sincronizado${NC}"
else
    echo -e "${RED}❌ privacy.html NO sincronizado${NC}"
fi

echo ""

# 7. Probar endpoints
echo -e "${BLUE}🌐 Paso 7: Probando endpoints...${NC}"
echo "--------------------------------"

echo "Probando /terms..."
TERMS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/terms)
if [ "$TERMS_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ /terms responde correctamente (200)${NC}"
else
    echo -e "${RED}❌ /terms responde con código: $TERMS_STATUS${NC}"
fi

echo "Probando /privacy..."
PRIVACY_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/privacy)
if [ "$PRIVACY_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ /privacy responde correctamente (200)${NC}"
else
    echo -e "${RED}❌ /privacy responde con código: $PRIVACY_STATUS${NC}"
fi

echo ""

# 8. Mostrar últimas líneas del log
echo -e "${BLUE}📋 Paso 8: Últimas líneas del log...${NC}"
echo "------------------------------------"
docker logs --tail 15 $CONTAINER_NAME

echo ""
echo "=========================================="
echo -e "${GREEN}✅ ACTUALIZACIÓN COMPLETADA${NC}"
echo "=========================================="
echo ""
echo "URLs disponibles:"
echo "  - http://localhost:8000/terms"
echo "  - http://localhost:8000/privacy"
echo "  - http://localhost:8000/help"
echo ""
echo "Si usas un dominio, reemplaza localhost:8000 con tu dominio"
echo ""
