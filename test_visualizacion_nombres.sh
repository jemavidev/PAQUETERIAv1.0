#!/bin/bash

# Script para verificar que los nombres personalizados se muestran correctamente

echo "=========================================="
echo "PRUEBA: Visualización de Nombres Personalizados"
echo "=========================================="
echo ""

# Configuración
BASE_URL="https://staging.jemavi.co"

echo "🔍 Consultando lista de paquetes/anuncios..."
echo ""

# Obtener los últimos anuncios
curl -s "$BASE_URL/api/packages/list?page=1&limit=10" | jq '.items[] | select(.status == "ANUNCIADO") | {guide_number, tracking_code, customer_name, status}' 2>/dev/null

echo ""
echo "=========================================="
echo "Verifica que los nombres mostrados sean los"
echo "nombres personalizados del anuncio, no los"
echo "nombres originales de los clientes."
echo "=========================================="
