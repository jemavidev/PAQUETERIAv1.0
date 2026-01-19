#!/bin/bash
# Script para probar la carga de facturas en staging

echo "╔════════════════════════════════════════════════════════╗"
echo "║     TEST: CARGA DE FACTURAS EN STAGING                ║"
echo "╚════════════════════════════════════════════════════════╝"

# Verificar que existe un PDF de prueba
if [ ! -f "CUFE/FACTURAS/FE15778.pdf" ]; then
    echo "❌ No se encontró archivo de prueba"
    exit 1
fi

echo -e "\n📤 Subiendo archivo de prueba a staging..."

# Obtener cookies de sesión (necesitas estar autenticado)
echo "⚠️  NOTA: Este test requiere que tengas una sesión activa en staging"
echo "   Abre https://staging.jemavi.co/invoices en tu navegador primero"
echo ""

# Simular la carga
RESPONSE=$(curl -s -w "\n%{http_code}" \
  -X POST \
  -F "files=@CUFE/FACTURAS/FE15778.pdf" \
  -H "Cookie: session=YOUR_SESSION_COOKIE" \
  https://staging.jemavi.co/invoices/api/supplier-invoices/upload)

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

echo "📊 Respuesta del servidor:"
echo "   HTTP Status: $HTTP_CODE"
echo "   Body: $BODY"

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "\n✅ Upload exitoso"
else
    echo -e "\n❌ Upload falló"
fi

echo -e "\n📋 Últimos logs del servidor:"
ssh -o ConnectTimeout=10 staging 'docker logs --tail 10 paqueteria_staging_app 2>&1 | grep -E "supplier-invoices|upload|ERROR"'

echo -e "\n╔════════════════════════════════════════════════════════╗"
echo "║     TEST COMPLETADO                                    ║"
echo "╚════════════════════════════════════════════════════════╝"
