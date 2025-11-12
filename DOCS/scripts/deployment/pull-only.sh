#!/bin/bash
# PAQUETERÍA v1.0 - Pull de código desde GitHub (sin rebuild)
# Uso: ./DOCS/scripts/deployment/pull-only.sh [branch|tag]
# 
# Este script solo actualiza los archivos desde GitHub usando sparse-checkout
# NO reconstruye imágenes Docker ni reinicia servicios
# Útil para actualizar código sin downtime

set -euo pipefail

BRANCH_OR_TAG="${1:-main}"

info() { echo -e "\033[0;34m[INFO]\033[0m $1"; }
success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }
warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }

# Verificar que estamos en un repositorio git
if [ ! -d ".git" ]; then
  error "No se encontró repositorio Git. Ejecuta desde el directorio del proyecto."
  exit 1
fi

info "🔄 Actualizando código desde GitHub (sin rebuild)..."
info "Rama/Tag: $BRANCH_OR_TAG"

# Verificar que sparse-checkout está activo
if ! git config core.sparseCheckout | grep -q "true"; then
  warning "Sparse checkout no está activo. Los archivos se actualizarán según configuración actual."
fi

# Traer todos los cambios remotos
info "📥 Traendo cambios desde remoto..."
git fetch --all --tags

if [ $? -ne 0 ]; then
  error "Error al hacer fetch. Verifica la conexión a GitHub."
  exit 1
fi

# Cambiar a la rama/tag especificada
info "🔀 Cambiando a $BRANCH_OR_TAG..."
if git checkout "$BRANCH_OR_TAG" 2>/dev/null; then
  success "Cambiado a $BRANCH_OR_TAG"
else
  error "No se pudo cambiar a $BRANCH_OR_TAG"
  error "Ramas disponibles:"
  git branch -r | head -10
  exit 1
fi

# Actualizar archivos (solo los del sparse-checkout)
info "📦 Actualizando archivos (sparse-checkout)..."
if git pull --ff-only; then
  success "Archivos actualizados correctamente"
else
  warning "Pull falló (puede ser que ya esté actualizado o hay cambios locales)"
  warning "Estado actual:"
  git status --short | head -5 || true
fi

# Mostrar resumen
echo ""
info "📊 Resumen de cambios:"
echo "─────────────────────────────────────────"

# Ver archivos modificados
MODIFIED=$(git diff --name-only HEAD@{1} HEAD 2>/dev/null || git diff --name-only HEAD@{1} 2>/dev/null || echo "")
if [ -n "$MODIFIED" ]; then
  info "Archivos modificados:"
  echo "$MODIFIED" | while read -r file; do
    if [ -n "$file" ]; then
      echo "  📝 $file"
    fi
  done
else
  info "No hay cambios nuevos"
fi

# Mostrar último commit
LAST_COMMIT=$(git log -1 --oneline 2>/dev/null || echo "")
if [ -n "$LAST_COMMIT" ]; then
  echo ""
  info "Último commit:"
  echo "  $LAST_COMMIT"
fi

# Verificar estado de contenedores (sin hacer nada)
echo ""
info "🐳 Estado actual de contenedores:"
if command -v docker &> /dev/null; then
  docker compose ps 2>/dev/null || docker ps --filter "name=paqueteria" --format "table {{.Names}}\t{{.Status}}" || echo "  (No se pudo verificar)"
else
  warning "Docker no disponible"
fi

echo ""
success "✅ Pull completado (sin rebuild)"
info "💡 Para aplicar cambios en la aplicación, reinicia los contenedores:"
info "   docker compose restart app"
info "   O usa: ./DOCS/scripts/deployment/deploy.sh para rebuild completo"

