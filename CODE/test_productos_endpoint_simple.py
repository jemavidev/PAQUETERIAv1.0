#!/usr/bin/env python3
"""
Test simple del endpoint de productos
"""
import requests
import json

# URL del endpoint
url = "http://localhost:8000/api/v2/invoices/productos?skip=0&limit=10"

print("🧪 Probando endpoint de productos...")
print(f"URL: {url}\n")

try:
    # Hacer request SIN autenticación
    response = requests.get(url)
    
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"\nPrimeros 500 caracteres de la respuesta:")
    print(response.text[:500])
    print("\n" + "="*80)
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("\n✅ Respuesta JSON válida:")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
        except:
            print("\n❌ La respuesta NO es JSON válido")
            print("Es HTML:", "<html" in response.text.lower())
    elif response.status_code == 401:
        print("\n⚠️ Requiere autenticación (401)")
        print("Esto es esperado si el endpoint está protegido")
    else:
        print(f"\n❌ Error inesperado: {response.status_code}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
