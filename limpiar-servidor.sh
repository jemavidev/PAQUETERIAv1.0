#!/bin/bash
# ========================================
# SCRIPT DE LIMPIEZA DEL SERVIDOR
# ========================================
# Elimina archivos duplicados en la raíz del servidor
# que deberían estar solo en DOCS/scripts/deployment/
# ========================================

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo "========================================="
echo "🧹 LIMPIEZA DEL SERVIDOR"
echo "========================================="
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -d ".git" ]; then
    log_error "No se encontró repositorio Git. Ejecuta desde la raíz del proyecto."
    exit 1
fi

log_info "Directorio actual: $(pwd)"
echo ""

# Archivos que deben eliminarse de la raíz (están duplicados en DOCS/scripts/deployment/)
ARCHIVOS_A_ELIMINAR=(
    "deploy-aws.sh"
    "deploy.sh"
    "dev-up.sh"
    "pull-only.sh"
    "pull-update.sh"
    "rollback.sh"
    "setup-env.sh"
    "setup-production.sh"
    "update.sh"
)

# Archivos que deben permanecer en la raíz
ARCHIVOS_VALIDOS=(
    "deploy-lightsail.sh"
    "deploy-to-aws.sh"
    "monitor.sh"
    "start.sh"
    "test-scripts.sh"
)

log_info "Archivos a eliminar (duplicados en DOCS/scripts/deployment/):"
for archivo in "${ARCHIVOS_A_ELIMINAR[@]}"; do
    if [ -f "$archivo" ]; then
        echo "  🗑️  $archivo"
    fi
done
echo ""

log_info "Archivos que permanecerán en la raíz:"
for archivo in "${ARCHIVOS_VALIDOS[@]}"; do
    if [ -f "$archivo" ]; then
        echo "  ✅ $archivo"
    fi
done
echo ""

# Preguntar confirmación
read -p "¿Deseas eliminar los archivos duplicados? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "Operación cancelada"
    exit 0
fi

# Eliminar archivos duplicados
log_info "Eliminando archivos duplicados..."
ELIMINADOS=0

for archivo in "${ARCHIVOS_A_ELIMINAR[@]}"; do
    if [ -f "$archivo" ]; then
        rm "$archivo"
        log_success "Eliminado: $archivo"
        ELIMINADOS=$((ELIMINADOS + 1))
    fi
done

echo ""

if [ $ELIMINADOS -eq 0 ]; then
    log_info "No había archivos duplicados para eliminar"
else
    log_success "Se eliminaron $ELIMINADOS archivos duplicados"
fi

echo ""

# Verificar estado de Git
log_info "Estado de Git después de la limpieza:"
git status --short

echo ""
log_success "✅ Limpieza completada"
echo ""

log_info "Los archivos correctos están en:"
echo "  - Raíz del proyecto: deploy-lightsail.sh, deploy-to-aws.sh, monitor.sh, start.sh, test-scripts.sh"
echo "  - DOCS/scripts/deployment/: deploy.sh, pull-update.sh, pull-only.sh, etc."
echo ""
