#!/bin/bash
# Script para aplicar la corrección inmediatamente

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     APLICANDO CORRECCIÓN AHORA                                ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}Problema identificado:${NC}"
echo "El contenedor actual tiene un montaje redundante en /app/static"
echo "que debe ser eliminado."
echo ""

echo -e "${YELLOW}Solución:${NC}"
echo "Recrear el contenedor sin el montaje redundante."
echo ""

read -p "¿Deseas aplicar la corrección ahora? (s/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Operación cancelada"
    exit 0
fi

echo ""
echo -e "${BLUE}Paso 1: Deteniendo contenedores...${NC}"
docker compose -f docker-compose.prod.yml down

echo ""
echo -e "${BLUE}Paso 2: Iniciando contenedores con nueva configuración...${NC}"
docker compose -f docker-compose.prod.yml up -d

echo ""
echo -e "${BLUE}Paso 3: Esperando que la aplicación esté lista...${NC}"
sleep 10

echo ""
echo -e "${BLUE}Paso 4: Verificando montajes...${NC}"
CONTAINER=$(docker ps --filter "name=paqueteria_v1_prod_app" --format "{{.Names}}")
echo "Montajes actuales:"
docker inspect $CONTAINER --format='{{range .Mounts}}{{.Destination}}{{println}}{{end}}' | grep -E "app|static"

echo ""
echo -e "${BLUE}Paso 5: Probando acceso a archivos estáticos...${NC}"
sleep 5

echo ""
echo -n "Health check... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FALLO (HTTP $HTTP_CODE)${NC}"
fi

echo -n "Favicon... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/static/images/favicon.png)
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ OK (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ FALLO (HTTP $HTTP_CODE)${NC}"
fi

echo -n "Logo... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/static/images/logo.png)
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ OK (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ FALLO (HTTP $HTTP_CODE)${NC}"
fi

echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     CORRECCIÓN APLICADA                                       ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo "Verifica en el navegador que las imágenes se visualicen correctamente."
echo ""
echo "Si todo funciona localmente, aplica la misma corrección en el servidor:"
echo "  ./deploy-static-fix-to-server.sh"
