#!/bin/bash
# Script para reiniciar el servidor y limpiar caché

echo "🔄 Deteniendo servidor..."
pkill -f "uvicorn main:app" 2>/dev/null

echo "🧹 Limpiando caché de Python..."
find CODE/src -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find CODE/src -type f -name "*.pyc" -delete 2>/dev/null

echo "✅ Caché limpiado"
echo ""
echo "🚀 Para iniciar el servidor ejecuta:"
echo "   cd CODE/src"
echo "   uvicorn main:app --reload --host 0.0.0.0 --port 8000"
