#!/bin/bash
# ========================================
# Script de Verificación de Templates
# ========================================

echo "🔍 VERIFICACIÓN DE TEMPLATES DE TÉRMINOS Y PRIVACIDAD"
echo "======================================================"
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Verificar archivos en el host
echo "📁 1. Verificando archivos en el host..."
echo "----------------------------------------"

if [ -f "CODE/src/templates/general/terms.html" ]; then
    echo -e "${GREEN}✅ terms.html existe en el host${NC}"
    ls -lh CODE/src/templates/general/terms.html
else
    echo -e "${RED}❌ terms.html NO existe en el host${NC}"
fi

if [ -f "CODE/src/templates/general/privacy.html" ]; then
    echo -e "${GREEN}✅ privacy.html existe en el host${NC}"
    ls -lh CODE/src/templates/general/privacy.html
else
    echo -e "${RED}❌ privacy.html NO existe en el host${NC}"
fi

echo ""

# 2. Verificar archivos dentro del contenedor
echo "🐳 2. Verificando archivos dentro del contenedor..."
echo "---------------------------------------------------"

CONTAINER_NAME="paqueteria_v1_prod_app"

if docker ps | grep -q "$CONTAINER_NAME"; then
    echo -e "${GREEN}✅ Contenedor $CONTAINER_NAME está corriendo${NC}"
    echo ""
    
    echo "Verificando templates dentro del contenedor:"
    docker exec $CONTAINER_NAME ls -lh /app/src/templates/general/terms.html 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ terms.html existe en el contenedor${NC}"
    else
        echo -e "${RED}❌ terms.html NO existe en el contenedor${NC}"
    fi
    
    docker exec $CONTAINER_NAME ls -lh /app/src/templates/general/privacy.html 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ privacy.html existe en el contenedor${NC}"
    else
        echo -e "${RED}❌ privacy.html NO existe en el contenedor${NC}"
    fi
else
    echo -e "${RED}❌ Contenedor $CONTAINER_NAME NO está corriendo${NC}"
fi

echo ""

# 3. Verificar rutas en public.py
echo "🛣️  3. Verificando rutas en public.py..."
echo "----------------------------------------"

if grep -q "@router.get(\"/terms\")" CODE/src/app/routes/public.py; then
    echo -e "${GREEN}✅ Ruta /terms configurada${NC}"
else
    echo -e "${RED}❌ Ruta /terms NO configurada${NC}"
fi

if grep -q "@router.get(\"/privacy\")" CODE/src/app/routes/public.py; then
    echo -e "${GREEN}✅ Ruta /privacy configurada${NC}"
else
    echo -e "${RED}❌ Ruta /privacy NO configurada${NC}"
fi

echo ""

# 4. Verificar PDFs
echo "📄 4. Verificando archivos PDF..."
echo "---------------------------------"

if [ -f "CODE/static/pdf/TERMINOS_Y_CONDICIONES.pdf" ]; then
    echo -e "${GREEN}✅ TERMINOS_Y_CONDICIONES.pdf existe${NC}"
    ls -lh CODE/static/pdf/TERMINOS_Y_CONDICIONES.pdf
else
    echo -e "${YELLOW}⚠️  TERMINOS_Y_CONDICIONES.pdf NO existe${NC}"
fi

if [ -f "CODE/static/pdf/POLITICAS_PRIVACIDAD.pdf" ]; then
    echo -e "${GREEN}✅ POLITICAS_PRIVACIDAD.pdf existe${NC}"
    ls -lh CODE/static/pdf/POLITICAS_PRIVACIDAD.pdf
else
    echo -e "${YELLOW}⚠️  POLITICAS_PRIVACIDAD.pdf NO existe${NC}"
fi

echo ""

# 5. Probar endpoints (si el contenedor está corriendo)
echo "🌐 5. Probando endpoints..."
echo "---------------------------"

if docker ps | grep -q "$CONTAINER_NAME"; then
    echo "Probando /terms..."
    curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:8000/terms
    
    echo "Probando /privacy..."
    curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:8000/privacy
else
    echo -e "${YELLOW}⚠️  No se pueden probar endpoints (contenedor no está corriendo)${NC}"
fi

echo ""
echo "======================================================"
echo "✅ Verificación completada"
echo "======================================================"
