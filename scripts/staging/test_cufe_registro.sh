#!/bin/bash

CUFE="88f565e6a165010edd2680ea0f37c2453f3d2a11e2b58fcff298241c760f260cafef0dbed0b6214df2e67a3895ea6132"

echo "🧪 Probando registro de CUFE en staging..."
echo "CUFE: $CUFE"
echo ""

# Primero necesitamos obtener las cookies de sesión
# Simulando que ya estamos autenticados

curl -X POST https://staging.jemavi.co/invoices/api/cufe/register \
  -H "Content-Type: application/json" \
  -d "{\"cufe\": \"$CUFE\"}" \
  -v 2>&1 | grep -E "HTTP|success|error|message"
