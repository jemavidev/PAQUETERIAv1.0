#!/bin/bash
# ========================================
# Auto-start all containers
# ========================================

echo "🚀 Iniciando todos los contenedores..."

# Development
echo "📦 Iniciando contenedor de desarrollo..."
docker start paquetex_dev_app 2>/dev/null || echo "⚠️  Contenedor de desarrollo no encontrado"

# Staging
echo "📦 Iniciando contenedores de staging..."
docker start paqueteria_staging_redis 2>/dev/null || echo "⚠️  Redis staging no encontrado"
docker start paqueteria_staging_app 2>/dev/null || echo "⚠️  App staging no encontrada"

# Production (si existen)
echo "📦 Iniciando contenedores de producción..."
docker start paqueteria_v1_prod_redis 2>/dev/null || echo "⚠️  Redis producción no encontrado"
docker start paqueteria_v1_prod_app 2>/dev/null || echo "⚠️  App producción no encontrada"
docker start paqueteria_v1_prod_celery 2>/dev/null || echo "⚠️  Celery worker no encontrado"
docker start paqueteria_v1_prod_celery_beat 2>/dev/null || echo "⚠️  Celery beat no encontrado"
docker start paqueteria_v1_prod_prometheus 2>/dev/null || echo "⚠️  Prometheus no encontrado"
docker start paqueteria_v1_prod_grafana 2>/dev/null || echo "⚠️  Grafana no encontrado"
docker start paqueteria_v1_prod_node_exporter 2>/dev/null || echo "⚠️  Node exporter no encontrado"

echo ""
echo "✅ Proceso completado. Estado de contenedores:"
echo ""
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
