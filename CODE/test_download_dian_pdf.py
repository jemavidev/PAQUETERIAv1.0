#!/usr/bin/env python3
"""
Script de prueba para verificar la descarga de archivos PDF DIAN
"""
import requests
import sys

BASE_URL = "http://localhost:8000"

def test_download_dian_pdf(cufe: str):
    """
    Prueba la descarga de un archivo PDF DIAN
    """
    print(f"\n{'='*80}")
    print(f"🧪 PRUEBA: Descarga de PDF DIAN")
    print(f"{'='*80}\n")
    
    # 1. Obtener URL de descarga del archivo DIAN
    print(f"📥 Solicitando URL de descarga para CUFE: {cufe[:16]}...")
    url = f"{BASE_URL}/api/v2/invoices/facturas/{cufe}/download-url?file_type=dian"
    
    try:
        response = requests.get(url)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ URL obtenida exitosamente")
            print(f"   📄 Filename: {data.get('filename')}")
            print(f"   🔗 URL: {data.get('download_url')[:100]}...")
            
            # 2. Verificar que la URL sea accesible
            print(f"\n🔍 Verificando accesibilidad de la URL...")
            download_response = requests.head(data.get('download_url'))
            print(f"   Status: {download_response.status_code}")
            
            if download_response.status_code == 200:
                print(f"   ✅ URL accesible")
                content_length = download_response.headers.get('Content-Length', 'Unknown')
                print(f"   📦 Tamaño: {content_length} bytes")
            else:
                print(f"   ❌ URL no accesible")
                
        elif response.status_code == 404:
            error = response.json()
            print(f"   ⚠️ {error.get('detail')}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n{'='*80}\n")

def test_download_proveedor_pdf(cufe: str):
    """
    Prueba la descarga de un archivo PDF del proveedor
    """
    print(f"\n{'='*80}")
    print(f"🧪 PRUEBA: Descarga de PDF Proveedor")
    print(f"{'='*80}\n")
    
    # 1. Obtener URL de descarga del archivo del proveedor
    print(f"📥 Solicitando URL de descarga para CUFE: {cufe[:16]}...")
    url = f"{BASE_URL}/api/v2/invoices/facturas/{cufe}/download-url?file_type=proveedor"
    
    try:
        response = requests.get(url)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ URL obtenida exitosamente")
            print(f"   📄 Filename: {data.get('filename')}")
            print(f"   🔗 URL: {data.get('download_url')[:100]}...")
        elif response.status_code == 404:
            error = response.json()
            print(f"   ⚠️ {error.get('detail')}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python test_download_dian_pdf.py <CUFE>")
        sys.exit(1)
    
    cufe = sys.argv[1]
    
    # Probar descarga de archivo DIAN
    test_download_dian_pdf(cufe)
    
    # Probar descarga de archivo proveedor
    test_download_proveedor_pdf(cufe)
