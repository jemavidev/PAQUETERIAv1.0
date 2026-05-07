#!/bin/bash
set -e

PROJECT_PATH="/home/ubuntu/paqueteria-staging"
SLOT_FILE="$PROJECT_PATH/active-slot"
UPSTREAM_CONF="$PROJECT_PATH/active-upstream.conf"

# Leer slot activo
active=$(cat "$SLOT_FILE" 2>/dev/null || echo "blue")
if [ "$active" = "blue" ]; then
    prev="green"; prev_port=8002
else
    prev="blue"; prev_port=8001
fi

echo "🔙 Rollback: $active → $prev (puerto $prev_port)"

# Verificar que el slot anterior sigue corriendo
if ! docker ps -q -f "name=paqueteria_staging_$prev" | grep -q .; then
    echo "❌ Slot $prev no está corriendo — no se puede hacer rollback automático"
    echo "   Arrancar manualmente: docker compose -f docker-compose.staging.yml --profile blue --profile green up -d app_$prev"
    exit 1
fi

# Cambiar upstream de regreso
echo "🔄 Nginx: revert upstream → reload"
cat > "$UPSTREAM_CONF" << EOF
upstream fastapi_staging {
    server 127.0.0.1:$prev_port max_fails=3 fail_timeout=30s;
    keepalive 32;
}
EOF
sudo nginx -t && sudo nginx -s reload
echo "$prev" > "$SLOT_FILE"

# Detener slot actual
docker stop "paqueteria_staging_$active" 2>/dev/null || true

echo ""
echo "✅ Rollback completo: $active → $prev"
