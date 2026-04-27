#!/bin/bash
# Script para analizar precios con IVA en productos

echo "🔍 Analizando precios con IVA en productos..."
echo ""

# Verificar si estamos en Docker o local
if [ -f "/.dockerenv" ]; then
    echo "📦 Ejecutando en Docker..."
    python3 recalcular_precios_iva_productos.py
else
    echo "💻 Ejecutando en local..."
    if [ -d ".venv" ]; then
        source .venv/bin/activate
        python recalcular_precios_iva_productos.py
    else
        echo "❌ No se encontró el entorno virtual .venv"
        echo "💡 Ejecuta este comando dentro del contenedor Docker:"
        echo "   docker-compose exec web python recalcular_precios_iva_productos.py"
        exit 1
    fi
fi
