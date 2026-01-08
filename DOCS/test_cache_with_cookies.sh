#!/bin/bash
# ========================================
# Test de cache con autenticación por cookies
# ========================================

set -e

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración
BASE_URL="${1:-https://staging.jemavi.co}"
USERNAME="${2:-admin}"
PASSWORD="${3}"

# Archivo temporal para cookies
COOKIE_FILE="/tmp/staging_cookies.txt"

echo "=========================================="
echo "🧪 TEST DE CACHE CON AUTENTICACIÓN"
echo "=========================================="
echo ""
echo "URL Base: $BASE_URL"
echo "Usuario: $USERNAME"
echo ""

# Verificar que se proporcionó password
if [ -z "$PASSWORD" ]; then
    echo -e "${RED}❌ Error: Debes proporcionar la contraseña${NC}"
    echo ""
    echo "Uso:"
    echo "  $0 <url> <usuario> <password>"
    echo ""
    echo "Ejemplo:"
    echo "  $0 https://staging.jemavi.co admin mi_password"
    echo ""
    exit 1
fi

# Función para medir tiempo
measure_time_with_auth() {
    local url=$1
    local name=$2
    
    echo -e "${BLUE}📊 Test: $name${NC}"
    echo "------------------------------------------"
    
    # Primera llamada (cache miss)
    echo -n "Primera llamada (CACHE MISS): "
    time1=$(curl -s -o /dev/null -w '%{time_total}' -b "$COOKIE_FILE" "$url")
    status1=$(curl -s -o /dev/null -w '%{http_code}' -b "$COOKIE_FILE" "$url")
    echo "${time1}s (Status: $status1)"
    
    # Esperar un poco
    sleep 0.5
    
    # Segunda llamada (cache hit)
    echo -n "Segunda llamada (CACHE HIT):  "
    time2=$(curl -s -o /dev/null -w '%{time_total}' -b "$COOKIE_FILE" "$url")
    status2=$(curl -s -o /dev/null -w '%{http_code}' -b "$COOKIE_FILE" "$url")
    echo "${time2}s (Status: $status2)"
    
    # Calcular mejora
    if command -v bc &> /dev/null; then
        improvement=$(echo "scale=2; (($time1 - $time2) / $time1) * 100" | bc)
        echo -e "${GREEN}🚀 Mejora: ${improvement}%${NC}"
        
        # Evaluar resultado
        result=$(echo "$improvement > 80" | bc)
        if [ "$result" -eq 1 ]; then
            echo -e "   ${GREEN}✅ EXCELENTE: Cache funcionando óptimamente${NC}"
        else
            result=$(echo "$improvement > 50" | bc)
            if [ "$result" -eq 1 ]; then
                echo -e "   ${GREEN}✅ BUENO: Cache funcionando bien${NC}"
            else
                result=$(echo "$improvement > 20" | bc)
                if [ "$result" -eq 1 ]; then
                    echo -e "   ${YELLOW}⚠️  ACEPTABLE: Cache funcionando${NC}"
                else
                    echo -e "   ${RED}❌ PROBLEMA: Cache no está mejorando${NC}"
                fi
            fi
        fi
    fi
    echo ""
}

# Paso 1: Login y obtener cookies
echo "🔐 Paso 1: Autenticación"
echo "------------------------------------------"

# Hacer login usando form data
login_response=$(curl -s -c "$COOKIE_FILE" -X POST "$BASE_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}" \
    -w "\n%{http_code}")

# Extraer status code
status_code=$(echo "$login_response" | tail -n1)
response_body=$(echo "$login_response" | head -n-1)

if [ "$status_code" = "200" ]; then
    echo -e "${GREEN}✅ Login exitoso${NC}"
    
    # Mostrar token si está en la respuesta
    if echo "$response_body" | grep -q "access_token"; then
        token=$(echo "$response_body" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', 'N/A')[:50])" 2>/dev/null || echo "N/A")
        echo "   Token: ${token}..."
    fi
    
    # Verificar que se guardaron las cookies
    if [ -f "$COOKIE_FILE" ]; then
        cookie_count=$(grep -v "^#" "$COOKIE_FILE" | wc -l)
        echo "   Cookies guardadas: $cookie_count"
    fi
else
    echo -e "${RED}❌ Login fallido (Status: $status_code)${NC}"
    echo "   Respuesta: $response_body"
    rm -f "$COOKIE_FILE"
    exit 1
fi
echo ""

# Paso 2: Verificar autenticación
echo "🔍 Paso 2: Verificar autenticación"
echo "------------------------------------------"
health_response=$(curl -s -b "$COOKIE_FILE" "$BASE_URL/health")
echo "$health_response" | python3 -m json.tool 2>/dev/null || echo "$health_response"
echo ""

# Paso 3: Tests de cache
echo "=========================================="
echo "📊 TESTS DE CACHE"
echo "=========================================="
echo ""

# Test 1: Búsqueda de paquetes
measure_time_with_auth "$BASE_URL/api/packages?limit=10" "Búsqueda de paquetes"

# Test 2: Estadísticas de dashboard
measure_time_with_auth "$BASE_URL/api/admin/dashboard" "Estadísticas de dashboard"

# Test 3: Lista de clientes
measure_time_with_auth "$BASE_URL/api/admin/customers?limit=10" "Lista de clientes"

# Test 4: Lista de usuarios
measure_time_with_auth "$BASE_URL/api/admin/users?limit=10" "Lista de usuarios"

# Limpiar
rm -f "$COOKIE_FILE"

# Resumen
echo "=========================================="
echo "✅ PRUEBAS COMPLETADAS"
echo "=========================================="
echo ""
echo "💡 Notas:"
echo "   - Cache HIT debe ser significativamente más rápido"
echo "   - Mejora esperada: >80%"
echo "   - Si no hay mejora, verificar Redis"
echo ""
