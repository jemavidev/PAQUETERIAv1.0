#!/bin/bash
# Script de prueba para verificar find_project_root

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
echo "Script dir: $SCRIPT_DIR"

PROJECT_ROOT=$(find_project_root "$SCRIPT_DIR")
EXIT_CODE=$?

echo "Exit code: $EXIT_CODE"
echo "Project root: $PROJECT_ROOT"

if [ $EXIT_CODE -ne 0 ] || [ -z "$PROJECT_ROOT" ]; then
    echo "ERROR: No se encontró .git"
    exit 1
else
    echo "SUCCESS: .git encontrado en $PROJECT_ROOT"
    exit 0
fi

