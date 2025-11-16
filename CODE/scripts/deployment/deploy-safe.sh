#!/bin/bash
# Script de despliegue seguro con verificación previa

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     DESPLIEGUE SEGURO AL SERVIDOR                             ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Paso 1: Verificar configuración local
echo -e "${YELLOW}Paso 1: Verificando configuración local...${NC}"
if ! ./CODE/scripts/deployment/sync-configs.sh | grep -q "TODAS LAS CONFIGURACIONES ESTÁN CORRECTAS"; then
    echo -e "${RED}❌ Error: La configuración local tiene problemas${NC}"
    echo "Ejecuta './CODE/scripts/deployment/sync-configs.sh' para ver los detalles"
    exit 1
fi
echo -e "${GREEN}✅ Configuración local correcta${NC}"
echo ""

# Paso 2: Verificar que funciona en localhost
echo -e "${YELLOW}Paso 2: Verificando que la aplicación funciona en localhost...${NC}"
if ! docker ps | grep -q "paqueteria_v1_prod_app"; then
    echo -e "${YELLOW}⚠️  Los contenedores no están corriendo en localhost${NC}"
    read -p "¿Deseas iniciarlos ahora? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        docker compose -f docker-compose.prod.yml up -d
        sleep 10
    else
        echo -e "${RED}❌ Despliegue cancelado${NC}"
        exit 1
    fi
fi

# Probar acceso local
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health | grep -q "200"; then
    echo -e "${GREEN}✅ Aplicación funciona correctamente en localhost${NC}"
else
    echo -e "${RED}❌ Error: La aplicación no responde en localhost${NC}"
    exit 1
fi
echo ""

# Paso 3: Confirmar despliegue
echo -e "${YELLOW}Paso 3: Confirmación de despliegue${NC}"
echo ""
echo "Estás a punto de desplegar al servidor de producción:"
echo "  Servidor: papyrus (paquetex.papyrus.com.co)"
echo "  Archivo: docker-compose.prod.yml"
echo ""
read -p "¿Deseas continuar? (s/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo -e "${YELLOW}Despliegue cancelado${NC}"
    exit 0
fi
echo ""

# Paso 4: Crear backup en el servidor
echo -e "${YELLOW}Paso 4: Creando backup en el servidor...${NC}"
ssh papyrus "cd /home/ubuntu/paqueteria && \
    mkdir -p backups && \
    cp docker-compose.prod.yml backups/docker-compose.prod.yml.backup-\$(date +%Y%m%d-%H%M%S) 2>/dev/null || true"
echo -e "${GREEN}✅ Backup creado${NC}"
echo ""

# Paso 5: Subir archivos
echo -e "${YELLOW}Paso 5: Subiendo archivos al servidor...${NC}"
scp docker-compose.prod.yml papyrus:/home/ubuntu/paqueteria/
echo -e "${GREEN}✅ Archivos subidos${NC}"
echo ""

# Paso 6: Desplegar
echo -e "${YELLOW}Paso 6: Desplegando en el servidor...${NC}"
ssh papyrus "cd /home/ubuntu/paqueteria && \
    docker compose -f docker-compose.prod.yml down && \
    docker compose -f docker-compose.prod.yml up -d"
echo -e "${GREEN}✅ Contenedores desplegados${NC}"
echo ""

# Paso 7: Esperar y verificar
echo -e "${YELLOW}Paso 7: Esperando que la aplicación esté lista...${NC}"
sleep 15

# Paso 8: Verificar que funciona
echo -e "${YELLOW}Paso 8: Verificando que la aplicación funciona...${NC}"
echo ""

# Health check
echo -n "  Health check... "
if curl -s https://paquetex.papyrus.com.co/health | grep -q "healthy"; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FALLO${NC}"
fi

# Favicon
echo -n "  Favicon... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://paquetex.papyrus.com.co/static/images/favicon.png)
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ OK (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ FALLO (HTTP $HTTP_CODE)${NC}"
fi

# Logo
echo -n "  Logo... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://paquetex.papyrus.com.co/static/images/logo.png)
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ OK (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ FALLO (HTTP $HTTP_CODE)${NC}"
fi

echo ""
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     DESPLIEGUE COMPLETADO                                     ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}✅ La aplicación ha sido desplegada exitosamente${NC}"
echo ""
echo "🌐 URL: https://paquetex.papyrus.com.co"
echo ""
echo "📝 Comandos útiles:"
echo "  Ver logs:      ssh papyrus 'docker logs -f paqueteria_v1_prod_app'"
echo "  Ver estado:    ssh papyrus 'docker ps'"
echo "  Reiniciar:     ssh papyrus 'cd /home/ubuntu/paqueteria && docker compose -f docker-compose.prod.yml restart app'"
