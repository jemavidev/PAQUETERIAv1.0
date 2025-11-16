#!/bin/bash
# Script para resolver conflicto de puertos

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     RESOLVIENDO CONFLICTO DE PUERTOS                          ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

SERVER="papyrus"
SERVER_PATH="/home/ubuntu/paqueteria"

echo -e "${YELLOW}Problema detectado:${NC}"
echo "Los contenedores de producción están usando el puerto 8000"
echo ""

echo -e "${YELLOW}Paso 1: Deteniendo contenedores de producción...${NC}"
ssh $SERVER "cd $SERVER_PATH && docker compose -f docker-compose.prod.yml down" || true

echo ""
echo -e "${YELLOW}Paso 2: Limpiando contenedores huérfanos...${NC}"
ssh $SERVER "docker container prune -f"

echo ""
echo -e "${YELLOW}Paso 3: Iniciando contenedores de Lightsail...${NC}"
ssh $SERVER "cd $SERVER_PATH && docker compose -f docker-compose.lightsail.yml up -d"

echo ""
echo -e "${YELLOW}Paso 4: Esperando que la aplicación esté lista...${NC}"
sleep 15

echo ""
echo -e "${YELLOW}Paso 5: Verificando estado...${NC}"
CONTAINER=$(ssh $SERVER "docker ps --filter 'name=paqueteria_app' --format '{{.Names}}' | head -n 1")
echo -e "${GREEN}Contenedor activo: $CONTAINER${NC}"

echo ""
echo "Montajes actuales:"
ssh $SERVER "docker inspect $CONTAINER --format='{{range .Mounts}}{{.Destination}}{{println}}{{end}}' | grep -E 'app|static'"

echo ""
echo -e "${YELLOW}Paso 6: Probando acceso...${NC}"
sleep 5

echo -n "Health check... "
HTTP_CODE=$(ssh $SERVER "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health")
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FALLO (HTTP $HTTP_CODE)${NC}"
fi

echo -n "Favicon... "
HTTP_CODE=$(ssh $SERVER "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/static/images/favicon.png")
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ OK (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ FALLO (HTTP $HTTP_CODE)${NC}"
fi

echo -n "Logo... "
HTTP_CODE=$(ssh $SERVER "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/static/images/logo.png")
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ OK (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ FALLO (HTTP $HTTP_CODE)${NC}"
fi

echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     CORRECCIÓN COMPLETADA                                     ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

SERVER_IP=$(ssh $SERVER "curl -s ifconfig.me")
echo "🌐 Accede a la aplicación en: http://$SERVER_IP"
echo ""
echo "Verifica que las imágenes se visualicen correctamente en el navegador."
