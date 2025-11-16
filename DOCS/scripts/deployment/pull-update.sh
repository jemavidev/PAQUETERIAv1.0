#!/bin/bash
# ========================================
# SCRIPT DE ACTUALIZACIÓN AUTOMÁTICA - PULL Y DEPLOY
# ========================================
# Hace pull de GitHub y actualiza el código sin necesidad de rebuild/restart
# Los cambios en código Python/HTML/JS se reflejan automáticamente gracias a hot reload
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

# Obtener directorio del script y navegar a la raíz del proyecto
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../../.." && pwd )"
cd "$PROJECT_ROOT"

echo "========================================="
echo "🔄 ACTUALIZACIÓN AUTOMÁTICA - PAQUETERÍA v1.0"
echo "========================================="
echo ""
log_info "Directorio del proyecto: $PROJECT_ROOT"
echo ""

# ========================================
# 1. VERIFICAR QUE ESTAMOS EN UN REPO GIT
# ========================================

log_info "Verificando repositorio Git..."

if [ ! -d ".git" ]; then
    log_error "No se encontró un repositorio Git en este directorio"
    exit 1
fi

log_success "Repositorio Git encontrado"
echo ""

# ========================================
# 2. VERIFICAR ESTADO DEL REPO
# ========================================

log_info "Verificando estado del repositorio..."

# Verificar si hay cambios locales sin commitear
if ! git diff-index --quiet HEAD --; then
    log_warning "Hay cambios locales sin commitear"
    echo ""
    read -p "¿Deseas guardar los cambios locales en un stash antes de hacer pull? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Guardando cambios en stash..."
        git stash save "Cambios locales antes de pull - $(date '+%Y-%m-%d %H:%M:%S')"
        log_success "Cambios guardados en stash"
    else
        log_warning "Continuando sin guardar cambios locales..."
    fi
fi

echo ""

# ========================================
# 3. OBTENER RAMA ACTUAL
# ========================================

CURRENT_BRANCH=$(git branch --show-current)
log_info "Rama actual: $CURRENT_BRANCH"
echo ""

# ========================================
# 4. HACER PULL DE LOS CAMBIOS
# ========================================

log_info "Obteniendo cambios desde GitHub..."

# Guardar el estado antes del pull para detectar cambios
CHANGED_FILES_BEFORE=$(git ls-files -m)
git fetch origin "$CURRENT_BRANCH" 2>&1

# Verificar si hay cambios remotos
LOCAL_COMMIT=$(git rev-parse HEAD)
REMOTE_COMMIT=$(git rev-parse "origin/$CURRENT_BRANCH")

if [ "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]; then
    log_success "No hay cambios nuevos en el repositorio remoto"
    echo ""
    log_info "Tu código está actualizado"
    exit 0
fi

log_info "Encontrados cambios nuevos. Aplicando pull..."
git pull origin "$CURRENT_BRANCH" 2>&1

if [ $? -ne 0 ]; then
    log_error "Error al hacer pull. Puede haber conflictos."
    log_warning "Revisa manualmente con: git status"
    exit 1
fi

log_success "Pull completado exitosamente"
echo ""

# ========================================
# 5. DETECTAR TIPOS DE CAMBIOS
# ========================================

log_info "Analizando cambios para determinar acciones necesarias..."

# Archivos críticos que requieren rebuild/restart
CRITICAL_FILES=(
    "CODE/requirements.txt"
    "CODE/Dockerfile"
    "CODE/Dockerfile.lightsail"
    "docker-compose.prod.yml"
    "docker-compose.lightsail.yml"
    "CODE/nginx/nginx.lightsail.conf"
    "deploy-lightsail.sh"
)

# Obtener cambios desde el último commit
CHANGED_FILES=$(git diff --name-only "$LOCAL_COMMIT".."$REMOTE_COMMIT")

NEEDS_REBUILD=false
NEEDS_RESTART=false
CRITICAL_CHANGES=""

for file in "${CRITICAL_FILES[@]}"; do
    if echo "$CHANGED_FILES" | grep -q "^$file$"; then
        CRITICAL_CHANGES="$CRITICAL_CHANGES\n  - $file"
        if [[ "$file" == *"requirements.txt"* ]] || [[ "$file" == *"Dockerfile"* ]]; then
            NEEDS_REBUILD=true
        fi
        if [[ "$file" == *"docker-compose"* ]]; then
            NEEDS_RESTART=true
        fi
    fi
done

# Detectar cambios en código Python/HTML/JS que se recargan automáticamente
CODE_CHANGES=$(echo "$CHANGED_FILES" | grep -E "\.(py|html|css|js|json)$" | grep "^CODE/src/" | wc -l)

echo ""

# ========================================
# 6. MOSTRAR RESUMEN DE CAMBIOS
# ========================================

log_info "Resumen de cambios:"
echo ""

if [ -n "$CRITICAL_CHANGES" ]; then
    log_warning "Archivos críticos modificados:$CRITICAL_CHANGES"
fi

if [ "$CODE_CHANGES" -gt 0 ]; then
    log_success "Archivos de código modificados: $CODE_CHANGES"
    log_info "Estos cambios se aplicarán automáticamente gracias a hot reload"
fi

echo ""

# ========================================
# 7. ACCIONES SEGÚN TIPO DE CAMBIOS
# ========================================

# Si hay cambios críticos, preguntar si hacer rebuild/restart
if [ "$NEEDS_REBUILD" = true ] || [ "$NEEDS_RESTART" = true ]; then
    log_warning "⚠️  Se detectaron cambios que requieren rebuild/restart"
    echo ""
    log_info "Archivos modificados:$CRITICAL_CHANGES"
    echo ""
    read -p "¿Deseas hacer rebuild y restart de los contenedores? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Reiniciando contenedores..."
        
        # Determinar qué docker-compose usar
        if [ -f "docker-compose.lightsail.yml" ] && docker compose -f docker-compose.lightsail.yml ps -q | grep -q .; then
            COMPOSE_FILE="docker-compose.lightsail.yml"
        elif [ -f "docker-compose.prod.yml" ] && docker compose -f docker-compose.prod.yml ps -q | grep -q .; then
            COMPOSE_FILE="docker-compose.prod.yml"
        else
            log_error "No se encontró un docker-compose activo"
            exit 1
        fi
        
        log_info "Usando: $COMPOSE_FILE"
        
        # Rebuild solo si hay cambios en requirements.txt o Dockerfile
        if [ "$NEEDS_REBUILD" = true ]; then
            log_info "Reconstruyendo imagen Docker..."
            docker compose -f "$COMPOSE_FILE" build --no-cache app
            
            if [ $? -eq 0 ]; then
                log_success "Imagen reconstruida"
            else
                log_error "Error al reconstruir la imagen"
                exit 1
            fi
        fi
        
        # Restart de contenedores
        log_info "Reiniciando contenedores..."
        docker compose -f "$COMPOSE_FILE" restart app
        
        if [ $? -eq 0 ]; then
            log_success "Contenedores reiniciados"
        else
            log_warning "Advertencia: algunos contenedores pueden no haberse reiniciado correctamente"
        fi
        
        echo ""
        log_info "Esperando a que los servicios estén listos..."
        sleep 5
        
        # Verificar health check
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            log_success "Health check exitoso"
        else
            log_warning "Health check falló. Revisa los logs con:"
            log_info "docker compose -f $COMPOSE_FILE logs -f app"
        fi
    else
        log_info "Omitiendo rebuild/restart. Los cambios críticos no se aplicarán hasta que reinicies manualmente."
    fi
else
    log_success "No se requieren acciones adicionales"
    log_info "Los cambios en código se aplicarán automáticamente gracias a hot reload"
    log_info "Uvicorn detectará los cambios y recargará la aplicación automáticamente"
fi

echo ""

# ========================================
# 8. VERIFICAR LOGS (opcional)
# ========================================

read -p "¿Deseas ver los logs de la aplicación? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "docker-compose.lightsail.yml" ] && docker compose -f docker-compose.lightsail.yml ps -q | grep -q .; then
        docker compose -f docker-compose.lightsail.yml logs -f --tail=50 app
    elif [ -f "docker-compose.prod.yml" ] && docker compose -f docker-compose.prod.yml ps -q | grep -q .; then
        docker compose -f docker-compose.prod.yml logs -f --tail=50 app
    fi
fi

echo ""
echo "========================================="
log_success "ACTUALIZACIÓN COMPLETADA"
echo "========================================="
echo ""
log_info "Comandos útiles:"
log_info "  - Ver logs: docker compose -f <archivo> logs -f app"
log_info "  - Ver estado: docker compose -f <archivo> ps"
log_info "  - Reiniciar manualmente: docker compose -f <archivo> restart app"
echo ""

