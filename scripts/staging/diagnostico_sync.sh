#!/bin/bash
# Script de diagnóstico para el sistema de sincronización

echo "🔍 DIAGNÓSTICO DEL SISTEMA DE SINCRONIZACIÓN"
echo "=============================================="
echo ""

echo "1️⃣ Usuario actual:"
whoami
echo ""

echo "2️⃣ Grupos del usuario:"
groups
echo ""

echo "3️⃣ Docker disponible:"
if command -v docker &> /dev/null; then
    echo "✅ Docker encontrado: $(which docker)"
    docker --version
else
    echo "❌ Docker NO encontrado"
fi
echo ""

echo "4️⃣ Permisos de Docker:"
if docker ps &> /dev/null; then
    echo "✅ Usuario puede ejecutar Docker"
else
    echo "❌ Usuario NO puede ejecutar Docker"
    echo "   Solución: sudo usermod -aG docker $USER"
    echo "   Luego: cerrar sesión y volver a conectar"
fi
echo ""

echo "5️⃣ Script de monitoreo:"
if [ -f ~/sync_staging_monitor.sh ]; then
    echo "✅ Script existe: ~/sync_staging_monitor.sh"
    ls -lh ~/sync_staging_monitor.sh
else
    echo "❌ Script NO existe"
fi
echo ""

echo "6️⃣ Servicio systemd:"
if systemctl list-unit-files | grep -q staging-sync-monitor; then
    echo "✅ Servicio instalado"
    sudo systemctl status staging-sync-monitor --no-pager | head -10
else
    echo "❌ Servicio NO instalado"
fi
echo ""

echo "7️⃣ Archivos temporales:"
ls -la /tmp/staging_sync_* 2>/dev/null || echo "No hay archivos temporales"
echo ""

echo "8️⃣ Script simple_sync.sh (alternativo):"
if [ -f ~/simple_sync.sh ]; then
    echo "✅ Script alternativo existe"
    ls -lh ~/simple_sync.sh
else
    echo "⚠️  Script alternativo NO existe (opcional)"
fi
echo ""

echo "9️⃣ Últimos logs del servicio:"
sudo journalctl -u staging-sync-monitor -n 10 --no-pager 2>/dev/null || echo "Servicio no tiene logs aún"
echo ""

echo "🔟 Conectividad a RDS:"
if command -v docker &> /dev/null && docker ps &> /dev/null; then
    echo "Probando conexión..."
    docker run --rm postgres:17-alpine \
        psql -h ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com \
        -U jveyes -d paqueteria_v4 -c "SELECT 1 as test;" 2>&1 | head -5
else
    echo "⚠️  No se puede probar (Docker no disponible)"
fi
echo ""

echo "=============================================="
echo "✅ Diagnóstico completado"
