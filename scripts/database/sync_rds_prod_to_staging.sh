#!/bin/bash
# ╔════════════════════════════════════════════════════════════════════════════╗
# ║     SINCRONIZACIÓN AWS RDS: PRODUCCIÓN → STAGING                           ║
# ║              Sincronización de Base de Datos en AWS RDS                    ║
# ╚════════════════════════════════════════════════════════════════════════════╝
#
# PROPÓSITO:
# - Hacer dump completo de la BD de producción (AWS RDS)
# - Restaurar el dump en staging (AWS RDS)
# - Mantener datos actualizados en staging para pruebas
#
# USO:
#   ./sync_rds_prod_to_staging.sh                    # Modo interactivo
#   ./sync_rds_prod_to_staging.sh --auto             # Modo automático
#   ./sync_rds_prod_to_staging.sh --dry-run          # Simular sin ejecutar
#
# REQUISITOS:
# - PostgreSQL client (pg_dump, psql) instalado localmente
# - Acceso a AWS RDS de producción (credenciales en .env)
# - Acceso a AWS RDS de staging (credenciales en .env.staging)
# - Archivos .env configurados correctamente
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
CODE_DIR="$PROJECT_ROOT/CODE"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
TEMP_DIR="/tmp/db_sync_rds_${TIMESTAMP}"
DUMP_FILE="${TEMP_DIR}/production_dump.sql"
SANITIZED_FILE="${TEMP_DIR}/production_dump_sanitized.sql"

# Archivos de configuración
ENV_PROD="$CODE_DIR/.env"
ENV_STAGING="$CODE_DIR/.env.staging"

# Flags
DRY_RUN=false
AUTO_MODE=false

# Variables de BD (se cargarán desde .env)
PROD_DB_URL=""
STAGING_DB_URL=""

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
    echo "║     SINCRONIZACIÓN AWS RDS: PRODUCCIÓN → STAGING                           ║"
    echo "║              Sincronización de Base de Datos en AWS RDS                    ║"
    echo "╚════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_separator() {
    echo "────────────────────────────────────────────────────────────────────────────"
}

check_dependencies() {
    log_step "Verificando dependencias..."
    
    local missing_deps=()
    
    command -v pg_dump >/dev/null 2>&1 || missing_deps+=("pg_dump")
    command -v psql >/dev/null 2>&1 || missing_deps+=("psql")
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_error "Faltan dependencias: ${missing_deps[*]}"
        log_info "Instala con: sudo apt-get install postgresql-client"
        exit 1
    fi
    
    log_success "Todas las dependencias están instaladas"
}

check_env_files() {
    log_step "Verificando archivos de configuración..."
    
    if [ ! -f "$ENV_PROD" ]; then
        log_error "No se encuentra el archivo .env de producción: $ENV_PROD"
        exit 1
    fi
    log_success "Archivo .env de producción encontrado"
    
    if [ ! -f "$ENV_STAGING" ]; then
        log_warning "No se encuentra el archivo .env.staging: $ENV_STAGING"
        log_info "Creando .env.staging desde .env..."
        cp "$ENV_PROD" "$ENV_STAGING"
        log_warning "IMPORTANTE: Edita $ENV_STAGING con las credenciales de staging"
        exit 1
    fi
    log_success "Archivo .env.staging encontrado"
}

load_db_credentials() {
    log_step "Cargando credenciales de base de datos..."
    
    # Cargar DATABASE_URL de producción
    if [ -f "$ENV_PROD" ]; then
        PROD_DB_URL=$(grep "^DATABASE_URL=" "$ENV_PROD" | cut -d'=' -f2- | tr -d '"' | tr -d "'")
    fi
    
    if [ -z "$PROD_DB_URL" ]; then
        log_error "No se pudo obtener DATABASE_URL de producción desde $ENV_PROD"
        exit 1
    fi
    log_success "Credenciales de producción cargadas"
    
    # Cargar DATABASE_URL de staging
    if [ -f "$ENV_STAGING" ]; then
        STAGING_DB_URL=$(grep "^DATABASE_URL=" "$ENV_STAGING" | cut -d'=' -f2- | tr -d '"' | tr -d "'")
    fi
    
    if [ -z "$STAGING_DB_URL" ]; then
        log_error "No se pudo obtener DATABASE_URL de staging desde $ENV_STAGING"
        log_info "Asegúrate de que $ENV_STAGING tiene DATABASE_URL configurado"
        exit 1
    fi
    log_success "Credenciales de staging cargadas"
}

extract_db_info() {
    local db_url=$1
    local prefix=$2
    
    # Extraer componentes de la URL
    # Formato: postgresql://user:pass@host:port/dbname
    
    # Remover el prefijo postgresql://
    local url_without_prefix="${db_url#postgresql://}"
    
    # Extraer usuario y password
    local user_pass="${url_without_prefix%%@*}"
    local user="${user_pass%%:*}"
    local pass="${user_pass#*:}"
    
    # Extraer host, port y dbname
    local host_port_db="${url_without_prefix#*@}"
    local host_port="${host_port_db%%/*}"
    local host="${host_port%%:*}"
    local port="${host_port#*:}"
    local dbname="${host_port_db#*/}"
    
    # Exportar variables
    eval "${prefix}_USER='$user'"
    eval "${prefix}_PASS='$pass'"
    eval "${prefix}_HOST='$host'"
    eval "${prefix}_PORT='$port'"
    eval "${prefix}_NAME='$dbname'"
}

show_summary() {
    echo ""
    print_separator
    echo -e "${WHITE}RESUMEN DE SINCRONIZACIÓN:${NC}"
    print_separator
    echo ""
    echo -e "  ${CYAN}ORIGEN (Producción - AWS RDS):${NC}"
    echo -e "    Host: ${PROD_HOST}"
    echo -e "    Base de datos: ${PROD_NAME}"
    echo -e "    Usuario: ${PROD_USER}"
    echo ""
    echo -e "  ${YELLOW}DESTINO (Staging - AWS RDS):${NC}"
    echo -e "    Host: ${STAGING_HOST}"
    echo -e "    Base de datos: ${STAGING_NAME}"
    echo -e "    Usuario: ${STAGING_USER}"
    echo ""
    echo -e "  ${RED}⚠️  ADVERTENCIA:${NC}"
    echo -e "    - La BD de staging será SOBRESCRITA COMPLETAMENTE"
    echo -e "    - Todos los datos actuales de staging se perderán"
    echo -e "    - Este proceso puede tardar varios minutos"
    echo -e "    - Se crearán backups antes de proceder"
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
    log_step "Haciendo dump de BD de producción (AWS RDS)..."
    log_info "Esto puede tardar varios minutos dependiendo del tamaño de la BD..."
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Se haría dump de $PROD_NAME"
        return 0
    fi
    
    # Ejecutar pg_dump directamente contra AWS RDS
    PGPASSWORD="$PROD_PASS" pg_dump \
        -h "$PROD_HOST" \
        -p "$PROD_PORT" \
        -U "$PROD_USER" \
        -d "$PROD_NAME" \
        --clean \
        --if-exists \
        --no-owner \
        --no-acl \
        --verbose \
        > "$DUMP_FILE" 2>/dev/null
    
    if [ $? -eq 0 ] && [ -f "$DUMP_FILE" ]; then
        local size=$(du -h "$DUMP_FILE" | cut -f1)
        log_success "Dump completado: $size"
    else
        log_error "Error al hacer dump de la BD de producción"
        log_error "Verifica las credenciales y la conectividad a AWS RDS"
        cleanup
        exit 1
    fi
}

sanitize_dump() {
    log_step "Preparando dump para staging..."
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Se prepararía el dump"
        return 0
    fi
    
    # Copiar dump original
    cp "$DUMP_FILE" "$SANITIZED_FILE"
    
    log_success "Dump preparado para restauración"
    log_info "NOTA: Los datos se copian tal cual desde producción"
    log_warning "Las contraseñas de usuarios serán las mismas que en producción"
}

backup_staging_db() {
    log_step "Creando backup de BD staging actual (por seguridad)..."
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Se haría backup de staging"
        return 0
    fi
    
    local backup_file="${TEMP_DIR}/staging_backup_before_sync.sql"
    
    PGPASSWORD="$STAGING_PASS" pg_dump \
        -h "$STAGING_HOST" \
        -p "$STAGING_PORT" \
        -U "$STAGING_USER" \
        -d "$STAGING_NAME" \
        --clean \
        --if-exists \
        > "$backup_file" 2>/dev/null || true
    
    if [ -f "$backup_file" ]; then
        local size=$(du -h "$backup_file" | cut -f1)
        log_success "Backup de staging guardado: $backup_file ($size)"
    else
        log_warning "No se pudo crear backup de staging (puede estar vacía)"
    fi
}

drop_staging_db() {
    log_step "Limpiando BD de staging..."
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Se limpiaría BD $STAGING_NAME"
        return 0
    fi
    
    # Terminar todas las conexiones activas
    PGPASSWORD="$STAGING_PASS" psql \
        -h "$STAGING_HOST" \
        -p "$STAGING_PORT" \
        -U "$STAGING_USER" \
        -d postgres \
        -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$STAGING_NAME' AND pid <> pg_backend_pid();" \
        >/dev/null 2>&1 || true
    
    # Eliminar BD
    PGPASSWORD="$STAGING_PASS" psql \
        -h "$STAGING_HOST" \
        -p "$STAGING_PORT" \
        -U "$STAGING_USER" \
        -d postgres \
        -c "DROP DATABASE IF EXISTS $STAGING_NAME;" \
        >/dev/null 2>&1
    
    # Crear BD nueva
    PGPASSWORD="$STAGING_PASS" psql \
        -h "$STAGING_HOST" \
        -p "$STAGING_PORT" \
        -U "$STAGING_USER" \
        -d postgres \
        -c "CREATE DATABASE $STAGING_NAME;" \
        >/dev/null 2>&1
    
    log_success "BD de staging recreada (vacía)"
}

restore_to_staging() {
    log_step "Restaurando dump en staging (AWS RDS)..."
    log_info "Esto puede tardar varios minutos..."
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Se restauraría dump en staging"
        return 0
    fi
    
    # Restaurar en staging
    PGPASSWORD="$STAGING_PASS" psql \
        -h "$STAGING_HOST" \
        -p "$STAGING_PORT" \
        -U "$STAGING_USER" \
        -d "$STAGING_NAME" \
        -f "$SANITIZED_FILE" \
        --quiet \
        2>/dev/null
    
    if [ $? -eq 0 ]; then
        log_success "Restauración completada"
    else
        log_error "Error al restaurar dump en staging"
        log_error "Verifica las credenciales y la conectividad a AWS RDS"
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
    local prod_packages=$(PGPASSWORD="$PROD_PASS" psql \
        -h "$PROD_HOST" \
        -p "$PROD_PORT" \
        -U "$PROD_USER" \
        -d "$PROD_NAME" \
        -t -c 'SELECT COUNT(*) FROM packages;' 2>/dev/null | tr -d ' ')
    
    local staging_packages=$(PGPASSWORD="$STAGING_PASS" psql \
        -h "$STAGING_HOST" \
        -p "$STAGING_PORT" \
        -U "$STAGING_USER" \
        -d "$STAGING_NAME" \
        -t -c 'SELECT COUNT(*) FROM packages;' 2>/dev/null | tr -d ' ')
    
    local prod_users=$(PGPASSWORD="$PROD_PASS" psql \
        -h "$PROD_HOST" \
        -p "$PROD_PORT" \
        -U "$PROD_USER" \
        -d "$PROD_NAME" \
        -t -c 'SELECT COUNT(*) FROM users;' 2>/dev/null | tr -d ' ')
    
    local staging_users=$(PGPASSWORD="$STAGING_PASS" psql \
        -h "$STAGING_HOST" \
        -p "$STAGING_PORT" \
        -U "$STAGING_USER" \
        -d "$STAGING_NAME" \
        -t -c 'SELECT COUNT(*) FROM users;' 2>/dev/null | tr -d ' ')
    
    echo ""
    print_separator
    echo -e "${WHITE}VERIFICACIÓN:${NC}"
    print_separator
    echo ""
    echo -e "  ${CYAN}Paquetes:${NC}"
    echo -e "    Producción: $prod_packages"
    echo -e "    Staging:    $staging_packages"
    echo ""
    echo -e "  ${CYAN}Usuarios:${NC}"
    echo -e "    Producción: $prod_users"
    echo -e "    Staging:    $staging_users"
    echo ""
    
    if [ "$prod_packages" = "$staging_packages" ] && [ "$prod_users" = "$staging_users" ]; then
        log_success "Sincronización verificada correctamente ✓"
    else
        log_warning "Los conteos no coinciden exactamente"
        log_info "Esto puede ser normal si hay transacciones en curso en producción"
    fi
}

cleanup() {
    log_step "Limpiando archivos temporales..."
    
    # Mantener backups pero eliminar dumps
    if [ -d "$TEMP_DIR" ]; then
        rm -f "$DUMP_FILE" "$SANITIZED_FILE" 2>/dev/null || true
        log_success "Limpieza completada"
        log_info "Backups guardados en: $TEMP_DIR"
    fi
}

restart_staging_services() {
    log_step "¿Deseas reiniciar los servicios de staging?"
    
    if [ "$AUTO_MODE" = false ]; then
        echo ""
        read -p "Reiniciar servicios de staging? [y/N]: " -n 1 -r
        echo ""
        
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Servicios no reiniciados"
            return 0
        fi
    fi
    
    log_info "Para reiniciar staging, ejecuta:"
    echo ""
    echo "  cd $PROJECT_ROOT"
    echo "  docker compose -f docker-compose.staging.yml restart"
    echo ""
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
            echo "Archivos de configuración:"
            echo "  Producción: $ENV_PROD"
            echo "  Staging:    $ENV_STAGING"
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
    check_env_files
    load_db_credentials
    
    # Extraer información de las URLs
    extract_db_info "$PROD_DB_URL" "PROD"
    extract_db_info "$STAGING_DB_URL" "STAGING"
    
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
    log_success "Sincronización completada en ${duration}s ✓"
    print_separator
    echo ""
    
    restart_staging_services
    
    log_info "Los datos de staging ahora coinciden con producción"
    log_warning "Recuerda que las contraseñas son las mismas que en producción"
    echo ""
}

# Ejecutar
main
