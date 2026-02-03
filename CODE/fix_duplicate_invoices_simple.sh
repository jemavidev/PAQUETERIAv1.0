#!/bin/bash
# Script simple para verificar y limpiar facturas duplicadas

echo "🔍 Verificando facturas duplicadas..."
echo ""

# Conectar a la base de datos y verificar duplicados
docker-compose exec db psql -U paquetex_user -d paquetex_db -c "
SELECT cufe, COUNT(*) as count
FROM invoices_v2
GROUP BY cufe
HAVING COUNT(*) > 1
ORDER BY count DESC
LIMIT 10;
"

echo ""
echo "¿Deseas eliminar los duplicados? (s/n)"
read -r response

if [[ "$response" == "s" || "$response" == "S" ]]; then
    echo "🧹 Eliminando duplicados (manteniendo el más reciente)..."
    
    docker-compose exec db psql -U paquetex_user -d paquetex_db -c "
    DELETE FROM invoices_v2
    WHERE id NOT IN (
        SELECT MAX(id)
        FROM invoices_v2
        GROUP BY cufe
    );
    "
    
    echo ""
    echo "✅ Duplicados eliminados"
    echo ""
    echo "📊 Verificando resultado..."
    
    docker-compose exec db psql -U paquetex_user -d paquetex_db -c "
    SELECT COUNT(*) as total_facturas FROM invoices_v2;
    "
    
    docker-compose exec db psql -U paquetex_user -d paquetex_db -c "
    SELECT cufe, COUNT(*) as count
    FROM invoices_v2
    GROUP BY cufe
    HAVING COUNT(*) > 1;
    "
    
    echo ""
    echo "✅ Proceso completado"
else
    echo "❌ Operación cancelada"
fi
