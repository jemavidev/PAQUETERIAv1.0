#!/bin/bash
# Script de sincronización sin Docker - usa pg_dump/pg_restore del host

HOST="ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com"
USER="jveyes"
PASS='a?HC!2.*1#?[==:|289qAI=)#V4kDzl'

export PGPASSWORD="$PASS"

echo "🔄 Sincronizando producción → staging..."
echo ""

# Exportar producción
echo "📦 Exportando producción..."
pg_dump -h "$HOST" -U "$USER" -d paqueteria_v4 -F c -f /tmp/backup.dump --no-owner --no-acl

if [ $? -eq 0 ]; then
    echo "✅ Exportado"
else
    echo "❌ Error en exportación"
    exit 1
fi

echo ""

# Restaurar en staging
echo "📥 Restaurando en staging..."
pg_restore -h "$HOST" -U "$USER" -d paqueteria_staging /tmp/backup.dump --clean --if-exists --no-owner --no-acl 2>&1 | grep -v "^WARNING" || true

if [ $? -le 1 ]; then
    echo "✅ Restaurado"
else
    echo "❌ Error en restauración"
    exit 1
fi

echo ""
echo "✅ Sincronización completada"
rm -f /tmp/backup.dump
