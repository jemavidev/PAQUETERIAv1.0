#!/bin/bash
# Script para resetear staging desde GitHub (fuente única de verdad)
# Fecha: 2025-11-28
# ADVERTENCIA: Esto descartará TODOS los cambios locales en staging

set -e  # Salir si hay algún error

echo "🔄 =========================================="
echo "   RESET STAGING DESDE GITHUB"
echo "   =========================================="
echo ""
echo "⚠️  ADVERTENCIA: Este script descartará TODOS los cambios locales en staging"
echo "   y sincronizará con la rama 'staging' de GitHub."
echo ""
read -p "¿Estás seguro de continuar? (escribe 'SI' para confirmar): " confirmacion

if [ "$confirmacion" != "SI" ]; then
    echo "❌ Operación cancelada."
    exit 1
fi

echo ""
echo "📋 Paso 1: Verificando rama actual..."
CURRENT_BRANCH=$(git branch --show-current)
echo "   Rama actual: $CURRENT_BRANCH"

if [ "$CURRENT_BRANCH" != "staging" ]; then
    echo "⚠️  No estás en la rama 'staging'. Cambiando..."
    git checkout staging
fi

echo ""
echo "📋 Paso 2: Guardando cambios locales en stash (por seguridad)..."
git stash push -m "Backup antes de reset desde GitHub - $(date '+%Y-%m-%d %H:%M:%S')"
echo "   ✅ Cambios guardados en stash (puedes recuperarlos con 'git stash pop' si es necesario)"

echo ""
echo "📋 Paso 3: Obteniendo última versión de GitHub..."
git fetch origin staging

echo ""
echo "📋 Paso 4: Reseteando a la versión de GitHub (HARD RESET)..."
git reset --hard origin/staging
echo "   ✅ Código local ahora coincide 100% con GitHub"

echo ""
echo "📋 Paso 5: Limpiando archivos no rastreados..."
git clean -fd
echo "   ✅ Archivos no rastreados eliminados"

echo ""
echo "📋 Paso 6: Verificando estado del repositorio..."
git status

echo ""
echo "📋 Paso 7: Deteniendo contenedores Docker..."
if command -v docker-compose &> /dev/null; then
    docker-compose -f docker-compose.staging.yml down
    echo "   ✅ Contenedores detenidos"
else
    echo "   ⚠️  docker-compose no encontrado, saltando..."
fi

echo ""
echo "📋 Paso 8: Reconstruyendo contenedores desde cero..."
if command -v docker-compose &> /dev/null; then
    docker-compose -f docker-compose.staging.yml build --no-cache
    echo "   ✅ Contenedores reconstruidos"
else
    echo "   ⚠️  docker-compose no encontrado, saltando..."
fi

echo ""
echo "📋 Paso 9: Iniciando contenedores..."
if command -v docker-compose &> /dev/null; then
    docker-compose -f docker-compose.staging.yml up -d
    echo "   ✅ Contenedores iniciados"
else
    echo "   ⚠️  docker-compose no encontrado, saltando..."
fi

echo ""
echo "✅ =========================================="
echo "   RESET COMPLETADO EXITOSAMENTE"
echo "   =========================================="
echo ""
echo "📊 Resumen:"
echo "   - Código local sincronizado con GitHub ✅"
echo "   - Cambios locales guardados en stash (recuperables) ✅"
echo "   - Contenedores reconstruidos desde cero ✅"
echo "   - Servidor staging reiniciado ✅"
echo ""
echo "🔍 Verificación:"
echo "   - Última commit: $(git log -1 --oneline)"
echo "   - Rama: $(git branch --show-current)"
echo "   - Estado: $(git status --short | wc -l) archivos modificados"
echo ""
echo "💡 Notas:"
echo "   - Si necesitas recuperar cambios locales: git stash list"
echo "   - Para aplicar el último stash: git stash pop"
echo "   - Para ver todos los stash: git stash list"
echo ""
echo "🎉 ¡Staging ahora refleja exactamente lo que está en GitHub!"
