#!/bin/bash
# Script para configurar el monitor de sincronización en staging
# Ejecutar en el servidor staging como usuario rocky

set -e

echo "🚀 Configurando monitor de sincronización..."
echo ""

# 0. Verificar y agregar usuario al grupo docker
echo "🔐 Verificando permisos de Docker..."
if ! groups | grep -q docker; then
    echo "⚠️  Usuario no está en el grupo docker, agregando..."
    sudo usermod -aG docker $USER
    echo "✅ Usuario agregado al grupo docker"
    echo "⚠️  IMPORTANTE: Necesitas cerrar sesión y volver a conectar para que los cambios surtan efecto"
    echo "   Después de reconectar, ejecuta este script de nuevo."
    echo ""
    read -p "Presiona Enter para continuar o Ctrl+C para salir y reconectar..."
else
    echo "✅ Usuario ya está en el grupo docker"
fi
echo ""

# 1. Copiar el script de monitoreo
echo "📋 Copiando script de monitoreo..."
cp sync_staging_monitor.sh ~/sync_staging_monitor.sh
chmod +x ~/sync_staging_monitor.sh
echo "✅ Script copiado a ~/sync_staging_monitor.sh"
echo ""

# 2. Copiar el archivo de servicio systemd
echo "📋 Configurando servicio systemd..."
sudo cp staging-sync-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
echo "✅ Servicio configurado"
echo ""

# 3. Habilitar e iniciar el servicio
echo "🔄 Iniciando servicio..."
sudo systemctl enable staging-sync-monitor.service
sudo systemctl start staging-sync-monitor.service
echo "✅ Servicio iniciado"
echo ""

# 4. Verificar estado
echo "🔍 Verificando estado del servicio..."
sleep 2
sudo systemctl status staging-sync-monitor.service --no-pager || true
echo ""

# 5. Verificar logs
echo "📋 Últimos logs del servicio:"
sudo journalctl -u staging-sync-monitor -n 20 --no-pager
echo ""

echo "✅ Configuración completada!"
echo ""
echo "📝 Comandos útiles:"
echo "   Ver logs:      sudo journalctl -u staging-sync-monitor -f"
echo "   Ver estado:    sudo systemctl status staging-sync-monitor"
echo "   Reiniciar:     sudo systemctl restart staging-sync-monitor"
echo "   Detener:       sudo systemctl stop staging-sync-monitor"
echo ""
echo "🎉 El botón de sincronización ya debería funcionar en el navegador!"
