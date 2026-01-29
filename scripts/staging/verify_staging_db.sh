#!/bin/bash
# Script para verificar la base de datos staging usando Docker

echo "================================================================================"
echo "🔍 VERIFICACIÓN DE BASE DE DATOS STAGING"
echo "================================================================================"
echo ""

# Cargar variables de entorno
if [ -f .env.staging ]; then
    source .env.staging
    echo "✅ Variables cargadas desde .env.staging"
else
    echo "❌ Error: .env.staging no encontrado"
    exit 1
fi

echo ""
echo "📡 Host: $POSTGRES_HOST"
echo "👤 Usuario: $POSTGRES_USER"
echo "🗄️  Base de datos: $POSTGRES_DB"
echo ""
echo "================================================================================"
echo ""

# Función para ejecutar comandos SQL
run_sql() {
    docker run --rm \
        -e PGPASSWORD="$POSTGRES_PASSWORD" \
        postgres:15-alpine \
        psql -h "$POSTGRES_HOST" \
              -p "$POSTGRES_PORT" \
              -U "$POSTGRES_USER" \
              -d "$1" \
              -c "$2" \
              -t
}

# Verificar conexión al servidor
echo "📌 Paso 1: Verificando conexión al servidor PostgreSQL..."
if run_sql "postgres" "SELECT 1" > /dev/null 2>&1; then
    echo "✅ Conexión exitosa"
else
    echo "❌ Error: No se pudo conectar al servidor"
    exit 1
fi
echo ""

# Verificar si la base de datos staging existe
echo "📌 Paso 2: Verificando si $POSTGRES_DB existe..."
DB_EXISTS=$(run_sql "postgres" "SELECT 1 FROM pg_database WHERE datname='$POSTGRES_DB'" 2>/dev/null | tr -d ' ')

if [ "$DB_EXISTS" = "1" ]; then
    echo "✅ La base de datos $POSTGRES_DB existe"
else
    echo "⚠️  La base de datos $POSTGRES_DB NO existe"
    echo ""
    read -p "¿Deseas crearla? (s/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        echo "📝 Creando base de datos $POSTGRES_DB..."
        run_sql "postgres" "CREATE DATABASE $POSTGRES_DB OWNER $POSTGRES_USER" > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo "✅ Base de datos $POSTGRES_DB creada exitosamente"
        else
            echo "❌ Error al crear la base de datos"
            exit 1
        fi
    else
        echo "❌ Operación cancelada"
        exit 1
    fi
fi
echo ""

# Listar bases de datos del proyecto
echo "📌 Paso 3: Listando bases de datos del proyecto..."
echo ""
echo "Base de Datos              Tamaño          Conexiones"
echo "--------------------------------------------------------------------------------"

run_sql "postgres" "
SELECT 
    datname || '  ' || 
    pg_size_pretty(pg_database_size(datname)) || '  ' ||
    (SELECT count(*) FROM pg_stat_activity WHERE datname = d.datname)::text
FROM pg_database d
WHERE datname IN ('paqueteria_v4', 'paqueteria_staging')
ORDER BY datname
" 2>/dev/null | while read line; do
    if [[ $line == *"paqueteria_staging"* ]]; then
        echo "🟢 $line"
    elif [[ $line == *"paqueteria_v4"* ]]; then
        echo "🔵 $line"
    else
        echo "   $line"
    fi
done

echo ""

# Verificar esquema de staging
echo "📌 Paso 4: Verificando esquema de $POSTGRES_DB..."
TABLE_COUNT=$(run_sql "$POSTGRES_DB" "
SELECT count(*) 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_type = 'BASE TABLE'
" 2>/dev/null | tr -d ' ')

echo "📊 Tablas encontradas: $TABLE_COUNT"
echo ""

if [ "$TABLE_COUNT" = "0" ]; then
    echo "⚠️  La base de datos está VACÍA (sin tablas)"
    echo ""
    echo "📝 OPCIONES:"
    echo "   1. Ejecutar migraciones de Alembic:"
    echo "      cd CODE && alembic upgrade head"
    echo ""
    echo "   2. Copiar esquema desde producción:"
    echo "      bash scripts/staging/copy_schema_from_prod.sh"
    echo ""
else
    echo "✅ La base de datos tiene tablas"
    echo ""
    
    # Listar tablas principales
    echo "📋 Tablas principales:"
    echo ""
    run_sql "$POSTGRES_DB" "
    SELECT '   ' || table_name || '  (' || 
           pg_size_pretty(pg_total_relation_size(quote_ident(table_name)::regclass)) || ')'
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    AND table_name IN ('users', 'customers', 'packages', 'invoices', 'supplier_invoices', 'products')
    ORDER BY table_name
    " 2>/dev/null
    
    echo ""
    
    # Contar registros en tablas principales
    echo "📊 Registros en tablas principales:"
    echo ""
    echo "Tabla                          Registros"
    echo "--------------------------------------------------------------------------------"
    
    for table in users customers packages invoices supplier_invoices products; do
        COUNT=$(run_sql "$POSTGRES_DB" "SELECT count(*) FROM $table" 2>/dev/null | tr -d ' ')
        if [ -n "$COUNT" ]; then
            printf "   %-30s %10s\n" "$table" "$COUNT"
        else
            printf "   %-30s %10s\n" "$table" "N/A"
        fi
    done
fi

echo ""
echo "================================================================================"
echo "✅ VERIFICACIÓN COMPLETADA"
echo "================================================================================"
echo ""
echo "🚀 PRÓXIMOS PASOS:"
echo ""

if [ "$TABLE_COUNT" = "0" ]; then
    echo "   1. Inicializar esquema (elegir una opción):"
    echo "      • Migraciones: cd CODE && alembic upgrade head"
    echo "      • Copiar de prod: bash scripts/staging/copy_schema_from_prod.sh"
    echo ""
    echo "   2. Levantar servidor staging:"
    echo "      docker-compose -f docker-compose.staging.yml up -d"
else
    echo "   1. Levantar servidor staging:"
    echo "      docker-compose -f docker-compose.staging.yml up -d"
    echo ""
    echo "   2. Verificar que funciona:"
    echo "      curl http://localhost:8001/health"
    echo ""
    echo "   3. Ver logs:"
    echo "      docker-compose -f docker-compose.staging.yml logs -f app"
fi

echo ""
