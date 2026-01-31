#!/bin/bash
# Script para revertir migraciones en STAGING REMOTO

echo "🔄 Revirtiendo migraciones en STAGING REMOTO"
echo ""
echo "⚠️  Esto eliminará las tablas:"
echo "  - invoices_v2"
echo "  - invoice_products_v2"
echo ""
read -p "¿Continuar? (escribe 'SI'): " confirm

if [ "$confirm" != "SI" ]; then
    echo "❌ Cancelado"
    exit 1
fi

echo ""
echo "Conectando a staging remoto..."

# Conectar al servidor staging y revertir
ssh ubuntu@staging << 'ENDSSH'
cd /home/ubuntu/paqueteria-staging

echo "📊 Migración actual:"
docker compose -f docker-compose.staging.yml exec -T app alembic current

echo ""
echo "🔄 Revirtiendo migración..."
docker compose -f docker-compose.staging.yml exec -T app alembic downgrade -1

echo ""
echo "📊 Migración después de revertir:"
docker compose -f docker-compose.staging.yml exec -T app alembic current

echo ""
echo "🔄 Reiniciando aplicación..."
docker compose -f docker-compose.staging.yml restart app

echo ""
echo "✅ Completado en staging remoto"
ENDSSH

echo ""
echo "✅ Proceso completado"
