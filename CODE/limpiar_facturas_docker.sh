#!/bin/bash
# Script para limpiar todas las facturas ejecutando el script Python dentro de Docker

echo "=========================================="
echo "LIMPIEZA COMPLETA DE FACTURAS"
echo "=========================================="
echo ""
echo "⚠️  ADVERTENCIA: Esta operación eliminará:"
echo "   - Todas las facturas"
echo "   - Todos los items de facturas"
echo "   - Todas las irregularidades"
echo "   - Todos los proveedores"
echo "   - Todos los archivos rechazados"
echo "   - Todos los archivos PDF"
echo ""
echo "⚠️  ESTA OPERACIÓN ES IRREVERSIBLE"
echo ""

read -p "¿Estás seguro de continuar? (escribe SI para confirmar): " confirmacion

if [ "$confirmacion" != "SI" ]; then
    echo ""
    echo "✗ Operación cancelada"
    exit 0
fi

echo ""
echo "🚀 Iniciando limpieza..."
echo ""

# Verificar qué archivo docker-compose usar
if [ -f "docker-compose.dev.yml" ]; then
    COMPOSE_FILE="docker-compose.dev.yml"
elif [ -f "docker-compose.prod.yml" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
elif [ -f "docker-compose.yml" ]; then
    COMPOSE_FILE="docker-compose.yml"
else
    echo "✗ No se encontró archivo docker-compose"
    exit 1
fi

echo "Usando: $COMPOSE_FILE"
echo ""

# Ejecutar el script dentro del contenedor
docker-compose -f $COMPOSE_FILE exec web python /app/src/limpiar_facturas.py

echo ""
echo "✅ Proceso completado"
echo ""
