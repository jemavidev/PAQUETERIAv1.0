#!/bin/bash
# PAQUETERÍA v1.0 - Rollback a tag/commit previo
# Uso: ./DOCS/scripts/deployment/rollback.sh <tag|commit>

set -euo pipefail

if [ "${1:-}" = "" ]; then
  echo "Uso: $0 <tag|commit>" >&2
  exit 1
fi

TARGET="$1"
COMPOSE_FILE="docker-compose.prod.yml"

info() { echo -e "\033[0;34m[INFO]\033[0m $1"; }
success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }

if [ ! -f "$COMPOSE_FILE" ]; then
  error "No se encontró $COMPOSE_FILE en $(pwd)"
  exit 1
fi

if [ ! -f ".env" ]; then
  error "Falta .env (producción). Colócalo en la raíz del proyecto."
  exit 1
fi

info "Obteniendo tags/commits..."

git fetch --all --tags

git checkout "$TARGET"

git reset --hard "$TARGET"

info "Aplicando rollback con Docker Compose..."

docker compose -f "$COMPOSE_FILE" build

docker compose -f "$COMPOSE_FILE" up -d

success "Rollback completado a $TARGET"