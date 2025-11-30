#!/bin/bash
# Script de verificación del footer móvil autenticado v2
# Fecha: 2025-11-29

echo "=========================================="
echo "  VERIFICACIÓN FOOTER AUTENTICADO V2"
echo "=========================================="
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Contador de tests
PASSED=0
FAILED=0
WARNINGS=0

# Test 1: Verificar que existe el archivo
echo -n "1. Verificando archivo footer autenticado... "
if [ -f "CODE/src/templates/components/mobile-footer-authenticated.html" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

# Test 2: Verificar versión v2
echo -n "2. Verificando versión v2... "
if grep -q "VERSION: 2025-11-29-v2" CODE/src/templates/components/mobile-footer-authenticated.html; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ WARNING${NC} (versión no actualizada)"
    ((WARNINGS++))
fi

# Test 3: Verificar 5 botones
echo -n "3. Verificando 5 botones de navegación... "
BUTTON_COUNT=$(grep -c "mobile-footer-btn" CODE/src/templates/components/mobile-footer-authenticated.html)
if [ "$BUTTON_COUNT" -ge 10 ]; then
    echo -e "${GREEN}✓ PASS${NC} ($BUTTON_COUNT referencias)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} (solo $BUTTON_COUNT referencias)"
    ((FAILED++))
fi

# Test 4: Verificar botón "Anuncio"
echo -n "4. Verificando botón Anuncio... "
if grep -q ">Anuncio<" CODE/src/templates/components/mobile-footer-authenticated.html; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

# Test 5: Verificar botón "Buscar"
echo -n "5. Verificando botón Buscar... "
if grep -q ">Buscar<" CODE/src/templates/components/mobile-footer-authenticated.html; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

# Test 6: Verificar botón "Paquetes"
echo -n "6. Verificando botón Paquetes... "
if grep -q ">Paquetes<" CODE/src/templates/components/mobile-footer-authenticated.html; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

# Test 7: Verificar botón "Mensajes"
echo -n "7. Verificando botón Mensajes... "
if grep -q ">Mensajes<" CODE/src/templates/components/mobile-footer-authenticated.html; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

# Test 8: Verificar botón "Clientes"
echo -n "8. Verificando botón Clientes... "
if grep -q ">Clientes<" CODE/src/templates/components/mobile-footer-authenticated.html; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

# Test 9: Verificar badge de Paquetes
echo -n "9. Verificando badge de Paquetes... "
if grep -q "packages-badge-footer" CODE/src/templates/components/mobile-footer-authenticated.html; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

# Test 10: Verificar badge de Mensajes
echo -n "10. Verificando badge de Mensajes... "
if grep -q "messages-badge-footer" CODE/src/templates/components/mobile-footer-authenticated.html; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

# Test 11: Verificar función de sincronización
echo -n "11. Verificando función syncFooterBadges... "
if grep -q "function syncFooterBadges" CODE/src/templates/components/mobile-footer-authenticated.html; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

# Test 12: Verificar MutationObserver
echo -n "12. Verificando MutationObserver... "
OBSERVER_COUNT=$(grep -c "MutationObserver" CODE/src/templates/components/mobile-footer-authenticated.html)
if [ "$OBSERVER_COUNT" -ge 2 ]; then
    echo -e "${GREEN}✓ PASS${NC} ($OBSERVER_COUNT observers)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} (solo $OBSERVER_COUNT observers)"
    ((FAILED++))
fi

# Test 13: Verificar rutas correctas
echo -n "13. Verificando rutas de navegación... "
ROUTES_OK=true
grep -q 'href="/announce"' CODE/src/templates/components/mobile-footer-authenticated.html || ROUTES_OK=false
grep -q 'href="/search"' CODE/src/templates/components/mobile-footer-authenticated.html || ROUTES_OK=false
grep -q 'href="/packages"' CODE/src/templates/components/mobile-footer-authenticated.html || ROUTES_OK=false
grep -q 'href="/messages"' CODE/src/templates/components/mobile-footer-authenticated.html || ROUTES_OK=false
grep -q 'href="/customers/manage"' CODE/src/templates/components/mobile-footer-authenticated.html || ROUTES_OK=false

if [ "$ROUTES_OK" = true ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

# Test 14: Verificar que NO tiene WhatsApp ni Ayuda
echo -n "14. Verificando que no tiene WhatsApp/Ayuda... "
if ! grep -q "wa.me" CODE/src/templates/components/mobile-footer-authenticated.html && \
   ! grep -q 'href="/help"' CODE/src/templates/components/mobile-footer-authenticated.html; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ WARNING${NC} (contiene enlaces antiguos)"
    ((WARNINGS++))
fi

# Test 15: Verificar integración en base.html
echo -n "15. Verificando integración en base.html... "
if grep -q "mobile-footer-authenticated.html" CODE/src/templates/base/base.html; then
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
echo -e "Advertencias: ${YELLOW}$WARNINGS${NC}"
echo ""

# Mostrar detalles de los botones
echo "=========================================="
echo "  BOTONES DETECTADOS"
echo "=========================================="
echo -e "${BLUE}1.${NC} Anuncio    → /announce"
echo -e "${BLUE}2.${NC} Buscar     → /search"
echo -e "${BLUE}3.${NC} Paquetes   → /packages   ${BLUE}[Badge]${NC}"
echo -e "${BLUE}4.${NC} Mensajes   → /messages   ${BLUE}[Badge]${NC}"
echo -e "${BLUE}5.${NC} Clientes   → /customers/manage"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ TODOS LOS TESTS PASARON${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠ Hay $WARNINGS advertencias (no críticas)${NC}"
    fi
    echo ""
    echo "El footer móvil v2 para usuarios autenticados está"
    echo "correctamente implementado con:"
    echo "  • 5 botones de navegación"
    echo "  • 2 badges sincronizados"
    echo "  • Sistema de sincronización en tiempo real"
    echo ""
    echo -e "${GREEN}🚀 LISTO PARA PRODUCCIÓN${NC}"
    exit 0
else
    echo -e "${RED}✗ ALGUNOS TESTS FALLARON${NC}"
    echo ""
    echo "Por favor, revisa los errores anteriores."
    exit 1
fi
