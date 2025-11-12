#!/bin/bash
# PAQUETERÍA v1.0 - Dev remoto (hot reload)
# Uso: ./DOCS/scripts/deployment/dev-up.sh [branch|tag]
# Requisitos: git, docker compose, .env en raíz del proyecto

set -euo pipefail

BRANCH_OR_TAG="${1:-main}"
COMPOSE_BASE="docker-compose.prod.yml"
COMPOSE_DEV="docker-compose.dev.override.yml"

info() { echo -e "\033[0;34m[INFO]\033[0m $1"; }
success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }

if [ ! -f "$COMPOSE_BASE" ] || [ ! -f "$COMPOSE_DEV" ]; then
  error "Faltan $COMPOSE_BASE o $COMPOSE_DEV en $(pwd)"
  exit 1
fi

if [ ! -f ".env" ]; then
  error "Falta .env (producción/desarrollo). Colócalo en la raíz del proyecto."
  exit 1
fi

info "Actualizando código desde GitHub..."

git fetch --all --tags

git checkout "$BRANCH_OR_TAG"

git pull --ff-only || true

info "Levantando servicios en modo hot reload (override dev)..."

docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_DEV" up -d app celery_worker

success "Entorno hot reload activo. Edita el código o haz git pull para recargar."
