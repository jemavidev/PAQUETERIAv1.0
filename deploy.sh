#!/bin/bash
# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                    DEPLOY MANAGER UNIVERSAL                                ║
# ║                         PAQUETEX v4.0                                      ║
# ╚════════════════════════════════════════════════════════════════════════════╝
#
# Sistema unificado de deploy multi-entorno
# Versión: 2.0.0
# Fecha: 2024-11-22
#
# USO:
#   ./deploy.sh                          # Modo interactivo
#   ./deploy.sh --env localhost --deploy # Deploy en localhost
#   ./deploy.sh --env papyrus --deploy   # Deploy en papyrus
#   ./deploy.sh --help                   # Ver ayuda
#
# ════════════════════════════════════════════════════════════════════════════

set -e

# Directorio base del sistema de deploy
DEPLOY_DIR=".deploy"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Verificar que existe el directorio .deploy
if [ ! -d "$PROJECT_ROOT/$DEPLOY_DIR" ]; then
    echo "❌ Error: Directorio $DEPLOY_DIR no encontrado"
    echo "Asegúrate de estar en el directorio raíz del proyecto"
    exit 1
fi

# Cargar configuración global
if [ ! -f "$PROJECT_ROOT/$DEPLOY_DIR/config/deploy.conf" ]; then
    echo "❌ Error: Archivo de configuración no encontrado"
    echo "Esperado: $PROJECT_ROOT/$DEPLOY_DIR/config/deploy.conf"
    exit 1
fi

source "$PROJECT_ROOT/$DEPLOY_DIR/config/deploy.conf"

# Cargar librerías
source "$PROJECT_ROOT/$DEPLOY_DIR/lib/colors.sh"
source "$PROJECT_ROOT/$DEPLOY_DIR/lib/git.sh"

# Variables globales
CURRENT_ENV=""
ENV_CONFIG=""
DRY_RUN=false
VERBOSE=false

# ════════════════════════════════════════════════════════════════════════════
# FUNCIONES PRINCIPALES
# ════════════════════════════════════════════════════════════════════════════

load_environment() {
    local env_name="$1"
    local config_file="$PROJECT_ROOT/$DEPLOY_DIR/config/${env_name}.conf"
    
    if [ ! -f "$config_file" ]; then
        log_error "Configuración no encontrada: $config_file"
        return 1
    fi
    
    source "$config_file"
    CURRENT_ENV="$env_name"
    ENV_CONFIG="$config_file"
    
    log_debug "Entorno cargado: $env_name"
    return 0
}

show_environment_selector() {
    print_banner
    echo -e "${WHITE}SELECCIONAR ENTORNO${NC}"
    print_separator
    echo ""
    
    local i=1
    for env in "${ENVIRONMENTS[@]}"; do
        if load_environment "$env" 2>/dev/null; then
            local color_var="${ENV_COLOR:-blue}"
            case $color_var in
                green) color=$GREEN ;;
                yellow) color=$YELLOW ;;
                red) color=$RED ;;
                cyan) color=$CYAN ;;
                *) color=$BLUE ;;
            esac
            
            echo -e "  ${color}[$i]${NC} $env - $ENV_DESCRIPTION"
            ((i++))
        fi
    done
    
    echo ""
    print_separator
    read -p "Selecciona entorno [1-${#ENVIRONMENTS[@]}]: " choice
    
    if [ "$choice" -ge 1 ] && [ "$choice" -le "${#ENVIRONMENTS[@]}" ] 2>/dev/null; then
        local selected_env="${ENVIRONMENTS[$((choice-1))]}"
        load_environment "$selected_env"
        echo "$selected_env" > "$PROJECT_ROOT/.deploy-current"
        log_success "Entorno seleccionado: $selected_env"
        return 0
    else
        log_error "Opción inválida"
        return 1
    fi
}

execute_command() {
    local cmd="$1"
    local description="$2"
    
    log_step "$description"
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] $cmd"
        return 0
    fi
    
    if [ "$ENV_TYPE" = "remote" ]; then
        ssh $SSH_OPTIONS "$SSH_USER@$SSH_HOST" "cd $PROJECT_PATH && $cmd"
    else
        cd "$PROJECT_PATH" && eval "$cmd"
    fi
}

docker_operation() {
    local operation="$1"
    local compose_file="${DOCKER_COMPOSE_FILE}"
    
    case $operation in
        up)
            execute_command "docker compose -f $compose_file up -d" "Iniciando servicios..."
            ;;
        down)
            execute_command "docker compose -f $compose_file down" "Deteniendo servicios..."
            ;;
        restart)
            execute_command "docker compose -f $compose_file restart" "Reiniciando servicios..."
            ;;
        pull)
            execute_command "docker compose -f $compose_file pull" "Descargando imágenes..."
            ;;
        rebuild)
            execute_command "docker compose -f $compose_file build --no-cache" "Reconstruyendo..."
            ;;
        logs)
            execute_command "docker compose -f $compose_file logs -f" "Mostrando logs..."
            ;;
        ps)
            execute_command "docker compose -f $compose_file ps" "Estado de servicios..."
            ;;
    esac
}

git_pull_only() {
    log_step "Ejecutando Git Pull..."
    
    if [ "$GIT_ENABLED" != true ]; then
        log_warning "Git está deshabilitado en este entorno"
        return 1
    fi
    
    execute_command "git pull origin ${GIT_BRANCH}" "Descargando cambios desde GitHub..."
    log_success "Pull completado"
}

git_pull_to_commit() {
    if [ "$GIT_ENABLED" != true ]; then
        log_warning "Git está deshabilitado en este entorno"
        read -p "Presiona Enter para continuar..."
        return 1
    fi
    
    clear
    print_banner
    echo -e "${WHITE}📜 ÚLTIMOS 15 COMMITS${NC}"
    print_separator
    echo ""
    
    # Obtener lista de commits
    if [ "$ENV_TYPE" = "remote" ]; then
        ssh $SSH_OPTIONS "$SSH_USER@$SSH_HOST" "cd $PROJECT_PATH && git log --oneline -15 --pretty=format:'%C(yellow)%h%C(reset) - %C(cyan)%ar%C(reset) - %s %C(green)(%an)%C(reset)'"
    else
        cd "$PROJECT_PATH"
        git log --oneline -15 --pretty=format:'%C(yellow)%h%C(reset) - %C(cyan)%ar%C(reset) - %s %C(green)(%an)%C(reset)'
    fi
    
    echo ""
    echo ""
    print_separator
    read -p "Ingresa el hash del commit (o Enter para cancelar): " commit_hash
    
    if [ -z "$commit_hash" ]; then
        log_info "Operación cancelada"
        return 0
    fi
    
    log_step "Haciendo checkout a commit: $commit_hash"
    execute_command "git checkout $commit_hash" "Cambiando a commit específico..."
    log_success "Checkout completado"
}

show_logs_interactive() {
    local lines=100
    
    while true; do
        clear
        print_banner
        echo -e "${WHITE}📋 LOGS DE DOCKER (Últimas $lines líneas)${NC}"
        print_separator
        echo ""
        
        # Usar execute_command para manejar tanto local como remoto
        if [ "$ENV_TYPE" = "remote" ]; then
            ssh $SSH_OPTIONS "$SSH_USER@$SSH_HOST" "cd $PROJECT_PATH && docker compose -f $DOCKER_COMPOSE_FILE logs --tail=$lines"
        else
            cd "$PROJECT_PATH"
            docker compose -f "$DOCKER_COMPOSE_FILE" logs --tail="$lines"
        fi
        
        echo ""
        print_separator
        echo -e "  ${CYAN}[M]${NC} Ver 100 líneas más"
        echo -e "  ${CYAN}[F]${NC} Seguir logs en tiempo real"
        echo -e "  ${CYAN}[Q]${NC} Volver al menú"
        echo ""
        print_separator
        read -p "Opción: " log_option
        
        case $log_option in
            M|m)
                lines=$((lines + 100))
                ;;
            F|f)
                if [ "$ENV_TYPE" = "remote" ]; then
                    ssh $SSH_OPTIONS "$SSH_USER@$SSH_HOST" "cd $PROJECT_PATH && docker compose -f $DOCKER_COMPOSE_FILE logs -f"
                else
                    cd "$PROJECT_PATH"
                    docker compose -f "$DOCKER_COMPOSE_FILE" logs -f
                fi
                lines=100
                ;;
            Q|q)
                return 0
                ;;
            *)
                log_error "Opción inválida"
                sleep 1
                ;;
        esac
    done
}

health_check() {
    if [ "$HEALTH_CHECK_ENABLED" != true ]; then
        log_info "Health check deshabilitado"
        return 0
    fi
    
    log_step "Ejecutando health check..."
    local attempts=0
    local max_attempts=${HEALTH_CHECK_RETRIES:-10}
    
    while [ $attempts -lt $max_attempts ]; do
        if [ "$ENV_TYPE" = "remote" ]; then
            if ssh $SSH_OPTIONS "$SSH_USER@$SSH_HOST" "curl -f $HEALTH_CHECK_URL" &> /dev/null; then
                log_success "Health check exitoso"
                return 0
            fi
        else
            if curl -f "$HEALTH_CHECK_URL" &> /dev/null; then
                log_success "Health check exitoso"
                return 0
            fi
        fi
        
        attempts=$((attempts + 1))
        printf "."
        sleep ${HEALTH_CHECK_INTERVAL:-2}
    done
    
    echo ""
    log_warning "Health check timeout"
    return 1
}

deploy_full() {
    local start_time=$(date +%s)
    
    print_banner
    log_step "Iniciando deploy completo en: $ENV_NAME"
    echo ""
    
    # Paso 1: Git operations
    if [ "$GIT_ENABLED" = true ]; then
        echo -e "${CYAN}[1/6]${NC} Git Operations"
        
        # Para entornos locales: commit y push
        if [ "$ENV_TYPE" = "local" ]; then
            if git_check_status; then
                git_show_status
                if [ "$GIT_AUTO_COMMIT" = true ]; then
                    git_commit_and_push "auto deploy $(date +%Y%m%d_%H%M%S)"
                else
                    read -p "¿Hacer commit y push? [y/N]: " -n 1 -r
                    echo ""
                    [[ $REPLY =~ ^[Yy]$ ]] && git_commit_and_push ""
                fi
            fi
        fi
        
        # Para entornos remotos: pull
        if [ "$ENV_TYPE" = "remote" ]; then
            execute_command "git pull origin ${GIT_BRANCH}" "Descargando cambios..."
        fi
    fi
    
    # Paso 2: Backup
    if [ "$BACKUP_AUTO_BEFORE_DEPLOY" = true ]; then
        echo -e "${CYAN}[2/6]${NC} Backup"
        create_backup
    fi
    
    # Paso 3: Docker operations
    echo -e "${CYAN}[3/6]${NC} Docker Operations"
    [ "$DOCKER_PULL_BEFORE_DEPLOY" = true ] && docker_operation "pull"
    [ "$DOCKER_REBUILD_ON_DEPLOY" = true ] && docker_operation "rebuild"
    docker_operation "up"
    
    # Paso 4: Health check
    echo -e "${CYAN}[4/6]${NC} Health Check"
    health_check
    
    # Paso 5: Migraciones
    if [ "$MIGRATIONS_ENABLED" = true ] && [ "$MIGRATIONS_AUTO" = true ]; then
        echo -e "${CYAN}[5/6]${NC} Migraciones"
        execute_command "$MIGRATIONS_COMMAND" "Ejecutando migraciones..."
    fi
    
    # Paso 6: Post-deploy hook
    echo -e "${CYAN}[6/6]${NC} Finalizando"
    if [ -n "$POST_DEPLOY_HOOK" ] && [ -f "$PROJECT_ROOT/$POST_DEPLOY_HOOK" ]; then
        bash "$PROJECT_ROOT/$POST_DEPLOY_HOOK"
    fi
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    echo ""
    log_success "Deploy completado en ${duration}s"
    
    # Guardar en historial
    echo "$(date '+%Y-%m-%d %H:%M:%S')|$ENV_NAME|deploy|success|${duration}s|$USER" >> "$PROJECT_ROOT/$HISTORY_FILE"
}

create_backup() {
    if [ "$BACKUP_ENABLED" != true ]; then
        log_info "Backup deshabilitado"
        return 0
    fi
    
    log_step "Creando backup..."
    local backup_name="backup_${ENV_NAME}_$(date +%Y%m%d_%H%M%S).sql"
    local backup_path="${BACKUP_PATH}/${backup_name}"
    
    if [ "$ENV_TYPE" = "remote" ]; then
        ssh $SSH_OPTIONS "$SSH_USER@$SSH_HOST" "mkdir -p $BACKUP_PATH"
        ssh $SSH_OPTIONS "$SSH_USER@$SSH_HOST" "cd $PROJECT_PATH && $BACKUP_DB_COMMAND > $backup_path"
    else
        mkdir -p "$BACKUP_PATH"
        cd "$PROJECT_PATH" && eval "$BACKUP_DB_COMMAND" > "$backup_path"
    fi
    
    log_success "Backup creado: $backup_name"
}

show_main_menu() {
    print_banner
    
    if [ -n "$CURRENT_ENV" ]; then
        echo -e "Entorno Actual: ${GREEN}🌍 $ENV_NAME${NC} ($ENV_DESCRIPTION)"
        echo -e "Tipo: ${CYAN}$ENV_TYPE${NC}"
    else
        echo -e "${YELLOW}⚠️  No hay entorno seleccionado${NC}"
    fi
    
    echo ""
    print_double_separator
    echo -e "${WHITE}GESTIÓN DE ENTORNOS:${NC}"
    print_separator
    echo ""
    echo -e "  ${CYAN}[E]${NC} 🌍 Cambiar Entorno"
    echo -e "  ${CYAN}[C]${NC} 📋 Ver Configuración Actual"
    echo ""
    print_separator
    echo -e "${WHITE}OPERACIONES DE DEPLOY:${NC}"
    print_separator
    echo ""
    echo -e "  ${CYAN}[1]${NC}  🚀 Deploy Completo"
    echo -e "  ${CYAN}[2]${NC}  📥 Git Pull (solo descargar)"
    echo -e "  ${CYAN}[3]${NC}  🔄 Restart Servicios"
    echo -e "  ${CYAN}[4]${NC}  📊 Ver Estado"
    echo -e "  ${CYAN}[5]${NC}  📋 Ver Logs"
    echo -e "  ${CYAN}[6]${NC}  🔨 Rebuild Contenedores"
    echo -e "  ${CYAN}[7]${NC}  🗄️  Migraciones"
    echo -e "  ${CYAN}[8]${NC}  💾 Crear Backup"
    echo -e "  ${CYAN}[9]${NC}  🔍 Health Check"
    echo -e "  ${CYAN}[P]${NC}  📜 Pull a Commit Específico"
    echo ""
    print_separator
    echo -e "  ${CYAN}[0]${NC}  ❌ Salir"
    echo ""
    print_separator
    echo ""
}

main_interactive() {
    if [ -f "$PROJECT_ROOT/.deploy-current" ]; then
        local saved_env=$(cat "$PROJECT_ROOT/.deploy-current")
        load_environment "$saved_env" 2>/dev/null || show_environment_selector
    else
        show_environment_selector
    fi
    
    while true; do
        show_main_menu
        read -p "Opción: " option
        echo ""
        
        case $option in
            E|e) show_environment_selector ;;
            C|c)
                clear
                print_banner
                echo -e "${WHITE}📋 CONFIGURACIÓN DEL ENTORNO${NC}"
                print_double_separator
                echo ""
                echo -e "${GREEN}🌍 Entorno:${NC} $ENV_NAME"
                echo -e "${CYAN}📝 Descripción:${NC} $ENV_DESCRIPTION"
                echo -e "${YELLOW}🔧 Tipo:${NC} $ENV_TYPE"
                echo ""
                print_separator
                echo -e "${WHITE}CONFIGURACIÓN GENERAL:${NC}"
                print_separator
                echo ""
                
                # Información del proyecto
                [ -n "$PROJECT_PATH" ] && echo -e "  ${CYAN}📁 Ruta del Proyecto:${NC} $PROJECT_PATH"
                [ -n "$DOCKER_COMPOSE_FILE" ] && echo -e "  ${CYAN}🐳 Docker Compose:${NC} $DOCKER_COMPOSE_FILE"
                
                echo ""
                print_separator
                echo -e "${WHITE}GIT:${NC}"
                print_separator
                echo ""
                [ -n "$GIT_ENABLED" ] && echo -e "  ${CYAN}✓ Habilitado:${NC} $GIT_ENABLED"
                [ -n "$GIT_BRANCH" ] && echo -e "  ${CYAN}🌿 Branch:${NC} $GIT_BRANCH"
                [ -n "$GIT_AUTO_COMMIT" ] && echo -e "  ${CYAN}🤖 Auto Commit:${NC} $GIT_AUTO_COMMIT"
                
                echo ""
                print_separator
                echo -e "${WHITE}DOCKER:${NC}"
                print_separator
                echo ""
                [ -n "$DOCKER_PULL_BEFORE_DEPLOY" ] && echo -e "  ${CYAN}⬇️  Pull antes de Deploy:${NC} $DOCKER_PULL_BEFORE_DEPLOY"
                [ -n "$DOCKER_REBUILD_ON_DEPLOY" ] && echo -e "  ${CYAN}🔨 Rebuild en Deploy:${NC} $DOCKER_REBUILD_ON_DEPLOY"
                
                echo ""
                print_separator
                echo -e "${WHITE}HEALTH CHECK:${NC}"
                print_separator
                echo ""
                [ -n "$HEALTH_CHECK_ENABLED" ] && echo -e "  ${CYAN}✓ Habilitado:${NC} $HEALTH_CHECK_ENABLED"
                [ -n "$HEALTH_CHECK_URL" ] && echo -e "  ${CYAN}🔗 URL:${NC} $HEALTH_CHECK_URL"
                [ -n "$HEALTH_CHECK_RETRIES" ] && echo -e "  ${CYAN}🔄 Reintentos:${NC} $HEALTH_CHECK_RETRIES"
                [ -n "$HEALTH_CHECK_INTERVAL" ] && echo -e "  ${CYAN}⏱️  Intervalo:${NC} ${HEALTH_CHECK_INTERVAL}s"
                
                echo ""
                print_separator
                echo -e "${WHITE}MIGRACIONES:${NC}"
                print_separator
                echo ""
                [ -n "$MIGRATIONS_ENABLED" ] && echo -e "  ${CYAN}✓ Habilitado:${NC} $MIGRATIONS_ENABLED"
                [ -n "$MIGRATIONS_AUTO" ] && echo -e "  ${CYAN}🤖 Automáticas:${NC} $MIGRATIONS_AUTO"
                [ -n "$MIGRATIONS_COMMAND" ] && echo -e "  ${CYAN}⚙️  Comando:${NC} $MIGRATIONS_COMMAND"
                
                echo ""
                print_separator
                echo -e "${WHITE}BACKUP:${NC}"
                print_separator
                echo ""
                [ -n "$BACKUP_ENABLED" ] && echo -e "  ${CYAN}✓ Habilitado:${NC} $BACKUP_ENABLED"
                [ -n "$BACKUP_AUTO_BEFORE_DEPLOY" ] && echo -e "  ${CYAN}🤖 Auto antes de Deploy:${NC} $BACKUP_AUTO_BEFORE_DEPLOY"
                [ -n "$BACKUP_PATH" ] && echo -e "  ${CYAN}📁 Ruta:${NC} $BACKUP_PATH"
                
                # SSH (solo para entornos remotos)
                if [ "$ENV_TYPE" = "remote" ]; then
                    echo ""
                    print_separator
                    echo -e "${WHITE}SSH (REMOTO):${NC}"
                    print_separator
                    echo ""
                    [ -n "$SSH_HOST" ] && echo -e "  ${CYAN}🖥️  Host:${NC} $SSH_HOST"
                    [ -n "$SSH_USER" ] && echo -e "  ${CYAN}👤 Usuario:${NC} $SSH_USER"
                    [ -n "$SSH_PORT" ] && echo -e "  ${CYAN}🔌 Puerto:${NC} $SSH_PORT"
                fi
                
                echo ""
                print_double_separator
                echo ""
                read -p "Presiona Enter para continuar..."
                ;;
            1) deploy_full; read -p "Presiona Enter para continuar..." ;;
            2) git_pull_only; read -p "Presiona Enter para continuar..." ;;
            3) docker_operation "restart"; health_check; read -p "Presiona Enter para continuar..." ;;
            4) docker_operation "ps"; read -p "Presiona Enter para continuar..." ;;
            5) show_logs_interactive ;;
            6) docker_operation "rebuild"; docker_operation "up"; health_check; read -p "Presiona Enter para continuar..." ;;
            7) execute_command "$MIGRATIONS_COMMAND" "Ejecutando migraciones..."; read -p "Presiona Enter para continuar..." ;;
            8) create_backup; read -p "Presiona Enter para continuar..." ;;
            9) health_check; read -p "Presiona Enter para continuar..." ;;
            P|p) git_pull_to_commit; read -p "Presiona Enter para continuar..." ;;
            0) log_success "¡Hasta luego! 👋"; exit 0 ;;
            *) log_error "Opción inválida"; sleep 2 ;;
        esac
    done
}

show_help() {
    print_banner
    echo "Uso: $0 [opciones]"
    echo ""
    echo "Opciones:"
    echo "  --env <nombre>          Seleccionar entorno"
    echo "  --list-envs             Listar entornos disponibles"
    echo "  --deploy                Deploy completo"
    echo "  --pull                  Git pull solamente"
    echo "  --pull-commit <hash>    Pull a commit específico"
    echo "  --restart               Restart servicios"
    echo "  --status                Ver estado"
    echo "  --logs                  Ver logs"
    echo "  --health                Health check"
    echo "  --backup                Crear backup"
    echo "  --migrations            Ejecutar migraciones"
    echo "  --dry-run               Modo simulación"
    echo "  --verbose               Modo verbose"
    echo "  --help                  Mostrar ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 --env localhost --deploy"
    echo "  $0 --env papyrus --restart"
    echo "  $0 --list-envs"
    echo ""
    echo "Documentación:"
    echo "  README: cat .deploy/docs/README.md"
    echo "  Quickstart: cat .deploy/docs/QUICKSTART.md"
    echo "  Ejemplos: cat .deploy/docs/EXAMPLES.md"
    echo ""
}

# ════════════════════════════════════════════════════════════════════════════
# MANEJO DE ARGUMENTOS CLI
# ════════════════════════════════════════════════════════════════════════════

if [ $# -eq 0 ]; then
    main_interactive
    exit 0
fi

while [ $# -gt 0 ]; do
    case "$1" in
        --env)
            load_environment "$2" || exit 1
            shift 2
            ;;
        --list-envs)
            echo "Entornos disponibles:"
            for env in "${ENVIRONMENTS[@]}"; do
                echo "  - $env"
            done
            exit 0
            ;;
        --deploy)
            [ -z "$CURRENT_ENV" ] && load_environment "$DEFAULT_ENVIRONMENT"
            deploy_full
            exit $?
            ;;
        --pull)
            [ -z "$CURRENT_ENV" ] && load_environment "$DEFAULT_ENVIRONMENT"
            git_pull_only
            exit $?
            ;;
        --pull-commit)
            [ -z "$CURRENT_ENV" ] && load_environment "$DEFAULT_ENVIRONMENT"
            execute_command "git checkout $2" "Cambiando a commit $2..."
            exit $?
            ;;
        --restart)
            [ -z "$CURRENT_ENV" ] && load_environment "$DEFAULT_ENVIRONMENT"
            docker_operation "restart"
            exit $?
            ;;
        --status)
            [ -z "$CURRENT_ENV" ] && load_environment "$DEFAULT_ENVIRONMENT"
            docker_operation "ps"
            exit $?
            ;;
        --logs)
            [ -z "$CURRENT_ENV" ] && load_environment "$DEFAULT_ENVIRONMENT"
            docker_operation "logs"
            exit $?
            ;;
        --health)
            [ -z "$CURRENT_ENV" ] && load_environment "$DEFAULT_ENVIRONMENT"
            health_check
            exit $?
            ;;
        --backup)
            [ -z "$CURRENT_ENV" ] && load_environment "$DEFAULT_ENVIRONMENT"
            create_backup
            exit $?
            ;;
        --migrations)
            [ -z "$CURRENT_ENV" ] && load_environment "$DEFAULT_ENVIRONMENT"
            execute_command "$MIGRATIONS_COMMAND" "Ejecutando migraciones..."
            exit $?
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            log_error "Opción desconocida: $1"
            show_help
            exit 1
            ;;
    esac
done
