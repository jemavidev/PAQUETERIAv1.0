#!/bin/bash
# Sincronización simple usando pg_dump y pg_restore

set -e

HOST="ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com"
USER="jveyes"
PASS="a?HC!2.*1#?[==:|289qAI=)#V4kDzl\$"

export PGPASSWORD="$PASS"

echo "🔄 Sincronizando producción → staging..."
echo ""

# Dump
echo "📦 Exportando producción..."
pg_dump -h "$HOST" -U "$USER" -d paqueteria_v4 -F c -f /tmp/backup.dump --no-owner --no-acl
echo "✅ Exportado"
echo ""

# Restore
echo "📥 Restaurando en staging..."
pg_restore -h "$HOST" -U "$USER" -d paqueteria_staging /tmp/backup.dump --clean --if-exists --no-owner --no-acl 2>&1 | grep -v "^WARNING" || true
echo "✅ Restaurado"
echo ""

# Verify
echo "🔍 Verificando..."
psql -h "$HOST" -U "$USER" -d paqueteria_staging -c "SELECT COUNT(*) as tablas FROM pg_tables WHERE schemaname='public';"
psql -h "$HOST" -U "$USER" -d paqueteria_staging -c "SELECT COUNT(*) as usuarios FROM users;" 2>/dev/null || echo "Tabla users pendiente"

echo ""
echo "✅ Sincronización completada"
