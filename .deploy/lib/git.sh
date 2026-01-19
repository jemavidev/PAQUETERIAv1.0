#!/bin/bash
# ════════════════════════════════════════════════════════════════════════════
# FUNCIONES DE GIT
# ════════════════════════════════════════════════════════════════════════════

git_check_status() {
    if [ "$ENV_TYPE" = "remote" ]; then
        local changes=$(ssh $SSH_OPTIONS "$SSH_USER@$SSH_HOST" "cd $PROJECT_PATH && git status --porcelain" | wc -l)
    else
        local changes=$(cd "$PROJECT_PATH" && git status --porcelain | wc -l)
    fi
    
    [ "$changes" -gt 0 ]
}

git_show_status() {
    log_step "Estado de Git:"
    echo ""
    
    if [ "$ENV_TYPE" = "remote" ]; then
        ssh $SSH_OPTIONS "$SSH_USER@$SSH_HOST" "cd $PROJECT_PATH && git status --short"
    else
        cd "$PROJECT_PATH" && git status --short
    fi
    
    echo ""
}

git_commit_and_push() {
    local message="$1"
    
    if [ -z "$message" ]; then
        read -p "Mensaje de commit: " message
    fi
    
    if [ -z "$message" ]; then
        log_error "Mensaje de commit vacío"
        return 1
    fi
    
    log_step "Haciendo commit y push..."
    
    if [ "$ENV_TYPE" = "remote" ]; then
        ssh $SSH_OPTIONS "$SSH_USER@$SSH_HOST" "cd $PROJECT_PATH && git add -A && git commit -m '$message' && git push origin ${GIT_BRANCH}"
    else
        cd "$PROJECT_PATH"
        git add -A
        git commit -m "$message"
        git push origin "${GIT_BRANCH}"
    fi
    
    if [ $? -eq 0 ]; then
        log_success "Commit y push completados"
        return 0
    else
        log_error "Error en commit/push"
        return 1
    fi
}

git_get_current_branch() {
    if [ "$ENV_TYPE" = "remote" ]; then
        ssh $SSH_OPTIONS "$SSH_USER@$SSH_HOST" "cd $PROJECT_PATH && git branch --show-current"
    else
        cd "$PROJECT_PATH" && git branch --show-current
    fi
}

git_get_last_commit() {
    if [ "$ENV_TYPE" = "remote" ]; then
        ssh $SSH_OPTIONS "$SSH_USER@$SSH_HOST" "cd $PROJECT_PATH && git log -1 --oneline"
    else
        cd "$PROJECT_PATH" && git log -1 --oneline
    fi
}
