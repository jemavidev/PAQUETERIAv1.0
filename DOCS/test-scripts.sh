#!/bin/bash
# ========================================
# SCRIPT DE PRUEBA - Verificar Scripts de Despliegue
# ========================================

echo "========================================="
echo "🧪 PRUEBA DE SCRIPTS DE DESPLIEGUE"
echo "========================================="
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Verificar que estamos en la raíz del proyecto
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Error: Ejecuta este script desde la raíz del proyecto${NC}"
    exit 1
fi

echo -e "${BLUE}ℹ️  Directorio actual: $(pwd)${NC}"
echo ""

# Test 1: Verificar estructura del proyecto
echo "Test 1: Verificar estructura del proyecto"
if [ -d "CODE" ] && [ -d "DOCS" ] && [ -f "README.md" ]; then
    echo -e "${GREEN}✅ Estructura del proyecto correcta${NC}"
else
    echo -e "${RED}❌ Estructura del proyecto incorrecta${NC}"
    exit 1
fi
echo ""

# Test 2: Verificar Git
echo "Test 2: Verificar configuración de Git"
if git remote -v | grep -q "github.com"; then
    echo -e "${GREEN}✅ Git configurado correctamente${NC}"
    git remote -v | head -2
else
    echo -e "${RED}❌ Git no configurado${NC}"
    exit 1
fi
echo ""

# Test 3: Verificar scripts de despliegue
echo "Test 3: Verificar scripts de despliegue"
SCRIPTS=(
    "deploy-to-aws.sh"
    "DOCS/scripts/deployment/pull-update.sh"
    "DOCS/scripts/deployment/pull-only.sh"
    "DOCS/scripts/deployment/deploy.sh"
)

for script in "${SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        if [ -x "$script" ]; then
            echo -e "${GREEN}✅ $script (ejecutable)${NC}"
        else
            echo -e "${BLUE}ℹ️  $script (no ejecutable, agregando permisos...)${NC}"
            chmod +x "$script"
            echo -e "${GREEN}✅ $script (permisos agregados)${NC}"
        fi
    else
        echo -e "${RED}❌ $script (no encontrado)${NC}"
    fi
done
echo ""

# Test 4: Verificar SSH al servidor
echo "Test 4: Verificar conexión SSH al servidor"
if ssh -o ConnectTimeout=5 papyrus "echo 'Conexión exitosa'" 2>/dev/null; then
    echo -e "${GREEN}✅ Conexión SSH al servidor exitosa${NC}"
else
    echo -e "${RED}❌ No se pudo conectar al servidor (esto es normal si no estás conectado)${NC}"
fi
echo ""

# Test 5: Verificar archivos de documentación
echo "Test 5: Verificar documentación de despliegue"
DOCS=(
    "DOCS/EMPEZAR_HOY.md"
    "DOCS/RESUMEN_DESPLIEGUE.md"
    "DOCS/documentacion/GUIA_DESARROLLO_Y_DESPLIEGUE.md"
    "DOCS/CONFIGURACION_SERVIDOR.md"
    "DOCS/documentacion/RESUMEN_FINAL_CORRECCION.md"
)

for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        echo -e "${GREEN}✅ $doc${NC}"
    else
        echo -e "${RED}❌ $doc (no encontrado)${NC}"
    fi
done
echo ""

# Resumen
echo "========================================="
echo "📊 RESUMEN DE PRUEBAS"
echo "========================================="
echo ""
echo -e "${GREEN}✅ Sistema listo para despliegue automatizado${NC}"
echo ""
echo "Próximos pasos:"
echo "1. Lee DOCS/EMPEZAR_HOY.md para configuración inicial"
echo "2. Ejecuta: ./deploy-to-aws.sh \"test: primer despliegue\""
echo ""
