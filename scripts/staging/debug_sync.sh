#!/bin/bash
# Script de debug para sincronización

echo "🔍 DEBUG - Sistema de Sincronización"
echo "===================================="
echo ""

echo "1️⃣ Estado del servicio:"
echo "------------------------"
sudo systemctl status staging-sync-monitor --no-pager | head -15
echo ""

echo "2️⃣ Últimos 30 logs del servicio:"
echo "------------------------"
sudo journalctl -u staging-sync-monitor -n 30 --no-pager
echo ""

echo "3️⃣ Archivos temporales:"
echo "------------------------"
ls -la /tmp/staging_sync_* 2>/dev/null || echo "No hay archivos temporales"
echo ""

echo "4️⃣ Contenido de archivos señal (si existen):"
echo "------------------------"
if [ -f /tmp/staging_sync_request ]; then
    echo "📄 staging_sync_request:"
    cat /tmp/staging_sync_request
else
    echo "❌ No existe staging_sync_request"
fi
echo ""

if [ -f /tmp/staging_sync_result ]; then
    echo "📄 staging_sync_result:"
    cat /tmp/staging_sync_result
else
    echo "❌ No existe staging_sync_result"
fi
echo ""

if [ -f /tmp/staging_sync.lock ]; then
    echo "🔒 staging_sync.lock existe (sincronización en curso)"
else
    echo "✅ No hay lock (no hay sincronización en curso)"
fi
echo ""

echo "5️⃣ Proceso del monitor:"
echo "------------------------"
ps aux | grep sync_staging_monitor | grep -v grep || echo "Proceso no encontrado"
echo ""

echo "6️⃣ Permisos Docker:"
echo "------------------------"
groups | grep docker && echo "✅ Usuario en grupo docker" || echo "❌ Usuario NO en grupo docker"
docker ps &> /dev/null && echo "✅ Docker funciona" || echo "❌ Docker NO funciona"
echo ""

echo "7️⃣ Script de monitoreo:"
echo "------------------------"
ls -la ~/sync_staging_monitor.sh
echo ""

echo "===================================="
echo "✅ Debug completado"
echo ""
echo "📝 Para ver logs en tiempo real:"
echo "   sudo journalctl -u staging-sync-monitor -f"
