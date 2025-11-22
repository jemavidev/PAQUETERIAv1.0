#!/bin/bash
# ========================================
# DEPLOY MANAGER - PAQUETEX v4.0
# ========================================
# Script unificado para deploy de localhost a AWS Cloud Server "papyrus"
# Autor: Equipo de Desarrollo
# Fecha: 2024-11-22
# Versión: 1.0.0
# ========================================

set -e  # Salir si hay error (se desactiva en modo interactivo)

# ========================================
# CONFIGURACIÓN
# ========================================
AWS_HOST="papyrus"
AWS_PROJECT_PATH="/home/ubuntu/paqueteria"
GIT_BRANCH="main"
SCRIPT_VERSION="1.0.0"
DEPLOY_HISTORY_FILE=".deploy-history"
CONFIG_FILE=".deploy-config"

# ========================================
# COLORES
# ========================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m'

# ========================================
# FUNCIONES DE LOGGING
# ========================================
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_step() { echo -e "${CYAN}▶️  $1${NC}"; }
log_debug() { [ "$VERBOSE" = true ] && echo -e "${GRAY}🔍 $1${NC}"; }

# ========================================
# FUNCIONES DE UI
# ========================================

print_banner() {
    clear
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                                                            ║"
    echo "║           🚀 DEPLOY MANAGER - PAQUETEX v4.0               ║"
    echo "║                                                            ║"
    echo "║              Servidor: ${WHITE}papyrus${CYAN}                            ║"
    echo "║              Versión: ${WHITE}$SCRIPT_VERSION${CYAN}                           ║"
    echo "║                                                            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_separator() {
    echo -e "${GRAY}────────────────────────────────────────────────────────────${NC}"
}

spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

progress_bar() {
    local current=$1
    local total=$2
    local width=40
    local percentage=$((current * 100 / total))
    local completed=$((width * current / total))
    local remaining=$((width - completed))
    
    printf "\r["
    printf "%${completed}s" | tr ' ' '█'
    printf "%${remaining}s" | tr ' ' '░'
    printf "] %3d%% (%d/%d)" $percentage $current $total
}


# ========================================
# FUNCIONES DE VALIDACIÓN
# ========================================
check_requirements() {
    log_step "Verificando requisitos..."
    
    local missing=0
    
    if ! command -v git &> /dev/null; then
        log_error "Git no está instalado"
        missing=1
    fi
    
    if ! command -v ssh &> /dev/null; then
        log_error "SSH no está instalado"
        missing=1
    fi
    
    if [ ! -d ".git" ]; then
        log_error "No estás en un repositorio Git"
        missing=1
    fi
    
    if [ $missing -eq 1 ]; then
        return 1
    fi
    
    log_success "Requisitos verificados"
    return 0
}

check_ssh_connection() {
    log_step "Verificando conexión SSH..."
    
    if ssh -o ConnectTimeout=5 -o BatchMode=yes "$AWS_HOST" "echo 'OK'" &> /dev/null; then
        log_success "Conexión SSH verificada"
        return 0
    else
        log_error "No se pudo conectar a $AWS_HOST"
        log_info "Verifica tu configuración SSH"
        return 1
    fi
}

check_git_status() {
    if [[ -z $(git status -s) ]]; then
        return 1  # No hay cambios
    else
        return 0  # Hay cambios
    fi
}


# ========================================
# FUNCIONES DE GIT
# ========================================
show_git_status() {
    echo ""
    log_info "Estado del repositorio:"
    print_separator
    
    # Archivos modificados
    local modified=$(git status -s | grep "^ M" | wc -l)
    local added=$(git status -s | grep "^A" | wc -l)
    local deleted=$(git status -s | grep "^D" | wc -l)
    local untracked=$(git status -s | grep "^??" | wc -l)
    
    echo -e "  ${YELLOW}Modificados:${NC} $modified"
    echo -e "  ${GREEN}Nuevos:${NC} $added"
    echo -e "  ${RED}Eliminados:${NC} $deleted"
    echo -e "  ${GRAY}Sin trackear:${NC} $untracked"
    
    echo ""
    if [ $modified -gt 0 ] || [ $added -gt 0 ] || [ $deleted -gt 0 ]; then
        git status -s | head -15
        local total=$(git status -s | wc -l)
        if [ $total -gt 15 ]; then
            echo -e "${GRAY}... y $((total - 15)) archivos más${NC}"
        fi
    fi
    print_separator
}

git_commit_and_push() {
    local commit_msg="$1"
    
    log_step "Preparando commit..."
    
    if [ -z "$commit_msg" ]; then
        echo ""
        read -p "📝 Mensaje del commit: " commit_msg
        if [ -z "$commit_msg" ]; then
            commit_msg="update: cambios generales $(date +%Y%m%d_%H%M%S)"
            log_warning "Usando mensaje automático"
        fi
    fi
    
    echo ""
    log_info "Archivos a commitear:"
    git status -s
    echo ""
    
    read -p "¿Continuar con el commit? [Y/n]: " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        log_warning "Commit cancelado"
        return 1
    fi
    
    log_info "Haciendo commit..."
    git add .
    git commit -m "$commit_msg"
    
    log_info "Subiendo a GitHub..."
    git push origin "$GIT_BRANCH"
    
    log_success "Cambios subidos: $commit_msg"
    
    # Guardar en historial
    echo "$(date '+%Y-%m-%d %H:%M:%S')|commit|$commit_msg|$USER" >> "$DEPLOY_HISTORY_FILE"
    
    return 0
}


git_stash_changes() {
    log_step "Guardando cambios en stash..."
    git stash push -m "Deploy stash $(date +%Y%m%d_%H%M%S)"
    log_success "Cambios guardados en stash"
}

git_reset_changes() {
    echo ""
    log_warning "⚠️  ADVERTENCIA: Esto descartará TODOS los cambios locales"
    read -p "¿Estás seguro? Escribe 'SI' para confirmar: " confirm
    
    if [ "$confirm" = "SI" ]; then
        git reset --hard HEAD
        git clean -fd
        log_success "Cambios descartados"
    else
        log_info "Operación cancelada"
    fi
}

git_show_diff() {
    log_info "Cambios en archivos:"
    print_separator
    git diff --stat
    echo ""
    read -p "¿Ver diff completo? [y/N]: " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git diff | less
    fi
}

git_rollback() {
    log_step "Preparando rollback..."
    echo ""
    log_info "Últimos 10 commits:"
    print_separator
    
    git log --oneline -10 | nl -w2 -s'. '
    
    echo ""
    read -p "Selecciona el número del commit para rollback [1-10] (0 para cancelar): " choice
    
    if [ "$choice" -eq 0 ] 2>/dev/null; then
        log_info "Rollback cancelado"
        return 1
    fi
    
    if [ "$choice" -ge 1 ] && [ "$choice" -le 10 ] 2>/dev/null; then
        local commit_hash=$(git log --oneline -10 | sed -n "${choice}p" | awk '{print $1}')
        
        echo ""
        log_warning "⚠️  Esto hará rollback a: $(git log --oneline -1 $commit_hash)"
        read -p "¿Continuar? [y/N]: " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git reset --hard $commit_hash
            git push -f origin "$GIT_BRANCH"
            log_success "Rollback completado a $commit_hash"
            return 0
        fi
    else
        log_error "Opción inválida"
    fi
    
    return 1
}


# ========================================
# FUNCIONES DE DEPLOY REMOTO
# ========================================
remote_deploy() {
    log_step "Iniciando deploy en servidor remoto..."
    echo ""
    
    local start_time=$(date +%s)
    
    # Paso 1: Pull cambios
    echo -e "${CYAN}[1/6]${NC} 📥 Descargando cambios desde GitHub..."
    ssh "$AWS_HOST" "cd $AWS_PROJECT_PATH && git fetch origin $GIT_BRANCH && git pull origin $GIT_BRANCH" || {
        log_error "Error al hacer pull"
        return 1
    }
    log_success "Cambios descargados"
    
    # Paso 2: Verificar cambios
    echo -e "${CYAN}[2/6]${NC} 🔍 Analizando cambios..."
    local files_changed=$(ssh "$AWS_HOST" "cd $AWS_PROJECT_PATH && git diff HEAD@{1} --name-only | wc -l")
    log_info "Archivos modificados: $files_changed"
    
    # Paso 3: Actualizar servicios
    echo -e "${CYAN}[3/6]${NC} 🔄 Actualizando servicios..."
    ssh "$AWS_HOST" "cd $AWS_PROJECT_PATH && docker compose -f docker-compose.prod.yml pull" 2>/dev/null || \
    ssh "$AWS_HOST" "cd $AWS_PROJECT_PATH && docker compose -f docker-compose.lightsail.yml pull" 2>/dev/null
    
    ssh "$AWS_HOST" "cd $AWS_PROJECT_PATH && docker compose -f docker-compose.prod.yml up -d" 2>/dev/null || \
    ssh "$AWS_HOST" "cd $AWS_PROJECT_PATH && docker compose -f docker-compose.lightsail.yml up -d" || {
        log_error "Error al actualizar servicios"
        return 1
    }
    log_success "Servicios actualizados"
    
    # Paso 4: Esperar health check
    echo -e "${CYAN}[4/6]${NC} ⏳ Esperando health check..."
    local attempts=0
    local max_attempts=30
    while [ $attempts -lt $max_attempts ]; do
        if ssh "$AWS_HOST" "curl -f http://localhost:8000/health" &> /dev/null; then
            log_success "Health check exitoso"
            break
        fi
        attempts=$((attempts + 1))
        printf "."
        sleep 2
    done
    echo ""
    
    if [ $attempts -eq $max_attempts ]; then
        log_warning "Health check timeout (puede ser normal)"
    fi
    
    # Paso 5: Tests de humo
    echo -e "${CYAN}[5/6]${NC} 🧪 Ejecutando tests de humo..."
    local tests_passed=0
    local tests_total=3
    
    if ssh "$AWS_HOST" "curl -f http://localhost:8000/health" &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} GET /health → 200"
        tests_passed=$((tests_passed + 1))
    else
        echo -e "  ${RED}✗${NC} GET /health → Error"
    fi
    
    if ssh "$AWS_HOST" "curl -f http://localhost:8000/api/packages" &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} GET /api/packages → 200"
        tests_passed=$((tests_passed + 1))
    else
        echo -e "  ${RED}✗${NC} GET /api/packages → Error"
    fi
    
    if ssh "$AWS_HOST" "docker exec \$(docker ps -qf name=redis) redis-cli ping" 2>/dev/null | grep -q "PONG"; then
        echo -e "  ${GREEN}✓${NC} Redis ping → PONG"
        tests_passed=$((tests_passed + 1))
    else
        echo -e "  ${RED}✗${NC} Redis ping → Error"
    fi
    
    echo -e "  Tests: $tests_passed/$tests_total pasados"
    
    # Paso 6: Verificar métricas
    echo -e "${CYAN}[6/6]${NC} 📊 Verificando métricas..."
    ssh "$AWS_HOST" "docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}'" 2>/dev/null | head -5
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    echo ""
    log_success "Deploy completado en ${duration}s"
    
    # Guardar en historial
    echo "$(date '+%Y-%m-%d %H:%M:%S')|deploy|success|${duration}s|$USER" >> "$DEPLOY_HISTORY_FILE"
    
    return 0
}


remote_restart() {
    log_step "Reiniciando servicios remotos..."
    
    ssh "$AWS_HOST" "cd $AWS_PROJECT_PATH && docker compose -f docker-compose.prod.yml restart" 2>/dev/null || \
    ssh "$AWS_HOST" "cd $AWS_PROJECT_PATH && docker compose -f docker-compose.lightsail.yml restart" || {
        log_error "Error al reiniciar servicios"
        return 1
    }
    
    log_success "Servicios reiniciados"
    
    # Esperar health check
    log_info "Esperando health check..."
    sleep 10
    
    if ssh "$AWS_HOST" "curl -f http://localhost:8000/health" &> /dev/null; then
        log_success "Servidor respondiendo correctamente"
    else
        log_warning "Servidor no responde (puede estar iniciando)"
    fi
}

remote_status() {
    log_step "Obteniendo estado del servidor..."
    echo ""
    
    print_separator
    echo -e "${WHITE}SERVICIOS:${NC}"
    ssh "$AWS_HOST" "cd $AWS_PROJECT_PATH && docker compose ps" 2>/dev/null || \
    ssh "$AWS_HOST" "cd $AWS_PROJECT_PATH && docker compose -f docker-compose.prod.yml ps" 2>/dev/null || \
    ssh "$AWS_HOST" "cd $AWS_PROJECT_PATH && docker compose -f docker-compose.lightsail.yml ps"
    
    echo ""
    print_separator
    echo -e "${WHITE}RECURSOS:${NC}"
    ssh "$AWS_HOST" "docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}'"
    
    echo ""
    print_separator
    echo -e "${WHITE}ESPACIO EN DISCO:${NC}"
    ssh "$AWS_HOST" "df -h | grep -E '(Filesystem|/$)'"
    
    echo ""
    print_separator
}

remote_logs() {
    echo ""
    log_info "Opciones de logs:"
    echo ""
    echo "  [1] Ver últimas 50 líneas"
    echo "  [2] Ver últimas 100 líneas"
    echo "  [3] Ver logs en tiempo real (Ctrl+C para salir)"
    echo "  [4] Buscar en logs (grep)"
    echo "  [5] Logs de servicio específico"
    echo "  [0] Volver"
    echo ""
    
    read -p "Selecciona opción: " log_option
    
    case $log_option in
        1)
            ssh "$AWS_HOST" "cd $AWS_PROJECT_PATH && docker compose logs --tail=50"
            ;;
        2)
            ssh "$AWS_HOST" "cd $AWS_PROJECT_PATH && docker compose logs --tail=100"
            ;;
        3)
            log_info "Mostrando logs en tiempo real (Ctrl+C para salir)..."
            ssh "$AWS_HOST" "cd $AWS_PROJECT_PATH && docker compose logs -f"
            ;;
        4)
            read -p "Buscar texto: " search_text
            ssh "$AWS_HOST" "cd $AWS_PROJECT_PATH && docker compose logs | grep '$search_text'"
            ;;
        5)
            echo ""
            echo "Servicios disponibles: app, redis, postgres, nginx"
            read -p "Nombre del servicio: " service_name
            ssh "$AWS_HOST" "cd $AWS_PROJECT_PATH && docker compose logs -f $service_name"
            ;;
        0)
            return
            ;;
        *)
            log_error "Opción inválida"
            ;;
    esac
    
    echo ""
    read -p "Presiona Enter para continuar..."
}


remote_health_check() {
    log_step "Ejecutando health check completo..."
    echo ""
    
    print_separator
    echo -e "${WHITE}SERVICIOS:${NC}"
    
    # Verificar servicios
    local services=("app" "redis" "postgres")
    for service in "${services[@]}"; do
        if ssh "$AWS_HOST" "docker ps | grep -q $service" 2>/dev/null; then
            echo -e "  ${GREEN}✓${NC} $service → Running"
        else
            echo -e "  ${RED}✗${NC} $service → Stopped"
        fi
    done
    
    echo ""
    print_separator
    echo -e "${WHITE}ENDPOINTS:${NC}"
    
    # Verificar endpoints
    local health_status=$(ssh "$AWS_HOST" "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health" 2>/dev/null)
    if [ "$health_status" = "200" ]; then
        echo -e "  ${GREEN}✓${NC} GET /health → 200 OK"
    else
        echo -e "  ${RED}✗${NC} GET /health → $health_status"
    fi
    
    local packages_status=$(ssh "$AWS_HOST" "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/packages" 2>/dev/null)
    if [ "$packages_status" = "200" ]; then
        echo -e "  ${GREEN}✓${NC} GET /api/packages → 200 OK"
    else
        echo -e "  ${RED}✗${NC} GET /api/packages → $packages_status"
    fi
    
    echo ""
    print_separator
    echo -e "${WHITE}RECURSOS:${NC}"
    
    # Verificar recursos
    ssh "$AWS_HOST" "docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}'" | head -5
    
    echo ""
    print_separator
    echo -e "${WHITE}CONECTIVIDAD:${NC}"
    
    # Verificar Redis
    if ssh "$AWS_HOST" "docker exec \$(docker ps -qf name=redis) redis-cli ping" 2>/dev/null | grep -q "PONG"; then
        echo -e "  ${GREEN}✓${NC} Redis → PONG"
    else
        echo -e "  ${RED}✗${NC} Redis → No responde"
    fi
    
    echo ""
    print_separator
    
    # Estado general
    if [ "$health_status" = "200" ] && [ "$packages_status" = "200" ]; then
        echo -e "${GREEN}Estado General: ✅ SALUDABLE${NC}"
    else
        echo -e "${YELLOW}Estado General: ⚠️  CON PROBLEMAS${NC}"
    fi
    
    echo ""
    read -p "Presiona Enter para continuar..."
}

remote_rebuild() {
    echo ""
    log_warning "⚠️  Esto reconstruirá los contenedores (puede tardar varios minutos)"
    read -p "¿Continuar? [y/N]: " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Operación cancelada"
        return
    fi
    
    log_step "Reconstruyendo contenedores..."
    
    ssh "$AWS_HOST" "cd $AWS_PROJECT_PATH && docker compose -f docker-compose.prod.yml down" 2>/dev/null || \
    ssh "$AWS_HOST" "cd $AWS_PROJECT_PATH && docker compose -f docker-compose.lightsail.yml down"
    
    ssh "$AWS_HOST" "cd $AWS_PROJECT_PATH && docker compose -f docker-compose.prod.yml build --no-cache" 2>/dev/null || \
    ssh "$AWS_HOST" "cd $AWS_PROJECT_PATH && docker compose -f docker-compose.lightsail.yml build --no-cache"
    
    ssh "$AWS_HOST" "cd $AWS_PROJECT_PATH && docker compose -f docker-compose.prod.yml up -d" 2>/dev/null || \
    ssh "$AWS_HOST" "cd $AWS_PROJECT_PATH && docker compose -f docker-compose.lightsail.yml up -d"
    
    log_success "Rebuild completado"
    
    log_info "Esperando que los servicios estén listos..."
    sleep 15
    
    remote_health_check
}


remote_migrations() {
    log_step "Gestión de migraciones..."
    echo ""
    
    echo "  [1] Ver migraciones pendientes"
    echo "  [2] Ejecutar migraciones (upgrade head)"
    echo "  [3] Rollback última migración"
    echo "  [4] Ver historial de migraciones"
    echo "  [0] Volver"
    echo ""
    
    read -p "Selecciona opción: " mig_option
    
    case $mig_option in
        1)
            log_info "Migraciones pendientes:"
            ssh "$AWS_HOST" "cd $AWS_PROJECT_PATH && docker compose exec app alembic current"
            ;;
        2)
            log_warning "Ejecutando migraciones..."
            ssh "$AWS_HOST" "cd $AWS_PROJECT_PATH && docker compose exec app alembic upgrade head"
            log_success "Migraciones ejecutadas"
            ;;
        3)
            log_warning "⚠️  Haciendo rollback de última migración"
            ssh "$AWS_HOST" "cd $AWS_PROJECT_PATH && docker compose exec app alembic downgrade -1"
            log_success "Rollback completado"
            ;;
        4)
            log_info "Historial de migraciones:"
            ssh "$AWS_HOST" "cd $AWS_PROJECT_PATH && docker compose exec app alembic history"
            ;;
        0)
            return
            ;;
        *)
            log_error "Opción inválida"
            ;;
    esac
    
    echo ""
    read -p "Presiona Enter para continuar..."
}

remote_cleanup() {
    echo ""
    log_warning "⚠️  Esto limpiará recursos Docker no usados"
    read -p "¿Continuar? [y/N]: " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Operación cancelada"
        return
    fi
    
    log_step "Limpiando recursos..."
    
    ssh "$AWS_HOST" "docker system prune -f"
    ssh "$AWS_HOST" "docker image prune -a -f"
    ssh "$AWS_HOST" "docker volume prune -f"
    
    log_success "Limpieza completada"
    
    echo ""
    log_info "Espacio liberado:"
    ssh "$AWS_HOST" "df -h | grep -E '(Filesystem|/$)'"
    
    echo ""
    read -p "Presiona Enter para continuar..."
}

remote_backup() {
    log_step "Creando backup de base de datos..."
    
    local backup_name="backup_$(date +%Y%m%d_%H%M%S).sql"
    
    ssh "$AWS_HOST" "cd $AWS_PROJECT_PATH && docker compose exec -T postgres pg_dump -U postgres paqueteria > /tmp/$backup_name"
    
    log_success "Backup creado: $backup_name"
    
    read -p "¿Descargar backup localmente? [y/N]: " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mkdir -p backups
        scp "$AWS_HOST:/tmp/$backup_name" "backups/$backup_name"
        log_success "Backup descargado a: backups/$backup_name"
    fi
    
    echo ""
    read -p "Presiona Enter para continuar..."
}


# ========================================
# FUNCIONES DE HISTORIAL
# ========================================
show_deploy_history() {
    log_step "Historial de deploys..."
    echo ""
    
    if [ ! -f "$DEPLOY_HISTORY_FILE" ]; then
        log_warning "No hay historial de deploys"
        return
    fi
    
    print_separator
    printf "%-20s %-10s %-40s %-10s\n" "FECHA" "TIPO" "DESCRIPCIÓN" "USUARIO"
    print_separator
    
    tail -10 "$DEPLOY_HISTORY_FILE" | while IFS='|' read -r date type desc user; do
        printf "%-20s %-10s %-40s %-10s\n" "$date" "$type" "${desc:0:40}" "$user"
    done
    
    print_separator
    echo ""
    read -p "Presiona Enter para continuar..."
}

# ========================================
# MENÚ PRINCIPAL
# ========================================
show_main_menu() {
    print_banner
    
    # Mostrar estado rápido
    if check_git_status; then
        echo -e "${YELLOW}⚠️  Hay cambios locales sin commitear${NC}"
    else
        echo -e "${GREEN}✓ Repositorio limpio${NC}"
    fi
    
    echo ""
    print_separator
    echo -e "${WHITE}SELECCIONA UNA OPCIÓN:${NC}"
    print_separator
    echo ""
    echo -e "  ${CYAN}[1]${NC}  🚀 Deploy Completo (commit + push + deploy)"
    echo -e "  ${CYAN}[2]${NC}  📤 Solo Commit y Push a GitHub"
    echo -e "  ${CYAN}[3]${NC}  📥 Solo Deploy a AWS (sin commit)"
    echo -e "  ${CYAN}[4]${NC}  🔄 Restart Servidor Remoto"
    echo -e "  ${CYAN}[5]${NC}  📊 Ver Estado del Servidor"
    echo -e "  ${CYAN}[6]${NC}  📋 Ver Logs Remotos"
    echo -e "  ${CYAN}[7]${NC}  🔨 Rebuild Contenedores Remotos"
    echo -e "  ${CYAN}[8]${NC}  🗄️  Ejecutar Migraciones Remotas"
    echo -e "  ${CYAN}[9]${NC}  ⏮️  Rollback (volver a commit anterior)"
    echo -e "  ${CYAN}[10]${NC} 🧹 Limpiar Recursos Docker Remotos"
    echo -e "  ${CYAN}[11]${NC} 💾 Backup Base de Datos Remota"
    echo -e "  ${CYAN}[12]${NC} 🔍 Health Check Completo"
    echo -e "  ${CYAN}[13]${NC} 📜 Ver Historial de Deploys"
    echo ""
    print_separator
    echo -e "  ${CYAN}[20]${NC} 📝 Gestionar Cambios Locales"
    echo -e "  ${CYAN}[0]${NC}  ❌ Salir"
    echo ""
    print_separator
    echo ""
}

manage_local_changes() {
    print_banner
    echo -e "${WHITE}GESTIÓN DE CAMBIOS LOCALES${NC}"
    echo ""
    
    show_git_status
    
    echo ""
    echo "  [1] Commitear todos los cambios"
    echo "  [2] Ver diff de cambios"
    echo "  [3] Hacer stash de cambios"
    echo "  [4] Descartar cambios (reset --hard)"
    echo "  [0] Volver"
    echo ""
    
    read -p "Selecciona opción: " local_option
    
    case $local_option in
        1)
            git_commit_and_push ""
            ;;
        2)
            git_show_diff
            ;;
        3)
            git_stash_changes
            ;;
        4)
            git_reset_changes
            ;;
        0)
            return
            ;;
        *)
            log_error "Opción inválida"
            ;;
    esac
    
    echo ""
    read -p "Presiona Enter para continuar..."
}


# ========================================
# FUNCIÓN PRINCIPAL
# ========================================
main() {
    # Verificar requisitos
    if ! check_requirements; then
        exit 1
    fi
    
    # Modo interactivo
    while true; do
        show_main_menu
        
        read -p "Opción: " option
        echo ""
        
        case $option in
            1)
                # Deploy completo
                log_step "Iniciando deploy completo..."
                echo ""
                
                if check_git_status; then
                    show_git_status
                    echo ""
                    
                    if git_commit_and_push ""; then
                        echo ""
                        if check_ssh_connection; then
                            remote_deploy
                        fi
                    fi
                else
                    log_info "No hay cambios locales"
                    read -p "¿Hacer deploy de todas formas? [y/N]: " -n 1 -r
                    echo ""
                    if [[ $REPLY =~ ^[Yy]$ ]]; then
                        if check_ssh_connection; then
                            remote_deploy
                        fi
                    fi
                fi
                
                echo ""
                read -p "Presiona Enter para continuar..."
                ;;
                
            2)
                # Solo commit y push
                if check_git_status; then
                    show_git_status
                    echo ""
                    git_commit_and_push ""
                else
                    log_warning "No hay cambios para commitear"
                fi
                
                echo ""
                read -p "Presiona Enter para continuar..."
                ;;
                
            3)
                # Solo deploy
                if check_ssh_connection; then
                    remote_deploy
                fi
                
                echo ""
                read -p "Presiona Enter para continuar..."
                ;;
                
            4)
                # Restart
                if check_ssh_connection; then
                    remote_restart
                fi
                
                echo ""
                read -p "Presiona Enter para continuar..."
                ;;
                
            5)
                # Estado
                if check_ssh_connection; then
                    remote_status
                fi
                
                echo ""
                read -p "Presiona Enter para continuar..."
                ;;
                
            6)
                # Logs
                if check_ssh_connection; then
                    remote_logs
                fi
                ;;
                
            7)
                # Rebuild
                if check_ssh_connection; then
                    remote_rebuild
                fi
                ;;
                
            8)
                # Migraciones
                if check_ssh_connection; then
                    remote_migrations
                fi
                ;;
                
            9)
                # Rollback
                git_rollback
                
                echo ""
                read -p "¿Hacer deploy del rollback? [y/N]: " -n 1 -r
                echo ""
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    if check_ssh_connection; then
                        remote_deploy
                    fi
                fi
                
                echo ""
                read -p "Presiona Enter para continuar..."
                ;;
                
            10)
                # Cleanup
                if check_ssh_connection; then
                    remote_cleanup
                fi
                ;;
                
            11)
                # Backup
                if check_ssh_connection; then
                    remote_backup
                fi
                ;;
                
            12)
                # Health check
                if check_ssh_connection; then
                    remote_health_check
                fi
                ;;
                
            13)
                # Historial
                show_deploy_history
                ;;
                
            20)
                # Gestionar cambios locales
                manage_local_changes
                ;;
                
            0)
                # Salir
                echo ""
                log_success "¡Hasta luego! 👋"
                echo ""
                exit 0
                ;;
                
            *)
                log_error "Opción inválida"
                sleep 2
                ;;
        esac
    done
}

# ========================================
# MANEJO DE ARGUMENTOS
# ========================================
if [ $# -gt 0 ]; then
    case "$1" in
        --help|-h)
            print_banner
            echo "Uso: $0 [opciones]"
            echo ""
            echo "Opciones:"
            echo "  --help, -h          Mostrar esta ayuda"
            echo "  --version, -v       Mostrar versión"
            echo "  --deploy            Deploy completo (no interactivo)"
            echo "  --commit \"msg\"      Solo commit y push"
            echo "  --restart           Restart remoto"
            echo "  --status            Ver estado"
            echo "  --logs              Ver logs"
            echo "  --health            Health check"
            echo ""
            echo "Sin argumentos: Modo interactivo"
            echo ""
            exit 0
            ;;
        --version|-v)
            echo "DEPLOY_PAPYRUS v$SCRIPT_VERSION"
            exit 0
            ;;
        --deploy)
            check_requirements || exit 1
            check_ssh_connection || exit 1
            if check_git_status; then
                git_commit_and_push "automated deploy $(date +%Y%m%d_%H%M%S)"
            fi
            remote_deploy
            exit $?
            ;;
        --commit)
            check_requirements || exit 1
            git_commit_and_push "$2"
            exit $?
            ;;
        --restart)
            check_requirements || exit 1
            check_ssh_connection || exit 1
            remote_restart
            exit $?
            ;;
        --status)
            check_requirements || exit 1
            check_ssh_connection || exit 1
            remote_status
            exit $?
            ;;
        --logs)
            check_requirements || exit 1
            check_ssh_connection || exit 1
            ssh "$AWS_HOST" "cd $AWS_PROJECT_PATH && docker compose logs -f"
            exit $?
            ;;
        --health)
            check_requirements || exit 1
            check_ssh_connection || exit 1
            remote_health_check
            exit $?
            ;;
        *)
            log_error "Opción desconocida: $1"
            echo "Usa --help para ver opciones disponibles"
            exit 1
            ;;
    esac
else
    # Modo interactivo
    main
fi
