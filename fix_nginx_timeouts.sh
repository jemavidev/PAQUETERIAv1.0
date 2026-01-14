#!/bin/bash
# Script para actualizar timeouts de Nginx en staging

echo "🔧 Actualizando timeouts de Nginx en staging..."

ssh staging << 'EOF'
# Backup del archivo actual
sudo cp /etc/nginx/sites-available/staging /etc/nginx/sites-available/staging.backup.$(date +%Y%m%d_%H%M%S)

# Actualizar timeouts
sudo sed -i 's/proxy_connect_timeout 10s;/proxy_connect_timeout 30s;/g' /etc/nginx/sites-available/staging
sudo sed -i 's/proxy_send_timeout 20s;/proxy_send_timeout 60s;/g' /etc/nginx/sites-available/staging
sudo sed -i 's/proxy_read_timeout 20s;/proxy_read_timeout 60s;/g' /etc/nginx/sites-available/staging

# Verificar configuración
echo "✅ Verificando configuración de Nginx..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Configuración válida, recargando Nginx..."
    sudo systemctl reload nginx
    echo "✅ Nginx recargado correctamente"
    
    echo ""
    echo "📊 Nuevos timeouts configurados:"
    grep -E "proxy_(connect|send|read)_timeout" /etc/nginx/sites-available/staging
else
    echo "❌ Error en configuración de Nginx, restaurando backup..."
    sudo cp /etc/nginx/sites-available/staging.backup.* /etc/nginx/sites-available/staging
    exit 1
fi
EOF

echo ""
echo "✅ Timeouts de Nginx actualizados correctamente"
