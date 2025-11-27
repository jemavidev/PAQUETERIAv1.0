#!/bin/bash

# ========================================
# PAQUETES EL CLUB v2.0 - Ejecutar Tests
# ========================================
# Archivo: CODE/tests/run_tests.sh
# Versión: 2.0.0
# Fecha: 2025-01-27
# ========================================

set -e  # Exit on error

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${CYAN}${BOLD}"
echo "========================================"
echo "  PAQUETES EL CLUB v2.0"
echo "  Tests de Comportamiento"
echo "========================================"
echo -e "${NC}"

# Verificar que estamos en el directorio correcto
if [ ! -f "tests/requirements-test.txt" ]; then
    echo -e "${RED}Error: Ejecutar desde el directorio CODE${NC}"
    echo "Uso: cd CODE && ./tests/run_tests.sh"
    exit 1
fi

# Función para mostrar ayuda
show_help() {
    echo "Uso: ./tests/run_tests.sh [OPCIÓN]"
    echo ""
    echo "Opciones:"
    echo "  install       Instalar dependencias de testing"
    echo "  all           Ejecutar todos los tests"
    echo "  e2e           Ejecutar solo tests E2E"
    echo "  integration   Ejecutar solo tests de integración"
    echo "  headed        Ejecutar tests con navegador visible"
    echo "  slow          Ejecutar tests en modo lento (debugging)"
    echo "  report        Generar reporte HTML"
    echo "  coverage      Ejecutar con cobertura de código"
    echo "  help          Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  ./tests/run_tests.sh install"
    echo "  ./tests/run_tests.sh all"
    echo "  ./tests/run_tests.sh e2e"
    echo "  ./tests/run_tests.sh headed"
}

# Función para instalar dependencias
install_deps() {
    echo -e "${BLUE}[1/2]${NC} Instalando dependencias de Python..."
    pip install -r tests/requirements-test.txt
    
    echo -e "${BLUE}[2/2]${NC} Instalando navegadores de Playwright..."
    playwright install chromium
    
    echo -e "${GREEN}✓ Dependencias instaladas correctamente${NC}"
}

# Función para verificar que el servidor está corriendo
check_server() {
    echo -e "${BLUE}Verificando servidor...${NC}"
    
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Servidor corriendo${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ Servidor no está corriendo${NC}"
        echo ""
        echo "Por favor, inicia el servidor primero:"
        echo "  docker-compose up -d"
        echo "  # O"
        echo "  uvicorn src.main:app --reload"
        echo ""
        return 1
    fi
}

# Función para ejecutar tests
run_tests() {
    local test_type=$1
    local extra_args=$2
    
    if ! check_server; then
        exit 1
    fi
    
    echo -e "${CYAN}Ejecutando tests: ${test_type}${NC}"
    echo ""
    
    case $test_type in
        all)
            pytest tests/ -v $extra_args
            ;;
        e2e)
            pytest tests/e2e/ -v $extra_args
            ;;
        integration)
            pytest tests/integration/ -v $extra_args
            ;;
        headed)
            pytest tests/e2e/ -v --headed $extra_args
            ;;
        slow)
            pytest tests/e2e/ -v --headed --slowmo=1000 $extra_args
            ;;
        report)
            pytest tests/ -v --html=report.html --self-contained-html $extra_args
            echo ""
            echo -e "${GREEN}✓ Reporte generado: report.html${NC}"
            ;;
        coverage)
            pytest tests/ -v --cov=src/app --cov-report=html $extra_args
            echo ""
            echo -e "${GREEN}✓ Reporte de cobertura generado: htmlcov/index.html${NC}"
            ;;
        *)
            echo -e "${RED}Tipo de test desconocido: $test_type${NC}"
            show_help
            exit 1
            ;;
    esac
}

# Main
case ${1:-help} in
    install)
        install_deps
        ;;
    all|e2e|integration|headed|slow|report|coverage)
        run_tests $1 "${@:2}"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Opción desconocida: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac

echo ""
echo -e "${CYAN}========================================${NC}"
