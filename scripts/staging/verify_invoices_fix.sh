#!/bin/bash
# Script para verificar el fix de carga de facturas

echo "╔════════════════════════════════════════════════════════╗"
echo "║     VERIFICACIÓN FIX - CARGA DE FACTURAS              ║"
echo "╚════════════════════════════════════════════════════════╝"

echo -e "\n1️⃣ Verificando archivo local..."
LOCAL_URL=$(grep -o "fetch('[^']*supplier-invoices/upload'" CODE/src/templates/invoices/_tab_facturas.html | head -1)
echo "   URL en archivo local: $LOCAL_URL"
if echo "$LOCAL_URL" | grep -q "/invoices/api/supplier-invoices/upload"; then
    echo "   ✅ URL correcta en local"
else
    echo "   ❌ URL incorrecta en local"
fi

echo -e "\n2️⃣ Verificando archivo en staging..."
STAGING_URL=$(ssh -o ConnectTimeout=10 staging "grep -o \"fetch('[^']*supplier-invoices/upload'\" /home/ubuntu/paqueteria-staging/CODE/src/templates/invoices/_tab_facturas.html | head -1" 2>&1)
echo "   URL en staging: $STAGING_URL"
if echo "$STAGING_URL" | grep -q "/invoices/api/supplier-invoices/upload"; then
    echo "   ✅ URL correcta en staging"
else
    echo "   ❌ URL incorrecta en staging"
fi

echo -e "\n3️⃣ Verificando endpoint..."
HTTP_CODE=$(ssh -o ConnectTimeout=10 staging 'curl -s -o /dev/null -w "%{http_code}" https://staging.jemavi.co/invoices/api/supplier-invoices/upload' 2>&1)
echo "   HTTP Status: $HTTP_CODE"
if [ "$HTTP_CODE" = "302" ] || [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "405" ]; then
    echo "   ✅ Endpoint existe (requiere autenticación)"
elif [ "$HTTP_CODE" = "404" ]; then
    echo "   ❌ Endpoint no encontrado (404)"
else
    echo "   ⚠️  Status inesperado: $HTTP_CODE"
fi

echo -e "\n4️⃣ Verificando estado del servidor..."
HEALTH=$(ssh -o ConnectTimeout=10 staging 'curl -s https://staging.jemavi.co/health' 2>&1)
if echo "$HEALTH" | grep -q "healthy"; then
    echo "   ✅ Servidor staging funcionando"
    echo "   $HEALTH"
else
    echo "   ❌ Problema con el servidor"
fi

echo -e "\n╔════════════════════════════════════════════════════════╗"
echo "║     VERIFICACIÓN COMPLETADA                           ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "📝 Instrucciones para probar:"
echo "   1. Abre https://staging.jemavi.co/invoices"
echo "   2. Ve al tab 'Facturas'"
echo "   3. Haz clic en 'Subir Facturas'"
echo "   4. Selecciona un archivo PDF"
echo "   5. Verifica que se suba correctamente"
echo ""
