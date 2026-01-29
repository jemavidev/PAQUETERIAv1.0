#!/bin/bash
# ============================================================================
# Script: Crear Base de Datos Staging (usando Docker)
# Descripción: Crea la base de datos paqueteria_staging en AWS RDS
# Uso: ./create_staging_database_docker.sh
# ============================================================================

set -e

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║          🆕 CREAR BASE DE DATOS STAGING                          ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

PROD_HOST="ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com"
PROD_USER="jveyes"
PROD_PASS="a?HC!2.*1#?[==:|289qAI=)#V4kDzl\$"

NEW_DB="paqueteria_staging"

# Función para ejecutar psql con Docker
psql_docker() {
    docker run --rm -e PGPASSWORD="$PROD_PASS" postgres:15-alpine psql \
        -h "$PROD_HOST" \
        -U "$PROD_USER" \
        "$@"
}

# ============================================================================
# VALIDACIONES DE SEGURIDAD
# ============================================================================

echo "🔒 Validaciones de seguridad..."
echo ""

# Confirmar con el usuario
echo "⚠️  IMPORTANTE: Este script creará una NUEVA base de datos."
echo ""
echo "   Base de datos a crear: $NEW_DB"
echo "   Host: $PROD_HOST"
echo "   Usuario: $PROD_USER"
echo ""
echo "   ✅ NO se modificará la base de datos de producción (paqueteria_v4)"
echo "   ✅ Solo se creará una nueva base de datos vacía"
echo ""
read -p "¿Deseas continuar? (escribe 'SI' para confirmar): " confirm

if [ "$confirm" != "SI" ]; then
    echo "❌ Operación cancelada por el usuario"
    exit 1
fi

echo ""
echo "✅ Confirmación recibida"
echo ""

# ============================================================================
# VERIFICAR CONEXIÓN A AWS RDS
# ============================================================================

echo "🔍 Verificando conexión a AWS RDS..."

if ! psql_docker -d postgres -c "SELECT version();" > /dev/null 2>&1; then
    echo "❌ ERROR: No se pudo conectar a AWS RDS"
    echo "   Verifica:"
    echo "   - Que tengas acceso a internet"
    echo "   - Que las credenciales sean correctas"
    echo "   - Que el servidor RDS esté accesible"
    exit 1
fi

echo "✅ Conexión exitosa a AWS RDS"
echo ""

# ============================================================================
# VERIFICAR SI LA BASE DE DATOS YA EXISTE
# ============================================================================

echo "🔍 Verificando si la base de datos ya existe..."

DB_EXISTS=$(psql_docker -d postgres -t -c "SELECT 1 FROM pg_database WHERE datname='$NEW_DB';" 2>/dev/null | tr -d ' ')

if [ "$DB_EXISTS" == "1" ]; then
    echo "⚠️  La base de datos '$NEW_DB' ya existe"
    echo ""
    read -p "¿Deseas eliminarla y recrearla? (escribe 'SI' para confirmar): " confirm_drop
    
    if [ "$confirm_drop" != "SI" ]; then
        echo "❌ Operación cancelada"
        exit 1
    fi
    
    echo ""
    echo "🗑️  Eliminando base de datos existente..."
    psql_docker -d postgres -c "DROP DATABASE $NEW_DB;"
    
    echo "✅ Base de datos eliminada"
fi

echo ""

# ============================================================================
# CREAR BASE DE DATOS
# ============================================================================

echo "🆕 Creando base de datos '$NEW_DB'..."

psql_docker -d postgres -c "CREATE DATABASE $NEW_DB OWNER $PROD_USER;"

if [ $? -eq 0 ]; then
    echo "✅ Base de datos creada exitosamente"
else
    echo "❌ ERROR: No se pudo crear la base de datos"
    exit 1
fi

echo ""

# ============================================================================
# VERIFICAR CREACIÓN
# ============================================================================

echo "🔍 Verificando creación..."

DB_SIZE=$(psql_docker -d postgres -t -c "SELECT pg_size_pretty(pg_database_size('$NEW_DB'));" 2>/dev/null | tr -d ' ')

if [ -n "$DB_SIZE" ]; then
    echo "✅ Base de datos verificada"
    echo "   Nombre: $NEW_DB"
    echo "   Tamaño: $DB_SIZE"
    echo "   Host: $PROD_HOST"
else
    echo "❌ ERROR: No se pudo verificar la base de datos"
    exit 1
fi

echo ""

# ============================================================================
# LISTAR BASES DE DATOS
# ============================================================================

echo "📊 Bases de datos en el servidor:"
echo ""

psql_docker -d postgres -c "SELECT datname, pg_size_pretty(pg_database_size(datname)) as size FROM pg_database WHERE datname IN ('paqueteria_v4', 'paqueteria_staging') ORDER BY datname;"

echo ""

# ============================================================================
# RESUMEN
# ============================================================================

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                  ✅ BASE DE DATOS CREADA                         ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Resumen:"
echo "   • Base de datos: $NEW_DB"
echo "   • Host: $PROD_HOST"
echo "   • Usuario: $PROD_USER"
echo "   • Estado: Vacía (lista para sincronización)"
echo ""
echo "🎯 Próximos pasos:"
echo "   1. Ejecutar sincronización inicial:"
echo "      ./scripts/database/sync_prod_to_staging_initial.sh"
echo ""
echo "   2. Verificar que staging use .env.staging:"
echo "      docker-compose -f docker-compose.staging.yml config | grep DATABASE_URL"
echo ""
echo "   3. Iniciar staging:"
echo "      docker-compose -f docker-compose.staging.yml up -d"
echo ""
