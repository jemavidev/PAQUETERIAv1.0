#!/bin/bash
# ========================================
# SCRIPT PARA CORREGIR CONFIGURACIÓN DE NGINX
# ========================================
# Corrige el problema de 403 Forbidden en archivos estáticos
# ========================================

set -e

echo "========================================="
echo "🔧 CORRECCIÓN DE NGINX PARA ARCHIVOS ESTÁTICOS"
echo "========================================="
echo ""

# Verificar que se ejecuta como root o con sudo
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Este script debe ejecutarse con sudo"
    echo "   Ejecuta: sudo bash fix-nginx-static.sh"
    exit 1
fi

# Buscar archivos de configuración que contengan "location /static"
echo "Buscando configuración de nginx..."
CONFIG_FILES=$(find /etc/nginx -name "*.conf" -type f -exec grep -l "location /static" {} \; 2>/dev/null)

if [ -z "$CONFIG_FILES" ]; then
    echo "⚠️  No se encontró configuración de /static/ en nginx"
    echo "   Esto podría significar que nginx está usando proxy_pass correctamente"
    exit 0
fi

echo "Archivos encontrados:"
echo "$CONFIG_FILES"
echo ""

# Procesar cada archivo
for config_file in $CONFIG_FILES; do
    echo "Procesando: $config_file"
    
    # Crear backup
    BACKUP_FILE="${config_file}.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$config_file" "$BACKUP_FILE"
    echo "  ✓ Backup creado: $BACKUP_FILE"
    
    # Buscar la sección location /static/
    if grep -q "alias /app/src/static/" "$config_file"; then
        echo "  ⚠️  Encontrado 'alias /app/src/static/' - necesita corrección"
        
        # Verificar si ya existe proxy_pass para fastapi
        if grep -q "proxy_pass http://fastapi" "$config_file" || grep -q "proxy_pass http://127.0.0.1:8000" "$config_file"; then
            UPSTREAM=$(grep -E "proxy_pass http://(fastapi|127.0.0.1:8000|localhost:8000)" "$config_file" | head -1 | sed -n 's/.*proxy_pass http://\([^;]*\).*/\1/p')
            if [ -z "$UPSTREAM" ]; then
                UPSTREAM="127.0.0.1:8000"
            fi
            echo "  ✓ Usando upstream existente: $UPSTREAM"
        else
            # Buscar upstream definido
            if grep -q "upstream.*fastapi" "$config_file"; then
                UPSTREAM=$(grep "upstream.*fastapi" "$config_file" | head -1 | awk '{print $2}' | tr -d '{')
                if [ -z "$UPSTREAM" ]; then
                    UPSTREAM="fastapi_backend"
                fi
            else
                UPSTREAM="127.0.0.1:8000"
            fi
            echo "  ℹ️  Usando: $UPSTREAM"
        fi
        
        # Crear script de reemplazo temporal
        TEMP_SCRIPT=$(mktemp)
        cat > "$TEMP_SCRIPT" << 'SCRIPTEND'
#!/usr/bin/env python3
import re
import sys

content = sys.stdin.read()

# Patrón para encontrar location /static/ con alias
pattern = r'(location\s+/static/\s*\{[^}]*?)alias\s+/app/src/static/;([^}]*?\})'

def replace_static(match):
    location_block = match.group(1)
    closing_brace = match.group(2)
    
    # Extraer configuración existente (expires, headers, etc.)
    other_config = re.sub(r'alias\s+/app/src/static/;', '', location_block)
    
    # Construir nueva configuración con proxy_pass
    new_config = f'''location /static/ {{
            # Proxy a FastAPI (los archivos estáticos están en el contenedor)
            proxy_pass http://127.0.0.1:8000;
            proxy_http_version 1.1;
            
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Connection "";
            
            # Configuración existente
{other_config}
            
            # Timeouts
            proxy_connect_timeout 10s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }}'''
    
    return new_config

new_content = re.sub(pattern, replace_static, content, flags=re.DOTALL)

# También reemplazar location /uploads/ si existe
pattern_uploads = r'(location\s+/uploads/\s*\{[^}]*?)alias\s+/app/uploads/;([^}]*?\})'
def replace_uploads(match):
    location_block = match.group(1)
    closing_brace = match.group(2)
    
    other_config = re.sub(r'alias\s+/app/uploads/;', '', location_block)
    
    new_config = f'''location /uploads/ {{
            # Proxy a FastAPI (los uploads están en el contenedor)
            proxy_pass http://127.0.0.1:8000;
            proxy_http_version 1.1;
            
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Connection "";
            
            # Configuración existente
{other_config}
            
            # Timeouts
            proxy_connect_timeout 10s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }}'''
    
    return new_config

new_content = re.sub(pattern_uploads, replace_uploads, new_content, flags=re.DOTALL)

print(new_content)
SCRIPTEND
        
        # Aplicar reemplazo
        python3 "$TEMP_SCRIPT" < "$config_file" > "${config_file}.new"
        
        if [ $? -eq 0 ]; then
            mv "${config_file}.new" "$config_file"
            echo "  ✓ Archivo actualizado"
        else
            echo "  ✗ Error al actualizar archivo"
            rm -f "${config_file}.new" "$TEMP_SCRIPT"
            continue
        fi
        
        rm -f "$TEMP_SCRIPT"
    else
        echo "  ✓ No requiere cambios (ya usa proxy_pass o no tiene alias)"
    fi
done

echo ""
echo "Verificando configuración de nginx..."
if nginx -t 2>&1 | grep -q "test is successful"; then
    echo "✅ Configuración de nginx válida"
    echo ""
    read -p "¿Deseas recargar nginx ahora? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        systemctl reload nginx
        echo "✅ Nginx recargado"
    else
        echo "⚠️  Recuerda recargar nginx con: sudo systemctl reload nginx"
    fi
else
    echo "❌ Error en la configuración de nginx"
    nginx -t
    echo ""
    echo "⚠️  Revisa los errores y corrige manualmente"
    echo "   O restaura el backup si es necesario"
    exit 1
fi

echo ""
echo "========================================="
echo "✅ CORRECCIÓN COMPLETADA"
echo "========================================="
echo ""
echo "Prueba las imágenes:"
echo "  curl -I http://localhost/static/images/logo.png"
echo "  curl -I http://localhost/static/images/favicon.png"

