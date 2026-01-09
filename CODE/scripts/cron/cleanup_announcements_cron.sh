#!/bin/bash
# ============================================
# CRON: Limpieza automática de anuncios antiguos
# ============================================
# Ejecutar diariamente para eliminar anuncios > 15 días
#
# Agregar a crontab:
#   0 3 * * * /path/to/cleanup_announcements_cron.sh >> /var/log/cleanup_announcements.log 2>&1
#
# O en Docker, agregar al entrypoint o usar un servicio de cron
# ============================================

set -e

# Directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Cargar variables de entorno
if [ -f "$PROJECT_DIR/.env" ]; then
    export $(cat "$PROJECT_DIR/.env" | grep -v '^#' | xargs)
fi

# Timestamp para logs
echo ""
echo "============================================"
echo "🕐 $(date '+%Y-%m-%d %H:%M:%S') - Iniciando limpieza de anuncios"
echo "============================================"

# Ejecutar script de limpieza en modo automático
cd "$PROJECT_DIR/src"
python "$PROJECT_DIR/scripts/maintenance/cleanup_old_announcements.py" --days 15 --auto

echo ""
echo "✅ $(date '+%Y-%m-%d %H:%M:%S') - Limpieza completada"
echo "============================================"
