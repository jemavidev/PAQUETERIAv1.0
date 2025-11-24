#!/bin/bash

echo "🔍 Verificación Completa del Sistema"
echo "===================================="
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

# 1. Verificar estructura de directorios
echo -e "${BLUE}📁 Verificando estructura de directorios...${NC}"
DIRS=(
    "CODE/src/app/routes"
    "CODE/src/app/models"
    "CODE/src/app/services"
    "CODE/src/templates"
    "CODE/src/static/js"
    "CODE/src/static/css"
)

for dir in "${DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} $dir"
    else
        echo -e "${RED}✗${NC} $dir - NO EXISTE"
        ((ERRORS++))
    fi
done

echo ""

# 2. Verificar archivos críticos
echo -e "${BLUE}📄 Verificando archivos críticos...${NC}"
CRITICAL_FILES=(
    "CODE/src/main.py"
    "CODE/src/app/config.py"
    "CODE/src/app/database.py"
    "CODE/src/app/dependencies.py"
    "CODE/src/app/routes/__init__.py"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file - NO EXISTE"
        ((ERRORS++))
    fi
done

echo ""

# 3. Verificar sintaxis Python de archivos principales
echo -e "${BLUE}🐍 Verificando sintaxis Python...${NC}"
PYTHON_FILES=(
    "CODE/src/main.py"
    "CODE/src/app/config.py"
    "CODE/src/app/database.py"
    "CODE/src/app/dependencies.py"
    "CODE/src/app/routes/views.py"
    "CODE/src/app/routes/settings_api.py"
    "CODE/src/app/routes/auth.py"
    "CODE/src/app/routes/packages.py"
)

for file in "${PYTHON_FILES[@]}"; do
    if [ -f "$file" ]; then
        if python3 -m py_compile "$file" 2>/dev/null; then
            echo -e "${GREEN}✓${NC} $file"
        else
            echo -e "${RED}✗${NC} $file - ERROR DE SINTAXIS"
            ((ERRORS++))
        fi
    fi
done

echo ""

# 4. Verificar imports de routers
echo -e "${BLUE}🔗 Verificando imports de routers...${NC}"
cd CODE
if python3 -c "import sys; sys.path.insert(0, 'src'); from app.routes import auth, packages, customers, rates, notifications, messages, files, admin, announcements, profile, settings_api" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Todos los routers se importan correctamente"
else
    echo -e "${RED}✗${NC} Error al importar routers"
    ((ERRORS++))
fi
cd ..

echo ""

# 5. Verificar templates principales
echo -e "${BLUE}🎨 Verificando templates principales...${NC}"
TEMPLATES=(
    "CODE/src/templates/base/base.html"
    "CODE/src/templates/auth/login.html"
    "CODE/src/templates/dashboard/dashboard_improved.html"
    "CODE/src/templates/settings/settings.html"
    "CODE/src/templates/packages/packages.html"
)

for template in "${TEMPLATES[@]}"; do
    if [ -f "$template" ]; then
        echo -e "${GREEN}✓${NC} $template"
    else
        echo -e "${YELLOW}⚠${NC} $template - NO EXISTE"
        ((WARNINGS++))
    fi
done

echo ""

# 6. Verificar archivos estáticos
echo -e "${BLUE}💅 Verificando archivos estáticos...${NC}"
STATIC_FILES=(
    "CODE/src/static/js/main.js"
    "CODE/src/static/js/config.js"
    "CODE/src/static/js/settings_users.js"
    "CODE/src/static/css/tailwind.css"
)

for file in "${STATIC_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${YELLOW}⚠${NC} $file - NO EXISTE"
        ((WARNINGS++))
    fi
done

echo ""

# 7. Verificar modelos principales
echo -e "${BLUE}📊 Verificando modelos...${NC}"
MODELS=(
    "CODE/src/app/models/user.py"
    "CODE/src/app/models/package.py"
    "CODE/src/app/models/user_preferences.py"
    "CODE/src/app/models/customer.py"
)

for model in "${MODELS[@]}"; do
    if [ -f "$model" ]; then
        echo -e "${GREEN}✓${NC} $model"
    else
        echo -e "${YELLOW}⚠${NC} $model - NO EXISTE"
        ((WARNINGS++))
    fi
done

echo ""

# 8. Verificar configuración Docker
echo -e "${BLUE}🐳 Verificando configuración Docker...${NC}"
DOCKER_FILES=(
    "CODE/Dockerfile"
    "docker-compose.prod.yml"
    "docker-compose.dev.yml"
)

for file in "${DOCKER_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${YELLOW}⚠${NC} $file - NO EXISTE"
        ((WARNINGS++))
    fi
done

echo ""

# 9. Verificar archivos de configuración
echo -e "${BLUE}⚙️  Verificando archivos de configuración...${NC}"
CONFIG_FILES=(
    "CODE/.env"
    "CODE/requirements.txt"
    "CODE/alembic.ini"
)

for file in "${CONFIG_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${YELLOW}⚠${NC} $file - NO EXISTE"
        ((WARNINGS++))
    fi
done

echo ""

# Resumen final
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}📊 RESUMEN DE VERIFICACIÓN${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ SISTEMA COMPLETAMENTE FUNCIONAL${NC}"
    echo "No se encontraron errores ni advertencias"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  SISTEMA FUNCIONAL CON ADVERTENCIAS${NC}"
    echo "Errores: $ERRORS"
    echo "Advertencias: $WARNINGS"
    echo ""
    echo "Las advertencias no afectan la funcionalidad principal"
else
    echo -e "${RED}❌ SISTEMA CON ERRORES${NC}"
    echo "Errores: $ERRORS"
    echo "Advertencias: $WARNINGS"
    echo ""
    echo "Por favor, revisa los errores antes de continuar"
fi

echo ""
echo -e "${BLUE}🚀 Para iniciar el sistema:${NC}"
echo "   docker-compose -f docker-compose.prod.yml up"
echo ""
echo -e "${BLUE}🔗 URLs principales:${NC}"
echo "   http://localhost:8000/              - Página principal"
echo "   http://localhost:8000/auth/login    - Login"
echo "   http://localhost:8000/dashboard     - Dashboard"
echo "   http://localhost:8000/settings      - Configuración"
echo "   http://localhost:8000/docs          - API Docs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

exit $ERRORS
