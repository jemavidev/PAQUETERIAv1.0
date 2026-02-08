#!/bin/bash
# ========================================
# Fix Staging Migrations - Reset Alembic
# ========================================

set -e

echo "🔧 Arreglando migraciones de staging..."

# Opción 1: Resetear la tabla alembic_version
echo ""
echo "📋 OPCIÓN 1: Resetear tabla alembic_version"
echo "Esto eliminará el historial de migraciones y empezará desde cero"
echo ""
echo "Ejecuta en staging:"
echo "docker-compose -f docker-compose.staging.yml exec app alembic stamp head"
echo ""

# Opción 2: Eliminar la tabla y recrear
echo "📋 OPCIÓN 2: Eliminar y recrear (más agresivo)"
echo ""
echo "SQL a ejecutar en la base de datos de staging:"
echo "DROP TABLE IF EXISTS alembic_version;"
echo ""
echo "Luego ejecuta:"
echo "docker-compose -f docker-compose.staging.yml exec app alembic stamp head"
echo ""

# Opción 3: Script automático
echo "📋 OPCIÓN 3: Script automático (RECOMENDADO)"
echo ""
read -p "¿Quieres ejecutar el fix automático? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "▶ Conectando a staging..."
    
    # Obtener DATABASE_URL de staging
    if [ -f .env.staging ]; then
        source .env.staging
    else
        echo "❌ No se encontró .env.staging"
        exit 1
    fi
    
    # Resetear alembic_version
    echo "▶ Reseteando tabla alembic_version..."
    docker-compose -f docker-compose.staging.yml exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" <<-EOSQL
        -- Eliminar tabla de versiones
        DROP TABLE IF EXISTS alembic_version;
        
        -- Recrear tabla
        CREATE TABLE alembic_version (
            version_num VARCHAR(32) NOT NULL,
            CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
        );
EOSQL
    
    echo "▶ Marcando HEAD actual..."
    docker-compose -f docker-compose.staging.yml exec app alembic stamp head
    
    echo "✅ Migraciones arregladas!"
    echo ""
    echo "▶ Ahora ejecuta el deploy nuevamente:"
    echo "./deploy.sh staging"
fi
