#!/bin/bash
# Script para revertir la migración de Facturas V2

echo "⚠️  ADVERTENCIA: Esto eliminará las tablas de Facturas V2"
echo ""
echo "Tablas que se eliminarán:"
echo "  - invoices_v2"
echo "  - invoice_products_v2"
echo ""
read -p "¿Estás seguro? (escribe 'SI' para confirmar): " confirm

if [ "$confirm" != "SI" ]; then
    echo "❌ Operación cancelada"
    exit 1
fi

echo ""
echo "🔄 Revirtiendo migración..."

# Revertir a la migración anterior
docker compose -f docker-compose.staging.yml exec -T app alembic downgrade -1

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migración revertida exitosamente"
    echo ""
    echo "Reiniciando aplicación..."
    docker compose -f docker-compose.staging.yml restart app
    echo ""
    echo "✅ Completado"
else
    echo ""
    echo "❌ Error al revertir migración"
    exit 1
fi
