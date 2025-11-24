#!/bin/bash

echo "🔍 Verificando la vista de Settings..."
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contador de errores
ERRORS=0

# 1. Verificar archivos necesarios
echo "📁 Verificando archivos necesarios..."
FILES=(
    "CODE/src/templates/settings/settings.html"
    "CODE/src/templates/settings/_users_table.html"
    "CODE/src/app/routes/settings_api.py"
    "CODE/src/static/js/settings_users.js"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file - NO ENCONTRADO"
        ((ERRORS++))
    fi
done

echo ""

# 2. Verificar sintaxis Python
echo "🐍 Verificando sintaxis Python..."
PYTHON_FILES=(
    "CODE/src/app/routes/settings_api.py"
    "CODE/src/app/routes/views.py"
    "CODE/src/main.py"
)

for file in "${PYTHON_FILES[@]}"; do
    if python3 -m py_compile "$file" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file - ERROR DE SINTAXIS"
        ((ERRORS++))
    fi
done

echo ""

# 3. Verificar que settings_api esté importado en main.py
echo "🔗 Verificando importaciones..."
if grep -q "settings_api" CODE/src/main.py; then
    echo -e "${GREEN}✓${NC} settings_api importado en main.py"
else
    echo -e "${RED}✗${NC} settings_api NO importado en main.py"
    ((ERRORS++))
fi

if grep -q "settings_api" CODE/src/app/routes/__init__.py; then
    echo -e "${GREEN}✓${NC} settings_api exportado en __init__.py"
else
    echo -e "${RED}✗${NC} settings_api NO exportado en __init__.py"
    ((ERRORS++))
fi

echo ""

# 4. Verificar ruta /settings en views.py
echo "🛣️  Verificando rutas..."
if grep -q "@router.get(\"/settings\")" CODE/src/app/routes/views.py; then
    echo -e "${GREEN}✓${NC} Ruta /settings definida en views.py"
else
    echo -e "${RED}✗${NC} Ruta /settings NO definida en views.py"
    ((ERRORS++))
fi

echo ""

# 5. Verificar endpoints API
echo "🔌 Verificando endpoints API..."
API_ENDPOINTS=(
    '"/profile"'
    '"/change-password"'
    '"/notifications"'
)

for endpoint in "${API_ENDPOINTS[@]}"; do
    if grep -q "$endpoint" CODE/src/app/routes/settings_api.py; then
        echo -e "${GREEN}✓${NC} Endpoint $endpoint"
    else
        echo -e "${RED}✗${NC} Endpoint $endpoint - NO ENCONTRADO"
        ((ERRORS++))
    fi
done

echo ""

# 6. Verificar modelo UserPreferences
echo "📊 Verificando modelos..."
if [ -f "CODE/src/app/models/user_preferences.py" ]; then
    echo -e "${GREEN}✓${NC} Modelo UserPreferences existe"
else
    echo -e "${YELLOW}⚠${NC} Modelo UserPreferences NO existe (las notificaciones no funcionarán)"
fi

echo ""

# Resumen
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ VERIFICACIÓN EXITOSA${NC}"
    echo "La vista de Settings está lista para usar"
    echo ""
    echo "Para probar:"
    echo "1. Inicia el servidor: docker-compose up"
    echo "2. Accede a: http://localhost:8000/settings"
else
    echo -e "${RED}❌ VERIFICACIÓN FALLIDA${NC}"
    echo "Se encontraron $ERRORS errores"
    echo "Por favor, revisa los mensajes anteriores"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
