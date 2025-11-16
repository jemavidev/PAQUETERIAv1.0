#!/bin/bash
# ========================================
# SCRIPT SIMPLE DE ACTUALIZACIÓN
# ========================================
# Versión simplificada: solo hace pull y muestra cambios
# Para uso rápido: ./CODE/scripts/deployment/update.sh
# Funciona desde cualquier ubicación dentro del proyecto
# ========================================

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
exec "$SCRIPT_DIR/pull-update.sh"
