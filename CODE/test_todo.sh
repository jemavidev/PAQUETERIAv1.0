#!/bin/bash

# ========================================
# TEST COMPLETO: Verificar todos los fixes
# ========================================

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${CYAN}${BOLD}"
echo "========================================"
echo "  TEST COMPLETO"
echo "  Verificación de Todos los Fixes"
echo "========================================"
echo -e "${NC}"

TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

run_test() {
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "${BLUE}[$TOTAL_TESTS]${NC} $1"
}

test_passed() {
    PASSED_TESTS=$((PASSED_TESTS + 1))
    echo -e "${GREEN}  ✓${NC} $1"
}

test_failed() {
    FAILED_TESTS=$((FAILED_TESTS + 1))
    echo -e "${RED}  ✗${NC} $1"
}

# ========================================
# TEST 1: Servidor funcionando
# ========================================
run_test "Verificando servidor..."

if curl -s http://localhost:8000/health | grep -q "healthy"; then
    test_passed "Servidor funcionando"
else
    test_failed "Servidor no responde"
fi

# ========================================
# TEST 2: No hay ruta duplicada
# ========================================
run_test "Verificando que no hay ruta duplicada..."

duplicate_count=$(grep -c '@router.get("/auth/login")' src/app/routes/public.py 2>/dev/null || echo "0")

if [ "$duplicate_count" -eq "1" ]; then
    test_passed "Solo una definición de /auth/login"
elif [ "$duplicate_count" -gt "1" ]; then
    test_failed "Hay $duplicate_count definiciones de /auth/login"
else
    test_failed "No se pudo verificar el archivo"
fi

# ========================================
# TEST 3: Mensaje de sesión expirada
# ========================================
run_test "Verificando mensaje de sesión expirada..."

COOKIE_FILE="/tmp/test_cookies_all.txt"
cat > "$COOKIE_FILE" << EOF
localhost	FALSE	/	FALSE	0	access_token	expired_token_test
localhost	FALSE	/	FALSE	0	user_id	999
EOF

response=$(curl -s -b "$COOKIE_FILE" http://localhost:8000/auth/login)

if echo "$response" | grep -qi "sesión ha expirado\|session.*expired"; then
    test_passed "Mensaje de sesión expirada funciona"
else
    test_failed "Mensaje de sesión expirada NO se muestra"
fi

rm -f "$COOKIE_FILE"

# ========================================
# TEST 4: No hay verificación duplicada en login.html
# ========================================
run_test "Verificando que no hay verificación duplicada..."

if curl -s http://localhost:8000/auth/login | grep -q "checkAuthAndRedirect"; then
    test_failed "checkAuthAndRedirect todavía está en login.html"
else
    test_passed "No hay verificación duplicada en login.html"
fi

# ========================================
# TEST 5: auth-redirect.js excluye /auth/login
# ========================================
run_test "Verificando exclusión en auth-redirect.js..."

if grep -q "currentPath !== '/auth/login'" src/static/js/auth-redirect.js; then
    test_passed "auth-redirect.js excluye /auth/login correctamente"
else
    test_failed "auth-redirect.js no excluye /auth/login"
fi

# ========================================
# TEST 6: Página de login carga correctamente
# ========================================
run_test "Verificando carga de página de login..."

response=$(curl -s -w "\n%{http_code}" http://localhost:8000/auth/login)
http_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | head -n -1)

if [ "$http_code" = "200" ]; then
    if echo "$body" | grep -q "Iniciar Sesión"; then
        test_passed "Página de login carga correctamente"
    else
        test_failed "Página de login no tiene el contenido esperado"
    fi
else
    test_failed "Código HTTP inesperado: $http_code"
fi

# ========================================
# TEST 7: /admin redirige sin autenticación
# ========================================
run_test "Verificando redirección desde /admin..."

admin_response=$(curl -s -i http://localhost:8000/admin | grep -i "location:")

if echo "$admin_response" | grep -q "/auth/login"; then
    test_passed "/admin redirige a login correctamente"
else
    test_failed "/admin no redirige correctamente"
fi

# ========================================
# TEST 8: /api/auth/me retorna 401 sin autenticación
# ========================================
run_test "Verificando endpoint /api/auth/me..."

me_response=$(curl -s -w "\n%{http_code}" http://localhost:8000/api/auth/me)
me_http_code=$(echo "$me_response" | tail -n 1)

if [ "$me_http_code" = "401" ]; then
    test_passed "/api/auth/me retorna 401 correctamente"
else
    test_failed "/api/auth/me retorna código inesperado: $me_http_code"
fi

# ========================================
# RESUMEN
# ========================================
echo ""
echo -e "${CYAN}${BOLD}========================================${NC}"
echo -e "${CYAN}${BOLD}  RESUMEN${NC}"
echo -e "${CYAN}${BOLD}========================================${NC}"
echo ""
echo -e "Total de tests: ${BOLD}$TOTAL_TESTS${NC}"
echo -e "Tests exitosos: ${GREEN}${BOLD}$PASSED_TESTS${NC}"
echo -e "Tests fallidos: ${RED}${BOLD}$FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}${BOLD}✓ TODOS LOS TESTS PASARON${NC}"
    echo ""
    echo "El sistema está funcionando correctamente:"
    echo "  ✓ Servidor funcionando"
    echo "  ✓ No hay rutas duplicadas"
    echo "  ✓ Mensaje de sesión expirada funciona"
    echo "  ✓ No hay verificación duplicada en JavaScript"
    echo "  ✓ auth-redirect.js configurado correctamente"
    echo "  ✓ Página de login carga sin problemas"
    echo "  ✓ Redirección desde /admin funciona"
    echo "  ✓ Endpoint /api/auth/me funciona"
    echo ""
    echo -e "${CYAN}Próximo paso:${NC}"
    echo "  Prueba manual en tu navegador:"
    echo "  1. Abre: http://localhost:8000/auth/login"
    echo "  2. Verifica que NO se refresca automáticamente"
    echo "  3. Inicia sesión con: jesus / jesusSeaboard12"
    echo "  4. Verifica que NO entras en loop de redirección"
    echo ""
    exit 0
else
    echo -e "${RED}${BOLD}✗ ALGUNOS TESTS FALLARON${NC}"
    echo ""
    echo "Revisa los errores arriba y:"
    echo "  1. Verifica que los archivos se guardaron correctamente"
    echo "  2. Reinicia el servidor si es necesario"
    echo "  3. Ejecuta este script nuevamente"
    echo ""
    echo "Para más ayuda, revisa:"
    echo "  DOCS/fixes/INSTRUCCIONES_TEST_FIX.md"
    echo ""
    exit 1
fi
