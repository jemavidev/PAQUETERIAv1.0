#!/bin/bash
# Script para ejecutar migración de extraction_quality en staging

echo "🚀 EJECUTANDO MIGRACIÓN EN STAGING"
echo "=================================="
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar si estamos en el directorio correcto
if [ ! -f "CODE/add_extraction_quality_column.sql" ]; then
    echo -e "${RED}❌ Error: No se encuentra el archivo SQL${NC}"
    echo "Asegúrate de estar en el directorio raíz del proyecto"
    exit 1
fi

echo -e "${YELLOW}📋 Opciones de ejecución:${NC}"
echo ""
echo "  [1] Ejecutar en servidor remoto (staging.jemavi.co)"
echo "  [2] Ejecutar en Docker local"
echo "  [3] Ejecutar en PostgreSQL local"
echo ""
read -p "Selecciona opción [1-3]: " option

case $option in
    1)
        echo ""
        echo -e "${YELLOW}🌐 Ejecutando en servidor remoto...${NC}"
        echo ""
        
        # Verificar si tenemos acceso SSH
        read -p "Usuario SSH (ej: ubuntu, admin): " ssh_user
        read -p "Host (ej: staging.jemavi.co): " ssh_host
        
        echo ""
        echo -e "${YELLOW}📤 Copiando archivo SQL al servidor...${NC}"
        scp CODE/add_extraction_quality_column.sql ${ssh_user}@${ssh_host}:/tmp/
        
        echo ""
        echo -e "${YELLOW}🔧 Ejecutando migración...${NC}"
        ssh ${ssh_user}@${ssh_host} << 'ENDSSH'
            # Buscar contenedor de PostgreSQL
            DB_CONTAINER=$(docker ps --format '{{.Names}}' | grep -E 'postgres|db' | head -1)
            
            if [ -z "$DB_CONTAINER" ]; then
                echo "❌ No se encontró contenedor de PostgreSQL"
                exit 1
            fi
            
            echo "✅ Contenedor encontrado: $DB_CONTAINER"
            echo ""
            
            # Ejecutar SQL
            docker exec -i $DB_CONTAINER psql -U postgres -d paquetex < /tmp/add_extraction_quality_column.sql
            
            # Limpiar
            rm /tmp/add_extraction_quality_column.sql
ENDSSH
        
        if [ $? -eq 0 ]; then
            echo ""
            echo -e "${GREEN}✅ Migración ejecutada exitosamente${NC}"
        else
            echo ""
            echo -e "${RED}❌ Error ejecutando migración${NC}"
            exit 1
        fi
        ;;
        
    2)
        echo ""
        echo -e "${YELLOW}🐳 Ejecutando en Docker local...${NC}"
        echo ""
        
        # Buscar contenedor de PostgreSQL
        DB_CONTAINER=$(docker ps --format '{{.Names}}' | grep -E 'postgres|db' | head -1)
        
        if [ -z "$DB_CONTAINER" ]; then
            echo -e "${RED}❌ No se encontró contenedor de PostgreSQL corriendo${NC}"
            echo "Contenedores disponibles:"
            docker ps --format 'table {{.Names}}\t{{.Status}}'
            exit 1
        fi
        
        echo -e "${GREEN}✅ Contenedor encontrado: $DB_CONTAINER${NC}"
        echo ""
        
        # Ejecutar SQL
        docker exec -i $DB_CONTAINER psql -U postgres -d paquetex < CODE/add_extraction_quality_column.sql
        
        if [ $? -eq 0 ]; then
            echo ""
            echo -e "${GREEN}✅ Migración ejecutada exitosamente${NC}"
        else
            echo ""
            echo -e "${RED}❌ Error ejecutando migración${NC}"
            exit 1
        fi
        ;;
        
    3)
        echo ""
        echo -e "${YELLOW}💾 Ejecutando en PostgreSQL local...${NC}"
        echo ""
        
        read -p "Usuario PostgreSQL [postgres]: " pg_user
        pg_user=${pg_user:-postgres}
        
        read -p "Base de datos [paquetex]: " pg_db
        pg_db=${pg_db:-paquetex}
        
        read -p "Host [localhost]: " pg_host
        pg_host=${pg_host:-localhost}
        
        read -p "Puerto [5432]: " pg_port
        pg_port=${pg_port:-5432}
        
        echo ""
        psql -U $pg_user -d $pg_db -h $pg_host -p $pg_port < CODE/add_extraction_quality_column.sql
        
        if [ $? -eq 0 ]; then
            echo ""
            echo -e "${GREEN}✅ Migración ejecutada exitosamente${NC}"
        else
            echo ""
            echo -e "${RED}❌ Error ejecutando migración${NC}"
            exit 1
        fi
        ;;
        
    *)
        echo -e "${RED}❌ Opción inválida${NC}"
        exit 1
        ;;
esac

echo ""
echo "=================================="
echo -e "${GREEN}🎉 PROCESO COMPLETADO${NC}"
echo "=================================="
echo ""
echo "Próximos pasos:"
echo "  1. Reiniciar servicios web"
echo "  2. Verificar en https://staging.jemavi.co/invoices"
echo "  3. Probar subiendo una factura"
echo ""
