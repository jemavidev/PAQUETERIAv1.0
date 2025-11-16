#!/bin/bash
# ========================================
# SCRIPT DE DESPLIEGUE AUTOMATIZADO A AWS
# ========================================
# Uso: ./deploy-to-aws.sh [mensaje-commit]
# 
# Este script automatiza el flujo completo:
# 1. Commit y push a GitHub desde localhost
# 2. Pull y actualización en servidor AWS
# ========================================

set -e

# ========================================
# CONFIGURACIÓN (Edita estos valores)
# ========================================
AWS_HOST="papyrus"  # Alias SSH configurado
AWS_PROJECT_PATH="/home/ubuntu/paqueteria"  # Ruta del proyecto en servidor
GIT_BRANCH="main"  # Rama a usar

# ========================================
# Colores para output
# ========================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ========================================
# Funciones de logging
# ========================================
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

log_step() {
    echo -e "${CYAN}▶️  $1${NC}"
}

# ========================================
# Banner
# ========================================
echo ""
echo "========================================="
echo "🚀 DESPLIEGUE AUTOMATIZADO A AWS"
echo "========================================="
echo ""

# ========================================
# 1. VERIFICAR CONFIGURACIÓN
# ========================================
log_step "Verificando configuración..."

if [ "$AWS_HOST" = "usuario@tu-servidor-aws.com" ]; then
    log_error "Debes configurar AWS_HOST en este script"
    log_info "Edita deploy-to-aws.sh y cambia AWS_HOST por tu servidor real"
    exit 1
fi

if [ ! -d ".git" ]; then
    log_error "No estás en un repositorio Git"
    exit 1
fi

log_success "Configuración verificada"
echo ""

# ========================================
# 2. VERIFICAR ESTADO LOCAL
# ========================================
log_step "Verificando estado del repositorio local..."

# Verificar si hay cambios
if [[ -z $(git status -s) ]]; then
    log_info "No hay cambios locales para commitear"
    
    read -p "¿Deseas hacer pull en AWS de todas formas? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Operación cancelada"
        exit 0
    fi
    SKIP_COMMIT=true
else
    log_info "Cambios detectados:"
    git status -s | head -10
    echo ""
    SKIP_COMMIT=false
fi

# ========================================
# 3. COMMIT Y PUSH (si hay cambios)
# ========================================
if [ "$SKIP_COMMIT" = false ]; then
    log_step "Preparando commit..."
    
    # Obtener mensaje de commit
    if [ -n "$1" ]; then
        COMMIT_MSG="$1"
    else
        read -p "📝 Mensaje del commit: " COMMIT_MSG
        if [ -z "$COMMIT_MSG" ]; then
            COMMIT_MSG="update: cambios generales"
            log_warning "Usando mensaje por defecto: $COMMIT_MSG"
        fi
    fi
    
    # Mostrar archivos que se van a commitear
    log_info "Archivos a commitear:"
    git status -s
    echo ""
    
    read -p "¿Continuar con el commit? (Y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        log_info "Operación cancelada"
        exit 0
    fi
    
    # Hacer commit
    log_info "Haciendo commit..."
    git add .
    git commit -m "$COMMIT_MSG"
    log_success "Commit realizado: $COMMIT_MSG"
    
    # Push a GitHub
    log_info "Subiendo cambios a GitHub..."
    git push origin "$GIT_BRANCH"
    
    if [ $? -eq 0 ]; then
        log_success "Cambios subidos a GitHub correctamente"
    else
        log_error "Error al subir cambios a GitHub"
        exit 1
    fi
    
    echo ""
fi

# ========================================
# 4. DESPLEGAR EN AWS
# ========================================
log_step "Desplegando en servidor AWS..."

log_info "Conectando a: $AWS_HOST"
log_info "Directorio: $AWS_PROJECT_PATH"
echo ""

# Verificar conexión SSH
log_info "Verificando conexión SSH..."
if ! ssh -o ConnectTimeout=5 "$AWS_HOST" "echo 'Conexión exitosa'" > /dev/null 2>&1; then
    log_error "No se pudo conectar al servidor AWS"
    log_info "Verifica:"
    log_info "  - Que AWS_HOST esté configurado correctamente"
    log_info "  - Que tengas acceso SSH al servidor"
    log_info "  - Que tu clave SSH esté configurada"
    exit 1
fi
log_success "Conexión SSH verificada"
echo ""

# Ejecutar actualización en AWS
log_info "Ejecutando actualización en AWS..."
echo "─────────────────────────────────────────"

# Usar pull-update.sh que analiza cambios inteligentemente
ssh "$AWS_HOST" "cd $AWS_PROJECT_PATH && ./DOCS/scripts/deployment/pull-update.sh"

SSH_EXIT_CODE=$?

echo "─────────────────────────────────────────"
echo ""

if [ $SSH_EXIT_CODE -eq 0 ]; then
    log_success "Actualización en AWS completada exitosamente"
else
    log_error "Error durante la actualización en AWS"
    log_info "Revisa los logs arriba para más detalles"
    exit 1
fi

# ========================================
# 5. VERIFICACIÓN POST-DESPLIEGUE
# ========================================
log_step "Verificando despliegue..."

# Health check
log_info "Verificando health check..."
if ssh "$AWS_HOST" "curl -f http://localhost:8000/health" > /dev/null 2>&1; then
    log_success "Health check exitoso"
else
    log_warning "Health check falló (puede ser normal si el servidor está reiniciando)"
fi

# Estado de contenedores
log_info "Estado de contenedores:"
ssh "$AWS_HOST" "cd $AWS_PROJECT_PATH && docker compose -f docker-compose.prod.yml ps" || \
ssh "$AWS_HOST" "cd $AWS_PROJECT_PATH && docker compose -f docker-compose.lightsail.yml ps" || \
log_warning "No se pudo obtener estado de contenedores"

echo ""

# ========================================
# 6. RESUMEN FINAL
# ========================================
echo "========================================="
log_success "DESPLIEGUE COMPLETADO"
echo "========================================="
echo ""

if [ "$SKIP_COMMIT" = false ]; then
    log_info "📝 Commit: $COMMIT_MSG"
fi
log_info "🌐 Servidor: $AWS_HOST"
log_info "📁 Directorio: $AWS_PROJECT_PATH"
log_info "🌿 Rama: $GIT_BRANCH"
echo ""

log_info "Comandos útiles:"
echo "  Ver logs remotos:"
echo "    ssh $AWS_HOST 'cd $AWS_PROJECT_PATH && docker compose logs -f app'"
echo ""
echo "  Verificar estado:"
echo "    ssh $AWS_HOST 'cd $AWS_PROJECT_PATH && docker compose ps'"
echo ""
echo "  Reiniciar aplicación:"
echo "    ssh $AWS_HOST 'cd $AWS_PROJECT_PATH && docker compose restart app'"
echo ""

log_success "✨ Todo listo!"
echo ""
