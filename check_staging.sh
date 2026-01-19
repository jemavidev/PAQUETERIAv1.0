#!/bin/bash
# Script para diagnosticar staging con timeouts apropiados

echo "=== Verificando estado de staging ==="

echo -e "\n1. Estado de contenedores:"
ssh -o ConnectTimeout=10 -o ServerAliveInterval=5 staging 'timeout 5 docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"' 2>&1 || echo "ERROR: No se pudo obtener estado de contenedores"

echo -e "\n2. Health check del contenedor:"
ssh -o ConnectTimeout=10 staging 'timeout 3 docker inspect paqueteria_staging_app --format="{{.State.Health.Status}}" 2>/dev/null || echo "No disponible"' 2>&1

echo -e "\n3. Últimas 30 líneas de logs:"
ssh -o ConnectTimeout=10 staging 'timeout 5 docker logs --tail 30 paqueteria_staging_app 2>&1' 2>&1 || echo "ERROR: No se pudieron obtener logs"

echo -e "\n4. Test de conectividad al puerto 8001:"
ssh -o ConnectTimeout=10 staging 'timeout 3 curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/health 2>/dev/null || echo "FAILED"' 2>&1

echo -e "\n5. Estado de nginx:"
ssh -o ConnectTimeout=10 staging 'timeout 3 systemctl is-active nginx' 2>&1 || echo "ERROR"

echo -e "\n=== Diagnóstico completado ==="
