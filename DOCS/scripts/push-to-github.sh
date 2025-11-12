#!/bin/bash
# Script para hacer push a GitHub
# Uso: ./push-to-github.sh [usuario_github]

set -e

REPO_NAME="PAQUETERIAv1.0"
GITHUB_USER="${1:-}"

if [ -z "$GITHUB_USER" ]; then
    echo "❌ Error: Necesitas proporcionar tu nombre de usuario de GitHub"
    echo ""
    echo "Uso: ./push-to-github.sh TU_USUARIO_GITHUB"
    echo ""
    echo "O proporciona la URL completa del repositorio:"
    echo "  git remote add origin https://github.com/TU_USUARIO/PAQUETERIAv1.0.git"
    exit 1
fi

REPO_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}.git"

echo "🚀 Preparando push a GitHub..."
echo "📦 Repositorio: ${REPO_URL}"
echo ""

# Verificar si el remoto ya existe
if git remote get-url origin >/dev/null 2>&1; then
    echo "⚠️  El remoto 'origin' ya existe. ¿Deseas actualizarlo? (s/n)"
    read -r response
    if [[ "$response" =~ ^[Ss]$ ]]; then
        git remote set-url origin "$REPO_URL"
        echo "✅ Remoto actualizado"
    else
        echo "❌ Operación cancelada"
        exit 1
    fi
else
    git remote add origin "$REPO_URL"
    echo "✅ Remoto agregado"
fi

# Verificar conexión
echo ""
echo "🔍 Verificando conexión con GitHub..."
if git ls-remote --heads origin >/dev/null 2>&1; then
    echo "✅ Conexión exitosa"
else
    echo "❌ Error: No se pudo conectar al repositorio"
    echo ""
    echo "Por favor verifica:"
    echo "  1. Que el repositorio '${REPO_NAME}' existe en GitHub"
    echo "  2. Que tienes permisos para hacer push"
    echo "  3. Que tu nombre de usuario es correcto: ${GITHUB_USER}"
    exit 1
fi

# Hacer push
echo ""
echo "📤 Haciendo push a GitHub..."
git push -u origin main

echo ""
echo "✅ ¡Push completado exitosamente!"
echo "🌐 Repositorio: ${REPO_URL}"

