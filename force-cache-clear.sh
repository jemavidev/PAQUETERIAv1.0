#!/bin/bash
# Script para forzar limpieza de caché y reinicio
# Fecha: 2025-11-28

echo "🔄 Forzando limpieza de caché..."

# Si estás usando Docker
if command -v docker &> /dev/null; then
    echo "🐳 Reiniciando contenedores Docker..."
    docker-compose down
    docker-compose up -d --build
fi

# Si estás usando systemd
if command -v systemctl &> /dev/null; then
    echo "🔄 Reiniciando servicio..."
    sudo systemctl restart paquetex
fi

echo "✅ Caché limpiado y servicio reiniciado"
echo ""
echo "📱 INSTRUCCIONES PARA EL CELULAR:"
echo "1. Abre el navegador en tu celular"
echo "2. Ve a Configuración/Ajustes del navegador"
echo "3. Busca 'Borrar datos de navegación' o 'Limpiar caché'"
echo "4. Selecciona 'Imágenes y archivos en caché'"
echo "5. Confirma"
echo ""
echo "O simplemente:"
echo "- Chrome: Mantén presionado el botón de recargar → 'Recarga forzada'"
echo "- Safari: Ajustes → Safari → Borrar historial y datos"
echo ""
