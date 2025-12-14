#!/bin/bash
# ════════════════════════════════════════════════════════════════════════════
# SCRIPT DE PRUEBAS - DASHBOARD UNIFICADO
# ════════════════════════════════════════════════════════════════════════════
# Prueba todos los tabs, botones y funcionalidades del dashboard
# URL: https://staging.jemavi.co/admin
# ════════════════════════════════════════════════════════════════════════════

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Variables
BASE_URL="https://staging.jemavi.co"
ADMIN_URL="$BASE_URL/admin"
RESULTS_FILE="test_results_$(date +%Y%m%d_%H%M%S).txt"

# Contadores
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# ════════════════════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ════════════════════════════════════════════════════════════════════════════

print_header() {
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_test() {
    echo -e "${BLUE}[TEST $TOTAL_TESTS]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓ PASS:${NC} $1"
    ((PASSED_TESTS++))
}

print_fail() {
    echo -e "${RED}✗ FAIL:${NC} $1"
    ((FAILED_TESTS++))
}

print_info() {
    echo -e "${YELLOW}ℹ INFO:${NC} $1"
}

test_endpoint() {
    local url="$1"
    local description="$2"
    local expected_code="${3:-200}"
    
    ((TOTAL_TESTS++))
    print_test "$description"
    
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    
    if [ "$response" -eq "$expected_code" ]; then
        print_success "Endpoint responde con código $response"
        return 0
    else
        print_fail "Esperado $expected_code, recibido $response"
        return 1
    fi
}

test_api_endpoint() {
    local url="$1"
    local description="$2"
    
    ((TOTAL_TESTS++))
    print_test "$description"
    
    local response=$(curl -s "$url")
    local http_code=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    
    if [ "$http_code" -eq 200 ] && [ -n "$response" ]; then
        print_success "API responde correctamente"
        echo "   Respuesta: ${response:0:100}..."
        return 0
    else
        print_fail "API no responde correctamente (código: $http_code)"
        return 1
    fi
}

# ════════════════════════════════════════════════════════════════════════════
# INICIO DE PRUEBAS
# ════════════════════════════════════════════════════════════════════════════

clear
print_header "PRUEBAS DEL DASHBOARD UNIFICADO"
echo "URL Base: $BASE_URL"
echo "Dashboard: $ADMIN_URL"
echo "Fecha: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# ════════════════════════════════════════════════════════════════════════════
# 1. PRUEBAS DE INFRAESTRUCTURA
# ════════════════════════════════════════════════════════════════════════════

print_header "1. PRUEBAS DE INFRAESTRUCTURA"

test_endpoint "$BASE_URL/health" "Health check del sistema"
test_endpoint "$BASE_URL" "Página principal accesible" 200
test_endpoint "$ADMIN_URL" "Dashboard admin accesible" 200

# ════════════════════════════════════════════════════════════════════════════
# 2. PRUEBAS DE APIs DEL DASHBOARD
# ════════════════════════════════════════════════════════════════════════════

print_header "2. PRUEBAS DE APIs DEL DASHBOARD"

test_api_endpoint "$BASE_URL/api/admin/dashboard?period_days=30" "API de estadísticas generales"
test_api_endpoint "$BASE_URL/api/admin/dashboard?period_days=30&include_analytics=true" "API con analytics completos"

# ════════════════════════════════════════════════════════════════════════════
# 3. PRUEBAS DE RUTAS DE GESTIÓN
# ════════════════════════════════════════════════════════════════════════════

print_header "3. PRUEBAS DE RUTAS DE GESTIÓN"

test_endpoint "$BASE_URL/admin/users" "Ruta de gestión de usuarios" 200
test_endpoint "$BASE_URL/packages" "Ruta de gestión de paquetes" 200
test_endpoint "$BASE_URL/customers" "Ruta de gestión de clientes" 200
test_endpoint "$BASE_URL/messages" "Ruta de gestión de mensajes" 200

# ════════════════════════════════════════════════════════════════════════════
# 4. PRUEBAS DE CONTENIDO DEL DASHBOARD
# ════════════════════════════════════════════════════════════════════════════

print_header "4. PRUEBAS DE CONTENIDO DEL DASHBOARD"

((TOTAL_TESTS++))
print_test "Verificar que el dashboard contiene los 6 tabs"
dashboard_content=$(curl -s "$ADMIN_URL")

tabs_found=0
if echo "$dashboard_content" | grep -q "tab-dashboard"; then ((tabs_found++)); fi
if echo "$dashboard_content" | grep -q "tab-users"; then ((tabs_found++)); fi
if echo "$dashboard_content" | grep -q "tab-packages"; then ((tabs_found++)); fi
if echo "$dashboard_content" | grep -q "tab-customers"; then ((tabs_found++)); fi
if echo "$dashboard_content" | grep -q "tab-messages"; then ((tabs_found++)); fi
if echo "$dashboard_content" | grep -q "tab-settings"; then ((tabs_found++)); fi

if [ "$tabs_found" -eq 6 ]; then
    print_success "Los 6 tabs están presentes en el HTML"
else
    print_fail "Solo se encontraron $tabs_found de 6 tabs"
fi

# ════════════════════════════════════════════════════════════════════════════
# 5. PRUEBAS DE FUNCIONES JAVASCRIPT
# ════════════════════════════════════════════════════════════════════════════

print_header "5. PRUEBAS DE FUNCIONES JAVASCRIPT"

((TOTAL_TESTS++))
print_test "Verificar función switchTab()"
if echo "$dashboard_content" | grep -q "function switchTab"; then
    print_success "Función switchTab() encontrada"
else
    print_fail "Función switchTab() no encontrada"
fi

((TOTAL_TESTS++))
print_test "Verificar función loadDashboardStats()"
if echo "$dashboard_content" | grep -q "function loadDashboardStats"; then
    print_success "Función loadDashboardStats() encontrada"
else
    print_fail "Función loadDashboardStats() no encontrada"
fi

((TOTAL_TESTS++))
print_test "Verificar función loadUsersTab()"
if echo "$dashboard_content" | grep -q "function loadUsersTab"; then
    print_success "Función loadUsersTab() encontrada"
else
    print_fail "Función loadUsersTab() no encontrada"
fi

((TOTAL_TESTS++))
print_test "Verificar función loadPackagesTab()"
if echo "$dashboard_content" | grep -q "function loadPackagesTab"; then
    print_success "Función loadPackagesTab() encontrada"
else
    print_fail "Función loadPackagesTab() no encontrada"
fi

((TOTAL_TESTS++))
print_test "Verificar función loadCustomersTab()"
if echo "$dashboard_content" | grep -q "function loadCustomersTab"; then
    print_success "Función loadCustomersTab() encontrada"
else
    print_fail "Función loadCustomersTab() no encontrada"
fi

((TOTAL_TESTS++))
print_test "Verificar función loadMessagesTab()"
if echo "$dashboard_content" | grep -q "function loadMessagesTab"; then
    print_success "Función loadMessagesTab() encontrada"
else
    print_fail "Función loadMessagesTab() no encontrada"
fi

# ════════════════════════════════════════════════════════════════════════════
# 6. PRUEBAS DE ELEMENTOS DEL TAB DASHBOARD
# ════════════════════════════════════════════════════════════════════════════

print_header "6. PRUEBAS DE ELEMENTOS DEL TAB DASHBOARD"

((TOTAL_TESTS++))
print_test "Verificar sección Financiero"
if echo "$dashboard_content" | grep -q "💰 Financiero"; then
    print_success "Sección Financiero presente"
else
    print_fail "Sección Financiero no encontrada"
fi

((TOTAL_TESTS++))
print_test "Verificar sección Paquetes"
if echo "$dashboard_content" | grep -q "📦 Paquetes"; then
    print_success "Sección Paquetes presente"
else
    print_fail "Sección Paquetes no encontrada"
fi

((TOTAL_TESTS++))
print_test "Verificar sección Clientes"
if echo "$dashboard_content" | grep -q "👥 Clientes"; then
    print_success "Sección Clientes presente"
else
    print_fail "Sección Clientes no encontrada"
fi

((TOTAL_TESTS++))
print_test "Verificar sección SMS"
if echo "$dashboard_content" | grep -q "📱 SMS"; then
    print_success "Sección SMS presente"
else
    print_fail "Sección SMS no encontrada"
fi

((TOTAL_TESTS++))
print_test "Verificar sección Performance"
if echo "$dashboard_content" | grep -q "⚡ Performance"; then
    print_success "Sección Performance presente"
else
    print_fail "Sección Performance no encontrada"
fi

((TOTAL_TESTS++))
print_test "Verificar sección Salud del Sistema"
if echo "$dashboard_content" | grep -q "🏥 Salud"; then
    print_success "Sección Salud del Sistema presente"
else
    print_fail "Sección Salud del Sistema no encontrada"
fi

# ════════════════════════════════════════════════════════════════════════════
# 7. PRUEBAS DE BOTONES DE NAVEGACIÓN
# ════════════════════════════════════════════════════════════════════════════

print_header "7. PRUEBAS DE BOTONES DE NAVEGACIÓN"

((TOTAL_TESTS++))
print_test "Verificar botón 'Ir a Gestión Completa' en tab Usuarios"
if echo "$dashboard_content" | grep -q "Ir a Gestión Completa"; then
    print_success "Botón de navegación encontrado"
else
    print_fail "Botón de navegación no encontrado"
fi

((TOTAL_TESTS++))
print_test "Verificar botón 'Ver Todos los Paquetes' en tab Paquetes"
if echo "$dashboard_content" | grep -q "Ver Todos los Paquetes"; then
    print_success "Botón de navegación encontrado"
else
    print_fail "Botón de navegación no encontrado"
fi

((TOTAL_TESTS++))
print_test "Verificar botón 'Ver Todos los Clientes' en tab Clientes"
if echo "$dashboard_content" | grep -q "Ver Todos los Clientes"; then
    print_success "Botón de navegación encontrado"
else
    print_fail "Botón de navegación no encontrado"
fi

((TOTAL_TESTS++))
print_test "Verificar botón 'Ver Todos los Mensajes' en tab Mensajes"
if echo "$dashboard_content" | grep -q "Ver Todos los Mensajes"; then
    print_success "Botón de navegación encontrado"
else
    print_fail "Botón de navegación no encontrado"
fi

# ════════════════════════════════════════════════════════════════════════════
# 8. PRUEBAS DE TAB SETTINGS
# ════════════════════════════════════════════════════════════════════════════

print_header "8. PRUEBAS DE TAB SETTINGS"

((TOTAL_TESTS++))
print_test "Verificar sección Enlaces Rápidos"
if echo "$dashboard_content" | grep -q "Enlaces Rápidos"; then
    print_success "Sección Enlaces Rápidos presente"
else
    print_fail "Sección Enlaces Rápidos no encontrada"
fi

((TOTAL_TESTS++))
print_test "Verificar sección Información del Sistema"
if echo "$dashboard_content" | grep -q "Información del Sistema"; then
    print_success "Sección Información del Sistema presente"
else
    print_fail "Sección Información del Sistema no encontrada"
fi

((TOTAL_TESTS++))
print_test "Verificar sección Límites y Configuración"
if echo "$dashboard_content" | grep -q "Límites y Configuración"; then
    print_success "Sección Límites y Configuración presente"
else
    print_fail "Sección Límites y Configuración no encontrada"
fi

# ════════════════════════════════════════════════════════════════════════════
# 9. PRUEBAS DE RESPONSIVE DESIGN
# ════════════════════════════════════════════════════════════════════════════

print_header "9. PRUEBAS DE RESPONSIVE DESIGN"

((TOTAL_TESTS++))
print_test "Verificar clases responsive de Tailwind"
if echo "$dashboard_content" | grep -q "sm:"; then
    print_success "Clases responsive sm: encontradas"
else
    print_fail "Clases responsive sm: no encontradas"
fi

((TOTAL_TESTS++))
print_test "Verificar clases responsive md:"
if echo "$dashboard_content" | grep -q "md:"; then
    print_success "Clases responsive md: encontradas"
else
    print_fail "Clases responsive md: no encontradas"
fi

((TOTAL_TESTS++))
print_test "Verificar clases responsive lg:"
if echo "$dashboard_content" | grep -q "lg:"; then
    print_success "Clases responsive lg: encontradas"
else
    print_fail "Clases responsive lg: no encontradas"
fi

# ════════════════════════════════════════════════════════════════════════════
# 10. PRUEBAS DE ICONOS SVG
# ════════════════════════════════════════════════════════════════════════════

print_header "10. PRUEBAS DE ICONOS SVG"

((TOTAL_TESTS++))
print_test "Verificar iconos SVG en tabs"
svg_count=$(echo "$dashboard_content" | grep -o "<svg" | wc -l)
if [ "$svg_count" -gt 20 ]; then
    print_success "Encontrados $svg_count iconos SVG"
else
    print_fail "Solo se encontraron $svg_count iconos SVG (esperado > 20)"
fi

# ════════════════════════════════════════════════════════════════════════════
# RESUMEN DE RESULTADOS
# ════════════════════════════════════════════════════════════════════════════

print_header "RESUMEN DE RESULTADOS"

echo ""
echo -e "${CYAN}Total de pruebas:${NC} $TOTAL_TESTS"
echo -e "${GREEN}Pruebas exitosas:${NC} $PASSED_TESTS"
echo -e "${RED}Pruebas fallidas:${NC} $FAILED_TESTS"
echo ""

if [ "$FAILED_TESTS" -eq 0 ]; then
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ TODAS LAS PRUEBAS PASARON EXITOSAMENTE${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    exit_code=0
else
    echo -e "${RED}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}✗ ALGUNAS PRUEBAS FALLARON${NC}"
    echo -e "${RED}════════════════════════════════════════════════════════════════${NC}"
    exit_code=1
fi

echo ""
echo "Resultados guardados en: $RESULTS_FILE"
echo ""

# Guardar resultados en archivo
{
    echo "════════════════════════════════════════════════════════════════"
    echo "REPORTE DE PRUEBAS - DASHBOARD UNIFICADO"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    echo "Fecha: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "URL: $ADMIN_URL"
    echo ""
    echo "Total de pruebas: $TOTAL_TESTS"
    echo "Pruebas exitosas: $PASSED_TESTS"
    echo "Pruebas fallidas: $FAILED_TESTS"
    echo ""
    if [ "$FAILED_TESTS" -eq 0 ]; then
        echo "Estado: ✓ TODAS LAS PRUEBAS PASARON"
    else
        echo "Estado: ✗ ALGUNAS PRUEBAS FALLARON"
    fi
    echo ""
    echo "════════════════════════════════════════════════════════════════"
} > "$RESULTS_FILE"

exit $exit_code
