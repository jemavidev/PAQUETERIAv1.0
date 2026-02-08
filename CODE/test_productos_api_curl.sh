#!/bin/bash
# Test the productos API endpoint directly

echo "=========================================="
echo "TESTING PRODUCTOS API ENDPOINT"
echo "=========================================="
echo ""

# Test without authentication
echo "1. Testing WITHOUT authentication:"
curl -s "http://localhost:8000/api/v2/invoices/productos?skip=0&limit=10" | python -m json.tool | head -50

echo ""
echo ""
echo "2. Testing WITH authentication (if cookies exist):"
curl -s -b cookies.txt "http://localhost:8000/api/v2/invoices/productos?skip=0&limit=10" | python -m json.tool | head -50

echo ""
echo ""
echo "=========================================="
echo "TEST COMPLETED"
echo "=========================================="
