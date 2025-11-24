#!/bin/bash
# Script de verificación rápida antes de hacer commit

echo "🔍 VERIFICACIÓN DE CAMBIOS - PAQUETEX v1.0"
echo "=========================================="
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contador de errores
ERRORS=0

echo "1️⃣ Verificando archivos modificados..."
MODIFIED=$(git status --short | grep "^ M" | wc -l)
NEW=$(git status --short | grep "^??" | wc -l)
echo -e "${GREEN}✅ $MODIFIED archivos modificados${NC}"
echo -e "${GREEN}✅ $NEW archivos nuevos${NC}"
echo ""

echo "2️⃣ Verificando sintaxis Python..."
for file in CODE/src/app/utils/auth.py CODE/src/app/dependencies.py CODE/src/app/routes/views.py CODE/src/main.py CODE/src/app/routes/settings_api.py; do
    if python3 -m py_compile "$file" 2>/dev/null; then
        echo -e "${GREEN}✅ $(basename $file)${NC}"
    else
        echo -e "${RED}❌ $(basename $file) - ERROR DE SINTAXIS${NC}"
        ERRORS=$((ERRORS + 1))
    fi
done
echo ""

echo "3️⃣ Verificando archivos críticos..."
FILES=(
    "CODE/src/templates/settings/settings.html"
    "CODE/src/templates/settings/_users_table.html"
    "CODE/src/static/js/settings_users.js"
    "CODE/src/app/routes/settings_api.py"
    "CODE/src/app/models/user_preferences.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $(basename $file)${NC}"
    else
        echo -e "${RED}❌ $(basename $file) - NO EXISTE${NC}"
        ERRORS=$((ERRORS + 1))
    fi
done
echo ""

echo "4️⃣ Verificando protección de endpoints de desarrollo..."
# Verificar que los endpoints de desarrollo estén protegidos
DEV_ENDPOINTS=$(grep -l "fake_token_for_development" CODE/src/app/routes/*.py 2>/dev/null)
if [ -n "$DEV_ENDPOINTS" ]; then
    # Verificar que tengan protección de producción
    PROTECTED=true
    for file in $DEV_ENDPOINTS; do
        if ! grep -q "settings.environment == \"production\"" "$file"; then
            echo -e "${RED}❌ $file tiene token de desarrollo sin protección${NC}"
            PROTECTED=false
            ERRORS=$((ERRORS + 1))
        fi
    done
    if [ "$PROTECTED" = true ]; then
        echo -e "${YELLOW}⚠️  Endpoints de desarrollo encontrados pero están protegidos${NC}"
        echo -e "${GREEN}✅ Los endpoints están bloqueados en producción${NC}"
    fi
else
    echo -e "${GREEN}✅ No se encontraron tokens de desarrollo${NC}"
fi
echo ""

echo "5️⃣ Verificando imports en __init__.py..."
if grep -q "settings_api" CODE/src/app/routes/__init__.py; then
    echo -e "${GREEN}✅ settings_api está exportado${NC}"
else
    echo -e "${RED}❌ settings_api NO está exportado${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

echo "=========================================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ VERIFICACIÓN EXITOSA - TODO CORRECTO${NC}"
    echo ""
    echo "Puedes hacer commit con:"
    echo "  git add ."
    echo "  git commit -m 'feat: Sistema de configuración unificado y correcciones de seguridad'"
    echo ""
else
    echo -e "${RED}❌ SE ENCONTRARON $ERRORS ERRORES${NC}"
    echo "Por favor, revisa los errores antes de hacer commit"
    exit 1
fi
