#!/bin/bash
# ========================================
# SCRIPT DE SETUP AUTOMÁTICO PARA STAGING
# ========================================
# Este script configura staging en el servidor
# Ejecutar desde el servidor: ssh papyrus
# ========================================

set -e

echo "========================================="
echo "🚀 SETUP STAGING - PAQUETERÍA v1.0"
echo "========================================="
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Variables
STAGING_PATH="/home/ubuntu/paqueteria-staging"
REPO_URL="https://github.com/TU_USUARIO/TU_REPO.git"  # CAMBIAR ESTO
NGINX_CONF_SOURCE="$STAGING_PATH/.deploy/templates/nginx-staging.conf"
NGINX_CONF_DEST="/etc/nginx/sites-available/staging"

echo -e "${YELLOW}⚠️  IMPORTANTE: Edita este script y cambia REPO_URL${NC}"
echo ""
read -p "¿Has editado REPO_URL? (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}❌ Edita el script primero${NC}"
    exit 1
fi

# Paso 1: Clonar repositorio
echo -e "${GREEN}[1/5]${NC} Clonando repositorio en $STAGING_PATH..."
if [ -d "$STAGING_PATH" ]; then
    echo -e "${YELLOW}⚠️  El directorio ya existe${NC}"
    read -p "¿Eliminar y clonar de nuevo? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$STAGING_PATH"
        git clone "$REPO_URL" "$STAGING_PATH"
    fi
else
    git clone "$REPO_URL" "$STAGING_PATH"
fi

# Paso 2: Cambiar a rama staging
echo -e "${GREEN}[2/5]${NC} Cambiando a rama staging..."
cd "$STAGING_PATH"
git checkout staging || {
    echo -e "${RED}❌ Rama staging no existe. Créala primero.${NC}"
    exit 1
}

# Paso 3: Configurar Nginx
echo -e "${GREEN}[3/5]${NC} Configurando Nginx..."
if [ -f "$NGINX_CONF_SOURCE" ]; then
    sudo cp "$NGINX_CONF_SOURCE" "$NGINX_CONF_DEST"
    sudo ln -sf "$NGINX_CONF_DEST" /etc/nginx/sites-enabled/staging
    echo -e "${GREEN}✓${NC} Nginx configurado"
else
    echo -e "${RED}❌ No se encontró el archivo de configuración de Nginx${NC}"
    exit 1
fi

# Paso 4: Verificar Nginx
echo -e "${GREEN}[4/5]${NC} Verificando configuración de Nginx..."
sudo nginx -t
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Configuración de Nginx OK"
    sudo systemctl reload nginx
else
    echo -e "${RED}❌ Error en configuración de Nginx${NC}"
    exit 1
fi

# Paso 5: Abrir puertos en firewall
echo -e "${GREEN}[5/5]${NC} Configurando firewall..."
sudo ufw allow 8080/tcp comment 'Staging HTTP'
sudo ufw allow 8443/tcp comment 'Staging HTTPS'
echo -e "${GREEN}✓${NC} Puertos 8080 y 8443 abiertos"

echo ""
echo "========================================="
echo -e "${GREEN}✅ SETUP COMPLETADO${NC}"
echo "========================================="
echo ""
echo "Próximos pasos:"
echo "1. Desde tu máquina local, ejecuta:"
echo "   ./deploy.sh --env staging --deploy"
echo ""
echo "2. Verifica que funciona:"
echo "   curl http://staging.jemavi.co:8080/health"
echo ""
echo "3. (Opcional) Configura SSL:"
echo "   sudo certbot certonly --nginx -d staging.jemavi.co"
echo ""
