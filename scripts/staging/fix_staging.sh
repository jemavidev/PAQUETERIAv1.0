#!/bin/bash
# Script para reiniciar staging correctamente

echo "=== Reiniciando servicios de staging ==="

echo -e "\n1. Deteniendo contenedor actual..."
ssh -o ConnectTimeout=10 staging 'timeout 10 docker stop paqueteria_staging_app 2>&1' || echo "Ya estaba detenido"

echo -e "\n2. Eliminando contenedor..."
ssh -o ConnectTimeout=10 staging 'timeout 5 docker rm paqueteria_staging_app 2>&1' || echo "Ya estaba eliminado"

echo -e "\n3. Verificando docker-compose..."
ssh -o ConnectTimeout=10 staging 'cd /home/stk/paqueteria-staging && timeout 5 docker-compose ps 2>&1'

echo -e "\n4. Levantando servicios con docker-compose..."
ssh -o ConnectTimeout=10 staging 'cd /home/stk/paqueteria-staging && timeout 30 docker-compose up -d 2>&1'

echo -e "\n5. Esperando 15 segundos para que inicie..."
sleep 15

echo -e "\n6. Verificando estado final..."
ssh -o ConnectTimeout=10 staging 'timeout 5 docker ps --format "table {{.Names}}\t{{.Status}}" 2>&1'

echo -e "\n7. Test de conectividad:"
ssh -o ConnectTimeout=10 staging 'timeout 5 curl -s http://localhost:8001/health 2>&1 || echo "FAILED"'

echo -e "\n=== Proceso completado ==="
