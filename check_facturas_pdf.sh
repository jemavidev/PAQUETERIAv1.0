#!/bin/bash

echo "=========================================="
echo "DIAGNÓSTICO: Botón de Descarga PDF"
echo "=========================================="
echo ""

# Verificar si el botón está en el código
echo "1. Verificando código del botón..."
if grep -q "downloadInvoice" CODE/src/templates/invoices_v2/facturas.html; then
    echo "   ✅ Botón de descarga encontrado en el código"
else
    echo "   ❌ Botón de descarga NO encontrado"
fi

# Verificar función JavaScript
if grep -q "function downloadInvoice" CODE/src/templates/invoices_v2/facturas.html; then
    echo "   ✅ Función downloadInvoice() encontrada"
else
    echo "   ❌ Función downloadInvoice() NO encontrada"
fi

echo ""
echo "2. Verificando configuración de AWS S3..."
if grep -q "AWS_ACCESS_KEY_ID" CODE/.env; then
    echo "   ✅ AWS_ACCESS_KEY_ID configurado"
else
    echo "   ❌ AWS_ACCESS_KEY_ID NO configurado"
fi

if grep -q "AWS_S3_BUCKET" CODE/.env; then
    BUCKET=$(grep "AWS_S3_BUCKET" CODE/.env | cut -d'=' -f2)
    echo "   ✅ AWS_S3_BUCKET configurado: $BUCKET"
else
    echo "   ❌ AWS_S3_BUCKET NO configurado"
fi

echo ""
echo "3. Posibles causas del problema:"
echo "   a) Las facturas NO tienen archivo_proveedor_url en la BD"
echo "   b) El servicio S3 falló al subir los archivos"
echo "   c) Las facturas fueron creadas antes de implementar S3"
echo ""
echo "=========================================="
echo "SOLUCIÓN RECOMENDADA"
echo "=========================================="
echo ""
echo "Para verificar si las facturas tienen PDF:"
echo ""
echo "1. Abre la consola del navegador (F12)"
echo "2. Ve a la pestaña 'Network'"
echo "3. Recarga la página /invoices"
echo "4. Busca la petición a '/api/v2/invoices/facturas'"
echo "5. Mira la respuesta JSON"
echo "6. Verifica si 'archivo_proveedor_url' tiene valor o es null"
echo ""
echo "Si archivo_proveedor_url es NULL:"
echo "  → Re-sube las facturas usando el modal de carga"
echo "  → Los nuevos archivos se subirán a S3 automáticamente"
echo ""
echo "Si archivo_proveedor_url tiene valor pero no descarga:"
echo "  → Verifica que la URL de S3 sea accesible"
echo "  → Revisa los permisos del bucket S3"
echo "  → Mira la consola del navegador para ver errores"
echo ""
echo "=========================================="
