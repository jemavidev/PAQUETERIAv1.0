#!/bin/bash

# ========================================
# TEST: Verificar que NO hay loop infinito
# ========================================

BASE_URL="http://localhost:8000"

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}TEST: Verificar que NO hay loop infinito${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Test 1: Verificar que checkAuthAndRedirect no está en login.html
echo -e "${BLUE}[1/3]${NC} Verificando que no hay verificación duplicada en login.html..."

if curl -s "$BASE_URL/auth/login" | grep -q "checkAuthAndRedirect"; then
    echo -e "${RED}✗${NC} FALLO: checkAuthAndRedirect todavía está en login.html"
    exit 1
else
    echo -e "${GREEN}✓${NC} OK: No hay verificación duplicada en login.html"
fi

# Test 2: Verificar que auth-redirect.js excluye /auth/login
echo -e "${BLUE}[2/3]${NC} Verificando que auth-redirect.js excluye /auth/login..."

if grep -q "currentPath !== '/auth/login'" src/static/js/auth-redirect.js; then
    echo -e "${GREEN}✓${NC} OK: auth-redirect.js excluye /auth/login correctamente"
else
    echo -e "${RED}✗${NC} FALLO: auth-redirect.js no excluye /auth/login"
    exit 1
fi

# Test 3: Verificar que la página de login carga sin errores
echo -e "${BLUE}[3/3]${NC} Verificando que la página de login carga correctamente..."

response=$(curl -s -w "\n%{http_code}" "$BASE_URL/auth/login")
http_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | head -n -1)

if [ "$http_code" = "200" ]; then
    if echo "$body" | grep -q "Iniciar Sesión"; then
        echo -e "${GREEN}✓${NC} OK: Página de login carga correctamente"
    else
        echo -e "${RED}✗${NC} FALLO: Página de login no tiene el contenido esperado"
        exit 1
    fi
else
    echo -e "${RED}✗${NC} FALLO: Código HTTP inesperado: $http_code"
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ TODOS LOS TESTS PASARON${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "La página de login debería funcionar sin loops."
echo ""
echo "Prueba manual:"
echo "1. Abre tu navegador en: $BASE_URL/auth/login"
echo "2. Verifica que la página NO se refresca automáticamente"
echo "3. Abre la consola (F12) y verifica que NO hay llamadas constantes a /api/auth/me"
echo "4. Inicia sesión y verifica que funciona correctamente"
echo ""
