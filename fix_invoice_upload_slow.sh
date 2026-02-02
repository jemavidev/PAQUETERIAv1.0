#!/bin/bash

echo "🔧 Aplicando fix para carga lenta de facturas..."

# Detectar entorno
if [ -f "CODE/.env.staging" ]; then
    ENV="staging"
    COMPOSE_FILE="docker-compose.staging.yml"
    SERVICE="app"
else
    ENV="production"
    COMPOSE_FILE="docker-compose.prod.yml"
    SERVICE="app"
fi

echo "📍 Entorno detectado: $ENV"

# Reiniciar servicio
echo "🔄 Reiniciando servicio $SERVICE..."
docker compose -f "$COMPOSE_FILE" restart "$SERVICE"

echo "⏳ Esperando 10 segundos..."
sleep 10

# Verificar logs
echo "📋 Últimos logs:"
docker compose -f "$COMPOSE_FILE" logs --tail=20 "$SERVICE"

echo ""
echo "✅ Fix aplicado!"
echo ""
echo "📝 Cambios realizados:"
echo "  ✅ Procesamiento secuencial (1 archivo a la vez)"
echo "  ✅ Timeout de 30s por archivo en frontend"
echo "  ✅ Timeout de 60s en backend"
echo "  ✅ Optimización de parseo de PDF (solo primeras 5 páginas)"
echo "  ✅ Validación de tamaño (máximo 5MB)"
echo "  ✅ Extracción simplificada de productos"
echo "  ✅ Fix error 422 en query parameters"
echo ""
echo "🧪 Prueba subiendo 1-2 archivos primero para verificar"
echo "🌐 URL: https://staging.jemavi.co/invoices/facturas"
