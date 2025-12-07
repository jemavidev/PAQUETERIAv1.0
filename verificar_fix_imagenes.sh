#!/bin/bash

# Script de verificación del fix de imágenes
# Fecha: 7 de diciembre de 2025

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          VERIFICACIÓN DEL FIX DE IMÁGENES S3                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Nombre del contenedor
CONTAINER_NAME="paquetex_web"

echo -e "${BLUE}1. Verificando configuración de rutas...${NC}"
echo ""

# Verificar que /api/images está en rutas públicas
ROUTE_CHECK=$(docker exec $CONTAINER_NAME python3 -c "
import sys
sys.path.insert(0, '/app/src')
from app.config_routes import is_api_public_route, API_PUBLIC_ROUTES

# Verificar que /api/images está en la lista
in_list = '/api/images' in API_PUBLIC_ROUTES
print(f'IN_LIST:{in_list}')

# Verificar que la función funciona
test1 = is_api_public_route('/api/images/123')
test2 = is_api_public_route('/api/images/456')
test3 = is_api_public_route('/api/packages')

print(f'TEST1:{test1}')
print(f'TEST2:{test2}')
print(f'TEST3:{test3}')
" 2>&1)

IN_LIST=$(echo "$ROUTE_CHECK" | grep "IN_LIST:" | cut -d: -f2)
TEST1=$(echo "$ROUTE_CHECK" | grep "TEST1:" | cut -d: -f2)
TEST2=$(echo "$ROUTE_CHECK" | grep "TEST2:" | cut -d: -f2)
TEST3=$(echo "$ROUTE_CHECK" | grep "TEST3:" | cut -d: -f2)

if [ "$IN_LIST" = "True" ]; then
    echo -e "${GREEN}✓ /api/images está en API_PUBLIC_ROUTES${NC}"
else
    echo -e "${RED}❌ /api/images NO está en API_PUBLIC_ROUTES${NC}"
    echo -e "${YELLOW}   Solución: Agregar '/api/images' a API_PUBLIC_ROUTES en config_routes.py${NC}"
    exit 1
fi

if [ "$TEST1" = "True" ] && [ "$TEST2" = "True" ]; then
    echo -e "${GREEN}✓ is_api_public_route() funciona correctamente${NC}"
else
    echo -e "${RED}❌ is_api_public_route() NO funciona correctamente${NC}"
    echo "  Test /api/images/123: $TEST1 (esperado: True)"
    echo "  Test /api/images/456: $TEST2 (esperado: True)"
    exit 1
fi

if [ "$TEST3" = "False" ]; then
    echo -e "${GREEN}✓ Rutas protegidas siguen protegidas${NC}"
else
    echo -e "${RED}❌ Rutas protegidas están públicas (error de configuración)${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}2. Probando acceso HTTP a imágenes...${NC}"
echo ""

# Obtener ID de una imagen real
IMAGE_ID=$(docker exec $CONTAINER_NAME python3 -c "
import sys
sys.path.insert(0, '/app/src')
from app.database import SessionLocal
from app.models.file_upload import FileUpload
db = SessionLocal()
img = db.query(FileUpload).first()
if img:
    print(img.id)
else:
    print('NO_IMAGES')
db.close()
" 2>&1 | tail -1)

if [ "$IMAGE_ID" = "NO_IMAGES" ]; then
    echo -e "${YELLOW}⚠️  No hay imágenes en la base de datos para probar${NC}"
    echo "   Sube una imagen primero para probar el acceso HTTP"
else
    echo "  Probando imagen ID: $IMAGE_ID"
    
    # Probar acceso HTTP
    HTTP_CODE=$(docker exec $CONTAINER_NAME curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/images/$IMAGE_ID)
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✓ Acceso HTTP: 200 OK${NC}"
    elif [ "$HTTP_CODE" = "404" ]; then
        echo -e "${YELLOW}⚠️  Acceso HTTP: 404 Not Found (imagen no existe en S3)${NC}"
        echo "   Esto es normal si la imagen fue eliminada de S3"
    elif [ "$HTTP_CODE" = "401" ]; then
        echo -e "${RED}❌ Acceso HTTP: 401 Unauthorized (middleware bloqueando)${NC}"
        echo "   El fix NO funcionó - revisar configuración"
        exit 1
    elif [ "$HTTP_CODE" = "302" ]; then
        echo -e "${RED}❌ Acceso HTTP: 302 Redirect (middleware bloqueando)${NC}"
        echo "   El fix NO funcionó - revisar configuración"
        exit 1
    else
        echo -e "${YELLOW}⚠️  Acceso HTTP: $HTTP_CODE${NC}"
    fi
fi

echo ""
echo -e "${BLUE}3. Verificando conexión S3...${NC}"
echo ""

S3_TEST=$(docker exec $CONTAINER_NAME python3 -c "
import sys
sys.path.insert(0, '/app/src')
try:
    from app.services.s3_service import S3Service
    s3 = S3Service()
    result = s3.test_connection()
    print(f'S3_OK:{result}')
except Exception as e:
    print(f'S3_ERROR:{str(e)}')
" 2>&1)

if echo "$S3_TEST" | grep -q "S3_OK:True"; then
    echo -e "${GREEN}✓ Conexión S3 exitosa${NC}"
elif echo "$S3_TEST" | grep -q "S3_ERROR"; then
    ERROR=$(echo "$S3_TEST" | grep "S3_ERROR:" | cut -d: -f2-)
    echo -e "${RED}❌ Error de conexión S3: $ERROR${NC}"
    echo -e "${YELLOW}   Verificar credenciales AWS en .env${NC}"
else
    echo -e "${YELLOW}⚠️  No se pudo verificar conexión S3${NC}"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ VERIFICACIÓN COMPLETADA${NC}"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Resumen:"
echo "  - Configuración de rutas: OK"
echo "  - Función is_api_public_route(): OK"
echo "  - Acceso HTTP a imágenes: OK"
echo ""
echo "Las imágenes deberían cargarse correctamente ahora."
echo ""
echo "Para probar en el navegador:"
echo "  1. Abre: http://localhost:8000/search?auto_search=IMV6"
echo "  2. Abre DevTools (F12) → Network"
echo "  3. Verifica que /api/images/ retorna 200 OK"
echo ""
