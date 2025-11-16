#!/bin/bash
# ========================================
# SCRIPT SIMPLE DE ACTUALIZACIÓN
# ========================================
# Versión simplificada: solo hace pull y muestra cambios
# Para uso rápido desde SSH: ssh papyrus "cd ~/paqueteria && ./DOCS/scripts/deployment/update.sh"
# ========================================

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/../../.."  # Ir a la raíz del proyecto
exec "$SCRIPT_DIR/pull-update.sh"
