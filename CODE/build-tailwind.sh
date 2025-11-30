#!/bin/bash

# Script para compilar Tailwind CSS
# Fecha: 2024-11-30

set -e

echo "🎨 Compilando Tailwind CSS..."
echo "=============================="
echo ""

# Verificar si node_modules existe
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependencias..."
    npm install
    echo ""
fi

# Compilar Tailwind
echo "🔨 Compilando CSS..."
npm run build:css

echo ""
echo "✅ Tailwind CSS compilado exitosamente"
echo "📄 Archivo generado: src/static/css/tailwind.css"
echo ""
echo "💡 Para desarrollo con auto-reload:"
echo "   npm run watch:css"
echo ""
