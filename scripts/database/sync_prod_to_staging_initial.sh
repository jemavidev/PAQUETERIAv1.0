#!/bin/bash
# ============================================================================
# Script: Sincronización Inicial Producción → Staging
# Descripción: Copia completa de la base de datos de producción a staging
# Uso: ./sync_prod_to_staging_initial.sh
# ============================================================================

set -e  # Salir si hay error

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║     🔄 SINCRONIZACIÓN INICIAL: PRODUCCIÓN → STAGING             ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# Producción
PROD_HOST="ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com"
PROD_DB="paqueteria_v4"
PROD_USER="jveyes"
PROD_PASS="a?HC!2.*1#?[==:|289qAI=)#V4kDzl\$"

# Staging (CONFIGURAR ESTOS VALORES)
STAGING_HOST="TU_STAGING_HOST.rds.amazonaws.com"
STAGING_DB="paqueteria_staging"
STAGING_USER="jveyes"
STAGING_PASS="TU_STAGING_PASSWORD"

# Archivos temporales
BACKUP_DIR="/tmp/db_sync"
BACKUP_FILE="$BACKUP_DIR/prod_backup_$(date +%Y%m%d_%H%M%S).dump"
LOG_FILE="$BACKUP_DIR/sync_$(date +%Y%m%d_%H%M%S).log"

# ============================================================================
# VALIDACIONES
# ============================================================================

echo "📋 Validando configuración..."

if [ "$STAGING_HOST" == "TU_STAGING_HOST.rds.amazonaws.com" ]; then
    echo "❌ ERROR: Debes configurar STAGING_HOST en el script"
    exit 1
fi

if [ "$STAGING_PASS" == "TU_STAGING_PASSWORD" ]; then
    echo "❌ ERROR: Debes configurar STAGING_PASS en el script"
    exit 1
fi

# Crear directorio de backup
mkdir -p $BACKUP_DIR

echo "✅ Configuración validada"
echo ""

# ============================================================================
# BACKUP DE STAGING (por seguridad)
# ============================================================================

echo "💾 Creando backup de staging (por seguridad)..."
STAGING_BACKUP="$BACKUP_DIR/staging_backup_before_sync_$(date +%Y%m%d_%H%M%S).dump"

PGPASSWORD=$STAGING_PASS pg_dump \
  -h $STAGING_HOST \
  -U $STAGING_USER \
  -d $STAGING_DB \
  --no-owner \
  --no-acl \
  -F c \
  -f $STAGING_BACKUP 2>/dev/null || echo "⚠️  Staging vacío o no existe (normal en primera ejecución)"

echo "✅ Backup de staging guardado en: $STAGING_BACKUP"
echo ""

# ============================================================================
# EXPORTAR PRODUCCIÓN
# ============================================================================

echo "📦 Exportando base de datos de producción..."
echo "   Host: $PROD_HOST"
echo "   Database: $PROD_DB"
echo ""

PGPASSWORD=$PROD_PASS pg_dump \
  -h $PROD_HOST \
  -U $PROD_USER \
  -d $PROD_DB \
  --no-owner \
  --no-acl \
  -F c \
  -f $BACKUP_FILE

if [ $? -eq 0 ]; then
    BACKUP_SIZE=$(du -h $BACKUP_FILE | cut -f1)
    echo "✅ Exportación completada: $BACKUP_SIZE"
else
    echo "❌ ERROR: Falló la exportación de producción"
    exit 1
fi
echo ""

# ============================================================================
# IMPORTAR A STAGING
# ============================================================================

echo "📥 Importando a staging..."
echo "   Host: $STAGING_HOST"
echo "   Database: $STAGING_DB"
echo ""

PGPASSWORD=$STAGING_PASS pg_restore \
  -h $STAGING_HOST \
  -U $STAGING_USER \
  -d $STAGING_DB \
  --clean \
  --if-exists \
  --no-owner \
  --no-acl \
  $BACKUP_FILE 2>&1 | tee -a $LOG_FILE

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "✅ Importación completada"
else
    echo "⚠️  Importación completada con advertencias (revisar log)"
fi
echo ""

# ============================================================================
# APLICAR MIGRACIONES DE STAGING
# ============================================================================

echo "🔧 Aplicando migraciones de staging..."
cd CODE

DATABASE_URL="postgresql://$STAGING_USER:$STAGING_PASS@$STAGING_HOST:5432/$STAGING_DB" \
  alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Migraciones aplicadas"
else
    echo "❌ ERROR: Falló la aplicación de migraciones"
    exit 1
fi
echo ""

# ============================================================================
# VERIFICACIÓN
# ============================================================================

echo "🔍 Verificando sincronización..."

# Contar tablas
PROD_TABLES=$(PGPASSWORD=$PROD_PASS psql -h $PROD_HOST -U $PROD_USER -d $PROD_DB -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';" | tr -d ' ')

STAGING_TABLES=$(PGPASSWORD=$STAGING_PASS psql -h $STAGING_HOST -U $STAGING_USER -d $STAGING_DB -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';" | tr -d ' ')

echo "   Tablas en producción: $PROD_TABLES"
echo "   Tablas en staging: $STAGING_TABLES"

if [ $STAGING_TABLES -ge $PROD_TABLES ]; then
    echo "✅ Staging tiene todas las tablas de producción (+ nuevas)"
else
    echo "⚠️  Staging tiene menos tablas que producción"
fi
echo ""

# ============================================================================
# LIMPIEZA
# ============================================================================

echo "🧹 Limpiando archivos temporales..."
# Mantener backups por 7 días
find $BACKUP_DIR -name "*.dump" -mtime +7 -delete
find $BACKUP_DIR -name "*.log" -mtime +7 -delete
echo "✅ Limpieza completada"
echo ""

# ============================================================================
# RESUMEN
# ============================================================================

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                  ✅ SINCRONIZACIÓN COMPLETADA                    ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Resumen:"
echo "   • Backup de producción: $BACKUP_FILE"
echo "   • Backup de staging: $STAGING_BACKUP"
echo "   • Log: $LOG_FILE"
echo "   • Tablas sincronizadas: $PROD_TABLES"
echo "   • Tablas en staging: $STAGING_TABLES"
echo ""
echo "🎯 Próximos pasos:"
echo "   1. Verificar que staging funcione correctamente"
echo "   2. Configurar sincronización diaria (cron job)"
echo "   3. Probar nuevas features en staging"
echo ""
