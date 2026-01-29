#!/bin/bash
# ========================================
# Ejecutar eliminación de tablas de invoices
# ========================================

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "========================================"
echo "⚠️  ELIMINACIÓN DE SISTEMA DE INVOICES"
echo "========================================"
echo ""

# Cargar variables de entorno
if [ -f ".env.staging" ]; then
    source .env.staging
    echo "✓ Usando base de datos: $POSTGRES_DB"
elif [ -f ".env" ]; then
    source .env
    echo "✓ Usando base de datos: $POSTGRES_DB"
else
    echo "❌ No se encontró archivo .env"
    exit 1
fi

echo ""
echo "Host: $POSTGRES_HOST"
echo "Database: $POSTGRES_DB"
echo "User: $POSTGRES_USER"
echo ""

# Confirmación
echo "========================================"
echo "⚠️  ADVERTENCIA"
echo "========================================"
echo ""
echo "Se eliminarán las siguientes tablas:"
echo "  - invoice_irregularities"
echo "  - invoice_items"
echo "  - invoice_rejected_files"
echo "  - invoices"
echo "  - supplier_invoices"
echo "  - suppliers"
echo "  - cufe_records"
echo ""
echo "Esta operación es IRREVERSIBLE"
echo ""
read -p "¿Continuar? (escribe 'SI' en mayúsculas): " confirmacion

if [ "$confirmacion" != "SI" ]; then
    echo ""
    echo "❌ Operación cancelada"
    exit 0
fi

echo ""
echo "========================================"
echo "🔄 Ejecutando eliminación..."
echo "========================================"
echo ""

# Ejecutar SQL
PGPASSWORD="$POSTGRES_PASSWORD" psql \
    -h "$POSTGRES_HOST" \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_DB" \
    -p "$POSTGRES_PORT" \
    -f scripts/database/eliminar_sistema_invoices.sql

echo ""
echo "========================================"
echo "✅ ELIMINACIÓN COMPLETADA"
echo "========================================"
echo ""
