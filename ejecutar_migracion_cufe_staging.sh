#!/bin/bash

echo "🚀 Ejecutando migración de tabla cufe_records en STAGING"
echo "=========================================================="

# Conectar a staging y ejecutar la migración
ssh jemavi@staging.jemavi.co << 'ENDSSH'

cd /home/jemavi/paquetex

echo "📦 Entrando al contenedor de la aplicación..."
docker-compose -f docker-compose.staging.yml exec -T app bash << 'ENDCONTAINER'

cd /app

echo "🔍 Verificando estado actual de migraciones..."
alembic current

echo ""
echo "📋 Historial de migraciones:"
alembic history | head -20

echo ""
echo "🔄 Ejecutando migración create_cufe_records..."
alembic upgrade create_cufe_records

echo ""
echo "✅ Verificando migración aplicada..."
alembic current

echo ""
echo "🔍 Verificando que la tabla existe..."
python3 << 'ENDPYTHON'
import sys
sys.path.insert(0, '/app/src')
from app.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()

if 'cufe_records' in tables:
    print("✅ Tabla 'cufe_records' creada exitosamente")
    columns = inspector.get_columns('cufe_records')
    print(f"   Columnas: {[c['name'] for c in columns]}")
else:
    print("❌ ERROR: Tabla 'cufe_records' NO existe")
    print(f"   Tablas disponibles: {tables}")
ENDPYTHON

ENDCONTAINER

echo ""
echo "🔄 Reiniciando servicios para aplicar cambios..."
docker-compose -f docker-compose.staging.yml restart app

echo ""
echo "✅ Migración completada"

ENDSSH

echo ""
echo "=========================================================="
echo "✅ Proceso completado"
echo ""
echo "Ahora puedes:"
echo "1. Ir a https://staging.jemavi.co/invoices"
echo "2. Hacer clic en el tab 'CUFE'"
echo "3. Agregar códigos CUFE sin errores"
