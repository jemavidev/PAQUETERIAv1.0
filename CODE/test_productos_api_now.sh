#!/bin/bash

echo "🧪 Probando endpoint /api/v2/invoices/productos"
echo "================================================"
echo ""

# Test 1: Sin autenticación (debería retornar 401 JSON)
echo "📝 Test 1: Sin autenticación"
curl -s -w "\nStatus: %{http_code}\n" \
  "http://localhost:8000/api/v2/invoices/productos?skip=0&limit=10" \
  | head -20

echo ""
echo "================================================"
echo ""

# Test 2: Con cookies de sesión (si existen)
echo "📝 Test 2: Con cookies (si existen)"
curl -s -w "\nStatus: %{http_code}\n" \
  -b ~/.paquetex_cookies.txt \
  "http://localhost:8000/api/v2/invoices/productos?skip=0&limit=10" \
  | head -20

echo ""
echo "================================================"
echo "✅ Tests completados"
