#!/bin/bash

# Script de prueba para verificar nombres personalizados en anuncios

echo "=========================================="
echo "PRUEBA: Nombres Personalizados en Anuncios"
echo "=========================================="
echo ""

# Configuración
BASE_URL="https://staging.jemavi.co"
TEST_PHONE="3001234567"

echo "📱 Teléfono de prueba: $TEST_PHONE"
echo ""

# Paso 1: Buscar cliente existente
echo "1️⃣ Buscando cliente existente..."
CUSTOMER_RESPONSE=$(curl -s "$BASE_URL/api/customers/search-by-phone?phone=$TEST_PHONE")
echo "Respuesta: $CUSTOMER_RESPONSE"
echo ""

# Extraer nombre del cliente
CUSTOMER_NAME=$(echo $CUSTOMER_RESPONSE | grep -o '"full_name":"[^"]*"' | cut -d'"' -f4)
echo "✅ Cliente encontrado: $CUSTOMER_NAME"
echo ""

# Paso 2: Crear anuncio con nombre personalizado
echo "2️⃣ Creando anuncio con nombre personalizado..."
CUSTOM_NAME="$CUSTOMER_NAME - OFICINA PRINCIPAL"
echo "📝 Nombre personalizado: $CUSTOM_NAME"
echo ""

ANNOUNCEMENT_DATA=$(cat <<EOF
{
  "customer_phone": "$TEST_PHONE",
  "customer_name": "$CUSTOM_NAME"
}
EOF
)

ANNOUNCEMENT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/announcements/quick" \
  -H "Content-Type: application/json" \
  -d "$ANNOUNCEMENT_DATA")

echo "Respuesta del anuncio:"
echo "$ANNOUNCEMENT_RESPONSE" | jq '.' 2>/dev/null || echo "$ANNOUNCEMENT_RESPONSE"
echo ""

# Extraer número de guía
GUIDE_NUMBER=$(echo $ANNOUNCEMENT_RESPONSE | grep -o '"guide_number":"[^"]*"' | cut -d'"' -f4)
echo "📦 Número de guía: $GUIDE_NUMBER"
echo ""

# Paso 3: Verificar que el cliente mantiene su nombre original
echo "3️⃣ Verificando que el cliente mantiene su nombre original..."
CUSTOMER_CHECK=$(curl -s "$BASE_URL/api/customers/search-by-phone?phone=$TEST_PHONE")
CUSTOMER_NAME_CHECK=$(echo $CUSTOMER_CHECK | grep -o '"full_name":"[^"]*"' | cut -d'"' -f4)

echo "Nombre del cliente después del anuncio: $CUSTOMER_NAME_CHECK"
echo ""

# Comparación
if [ "$CUSTOMER_NAME" = "$CUSTOMER_NAME_CHECK" ]; then
    echo "✅ ÉXITO: El cliente mantiene su nombre original"
    echo "   Original: $CUSTOMER_NAME"
    echo "   Actual:   $CUSTOMER_NAME_CHECK"
else
    echo "❌ ERROR: El nombre del cliente cambió"
    echo "   Original: $CUSTOMER_NAME"
    echo "   Actual:   $CUSTOMER_NAME_CHECK"
fi

echo ""
echo "=========================================="
echo "RESUMEN:"
echo "- Cliente original: $CUSTOMER_NAME"
echo "- Nombre en anuncio: $CUSTOM_NAME"
echo "- Cliente después: $CUSTOMER_NAME_CHECK"
echo "- Guía generada: $GUIDE_NUMBER"
echo "=========================================="
