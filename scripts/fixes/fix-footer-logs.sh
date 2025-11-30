#!/bin/bash

# 🔧 Fix: Deshabilitar logs en footers móviles
# Fecha: 2024-11-30
# Problema: Los footers móviles causan bloqueo del navegador con logs excesivos

set -e

echo "🔧 FIX: Deshabilitando logs en footers móviles"
echo "=============================================="
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Verificar que estamos en staging
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "staging" ]; then
    echo -e "${YELLOW}⚠️  No estás en la rama staging (rama actual: $CURRENT_BRANCH)${NC}"
    echo "¿Deseas continuar de todos modos? (s/n)"
    read -r response
    if [[ ! "$response" =~ ^[Ss]$ ]]; then
        echo "Operación cancelada"
        exit 1
    fi
fi

echo "📝 Archivos modificados:"
echo "  - CODE/src/templates/components/mobile-footer.html"
echo "  - CODE/src/templates/components/mobile-footer-authenticated.html"
echo ""

# Verificar que los cambios se aplicaron
echo "🔍 Verificando cambios..."
if grep -q "ENABLE_FOOTER_LOGS = false" CODE/src/templates/components/mobile-footer.html; then
    echo -e "${GREEN}✅${NC} mobile-footer.html - Logs deshabilitados"
else
    echo "❌ mobile-footer.html - Logs NO deshabilitados"
    exit 1
fi

if grep -q "ENABLE_FOOTER_LOGS = false" CODE/src/templates/components/mobile-footer-authenticated.html; then
    echo -e "${GREEN}✅${NC} mobile-footer-authenticated.html - Logs deshabilitados"
else
    echo "❌ mobile-footer-authenticated.html - Logs NO deshabilitados"
    exit 1
fi

if grep -q "ENABLE_BADGE_SYNC = false" CODE/src/templates/components/mobile-footer-authenticated.html; then
    echo -e "${GREEN}✅${NC} mobile-footer-authenticated.html - MutationObservers deshabilitados"
else
    echo "❌ mobile-footer-authenticated.html - MutationObservers NO deshabilitados"
    exit 1
fi

echo ""
echo "📦 Haciendo commit..."
git add CODE/src/templates/components/mobile-footer.html
git add CODE/src/templates/components/mobile-footer-authenticated.html

git commit -m "FIX CRÍTICO: Deshabilitar logs y MutationObservers en footers que causan alto CPU

- Agregado flag ENABLE_FOOTER_LOGS = false en ambos footers
- Agregado flag ENABLE_BADGE_SYNC = false en mobile-footer-authenticated.html
- Deshabilitados 4 MutationObservers que monitoreaban el DOM constantemente
- Los logs de 'Detección de dispositivo' ahora están deshabilitados
- Sincronización de badges ahora es solo inicial (no en tiempo real)
- Esto previene el alto uso de CPU (12.7%) y bloqueo del navegador
- Los observers se pueden reactivar cambiando ENABLE_BADGE_SYNC a true"

echo ""
echo -e "${GREEN}✅ Commit realizado exitosamente${NC}"
echo ""
echo "🚀 Próximos pasos:"
echo "  1. Push a staging: git push origin staging"
echo "  2. Rebuild en staging: cd CODE && docker-compose -f docker-compose.staging.yml up -d --build"
echo "  3. Probar en navegador: https://staging.jemavi.co"
echo ""
