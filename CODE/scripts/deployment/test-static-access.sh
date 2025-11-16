#!/bin/bash
# Script para probar acceso a archivos estáticos

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     TEST DE ACCESO A ARCHIVOS ESTÁTICOS                       ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Solicitar información
read -p "Ingresa la IP del servidor (o 'local' para localhost): " SERVER_IP
if [ "$SERVER_IP" = "local" ]; then
    SERVER_IP="localhost"
    IS_LOCAL=true
else
    IS_LOCAL=false
    read -p "Ingresa el usuario SSH (default: ubuntu): " SSH_USER
    SSH_USER=${SSH_USER:-ubuntu}
fi

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}TEST 1: Acceso directo al puerto 8000 (FastAPI)${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo ""

test_direct() {
    local url=$1
    local name=$2
    
    echo -n "  $name... "
    
    if [ "$IS_LOCAL" = true ]; then
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
        CONTENT_TYPE=$(curl -s -I "$url" 2>/dev/null | grep -i "content-type" | cut -d' ' -f2-)
    else
        HTTP_CODE=$(ssh $SSH_USER@$SERVER_IP "curl -s -o /dev/null -w '%{http_code}' '$url'" 2>/dev/null)
        CONTENT_TYPE=$(ssh $SSH_USER@$SERVER_IP "curl -s -I '$url' | grep -i 'content-type' | cut -d' ' -f2-" 2>/dev/null)
    fi
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✅ OK (HTTP $HTTP_CODE) - $CONTENT_TYPE${NC}"
    else
        echo -e "${RED}❌ FALLO (HTTP $HTTP_CODE)${NC}"
    fi
}

echo "Probando acceso directo a FastAPI (puerto 8000):"
test_direct "http://$SERVER_IP:8000/health" "Health Check"
test_direct "http://$SERVER_IP:8000/static/images/favicon.png" "Favicon"
test_direct "http://$SERVER_IP:8000/static/images/logo.png" "Logo"
test_direct "http://$SERVER_IP:8000/static/css/main.css" "CSS"

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}TEST 2: Acceso a través de Nginx (puerto 80)${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo "Probando acceso a través de Nginx (puerto 80):"
test_direct "http://$SERVER_IP/health" "Health Check"
test_direct "http://$SERVER_IP/static/images/favicon.png" "Favicon"
test_direct "http://$SERVER_IP/static/images/logo.png" "Logo"
test_direct "http://$SERVER_IP/static/css/main.css" "CSS"

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}TEST 3: Verificación desde dentro del contenedor${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo ""

if [ "$IS_LOCAL" = true ]; then
    CONTAINER=$(docker ps --filter "name=paqueteria" --format "{{.Names}}" | grep -i app | head -n 1)
else
    CONTAINER=$(ssh $SSH_USER@$SERVER_IP "docker ps --filter 'name=paqueteria' --format '{{.Names}}' | grep -i app | head -n 1")
fi

if [ -z "$CONTAINER" ]; then
    echo -e "${RED}❌ No se encontró el contenedor${NC}"
else
    echo -e "${GREEN}✅ Contenedor: $CONTAINER${NC}"
    echo ""
    
    echo "Verificando archivos en el contenedor:"
    
    if [ "$IS_LOCAL" = true ]; then
        echo -n "  /app/src/static/images/favicon.png... "
        if docker exec $CONTAINER test -f /app/src/static/images/favicon.png 2>/dev/null; then
            SIZE=$(docker exec $CONTAINER du -h /app/src/static/images/favicon.png 2>/dev/null | cut -f1)
            echo -e "${GREEN}✅ Existe ($SIZE)${NC}"
        else
            echo -e "${RED}❌ No existe${NC}"
        fi
        
        echo -n "  /app/src/static/images/logo.png... "
        if docker exec $CONTAINER test -f /app/src/static/images/logo.png 2>/dev/null; then
            SIZE=$(docker exec $CONTAINER du -h /app/src/static/images/logo.png 2>/dev/null | cut -f1)
            echo -e "${GREEN}✅ Existe ($SIZE)${NC}"
        else
            echo -e "${RED}❌ No existe${NC}"
        fi
        
        echo ""
        echo "Probando curl desde dentro del contenedor:"
        echo -n "  http://localhost:8000/static/images/favicon.png... "
        RESULT=$(docker exec $CONTAINER curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/static/images/favicon.png 2>/dev/null)
        if [ "$RESULT" = "200" ]; then
            echo -e "${GREEN}✅ OK (HTTP $RESULT)${NC}"
        else
            echo -e "${RED}❌ FALLO (HTTP $RESULT)${NC}"
        fi
    else
        echo -n "  /app/src/static/images/favicon.png... "
        if ssh $SSH_USER@$SERVER_IP "docker exec $CONTAINER test -f /app/src/static/images/favicon.png" 2>/dev/null; then
            SIZE=$(ssh $SSH_USER@$SERVER_IP "docker exec $CONTAINER du -h /app/src/static/images/favicon.png" 2>/dev/null | cut -f1)
            echo -e "${GREEN}✅ Existe ($SIZE)${NC}"
        else
            echo -e "${RED}❌ No existe${NC}"
        fi
        
        echo -n "  /app/src/static/images/logo.png... "
        if ssh $SSH_USER@$SERVER_IP "docker exec $CONTAINER test -f /app/src/static/images/logo.png" 2>/dev/null; then
            SIZE=$(ssh $SSH_USER@$SERVER_IP "docker exec $CONTAINER du -h /app/src/static/images/logo.png" 2>/dev/null | cut -f1)
            echo -e "${GREEN}✅ Existe ($SIZE)${NC}"
        else
            echo -e "${RED}❌ No existe${NC}"
        fi
        
        echo ""
        echo "Probando curl desde dentro del contenedor:"
        echo -n "  http://localhost:8000/static/images/favicon.png... "
        RESULT=$(ssh $SSH_USER@$SERVER_IP "docker exec $CONTAINER curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/static/images/favicon.png" 2>/dev/null)
        if [ "$RESULT" = "200" ]; then
            echo -e "${GREEN}✅ OK (HTTP $RESULT)${NC}"
        else
            echo -e "${RED}❌ FALLO (HTTP $RESULT)${NC}"
        fi
    fi
fi

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}TEST 4: Verificación de logs${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo ""

if [ ! -z "$CONTAINER" ]; then
    echo "Últimas líneas de logs (buscando errores de static):"
    echo "-------------------------------------------------------------------"
    if [ "$IS_LOCAL" = true ]; then
        docker logs $CONTAINER --tail 50 2>&1 | grep -i "static\|404\|error" | tail -20 || echo "No se encontraron errores relacionados"
    else
        ssh $SSH_USER@$SERVER_IP "docker logs $CONTAINER --tail 50 2>&1 | grep -i 'static\|404\|error' | tail -20" || echo "No se encontraron errores relacionados"
    fi
    echo "-------------------------------------------------------------------"
fi

echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     RESUMEN                                                   ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Si el acceso directo al puerto 8000 funciona pero el puerto 80 no:"
echo "  → El problema está en Nginx"
echo ""
echo "Si el acceso desde dentro del contenedor funciona pero desde fuera no:"
echo "  → El problema está en el firewall o puertos"
echo ""
echo "Si los archivos no existen en el contenedor:"
echo "  → El problema está en los volúmenes de Docker"
echo ""
echo "Si los archivos existen pero FastAPI retorna 404:"
echo "  → El problema está en la configuración de FastAPI"
echo ""
