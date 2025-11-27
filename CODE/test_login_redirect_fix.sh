#!/bin/bash

# ========================================
# TEST: Fix de Loop de Redirección en Login
# ========================================

set -e

BASE_URL="http://localhost:8000"
COOKIE_FILE="/tmp/test_cookies.txt"
TEST_RESULTS="/tmp/test_results.txt"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Limpiar archivos temporales
cleanup() {
    rm -f "$COOKIE_FILE" "$TEST_RESULTS"
}

# Inicializar
cleanup
echo "========================================" > "$TEST_RESULTS"
echo "TEST: Fix de Loop de Redirección" >> "$TEST_RESULTS"
echo "Fecha: $(date)" >> "$TEST_RESULTS"
echo "========================================" >> "$TEST_RESULTS"
echo "" >> "$TEST_RESULTS"

# ========================================
# TEST 1: Acceso a /admin sin autenticación
# ========================================
print_test "TEST 1: Acceso a /admin sin autenticación"
echo "TEST 1: Acceso a /admin sin autenticación" >> "$TEST_RESULTS"

response=$(curl -s -w "\n%{http_code}" -L -c "$COOKIE_FILE" "$BASE_URL/admin")
http_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | head -n -1)

if [ "$http_code" = "200" ]; then
    if echo "$body" | grep -q "Iniciar Sesión" || echo "$body" | grep -q "login"; then
        print_success "Redirigido correctamente a login"
        echo "✓ Redirigido correctamente a login (HTTP $http_code)" >> "$TEST_RESULTS"
    else
        print_error "Respuesta inesperada"
        echo "✗ Respuesta inesperada (HTTP $http_code)" >> "$TEST_RESULTS"
    fi
else
    print_error "Código HTTP inesperado: $http_code"
    echo "✗ Código HTTP inesperado: $http_code" >> "$TEST_RESULTS"
fi
echo "" >> "$TEST_RESULTS"

# ========================================
# TEST 2: Login con credenciales válidas
# ========================================
print_test "TEST 2: Login con credenciales válidas"
echo "TEST 2: Login con credenciales válidas" >> "$TEST_RESULTS"

# Intentar login (ajusta las credenciales según tu sistema)
login_response=$(curl -s -w "\n%{http_code}" \
    -X POST \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=jesus&password=jesus123" \
    -c "$COOKIE_FILE" \
    "$BASE_URL/api/auth/login")

login_http_code=$(echo "$login_response" | tail -n 1)
login_body=$(echo "$login_response" | head -n -1)

if [ "$login_http_code" = "200" ]; then
    if echo "$login_body" | grep -q "access_token" || echo "$login_body" | grep -q "success"; then
        print_success "Login exitoso"
        echo "✓ Login exitoso (HTTP $login_http_code)" >> "$TEST_RESULTS"
        
        # Verificar que se establecieron las cookies
        if [ -f "$COOKIE_FILE" ]; then
            cookie_count=$(grep -c "access_token\|user_id\|user_name\|user_role" "$COOKIE_FILE" || true)
            if [ "$cookie_count" -gt 0 ]; then
                print_success "Cookies establecidas correctamente ($cookie_count cookies)"
                echo "✓ Cookies establecidas: $cookie_count" >> "$TEST_RESULTS"
            else
                print_warning "No se encontraron cookies esperadas"
                echo "! No se encontraron cookies esperadas" >> "$TEST_RESULTS"
            fi
        fi
    else
        print_error "Login falló"
        echo "✗ Login falló (HTTP $login_http_code)" >> "$TEST_RESULTS"
        echo "Respuesta: $login_body" >> "$TEST_RESULTS"
    fi
else
    print_error "Código HTTP inesperado en login: $login_http_code"
    echo "✗ Código HTTP inesperado: $login_http_code" >> "$TEST_RESULTS"
fi
echo "" >> "$TEST_RESULTS"

# ========================================
# TEST 3: Acceso a /admin con autenticación válida
# ========================================
print_test "TEST 3: Acceso a /admin con autenticación válida"
echo "TEST 3: Acceso a /admin con autenticación válida" >> "$TEST_RESULTS"

admin_response=$(curl -s -w "\n%{http_code}" -b "$COOKIE_FILE" "$BASE_URL/admin")
admin_http_code=$(echo "$admin_response" | tail -n 1)
admin_body=$(echo "$admin_response" | head -n -1)

if [ "$admin_http_code" = "200" ]; then
    if echo "$admin_body" | grep -q "Dashboard\|Administración\|admin"; then
        print_success "Acceso a /admin exitoso"
        echo "✓ Acceso a /admin exitoso (HTTP $admin_http_code)" >> "$TEST_RESULTS"
    else
        print_warning "Acceso permitido pero contenido inesperado"
        echo "! Acceso permitido pero contenido inesperado" >> "$TEST_RESULTS"
    fi
else
    print_error "No se pudo acceder a /admin: HTTP $admin_http_code"
    echo "✗ No se pudo acceder a /admin: HTTP $admin_http_code" >> "$TEST_RESULTS"
fi
echo "" >> "$TEST_RESULTS"

# ========================================
# TEST 4: Verificar endpoint /api/auth/me
# ========================================
print_test "TEST 4: Verificar endpoint /api/auth/me"
echo "TEST 4: Verificar endpoint /api/auth/me" >> "$TEST_RESULTS"

me_response=$(curl -s -w "\n%{http_code}" -b "$COOKIE_FILE" "$BASE_URL/api/auth/me")
me_http_code=$(echo "$me_response" | tail -n 1)
me_body=$(echo "$me_response" | head -n -1)

if [ "$me_http_code" = "200" ]; then
    if echo "$me_body" | grep -q "username\|id"; then
        print_success "Endpoint /api/auth/me funciona correctamente"
        echo "✓ Endpoint /api/auth/me funciona (HTTP $me_http_code)" >> "$TEST_RESULTS"
        echo "Respuesta: $me_body" >> "$TEST_RESULTS"
    else
        print_warning "Respuesta inesperada de /api/auth/me"
        echo "! Respuesta inesperada" >> "$TEST_RESULTS"
    fi
else
    print_error "Error en /api/auth/me: HTTP $me_http_code"
    echo "✗ Error en /api/auth/me: HTTP $me_http_code" >> "$TEST_RESULTS"
fi
echo "" >> "$TEST_RESULTS"

# ========================================
# TEST 5: Acceso a /auth/login estando autenticado
# ========================================
print_test "TEST 5: Acceso a /auth/login estando autenticado (debe redirigir)"
echo "TEST 5: Acceso a /auth/login estando autenticado" >> "$TEST_RESULTS"

login_page_response=$(curl -s -w "\n%{http_code}" -L -b "$COOKIE_FILE" "$BASE_URL/auth/login")
login_page_http_code=$(echo "$login_page_response" | tail -n 1)
login_page_body=$(echo "$login_page_response" | head -n -1)

if [ "$login_page_http_code" = "200" ]; then
    # Verificar si fue redirigido (no debería ver el formulario de login)
    if echo "$login_page_body" | grep -q "Iniciar Sesión" && echo "$login_page_body" | grep -q "password"; then
        print_warning "Mostró formulario de login (debería haber redirigido)"
        echo "! Mostró formulario de login en lugar de redirigir" >> "$TEST_RESULTS"
    else
        print_success "Redirigido correctamente (no mostró formulario)"
        echo "✓ Redirigido correctamente" >> "$TEST_RESULTS"
    fi
else
    print_warning "Código HTTP inesperado: $login_page_http_code"
    echo "! Código HTTP inesperado: $login_page_http_code" >> "$TEST_RESULTS"
fi
echo "" >> "$TEST_RESULTS"

# ========================================
# TEST 6: Simular token expirado
# ========================================
print_test "TEST 6: Simular token expirado (cookies inválidas)"
echo "TEST 6: Simular token expirado" >> "$TEST_RESULTS"

# Crear cookies con token inválido
echo "localhost	FALSE	/	FALSE	0	access_token	invalid_token_12345" > "$COOKIE_FILE"
echo "localhost	FALSE	/	FALSE	0	user_id	1" >> "$COOKIE_FILE"
echo "localhost	FALSE	/	FALSE	0	user_name	testuser" >> "$COOKIE_FILE"
echo "localhost	FALSE	/	FALSE	0	user_role	admin" >> "$COOKIE_FILE"

expired_response=$(curl -s -w "\n%{http_code}" -L -b "$COOKIE_FILE" "$BASE_URL/auth/login")
expired_http_code=$(echo "$expired_response" | tail -n 1)
expired_body=$(echo "$expired_response" | head -n -1)

if [ "$expired_http_code" = "200" ]; then
    if echo "$expired_body" | grep -q "sesión ha expirado\|session.*expired"; then
        print_success "Mensaje de sesión expirada mostrado correctamente"
        echo "✓ Mensaje de sesión expirada mostrado" >> "$TEST_RESULTS"
    else
        print_warning "No se encontró mensaje de sesión expirada"
        echo "! No se encontró mensaje de sesión expirada" >> "$TEST_RESULTS"
    fi
else
    print_error "Código HTTP inesperado: $expired_http_code"
    echo "✗ Código HTTP inesperado: $expired_http_code" >> "$TEST_RESULTS"
fi
echo "" >> "$TEST_RESULTS"

# ========================================
# TEST 7: Verificar que cookies inválidas se limpian
# ========================================
print_test "TEST 7: Verificar limpieza de cookies inválidas"
echo "TEST 7: Verificar limpieza de cookies inválidas" >> "$TEST_RESULTS"

# Hacer petición con cookies inválidas y capturar headers de respuesta
cleanup_response=$(curl -s -i -b "$COOKIE_FILE" "$BASE_URL/auth/login" | grep -i "set-cookie" || true)

if echo "$cleanup_response" | grep -q "access_token=.*expires\|access_token=;"; then
    print_success "Cookies siendo limpiadas (Set-Cookie con expires detectado)"
    echo "✓ Cookies siendo limpiadas correctamente" >> "$TEST_RESULTS"
else
    print_warning "No se detectó limpieza explícita de cookies"
    echo "! No se detectó limpieza explícita de cookies" >> "$TEST_RESULTS"
fi
echo "" >> "$TEST_RESULTS"

# ========================================
# RESUMEN
# ========================================
echo "" >> "$TEST_RESULTS"
echo "========================================" >> "$TEST_RESULTS"
echo "RESUMEN DE TESTS" >> "$TEST_RESULTS"
echo "========================================" >> "$TEST_RESULTS"

success_count=$(grep -c "^✓" "$TEST_RESULTS" || true)
warning_count=$(grep -c "^!" "$TEST_RESULTS" || true)
error_count=$(grep -c "^✗" "$TEST_RESULTS" || true)

echo "Tests exitosos: $success_count" >> "$TEST_RESULTS"
echo "Advertencias: $warning_count" >> "$TEST_RESULTS"
echo "Errores: $error_count" >> "$TEST_RESULTS"

echo ""
echo "========================================"
echo "RESUMEN DE TESTS"
echo "========================================"
print_success "Tests exitosos: $success_count"
print_warning "Advertencias: $warning_count"
print_error "Errores: $error_count"
echo ""
echo "Resultados completos guardados en: $TEST_RESULTS"
echo ""

# Mostrar resultados completos
cat "$TEST_RESULTS"

# Limpiar
cleanup

# Exit code basado en resultados
if [ "$error_count" -gt 0 ]; then
    exit 1
else
    exit 0
fi
