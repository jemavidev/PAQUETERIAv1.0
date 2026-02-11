#!/bin/bash
# Script para marcar la migración como aplicada sin ejecutarla

set -e

echo "=================================================="
echo "FIX: Migración tipo_factura ya aplicada"
echo "=================================================="
echo ""

echo "La columna 'tipo_factura' ya existe en la base de datos."
echo "Vamos a marcar la migración como aplicada sin ejecutarla."
echo ""

# Opción 1: Marcar la migración como aplicada (RECOMENDADO)
echo "[Opción 1] Marcar migración como aplicada (stamp)"
echo ""
echo "Ejecuta en el servidor staging:"
echo ""
echo "  docker-compose -f docker-compose.staging.yml exec app alembic stamp 20260211_092552"
echo ""
echo "Esto le dice a Alembic que la migración 20260211_092552 ya está aplicada"
echo "sin intentar ejecutarla nuevamente."
echo ""

echo "=================================================="
echo ""

# Opción 2: Modificar la migración para que sea idempotente
echo "[Opción 2] Hacer la migración idempotente (alternativa)"
echo ""
echo "Si prefieres que la migración verifique si la columna existe antes de crearla,"
echo "podemos modificar el archivo de migración."
echo ""

echo "=================================================="
echo "RECOMENDACIÓN: Usa Opción 1 (stamp)"
echo "=================================================="
