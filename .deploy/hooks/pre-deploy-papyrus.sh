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
    read -p "¿Continuar de todas formas? [y/N]: " -n 1 -r
    echo ""
    [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1
fi

# 2. Verificar servicios críticos
echo "🔍 Verificando servicios críticos..."
if ! docker ps | grep -q "redis"; then
    echo "❌ Redis no está corriendo"
    exit 1
fi

# 3. Crear backup de seguridad
echo "💾 Creando backup de seguridad..."
BACKUP_NAME="pre-deploy-$(date +%Y%m%d_%H%M%S).sql"
docker compose exec -T postgres pg_dump -U postgres paqueteria > "/tmp/$BACKUP_NAME"
echo "✅ Backup creado: $BACKUP_NAME"

# 4. Notificar inicio de deploy (opcional)
# curl -X POST $SLACK_WEBHOOK -d '{"text":"🚀 Iniciando deploy en papyrus..."}'

echo "✅ Verificaciones pre-deploy completadas"
exit 0
