#!/bin/bash

echo "=========================================="
echo "PRUEBA DIRECTA CON CURL - LIWA.CO"
echo "=========================================="

# Cargar variables de entorno
source .env

echo ""
echo "1. Autenticación..."
AUTH_RESPONSE=$(curl -s -X POST "https://api.liwa.co/v2/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"account\": \"$LIWA_ACCOUNT\",
    \"password\": \"$LIWA_PASSWORD\"
  }")

echo "Respuesta: $AUTH_RESPONSE"

TOKEN=$(echo $AUTH_RESPONSE | grep -o '"token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ Error: No se obtuvo token"
    exit 1
fi

echo "✅ Token obtenido: ${TOKEN:0:20}...${TOKEN: -10}"

echo ""
echo "2. Enviando SMS con Bearer Token..."
SMS_RESPONSE=$(curl -s -X POST "https://api.liwa.co/v2/sms/send" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"to\": \"3044000678\",
    \"message\": \"Prueba desde PAQUETEX EL CLUB\",
    \"from\": \"PAQUETES\"
  }")

echo "Respuesta: $SMS_RESPONSE"

echo ""
echo "3. Enviando SMS con Bearer Token + X-API-Key header..."
SMS_RESPONSE2=$(curl -s -X POST "https://api.liwa.co/v2/sms/send" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-API-Key: $LIWA_API_KEY" \
  -d "{
    \"to\": \"3044000678\",
    \"message\": \"Prueba desde PAQUETEX EL CLUB\",
    \"from\": \"PAQUETES\"
  }")

echo "Respuesta: $SMS_RESPONSE2"

echo ""
echo "=========================================="
