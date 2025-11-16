#!/bin/bash
# Script para limpiar scripts antiguos de la raíz del proyecto
# Ejecutar: bash limpiar-scripts-antiguos.sh

echo "========================================="
echo "🧹 LIMPIEZA DE SCRIPTS ANTIGUOS"
echo "========================================="
echo ""

cd ~/paqueteria || exit 1

# Scripts que deben estar en CODE/scripts/deployment/
SCRIPTS_ANTIGUOS=(
    "deploy-aws.sh"
    "deploy.sh"
    "dev-up.sh"
    "git-add-server-files.sh"
    "pull-only.sh"
    "pull-update.sh"
    "rollback.sh"
    "setup-env.sh"
    "setup-production.sh"
    "update.sh"
)

echo "Scripts encontrados en la raíz:"
for script in "${SCRIPTS_ANTIGUOS[@]}"; do
    if [ -f "$script" ]; then
        echo "  ✓ $script"
        
        # Verificar si existe en CODE/scripts/deployment/
        if [ -f "CODE/scripts/deployment/$script" ]; then
            echo "    → Ya existe en CODE/scripts/deployment/"
            echo "    → Eliminando de la raíz..."
            rm -f "$script"
        else
            echo "    → NO existe en CODE/scripts/deployment/"
            echo "    → Moviendo a CODE/scripts/deployment/"
            mv "$script" "CODE/scripts/deployment/" 2>/dev/null || echo "      ✗ Error al mover"
        fi
    fi
done

echo ""
echo "Verificando Git..."
git status --short | grep -E "^\?\?" | head -10

echo ""
echo "========================================="
echo "✅ Limpieza completada"
echo "========================================="

