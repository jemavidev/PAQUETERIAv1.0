#!/bin/bash
# Script para desplegar la corrección al servidor papyrus

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     DESPLIEGUE AL SERVIDOR PAPYRUS                            ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

SERVER="papyrus"
SERVER_PATH="/home/ubuntu/paqueteria"

echo -e "${BLUE}Servidor: $SERVER${NC}"
echo -e "${BLUE}Ruta: $SERVER_PATH${NC}"
echo ""

# Verificar conexión SSH
echo -e "${YELLOW}Paso 1: Verificando conexión SSH...${NC}"
if ! ssh $SERVER "echo 'Conexión exitosa'" 2>/dev/null; then
    echo -e "${RED}❌ No se pudo conectar al servidor${NC}"
    echo "Verifica que el alias 'papyrus' esté configurado en ~/.ssh/config"
    exit 1
fi
echo -e "${GREEN}✅ Conexión SSH exitosa${NC}"
echo ""

# Crear backup
echo -e "${YELLOW}Paso 2: Creando backup de configuración actual...${NC}"
ssh $SERVER "cd $SERVER_PATH && \
    mkdir -p backups && \
    cp docker-compose.lightsail.yml backups/docker-compose.lightsail.yml.backup-\$(date +%Y%m%d-%H%M%S) 2>/dev/null || true && \
    cp CODE/nginx/nginx.lightsail.conf backups/nginx.lightsail.conf.backup-\$(date +%Y%m%d-%H%M%S) 2>/dev/null || true"
echo -e "${GREEN}✅ Backup creado${NC}"
echo ""

# Subir archivos corregidos
echo -e "${YELLOW}Paso 3: Subiendo archivos corregidos...${NC}"
scp docker-compose.lightsail.yml $SERVER:$SERVER_PATH/
scp CODE/nginx/nginx.lightsail.conf $SERVER:$SERVER_PATH/CODE/nginx/
echo -e "${GREEN}✅ Archivos subidos${NC}"
echo ""

# Verificar archivos estáticos en el servidor
echo -e "${YELLOW}Paso 4: Verificando archivos estáticos en el servidor...${NC}"
ssh $SERVER "ls -lh $SERVER_PATH/CODE/src/static/images/"
echo ""

# Aplicar corrección
echo -e "${YELLOW}Paso 5: Aplicando corrección en el servidor...${NC}"
echo ""
echo -e "${CYAN}Deteniendo contenedores...${NC}"
ssh $SERVER "cd $SERVER_PATH && docker compose -f docker-compose.lightsail.yml down"

echo ""
echo -e "${CYAN}Iniciando contenedores con nueva configuración...${NC}"
ssh $SERVER "cd $SERVER_PATH && docker compose -f docker-compose.lightsail.yml up -d"

echo ""
echo -e "${CYAN}Esperando que la aplicación esté lista...${NC}"
sleep 15

echo ""
echo -e "${YELLOW}Paso 6: Verificando montajes en el servidor...${NC}"
CONTAINER=$(ssh $SERVER "docker ps --filter 'name=paqueteria_app' --format '{{.Names}}' | head -n 1")
echo -e "${GREEN}Contenedor: $CONTAINER${NC}"
echo ""
echo "Montajes actuales:"
ssh $SERVER "docker inspect $CONTAINER --format='{{range .Mounts}}{{.Destination}}{{println}}{{end}}' | grep -E 'app|static'"

echo ""
echo -e "${YELLOW}Paso 7: Probando acceso a archivos estáticos...${NC}"
sleep 5

# Obtener la IP del servidor
SERVER_IP=$(ssh $SERVER "curl -s ifconfig.me")
echo -e "${CYAN}IP del servidor: $SERVER_IP${NC}"
echo ""

# Probar acceso directo al puerto 8000
echo "Probando acceso directo (puerto 8000):"
echo -n "  Health check... "
HTTP_CODE=$(ssh $SERVER "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health")
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FALLO (HTTP $HTTP_CODE)${NC}"
fi

echo -n "  Favicon... "
HTTP_CODE=$(ssh $SERVER "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/static/images/favicon.png")
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ OK (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ FALLO (HTTP $HTTP_CODE)${NC}"
fi

echo -n "  Logo... "
HTTP_CODE=$(ssh $SERVER "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/static/images/logo.png")
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ OK (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ FALLO (HTTP $HTTP_CODE)${NC}"
fi

# Probar acceso a través de Nginx (puerto 80)
echo ""
echo "Probando acceso a través de Nginx (puerto 80):"
echo -n "  Health check... "
HTTP_CODE=$(ssh $SERVER "curl -s -o /dev/null -w '%{http_code}' http://localhost/health")
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FALLO (HTTP $HTTP_CODE)${NC}"
fi

echo -n "  Favicon... "
HTTP_CODE=$(ssh $SERVER "curl -s -o /dev/null -w '%{http_code}' http://localhost/static/images/favicon.png")
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ OK (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ FALLO (HTTP $HTTP_CODE)${NC}"
fi

echo -n "  Logo... "
HTTP_CODE=$(ssh $SERVER "curl -s -o /dev/null -w '%{http_code}' http://localhost/static/images/logo.png")
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ OK (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ FALLO (HTTP $HTTP_CODE)${NC}"
fi

echo ""
echo -e "${YELLOW}Paso 8: Verificando logs del servidor...${NC}"
echo "-------------------------------------------------------------------"
ssh $SERVER "docker logs $CONTAINER --tail 30" 2>&1 | tail -20
echo "-------------------------------------------------------------------"

echo ""
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     DESPLIEGUE COMPLETADO                                     ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}✅ La corrección ha sido aplicada en el servidor${NC}"
echo ""
echo "📝 Comandos útiles:"
echo ""
echo "  Ver logs en tiempo real:"
echo "    ssh $SERVER 'cd $SERVER_PATH && docker logs -f $CONTAINER'"
echo ""
echo "  Ver estado de contenedores:"
echo "    ssh $SERVER 'cd $SERVER_PATH && docker compose -f docker-compose.lightsail.yml ps'"
echo ""
echo "  Reiniciar aplicación:"
echo "    ssh $SERVER 'cd $SERVER_PATH && docker compose -f docker-compose.lightsail.yml restart app'"
echo ""
echo "🌐 URLs de acceso:"
echo "  Aplicación:  http://$SERVER_IP"
echo "  Health:      http://$SERVER_IP/health"
echo "  Favicon:     http://$SERVER_IP/static/images/favicon.png"
echo ""
echo "Verifica en el navegador que las imágenes se visualicen correctamente."
