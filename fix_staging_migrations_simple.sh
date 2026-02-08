#!/bin/bash
# ========================================
# Fix Staging Migrations - Versión Simple
# ========================================

set -e

echo "🔧 Arreglando migraciones de staging..."
echo ""

# Cargar variables de entorno
if [ -f .env.staging ]; then
    source .env.staging
else
    echo "❌ No se encontró .env.staging"
    exit 1
fi

echo "▶ Paso 1: Resetear tabla alembic_version en la base de datos..."
docker compose -f docker-compose.staging.yml exec -T app python3 <<-EOPY
import psycopg2
import os

# Conectar a la base de datos
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Resetear tabla alembic_version
cur.execute("DROP TABLE IF EXISTS alembic_version;")
cur.execute("""
    CREATE TABLE alembic_version (
        version_num VARCHAR(32) NOT NULL,
        CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
    );
""")

conn.commit()
cur.close()
conn.close()

print("✅ Tabla alembic_version reseteada")
EOPY

echo ""
echo "▶ Paso 2: Marcar HEAD actual sin ejecutar migraciones..."
docker compose -f docker-compose.staging.yml exec app alembic stamp head

echo ""
echo "✅ Migraciones arregladas!"
echo ""
echo "▶ Ahora puedes ejecutar el deploy nuevamente:"
echo "   ./deploy.sh staging"
