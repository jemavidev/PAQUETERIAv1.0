#!/bin/bash
# Script para corregir el problema de archivos estáticos

set -e

echo "========================================="
echo "CORRECCIÓN DE ARCHIVOS ESTÁTICOS"
echo "========================================="
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar si estamos en el directorio correcto
if [ ! -f "docker-compose.lightsail.yml" ]; then
    echo -e "${RED}❌ Error: No se encuentra docker-compose.lightsail.yml${NC}"
    echo "Por favor, ejecuta este script desde el directorio raíz del proyecto"
    exit 1
fi

echo -e "${YELLOW}📋 Paso 1: Verificando archivos estáticos locales...${NC}"
if [ ! -d "CODE/src/static/images" ]; then
    echo -e "${RED}❌ Error: No existe el directorio CODE/src/static/images${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Archivos estáticos encontrados:${NC}"
ls -lh CODE/src/static/images/

echo ""
echo -e "${YELLOW}📋 Paso 2: Deteniendo contenedores...${NC}"
docker compose -f docker-compose.lightsail.yml down

echo ""
echo -e "${YELLOW}📋 Paso 3: Reconstruyendo imagen con nueva configuración...${NC}"
docker compose -f docker-compose.lightsail.yml build --no-cache app

echo ""
echo -e "${YELLOW}📋 Paso 4: Iniciando contenedores...${NC}"
docker compose -f docker-compose.lightsail.yml up -d

echo ""
echo -e "${YELLOW}📋 Paso 5: Esperando que la aplicación esté lista...${NC}"
sleep 10

echo ""
echo -e "${YELLOW}📋 Paso 6: Verificando estructura de directorios en el contenedor...${NC}"
CONTAINER=$(docker ps --filter "name=paqueteria_app" --format "{{.Names}}" | head -n 1)

if [ -z "$CONTAINER" ]; then
    echo -e "${RED}❌ No se encontró el contenedor de la aplicación${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Contenedor: $CONTAINER${NC}"
echo ""

echo "Verificando /app/src/static/images/:"
docker exec $CONTAINER ls -lh /app/src/static/images/ || echo -e "${RED}❌ No existe${NC}"

echo ""
echo -e "${YELLOW}📋 Paso 7: Probando acceso a archivos estáticos...${NC}"
echo "Esperando 5 segundos más..."
sleep 5

echo ""
echo "Probando favicon.png:"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/static/images/favicon.png)
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ favicon.png accesible (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ favicon.png no accesible (HTTP $HTTP_CODE)${NC}"
fi

echo ""
echo "Probando logo.png:"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/static/images/logo.png)
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ logo.png accesible (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ logo.png no accesible (HTTP $HTTP_CODE)${NC}"
fi

echo ""
echo "Probando main.css:"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/static/css/main.css)
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ main.css accesible (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ main.css no accesible (HTTP $HTTP_CODE)${NC}"
fi

echo ""
echo -e "${YELLOW}📋 Paso 8: Verificando logs del contenedor...${NC}"
docker logs $CONTAINER --tail 30

echo ""
echo "========================================="
echo -e "${GREEN}✅ CORRECCIÓN COMPLETADA${NC}"
echo "========================================="
echo ""
echo "Si las imágenes aún no se ven, verifica:"
echo "1. Que Nginx esté configurado correctamente"
echo "2. Que las rutas en los templates sean correctas"
echo "3. Los logs del navegador (F12 -> Console)"
echo ""
echo "Para ver los logs en tiempo real:"
echo "  docker logs -f $CONTAINER"
