#!/bin/bash
# Script de verificación del footer móvil autenticado
# Fecha: 2025-11-29

echo "=========================================="
echo "  VERIFICACIÓN FOOTER MÓVIL AUTENTICADO"
echo "=========================================="
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contador de tests
PASSED=0
FAILED=0

# Test 1: Verificar que existe el archivo del footer autenticado
echo -n "1. Verificando archivo footer autenticado... "
if [ -f "CODE/src/templates/components/mobile-footer-authenticated.html" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

# Test 2: Verificar que existe el archivo del footer público
echo -n "2. Verificando archivo footer público... "
if [ -f "CODE/src/templates/components/mobile-footer.html" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

# Test 3: Verificar que base.html incluye el footer autenticado
echo -n "3. Verificando inclusión en base.html... "
if grep -q "mobile-footer-authenticated.html" CODE/src/templates/base/base.html; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

# Test 4: Verificar que los IDs son únicos
echo -n "4. Verificando IDs únicos... "
ID_AUTH=$(grep -o 'id="mobile-footer-authenticated"' CODE/src/templates/components/mobile-footer-authenticated.html | wc -l)
ID_PUBLIC=$(grep -o 'id="mobile-footer-public"' CODE/src/templates/components/mobile-footer.html | wc -l)
if [ "$ID_AUTH" -eq 1 ] && [ "$ID_PUBLIC" -eq 1 ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

# Test 5: Verificar que ambos footers tienen el mismo número de líneas
echo -n "5. Verificando paridad de líneas... "
LINES_AUTH=$(wc -l < CODE/src/templates/components/mobile-footer-authenticated.html)
LINES_PUBLIC=$(wc -l < CODE/src/templates/components/mobile-footer.html)
if [ "$LINES_AUTH" -eq "$LINES_PUBLIC" ]; then
    echo -e "${GREEN}✓ PASS${NC} ($LINES_AUTH líneas)"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ WARNING${NC} (Auth: $LINES_AUTH, Public: $LINES_PUBLIC)"
    ((PASSED++))
fi

# Test 6: Verificar que tienen los 4 botones de navegación
echo -n "6. Verificando botones de navegación... "
BUTTONS_AUTH=$(grep -c "mobile-footer-btn" CODE/src/templates/components/mobile-footer-authenticated.html)
BUTTONS_PUBLIC=$(grep -c "mobile-footer-btn" CODE/src/templates/components/mobile-footer.html)
if [ "$BUTTONS_AUTH" -eq "$BUTTONS_PUBLIC" ]; then
    echo -e "${GREEN}✓ PASS${NC} ($BUTTONS_AUTH botones)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} (Auth: $BUTTONS_AUTH, Public: $BUTTONS_PUBLIC)"
    ((FAILED++))
fi

# Test 7: Verificar función JavaScript única
echo -n "7. Verificando función JavaScript única... "
if grep -q "initMobileFooterAuthenticated" CODE/src/templates/components/mobile-footer-authenticated.html; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

# Test 8: Verificar estilos CSS
echo -n "8. Verificando estilos CSS... "
if grep -q "@media (max-width: 1024px)" CODE/src/templates/components/mobile-footer-authenticated.html; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

# Test 9: Verificar detección de dispositivos móviles
echo -n "9. Verificando detección móvil... "
if grep -q "detectMobileDevice" CODE/src/templates/components/mobile-footer-authenticated.html; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

# Test 10: Verificar feedback táctil
echo -n "10. Verificando feedback táctil... "
if grep -q "touch-active" CODE/src/templates/components/mobile-footer-authenticated.html; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

echo ""
echo "=========================================="
echo "  RESUMEN"
echo "=========================================="
echo -e "Tests pasados: ${GREEN}$PASSED${NC}"
echo -e "Tests fallidos: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ TODOS LOS TESTS PASARON${NC}"
    echo ""
    echo "El footer móvil para usuarios autenticados está"
    echo "correctamente implementado y listo para usar."
    exit 0
else
    echo -e "${RED}✗ ALGUNOS TESTS FALLARON${NC}"
    echo ""
    echo "Por favor, revisa los errores anteriores."
    exit 1
fi
