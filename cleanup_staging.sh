#!/bin/bash

# Script de limpieza para staging
# Fecha: 7 de diciembre de 2025

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              LIMPIEZA DE STAGING                               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}1. Deteniendo contenedores de staging...${NC}"
docker compose -f docker-compose.staging.yml down -v 2>&1

echo ""
echo -e "${BLUE}2. Verificando puertos ocupados...${NC}"

# Verificar puerto 6380 (Redis staging)
PORT_6380=$(sudo lsof -i :6380 2>/dev/null | grep docker-pr | awk '{print $2}')
if [ -n "$PORT_6380" ]; then
    echo -e "${YELLOW}⚠️  Puerto 6380 ocupado por procesos: $PORT_6380${NC}"
    echo -e "${BLUE}   Matando procesos...${NC}"
    echo "$PORT_6380" | xargs -r sudo kill -9
    echo -e "${GREEN}✓ Procesos eliminados${NC}"
else
    echo -e "${GREEN}✓ Puerto 6380 libre${NC}"
fi

# Verificar puerto 8001 (App staging)
PORT_8001=$(sudo lsof -i :8001 2>/dev/null | grep docker-pr | awk '{print $2}')
if [ -n "$PORT_8001" ]; then
    echo -e "${YELLOW}⚠️  Puerto 8001 ocupado por procesos: $PORT_8001${NC}"
    echo -e "${BLUE}   Matando procesos...${NC}"
    echo "$PORT_8001" | xargs -r sudo kill -9
    echo -e "${GREEN}✓ Procesos eliminados${NC}"
else
    echo -e "${GREEN}✓ Puerto 8001 libre${NC}"
fi

echo ""
echo -e "${BLUE}3. Limpiando contenedores huérfanos...${NC}"
docker container prune -f 2>&1 | grep -v "Total reclaimed space"

echo ""
echo -e "${BLUE}4. Limpiando redes huérfanas...${NC}"
docker network prune -f 2>&1 | grep -v "Total reclaimed space"

echo ""
echo -e "${BLUE}5. Limpiando volúmenes no usados (opcional)...${NC}"
read -p "¿Deseas limpiar volúmenes no usados? Esto eliminará datos persistentes. (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker volume prune -f 2>&1 | grep -v "Total reclaimed space"
    echo -e "${GREEN}✓ Volúmenes limpiados${NC}"
else
    echo -e "${YELLOW}⊘ Volúmenes no limpiados${NC}"
fi

echo ""
echo -e "${BLUE}6. Verificando estado final...${NC}"

# Verificar que no hay contenedores de staging corriendo
STAGING_CONTAINERS=$(docker ps -a | grep staging | wc -l)
if [ "$STAGING_CONTAINERS" -eq 0 ]; then
    echo -e "${GREEN}✓ No hay contenedores de staging${NC}"
else
    echo -e "${YELLOW}⚠️  Aún hay $STAGING_CONTAINERS contenedores de staging${NC}"
    docker ps -a | grep staging
fi

# Verificar puertos
if ! sudo lsof -i :6380 2>/dev/null | grep -q docker-pr && \
   ! sudo lsof -i :8001 2>/dev/null | grep -q docker-pr; then
    echo -e "${GREEN}✓ Puertos 6380 y 8001 libres${NC}"
else
    echo -e "${RED}❌ Algunos puertos aún están ocupados${NC}"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ LIMPIEZA COMPLETADA${NC}"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Ahora puedes ejecutar:"
echo "  docker compose -f docker-compose.staging.yml up -d"
echo ""
