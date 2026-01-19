#!/bin/bash
# Script para ver los últimos logs sin follow

echo "╔════════════════════════════════════════════════════════╗"
echo "║     ÚLTIMOS LOGS - STAGING                             ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

echo "📋 Últimas peticiones HTTP:"
ssh staging "docker logs --tail 200 paqueteria_staging_app 2>&1 | grep 'POST\|GET' | tail -20"

echo ""
echo "📤 Últimos uploads:"
ssh staging "docker logs --tail 200 paqueteria_staging_app 2>&1 | grep 'supplier-invoices' | tail -10"

echo ""
echo "❌ Últimos errores:"
ssh staging "docker logs --tail 200 paqueteria_staging_app 2>&1 | grep -i 'error\|exception\|traceback' | tail -10"

echo ""
echo "✅ Últimos archivos guardados en S3:"
ssh staging "docker logs --tail 200 paqueteria_staging_app 2>&1 | grep 'PDF de proveedor guardado' | tail -5"

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║     FIN DE LOGS                                        ║"
echo "╚════════════════════════════════════════════════════════╝"
