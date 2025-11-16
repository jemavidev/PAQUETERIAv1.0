#!/bin/bash
# Script de diagnóstico profundo para el servidor

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║         DIAGNÓSTICO PROFUNDO DEL SERVIDOR                     ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Solicitar información del servidor
read -p "Ingresa la IP del servidor (o 'local' para localhost): " SERVER_IP
if [ "$SERVER_IP" = "local" ]; then
    SERVER_IP="localhost"
    SSH_PREFIX=""
    echo -e "${BLUE}Modo: LOCAL${NC}"
else
    read -p "Ingresa el usuario SSH (default: ubuntu): " SSH_USER
    SSH_USER=${SSH_USER:-ubuntu}
    SSH_PREFIX="ssh $SSH_USER@$SERVER_IP"
    echo -e "${BLUE}Modo: REMOTO ($SSH_USER@$SERVER_IP)${NC}"
fi

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}1. VERIFICANDO CONTENEDORES${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"

if [ -z "$SSH_PREFIX" ]; then
    CONTAINER=$(docker ps --filter "name=paqueteria" --format "{{.Names}}" | grep -i app | head -n 1)
else
    CONTAINER=$($SSH_PREFIX "docker ps --filter 'name=paqueteria' --format '{{.Names}}' | grep -i app | head -n 1")
fi

if [ -z "$CONTAINER" ]; then
    echo -e "${RED}❌ No se encontró el contenedor de la aplicación${NC}"
    echo ""
    echo "Contenedores activos:"
    if [ -z "$SSH_PREFIX" ]; then
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    else
        $SSH_PREFIX "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
    fi
    exit 1
fi

echo -e "${GREEN}✅ Contenedor encontrado: $CONTAINER${NC}"
echo ""

echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}2. VERIFICANDO ESTRUCTURA DE DIRECTORIOS EN EL CONTENEDOR${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"

echo ""
echo -e "${CYAN}Directorio /app/:${NC}"
if [ -z "$SSH_PREFIX" ]; then
    docker exec $CONTAINER ls -la /app/ 2>/dev/null || echo -e "${RED}❌ Error al acceder${NC}"
else
    $SSH_PREFIX "docker exec $CONTAINER ls -la /app/" 2>/dev/null || echo -e "${RED}❌ Error al acceder${NC}"
fi

echo ""
echo -e "${CYAN}Directorio /app/src/:${NC}"
if [ -z "$SSH_PREFIX" ]; then
    docker exec $CONTAINER ls -la /app/src/ 2>/dev/null || echo -e "${RED}❌ No existe /app/src/${NC}"
else
    $SSH_PREFIX "docker exec $CONTAINER ls -la /app/src/" 2>/dev/null || echo -e "${RED}❌ No existe /app/src/${NC}"
fi

echo ""
echo -e "${CYAN}Directorio /app/src/static/:${NC}"
if [ -z "$SSH_PREFIX" ]; then
    docker exec $CONTAINER ls -la /app/src/static/ 2>/dev/null || echo -e "${RED}❌ No existe /app/src/static/${NC}"
else
    $SSH_PREFIX "docker exec $CONTAINER ls -la /app/src/static/" 2>/dev/null || echo -e "${RED}❌ No existe /app/src/static/${NC}"
fi

echo ""
echo -e "${CYAN}Directorio /app/src/static/images/:${NC}"
if [ -z "$SSH_PREFIX" ]; then
    docker exec $CONTAINER ls -lh /app/src/static/images/ 2>/dev/null || echo -e "${RED}❌ No existe /app/src/static/images/${NC}"
else
    $SSH_PREFIX "docker exec $CONTAINER ls -lh /app/src/static/images/" 2>/dev/null || echo -e "${RED}❌ No existe /app/src/static/images/${NC}"
fi

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}3. VERIFICANDO MONTAJES DE VOLÚMENES${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"

echo ""
if [ -z "$SSH_PREFIX" ]; then
    docker inspect $CONTAINER --format='{{range .Mounts}}Origen: {{.Source}}
Destino: {{.Destination}}
Tipo: {{.Type}}
Modo: {{.Mode}}
---{{println}}{{end}}'
else
    $SSH_PREFIX "docker inspect $CONTAINER --format='{{range .Mounts}}Origen: {{.Source}}
Destino: {{.Destination}}
Tipo: {{.Type}}
Modo: {{.Mode}}
---{{println}}{{end}}'"
fi

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}4. VERIFICANDO PERMISOS DE ARCHIVOS${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"

echo ""
echo -e "${CYAN}Permisos de /app/src/static/:${NC}"
if [ -z "$SSH_PREFIX" ]; then
    docker exec $CONTAINER stat -c "%a %U:%G %n" /app/src/static/ 2>/dev/null || echo -e "${RED}❌ Error${NC}"
else
    $SSH_PREFIX "docker exec $CONTAINER stat -c '%a %U:%G %n' /app/src/static/" 2>/dev/null || echo -e "${RED}❌ Error${NC}"
fi

echo ""
echo -e "${CYAN}Permisos de archivos en /app/src/static/images/:${NC}"
if [ -z "$SSH_PREFIX" ]; then
    docker exec $CONTAINER stat -c "%a %U:%G %n" /app/src/static/images/* 2>/dev/null || echo -e "${RED}❌ Error${NC}"
else
    $SSH_PREFIX "docker exec $CONTAINER stat -c '%a %U:%G %n' /app/src/static/images/*" 2>/dev/null || echo -e "${RED}❌ Error${NC}"
fi

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}5. PROBANDO ACCESO HTTP A ARCHIVOS ESTÁTICOS${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"

# Determinar la URL base
if [ "$SERVER_IP" = "localhost" ]; then
    BASE_URL="http://localhost:8000"
else
    BASE_URL="http://$SERVER_IP:8000"
fi

echo ""
echo -e "${CYAN}URL Base: $BASE_URL${NC}"
echo ""

# Función para probar URL
test_url() {
    local url=$1
    local name=$2
    
    echo -n "Probando $name... "
    
    if [ -z "$SSH_PREFIX" ]; then
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    else
        HTTP_CODE=$($SSH_PREFIX "curl -s -o /dev/null -w '%{http_code}' '$url'" 2>/dev/null)
    fi
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✅ OK (HTTP $HTTP_CODE)${NC}"
        return 0
    else
        echo -e "${RED}❌ FALLO (HTTP $HTTP_CODE)${NC}"
        return 1
    fi
}

test_url "$BASE_URL/health" "Health Check"
test_url "$BASE_URL/static/images/favicon.png" "Favicon"
test_url "$BASE_URL/static/images/logo.png" "Logo"
test_url "$BASE_URL/static/css/main.css" "CSS Principal"
test_url "$BASE_URL/static/js/main.js" "JavaScript Principal"

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}6. VERIFICANDO LOGS DE LA APLICACIÓN${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"

echo ""
echo -e "${CYAN}Últimas 30 líneas de logs:${NC}"
echo "-------------------------------------------------------------------"
if [ -z "$SSH_PREFIX" ]; then
    docker logs $CONTAINER --tail 30 2>&1
else
    $SSH_PREFIX "docker logs $CONTAINER --tail 30" 2>&1
fi
echo "-------------------------------------------------------------------"

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}7. VERIFICANDO CONFIGURACIÓN DE FASTAPI${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"

echo ""
echo -e "${CYAN}Verificando montaje de StaticFiles en main.py:${NC}"
if [ -z "$SSH_PREFIX" ]; then
    docker exec $CONTAINER grep -A 2 "app.mount.*static" /app/src/main.py 2>/dev/null || echo -e "${RED}❌ No encontrado${NC}"
else
    $SSH_PREFIX "docker exec $CONTAINER grep -A 2 'app.mount.*static' /app/src/main.py" 2>/dev/null || echo -e "${RED}❌ No encontrado${NC}"
fi

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}8. VERIFICANDO NGINX (si está en uso)${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"

echo ""
if [ -z "$SSH_PREFIX" ]; then
    if command -v nginx &> /dev/null; then
        echo -e "${CYAN}Nginx está instalado${NC}"
        echo ""
        echo "Configuración de /static/:"
        grep -A 10 "location /static/" /etc/nginx/nginx.conf 2>/dev/null || echo "No encontrado en nginx.conf"
        
        echo ""
        echo "Logs de error de Nginx:"
        tail -20 /var/log/nginx/error.log 2>/dev/null || echo "No se puede acceder a los logs"
    else
        echo -e "${YELLOW}Nginx no está instalado en el host${NC}"
    fi
else
    if $SSH_PREFIX "command -v nginx" &> /dev/null; then
        echo -e "${CYAN}Nginx está instalado${NC}"
        echo ""
        echo "Configuración de /static/:"
        $SSH_PREFIX "grep -A 10 'location /static/' /etc/nginx/nginx.conf" 2>/dev/null || echo "No encontrado en nginx.conf"
        
        echo ""
        echo "Logs de error de Nginx:"
        $SSH_PREFIX "tail -20 /var/log/nginx/error.log" 2>/dev/null || echo "No se puede acceder a los logs"
    else
        echo -e "${YELLOW}Nginx no está instalado en el servidor${NC}"
    fi
fi

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}9. PRUEBA DIRECTA DESDE EL CONTENEDOR${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"

echo ""
echo -e "${CYAN}Probando acceso directo desde dentro del contenedor:${NC}"
echo ""

if [ -z "$SSH_PREFIX" ]; then
    echo "Test 1: ¿Existe el archivo favicon.png?"
    docker exec $CONTAINER test -f /app/src/static/images/favicon.png && echo -e "${GREEN}✅ Sí existe${NC}" || echo -e "${RED}❌ No existe${NC}"
    
    echo ""
    echo "Test 2: ¿Es legible el archivo?"
    docker exec $CONTAINER test -r /app/src/static/images/favicon.png && echo -e "${GREEN}✅ Es legible${NC}" || echo -e "${RED}❌ No es legible${NC}"
    
    echo ""
    echo "Test 3: Tamaño del archivo:"
    docker exec $CONTAINER du -h /app/src/static/images/favicon.png 2>/dev/null || echo -e "${RED}❌ Error${NC}"
    
    echo ""
    echo "Test 4: Curl desde dentro del contenedor:"
    docker exec $CONTAINER curl -I http://localhost:8000/static/images/favicon.png 2>/dev/null | head -n 1 || echo -e "${RED}❌ Error${NC}"
else
    echo "Test 1: ¿Existe el archivo favicon.png?"
    $SSH_PREFIX "docker exec $CONTAINER test -f /app/src/static/images/favicon.png" && echo -e "${GREEN}✅ Sí existe${NC}" || echo -e "${RED}❌ No existe${NC}"
    
    echo ""
    echo "Test 2: ¿Es legible el archivo?"
    $SSH_PREFIX "docker exec $CONTAINER test -r /app/src/static/images/favicon.png" && echo -e "${GREEN}✅ Es legible${NC}" || echo -e "${RED}❌ No es legible${NC}"
    
    echo ""
    echo "Test 3: Tamaño del archivo:"
    $SSH_PREFIX "docker exec $CONTAINER du -h /app/src/static/images/favicon.png" 2>/dev/null || echo -e "${RED}❌ Error${NC}"
    
    echo ""
    echo "Test 4: Curl desde dentro del contenedor:"
    $SSH_PREFIX "docker exec $CONTAINER curl -I http://localhost:8000/static/images/favicon.png" 2>/dev/null | head -n 1 || echo -e "${RED}❌ Error${NC}"
fi

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}10. RESUMEN Y RECOMENDACIONES${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"

echo ""
echo -e "${CYAN}Análisis completado. Revisa los resultados arriba.${NC}"
echo ""
echo -e "${BLUE}Posibles causas del problema:${NC}"
echo ""
echo "1. Los archivos no existen en el contenedor"
echo "   → Verifica que el volumen esté montado correctamente"
echo ""
echo "2. Problemas de permisos"
echo "   → Los archivos deben ser legibles por el usuario de la app"
echo ""
echo "3. FastAPI no está sirviendo los archivos"
echo "   → Verifica la configuración en main.py"
echo ""
echo "4. Nginx está bloqueando las peticiones"
echo "   → Revisa la configuración de Nginx"
echo ""
echo "5. El puerto no está accesible"
echo "   → Verifica el firewall y los puertos expuestos"
echo ""

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Diagnóstico completado${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
