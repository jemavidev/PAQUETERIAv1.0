#!/bin/bash
# ════════════════════════════════════════════════════════════════════════════
# COLORES Y FORMATO
# ════════════════════════════════════════════════════════════════════════════

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Funciones de logging
log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_info() {
    echo -e "${CYAN}ℹ${NC} $1"
}

log_step() {
    echo -e "${BLUE}▶${NC} $1"
}

log_debug() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${WHITE}[DEBUG]${NC} $1"
    fi
}

# Separadores
print_separator() {
    echo "────────────────────────────────────────────────────────────────────────────────"
}

print_double_separator() {
    echo "════════════════════════════════════════════════════════════════════════════════"
}

# Banner
print_banner() {
    clear
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════════════════════╗"
    echo "║                    DEPLOY MANAGER UNIVERSAL                                ║"
    echo "║                         PAQUETERIA v1.0                                    ║"
    echo "╚════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}
