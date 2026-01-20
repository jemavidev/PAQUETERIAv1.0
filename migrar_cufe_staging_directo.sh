#!/bin/bash
# Script para ejecutar DIRECTAMENTE en el servidor staging
# Copia este archivo al servidor y ejecútalo allí

echo "🚀 Ejecutando migración de tabla cufe_records"
echo "=============================================="

cd /home/jemavi/paquetex

echo "📦 Entrando al contenedor de la aplicación..."
docker-compose -f docker-compose.staging.yml exec app bash -c '
cd /app

echo "🔍 Verificando estado actual de migraciones..."
alembic current

echo ""
echo "📋 Últimas migraciones disponibles:"
alembic history | head -20

echo ""
echo "🔄 Ejecutando migración create_cufe_records..."
alembic upgrade create_cufe_records

echo ""
echo "✅ Verificando migración aplicada..."
alembic current

echo ""
echo "🔍 Verificando que la tabla existe..."
python3 << "ENDPYTHON"
import sys
sys.path.insert(0, "/app/src")
from app.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()

if "cufe_records" in tables:
    print("✅ Tabla cufe_records creada exitosamente")
    columns = inspector.get_columns("cufe_records")
    print(f"   Columnas: {[c[\"name\"] for c in columns]}")
else:
    print("❌ ERROR: Tabla cufe_records NO existe")
    print(f"   Tablas disponibles: {tables}")
ENDPYTHON
'

echo ""
echo "🔄 Reiniciando servicios..."
docker-compose -f docker-compose.staging.yml restart app

echo ""
echo "✅ Migración completada"
echo ""
echo "Ahora puedes ir a https://staging.jemavi.co/invoices"
echo "y usar el tab CUFE sin errores"
