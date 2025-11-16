#!/bin/bash
# Script para sincronizar configuraciones entre localhost y servidor

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     SINCRONIZACIÓN DE CONFIGURACIONES                         ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}Este script sincroniza las configuraciones entre:${NC}"
echo "  - docker-compose.prod.yml (localhost)"
echo "  - docker-compose.lightsail.yml (servidor)"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.prod.yml" ] || [ ! -f "docker-compose.lightsail.yml" ]; then
    echo -e "${RED}❌ Error: No se encuentran los archivos docker-compose${NC}"
    exit 1
fi

echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}VERIFICACIÓN DE CONFIGURACIONES${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Verificar montajes de volúmenes en docker-compose.prod.yml
echo -e "${CYAN}Verificando docker-compose.prod.yml...${NC}"
if grep -q "./CODE/src/static:/app/static" docker-compose.prod.yml; then
    echo -e "${RED}❌ PROBLEMA: Montaje redundante encontrado en docker-compose.prod.yml${NC}"
    echo "   Línea problemática: ./CODE/src/static:/app/static"
    PROD_OK=false
else
    echo -e "${GREEN}✅ docker-compose.prod.yml está correcto${NC}"
    PROD_OK=true
fi

echo ""

# Verificar montajes de volúmenes en docker-compose.lightsail.yml
echo -e "${CYAN}Verificando docker-compose.lightsail.yml...${NC}"
if grep -q "./CODE/src/static:/app/static" docker-compose.lightsail.yml; then
    echo -e "${RED}❌ PROBLEMA: Montaje redundante encontrado en docker-compose.lightsail.yml${NC}"
    echo "   Línea problemática: ./CODE/src/static:/app/static"
    LIGHTSAIL_OK=false
else
    echo -e "${GREEN}✅ docker-compose.lightsail.yml está correcto${NC}"
    LIGHTSAIL_OK=true
fi

echo ""

# Verificar que ambos tengan el montaje correcto
echo -e "${CYAN}Verificando montajes correctos...${NC}"
if grep -q "./CODE/src:/app/src" docker-compose.prod.yml && \
   grep -q "./CODE/src:/app/src" docker-compose.lightsail.yml; then
    echo -e "${GREEN}✅ Ambos archivos tienen el montaje correcto: ./CODE/src:/app/src${NC}"
else
    echo -e "${RED}❌ PROBLEMA: Falta el montaje correcto en uno o ambos archivos${NC}"
fi

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}RESUMEN${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo ""

if [ "$PROD_OK" = true ] && [ "$LIGHTSAIL_OK" = true ]; then
    echo -e "${GREEN}✅ TODAS LAS CONFIGURACIONES ESTÁN CORRECTAS${NC}"
    echo ""
    echo "Ambos archivos están sincronizados y no tienen montajes redundantes."
    echo "Puedes desplegar al servidor sin problemas."
else
    echo -e "${RED}❌ HAY PROBLEMAS EN LAS CONFIGURACIONES${NC}"
    echo ""
    echo "Necesitas corregir los archivos antes de desplegar."
    echo ""
    echo "Para corregir automáticamente, ejecuta:"
    echo "  sed -i '/\\.\/CODE\/src\/static:\\/app\\/static/d' docker-compose.prod.yml"
    echo "  sed -i '/\\.\/CODE\/src\/static:\\/app\\/static/d' docker-compose.lightsail.yml"
fi

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}CONFIGURACIÓN CORRECTA${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo "Los volúmenes deben estar configurados así:"
echo ""
echo -e "${GREEN}✅ CORRECTO:${NC}"
echo "  volumes:"
echo "    - ./CODE/src:/app/src"
echo "    - uploads_data:/app/uploads"
echo "    - logs_data:/app/logs"
echo ""
echo -e "${RED}❌ INCORRECTO:${NC}"
echo "  volumes:"
echo "    - ./CODE/src:/app/src"
echo "    - ./CODE/src/static:/app/static  ← NO DEBE EXISTIR"
echo "    - uploads_data:/app/uploads"
echo ""

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Verificación completada${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
