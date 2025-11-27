#!/bin/bash

# ========================================
# TEST AUTOMATIZADO: Fix de Loop de Redirección
# ========================================

set -e

BASE_URL="http://localhost:8000"
COOKIE_FILE="/tmp/test_cookies_auto.txt"
USERNAME="jesus"
PASSWORD="jesusSeaboard12"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo -e "\n${CYAN}========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}========================================${NC}\n"
}

print_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[i]${NC} $1"
}

# Contador de tests
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

run_test() {
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
}

test_passed() {
    PASSED_TESTS=$((PASSED_TESTS + 1))
    print_success "$1"
}

test_failed() {
    FAILED_TESTS=$((FAILED_TESTS + 1))
    print_error "$1"
}

# Limpiar cookies
rm -f "$COOKIE_FILE"

print_header "TEST AUTOMATIZADO: Fix de Loop de Redirección"
print_info "Usuario: $USERNAME"
print_info "Base URL: $BASE_URL"
echo ""

# ========================================
# TEST 1: Login
# ========================================
print_header "TEST 1: Login con credenciales válidas"
run_test

print_test "Intentando login..."

login_response=$(curl -s -w "\n%{http_code}" \
    -X POST \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=$USERNAME&password=$PASSWORD" \
    -c "$COOKIE_FILE" \
    "$BASE_URL/api/auth/login")

http_code=$(echo "$login_response" | tail -n 1)
body=$(echo "$login_response" | head -n -1)

echo "HTTP Code: $http_code"

if [ "$http_code" = "200" ]; then
    if echo "$body" | grep -q "success.*true\|access_token"; then
        test_passed "Login exitoso"
        
        # Verificar cookies
        if [ -f "$COOKIE_FILE" ]; then
            cookie_count=$(grep -c "access_token\|user_id\|user_name\|user_role" "$COOKIE_FILE" || true)
            print_info "Cookies establecidas: $cookie_count"
        fi
    else
        test_failed "Login falló - Respuesta inesperada"
        echo "Respuesta: $body"
    fi
else
    test_failed "Login falló - HTTP $http_code"
    echo "Respuesta: $body"
fi

# ========================================
# TEST 2: Verificar /api/auth/me
# ========================================
print_header "TEST 2: Verificar sesión con /api/auth/me"
run_test

print_test "Consultando /api/auth/me..."

me_response=$(curl -s -w "\n%{http_code}" -b "$COOKIE_FILE" "$BASE_URL/api/auth/me")
me_http_code=$(echo "$me_response" | tail -n 1)
me_body=$(echo "$me_response" | head -n -1)

echo "HTTP Code: $me_http_code"

if [ "$me_http_code" = "200" ]; then
    if echo "$me_body" | grep -q "username\|id"; then
        test_passed "Sesión válida - Usuario autenticado"
        echo "$me_body" | jq -r '.username' 2>/dev/null && echo "" || true
    else
        test_failed "Respuesta inesperada de /api/auth/me"
    fi
else
    test_failed "Sesión inválida - HTTP $me_http_code"
fi

# ========================================
# TEST 3: Acceso a /admin con sesión válida
# ========================================
print_header "TEST 3: Acceso a /admin con sesión válida"
run_test

print_test "Intentando acceder a /admin..."

admin_response=$(curl -s -w "\n%{http_code}" -b "$COOKIE_FILE" "$BASE_URL/admin")
admin_http_code=$(echo "$admin_response" | tail -n 1)
admin_body=$(echo "$admin_response" | head -n -1)

echo "HTTP Code: $admin_http_code"

if [ "$admin_http_code" = "200" ]; then
    if echo "$admin_body" | grep -qi "dashboard\|administración\|admin"; then
        test_passed "Acceso a /admin exitoso"
    else
        test_failed "Acceso permitido pero contenido inesperado"
    fi
elif [ "$admin_http_code" = "302" ] || [ "$admin_http_code" = "307" ]; then
    test_failed "Redirigido - No debería pasar con sesión válida"
    
    # Verificar a dónde redirige
    location=$(curl -s -i -b "$COOKIE_FILE" "$BASE_URL/admin" | grep -i "location:" | cut -d' ' -f2 | tr -d '\r')
    print_info "Redirige a: $location"
else
    test_failed "Error accediendo a /admin - HTTP $admin_http_code"
fi

# ========================================
# TEST 4: Acceso a /auth/login estando autenticado
# ========================================
print_header "TEST 4: Auto-redirect desde /auth/login"
run_test

print_test "Accediendo a /auth/login con sesión válida..."

# Sin -L para no seguir redirects automáticamente
login_page_response=$(curl -s -w "\n%{http_code}" -i -b "$COOKIE_FILE" "$BASE_URL/auth/login")
login_page_http_code=$(echo "$login_page_response" | tail -n 1)

echo "HTTP Code: $login_page_http_code"

if [ "$login_page_http_code" = "302" ] || [ "$login_page_http_code" = "307" ]; then
    location=$(echo "$login_page_response" | grep -i "location:" | cut -d' ' -f2 | tr -d '\r')
    test_passed "Redirigido correctamente a: $location"
else
    # Verificar si el body contiene el formulario
    login_page_body=$(echo "$login_page_response" | sed '1,/^\r$/d')
    if echo "$login_page_body" | grep -q "Iniciar Sesión" && echo "$login_page_body" | grep -q "password"; then
        test_failed "Mostró formulario de login (debería redirigir)"
        print_info "El auto-redirect del backend NO está funcionando"
    else
        test_passed "No mostró formulario de login"
    fi
fi

# ========================================
# TEST 5: Simular token expirado
# ========================================
print_header "TEST 5: Manejo de token expirado"
run_test

print_test "Creando cookies con token inválido..."

# Crear cookies con token inválido
cat > "$COOKIE_FILE" << EOF
# Netscape HTTP Cookie File
localhost	FALSE	/	FALSE	0	access_token	invalid_token_xyz123
localhost	FALSE	/	FALSE	0	user_id	1
localhost	FALSE	/	FALSE	0	user_name	testuser
localhost	FALSE	/	FALSE	0	user_role	admin
EOF

print_test "Accediendo a /auth/login con token inválido..."

expired_response=$(curl -s -b "$COOKIE_FILE" "$BASE_URL/auth/login")

if echo "$expired_response" | grep -qi "sesión ha expirado\|session.*expired"; then
    test_passed "Mensaje de sesión expirada mostrado"
else
    test_failed "No se encontró mensaje de sesión expirada"
    
    # Buscar en el HTML
    if echo "$expired_response" | grep -qi "expirado\|expired"; then
        print_info "Se encontró texto relacionado con expiración"
    fi
fi

# ========================================
# TEST 6: Limpieza de cookies inválidas
# ========================================
print_header "TEST 6: Limpieza de cookies inválidas"
run_test

print_test "Verificando headers Set-Cookie..."

cleanup_headers=$(curl -s -i -b "$COOKIE_FILE" "$BASE_URL/auth/login" | grep -i "set-cookie" || true)

if [ -n "$cleanup_headers" ]; then
    if echo "$cleanup_headers" | grep -q "access_token"; then
        test_passed "Cookies siendo limpiadas (Set-Cookie detectado)"
    else
        test_failed "Set-Cookie presente pero no limpia access_token"
    fi
else
    test_failed "No se detectaron headers Set-Cookie"
fi

# ========================================
# TEST 7: Acceso sin autenticación
# ========================================
print_header "TEST 7: Acceso a /admin sin autenticación"
run_test

rm -f "$COOKIE_FILE"

print_test "Intentando acceder a /admin sin cookies..."

no_auth_response=$(curl -s -w "\n%{http_code}" -L "$BASE_URL/admin")
no_auth_http_code=$(echo "$no_auth_response" | tail -n 1)
no_auth_body=$(echo "$no_auth_response" | head -n -1)

echo "HTTP Code: $no_auth_http_code"

if echo "$no_auth_body" | grep -qi "iniciar sesión\|login"; then
    test_passed "Redirigido correctamente a login"
else
    test_failed "No redirigió a login"
fi

# ========================================
# RESUMEN FINAL
# ========================================
print_header "RESUMEN FINAL"

echo -e "${CYAN}Total de tests:${NC} $TOTAL_TESTS"
echo -e "${GREEN}Tests exitosos:${NC} $PASSED_TESTS"
echo -e "${RED}Tests fallidos:${NC} $FAILED_TESTS"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✓ TODOS LOS TESTS PASARON${NC}"
    echo ""
    echo "El fix del loop de redirección está funcionando correctamente:"
    echo "  ✓ Login funciona"
    echo "  ✓ Acceso a /admin con sesión válida"
    echo "  ✓ Auto-redirect desde /auth/login"
    echo "  ✓ Manejo de tokens expirados"
    echo "  ✓ Limpieza de cookies inválidas"
    echo "  ✓ Redirección sin autenticación"
    exit 0
else
    echo -e "${RED}✗ ALGUNOS TESTS FALLARON${NC}"
    echo ""
    echo "Revisa los errores arriba para más detalles."
    exit 1
fi
