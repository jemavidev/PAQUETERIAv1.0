#!/bin/bash
# ========================================
# Script para eliminar TODOS los mensajes
# PAQUETEX - Sistema de Gestión de Paquetes
# Fecha: 2024-12-17
# ========================================

echo "=========================================="
echo "🗑️  ELIMINACIÓN DE TODOS LOS MENSAJES"
echo "=========================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar si estamos en el directorio correcto
if [ ! -f "docker-compose.prod.yml" ]; then
    echo -e "${RED}❌ Error: Este script debe ejecutarse desde el directorio raíz del proyecto${NC}"
    exit 1
fi

echo "📋 Opciones disponibles:"
echo "  1) Usar script Python (recomendado - más seguro)"
echo "  2) Usar script SQL directo"
echo "  3) Cancelar"
echo ""

read -p "Selecciona una opción (1-3): " option

case $option in
    1)
        echo ""
        echo -e "${YELLOW}🐍 Ejecutando script Python...${NC}"
        echo ""
        
        # Ejecutar dentro del contenedor backend
        docker compose -f docker-compose.prod.yml exec backend python /app/scripts/delete_all_messages.py
        
        if [ $? -eq 0 ]; then
            echo ""
            echo -e "${GREEN}✅ Script ejecutado exitosamente${NC}"
        else
            echo ""
            echo -e "${RED}❌ Error al ejecutar el script${NC}"
            exit 1
        fi
        ;;
    
    2)
        echo ""
        echo -e "${YELLOW}📊 Ejecutando script SQL...${NC}"
        echo ""
        
        # Ejecutar SQL en el contenedor de base de datos
        docker compose -f docker-compose.prod.yml exec db psql -U paquetex_user -d paquetex_db -f /scripts/delete_all_messages.sql
        
        if [ $? -eq 0 ]; then
            echo ""
            echo -e "${GREEN}✅ Script SQL ejecutado exitosamente${NC}"
        else
            echo ""
            echo -e "${RED}❌ Error al ejecutar el script SQL${NC}"
            exit 1
        fi
        ;;
    
    3)
        echo ""
        echo -e "${YELLOW}❌ Operación cancelada${NC}"
        exit 0
        ;;
    
    *)
        echo ""
        echo -e "${RED}❌ Opción inválida${NC}"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo -e "${GREEN}✅ PROCESO COMPLETADO${NC}"
echo "=========================================="
