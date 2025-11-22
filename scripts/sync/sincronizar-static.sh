#!/bin/bash
# ========================================
# Script para sincronizar /CODE/static con /CODE/src/static
# ========================================
# Uso: ./sincronizar-static.sh
# ========================================

set -e

echo "🔄 Sincronizando carpetas static..."
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar que existen ambas carpetas
if [ ! -d "CODE/static" ]; then
    echo -e "${RED}❌ Error: No existe CODE/static${NC}"
    exit 1
fi

if [ ! -d "CODE/src/static" ]; then
    echo -e "${RED}❌ Error: No existe CODE/src/static${NC}"
    exit 1
fi

# Mostrar diferencias
echo -e "${YELLOW}📊 Diferencias encontradas:${NC}"
echo ""
diff -r CODE/static CODE/src/static || true
echo ""

# Preguntar al usuario
echo -e "${YELLOW}⚠️  ¿Qué deseas hacer?${NC}"
echo "1) Copiar de CODE/static → CODE/src/static (sobrescribir destino)"
echo "2) Copiar de CODE/src/static → CODE/static (sobrescribir origen)"
echo "3) Eliminar CODE/static (usar solo CODE/src/static)"
echo "4) Cancelar"
echo ""
read -p "Selecciona una opción (1-4): " opcion

case $opcion in
    1)
        echo -e "${GREEN}📦 Copiando CODE/static → CODE/src/static...${NC}"
        rsync -av --delete CODE/static/ CODE/src/static/
        echo -e "${GREEN}✅ Sincronización completada${NC}"
        ;;
    2)
        echo -e "${GREEN}📦 Copiando CODE/src/static → CODE/static...${NC}"
        rsync -av --delete CODE/src/static/ CODE/static/
        echo -e "${GREEN}✅ Sincronización completada${NC}"
        ;;
    3)
        echo -e "${YELLOW}⚠️  Esto eliminará CODE/static permanentemente${NC}"
        read -p "¿Estás seguro? (si/no): " confirmar
        if [ "$confirmar" = "si" ]; then
            echo -e "${RED}🗑️  Eliminando CODE/static...${NC}"
            rm -rf CODE/static
            echo -e "${GREEN}✅ CODE/static eliminado${NC}"
            echo -e "${GREEN}💡 Ahora solo usa CODE/src/static (montado en Docker)${NC}"
        else
            echo -e "${YELLOW}❌ Operación cancelada${NC}"
        fi
        ;;
    4)
        echo -e "${YELLOW}❌ Operación cancelada${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}❌ Opción inválida${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✨ Proceso completado${NC}"
