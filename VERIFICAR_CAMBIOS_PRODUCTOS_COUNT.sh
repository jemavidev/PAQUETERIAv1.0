#!/bin/bash

echo "================================================================================"
echo "VERIFICACIÓN DE CAMBIOS - Conteo de Productos en Estado"
echo "================================================================================"
echo ""

echo "✅ 1. Verificando cambios en el backend (invoices_v2_routes.py)..."
echo ""
if grep -q "productos_count: Optional\[int\] = None" CODE/src/app/routes/invoices_v2_routes.py; then
    echo "   ✓ Schema InvoiceResponse actualizado con campo productos_count"
else
    echo "   ✗ ERROR: Campo productos_count no encontrado en schema"
fi

if grep -q "cufes_to_count = \[inv.cufe for inv in invoices if inv.estado in \['completo', 'validado'\]\]" CODE/src/app/routes/invoices_v2_routes.py; then
    echo "   ✓ Lógica de conteo implementada en endpoint /facturas"
else
    echo "   ✗ ERROR: Lógica de conteo no encontrada"
fi

if grep -q "productos_count.get(invoice.cufe, 0) if invoice.estado in \['completo', 'validado'\] else None" CODE/src/app/routes/invoices_v2_routes.py; then
    echo "   ✓ Asignación condicional de productos_count implementada"
else
    echo "   ✗ ERROR: Asignación condicional no encontrada"
fi

echo ""
echo "✅ 2. Verificando cambios en el frontend - Tab FACTURAS..."
echo ""
if grep -q "invoice.productos_count !== null && invoice.productos_count !== undefined" CODE/src/templates/invoices_v2/facturas.html; then
    echo "   ✓ Renderizado de conteo de productos implementado en facturas.html"
else
    echo "   ✗ ERROR: Renderizado de conteo no encontrado en facturas.html"
fi

if grep -q "prod\." CODE/src/templates/invoices_v2/facturas.html; then
    echo "   ✓ Texto 'prod.' encontrado en template de facturas"
else
    echo "   ✗ ERROR: Texto 'prod.' no encontrado"
fi

echo ""
echo "✅ 3. Verificando cambios en el frontend - Tab CUFE..."
echo ""
if grep -q "invoice.productos_count !== null && invoice.productos_count !== undefined" CODE/src/templates/invoices_v2/cufe.html; then
    echo "   ✓ Renderizado de conteo de productos implementado en cufe.html"
else
    echo "   ✗ ERROR: Renderizado de conteo no encontrado en cufe.html"
fi

if grep -q "prod\." CODE/src/templates/invoices_v2/cufe.html; then
    echo "   ✓ Texto 'prod.' encontrado en template de CUFE"
else
    echo "   ✗ ERROR: Texto 'prod.' no encontrado"
fi

echo ""
echo "================================================================================"
echo "RESUMEN DE ARCHIVOS MODIFICADOS"
echo "================================================================================"
echo ""
echo "Backend:"
echo "  • CODE/src/app/routes/invoices_v2_routes.py"
echo ""
echo "Frontend:"
echo "  • CODE/src/templates/invoices_v2/facturas.html"
echo "  • CODE/src/templates/invoices_v2/cufe.html"
echo ""
echo "Documentación:"
echo "  • CONTEO_PRODUCTOS_IMPLEMENTADO.md"
echo "  • test_productos_count_feature.py"
echo ""
echo "================================================================================"
echo "PRÓXIMOS PASOS"
echo "================================================================================"
echo ""
echo "1. Reiniciar el servidor de desarrollo:"
echo "   cd CODE"
echo "   ./start_server.sh"
echo ""
echo "2. Abrir el navegador en:"
echo "   http://localhost:8000/invoices/facturas"
echo "   http://localhost:8000/invoices/cufe"
echo ""
echo "3. Verificar que las facturas con estado 'Completo' o 'Validado' muestren:"
echo "   🟢 X prod.  (donde X es la cantidad de productos)"
echo ""
echo "4. Verificar que otros estados solo muestren el círculo de color"
echo ""
echo "================================================================================"
echo "✅ VERIFICACIÓN COMPLETADA"
echo "================================================================================"
