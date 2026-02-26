#!/bin/bash
# ╔════════════════════════════════════════════════════════════════════════════╗
# ║           SINCRONIZACIÓN BD: PRODUCCIÓN → STAGING                          ║
# ║                    Restauración Completa de BD                             ║
# ╚════════════════════════════════════════════════════════════════════════════╝
#
# PROPÓSITO:
# - Hacer dump completo de la BD de producción (PAQUETEX)
# - Sanitizar datos sensibles (contraseñas, tokens, etc.)
# - Eliminar completamente la BD de staging
# - Restaurar el dump en staging
#
# USO:
#   ./sync_production_to_staging.sh                    # Modo interactivo
#   ./sync_production_to_staging.sh --auto             # Modo automático (sin confirmación)
#   ./sync_production_to_staging.sh --dry-run          # Simular sin ejecutar
#
# REQUISITOS:
# - Acceso SSH al servidor de producción
# - Acceso SSH al servidor de staging
# - PostgreSQL client (pg_dump, psql)
# - Permisos de lectura en BD producción
# - Permisos de escritura en BD staging
#
# ════════════════════════════════════════════════════════════════════════════

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
TEMP_DIR="/tmp/db_sync_${TIMESTAMP}"
DUMP_FILE="${TEMP_DIR}/production_dump.sql"
SANITIZED_FILE="${TEMP_DIR}/production_dump_sanitized.sql"

# Flags
DRY_RUN=false
AUTO_MODE=false

# ════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE SERVIDORES
# ════════════════════════════════════════════════════════════════════════════

# PRODUCCIÓN (PAQUETEX)
PROD_SSH_HOST="papyrus"
PROD_SSH_USER="ubuntu"
PROD_DB_HOST="localhost"  # Desde el servidor de producción
PROD_DB_PORT="5432"
PROD_DB_NAME="paquetex"
PROD_DB_USER="postgres"
# PROD_DB_PASSWORD se obtiene del servidor

# STAGING
STAGING_SSH_HOST="staging"
STAGING_SSH_USER="ubuntu"
STAGING_DB_HOST="localhost"  # Desde el servidor de staging
STAGING_DB_PORT="5432"
STAGING_DB_NAME="staging"
STAGING_DB_USER="postgres"
# STAGING_DB_PASSWORD se obtiene del servidor

# ════════════════════════════════════════════════════════════════════════════
# FUNCIONES
# ════════════════════════════════════════════════════════════════════════════

log_success() { echo -e "${GREEN}✓${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }
log_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
log_info() { echo -e "${CYAN}ℹ${NC} $1"; }
log_step() { echo -e "${BLUE}▶${NC} $1"; }

print_banner() {
    clear
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════════════════════╗"
    echo "║           SINCRONIZACIÓN BD: PRODUCCIÓN → STAGING                          ║"
    echo "║                    Restauración Completa de BD                             ║"
    echo "╚════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_separator() {
    echo "────────────────────────────────────────────────────────────────────────────"
}

check_dependencies() {
    log_step "Verificando dependencias..."
    
    local missing_deps=()
    
    command -v ssh >/dev/null 2>&1 || missing_deps+=("ssh")
    command -v scp >/dev/null 2>&1 || missing_deps+=("scp")
    command -v pg_dump >/dev/null 2>&1 || missing_deps+=("pg_dump")
    command -v psql >/dev/null 2>&1 || missing_deps+=("psql")
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_error "Faltan dependencias: ${missing_deps[*]}"
        log_info "Instala con: sudo apt-get install postgresql-client openssh-client"
        exit 1
    fi
    
    log_success "Todas las dependencias están instaladas"
}

check_ssh_access() {
    log_step "Verificando acceso SSH..."
    
    # Verificar acceso a producción
    if ! ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$PROD_SSH_USER@$PROD_SSH_HOST" "echo 'OK'" >/dev/null 2>&1; then
        log_error "No se puede conectar al servidor de producción: $PROD_SSH_HOST"
        exit 1
    fi
    log_success "Acceso a producción: OK"
    
    # Verificar acceso a staging
    if ! ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$STAGING_SSH_USER@$STAGING_SSH_HOST" "echo 'OK'" >/dev/null 2>&1; then
        log_error "No se puede conectar al servidor de staging: $STAGING_SSH_HOST"
        exit 1
    fi
    log_success "Acceso a staging: OK"
}

get_db_credentials() {
    log_step "Obteniendo credenciales de BD..."
    
    # Obtener password de producción desde .env
    PROD_DB_PASSWORD=$(ssh "$PROD_SSH_USER@$PROD_SSH_HOST" "grep '^POSTGRES_PASSWORD=' /home/ubuntu/paqueteria/.env 2>/dev/null | cut -d'=' -f2" 2>/dev/null || echo "")
    
    if [ -z "$PROD_DB_PASSWORD" ]; then
        log_warning "No se pudo obtener password de producción automáticamente"
        read -sp "Ingresa password de BD producción: " PROD_DB_PASSWORD
        echo ""
    fi
    
    # Obtener password de staging desde .env
    STAGING_DB_PASSWORD=$(ssh "$STAGING_SSH_USER@$STAGING_SSH_HOST" "grep '^POSTGRES_PASSWORD=' /home/ubuntu/paqueteria-staging/.env 2>/dev/null | cut -d'=' -f2" 2>/dev/null || echo "")
    
    if [ -z "$STAGING_DB_PASSWORD" ]; then
        log_warning "No se pudo obtener password de staging automáticamente"
        read -sp "Ingresa password de BD staging: " STAGING_DB_PASSWORD
        echo ""
    fi
    
    log_success "Credenciales obtenidas"
}

show_summary() {
    echo ""
    print_separator
    echo -e "${WHITE}RESUMEN DE SINCRONIZACIÓN:${NC}"
    print_separator
    echo ""
    echo -e "  ${CYAN}ORIGEN (Producción):${NC}"
    echo -e "    Servidor: $PROD_SSH_HOST"
    echo -e "    Base de datos: $PROD_DB_NAME"
    echo -e "    Usuario: $PROD_DB_USER"
    echo ""
    echo -e "  ${YELLOW}DESTINO (Staging):${NC}"
    echo -e "    Servidor: $STAGING_SSH_HOST"
    echo -e "    Base de datos: $STAGING_DB_NAME"
    echo -e "    Usuario: $STAGING_DB_USER"
    echo ""
    echo -e "  ${RED}⚠️  ADVERTENCIA:${NC}"
    echo -e "    - La BD de staging será ELIMINADA COMPLETAMENTE"
    echo -e "    - Todos los datos actuales de staging se perderán"
    echo -e "    - Este proceso puede tardar varios minutos"
    echo ""
    print_separator
}

confirm_sync() {
    if [ "$AUTO_MODE" = true ]; then
        log_info "Modo automático: continuando sin confirmación"
        return 0
    fi
    
    echo ""
    read -p "¿Deseas continuar con la sincronización? [y/N]: " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_error "Sincronización cancelada por el usuario"
        exit 0
    fi
}

create_temp_dir() {
    log_step "Creando directorio temporal..."
    mkdir -p "$TEMP_DIR"
    log_success "Directorio temporal: $TEMP_DIR"
}

dump_production_db() {
    log_step "Haciendo dump de BD de producción..."
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Se haría dump de $PROD_DB_NAME"
        return 0
    fi
    
    # Ejecutar pg_dump en el servidor de producción
    ssh "$PROD_SSH_USER@$PROD_SSH_HOST" "PGPASSWORD='$PROD_DB_PASSWORD' pg_dump -h $PROD_DB_HOST -p $PROD_DB_PORT -U $PROD_DB_USER -d $PROD_DB_NAME --clean --if-exists --no-owner --no-acl" > "$DUMP_FILE" 2>/dev/null
    
    if [ $? -eq 0 ] && [ -f "$DUMP_FILE" ]; then
        local size=$(du -h "$DUMP_FILE" | cut -f1)
        log_success "Dump completado: $size"
    else
        log_error "Error al hacer dump de la BD"
        cleanup
        exit 1
    fi
}

sanitize_dump() {
    log_step "Sanitizando datos sensibles..."
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Se sanitizarían datos sensibles"
        return 0
    fi
    
    # Copiar dump original
    cp "$DUMP_FILE" "$SANITIZED_FILE"
    
    # Sanitizar contraseñas de usuarios (mantener estructura pero cambiar valores)
    # Cambiar todos los password_hash a un valor genérico
    sed -i "s/password_hash', '[^']*'/password_hash', '\$2b\$12\$SANITIZED_PASSWORD_HASH'/g" "$SANITIZED_FILE"
    
    # Sanitizar tokens de API
    sed -i "s/api_token', '[^']*'/api_token', 'SANITIZED_TOKEN'/g" "$SANITIZED_FILE"
    sed -i "s/api_key', '[^']*'/api_key', 'SANITIZED_API_KEY'/g" "$SANITIZED_FILE"
    
    # Sanitizar tokens de sesión
    sed -i "s/session_token', '[^']*'/session_token', 'SANITIZED_SESSION'/g" "$SANITIZED_FILE"
    
    # Sanitizar claves de recuperación
    sed -i "s/reset_token', '[^']*'/reset_token', 'SANITIZED_RESET_TOKEN'/g" "$SANITIZED_FILE"
    
    log_success "Datos sensibles sanitizados"
    log_warning "NOTA: Los usuarios no podrán iniciar sesión con sus contraseñas originales"
    log_info "Deberás restablecer contraseñas manualmente si es necesario"
}

backup_staging_db() {
    log_step "Creando backup de BD staging actual (por seguridad)..."
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Se haría backup de staging"
        return 0
    fi
    
    local backup_file="/tmp/staging_backup_before_sync_${TIMESTAMP}.sql"
    
    ssh "$STAGING_SSH_USER@$STAGING_SSH_HOST" "PGPASSWORD='$STAGING_DB_PASSWORD' pg_dump -h $STAGING_DB_HOST -p $STAGING_DB_PORT -U $STAGING_DB_USER -d $STAGING_DB_NAME --clean --if-exists" > "$backup_file" 2>/dev/null || true
    
    if [ -f "$backup_file" ]; then
        log_success "Backup de staging guardado: $backup_file"
    else
        log_warning "No se pudo crear backup de staging (puede estar vacía)"
    fi
}

drop_staging_db() {
    log_step "Eliminando BD de staging..."
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Se eliminaría BD $STAGING_DB_NAME"
        return 0
    fi
    
    # Terminar todas las conexiones activas
    ssh "$STAGING_SSH_USER@$STAGING_SSH_HOST" "PGPASSWORD='$STAGING_DB_PASSWORD' psql -h $STAGING_DB_HOST -p $STAGING_DB_PORT -U $STAGING_DB_USER -d postgres -c \"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$STAGING_DB_NAME' AND pid <> pg_backend_pid();\"" >/dev/null 2>&1 || true
    
    # Eliminar BD
    ssh "$STAGING_SSH_USER@$STAGING_SSH_HOST" "PGPASSWORD='$STAGING_DB_PASSWORD' psql -h $STAGING_DB_HOST -p $STAGING_DB_PORT -U $STAGING_DB_USER -d postgres -c \"DROP DATABASE IF EXISTS $STAGING_DB_NAME;\"" >/dev/null 2>&1
    
    # Crear BD nueva
    ssh "$STAGING_SSH_USER@$STAGING_SSH_HOST" "PGPASSWORD='$STAGING_DB_PASSWORD' psql -h $STAGING_DB_HOST -p $STAGING_DB_PORT -U $STAGING_DB_USER -d postgres -c \"CREATE DATABASE $STAGING_DB_NAME;\"" >/dev/null 2>&1
    
    log_success "BD de staging recreada (vacía)"
}

restore_to_staging() {
    log_step "Restaurando dump en staging..."
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Se restauraría dump en staging"
        return 0
    fi
    
    # Transferir dump sanitizado al servidor de staging
    scp -o StrictHostKeyChecking=no "$SANITIZED_FILE" "$STAGING_SSH_USER@$STAGING_SSH_HOST:/tmp/dump_to_restore.sql" >/dev/null 2>&1
    
    # Restaurar en staging
    ssh "$STAGING_SSH_USER@$STAGING_SSH_HOST" "PGPASSWORD='$STAGING_DB_PASSWORD' psql -h $STAGING_DB_HOST -p $STAGING_DB_PORT -U $STAGING_DB_USER -d $STAGING_DB_NAME -f /tmp/dump_to_restore.sql" >/dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        log_success "Restauración completada"
        
        # Limpiar archivo temporal en staging
        ssh "$STAGING_SSH_USER@$STAGING_SSH_HOST" "rm -f /tmp/dump_to_restore.sql" >/dev/null 2>&1
    else
        log_error "Error al restaurar dump en staging"
        cleanup
        exit 1
    fi
}

verify_sync() {
    log_step "Verificando sincronización..."
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Se verificaría la sincronización"
        return 0
    fi
    
    # Contar registros en tablas principales
    local prod_packages=$(ssh "$PROD_SSH_USER@$PROD_SSH_HOST" "PGPASSWORD='$PROD_DB_PASSWORD' psql -h $PROD_DB_HOST -p $PROD_DB_PORT -U $PROD_DB_USER -d $PROD_DB_NAME -t -c 'SELECT COUNT(*) FROM packages;'" 2>/dev/null | tr -d ' ')
    
    local staging_packages=$(ssh "$STAGING_SSH_USER@$STAGING_SSH_HOST" "PGPASSWORD='$STAGING_DB_PASSWORD' psql -h $STAGING_DB_HOST -p $STAGING_DB_PORT -U $STAGING_DB_USER -d $STAGING_DB_NAME -t -c 'SELECT COUNT(*) FROM packages;'" 2>/dev/null | tr -d ' ')
    
    echo ""
    print_separator
    echo -e "${WHITE}VERIFICACIÓN:${NC}"
    print_separator
    echo ""
    echo -e "  ${CYAN}Paquetes en Producción:${NC} $prod_packages"
    echo -e "  ${CYAN}Paquetes en Staging:${NC} $staging_packages"
    echo ""
    
    if [ "$prod_packages" = "$staging_packages" ]; then
        log_success "Sincronización verificada correctamente"
    else
        log_warning "Los conteos no coinciden exactamente (puede ser normal si hay transacciones en curso)"
    fi
}

cleanup() {
    log_step "Limpiando archivos temporales..."
    rm -rf "$TEMP_DIR" 2>/dev/null || true
    log_success "Limpieza completada"
}

# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════

# Procesar argumentos
while [ $# -gt 0 ]; do
    case "$1" in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --auto)
            AUTO_MODE=true
            shift
            ;;
        --help|-h)
            print_banner
            echo "Uso: $0 [opciones]"
            echo ""
            echo "Opciones:"
            echo "  --auto      Modo automático (sin confirmación)"
            echo "  --dry-run   Simular sin ejecutar"
            echo "  --help      Mostrar esta ayuda"
            echo ""
            exit 0
            ;;
        *)
            log_error "Opción desconocida: $1"
            exit 1
            ;;
    esac
done

# Ejecutar sincronización
main() {
    local start_time=$(date +%s)
    
    print_banner
    
    check_dependencies
    check_ssh_access
    get_db_credentials
    show_summary
    confirm_sync
    
    echo ""
    log_info "Iniciando sincronización..."
    echo ""
    
    create_temp_dir
    dump_production_db
    sanitize_dump
    backup_staging_db
    drop_staging_db
    restore_to_staging
    verify_sync
    cleanup
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    echo ""
    print_separator
    log_success "Sincronización completada en ${duration}s"
    print_separator
    echo ""
    log_warning "IMPORTANTE: Las contraseñas han sido sanitizadas"
    log_info "Los usuarios no podrán iniciar sesión hasta que restablezcan sus contraseñas"
    echo ""
}

# Ejecutar
main
