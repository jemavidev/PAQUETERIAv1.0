#!/bin/bash
# Script para ver logs de upload en tiempo real

echo "╔════════════════════════════════════════════════════════╗"
echo "║     LOGS DE UPLOAD - STAGING                           ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Mostrando últimos 100 logs..."
echo "   Presiona Ctrl+C para salir"
echo ""

ssh staging 'docker logs --tail 100 -f paqueteria_staging_app 2>&1 | grep --line-buffered -E "POST|upload|supplier-invoices|ERROR|Exception|Traceback|INFO.*invoices"'
