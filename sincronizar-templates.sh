#!/bin/bash
# ========================================
# Script de Sincronización de Templates
# ========================================

echo "🔄 SINCRONIZACIÓN DE TEMPLATES DE TÉRMINOS Y PRIVACIDAD"
echo "========================================================"
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

CONTAINER_NAME="paqueteria_v1_prod_app"

# 1. Verificar que los archivos existen en el host
echo -e "${BLUE}📁 Paso 1: Verificando archivos en el host...${NC}"
echo "----------------------------------------------"

FILES_OK=true

if [ ! -f "CODE/src/templates/general/terms.html" ]; then
    echo -e "${RED}❌ ERROR: terms.html no existe en el host${NC}"
    FILES_OK=false
fi

if [ ! -f "CODE/src/templates/general/privacy.html" ]; then
    echo -e "${RED}❌ ERROR: privacy.html no existe en el host${NC}"
    FILES_OK=false
fi

if [ "$FILES_OK" = false ]; then
    echo -e "${RED}❌ Los archivos no existen. Abortando.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Archivos verificados en el host${NC}"
echo ""

# 2. Verificar que el contenedor está corriendo
echo -e "${BLUE}🐳 Paso 2: Verificando contenedor...${NC}"
echo "------------------------------------"

if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo -e "${YELLOW}⚠️  Contenedor no está corriendo. Iniciando...${NC}"
    docker compose -f docker-compose.prod.yml up -d app
    sleep 5
fi

if docker ps | grep -q "$CONTAINER_NAME"; then
    echo -e "${GREEN}✅ Contenedor está corriendo${NC}"
else
    echo -e "${RED}❌ ERROR: No se pudo iniciar el contenedor${NC}"
    exit 1
fi

echo ""

# 3. Reiniciar el contenedor para forzar sincronización
echo -e "${BLUE}🔄 Paso 3: Reiniciando contenedor...${NC}"
echo "------------------------------------"

echo "Reiniciando $CONTAINER_NAME..."
docker compose -f docker-compose.prod.yml restart app

echo "Esperando que el contenedor esté listo..."
sleep 10

# Verificar health check
for i in {1..30}; do
    if docker inspect --format='{{.State.Health.Status}}' $CONTAINER_NAME 2>/dev/null | grep -q "healthy"; then
        echo -e "${GREEN}✅ Contenedor está saludable${NC}"
        break
    fi
    echo "Esperando health check... ($i/30)"
    sleep 2
done

echo ""

# 4. Verificar que los archivos están sincronizados
echo -e "${BLUE}🔍 Paso 4: Verificando sincronización...${NC}"
echo "----------------------------------------"

SYNC_OK=true

if docker exec $CONTAINER_NAME test -f /app/src/templates/general/terms.html; then
    echo -e "${GREEN}✅ terms.html sincronizado en el contenedor${NC}"
else
    echo -e "${RED}❌ terms.html NO está en el contenedor${NC}"
    SYNC_OK=false
fi

if docker exec $CONTAINER_NAME test -f /app/src/templates/general/privacy.html; then
    echo -e "${GREEN}✅ privacy.html sincronizado en el contenedor${NC}"
else
    echo -e "${RED}❌ privacy.html NO está en el contenedor${NC}"
    SYNC_OK=false
fi

if [ "$SYNC_OK" = false ]; then
    echo -e "${RED}❌ ERROR: Los archivos no se sincronizaron correctamente${NC}"
    echo ""
    echo "Posibles soluciones:"
    echo "1. Verificar que el volumen está montado correctamente en docker-compose.prod.yml"
    echo "2. Verificar permisos de archivos: chmod 644 CODE/src/templates/general/*.html"
    echo "3. Reconstruir el contenedor: docker compose -f docker-compose.prod.yml up -d --build app"
    exit 1
fi

echo ""

# 5. Probar los endpoints
echo -e "${BLUE}🌐 Paso 5: Probando endpoints...${NC}"
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

# 6. Ver logs del contenedor
echo -e "${BLUE}📋 Paso 6: Últimas líneas del log...${NC}"
echo "------------------------------------"
docker logs --tail 20 $CONTAINER_NAME

echo ""
echo "========================================================"
echo -e "${GREEN}✅ Sincronización completada${NC}"
echo "========================================================"
echo ""
echo "URLs disponibles:"
echo "  - http://localhost:8000/terms"
echo "  - http://localhost:8000/privacy"
echo "  - http://localhost:8000/help"
echo ""
