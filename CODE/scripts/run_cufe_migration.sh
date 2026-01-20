#!/bin/bash

# Script para ejecutar la migración de CUFE

echo "🔄 Ejecutando migración de tabla cufe_records..."

cd /app/CODE

# Ejecutar migración
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Migración ejecutada exitosamente"
else
    echo "❌ Error ejecutando migración"
    exit 1
fi
