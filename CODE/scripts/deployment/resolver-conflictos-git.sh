#!/bin/bash
# ========================================
# SCRIPT PARA RESOLVER CONFLICTOS DE GIT
# ========================================
# Ayuda a resolver conflictos cuando hay cambios locales
# que entran en conflicto con cambios remotos
# ========================================

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     RESOLUCIÓN DE CONFLICTOS GIT                               ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verificar que estamos en un repo Git
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Error: No estás en un repositorio Git${NC}"
    exit 1
fi

# Verificar estado
echo -e "${BLUE}📋 Verificando estado del repositorio...${NC}"
git status --short
echo ""

# Verificar si hay cambios sin commitear
if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}⚠️  Hay cambios locales sin commitear${NC}"
    echo ""
    echo "Opciones:"
    echo "  1) Guardar cambios en stash (recomendado si quieres conservarlos)"
    echo "  2) Hacer commit de los cambios locales"
    echo "  3) Descartar cambios locales (⚠️  PERDERÁS TUS CAMBIOS)"
    echo "  4) Ver diferencias antes de decidir"
    echo "  0) Cancelar"
    echo ""
    read -p "Selecciona una opción (0-4): " opcion
    
    case $opcion in
        1)
            echo ""
            echo -e "${BLUE}💾 Guardando cambios en stash...${NC}"
            read -p "Mensaje para el stash (opcional): " stash_msg
            if [ -z "$stash_msg" ]; then
                git stash push -m "Cambios locales antes de pull - $(date '+%Y-%m-%d %H:%M:%S')"
            else
                git stash push -m "$stash_msg"
            fi
            echo -e "${GREEN}✅ Cambios guardados en stash${NC}"
            echo ""
            echo -e "${BLUE}🔄 Intentando hacer pull...${NC}"
            git pull origin main
            echo ""
            echo -e "${YELLOW}💡 Para recuperar tus cambios: git stash pop${NC}"
            ;;
        2)
            echo ""
            echo -e "${BLUE}📝 Haciendo commit de cambios locales...${NC}"
            git status --short
            echo ""
            read -p "Mensaje del commit: " commit_msg
            if [ -z "$commit_msg" ]; then
                commit_msg="chore: cambios locales antes de pull"
            fi
            git add .
            git commit -m "$commit_msg"
            echo -e "${GREEN}✅ Cambios commitados${NC}"
            echo ""
            echo -e "${BLUE}🔄 Intentando hacer pull...${NC}"
            git pull origin main
            echo ""
            echo -e "${YELLOW}💡 Si hay conflictos, resuélvelos y luego: git add . && git commit${NC}"
            ;;
        3)
            echo ""
            echo -e "${RED}⚠️  ADVERTENCIA: Esto descartará TODOS los cambios locales${NC}"
            read -p "¿Estás seguro? Escribe 'SI' para confirmar: " confirmacion
            if [ "$confirmacion" = "SI" ]; then
                echo -e "${BLUE}🗑️  Descartando cambios locales...${NC}"
                git reset --hard HEAD
                git clean -fd
                echo -e "${GREEN}✅ Cambios descartados${NC}"
                echo ""
                echo -e "${BLUE}🔄 Haciendo pull...${NC}"
                git pull origin main
            else
                echo -e "${YELLOW}Operación cancelada${NC}"
                exit 0
            fi
            ;;
        4)
            echo ""
            echo -e "${BLUE}📊 Mostrando diferencias...${NC}"
            git diff
            echo ""
            echo -e "${YELLOW}Presiona Enter para continuar...${NC}"
            read
            echo ""
            echo "Ahora puedes elegir una opción (1-3) o cancelar (0)"
            read -p "Opción: " opcion2
            # Aquí se podría llamar recursivamente, pero mejor salir
            echo -e "${YELLOW}Ejecuta el script nuevamente para aplicar la opción elegida${NC}"
            ;;
        0)
            echo -e "${YELLOW}Operación cancelada${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Opción inválida${NC}"
            exit 1
            ;;
    esac
else
    echo -e "${GREEN}✅ No hay cambios locales sin commitear${NC}"
    echo ""
    echo -e "${BLUE}🔄 Haciendo pull...${NC}"
    git pull origin main
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Pull completado exitosamente${NC}"
    else
        echo -e "${RED}❌ Error al hacer pull${NC}"
        echo ""
        echo "Posibles causas:"
        echo "  - Hay conflictos que necesitan resolverse manualmente"
        echo "  - Problemas de conexión con el repositorio remoto"
        echo ""
        echo "Para ver conflictos: git status"
        echo "Para resolver conflictos manualmente:"
        echo "  1. Edita los archivos con conflictos"
        echo "  2. git add <archivo>"
        echo "  3. git commit"
        exit 1
    fi
fi

echo ""
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     PROCESO COMPLETADO                                          ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

