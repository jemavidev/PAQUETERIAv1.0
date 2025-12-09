#!/bin/bash
# Script de Verificación de Integridad del Proyecto
# Verifica que todos los archivos críticos estén en su lugar y sin errores

set -e

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║           VERIFICACIÓN DE INTEGRIDAD DEL PROYECTO                          ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

ERRORS=0
WARNINGS=0

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para verificar archivo
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        return 0
    else
        echo -e "${RED}✗${NC} $1 - NO ENCONTRADO"
        ((ERRORS++))
        return 1
    fi
}

# Función para verificar directorio
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
        return 0
    else
        echo -e "${RED}✗${NC} $1/ - NO ENCONTRADO"
        ((ERRORS++))
        return 1
    fi
}

# Función para compilar Python
check_python() {
    if python3 -m py_compile "$1" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $1 - Sintaxis OK"
        return 0
    else
        echo -e "${RED}✗${NC} $1 - ERROR DE SINTAXIS"
        ((ERRORS++))
        return 1
    fi
}

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "1. VERIFICANDO ESTRUCTURA DE DIRECTORIOS"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

check_dir "src"
check_dir "src/app"
check_dir "src/app/models"
check_dir "src/app/routes"
check_dir "src/app/services"
check_dir "src/templates"
check_dir "src/static"
check_dir "alembic"
check_dir "tests"
check_dir "scripts"
check_dir "scripts/testing"
check_dir "scripts/debug"
check_dir "scripts/database"
check_dir "docs"
check_dir "docs/analisis"
check_dir "docs/implementacion"
check_dir "docs/soluciones"
check_dir "docs/pruebas"
check_dir "docs/referencias"

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "2. VERIFICANDO ARCHIVOS DE CONFIGURACIÓN"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

check_file "requirements.txt"
check_file "package.json"
check_file "alembic.ini"
check_file "Dockerfile"
check_file "env.example"
check_file "README.md"
check_file "tailwind.config.js"
check_file "uvicorn_config.py"

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "3. VERIFICANDO ARCHIVOS PRINCIPALES DEL CÓDIGO"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

check_python "src/main.py"
check_python "src/app/routes/customer_preferences_otp.py"
check_python "src/app/services/sms_service.py"
check_python "src/app/services/email_service.py"
check_python "src/app/services/customer_portal_service.py"
check_python "src/app/models/customer_preferences.py"
check_python "src/app/models/customer_otp.py"

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "4. VERIFICANDO TEMPLATES CRÍTICOS"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

check_file "src/templates/customer_portal/dashboard.html"
check_file "src/templates/customers/manage.html"
check_file "src/templates/announce/announce.html"

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "5. VERIFICANDO SCRIPTS DE PRUEBAS"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

check_python "scripts/testing/test_sistema_completo_final.py"

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "6. VERIFICANDO DOCUMENTACIÓN PRINCIPAL"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

check_file "docs/pruebas/VERIFICACION_CODIGO_COMPLETA.md"
check_file "docs/pruebas/RESUMEN_PRUEBAS_SISTEMA.md"
check_file "docs/pruebas/INSTRUCCIONES_PRUEBAS.md"
check_file "docs/pruebas/RESUMEN_FINAL_VERIFICACION.txt"
check_file "docs/README.md"
check_file "scripts/README.md"
check_file "ESTRUCTURA_PROYECTO.md"

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "7. CONTANDO ARCHIVOS"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

PYTHON_FILES=$(find src -name "*.py" -type f | wc -l)
TEMPLATE_FILES=$(find src/templates -name "*.html" -type f | wc -l)
TEST_FILES=$(find scripts/testing -name "*.py" -type f | wc -l)
DOC_FILES=$(find docs -name "*.md" -type f | wc -l)

echo "Archivos Python en src/: $PYTHON_FILES"
echo "Templates HTML: $TEMPLATE_FILES"
echo "Scripts de prueba: $TEST_FILES"
echo "Documentos Markdown: $DOC_FILES"

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "RESUMEN"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ VERIFICACIÓN EXITOSA${NC}"
    echo "Todos los archivos críticos están en su lugar y sin errores."
    echo ""
    exit 0
else
    echo -e "${RED}❌ VERIFICACIÓN FALLIDA${NC}"
    echo "Se encontraron $ERRORS errores."
    echo "Por favor, revise los archivos marcados con ✗"
    echo ""
    exit 1
fi
