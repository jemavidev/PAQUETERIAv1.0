#!/bin/bash

# Script de diagnóstico para problema de imágenes
# Fecha: 7 de diciembre de 2025

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     DIAGNÓSTICO DE PROBLEMA DE VISUALIZACIÓN DE IMÁGENES      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Nombre del contenedor (ajustar si es diferente)
CONTAINER_NAME="paquetex_web"

# Verificar si el contenedor existe
if ! docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${RED}❌ Contenedor '${CONTAINER_NAME}' no encontrado${NC}"
    echo ""
    echo "Contenedores disponibles:"
    docker ps -a --format "table {{.Names}}\t{{.Status}}"
    echo ""
    echo "Por favor, edita el script y cambia CONTAINER_NAME al nombre correcto"
    exit 1
fi

# Verificar si el contenedor está corriendo
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${RED}❌ Contenedor '${CONTAINER_NAME}' no está corriendo${NC}"
    echo ""
    docker ps -a --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Status}}"
    exit 1
fi

echo -e "${GREEN}✓ Contenedor encontrado y corriendo${NC}"
echo ""

# ============================================
# 1. Verificar directorio uploads
# ============================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}1. VERIFICAR DIRECTORIO /app/uploads/${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if docker exec $CONTAINER_NAME test -d /app/uploads; then
    echo -e "${GREEN}✓ Directorio /app/uploads existe${NC}"
    
    FILE_COUNT=$(docker exec $CONTAINER_NAME find /app/uploads -type f | wc -l)
    echo -e "  Archivos encontrados: ${YELLOW}${FILE_COUNT}${NC}"
    
    if [ $FILE_COUNT -gt 0 ]; then
        echo ""
        echo "  Primeros 10 archivos:"
        docker exec $CONTAINER_NAME find /app/uploads -type f | head -10 | while read file; do
            echo "    - $file"
        done
    else
        echo -e "${YELLOW}⚠️  Directorio vacío - no hay imágenes subidas${NC}"
    fi
else
    echo -e "${RED}❌ Directorio /app/uploads NO existe${NC}"
    echo -e "${YELLOW}   Solución: docker exec $CONTAINER_NAME mkdir -p /app/uploads${NC}"
fi

echo ""

# ============================================
# 2. Verificar permisos
# ============================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}2. VERIFICAR PERMISOS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

PERMS=$(docker exec $CONTAINER_NAME stat -c "%a %U:%G" /app/uploads 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Permisos: ${PERMS}${NC}"
    
    PERM_NUM=$(echo $PERMS | cut -d' ' -f1)
    if [ "$PERM_NUM" -ge "755" ]; then
        echo -e "${GREEN}✓ Permisos correctos (lectura pública)${NC}"
    else
        echo -e "${YELLOW}⚠️  Permisos restrictivos - puede causar problemas${NC}"
        echo -e "${YELLOW}   Solución: docker exec $CONTAINER_NAME chmod 755 /app/uploads${NC}"
    fi
else
    echo -e "${RED}❌ No se pudieron verificar permisos${NC}"
fi

echo ""

# ============================================
# 3. Verificar configuración de rutas
# ============================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}3. VERIFICAR CONFIGURACIÓN DE RUTAS ESTÁTICAS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

ROUTE_TEST=$(docker exec $CONTAINER_NAME python3 -c "
import sys
sys.path.insert(0, '/app/src')
try:
    from app.config_routes import is_static_route, STATIC_PREFIXES
    print('PREFIXES:', ','.join(STATIC_PREFIXES))
    print('TEST_UPLOADS:', is_static_route('/uploads/test.jpg'))
    print('TEST_STATIC:', is_static_route('/static/css/style.css'))
    print('TEST_ADMIN:', is_static_route('/admin'))
except Exception as e:
    print('ERROR:', str(e))
" 2>&1)

if echo "$ROUTE_TEST" | grep -q "ERROR"; then
    echo -e "${RED}❌ Error al verificar configuración de rutas${NC}"
    echo "$ROUTE_TEST"
else
    PREFIXES=$(echo "$ROUTE_TEST" | grep "PREFIXES:" | cut -d: -f2)
    TEST_UPLOADS=$(echo "$ROUTE_TEST" | grep "TEST_UPLOADS:" | cut -d: -f2)
    TEST_STATIC=$(echo "$ROUTE_TEST" | grep "TEST_STATIC:" | cut -d: -f2)
    TEST_ADMIN=$(echo "$ROUTE_TEST" | grep "TEST_ADMIN:" | cut -d: -f2)
    
    echo "  Prefijos configurados: ${YELLOW}${PREFIXES}${NC}"
    
    if echo "$PREFIXES" | grep -q "/uploads/"; then
        echo -e "${GREEN}✓ /uploads/ está en prefijos estáticos${NC}"
    else
        echo -e "${RED}❌ /uploads/ NO está en prefijos estáticos${NC}"
    fi
    
    if [ "$TEST_UPLOADS" = "True" ]; then
        echo -e "${GREEN}✓ is_static_route('/uploads/test.jpg') = True${NC}"
    else
        echo -e "${RED}❌ is_static_route('/uploads/test.jpg') = False${NC}"
    fi
    
    if [ "$TEST_STATIC" = "True" ]; then
        echo -e "${GREEN}✓ is_static_route('/static/css/style.css') = True${NC}"
    else
        echo -e "${RED}❌ is_static_route('/static/css/style.css') = False${NC}"
    fi
    
    if [ "$TEST_ADMIN" = "False" ]; then
        echo -e "${GREEN}✓ is_static_route('/admin') = False (correcto)${NC}"
    else
        echo -e "${RED}❌ is_static_route('/admin') = True (incorrecto)${NC}"
    fi
fi

echo ""

# ============================================
# 4. Verificar orden de montaje en main.py
# ============================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}4. VERIFICAR ORDEN DE MONTAJE EN main.py${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

MAIN_PY=$(docker exec $CONTAINER_NAME cat /app/src/main.py 2>/dev/null)
if [ $? -eq 0 ]; then
    # Buscar líneas de add_middleware y app.mount
    MIDDLEWARE_LINE=$(echo "$MAIN_PY" | grep -n "add_middleware(AuthMiddleware" | head -1 | cut -d: -f1)
    MOUNT_LINE=$(echo "$MAIN_PY" | grep -n 'app.mount("/uploads"' | head -1 | cut -d: -f1)
    
    if [ -n "$MIDDLEWARE_LINE" ] && [ -n "$MOUNT_LINE" ]; then
        echo "  Línea add_middleware(AuthMiddleware): ${YELLOW}${MIDDLEWARE_LINE}${NC}"
        echo "  Línea app.mount('/uploads'): ${YELLOW}${MOUNT_LINE}${NC}"
        
        if [ "$MIDDLEWARE_LINE" -lt "$MOUNT_LINE" ]; then
            echo -e "${GREEN}✓ Orden correcto: Middlewares ANTES de app.mount()${NC}"
        else
            echo -e "${RED}❌ Orden incorrecto: app.mount() ANTES de middlewares${NC}"
            echo -e "${YELLOW}   Este es el problema - las imágenes están bloqueadas${NC}"
            echo -e "${YELLOW}   Solución: Mover app.mount() DESPUÉS de add_middleware()${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  No se encontraron las líneas esperadas${NC}"
    fi
else
    echo -e "${RED}❌ No se pudo leer /app/src/main.py${NC}"
fi

echo ""

# ============================================
# 5. Probar acceso directo
# ============================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}5. PROBAR ACCESO DIRECTO A IMÁGENES${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Buscar una imagen real para probar
FIRST_IMAGE=$(docker exec $CONTAINER_NAME find /app/uploads -type f \( -name "*.jpg" -o -name "*.png" -o -name "*.jpeg" \) | head -1)

if [ -n "$FIRST_IMAGE" ]; then
    IMAGE_PATH=$(echo $FIRST_IMAGE | sed 's|/app||')
    echo "  Probando imagen: ${YELLOW}${IMAGE_PATH}${NC}"
    
    # Probar desde dentro del contenedor
    HTTP_CODE=$(docker exec $CONTAINER_NAME curl -s -o /dev/null -w "%{http_code}" http://localhost:8000${IMAGE_PATH})
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✓ Acceso interno: 200 OK${NC}"
    elif [ "$HTTP_CODE" = "404" ]; then
        echo -e "${RED}❌ Acceso interno: 404 Not Found${NC}"
    elif [ "$HTTP_CODE" = "302" ]; then
        echo -e "${RED}❌ Acceso interno: 302 Redirect (middleware bloqueando)${NC}"
    elif [ "$HTTP_CODE" = "401" ]; then
        echo -e "${RED}❌ Acceso interno: 401 Unauthorized (middleware bloqueando)${NC}"
    else
        echo -e "${YELLOW}⚠️  Acceso interno: ${HTTP_CODE}${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No se encontraron imágenes para probar${NC}"
    echo "  Sube una imagen primero para probar el acceso"
fi

echo ""

# ============================================
# 6. Ver logs recientes
# ============================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}6. LOGS RECIENTES (últimas 20 líneas con 'uploads')${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

LOGS=$(docker logs $CONTAINER_NAME 2>&1 | grep -i "uploads" | tail -20)
if [ -n "$LOGS" ]; then
    echo "$LOGS"
else
    echo -e "${YELLOW}⚠️  No se encontraron logs relacionados con 'uploads'${NC}"
fi

echo ""

# ============================================
# RESUMEN Y RECOMENDACIONES
# ============================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}RESUMEN Y RECOMENDACIONES${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo ""
echo "Basado en el diagnóstico:"
echo ""

# Verificar si hay problemas críticos
CRITICAL_ISSUES=0

if ! docker exec $CONTAINER_NAME test -d /app/uploads; then
    echo -e "${RED}❌ CRÍTICO: Directorio /app/uploads no existe${NC}"
    echo "   Solución: docker exec $CONTAINER_NAME mkdir -p /app/uploads"
    CRITICAL_ISSUES=$((CRITICAL_ISSUES + 1))
fi

if [ -n "$MIDDLEWARE_LINE" ] && [ -n "$MOUNT_LINE" ] && [ "$MIDDLEWARE_LINE" -gt "$MOUNT_LINE" ]; then
    echo -e "${RED}❌ CRÍTICO: Orden incorrecto en main.py${NC}"
    echo "   Solución: Editar CODE/src/main.py y mover app.mount() DESPUÉS de add_middleware()"
    CRITICAL_ISSUES=$((CRITICAL_ISSUES + 1))
fi

if [ "$TEST_UPLOADS" != "True" ]; then
    echo -e "${RED}❌ CRÍTICO: /uploads/ no está configurado como ruta estática${NC}"
    echo "   Solución: Verificar CODE/src/app/config_routes.py"
    CRITICAL_ISSUES=$((CRITICAL_ISSUES + 1))
fi

if [ $CRITICAL_ISSUES -eq 0 ]; then
    echo -e "${GREEN}✓ No se encontraron problemas críticos en la configuración${NC}"
    echo ""
    echo "Si las imágenes aún no funcionan, el problema puede ser:"
    echo "  1. Volumen no montado en docker-compose.yml"
    echo "  2. Problema de nginx (si aplica)"
    echo "  3. Rutas incorrectas en HTML"
    echo "  4. Problema de CORS"
else
    echo ""
    echo -e "${YELLOW}Se encontraron ${CRITICAL_ISSUES} problema(s) crítico(s)${NC}"
    echo "Corrige los problemas indicados arriba y reinicia el contenedor:"
    echo "  docker-compose restart web"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "Diagnóstico completado - $(date)"
echo "═══════════════════════════════════════════════════════════════"
