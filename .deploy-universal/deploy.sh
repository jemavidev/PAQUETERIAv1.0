#!/bin/bash
# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                    DEPLOY MANAGER UNIVERSAL v3.0                           ║
# ║                      Configuration-Driven Deploy System                    ║
# ╚════════════════════════════════════════════════════════════════════════════╝
#
# Universal deployment system that works with any project.
# All project-specific data is in .deploy-config.yml
#
# USAGE:
#   ./deploy.sh                              # Interactive mode
#   ./deploy.sh deploy localhost             # Deploy to localhost
#   ./deploy.sh deploy staging               # Deploy to staging
#   ./deploy.sh deploy production            # Deploy to production
#   ./deploy.sh --help                       # Show help
#
# ════════════════════════════════════════════════════════════════════════════

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Load libraries
source "$SCRIPT_DIR/lib/colors.sh"
source "$SCRIPT_DIR/lib/config-parser.sh"
source "$SCRIPT_DIR/lib/ssh.sh"
source "$SCRIPT_DIR/lib/docker.sh"
source "$SCRIPT_DIR/lib/git.sh"
source "$SCRIPT_DIR/lib/health.sh"
source "$SCRIPT_DIR/lib/backup.sh"
source "$SCRIPT_DIR/lib/migrations.sh"
source "$SCRIPT_DIR/lib/rollback.sh"
source "$SCRIPT_DIR/lib/hooks.sh"

# Global variables
CONFIG_FILE="${PROJECT_ROOT}/.deploy-config.yml"
DRY_RUN=false
VERBOSE=false
NON_INTERACTIVE=false
CURRENT_ENV=""

# ════════════════════════════════════════════════════════════════════════════
# MAIN FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════

# Full deploy process
deploy_full() {
    local start_time=$(date +%s)
    local checkpoint_id=""
    
    print_banner
    log_step "Starting full deploy to: $ENV_NAME"
    echo ""
    
    # Validate dependencies
    check_dependencies || return 1
    
    # Create checkpoint for rollback
    if [ "$ROLLBACK_ENABLED" = "true" ]; then
        checkpoint_id=$(create_checkpoint)
    fi
    
    # Execute deploy steps
    if ! execute_deploy_steps; then
        log_error "Deploy failed!"
        
        # Rollback if enabled
        if [ "$ROLLBACK_ENABLED" = "true" ] && [ -n "$checkpoint_id" ]; then
            log_warning "Initiating automatic rollback..."
            rollback_to_checkpoint "$checkpoint_id"
        fi
        
        return 1
    fi
    
    # Clean old checkpoints
    if [ "$ROLLBACK_ENABLED" = "true" ]; then
        clean_old_checkpoints
    fi
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    echo ""
    log_success "Deploy completed successfully in ${duration}s"
    
    return 0
}

# Execute deploy steps
execute_deploy_steps() {
    # Step 1: Pre-deploy hook
    echo -e "${CYAN}[1/7]${NC} Pre-deploy Hook"
    execute_pre_deploy_hook || return 1
    
    # Step 2: Git operations
    echo -e "${CYAN}[2/7]${NC} Git Operations"
    if [ "$GIT_ENABLED" = "true" ]; then
        if [ "$ENV_TYPE" = "local" ]; then
            if git_check_status; then
                git_show_status
                if [ "$GIT_AUTO_COMMIT" = "true" ]; then
                    git_commit_and_push "auto deploy $(date +%Y%m%d_%H%M%S)"
                fi
            fi
        else
            git_pull || return 1
        fi
    fi
    
    # Step 3: Copy env file (remote only)
    if [ "$ENV_TYPE" = "remote" ] && [ -n "$ENV_FILE" ]; then
        echo -e "${CYAN}[3/7]${NC} Environment File"
        if [ -f "$PROJECT_ROOT/$ENV_FILE" ]; then
            remote_copy "$PROJECT_ROOT/$ENV_FILE" "$PROJECT_PATH/$ENV_FILE"
        else
            log_warning "Env file not found: $ENV_FILE"
        fi
    fi
    
    # Step 4: Backup
    echo -e "${CYAN}[4/7]${NC} Backup"
    if [ "$BACKUP_AUTO_BEFORE_DEPLOY" = "true" ]; then
        create_backup || log_warning "Backup failed (non-critical)"
    fi
    
    # Step 5: Docker operations
    echo -e "${CYAN}[5/7]${NC} Docker Operations"
    if [ "$DOCKER_ENABLED" = "true" ]; then
        if [ "$DOCKER_REBUILD" = "true" ]; then
            docker_operation "rebuild" || return 1
        fi
        docker_operation "up" || return 1
    fi
    
    # Step 6: Migrations
    echo -e "${CYAN}[6/7]${NC} Database Migrations"
    run_migrations || return 1
    
    # Step 7: Health check
    echo -e "${CYAN}[7/7]${NC} Health Check"
    health_check || log_warning "Health check failed (non-critical)"
    
    # Post-deploy hook
    execute_post_deploy_hook
    
    return 0
}

# Check dependencies
check_dependencies() {
    log_step "Checking dependencies..."
    
    local missing=()
    
    # Check required commands
    if [ "$ENV_TYPE" = "remote" ]; then
        command -v ssh >/dev/null || missing+=("ssh")
        command -v scp >/dev/null || missing+=("scp")
    fi
    
    if [ "$DOCKER_ENABLED" = "true" ]; then
        check_docker || return 1
    fi
    
    if [ "$GIT_ENABLED" = "true" ]; then
        check_git || return 1
    fi
    
    if [ "$HEALTH_CHECK_ENABLED" = "true" ]; then
        command -v curl >/dev/null || missing+=("curl")
    fi
    
    if [ ${#missing[@]} -gt 0 ]; then
        log_error "Missing dependencies: ${missing[*]}"
        return 1
    fi
    
    # Test SSH connection for remote
    if [ "$ENV_TYPE" = "remote" ]; then
        test_ssh_connection || return 1
    fi
    
    log_success "All dependencies OK"
    return 0
}

# Interactive menu
show_main_menu() {
    while true; do
        print_banner
        
        if [ -n "$CURRENT_ENV" ]; then
            echo -e "Current Environment: ${GREEN}$ENV_NAME${NC}"
            echo -e "Type: ${CYAN}$ENV_TYPE${NC}"
        else
            echo -e "${YELLOW}No environment selected${NC}"
        fi
        
        echo ""
        print_double_separator
        echo -e "${WHITE}OPERATIONS:${NC}"
        print_separator
        echo ""
        echo -e "  ${CYAN}[1]${NC}  🚀 Deploy Full"
        echo -e "  ${CYAN}[2]${NC}  📥 Git Pull"
        echo -e "  ${CYAN}[3]${NC}  🔄 Restart Services"
        echo -e "  ${CYAN}[4]${NC}  📊 Show Status"
        echo -e "  ${CYAN}[5]${NC}  📋 Show Logs"
        echo -e "  ${CYAN}[6]${NC}  🔍 Health Check"
        echo -e "  ${CYAN}[7]${NC}  💾 Create Backup"
        echo -e "  ${CYAN}[8]${NC}  🔨 Rebuild Containers"
        echo -e "  ${CYAN}[9]${NC}  ⚙️  Run Migrations"
        echo -e "  ${CYAN}[R]${NC}  ↩️  Rollback"
        echo ""
        print_separator
        echo -e "  ${CYAN}[E]${NC}  🌍 Change Environment"
        echo -e "  ${CYAN}[C]${NC}  📋 Show Configuration"
        echo -e "  ${CYAN}[0]${NC}  ❌ Exit"
        echo ""
        print_separator
        echo ""
        
        read -p "Select option: " option
        echo ""
        
        case $option in
            1) deploy_full; read -p "Press Enter to continue..." ;;
            2) git_pull; read -p "Press Enter to continue..." ;;
            3) docker_operation "restart"; health_check; read -p "Press Enter to continue..." ;;
            4) docker_operation "status"; read -p "Press Enter to continue..." ;;
            5) docker_operation "logs"; read -p "Press Enter to continue..." ;;
            6) health_check; read -p "Press Enter to continue..." ;;
            7) create_backup; read -p "Press Enter to continue..." ;;
            8) docker_operation "rebuild"; docker_operation "up"; read -p "Press Enter to continue..." ;;
            9) run_migrations; read -p "Press Enter to continue..." ;;
            R|r) list_checkpoints; read -p "Checkpoint ID: " cp_id; rollback_to_checkpoint "$cp_id"; read -p "Press Enter..." ;;
            E|e) select_environment ;;
            C|c) show_config; read -p "Press Enter to continue..." ;;
            0) log_success "Goodbye! 👋"; exit 0 ;;
            *) log_error "Invalid option"; sleep 1 ;;
        esac
    done
}

# Environment selector
select_environment() {
    print_banner
    echo -e "${WHITE}SELECT ENVIRONMENT${NC}"
    print_separator
    echo ""
    echo -e "  ${CYAN}[1]${NC} localhost"
    echo -e "  ${CYAN}[2]${NC} staging"
    echo -e "  ${CYAN}[3]${NC} production"
    echo ""
    print_separator
    read -p "Select environment [1-3]: " choice
    
    case $choice in
        1) load_environment "localhost" ;;
        2) load_environment "staging" ;;
        3) load_environment "production" ;;
        *) log_error "Invalid option"; return 1 ;;
    esac
}

# Load environment
load_environment() {
    local env="$1"
    
    log_step "Loading environment: $env"
    
    # Load configuration
    load_config "$CONFIG_FILE" "$env" || return 1
    
    # Validate configuration
    validate_config "$env" || return 1
    
    CURRENT_ENV="$env"
    log_success "Environment loaded: $env"
}

# Show help
show_help() {
    print_banner
    echo "Usage: $0 [command] [environment] [options]"
    echo ""
    echo "Commands:"
    echo "  deploy <env>        Full deployment"
    echo "  pull <env>          Git pull only"
    echo "  restart <env>       Restart services"
    echo "  status <env>        Show status"
    echo "  logs <env>          Show logs"
    echo "  health <env>        Health check"
    echo "  backup <env>        Create backup"
    echo "  rollback <env>      Rollback to checkpoint"
    echo ""
    echo "Environments:"
    echo "  localhost           Local development"
    echo "  staging             Staging server"
    echo "  production          Production server"
    echo ""
    echo "Options:"
    echo "  --config <file>     Custom config file"
    echo "  --non-interactive   No prompts (for CI/CD)"
    echo "  --dry-run           Show what would be done"
    echo "  --verbose           Verbose output"
    echo "  --help              Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 deploy localhost"
    echo "  $0 deploy production --non-interactive"
    echo "  $0 status staging"
    echo "  $0 logs production"
    echo ""
}

# ════════════════════════════════════════════════════════════════════════════
# COMMAND LINE INTERFACE
# ════════════════════════════════════════════════════════════════════════════

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --non-interactive)
            NON_INTERACTIVE=true
            shift
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
        deploy|pull|restart|status|logs|health|backup|rollback)
            COMMAND="$1"
            ENVIRONMENT="$2"
            shift 2
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Execute command or show interactive menu
if [ -n "$COMMAND" ]; then
    # CLI mode
    if [ -z "$ENVIRONMENT" ]; then
        log_error "Environment is required"
        show_help
        exit 1
    fi
    
    load_environment "$ENVIRONMENT" || exit 1
    
    case $COMMAND in
        deploy) deploy_full ;;
        pull) git_pull ;;
        restart) docker_operation "restart"; health_check ;;
        status) docker_operation "status" ;;
        logs) docker_operation "logs" ;;
        health) health_check ;;
        backup) create_backup ;;
        rollback) list_checkpoints; read -p "Checkpoint ID: " cp_id; rollback_to_checkpoint "$cp_id" ;;
    esac
else
    # Interactive mode
    if [ ! -f "$CONFIG_FILE" ]; then
        log_error "Configuration file not found: $CONFIG_FILE"
        log_info "Create one from template:"
        log_info "  cp $SCRIPT_DIR/templates/deploy-config.yml.example .deploy-config.yml"
        exit 1
    fi
    
    select_environment
    show_main_menu
fi
