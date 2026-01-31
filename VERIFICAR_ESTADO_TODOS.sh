#!/bin/bash
# Script para verificar el estado de migraciones en todos los ambientes

echo "=========================================="
echo "  VERIFICACIÓN DE MIGRACIONES"
echo "=========================================="
echo ""

# 1. Staging Local
echo "📍 1. STAGING LOCAL (localhost:8001)"
echo "----------------------------------------"
if docker compose -f docker-compose.staging.yml ps | grep -q "Up"; then
    docker compose -f docker-compose.staging.yml exec -T app alembic current 2>&1 | grep -E "036db1d68539|head|Current revision"
    if [ $? -eq 0 ]; then
        echo "⚠️  Migración de Facturas V2 APLICADA"
    else
        echo "✅ Sin migración de Facturas V2"
    fi
else
    echo "❌ Contenedor no está corriendo"
fi
echo ""

# 2. Staging Remoto
echo "📍 2. STAGING REMOTO (servidor)"
echo "----------------------------------------"
ssh ubuntu@staging "cd /home/ubuntu/paqueteria-staging && docker compose -f docker-compose.staging.yml exec -T app alembic current 2>&1" | grep -E "036db1d68539|head|Current revision" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "⚠️  Migración de Facturas V2 APLICADA"
else
    echo "✅ Sin migración de Facturas V2 (o no accesible)"
fi
echo ""

# 3. Producción
echo "📍 3. PRODUCCIÓN (papyrus)"
echo "----------------------------------------"
ssh ubuntu@papyrus "cd /home/ubuntu/paqueteria && docker compose -f docker-compose.prod.yml exec -T app alembic current 2>&1" | grep -E "036db1d68539|head|Current revision" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "⚠️  Migración de Facturas V2 APLICADA"
else
    echo "✅ Sin migración de Facturas V2 (o no accesible)"
fi
echo ""

echo "=========================================="
echo "  FIN DE VERIFICACIÓN"
echo "=========================================="
