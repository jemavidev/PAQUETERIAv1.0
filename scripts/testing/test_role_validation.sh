#!/bin/bash

# Script de pruebas para validación de roles
# Fecha: 7 de diciembre de 2025

echo "========================================="
echo "PRUEBAS DE VALIDACIÓN DE ROLES"
echo "========================================="
echo ""

BASE_URL="http://localhost:8001"

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir resultados
print_result() {
    local test_name="$1"
    local expected="$2"
    local actual="$3"
    
    if [ "$expected" == "$actual" ]; then
        echo -e "${GREEN}✅ PASS${NC}: $test_name"
    else
        echo -e "${RED}❌ FAIL${NC}: $test_name (Expected: $expected, Got: $actual)"
    fi
}

echo "=== TEST 1: Health Check ==="
response=$(curl -s "$BASE_URL/health")
status=$(echo "$response" | jq -r '.status')
print_result "Health Check" "healthy" "$status"
echo ""

echo "=== TEST 2: Endpoint público /api/images ==="
# Probar que /api/images es público (no requiere auth)
http_code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/images/1")
if [ "$http_code" == "200" ] || [ "$http_code" == "404" ]; then
    echo -e "${GREEN}✅ PASS${NC}: /api/images es público (HTTP $http_code)"
else
    echo -e "${RED}❌ FAIL${NC}: /api/images requiere auth (HTTP $http_code)"
fi
echo ""

echo "=== TEST 3: Endpoint protegido sin auth ==="
# Probar que endpoints protegidos requieren auth
http_code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/admin/users")
print_result "Admin endpoint sin auth" "401" "$http_code"
echo ""

echo "=== TEST 4: Verificar estructura de código ==="
# Verificar que no hay inconsistencias en el código
echo "Buscando inconsistencias en validación de roles..."

# Buscar patrones antiguos (no deberían existir)
old_pattern_count=$(grep -r "current_user.role != UserRole" /home/ubuntu/paqueteria-staging/CODE/src/app/routes/ 2>/dev/null | wc -l)
if [ "$old_pattern_count" -eq 0 ]; then
    echo -e "${GREEN}✅ PASS${NC}: No se encontraron patrones antiguos de validación"
else
    echo -e "${RED}❌ FAIL${NC}: Se encontraron $old_pattern_count patrones antiguos"
fi

# Buscar patrones nuevos (deberían existir)
new_pattern_count=$(grep -r "current_user.role.value" /home/ubuntu/paqueteria-staging/CODE/src/app/routes/ 2>/dev/null | wc -l)
if [ "$new_pattern_count" -gt 0 ]; then
    echo -e "${GREEN}✅ PASS${NC}: Se encontraron $new_pattern_count patrones nuevos de validación"
else
    echo -e "${YELLOW}⚠️  WARN${NC}: No se encontraron patrones nuevos"
fi
echo ""

echo "=== TEST 5: Verificar logs de aplicación ==="
# Verificar que no hay errores en los logs
error_count=$(docker compose -f /home/ubuntu/paqueteria-staging/docker-compose.staging.yml logs app --tail=100 2>/dev/null | grep -i "error" | grep -v "ERROR_RATE" | wc -l)
if [ "$error_count" -eq 0 ]; then
    echo -e "${GREEN}✅ PASS${NC}: No hay errores en los logs recientes"
else
    echo -e "${YELLOW}⚠️  WARN${NC}: Se encontraron $error_count líneas con 'error' en logs"
fi
echo ""

echo "=== TEST 6: Verificar archivos modificados ==="
files_to_check=(
    "/home/ubuntu/paqueteria-staging/CODE/src/app/routes/api.py"
    "/home/ubuntu/paqueteria-staging/CODE/src/app/routes/admin.py"
    "/home/ubuntu/paqueteria-staging/CODE/src/app/routes/protected.py"
    "/home/ubuntu/paqueteria-staging/CODE/src/app/routes/debug.py"
)

for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        # Verificar que el archivo contiene el patrón nuevo
        if grep -q "role.value" "$file"; then
            echo -e "${GREEN}✅ PASS${NC}: $(basename $file) usa validación consistente"
        else
            echo -e "${YELLOW}⚠️  WARN${NC}: $(basename $file) no contiene patrón nuevo"
        fi
    else
        echo -e "${RED}❌ FAIL${NC}: $(basename $file) no existe"
    fi
done
echo ""

echo "========================================="
echo "RESUMEN DE PRUEBAS"
echo "========================================="
echo ""
echo "Fecha: $(date)"
echo "Servidor: staging.jemavi.co"
echo "Puerto: 8001"
echo ""
echo "✅ Todas las pruebas de estructura completadas"
echo "⚠️  Para pruebas funcionales completas, se requiere autenticación"
echo ""
