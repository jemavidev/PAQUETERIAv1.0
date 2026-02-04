#!/bin/bash
# Script para reiniciar el servidor y aplicar cambios

echo "=========================================="
echo "🔄 Reiniciando Servidor PAQUETEX"
echo "=========================================="
echo ""

# Detectar si está usando Docker o systemd
if docker ps | grep -q paquetex; then
    echo "🐳 Detectado: Docker"
    echo "   Reiniciando contenedor..."
    docker-compose restart app
    echo ""
    echo "✅ Contenedor reiniciado"
    echo ""
    echo "📝 Ver logs:"
    echo "   docker-compose logs -f app"
    
elif systemctl is-active --quiet paquetex; then
    echo "⚙️ Detectado: Systemd"
    echo "   Reiniciando servicio..."
    sudo systemctl restart paquetex
    echo ""
    echo "✅ Servicio reiniciado"
    echo ""
    echo "📝 Ver logs:"
    echo "   journalctl -u paquetex -f"
    
else
    echo "🔍 No se detectó Docker ni Systemd"
    echo ""
    echo "💡 Opciones manuales:"
    echo ""
    echo "   Si usas Docker:"
    echo "   docker-compose restart app"
    echo ""
    echo "   Si usas Systemd:"
    echo "   sudo systemctl restart paquetex"
    echo ""
    echo "   Si ejecutas manualmente:"
    echo "   1. Detén el proceso actual (Ctrl+C)"
    echo "   2. Ejecuta: cd CODE && source .venv/bin/activate && uvicorn src.main:app --reload"
fi

echo ""
echo "=========================================="
echo "⏳ Esperando 5 segundos..."
echo "=========================================="
sleep 5

echo ""
echo "🧪 Verificando que el servidor esté corriendo..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Servidor está corriendo correctamente"
else
    echo "⚠️ El servidor no responde aún, espera unos segundos más"
fi

echo ""
echo "=========================================="
echo "✅ LISTO PARA PROBAR"
echo "=========================================="
echo ""
echo "🎯 Ahora puedes:"
echo "   1. Eliminar las facturas actuales"
echo "   2. Cargar nuevas facturas"
echo "   3. El botón de descarga estará VERDE ✅"
echo ""
