#!/bin/bash
# Script para eliminar TODAS las facturas de la base de datos
# ADVERTENCIA: Esta operación es IRREVERSIBLE

echo "================================================================================"
echo "⚠️  ADVERTENCIA: ELIMINACIÓN TOTAL DE FACTURAS"
echo "================================================================================"
echo ""
echo "Esta operación eliminará:"
echo "  • Todas las facturas de la base de datos"
echo "  • Todos los productos asociados"
echo ""
echo "⚠️  ESTA OPERACIÓN ES IRREVERSIBLE ⚠️"
echo ""
echo "NOTA: Los archivos en S3 deben eliminarse manualmente"
echo ""
echo "================================================================================"
echo ""

# Confirmación 1
read -p "¿Estás seguro de que quieres continuar? (escribe 'SI' en mayúsculas): " respuesta1
if [ "$respuesta1" != "SI" ]; then
    echo ""
    echo "❌ Operación cancelada"
    exit 0
fi

# Confirmación 2
read -p "¿REALMENTE quieres eliminar TODAS las facturas? (escribe 'ELIMINAR TODO'): " respuesta2
if [ "$respuesta2" != "ELIMINAR TODO" ]; then
    echo ""
    echo "❌ Operación cancelada"
    exit 0
fi

echo ""
echo "🔄 Iniciando eliminación..."
echo ""

# Verificar si estamos en Docker o local
if [ -f "/.dockerenv" ]; then
    # Estamos en Docker
    DB_HOST="${DB_HOST:-db}"
    DB_NAME="${DB_NAME:-paquetex_db}"
    DB_USER="${DB_USER:-paquetex_user}"
    DB_PASSWORD="${DB_PASSWORD:-paquetex_password}"
    
    # Ejecutar SQL
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME << EOF
-- Mostrar estadísticas antes
SELECT 'ANTES DE ELIMINAR:' as info;
SELECT COUNT(*) as total_facturas FROM invoices_v2;
SELECT COUNT(*) as total_productos FROM invoice_products_v2;

-- Eliminar productos
DELETE FROM invoice_products_v2;

-- Eliminar facturas
DELETE FROM invoices_v2;

-- Mostrar estadísticas después
SELECT 'DESPUÉS DE ELIMINAR:' as info;
SELECT COUNT(*) as facturas_restantes FROM invoices_v2;
SELECT COUNT(*) as productos_restantes FROM invoice_products_v2;
EOF

else
    # Estamos en local, usar docker-compose
    echo "📦 Ejecutando desde docker-compose..."
    
    docker-compose exec db psql -U paquetex_user -d paquetex_db << EOF
-- Mostrar estadísticas antes
SELECT 'ANTES DE ELIMINAR:' as info;
SELECT COUNT(*) as total_facturas FROM invoices_v2;
SELECT COUNT(*) as total_productos FROM invoice_products_v2;

-- Eliminar productos
DELETE FROM invoice_products_v2;

-- Eliminar facturas
DELETE FROM invoices_v2;

-- Mostrar estadísticas después
SELECT 'DESPUÉS DE ELIMINAR:' as info;
SELECT COUNT(*) as facturas_restantes FROM invoices_v2;
SELECT COUNT(*) as productos_restantes FROM invoice_products_v2;
EOF

fi

echo ""
echo "================================================================================"
echo "✅ ELIMINACIÓN COMPLETADA"
echo "================================================================================"
echo ""
echo "⚠️  IMPORTANTE: Los archivos en S3 NO fueron eliminados"
echo "   Para eliminar archivos de S3, ejecuta:"
echo "   python3 eliminar_todas_facturas.py"
echo ""
