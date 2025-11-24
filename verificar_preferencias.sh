#!/bin/bash

echo "=========================================="
echo "VERIFICACIÓN DEL SISTEMA DE PREFERENCIAS"
echo "=========================================="
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "1. Verificando tabla customer_preferences..."
docker compose exec -T db psql -U paquetex -d paquetex_db -c "\d customer_preferences" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Tabla customer_preferences existe${NC}"
    echo ""
    echo "Estructura de la tabla:"
    docker compose exec -T db psql -U paquetex -d paquetex_db -c "\d customer_preferences"
else
    echo -e "${RED}❌ Tabla customer_preferences NO existe${NC}"
    echo ""
    echo "Creando tabla..."
    docker compose exec -T db psql -U paquetex -d paquetex_db -f /docker-entrypoint-initdb.d/crear_tabla_customer_preferences.sql
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Tabla creada exitosamente${NC}"
    else
        echo -e "${RED}❌ Error al crear la tabla${NC}"
        exit 1
    fi
fi

echo ""
echo "2. Verificando modelo Python..."
docker compose exec web python -c "from app.models.customer_preferences import CustomerPreferences; print('✅ Modelo importado correctamente')" 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Modelo Python funciona correctamente${NC}"
else
    echo -e "${RED}❌ Error al importar el modelo Python${NC}"
    exit 1
fi

echo ""
echo "3. Verificando endpoints de API..."
curl -s http://localhost:8000/docs | grep -q "customer/preferences"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Endpoints de API registrados${NC}"
else
    echo -e "${YELLOW}⚠️  No se pudo verificar los endpoints (el servidor debe estar corriendo)${NC}"
fi

echo ""
echo "4. Contando registros existentes..."
COUNT=$(docker compose exec -T db psql -U paquetex -d paquetex_db -t -c "SELECT COUNT(*) FROM customer_preferences;" 2>/dev/null | tr -d ' ')

if [ ! -z "$COUNT" ]; then
    echo -e "${GREEN}✅ Registros en customer_preferences: $COUNT${NC}"
else
    echo -e "${YELLOW}⚠️  No se pudo contar los registros${NC}"
fi

echo ""
echo "=========================================="
echo "VERIFICACIÓN COMPLETADA"
echo "=========================================="
echo ""
echo "Para probar el sistema:"
echo "1. Ve a http://localhost:8000/customers/manage"
echo "2. Haz clic en el botón morado (🔔) de cualquier cliente"
echo "3. Deberías ver el modal de preferencias"
echo ""
