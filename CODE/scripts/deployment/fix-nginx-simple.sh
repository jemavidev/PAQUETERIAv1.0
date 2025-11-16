#!/bin/bash
# Script simple para corregir nginx - versión manual

echo "========================================="
echo "🔧 CORRECCIÓN SIMPLE DE NGINX"
echo "========================================="
echo ""

# Buscar archivos con location /static
echo "Buscando configuración de nginx..."
CONFIG_FILE=$(find /etc/nginx -name "*.conf" -type f -exec grep -l "location /static" {} \; 2>/dev/null | head -1)

if [ -z "$CONFIG_FILE" ]; then
    echo "No se encontró configuración de /static/"
    echo "¿Puedes compartir el contenido de tu /etc/nginx/nginx.conf?"
    exit 1
fi

echo "Archivo encontrado: $CONFIG_FILE"
echo ""

# Mostrar la sección actual
echo "Configuración actual de /static/:"
grep -A 20 "location /static" "$CONFIG_FILE" | head -25
echo ""

# Crear backup
BACKUP="${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
cp "$CONFIG_FILE" "$BACKUP"
echo "✓ Backup creado: $BACKUP"
echo ""

# Reemplazo manual usando sed
echo "Aplicando corrección..."
sed -i 's|alias /app/src/static/;|proxy_pass http://127.0.0.1:8000;\n            proxy_http_version 1.1;\n            proxy_set_header Host $host;\n            proxy_set_header X-Real-IP $remote_addr;\n            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n            proxy_set_header X-Forwarded-Proto $scheme;\n            proxy_set_header Connection "";|' "$CONFIG_FILE"

# Verificar sintaxis
if nginx -t 2>&1 | grep -q "test is successful"; then
    echo "✅ Configuración válida"
    echo ""
    read -p "¿Recargar nginx? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        systemctl reload nginx
        echo "✅ Nginx recargado"
    fi
else
    echo "❌ Error en configuración - restaurando backup..."
    cp "$BACKUP" "$CONFIG_FILE"
    nginx -t
fi

