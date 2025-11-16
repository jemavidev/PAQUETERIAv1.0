#!/bin/bash
# Script para desplegar la corrección de archivos estáticos en el servidor remoto

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================="
echo "DESPLIEGUE DE CORRECCIÓN AL SERVIDOR"
echo "========================================="
echo ""

# Configuración del servidor (ajusta estos valores)
read -p "Ingresa la IP del servidor: " SERVER_IP
read -p "Ingresa el usuario SSH (default: ubuntu): " SSH_USER
SSH_USER=${SSH_USER:-ubuntu}

SERVER_PATH="/home/$SSH_USER/paqueteria"

echo ""
echo -e "${BLUE}Configuración:${NC}"
echo "  Servidor: $SSH_USER@$SERVER_IP"
echo "  Ruta: $SERVER_PATH"
echo ""

read -p "¿Es correcta esta configuración? (s/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Operación cancelada"
    exit 1
fi

echo ""
echo -e "${YELLOW}📋 Paso 1: Verificando conexión SSH...${NC}"
if ! ssh -o ConnectTimeout=5 $SSH_USER@$SERVER_IP "echo 'Conexión exitosa'"; then
    echo -e "${RED}❌ No se pudo conectar al servidor${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Conexión SSH exitosa${NC}"
echo ""

echo -e "${YELLOW}📋 Paso 2: Creando backup de configuración actual...${NC}"
ssh $SSH_USER@$SERVER_IP "cd $SERVER_PATH && \
    mkdir -p backups && \
    cp docker-compose.lightsail.yml backups/docker-compose.lightsail.yml.backup-\$(date +%Y%m%d-%H%M%S) && \
    cp CODE/nginx/nginx.lightsail.conf backups/nginx.lightsail.conf.backup-\$(date +%Y%m%d-%H%M%S)"
echo -e "${GREEN}✅ Backup creado${NC}"
echo ""

echo -e "${YELLOW}📋 Paso 3: Subiendo archivos corregidos...${NC}"
scp docker-compose.lightsail.yml $SSH_USER@$SERVER_IP:$SERVER_PATH/
scp CODE/nginx/nginx.lightsail.conf $SSH_USER@$SERVER_IP:$SERVER_PATH/CODE/nginx/
scp CODE/scripts/deployment/redeploy-with-static-fix.sh $SSH_USER@$SERVER_IP:$SERVER_PATH/CODE/scripts/deployment/
scp CODE/scripts/deployment/diagnose-static-files.sh $SSH_USER@$SERVER_IP:$SERVER_PATH/CODE/scripts/deployment/
echo -e "${GREEN}✅ Archivos subidos${NC}"
echo ""

echo -e "${YELLOW}📋 Paso 4: Verificando archivos estáticos en el servidor...${NC}"
ssh $SSH_USER@$SERVER_IP "cd $SERVER_PATH && ls -lh CODE/src/static/images/"
echo ""

echo -e "${YELLOW}📋 Paso 5: Aplicando corrección en el servidor...${NC}"
echo ""
read -p "¿Deseas aplicar la corrección ahora? (s/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo ""
    echo -e "${BLUE}Ejecutando redespliegue en el servidor...${NC}"
    echo "----------------------------------------"
    ssh -t $SSH_USER@$SERVER_IP "cd $SERVER_PATH && chmod +x CODE/scripts/deployment/redeploy-with-static-fix.sh && ./CODE/scripts/deployment/redeploy-with-static-fix.sh"
    echo "----------------------------------------"
    echo ""
    echo -e "${GREEN}✅ Redespliegue completado${NC}"
else
    echo ""
    echo -e "${YELLOW}⚠️  Corrección NO aplicada${NC}"
    echo "Para aplicarla manualmente, conéctate al servidor y ejecuta:"
    echo "  ssh $SSH_USER@$SERVER_IP"
    echo "  cd $SERVER_PATH"
    echo "  ./CODE/scripts/deployment/redeploy-with-static-fix.sh"
fi

echo ""
echo -e "${YELLOW}📋 Paso 6: Verificando estado del servidor...${NC}"
echo ""

# Verificar que los contenedores estén corriendo
echo "Estado de contenedores:"
ssh $SSH_USER@$SERVER_IP "cd $SERVER_PATH && docker compose -f docker-compose.lightsail.yml ps"
echo ""

# Obtener la IP pública si es posible
echo -e "${BLUE}Probando acceso a archivos estáticos...${NC}"
echo ""

# Probar health check
echo "Health check:"
if curl -s -o /dev/null -w "%{http_code}" http://$SERVER_IP:8000/health | grep -q "200"; then
    echo -e "${GREEN}✅ Health check OK${NC}"
else
    echo -e "${RED}❌ Health check falló${NC}"
fi

# Probar favicon
echo "Favicon:"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://$SERVER_IP:8000/static/images/favicon.png)
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Favicon accesible (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ Favicon no accesible (HTTP $HTTP_CODE)${NC}"
fi

# Probar logo
echo "Logo:"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://$SERVER_IP:8000/static/images/logo.png)
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Logo accesible (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ Logo no accesible (HTTP $HTTP_CODE)${NC}"
fi

echo ""
echo "========================================="
echo -e "${GREEN}✅ PROCESO COMPLETADO${NC}"
echo "========================================="
echo ""
echo "📝 Comandos útiles para el servidor:"
echo ""
echo "  Conectarse al servidor:"
echo "    ssh $SSH_USER@$SERVER_IP"
echo ""
echo "  Ver logs en tiempo real:"
echo "    ssh $SSH_USER@$SERVER_IP 'cd $SERVER_PATH && docker logs -f paqueteria_app'"
echo ""
echo "  Ejecutar diagnóstico:"
echo "    ssh $SSH_USER@$SERVER_IP 'cd $SERVER_PATH && ./CODE/scripts/deployment/diagnose-static-files.sh'"
echo ""
echo "  Reiniciar aplicación:"
echo "    ssh $SSH_USER@$SERVER_IP 'cd $SERVER_PATH && docker compose -f docker-compose.lightsail.yml restart app'"
echo ""
echo "🌐 URLs de acceso:"
echo "  Aplicación:  http://$SERVER_IP:8000"
echo "  Health:      http://$SERVER_IP:8000/health"
echo "  Favicon:     http://$SERVER_IP:8000/static/images/favicon.png"
echo ""

# Mostrar logs recientes si hay errores
if [ "$HTTP_CODE" != "200" ]; then
    echo ""
    echo -e "${YELLOW}⚠️  Algunos archivos no son accesibles${NC}"
    echo ""
    read -p "¿Deseas ver los logs del servidor? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        echo ""
        echo "Logs recientes:"
        echo "----------------------------------------"
        ssh $SSH_USER@$SERVER_IP "cd $SERVER_PATH && docker logs paqueteria_app --tail 50"
        echo "----------------------------------------"
    fi
fi
