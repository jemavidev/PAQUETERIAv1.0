#!/bin/bash
# Script para revertir migraciones en PRODUCCIÓN

echo "🚨 ADVERTENCIA: REVERTIR MIGRACIONES EN PRODUCCIÓN"
echo ""
echo "⚠️  Esto eliminará las tablas:"
echo "  - invoices_v2"
echo "  - invoice_products_v2"
echo ""
echo "🔴 ESTO AFECTARÁ PRODUCCIÓN"
echo ""
read -p "¿Estás ABSOLUTAMENTE SEGURO? (escribe 'SI ESTOY SEGURO'): " confirm

if [ "$confirm" != "SI ESTOY SEGURO" ]; then
    echo "❌ Cancelado"
    exit 1
fi

echo ""
echo "Conectando a producción (papyrus)..."

# Conectar al servidor de producción y revertir
ssh ubuntu@papyrus << 'ENDSSH'
cd /home/ubuntu/paqueteria

echo "📊 Migración actual:"
docker compose -f docker-compose.prod.yml exec -T app alembic current

echo ""
echo "🔄 Revirtiendo migración..."
docker compose -f docker-compose.prod.yml exec -T app alembic downgrade -1

echo ""
echo "📊 Migración después de revertir:"
docker compose -f docker-compose.prod.yml exec -T app alembic current

echo ""
echo "🔄 Reiniciando aplicación..."
docker compose -f docker-compose.prod.yml restart app

echo ""
echo "✅ Completado en producción"
ENDSSH

echo ""
echo "✅ Proceso completado"
