#!/usr/bin/env bash
# Borra el Postgres local persistente de paquetex_dev_up.sh (contenedor +
# volumen con nombre) para volver a datos limpios -- la próxima corrida de
# paquetex_dev_up.sh migra y siembra un admin nuevo desde cero.

set -euo pipefail

CONTAINER=paquetex_dev_pg
VOLUME=paquetex_dev_pgdata

echo "==> Borrando ${CONTAINER} y su volumen (${VOLUME})..."
docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
docker volume rm "$VOLUME" >/dev/null 2>&1 || true

echo "Listo -- corre ./scripts/paquetex_dev_up.sh para empezar de cero."
