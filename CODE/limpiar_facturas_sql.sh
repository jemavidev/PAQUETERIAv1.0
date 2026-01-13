#!/bin/bash
# Script para limpiar todas las facturas usando SQL directo
# ADVERTENCIA: Esta operación es IRREVERSIBLE

echo "=========================================="
echo "LIMPIEZA COMPLETA DE FACTURAS (SQL)"
echo "=========================================="
echo ""
echo "⚠️  ADVERTENCIA: Esta operación eliminará:"
echo "   - Todas las facturas"
echo "   - Todos los items de facturas"
echo "   - Todas las irregularidades"
echo "   - Todos los proveedores"
echo "   - Todos los archivos rechazados"
echo "   - Todos los archivos PDF"
echo ""
echo "⚠️  ESTA OPERACIÓN ES IRREVERSIBLE"
echo ""

read -p "¿Estás seguro de continuar? (escribe SI para confirmar): " confirmacion

if [ "$confirmacion" != "SI" ]; then
    echo ""
    echo "✗ Operación cancelada"
    exit 0
fi

echo ""
echo "🚀 Iniciando limpieza..."
echo ""

# Obtener credenciales de la base de datos desde .env
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Ejecutar SQL
echo "=== LIMPIEZA DE BASE DE DATOS ==="
echo ""

PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB << EOF
-- Deshabilitar triggers temporalmente para evitar problemas
SET session_replication_role = 'replica';

-- Contar registros antes de eliminar
SELECT 'Irregularidades a eliminar: ' || COUNT(*) FROM invoice_irregularities;
SELECT 'Items a eliminar: ' || COUNT(*) FROM invoice_items;
SELECT 'Facturas a eliminar: ' || COUNT(*) FROM invoices;
SELECT 'Proveedores a eliminar: ' || COUNT(*) FROM suppliers;
SELECT 'Archivos rechazados a eliminar: ' || COUNT(*) FROM invoice_rejected_files;

-- Eliminar en orden (respetando foreign keys)
DELETE FROM invoice_irregularities;
DELETE FROM invoice_items;
DELETE FROM invoices;
DELETE FROM suppliers;
DELETE FROM invoice_rejected_files;

-- Resetear secuencias
ALTER SEQUENCE invoice_irregularities_id_seq RESTART WITH 1;
ALTER SEQUENCE invoice_items_id_seq RESTART WITH 1;
ALTER SEQUENCE invoices_id_seq RESTART WITH 1;
ALTER SEQUENCE suppliers_id_seq RESTART WITH 1;
ALTER SEQUENCE invoice_rejected_files_id_seq RESTART WITH 1;

-- Rehabilitar triggers
SET session_replication_role = 'origin';

-- Verificar que todo está limpio
SELECT 'Irregularidades restantes: ' || COUNT(*) FROM invoice_irregularities;
SELECT 'Items restantes: ' || COUNT(*) FROM invoice_items;
SELECT 'Facturas restantes: ' || COUNT(*) FROM invoices;
SELECT 'Proveedores restantes: ' || COUNT(*) FROM suppliers;
SELECT 'Archivos rechazados restantes: ' || COUNT(*) FROM invoice_rejected_files;
EOF

echo ""
echo "✓ Base de datos limpiada"
echo ""

# Limpiar archivos PDF
echo "=== LIMPIEZA DE ARCHIVOS ==="
echo ""

PDF_DIR="/app/src/uploads/invoices"

if [ -d "$PDF_DIR" ]; then
    COUNT=$(find "$PDF_DIR" -name "*.pdf" | wc -l)
    if [ $COUNT -gt 0 ]; then
        rm -f "$PDF_DIR"/*.pdf
        echo "✓ $COUNT archivos PDF eliminados"
    else
        echo "✓ No hay archivos PDF para eliminar"
    fi
else
    echo "✓ Directorio de PDFs no existe"
fi

echo ""
echo "=========================================="
echo "✅ LIMPIEZA COMPLETADA EXITOSAMENTE"
echo "=========================================="
echo ""
echo "Ahora puedes importar las facturas nuevamente"
echo ""
