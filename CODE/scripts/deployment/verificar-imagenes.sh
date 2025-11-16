#!/bin/bash
# Script para verificar que las imágenes estén disponibles

echo "========================================="
echo "🖼️ VERIFICACIÓN DE IMÁGENES"
echo "========================================="
echo ""

# Función para encontrar la raíz del proyecto
find_project_root() {
    local current_dir="$1"
    local max_depth=10
    local depth=0
    
    while [ "$depth" -lt "$max_depth" ]; do
        if [ -d "$current_dir/.git" ]; then
            echo "$current_dir"
            return 0
        fi
        
        if [ "$current_dir" = "/" ]; then
            return 1
        fi
        
        current_dir="$(dirname "$current_dir")"
        depth=$((depth + 1))
    done
    
    return 1
}

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT=$(find_project_root "$SCRIPT_DIR")
cd "$PROJECT_ROOT"

echo "Directorio del proyecto: $PROJECT_ROOT"
echo ""

# Verificar archivos de imagen
IMAGES_DIR="CODE/src/static/images"
echo "Verificando imágenes en: $IMAGES_DIR"
echo ""

if [ ! -d "$IMAGES_DIR" ]; then
    echo "❌ El directorio $IMAGES_DIR NO existe"
    exit 1
fi

echo "Archivos en $IMAGES_DIR:"
ls -lah "$IMAGES_DIR" | tail -n +2
echo ""

# Verificar archivos específicos
FILES=("favicon.png" "logo.png")

for file in "${FILES[@]}"; do
    FILE_PATH="$IMAGES_DIR/$file"
    if [ -f "$FILE_PATH" ]; then
        SIZE=$(stat -f%z "$FILE_PATH" 2>/dev/null || stat -c%s "$FILE_PATH" 2>/dev/null || echo "desconocido")
        PERMS=$(stat -f%Sp "$FILE_PATH" 2>/dev/null || stat -c%A "$FILE_PATH" 2>/dev/null || ls -l "$FILE_PATH" | awk '{print $1}')
        echo "✓ $file existe"
        echo "  Tamaño: $SIZE bytes"
        echo "  Permisos: $PERMS"
    else
        echo "✗ $file NO existe"
    fi
    echo ""
done

# Verificar dentro del contenedor Docker
echo "Verificando dentro del contenedor Docker..."
if docker ps | grep -q "paqueteria_v1_prod_app"; then
    CONTAINER_NAME="paqueteria_v1_prod_app"
    echo "Contenedor encontrado: $CONTAINER_NAME"
    echo ""
    
    echo "Verificando /app/src/static/images:"
    docker exec "$CONTAINER_NAME" ls -lah /app/src/static/images 2>&1 || echo "❌ Error al acceder al contenedor"
    echo ""
    
    echo "Verificando archivos específicos:"
    docker exec "$CONTAINER_NAME" test -f /app/src/static/images/favicon.png && echo "✓ favicon.png existe en contenedor" || echo "✗ favicon.png NO existe en contenedor"
    docker exec "$CONTAINER_NAME" test -f /app/src/static/images/logo.png && echo "✓ logo.png existe en contenedor" || echo "✗ logo.png NO existe en contenedor"
    echo ""
    
    echo "Probando acceso HTTP:"
    echo "  /static/images/favicon.png"
    docker exec "$CONTAINER_NAME" curl -I http://127.0.0.1:8000/static/images/favicon.png 2>&1 | head -5
    echo ""
    echo "  /static/images/logo.png"
    docker exec "$CONTAINER_NAME" curl -I http://127.0.0.1:8000/static/images/logo.png 2>&1 | head -5
else
    echo "⚠️ Contenedor no está corriendo"
fi

echo ""
echo "========================================="
echo "✅ Verificación completada"
echo "========================================="

