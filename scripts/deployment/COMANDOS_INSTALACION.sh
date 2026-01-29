#!/bin/bash
# Comandos para instalar el botón de sincronización en staging
# Copiar y pegar estos comandos uno por uno

echo "🚀 Instalación del Botón de Sincronización - Staging"
echo "======================================================"
echo ""

echo "📋 PASO 1: Subir archivos al servidor staging"
echo "----------------------------------------------"
echo "Ejecutar desde tu máquina local:"
echo ""
cat << 'EOF'
scp sync_staging_monitor.sh staging:~/
scp staging-sync-monitor.service staging:~/
scp setup_sync_monitor.sh staging:~/
EOF
echo ""
echo "Presiona Enter cuando hayas ejecutado estos comandos..."
read

echo ""
echo "📋 PASO 2: Conectar al servidor staging"
echo "----------------------------------------------"
echo "Ejecutar:"
echo ""
cat << 'EOF'
ssh staging
EOF
echo ""
echo "Presiona Enter cuando estés conectado al servidor..."
read

echo ""
echo "📋 PASO 3: Ejecutar instalación automática"
echo "----------------------------------------------"
echo "Ejecutar en el servidor staging:"
echo ""
cat << 'EOF'
chmod +x setup_sync_monitor.sh
./setup_sync_monitor.sh
EOF
echo ""
echo "Presiona Enter cuando la instalación haya terminado..."
read

echo ""
echo "📋 PASO 4: Verificar instalación"
echo "----------------------------------------------"
echo "Ejecutar en el servidor staging:"
echo ""
cat << 'EOF'
sudo systemctl status staging-sync-monitor
EOF
echo ""
echo "Deberías ver: Active: active (running)"
echo ""
echo "Presiona Enter para continuar..."
read

echo ""
echo "📋 PASO 5: Ver logs en tiempo real"
echo "----------------------------------------------"
echo "Ejecutar en el servidor staging:"
echo ""
cat << 'EOF'
sudo journalctl -u staging-sync-monitor -f
EOF
echo ""
echo "Deberías ver:"
echo "  🔍 Monitor de sincronización iniciado..."
echo "  📁 Esperando señal en: /tmp/staging_sync_request"
echo ""
echo "Presiona Ctrl+C para salir de los logs"
echo ""
echo "Presiona Enter para continuar..."
read

echo ""
echo "✅ INSTALACIÓN COMPLETADA"
echo "======================================================"
echo ""
echo "🎉 El botón de sincronización ya está funcionando!"
echo ""
echo "📝 Próximos pasos:"
echo "  1. Abrir staging en el navegador"
echo "  2. Ver el botón '🔄 Sincronizar' en el header"
echo "  3. Click en el botón"
echo "  4. Confirmar la acción"
echo "  5. Esperar a que complete (1-3 minutos)"
echo "  6. ✅ Listo!"
echo ""
echo "📚 Documentación:"
echo "  - Guía rápida: QUICK_INSTALL_SYNC_BUTTON.md"
echo "  - Documentación completa: SOLUCION_BOTON_SINCRONIZACION.md"
echo "  - Diagrama de flujo: DIAGRAMA_FLUJO_SINCRONIZACION.md"
echo ""
echo "🛠️ Comandos útiles:"
echo "  Ver logs:      sudo journalctl -u staging-sync-monitor -f"
echo "  Ver estado:    sudo systemctl status staging-sync-monitor"
echo "  Reiniciar:     sudo systemctl restart staging-sync-monitor"
echo "  Detener:       sudo systemctl stop staging-sync-monitor"
echo ""
