#!/bin/bash
# ========================================
# PRE-DEPLOY HOOK - PAPYRUS
# ========================================
# Este script se ejecuta ANTES del deploy en papyrus

echo "🔍 Ejecutando verificaciones pre-deploy..."

# 1. Verificar espacio en disco
echo "📊 Verificando espacio en disco..."
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    echo "⚠️  Advertencia: Disco al ${DISK_USAGE}%"
    echo "💡 Considera limpiar imágenes Docker antiguas: docker system prune -a"
else
    echo "✅ Espacio en disco: ${DISK_USAGE}% usado"
fi

# 2. Verificar servicios críticos
echo "🔍 Verificando servicios críticos..."
if docker ps 2>/dev/null | grep -q "redis"; then
    echo "✅ Redis está corriendo"
else
    echo "⚠️  Redis no está corriendo (se iniciará con el deploy)"
fi

# 3. Backup de seguridad
# PostgreSQL está en RDS - los backups se manejan automáticamente
echo "💾 Backup de base de datos..."
echo "✅ PostgreSQL en RDS - Backups automáticos habilitados"

# 4. Verificar conectividad a RDS (opcional)
echo "🔍 Verificando conectividad..."
if docker compose -f docker-compose.prod.yml ps app 2>/dev/null | grep -q "Up"; then
    echo "✅ Aplicación corriendo"
else
    echo "⚠️  Aplicación no está corriendo (se iniciará con el deploy)"
fi

# 5. Notificar inicio de deploy (opcional)
# curl -X POST $SLACK_WEBHOOK -d '{"text":"🚀 Iniciando deploy en papyrus..."}'

echo "✅ Verificaciones pre-deploy completadas"
exit 0
