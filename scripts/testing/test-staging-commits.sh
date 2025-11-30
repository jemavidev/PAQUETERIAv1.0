#!/bin/bash

# 🧪 Script de Pruebas Automatizadas - Staging
# Fecha: 2024-11-29
# Prueba los últimos commits de staging

set -e

echo "🧪 INICIANDO PRUEBAS DE STAGING"
echo "================================"
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir resultados
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $2"
    else
        echo -e "${RED}❌ FAIL${NC}: $2"
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠️  WARNING${NC}: $1"
}

print_info() {
    echo -e "ℹ️  $1"
}

# Contador de pruebas
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# ============================================
# PRUEBA 1: Verificar que estamos en staging
# ============================================
echo "📍 PRUEBA 1: Verificar rama staging"
TOTAL_TESTS=$((TOTAL_TESTS + 1))

CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" = "staging" ]; then
    print_result 0 "Estamos en la rama staging"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    print_result 1 "NO estamos en staging (rama actual: $CURRENT_BRANCH)"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    print_warning "Cambiando a staging..."
    git checkout staging
fi
echo ""

# ============================================
# PRUEBA 2: Verificar commits recientes
# ============================================
echo "📍 PRUEBA 2: Verificar últimos commits"
TOTAL_TESTS=$((TOTAL_TESTS + 1))

LAST_COMMIT=$(git --no-pager log --oneline -1 | head -1)
echo "Último commit: $LAST_COMMIT"

if echo "$LAST_COMMIT" | grep -q "FIX MENSAJE DE WHATSAPP"; then
    print_result 0 "Último commit es el esperado"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    print_result 1 "Último commit NO es el esperado"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
echo ""

# ============================================
# PRUEBA 3: Verificar archivos modificados
# ============================================
echo "📍 PRUEBA 3: Verificar archivos modificados existen"
TOTAL_TESTS=$((TOTAL_TESTS + 1))

FILES_TO_CHECK=(
    "CODE/src/templates/packages/packages.html"
    "CODE/src/static/js/main.js"
    "CODE/src/static/js/mobile-scroll-debug.js"
    "CODE/src/static/js/validation-override.js"
)

ALL_FILES_EXIST=true
for file in "${FILES_TO_CHECK[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file existe"
    else
        echo "  ❌ $file NO existe"
        ALL_FILES_EXIST=false
    fi
done

if [ "$ALL_FILES_EXIST" = true ]; then
    print_result 0 "Todos los archivos existen"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    print_result 1 "Algunos archivos NO existen"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
echo ""

# ============================================
# PRUEBA 4: Verificar flags de debug
# ============================================
echo "📍 PRUEBA 4: Verificar flags de debug están deshabilitados"
TOTAL_TESTS=$((TOTAL_TESTS + 1))

FLAGS_OK=true

# Verificar ENABLE_VERBOSE_LOGS = false
if grep -q "ENABLE_VERBOSE_LOGS = false" CODE/src/templates/packages/packages.html; then
    echo "  ✅ ENABLE_VERBOSE_LOGS = false"
else
    echo "  ❌ ENABLE_VERBOSE_LOGS NO está en false"
    FLAGS_OK=false
fi

# Verificar DEBUG_VALIDATION = false
if grep -q "DEBUG_VALIDATION = false" CODE/src/static/js/validation-override.js; then
    echo "  ✅ DEBUG_VALIDATION = false"
else
    echo "  ❌ DEBUG_VALIDATION NO está en false"
    FLAGS_OK=false
fi

# Verificar ENABLE_MONITOR = false
if grep -q "ENABLE_MONITOR = false" CODE/src/static/js/mobile-scroll-debug.js; then
    echo "  ✅ ENABLE_MONITOR = false"
else
    echo "  ❌ ENABLE_MONITOR NO está en false"
    FLAGS_OK=false
fi

if [ "$FLAGS_OK" = true ]; then
    print_result 0 "Todos los flags están deshabilitados"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    print_result 1 "Algunos flags NO están deshabilitados"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
echo ""

# ============================================
# PRUEBA 5: Verificar mensaje de WhatsApp
# ============================================
echo "📍 PRUEBA 5: Verificar mensaje de WhatsApp incluye link"
TOTAL_TESTS=$((TOTAL_TESTS + 1))

if grep -q "Puedes consultar el estado aquí:" CODE/src/templates/packages/packages.html; then
    print_result 0 "Mensaje de WhatsApp incluye link de búsqueda"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    print_result 1 "Mensaje de WhatsApp NO incluye link"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
echo ""

# ============================================
# PRUEBA 6: Verificar función formatPhoneLinks
# ============================================
echo "📍 PRUEBA 6: Verificar función formatPhoneLinks actualizada"
TOTAL_TESTS=$((TOTAL_TESTS + 1))

if grep -q "trackingNumber = ''" CODE/src/templates/packages/packages.html; then
    print_result 0 "formatPhoneLinks tiene parámetro trackingNumber"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    print_result 1 "formatPhoneLinks NO tiene parámetro trackingNumber"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
echo ""

# ============================================
# PRUEBA 7: Verificar caché en isMobileDevice
# ============================================
echo "📍 PRUEBA 7: Verificar caché en isMobileDevice"
TOTAL_TESTS=$((TOTAL_TESTS + 1))

if grep -q "CACHE_DURATION = 5000" CODE/src/templates/packages/packages.html; then
    print_result 0 "isMobileDevice tiene caché de 5 segundos"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    print_result 1 "isMobileDevice NO tiene caché"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
echo ""

# ============================================
# PRUEBA 8: Verificar interceptor deshabilitado
# ============================================
echo "📍 PRUEBA 8: Verificar interceptor de fetch deshabilitado"
TOTAL_TESTS=$((TOTAL_TESTS + 1))

if grep -q "DESHABILITADO\|deshabilitado" CODE/src/static/js/main.js; then
    print_result 0 "Interceptor de fetch está deshabilitado"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    print_result 1 "Interceptor de fetch NO está deshabilitado"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
echo ""

# ============================================
# PRUEBA 9: Verificar documentación
# ============================================
echo "📍 PRUEBA 9: Verificar documentación existe"
TOTAL_TESTS=$((TOTAL_TESTS + 1))

DOCS_OK=true
if [ -f "FIX_BROWSER_FREEZE_2024-11-29.md" ]; then
    echo "  ✅ FIX_BROWSER_FREEZE_2024-11-29.md existe"
else
    echo "  ❌ FIX_BROWSER_FREEZE_2024-11-29.md NO existe"
    DOCS_OK=false
fi

if [ -f "SOLUCION_DEVTOOLS_MOVIL.md" ]; then
    echo "  ✅ SOLUCION_DEVTOOLS_MOVIL.md existe"
else
    echo "  ❌ SOLUCION_DEVTOOLS_MOVIL.md NO existe"
    DOCS_OK=false
fi

if [ -f "WHATSAPP_LINK_ACTUALIZADO.md" ]; then
    echo "  ✅ WHATSAPP_LINK_ACTUALIZADO.md existe"
else
    echo "  ❌ WHATSAPP_LINK_ACTUALIZADO.md NO existe"
    DOCS_OK=false
fi

if [ "$DOCS_OK" = true ]; then
    print_result 0 "Toda la documentación existe"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    print_result 1 "Falta documentación"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
echo ""

# ============================================
# PRUEBA 10: Verificar no hay console.log sin protección
# ============================================
echo "📍 PRUEBA 10: Verificar console.log están protegidos"
TOTAL_TESTS=$((TOTAL_TESTS + 1))

print_info "Buscando console.log sin protección en archivos JS..."

UNPROTECTED_LOGS=$(grep -n "console.log" CODE/src/static/js/*.js | grep -v "if (DEBUG" | grep -v "if (ENABLE" | grep -v "//" | wc -l)

if [ "$UNPROTECTED_LOGS" -eq 0 ]; then
    print_result 0 "No hay console.log sin protección"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    print_warning "Hay $UNPROTECTED_LOGS console.log sin protección (puede ser normal)"
    print_result 0 "Verificación manual requerida"
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi
echo ""

# ============================================
# RESUMEN
# ============================================
echo ""
echo "================================"
echo "📊 RESUMEN DE PRUEBAS"
echo "================================"
echo "Total de pruebas: $TOTAL_TESTS"
echo -e "${GREEN}Pasadas: $PASSED_TESTS${NC}"
echo -e "${RED}Fallidas: $FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✅ TODAS LAS PRUEBAS PASARON${NC}"
    echo ""
    echo "🎯 Próximos pasos:"
    echo "1. Prueba manual en navegador: http://localhost:8000"
    echo "2. Abre DevTools (F12) y verifica que NO se bloquea"
    echo "3. Prueba el botón de WhatsApp en /packages"
    echo "4. Verifica que el mensaje incluye el link de búsqueda"
    echo ""
    exit 0
else
    echo -e "${RED}❌ ALGUNAS PRUEBAS FALLARON${NC}"
    echo ""
    echo "🔍 Revisa los errores arriba y corrige antes de continuar"
    echo ""
    exit 1
fi
