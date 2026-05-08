#!/bin/bash
set -e

PROJECT_PATH="/home/ubuntu/paqueteria-staging"
SLOT_FILE="$PROJECT_PATH/active-slot"
UPSTREAM_CONF="$PROJECT_PATH/active-upstream.conf"

# Leer slot activo (default: blue en primer deploy)
active=$(cat "$SLOT_FILE" 2>/dev/null || echo "blue")
if [ "$active" = "blue" ]; then
    inactive="green"; inactive_port=8002; active_port=8001
else
    inactive="blue"; inactive_port=8001; active_port=8002
fi

echo "🔄 Deploy: activo=$active ($active_port) → construyendo $inactive ($inactive_port)"
cd "$PROJECT_PATH"

# 1. Construir imagen del slot inactivo
echo "🔨 Build: app_$inactive"
docker compose -f docker-compose.staging.yml --profile blue --profile green build "app_$inactive"

# 2. Levantar slot inactivo (sin tocar el activo)
echo "⬆️  Levantar: app_$inactive"
docker compose -f docker-compose.staging.yml --profile blue --profile green up -d "app_$inactive"

# 3. Migraciones en slot inactivo
echo "🗄️  Migraciones: alembic upgrade head"
docker exec "paqueteria_staging_$inactive" sh -c 'cd /app && alembic upgrade head' || {
    echo "❌ Migration falló - abortando, slot activo no cambia"
    docker compose -f docker-compose.staging.yml stop "app_$inactive"
    exit 1
}

# 4. Health check (max 30 segundos) con pre-warmup
echo "⏳ Pre-warmup del contenedor (5s)..."
sleep 5

echo "⏳ Health check en puerto $inactive_port..."
for i in $(seq 1 10); do
    response=$(curl -s -w "
%{http_code}" "http://localhost:$inactive_port/health" 2>&1)
    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)

    echo "  Intento $i: HTTP $http_code"

    if [ "$http_code" = "200" ]; then
        echo "✅ Health check OK"
        break
    fi

    if [ "$i" -eq 10 ]; then
        echo "❌ Health check falló tras 30s"
        echo "   Últim response HTTP $http_code"
        echo "   Container logs:"
        docker logs "paqueteria_staging_$inactive" 2>&1 | tail -10
        echo "   Deteniendo $inactive..."
        docker compose -f docker-compose.staging.yml --profile blue --profile green stop "app_$inactive"
        exit 1
    fi
    sleep 3
done

# 5. Escribir upstream y reload Nginx (zero downtime)
echo "🔄 Nginx: escribir upstream → reload"
cat > "$UPSTREAM_CONF" << EOF
upstream fastapi_staging {
    server 127.0.0.1:$inactive_port max_fails=3 fail_timeout=30s;
    keepalive 32;
}
EOF
sudo nginx -t && sudo nginx -s reload
echo "$inactive" > "$SLOT_FILE"
echo "✅ Tráfico → $inactive (puerto $inactive_port)"

# 6. Detener slot antiguo (delay para requests en vuelo)
echo "⏹️  Detener: app_$active (delay 5s para requests en vuelo)"
sleep 5
docker compose -f docker-compose.staging.yml --profile blue --profile green stop "app_$active"

echo ""
echo "🎉 Blue-Green deploy completo: $active → $inactive"
