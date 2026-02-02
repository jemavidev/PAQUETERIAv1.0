#!/bin/bash

echo "=========================================="
echo "REINICIANDO SERVIDOR PARA VER BOTONES"
echo "=========================================="
echo ""

echo "🔍 Buscando procesos de FastAPI/Uvicorn..."
PIDS=$(ps aux | grep -E "(uvicorn|python.*main)" | grep -v grep | awk '{print $2}')

if [ -z "$PIDS" ]; then
    echo "❌ No se encontró ningún servidor FastAPI corriendo"
    echo ""
    echo "Para iniciar el servidor manualmente:"
    echo "  cd CODE"
    echo "  python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000"
    exit 1
fi

echo "✓ Procesos encontrados:"
ps aux | grep -E "(uvicorn|python.*main)" | grep -v grep | head -5

echo ""
echo "⚠️  IMPORTANTE: Este script matará los procesos del servidor."
echo "    Después deberás reiniciarlo manualmente."
echo ""
read -p "¿Continuar? (s/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "❌ Operación cancelada"
    exit 0
fi

echo ""
echo "🛑 Deteniendo procesos..."
for PID in $PIDS; do
    echo "  Matando proceso $PID..."
    kill -9 $PID 2>/dev/null
done

echo ""
echo "✅ Procesos detenidos"
echo ""
echo "=========================================="
echo "SIGUIENTE PASO: REINICIAR EL SERVIDOR"
echo "=========================================="
echo ""
echo "Ejecuta uno de estos comandos según tu entorno:"
echo ""
echo "1. Si usas Docker:"
echo "   cd CODE"
echo "   docker-compose up -d"
echo ""
echo "2. Si usas desarrollo local:"
echo "   cd CODE"
echo "   python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "3. Después, limpia la caché del navegador:"
echo "   - Presiona Ctrl + Shift + R (Windows/Linux)"
echo "   - O abre en modo incógnito: Ctrl + Shift + N"
echo ""
echo "=========================================="
