#!/bin/bash
# Test que el endpoint de productos retorna el formato correcto

echo "🧪 Probando formato de respuesta del endpoint /api/v2/invoices/productos"
echo ""

# Hacer request desde dentro del container (sin autenticación necesaria en localhost)
ssh staging 'docker exec paqueteria_staging_app python3 -c "
import requests
import json

try:
    response = requests.get(\"http://127.0.0.1:8000/api/v2/invoices/productos?skip=0&limit=10\")
    print(f\"Status Code: {response.status_code}\")
    print(f\"Content-Type: {response.headers.get('Content-Type')}\")
    print()
    
    data = response.json()
    print(f\"Response Type: {type(data)}\")
    
    if isinstance(data, dict):
        print(f\"✅ Response is a DICT (correct!)\")
        print(f\"Keys: {list(data.keys())}\")
        print(f\"Total items: {data.get('total', 'N/A')}\")
        print(f\"Items count: {len(data.get('items', []))}\")
        print(f\"Page: {data.get('page', 'N/A')}\")
        print(f\"Total pages: {data.get('total_pages', 'N/A')}\")
    elif isinstance(data, list):
        print(f\"❌ Response is an ARRAY (incorrect!)\")
        print(f\"Array length: {len(data)}\")
    else:
        print(f\"❌ Response is {type(data)} (unexpected!)\")
        
except Exception as e:
    print(f\"❌ Error: {e}\")
"'

echo ""
echo "✅ Test completado"
