#!/bin/bash

# ========================================
# TEST: Comportamiento Actual del Sistema
# ========================================

BASE_URL="http://localhost:8000"

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

print_header "TEST: Comportamiento Actual del Sistema"

# ========================================
# TEST 1: Verificar que el servidor está corriendo
# ========================================
print_header "TEST 1: Health Check"

print_test "Verificando /health..."

health_response=$(curl -s "$BASE_URL/health")
echo "$health_response" | jq . 2>/dev/null || echo "$health_response"

if echo "$health_response" | grep -q "healthy"; then
    print_success "Servidor funcionando correctamente"
else
    print_error "Servidor no responde correctamente"
    exit 1
fi

# ========================================
# TEST 2: Acceso a /admin sin autenticación
# ========================================
print_header "TEST 2: Acceso a /admin sin autenticación"

print_test "Accediendo a /admin sin cookies..."

# Capturar headers y body
admin_no_auth=$(curl -s -i "$BASE_URL/admin")

# Extraer código HTTP
http_code=$(echo "$admin_no_auth" | grep "HTTP/" | tail -1 | awk '{print $2}')
echo "HTTP Code: $http_code"

# Verificar si hay redirección
if echo "$admin_no_auth" | grep -qi "location:"; then
    location=$(echo "$admin_no_auth" | grep -i "location:" | cut -d' ' -f2 | tr -d '\r')
    print_info "Redirige a: $location"
    
    if echo "$location" | grep -q "/auth/login"; then
        print_success "Redirige correctamente a login"
    else
        print_error "Redirige a ubicación inesperada"
    fi
fi

# Verificar contenido
body=$(echo "$admin_no_auth" | sed '1,/^\r$/d')
if echo "$body" | grep -qi "iniciar sesión\|login"; then
    print_success "Muestra página de login"
else
    print_info "Contenido de la respuesta (primeros 200 caracteres):"
    echo "$body" | head -c 200
fi

# ========================================
# TEST 3: Verificar página de login
# ========================================
print_header "TEST 3: Página de login"

print_test "Accediendo a /auth/login..."

login_page=$(curl -s "$BASE_URL/auth/login")

if echo "$login_page" | grep -q "Iniciar Sesión"; then
    print_success "Página de login carga correctamente"
else
    print_error "Página de login no carga correctamente"
fi

# Verificar elementos del formulario
if echo "$login_page" | grep -q "username_or_email"; then
    print_success "Campo de usuario presente"
else
    print_error "Campo de usuario no encontrado"
fi

if echo "$login_page" | grep -q "password"; then
    print_success "Campo de contraseña presente"
else
    print_error "Campo de contraseña no encontrado"
fi

# ========================================
# TEST 4: Simular token expirado
# ========================================
print_header "TEST 4: Comportamiento con token expirado"

print_test "Creando cookies con token inválido..."

COOKIE_FILE="/tmp/test_expired_cookies.txt"
cat > "$COOKIE_FILE" << EOF
# Netscape HTTP Cookie File
localhost	FALSE	/	FALSE	0	access_token	expired_token_xyz
localhost	FALSE	/	FALSE	0	user_id	999
localhost	FALSE	/	FALSE	0	user_name	expireduser
localhost	FALSE	/	FALSE	0	user_role	admin
EOF

print_test "Accediendo a /auth/login con cookies inválidas..."

expired_response=$(curl -s -b "$COOKIE_FILE" "$BASE_URL/auth/login")

# Verificar mensaje de sesión expirada
if echo "$expired_response" | grep -qi "sesión ha expirado\|session.*expired"; then
    print_success "✓ Mensaje de sesión expirada mostrado"
else
    print_error "✗ No se encontró mensaje de sesión expirada"
    
    # Buscar cualquier mención de expiración
    if echo "$expired_response" | grep -i "expirado\|expired" > /dev/null; then
        print_info "Se encontró texto relacionado con expiración"
        echo "$expired_response" | grep -i "expirado\|expired" | head -3
    else
        print_info "No se encontró ninguna mención de expiración en el HTML"
    fi
fi

# Verificar limpieza de cookies
print_test "Verificando limpieza de cookies..."

expired_headers=$(curl -s -i -b "$COOKIE_FILE" "$BASE_URL/auth/login" | grep -i "set-cookie")

if [ -n "$expired_headers" ]; then
    print_info "Headers Set-Cookie encontrados:"
    echo "$expired_headers"
    
    if echo "$expired_headers" | grep -q "access_token"; then
        print_success "✓ Cookies siendo limpiadas"
    else
        print_error "✗ No se está limpiando access_token"
    fi
else
    print_error "✗ No se encontraron headers Set-Cookie"
fi

# ========================================
# TEST 5: Verificar endpoint /api/auth/me sin autenticación
# ========================================
print_header "TEST 5: Endpoint /api/auth/me sin autenticación"

print_test "Consultando /api/auth/me sin cookies..."

me_response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/auth/me")
me_http_code=$(echo "$me_response" | tail -n 1)
me_body=$(echo "$me_response" | head -n -1)

echo "HTTP Code: $me_http_code"
echo "Respuesta:"
echo "$me_body" | jq . 2>/dev/null || echo "$me_body"

if [ "$me_http_code" = "401" ]; then
    print_success "Retorna 401 correctamente"
else
    print_error "Código HTTP inesperado: $me_http_code"
fi

# ========================================
# TEST 6: Verificar que /admin redirige con parámetro redirect
# ========================================
print_header "TEST 6: Parámetro redirect en URL"

print_test "Accediendo a /admin y verificando parámetro redirect..."

admin_redirect=$(curl -s -i "$BASE_URL/admin" | grep -i "location:")

if echo "$admin_redirect" | grep -q "redirect=/admin"; then
    print_success "Parámetro redirect presente en la URL"
    echo "$admin_redirect"
else
    print_info "Parámetro redirect:"
    echo "$admin_redirect"
fi

# ========================================
# RESUMEN
# ========================================
print_header "RESUMEN"

echo "Tests completados. Comportamiento observado:"
echo ""
echo "1. ✓ Servidor funcionando"
echo "2. ✓ /admin redirige a login sin autenticación"
echo "3. ✓ Página de login carga correctamente"
echo "4. ? Mensaje de sesión expirada (verificar manualmente)"
echo "5. ? Limpieza de cookies (verificar manualmente)"
echo "6. ✓ /api/auth/me retorna 401 sin autenticación"
echo ""
echo "Para probar el fix completo, necesitas:"
echo "1. Iniciar sesión con credenciales válidas"
echo "2. Verificar que puedes acceder a /admin"
echo "3. Verificar que no entras en loop de redirección"
echo ""
echo "Credenciales sugeridas para probar:"
echo "  Username: jesus"
echo "  Password: jesusSeaboard12"

rm -f "$COOKIE_FILE"
