#!/bin/bash
# ========================================
# SCRIPT PARA AGREGAR ARCHIVOS DEL SERVIDOR A GIT
# ========================================
# Ejecuta este script en el servidor para agregar los archivos
# que faltan en el repositorio y hacer push a GitHub
# ========================================

set -e  # Salir si hay error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones para logging
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

# ========================================
# FUNCIÓN PARA ENCONTRAR LA RAÍZ DEL PROYECTO
# ========================================
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

echo "========================================="
echo "📤 AGREGAR ARCHIVOS DEL SERVIDOR A GIT"
echo "========================================="
echo ""

# Obtener directorio del script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Buscar la raíz del proyecto (donde está .git)
PROJECT_ROOT=$(find_project_root "$SCRIPT_DIR")
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ] || [ -z "$PROJECT_ROOT" ]; then
    echo "❌ Error: No se encontró la raíz del proyecto (.git)" >&2
    echo "   Ejecuta este script desde dentro del repositorio Git" >&2
    echo "   Directorio actual del script: $SCRIPT_DIR" >&2
    exit 1
fi

# Cambiar a la raíz del proyecto
cd "$PROJECT_ROOT"

# ========================================
# 1. VERIFICAR QUE ESTAMOS EN UN REPO GIT
# ========================================

log_success "Repositorio Git encontrado en: $PROJECT_ROOT"
echo ""

# ========================================
# 2. VERIFICAR ESTADO ACTUAL
# ========================================

log_info "Verificando estado actual del repositorio..."
git status --short

echo ""

# ========================================
# 3. LISTA DE ARCHIVOS A AGREGAR
# ========================================

FILES_TO_ADD=(
    "CODE/Dockerfile.lightsail"
    "CODE/nginx/nginx.lightsail.conf"
    "CODE/src/app/cache_manager.py"
    "CODE/src/app/database_optimized.py"
    "deploy-lightsail.sh"
    "docker-compose.lightsail.yml"
    "CODE/scripts/deployment/monitor.sh"
)

log_info "Archivos a agregar al repositorio:"
for file in "${FILES_TO_ADD[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (no existe)"
    fi
done

echo ""

# ========================================
# 4. VERIFICAR QUE LOS ARCHIVOS EXISTAN
# ========================================

MISSING_FILES=()
for file in "${FILES_TO_ADD[@]}"; do
    if [ ! -f "$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    log_warning "Los siguientes archivos no existen y serán omitidos:"
    for file in "${MISSING_FILES[@]}"; do
        echo "  - $file"
    done
    echo ""
fi

# ========================================
# 5. AGREGAR ARCHIVOS AL STAGING
# ========================================

log_info "Agregando archivos al staging de Git..."

ADDED_COUNT=0
for file in "${FILES_TO_ADD[@]}"; do
    if [ -f "$file" ]; then
        git add "$file"
        ADDED_COUNT=$((ADDED_COUNT + 1))
    fi
done

if [ $ADDED_COUNT -eq 0 ]; then
    log_warning "No se agregaron archivos (puede que ya estén agregados o no existan)"
else
    log_success "Agregados $ADDED_COUNT archivo(s) al staging"
fi

echo ""

# ========================================
# 6. VERIFICAR ESTADO DESPUÉS DE AGREGAR
# ========================================

log_info "Estado después de agregar archivos:"
git status --short

echo ""

# ========================================
# 7. PREGUNTAR SI HACER COMMIT
# ========================================

STAGED_FILES=$(git diff --cached --name-only)

if [ -z "$STAGED_FILES" ]; then
    log_info "No hay archivos en staging para hacer commit"
    log_info "Todos los archivos ya están agregados o no hay cambios"
    exit 0
fi

log_info "Archivos listos para commit:"
echo "$STAGED_FILES" | while read -r file; do
    echo "  + $file"
done

echo ""

read -p "¿Deseas hacer commit de estos archivos? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "Commit cancelado. Los archivos están en staging."
    log_info "Puedes hacer commit manualmente con:"
    log_info "  git commit -m 'Agregar archivos de deployment y configuración del servidor'"
    exit 0
fi

# ========================================
# 8. HACER COMMIT
# ========================================

log_info "Haciendo commit..."

COMMIT_MESSAGE="feat: Agregar archivos de deployment y configuración del servidor

- CODE/Dockerfile.lightsail: Dockerfile optimizado para AWS Lightsail
- CODE/nginx/nginx.lightsail.conf: Configuración Nginx para Lightsail
- CODE/src/app/cache_manager.py: Gestor de caché
- CODE/src/app/database_optimized.py: Optimizaciones de base de datos
- deploy-lightsail.sh: Script de deployment para Lightsail
- docker-compose.lightsail.yml: Docker Compose para Lightsail
- CODE/scripts/deployment/monitor.sh: Script de monitoreo"

git commit -m "$COMMIT_MESSAGE"

if [ $? -eq 0 ]; then
    log_success "Commit realizado exitosamente"
else
    log_error "Error al hacer commit"
    exit 1
fi

echo ""

# ========================================
# 9. PREGUNTAR SI HACER PUSH
# ========================================

read -p "¿Deseas hacer push a GitHub? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "Push cancelado. Puedes hacer push manualmente con:"
    log_info "  git push origin main"
    exit 0
fi

# ========================================
# 10. OBTENER RAMA ACTUAL
# ========================================

CURRENT_BRANCH=$(git branch --show-current)
log_info "Rama actual: $CURRENT_BRANCH"

# ========================================
# 11. HACER PUSH
# ========================================

log_info "Haciendo push a GitHub..."

# Intentar push
if git push origin "$CURRENT_BRANCH"; then
    log_success "Push realizado exitosamente"
else
    log_error "Error al hacer push"
    log_warning "Puede que necesites hacer pull primero si hay cambios remotos"
    log_info "Intenta: git pull --rebase origin $CURRENT_BRANCH && git push origin $CURRENT_BRANCH"
    exit 1
fi

echo ""
echo "========================================="
log_success "ARCHIVOS AGREGADOS Y SUBIDOS A GITHUB"
echo "========================================="
echo ""
log_info "Ahora puedes trabajar desde localhost y servidor sincronizados"
echo ""

