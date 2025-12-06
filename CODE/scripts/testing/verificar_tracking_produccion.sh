#!/bin/bash
# Script de verificación del fix de tracking público en PRODUCCIÓN
# Fecha: 2024-12-06
# Servidor: https://paquetex.papyrus.com.co

echo "=========================================="
echo "VERIFICACIÓN FIX TRACKING - PRODUCCIÓN"
echo "=========================================="
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# URL de producción
PROD_URL="https://paquetex.papyrus.com.co"

# Código de prueba
TEST_CODE="IMV6"

echo "Servidor: $PROD_URL"
echo "Código de prueba: $TEST_CODE"
echo ""

# Test 1: Verificar que el endpoint de tracking es público
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 1: Endpoint de tracking público"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$PROD_URL/api/messages/tracking/$TEST_CODE")

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Endpoint retorna 200 OK (sin autenticación)"
    echo "  URL: $PROD_URL/api/messages/tracking/$TEST_CODE"
    echo "  HTTP Code: $HTTP_CODE"
else
    echo -e "${RED}✗ FAIL${NC} - Endpoint retorna $HTTP_CODE (esperado: 200)"
    echo "  URL: $PROD_URL/api/messages/tracking/$TEST_CODE"
    exit 1
fi
echo ""

# Test 2: Verificar que retorna JSON válido
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 2: Respuesta JSON válida"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
RESPONSE=$(curl -s "$PROD_URL/api/messages/tracking/$TEST_CODE")

if echo "$RESPONSE" | python3 -m json.tool > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC} - Respuesta es JSON válido"
    echo "  Respuesta: $RESPONSE"
else
    echo -e "${RED}✗ FAIL${NC} - Respuesta no es JSON válido"
    echo "  Respuesta: $RESPONSE"
    exit 1
fi
echo ""

# Test 3: Verificar que NO retorna error de autenticación
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 3: Sin error de autenticación"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if echo "$RESPONSE" | grep -q "No autenticado"; then
    echo -e "${RED}✗ FAIL${NC} - Respuesta contiene error de autenticación"
    echo "  Respuesta: $RESPONSE"
    exit 1
else
    echo -e "${GREEN}✓ PASS${NC} - No hay error de autenticación"
fi
echo ""

# Test 4: Verificar página de búsqueda
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 4: Página de búsqueda accesible"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
SEARCH_RESPONSE=$(curl -s "$PROD_URL/search?auto_search=$TEST_CODE")

if echo "$SEARCH_RESPONSE" | grep -q "Consultar Paquetes"; then
    echo -e "${GREEN}✓ PASS${NC} - Página de búsqueda carga correctamente"
    echo "  URL: $PROD_URL/search?auto_search=$TEST_CODE"
else
    echo -e "${RED}✗ FAIL${NC} - Página de búsqueda no carga correctamente"
    exit 1
fi
echo ""

# Test 5: Verificar configuración de rutas públicas
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 5: Configuración de rutas públicas"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
CONFIG=$(curl -s "$PROD_URL/api/config/public-routes")

if echo "$CONFIG" | grep -q "/api/messages/tracking"; then
    echo -e "${GREEN}✓ PASS${NC} - Ruta /api/messages/tracking está configurada como pública"
else
    echo -e "${RED}✗ FAIL${NC} - Ruta /api/messages/tracking NO está en rutas públicas"
    exit 1
fi
echo ""

# Resumen
echo "=========================================="
echo -e "${GREEN}✓ TODOS LOS TESTS PASARON${NC}"
echo "=========================================="
echo ""
echo "El fix de tracking público está funcionando correctamente en PRODUCCIÓN."
echo ""
echo "Prueba manual:"
echo "  1. Abre: $PROD_URL/search?auto_search=$TEST_CODE"
echo "  2. Verifica que NO te redirija a login"
echo "  3. Verifica que puedas ver la información del paquete"
echo ""
echo "Ahora puedes enviar este link a tus clientes sin problemas:"
echo "  $PROD_URL/search?auto_search=[CODIGO_PAQUETE]"
echo ""
