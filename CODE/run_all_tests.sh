#!/bin/bash
# Script para ejecutar todas las pruebas del sistema OTP
# Versión: 1.0.0
# Fecha: 2025-11-30

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
BOLD='\033[1m'

echo ""
echo -e "${BOLD}========================================================================${NC}"
echo -e "${BOLD}🧪 EJECUTANDO TODAS LAS PRUEBAS DEL SISTEMA OTP${NC}"
echo -e "${BOLD}========================================================================${NC}"
echo ""

# Cambiar al directorio CODE
cd "$(dirname "$0")"

# Verificar que estamos en el directorio correcto
if [ ! -f "test_otp_complete.py" ]; then
    echo -e "${RED}❌ Error: No se encuentra test_otp_complete.py${NC}"
    echo -e "${YELLOW}Asegúrate de ejecutar este script desde el directorio CODE${NC}"
    exit 1
fi

# 1. Pruebas Unitarias
echo -e "${BLUE}${BOLD}📋 PASO 1: Pruebas Unitarias${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if python3 test_otp_complete.py; then
    echo ""
    echo -e "${GREEN}✅ Pruebas unitarias completadas exitosamente${NC}"
    UNIT_TESTS_PASSED=true
else
    echo ""
    echo -e "${RED}❌ Pruebas unitarias fallaron${NC}"
    UNIT_TESTS_PASSED=false
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 2. Verificar si el servidor está corriendo para pruebas de API
echo -e "${BLUE}${BOLD}📋 PASO 2: Verificar Servidor${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Servidor está corriendo${NC}"
    SERVER_RUNNING=true
else
    echo -e "${YELLOW}⚠️  Servidor no está corriendo${NC}"
    echo -e "${YELLOW}Las pruebas de API serán omitidas${NC}"
    echo ""
    echo -e "${YELLOW}Para ejecutar pruebas de API, inicia el servidor:${NC}"
    echo -e "  cd src"
    echo -e "  uvicorn main:app --reload --host 0.0.0.0 --port 8000"
    SERVER_RUNNING=false
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 3. Pruebas de API (solo si el servidor está corriendo)
if [ "$SERVER_RUNNING" = true ]; then
    echo -e "${BLUE}${BOLD}📋 PASO 3: Pruebas de API${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    if python3 test_otp_api.py; then
        echo ""
        echo -e "${GREEN}✅ Pruebas de API completadas exitosamente${NC}"
        API_TESTS_PASSED=true
    else
        echo ""
        echo -e "${RED}❌ Pruebas de API fallaron${NC}"
        API_TESTS_PASSED=false
    fi
    
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
else
    API_TESTS_PASSED="skipped"
fi

# Resumen Final
echo ""
echo -e "${BOLD}========================================================================${NC}"
echo -e "${BOLD}📊 RESUMEN FINAL DE PRUEBAS${NC}"
echo -e "${BOLD}========================================================================${NC}"
echo ""

if [ "$UNIT_TESTS_PASSED" = true ]; then
    echo -e "Pruebas Unitarias............ ${GREEN}✅ PASARON${NC}"
else
    echo -e "Pruebas Unitarias............ ${RED}❌ FALLARON${NC}"
fi

if [ "$API_TESTS_PASSED" = true ]; then
    echo -e "Pruebas de API............... ${GREEN}✅ PASARON${NC}"
elif [ "$API_TESTS_PASSED" = "skipped" ]; then
    echo -e "Pruebas de API............... ${YELLOW}⏭️  OMITIDAS${NC}"
else
    echo -e "Pruebas de API............... ${RED}❌ FALLARON${NC}"
fi

echo ""
echo -e "${BOLD}========================================================================${NC}"

# Resultado final
if [ "$UNIT_TESTS_PASSED" = true ] && ([ "$API_TESTS_PASSED" = true ] || [ "$API_TESTS_PASSED" = "skipped" ]); then
    echo -e "${GREEN}${BOLD}🎉 ¡PRUEBAS COMPLETADAS EXITOSAMENTE!${NC}"
    echo ""
    echo -e "${GREEN}El sistema OTP está funcionando correctamente.${NC}"
    
    if [ "$API_TESTS_PASSED" = "skipped" ]; then
        echo ""
        echo -e "${YELLOW}Nota: Las pruebas de API fueron omitidas porque el servidor no está corriendo.${NC}"
        echo -e "${YELLOW}Para ejecutar pruebas completas, inicia el servidor primero.${NC}"
    fi
    
    echo ""
    echo -e "${BOLD}========================================================================${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}${BOLD}❌ ALGUNAS PRUEBAS FALLARON${NC}"
    echo ""
    echo -e "${YELLOW}Revisa los errores anteriores y corrígelos.${NC}"
    echo ""
    echo -e "${BOLD}========================================================================${NC}"
    echo ""
    exit 1
fi
