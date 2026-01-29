#!/bin/bash
# Script para reiniciar staging en la ubicación correcta

STAGING_DIR="/home/ubuntu/paqueteria-staging"

echo "=== Reiniciando staging en $STAGING_DIR ==="

echo -e "\n1. Deteniendo servicios..."
ssh -o ConnectTimeout=10 staging "cd $STAGING_DIR && timeout 30 docker-compose -f docker-compose.staging.yml down 2>&1"

echo -e "\n2. Levantando servicios..."
ssh -o ConnectTimeout=10 staging "cd $STAGING_DIR && timeout 60 docker-compose -f docker-compose.staging.yml up -d 2>&1"

echo -e "\n3. Esperando 20 segundos para que inicie..."
sleep 20

echo -e "\n4. Estado de contenedores:"
ssh -o ConnectTimeout=10 staging 'timeout 5 docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>&1'

echo -e "\n5. Logs recientes de la app:"
ssh -o ConnectTimeout=10 staging 'timeout 5 docker logs --tail 20 paqueteria_staging_app 2>&1'

echo -e "\n6. Test de health:"
ssh -o ConnectTimeout=10 staging 'timeout 5 curl -s http://localhost:8001/health 2>&1 | head -20'

echo -e "\n=== Completado ==="
