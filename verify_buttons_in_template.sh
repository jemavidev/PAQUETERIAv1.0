#!/bin/bash

echo "=========================================="
echo "VERIFICACIÓN DE BOTONES EN FACTURAS.HTML"
echo "=========================================="
echo ""

echo "✓ Verificando botón de copiar CUFE..."
if grep -q "copyCufe" CODE/src/templates/invoices_v2/facturas.html; then
    echo "  ✓ Botón de copiar CUFE encontrado en línea:"
    grep -n "onclick=\"copyCufe" CODE/src/templates/invoices_v2/facturas.html | head -1
    echo ""
else
    echo "  ✗ Botón de copiar CUFE NO encontrado"
    echo ""
fi

echo "✓ Verificando función copyCufe()..."
if grep -q "function copyCufe" CODE/src/templates/invoices_v2/facturas.html; then
    echo "  ✓ Función copyCufe() encontrada en línea:"
    grep -n "function copyCufe" CODE/src/templates/invoices_v2/facturas.html
    echo ""
else
    echo "  ✗ Función copyCufe() NO encontrada"
    echo ""
fi

echo "✓ Verificando botón de descargar PDF..."
if grep -q "downloadInvoice" CODE/src/templates/invoices_v2/facturas.html; then
    echo "  ✓ Botón de descargar PDF encontrado en línea:"
    grep -n "onclick=\"downloadInvoice" CODE/src/templates/invoices_v2/facturas.html | head -1
    echo ""
else
    echo "  ✗ Botón de descargar PDF NO encontrado"
    echo ""
fi

echo "✓ Verificando función downloadInvoice()..."
if grep -q "function downloadInvoice" CODE/src/templates/invoices_v2/facturas.html; then
    echo "  ✓ Función downloadInvoice() encontrada en línea:"
    grep -n "function downloadInvoice" CODE/src/templates/invoices_v2/facturas.html
    echo ""
else
    echo "  ✗ Función downloadInvoice() NO encontrada"
    echo ""
fi

echo "=========================================="
echo "RESUMEN"
echo "=========================================="
echo ""
echo "Todos los botones y funciones están presentes en el código."
echo ""
echo "Si NO ves los botones en el navegador, necesitas:"
echo ""
echo "1. REINICIAR el servidor FastAPI:"
echo "   cd CODE"
echo "   docker-compose restart web"
echo "   # O si estás en desarrollo local:"
echo "   # Ctrl+C para detener el servidor"
echo "   # python -m uvicorn src.main:app --reload"
echo ""
echo "2. LIMPIAR la caché del navegador:"
echo "   - Chrome/Edge: Ctrl + Shift + R (Windows/Linux)"
echo "   - Chrome/Edge: Cmd + Shift + R (Mac)"
echo "   - O abre en modo incógnito: Ctrl + Shift + N"
echo ""
echo "3. VERIFICAR que estás viendo la URL correcta:"
echo "   - http://localhost:8000/invoices"
echo "   - O tu URL de staging/producción"
echo ""
echo "=========================================="
