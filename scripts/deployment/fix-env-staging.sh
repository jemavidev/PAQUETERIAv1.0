#!/bin/bash
# ========================================
# Script para copiar .env.staging al servidor
# ========================================

set -e

REMOTE_DIR="/home/ubuntu/paqueteria-staging"

echo "🔧 Copiando archivo .env.staging al servidor..."

# Copiar el archivo .env.staging al servidor usando el alias ssh
scp .env.staging staging:$REMOTE_DIR/.env.staging

echo "✅ Archivo .env.staging copiado exitosamente"

# Verificar que el archivo existe
echo "🔍 Verificando archivo en el servidor..."
ssh staging "ls -lh $REMOTE_DIR/.env.staging"

echo ""
echo "✅ Listo! Ahora puedes reiniciar los servicios con:"
echo "   ssh staging"
echo "   cd /home/ubuntu/paqueteria-staging"
echo "   docker-compose -f docker-compose.staging.yml down"
echo "   docker-compose -f docker-compose.staging.yml up -d"
