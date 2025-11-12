#!/bin/bash
# PAQUETERÍA v1.0 - Deploy desde GitHub (pull + compose up)
# Uso: ./DOCS/scripts/deployment/deploy.sh [branch|tag]
# Requisitos: git, docker, docker compose plugin, .env (producción)

set -euo pipefail

BRANCH_OR_TAG="${1:-main}"
REPO_DIR="$(pwd)"

# Detectar archivo compose disponible (prod o genérico)
if [ -f "docker-compose.prod.yml" ]; then
  COMPOSE_FILE="docker-compose.prod.yml"
elif [ -f "docker-compose.yml" ]; then
  COMPOSE_FILE="docker-compose.yml"
else
  COMPOSE_FILE="docker-compose.prod.yml"  # Default para mensaje de error
fi

info() { echo -e "\033[0;34m[INFO]\033[0m $1"; }
success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }

if [ ! -f "$COMPOSE_FILE" ]; then
  error "No se encontró $COMPOSE_FILE en $REPO_DIR"
  exit 1
fi

if [ ! -f ".env" ]; then
  error "Falta .env (producción). Colócalo en la raíz del proyecto antes del deploy."
  exit 1
fi

info "Actualizando código desde GitHub..."

git fetch --all --tags

git checkout "$BRANCH_OR_TAG"

git pull --ff-only || true

info "Construyendo e iniciando servicios (modo producción)..."

docker compose -f "$COMPOSE_FILE" build

docker compose -f "$COMPOSE_FILE" up -d

info "Limpiando imágenes huérfanas..."

docker image prune -f || true

success "Deploy completado con $BRANCH_OR_TAG"
