#!/bin/bash
# Script simple para corregir nginx - reemplaza alias por proxy_pass

set -e

echo "========================================="
echo "🔧 CORRECCIÓN DE NGINX"
echo "========================================="
echo ""

if [ "$EUID" -ne 0 ]; then 
    echo "❌ Este script debe ejecutarse con sudo"
    echo "   Ejecuta: sudo bash corregir-nginx.sh"
    exit 1
fi

# Buscar archivo de configuración
CONFIG_FILE="/etc/nginx/nginx.conf"

# Verificar que existe
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ No se encontró $CONFIG_FILE"
    exit 1
fi

echo "Archivo de configuración: $CONFIG_FILE"
echo ""

# Crear backup
BACKUP="${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
cp "$CONFIG_FILE" "$BACKUP"
echo "✓ Backup creado: $BACKUP"
echo ""

# Verificar si tiene alias
if grep -q "alias /app/src/static/" "$CONFIG_FILE"; then
    echo "⚠️  Encontrado 'alias /app/src/static/' - corrigiendo..."
    
    # Leer el archivo completo
    TEMP_FILE=$(mktemp)
    cp "$CONFIG_FILE" "$TEMP_FILE"
    
    # Buscar la sección location /static/ y reemplazar
    python3 << 'PYTHON_SCRIPT'
import re
import sys

with open('/etc/nginx/nginx.conf', 'r') as f:
    content = f.read()

# Patrón para location /static/
pattern = r'(location\s+/static/\s*\{[^}]*?)\s*alias\s+/app/src/static/;([^}]*?\})'

def replace_func(match):
    before = match.group(1)
    after = match.group(2)
    
    # Limpiar configuraciones innecesarias que dependen de alias
    after = re.sub(r'\s*(sendfile|tcp_nopush|tcp_nodelay)\s+on;', '', after)
    
    replacement = f'''{before}
            # Proxy a FastAPI (archivos estáticos en el contenedor)
            proxy_pass http://127.0.0.1:8000;
            proxy_http_version 1.1;
            
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Connection "";
            
            # Timeouts
            proxy_connect_timeout 10s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
{after}'''
    
    return replacement

new_content = re.sub(pattern, replace_func, content, flags=re.DOTALL)

# También corregir /uploads/ si existe
pattern_uploads = r'(location\s+/uploads/\s*\{[^}]*?)\s*alias\s+/app/uploads/;([^}]*?\})'

def replace_uploads_func(match):
    before = match.group(1)
    after = match.group(2)
    
    replacement = f'''{before}
            # Proxy a FastAPI (uploads en el contenedor)
            proxy_pass http://127.0.0.1:8000;
            proxy_http_version 1.1;
            
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Connection "";
            
            # Timeouts
            proxy_connect_timeout 10s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
{after}'''
    
    return replacement

new_content = re.sub(pattern_uploads, replace_uploads_func, new_content, flags=re.DOTALL)

with open('/etc/nginx/nginx.conf', 'w') as f:
    f.write(new_content)

print("✅ Archivo actualizado")
PYTHON_SCRIPT
    
    if [ $? -eq 0 ]; then
        echo "✓ Reemplazo realizado"
    else
        echo "❌ Error al reemplazar - restaurando backup..."
        cp "$BACKUP" "$CONFIG_FILE"
        exit 1
    fi
else
    echo "ℹ️  No se encontró 'alias /app/src/static/' - verificando configuración..."
    grep -A 10 "location /static" "$CONFIG_FILE" | head -15
    echo ""
    echo "Si ya está usando proxy_pass, no se requieren cambios"
fi

echo ""
echo "Verificando configuración..."
if nginx -t 2>&1 | grep -q "test is successful"; then
    echo "✅ Configuración válida"
    echo ""
    read -p "¿Recargar nginx ahora? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        systemctl reload nginx
        echo "✅ Nginx recargado"
        echo ""
        echo "Probando acceso a imágenes:"
        sleep 2
        curl -I http://localhost/static/images/logo.png 2>&1 | head -3
    else
        echo "⚠️  Recarga nginx manualmente con: sudo systemctl reload nginx"
    fi
else
    echo "❌ Error en la configuración:"
    nginx -t 2>&1
    echo ""
    echo "Restaurando backup..."
    cp "$BACKUP" "$CONFIG_FILE"
    exit 1
fi

echo ""
echo "========================================="
echo "✅ CORRECCIÓN COMPLETADA"
echo "========================================="

