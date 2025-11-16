#!/bin/bash
# ========================================
# SCRIPT SIMPLE DE ACTUALIZACIÓN
# ========================================
# Versión simplificada: solo hace pull y muestra cambios
# Para uso rápido desde SSH: ssh papyrus "./update.sh"
# ========================================

cd "$(dirname "$0")"
exec ./pull-update.sh

