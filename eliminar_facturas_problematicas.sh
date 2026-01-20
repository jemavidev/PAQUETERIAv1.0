#!/bin/bash
# Script para eliminar facturas problemáticas directamente de la base de datos

CUFE1="468eb25da77268708c18f8c5020bd9d61dd135582f387a9d6583a6c63b0ab8ce4eac4dd524878b39a8296181f88d2816"
CUFE2="88f565e6a165010edd2680ea0f37c2453f3d2a11e2b58fcff298241c760f260cafef0dbed0b6214df2e67a3895ea6132"

echo "=========================================="
echo "ELIMINANDO FACTURAS PROBLEMÁTICAS"
echo "=========================================="

# Conectar a la base de datos y eliminar
docker compose -f docker-compose.staging.yml exec -T db psql -U paqueteria_user -d paqueteria_db << EOF

-- Factura 1
DO \$\$
DECLARE
    invoice_id_var INTEGER;
BEGIN
    -- Buscar ID de la factura
    SELECT id INTO invoice_id_var FROM invoices WHERE cufe_cude = '$CUFE1';
    
    IF invoice_id_var IS NOT NULL THEN
        RAISE NOTICE 'Eliminando factura ID: %', invoice_id_var;
        
        -- Eliminar items
        DELETE FROM invoice_items WHERE invoice_id = invoice_id_var;
        RAISE NOTICE '  → Items eliminados';
        
        -- Eliminar irregularidades
        DELETE FROM invoice_irregularities WHERE invoice_id = invoice_id_var;
        RAISE NOTICE '  → Irregularidades eliminadas';
        
        -- Eliminar factura
        DELETE FROM invoices WHERE id = invoice_id_var;
        RAISE NOTICE '  → Factura eliminada';
    ELSE
        RAISE NOTICE 'No se encontró factura con CUFE: $CUFE1';
    END IF;
END \$\$;

-- Factura 2
DO \$\$
DECLARE
    invoice_id_var INTEGER;
BEGIN
    -- Buscar ID de la factura
    SELECT id INTO invoice_id_var FROM invoices WHERE cufe_cude = '$CUFE2';
    
    IF invoice_id_var IS NOT NULL THEN
        RAISE NOTICE 'Eliminando factura ID: %', invoice_id_var;
        
        -- Eliminar items
        DELETE FROM invoice_items WHERE invoice_id = invoice_id_var;
        RAISE NOTICE '  → Items eliminados';
        
        -- Eliminar irregularidades
        DELETE FROM invoice_irregularities WHERE invoice_id = invoice_id_var;
        RAISE NOTICE '  → Irregularidades eliminadas';
        
        -- Eliminar factura
        DELETE FROM invoices WHERE id = invoice_id_var;
        RAISE NOTICE '  → Factura eliminada';
    ELSE
        RAISE NOTICE 'No se encontró factura con CUFE: $CUFE2';
    END IF;
END \$\$;

-- Eliminar registros CUFE si existen
DELETE FROM cufe_records WHERE cufe = '$CUFE1';
DELETE FROM cufe_records WHERE cufe = '$CUFE2';

-- Verificar que se eliminaron
SELECT 
    CASE 
        WHEN COUNT(*) = 0 THEN '✅ Todas las facturas fueron eliminadas correctamente'
        ELSE '❌ Aún quedan ' || COUNT(*) || ' facturas'
    END as resultado
FROM invoices 
WHERE cufe_cude IN ('$CUFE1', '$CUFE2');

EOF

echo ""
echo "=========================================="
echo "✅ LIMPIEZA COMPLETADA"
echo "=========================================="
echo "Ahora puedes subir los PDFs nuevamente"
