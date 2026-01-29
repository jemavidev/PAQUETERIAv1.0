#!/bin/bash
# Script simple para listar bases de datos usando psql

# Cargar variables de entorno
source .env.production

echo "=========================================="
echo "🔍 LISTANDO BASES DE DATOS EN AWS RDS"
echo "=========================================="
echo "📡 Host: $POSTGRES_HOST"
echo "👤 Usuario: $POSTGRES_USER"
echo "=========================================="
echo ""

# Listar bases de datos
PGPASSWORD=$POSTGRES_PASSWORD psql \
    -h $POSTGRES_HOST \
    -p $POSTGRES_PORT \
    -U $POSTGRES_USER \
    -d postgres \
    -c "\l+" \
    --pset=pager=off

echo ""
echo "=========================================="
echo "✅ Consulta completada"
echo "=========================================="
