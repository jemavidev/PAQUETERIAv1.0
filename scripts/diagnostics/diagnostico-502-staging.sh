#!/bin/bash

# ========================================
# DIAGNÓSTICO ERROR 502 - STAGING
# ========================================

echo "🔍 DIAGNÓSTICO ERROR 502 EN STAGING"
echo "===================================="
echo ""

# 1. Estado de contenedores
echo "📦 1. ESTADO DE CONTENEDORES DOCKER"
echo "-----------------------------------"
docker ps -a | grep -E "paqueteria_staging|CONTAINER"
echo ""

# 2. Logs recientes del contenedor app
echo "📋 2. LOGS DEL CONTENEDOR APP (últimas 30 líneas)"
echo "------------------------------------------------"
docker logs paqueteria_staging_app --tail 30 2>&1
echo ""

# 3. Logs de Redis
echo "📋 3. LOGS DE REDIS (últimas 20 líneas)"
echo "---------------------------------------"
docker logs paqueteria_staging_redis --tail 20 2>&1
echo ""

# 4. Verificar puertos
echo "🔌 4. PUERTOS EN USO"
echo "-------------------"
sudo netstat -tulpn | grep -E ":8001|:6380|:80|:443" || sudo ss -tulpn | grep -E ":8001|:6380|:80|:443"
echo ""

# 5. Verificar nginx
echo "🌐 5. ESTADO DE NGINX"
echo "--------------------"
sudo systemctl status nginx --no-pager | head -10
echo ""

# 6. Logs de nginx
echo "📋 6. LOGS DE NGINX (últimas 20 líneas)"
echo "---------------------------------------"
sudo tail -20 /var/log/nginx/error.log 2>&1
echo ""

# 7. Recursos del sistema
echo "💾 7. RECURSOS DEL SISTEMA"
echo "-------------------------"
echo "Espacio en disco:"
df -h / | grep -E "Filesystem|/$"
echo ""
echo "Memoria:"
free -h
echo ""

# 8. Test de conectividad
echo "🔗 8. TEST DE CONECTIVIDAD"
echo "-------------------------"
echo "Test al puerto 8001 (app):"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:8001/ 2>&1 || echo "❌ No se puede conectar al puerto 8001"
echo ""

# 9. Configuración de nginx para staging
echo "⚙️  9. CONFIGURACIÓN NGINX STAGING"
echo "----------------------------------"
if [ -f /etc/nginx/sites-available/staging ]; then
    echo "Archivo encontrado: /etc/nginx/sites-available/staging"
    grep -E "server_name|proxy_pass|listen" /etc/nginx/sites-available/staging
else
    echo "❌ No se encontró /etc/nginx/sites-available/staging"
    echo "Buscando otras configuraciones..."
    ls -la /etc/nginx/sites-available/ | grep -i staging
fi
echo ""

# 10. Resumen
echo "📊 RESUMEN"
echo "=========="
APP_STATUS=$(docker inspect -f '{{.State.Status}}' paqueteria_staging_app 2>/dev/null || echo "no encontrado")
REDIS_STATUS=$(docker inspect -f '{{.State.Status}}' paqueteria_staging_redis 2>/dev/null || echo "no encontrado")
NGINX_STATUS=$(sudo systemctl is-active nginx 2>/dev/null || echo "desconocido")

echo "App Container: $APP_STATUS"
echo "Redis Container: $REDIS_STATUS"
echo "Nginx: $NGINX_STATUS"
echo ""

# Recomendaciones
echo "💡 RECOMENDACIONES"
echo "=================="
if [ "$APP_STATUS" != "running" ]; then
    echo "❌ El contenedor de la app NO está corriendo"
    echo "   Ejecuta: docker-compose -f docker-compose.staging.yml up -d"
elif [ "$NGINX_STATUS" != "active" ]; then
    echo "❌ Nginx NO está activo"
    echo "   Ejecuta: sudo systemctl start nginx"
else
    echo "✅ Contenedores corriendo, revisar logs arriba para errores específicos"
    echo "   Si hay errores de conexión, verifica la configuración de nginx"
fi
echo ""
echo "🚀 SOLUCIÓN RÁPIDA:"
echo "   cd $(pwd)"
echo "   docker-compose -f docker-compose.staging.yml restart"
echo "   sudo systemctl restart nginx"
