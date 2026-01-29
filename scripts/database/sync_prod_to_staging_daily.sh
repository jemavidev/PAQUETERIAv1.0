#!/bin/bash
# ============================================================================
# Script: Sincronización Diaria Producción → Staging
# Descripción: Sincroniza solo las tablas existentes en producción
# Uso: ./sync_prod_to_staging_daily.sh
# Cron: 0 2 * * * /path/to/sync_prod_to_staging_daily.sh
# ============================================================================

set -e

echo "🔄 Sincronización diaria: $(date)"
echo "=================================="

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

PROD_HOST="ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com"
PROD_DB="paqueteria_v4"
PROD_USER="jveyes"
PROD_PASS="a?HC!2.*1#?[==:|289qAI=)#V4kDzl\$"

STAGING_HOST="TU_STAGING_HOST.rds.amazonaws.com"
STAGING_DB="paqueteria_staging"
STAGING_USER="jveyes"
STAGING_PASS="TU_STAGING_PASSWORD"

TEMP_DIR="/tmp/db_sync_daily"
mkdir -p $TEMP_DIR

# ============================================================================
# TABLAS A SINCRONIZAR (solo las de producción)
# ============================================================================

TABLES=(
  "users"
  "accounts"
  "packages"
  "customers"
  "rates"
  "messages"
  "announcements"
  "package_events"
  "customer_preferences"
  "files"
  "notifications"
)

# ============================================================================
# SINCRONIZACIÓN POR TABLA
# ============================================================================

TOTAL_TABLES=${#TABLES[@]}
SYNCED=0
FAILED=0

for table in "${TABLES[@]}"; do
  echo ""
  echo "📊 Sincronizando: $table"
  
  # 1. Exportar tabla de producción
  PGPASSWORD=$PROD_PASS pg_dump \
    -h $PROD_HOST \
    -U $PROD_USER \
    -d $PROD_DB \
    -t $table \
    --data-only \
    --no-owner \
    --column-inserts \
    -f $TEMP_DIR/${table}.sql 2>/dev/null
  
  if [ $? -ne 0 ]; then
    echo "   ⚠️  Tabla no existe en producción, omitiendo..."
    continue
  fi
  
  # 2. Truncar tabla en staging (mantener estructura)
  PGPASSWORD=$STAGING_PASS psql \
    -h $STAGING_HOST \
    -U $STAGING_USER \
    -d $STAGING_DB \
    -c "TRUNCATE TABLE $table RESTART IDENTITY CASCADE;" 2>/dev/null
  
  # 3. Importar datos
  PGPASSWORD=$STAGING_PASS psql \
    -h $STAGING_HOST \
    -U $STAGING_USER \
    -d $STAGING_DB \
    -f $TEMP_DIR/${table}.sql 2>/dev/null
  
  if [ $? -eq 0 ]; then
    # Contar registros
    COUNT=$(PGPASSWORD=$STAGING_PASS psql -h $STAGING_HOST -U $STAGING_USER -d $STAGING_DB -t -c "SELECT COUNT(*) FROM $table;" | tr -d ' ')
    echo "   ✅ $COUNT registros sincronizados"
    ((SYNCED++))
  else
    echo "   ❌ Error sincronizando $table"
    ((FAILED++))
  fi
done

# ============================================================================
# LIMPIEZA
# ============================================================================

rm -rf $TEMP_DIR

# ============================================================================
# RESUMEN
# ============================================================================

echo ""
echo "=================================="
echo "✅ Sincronización completada"
echo "   Total: $TOTAL_TABLES tablas"
echo "   Exitosas: $SYNCED"
echo "   Fallidas: $FAILED"
echo "   Fecha: $(date)"
echo "=================================="
