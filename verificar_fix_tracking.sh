#!/bin/bash

# Script para verificar que el fix de tracking funciona correctamente
# Uso: ./verificar_fix_tracking.sh [URL_BASE]
# Ejemplo: ./verificar_fix_tracking.sh https://paquetex.papyrus.com.co

BASE_URL="${1:-http://localhost:8000}"

echo "============================================================"
echo "VERIFICACIÓN DEL FIX DE TRACKING"
echo "============================================================"
echo "URL Base: $BASE_URL"
echo ""

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para probar un endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    local expected_status=$4
    
    echo -n "Probando: $description... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" -X $method "$BASE_URL$endpoint" 2>/dev/null)
    
    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✅ OK${NC} (HTTP $response)"
        return 0
    else
        echo -e "${RED}❌ FALLÓ${NC} (HTTP $response, esperado $expected_status)"
        return 1
    fi
}

# Contador de pruebas
total=0
passed=0

echo "📋 Probando endpoints públicos de tracking:"
echo ""

# Test 1: Página de búsqueda (debe ser accesible)
((total++))
if test_endpoint "GET" "/search" "Página de búsqueda" "200"; then
    ((passed++))
fi

# Test 2: Endpoint de tracking con código (debe devolver 200 o 404, NO 401)
((total++))
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/messages/tracking/TEST123" 2>/dev/null)
if [ "$response" != "401" ] && [ "$response" != "302" ]; then
    echo -e "Probando: Tracking con código... ${GREEN}✅ OK${NC} (HTTP $response - no redirige a login)"
    ((passed++))
else
    echo -e "Probando: Tracking con código... ${RED}❌ FALLÓ${NC} (HTTP $response - redirige a login)"
fi

# Test 3: Check tracking inquiries
((total++))
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/messages/check-tracking-inquiries?package_tracking_code=TEST123" 2>/dev/null)
if [ "$response" != "401" ] && [ "$response" != "302" ]; then
    echo -e "Probando: Check tracking inquiries... ${GREEN}✅ OK${NC} (HTTP $response - no redirige a login)"
    ((passed++))
else
    echo -e "Probando: Check tracking inquiries... ${RED}❌ FALLÓ${NC} (HTTP $response - redirige a login)"
fi

# Test 4: Check inquiry exists
((total++))
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/messages/check-inquiry-exists?customer_email=test@example.com" 2>/dev/null)
if [ "$response" != "401" ] && [ "$response" != "302" ]; then
    echo -e "Probando: Check inquiry exists... ${GREEN}✅ OK${NC} (HTTP $response - no redirige a login)"
    ((passed++))
else
    echo -e "Probando: Check inquiry exists... ${RED}❌ FALLÓ${NC} (HTTP $response - redirige a login)"
fi

# Test 5: Búsqueda de paquetes
((total++))
if test_endpoint "GET" "/api/announcements/search/package?query=TEST" "Búsqueda de paquetes" "200"; then
    ((passed++))
fi

echo ""
echo "============================================================"
echo "RESULTADOS"
echo "============================================================"
echo "Total de pruebas: $total"
echo "Pruebas exitosas: $passed"
echo "Pruebas fallidas: $((total - passed))"
echo ""

if [ $passed -eq $total ]; then
    echo -e "${GREEN}✅ TODAS LAS PRUEBAS PASARON${NC}"
    echo "El fix de tracking está funcionando correctamente"
    exit 0
else
    echo -e "${RED}❌ ALGUNAS PRUEBAS FALLARON${NC}"
    echo "Revisa la configuración del servidor"
    exit 1
fi
