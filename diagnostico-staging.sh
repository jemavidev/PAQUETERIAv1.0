#!/bin/bash
# Script de diagnóstico rápido para staging
# Fecha: 2025-11-28

echo "🔍 =========================================="
echo "   DIAGNÓSTICO RÁPIDO DE STAGING"
echo "   =========================================="
echo ""

echo "📋 1. Verificando contenedores Docker..."
echo "----------------------------------------"
docker-compose -f docker-compose.staging.yml ps
echo ""

echo "📋 2. Verificando logs recientes (últimas 100 líneas)..."
echo "----------------------------------------"
docker-compose -f docker-compose.staging.yml logs --tail=100
echo ""

echo "📋 3. Verificando puertos en uso..."
echo "----------------------------------------"
netstat -tulpn | grep -E ':(80|443|8000|5000)' || ss -tulpn | grep -E ':(80|443|8000|5000)'
echo ""

echo "📋 4. Verificando estado de servicios..."
echo "----------------------------------------"
if command -v systemctl &> /dev/null; then
    systemctl status nginx 2>/dev/null || echo "Nginx no está instalado o no usa systemd"
fi
echo ""

echo "📋 5. Verificando espacio en disco..."
echo "----------------------------------------"
df -h | grep -E '(Filesystem|/$|/var)'
echo ""

echo "📋 6. Verificando memoria..."
echo "----------------------------------------"
free -h
echo ""

echo "📋 7. Verificando procesos Python..."
echo "----------------------------------------"
ps aux | grep python | grep -v grep
echo ""

echo "✅ Diagnóstico completado"
echo ""
echo "💡 Acciones comunes según el problema:"
echo "   - Contenedores caídos: docker-compose -f docker-compose.staging.yml up -d"
echo "   - Error en logs: Revisar logs arriba y corregir"
echo "   - Puerto ocupado: Liberar puerto o cambiar configuración"
echo "   - Sin espacio: Limpiar archivos o logs antiguos"
echo "   - Sin memoria: Reiniciar contenedores o servidor"
