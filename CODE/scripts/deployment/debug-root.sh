#!/bin/bash
# Script de diagnóstico para verificar la búsqueda de la raíz del proyecto

echo "========================================="
echo "🔍 DIAGNÓSTICO: Búsqueda de raíz del proyecto"
echo "========================================="
echo ""

# Función para encontrar la raíz
find_project_root() {
    local current_dir="$1"
    local max_depth=10
    local depth=0
    
    echo "Buscando desde: $current_dir"
    
    while [ "$depth" -lt "$max_depth" ]; do
        echo "  Nivel $depth: $current_dir"
        
        if [ -d "$current_dir/.git" ]; then
            echo "  ✓ .git encontrado en: $current_dir"
            echo "$current_dir"
            return 0
        fi
        
        if [ "$current_dir" = "/" ]; then
            echo "  ✗ Llegamos a la raíz del sistema, no se encontró .git"
            return 1
        fi
        
        current_dir="$(dirname "$current_dir")"
        depth=$((depth + 1))
    done
    
    echo "  ✗ Máxima profundidad alcanzada sin encontrar .git"
    return 1
}

# Obtener directorio del script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Script ejecutado desde: $SCRIPT_DIR"
echo ""

# Probar la función
PROJECT_ROOT=$(find_project_root "$SCRIPT_DIR")
EXIT_CODE=$?

echo ""
echo "========================================="
echo "Resultado:"
echo "========================================="
echo "Exit code: $EXIT_CODE"
echo "PROJECT_ROOT: $PROJECT_ROOT"

if [ $EXIT_CODE -ne 0 ] || [ -z "$PROJECT_ROOT" ]; then
    echo ""
    echo "❌ ERROR: No se encontró la raíz del proyecto"
    exit 1
else
    echo ""
    echo "✅ ÉXITO: Raíz encontrada en $PROJECT_ROOT"
    
    # Verificar que podemos cambiar al directorio
    if cd "$PROJECT_ROOT"; then
        echo "✅ Puede cambiar al directorio raíz"
        echo "   Directorio actual: $(pwd)"
        if [ -d ".git" ]; then
            echo "✅ .git confirmado en el directorio raíz"
        else
            echo "❌ .git NO encontrado en el directorio raíz"
        fi
    else
        echo "❌ No puede cambiar al directorio raíz"
    fi
    
    exit 0
fi

