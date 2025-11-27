#!/bin/bash

# ========================================
# TEST INTERACTIVO: Fix de Loop de Redirección
# ========================================

BASE_URL="http://localhost:8000"
COOKIE_FILE="/tmp/test_cookies_interactive.txt"

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

# Limpiar cookies anteriores
rm -f "$COOKIE_FILE"

print_header "TEST INTERACTIVO: Fix de Loop de Redirección"

# Solicitar credenciales
echo -e "${YELLOW}Ingresa tus credenciales:${NC}"
read -p "Usuario: " username
read -sp "Contraseña: " password
echo ""
echo ""

# ========================================
# TEST 1: Login
# ========================================
print_header "TEST 1: Login con credenciales"

print_test "Intentando login con usuario: $username"

login_response=$(curl -s -w "\n%{http_code}" \
    -X POST \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=$username&password=$password" \
    -c "$COOKIE_FILE" \
    "$BASE_URL/api/auth/login")

http_code=$(echo "$login_response" | tail -n 1)
body=$(echo "$login_response" | head -n -1)

echo "HTTP Code: $http_code"
echo "Respuesta:"
echo "$body" | jq . 2>/dev/null || echo "$body"

if [ "$http_code" = "200" ]; then
    if echo "$body" | grep -q "success.*true\|access_token"; then
        print_success "Login exitoso"
        
        # Mostrar cookies
        echo ""
        print_info "Cookies establecidas:"
        if [ -f "$COOKIE_FILE" ]; then
            cat "$COOKIE_FILE" | grep -v "^#" | grep -v "^$"
        fi
    else
        print_error "Login falló - Respuesta inesperada"
        exit 1
    fi
else
    print_error "Login falló - HTTP $http_code"
    exit 1
fi

# ========================================
# TEST 2: Verificar /api/auth/me
# ========================================
print_header "TEST 2: Verificar sesión con /api/auth/me"

print_test "Consultando /api/auth/me con cookies"

me_response=$(curl -s -w "\n%{http_code}" -b "$COOKIE_FILE" "$BASE_URL/api/auth/me")
me_http_code=$(echo "$me_response" | tail -n 1)
me_body=$(echo "$me_response" | head -n -1)

echo "HTTP Code: $me_http_code"
echo "Respuesta:"
echo "$me_body" | jq . 2>/dev/null || echo "$me_body"

if [ "$me_http_code" = "200" ]; then
    print_success "Sesión válida - Usuario autenticado"
else
    print_error "Sesión inválida - HTTP $me_http_code"
fi

# ========================================
# TEST 3: Acceso a /admin
# ========================================
print_header "TEST 3: Acceso a /admin con sesión válida"

print_test "Intentando acceder a /admin"

admin_response=$(curl -s -w "\n%{http_code}" -b "$COOKIE_FILE" "$BASE_URL/admin")
admin_http_code=$(echo "$admin_response" | tail -n 1)
admin_body=$(echo "$admin_response" | head -n -1)

echo "HTTP Code: $admin_http_code"

if [ "$admin_http_code" = "200" ]; then
    if echo "$admin_body" | grep -q "Dashboard\|Administración\|admin"; then
        print_success "Acceso a /admin exitoso"
    else
        print_error "Acceso permitido pero contenido inesperado"
        echo "Primeras 500 caracteres:"
        echo "$admin_body" | head -c 500
    fi
elif [ "$admin_http_code" = "302" ] || [ "$admin_http_code" = "307" ]; then
    print_error "Redirigido - No debería pasar si la sesión es válida"
else
    print_error "Error accediendo a /admin - HTTP $admin_http_code"
fi

# ========================================
# TEST 4: Acceso a /auth/login estando autenticado
# ========================================
print_header "TEST 4: Acceso a /auth/login estando autenticado"

print_test "Intentando acceder a /auth/login (debería redirigir)"

login_page_response=$(curl -s -w "\n%{http_code}" -L -b "$COOKIE_FILE" "$BASE_URL/auth/login")
login_page_http_code=$(echo "$login_page_response" | tail -n 1)
login_page_body=$(echo "$login_page_response" | head -n -1)

echo "HTTP Code: $login_page_http_code"

if echo "$login_page_body" | grep -q "Iniciar Sesión" && echo "$login_page_body" | grep -q "password"; then
    print_error "Mostró formulario de login (debería haber redirigido)"
    print_info "Esto indica que el auto-redirect NO está funcionando"
else
    print_success "Redirigido correctamente (no mostró formulario)"
fi

# ========================================
# TEST 5: Simular token expirado
# ========================================
print_header "TEST 5: Simular token expirado"

print_test "Creando cookies con token inválido"

# Crear cookies con token inválido
cat > "$COOKIE_FILE" << EOF
# Netscape HTTP Cookie File
localhost	FALSE	/	FALSE	0	access_token	invalid_token_xyz123
localhost	FALSE	/	FALSE	0	user_id	1
localhost	FALSE	/	FALSE	0	user_name	testuser
localhost	FALSE	/	FALSE	0	user_role	admin
EOF

print_info "Cookies inválidas creadas"

print_test "Accediendo a /auth/login con token inválido"

expired_response=$(curl -s -w "\n%{http_code}" -b "$COOKIE_FILE" "$BASE_URL/auth/login")
expired_http_code=$(echo "$expired_response" | tail -n 1)
expired_body=$(echo "$expired_response" | head -n -1)

echo "HTTP Code: $expired_http_code"

if echo "$expired_body" | grep -qi "sesión ha expirado\|session.*expired"; then
    print_success "Mensaje de sesión expirada mostrado correctamente"
else
    print_error "No se encontró mensaje de sesión expirada"
    print_info "Buscando en el HTML..."
    echo "$expired_body" | grep -i "sesión\|session\|expirado\|expired" || echo "No se encontró"
fi

# Verificar si se están limpiando las cookies
print_test "Verificando limpieza de cookies"

cleanup_headers=$(curl -s -i -b "$COOKIE_FILE" "$BASE_URL/auth/login" | grep -i "set-cookie")

if echo "$cleanup_headers" | grep -q "access_token"; then
    print_success "Cookies siendo limpiadas (Set-Cookie detectado)"
    echo "$cleanup_headers"
else
    print_error "No se detectó limpieza de cookies en headers"
fi

# ========================================
# TEST 6: Verificar que /admin redirige sin autenticación
# ========================================
print_header "TEST 6: Acceso a /admin sin autenticación"

rm -f "$COOKIE_FILE"

print_test "Intentando acceder a /admin sin cookies"

no_auth_response=$(curl -s -w "\n%{http_code}" -L "$BASE_URL/admin")
no_auth_http_code=$(echo "$no_auth_response" | tail -n 1)
no_auth_body=$(echo "$no_auth_response" | head -n -1)

echo "HTTP Code: $no_auth_http_code"

if echo "$no_auth_body" | grep -q "Iniciar Sesión\|login"; then
    print_success "Redirigido correctamente a login"
else
    print_error "No redirigió a login"
fi

# ========================================
# RESUMEN
# ========================================
print_header "RESUMEN DE TESTS"

echo -e "${GREEN}Tests completados${NC}"
echo ""
echo "Para verificar manualmente:"
echo "1. Abre tu navegador en: $BASE_URL/auth/login"
echo "2. Inicia sesión con tus credenciales"
echo "3. Intenta acceder a: $BASE_URL/admin"
echo "4. Verifica que NO entres en un loop de redirección"
echo ""
echo "Archivo de cookies de prueba: $COOKIE_FILE"
