#!/usr/bin/env python3
"""
Script para cargar archivos XML de la DIAN a facturas existentes
Versión corregida - sin campos de trazabilidad
"""
import os
import sys
import requests
from pathlib import Path

# Configuración
API_BASE_URL = "http://localhost:8000"
XML_DIR = "/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE/CUFE-XML"

def cargar_xml(xml_path: str):
    """Carga un archivo XML a su factura correspondiente"""
    filename = Path(xml_path).name
    cufe = filename.replace('.xml', '')
    
    print(f"\n📄 Procesando: {filename}")
    print(f"   CUFE: {cufe[:20]}...")
    
    # Verificar que la factura existe
    try:
        response = requests.get(f"{API_BASE_URL}/api/v2/invoices/{cufe}")
        if response.status_code == 404:
            print(f"   ⚠️  Factura no encontrada en BD, saltando...")
            return False
    except Exception as e:
        print(f"   ❌ Error verificando factura: {e}")
        return False
    
    # Subir XML
    try:
        with open(xml_path, 'rb') as f:
            files = {'file': (filename, f, 'application/xml')}
            response = requests.post(
                f"{API_BASE_URL}/api/v2/invoices/cufe/{cufe}/upload-dian",
                files=files,
                timeout=30
            )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ XML cargado exitosamente")
            print(f"      Emisor: {data.get('dian_emisor_razon_social', 'N/A')}")
            print(f"      Total: ${data.get('dian_total_neto', 0):,.2f}")
            return True
        else:
            error_detail = response.json().get('detail', 'Error desconocido')
            print(f"   ❌ Error: {error_detail}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error subiendo XML: {e}")
        return False

def main():
    """Procesa todos los XMLs en el directorio"""
    print("=" * 80)
    print("🚀 CARGA MASIVA DE ARCHIVOS XML DIAN")
    print("=" * 80)
    
    # Verificar directorio
    if not os.path.exists(XML_DIR):
        print(f"❌ Directorio no encontrado: {XML_DIR}")
        sys.exit(1)
    
    # Obtener lista de XMLs
    xml_files = sorted([f for f in os.listdir(XML_DIR) if f.endswith('.xml')])
    
    if not xml_files:
        print(f"❌ No se encontraron archivos XML en: {XML_DIR}")
        sys.exit(1)
    
    print(f"\n📊 Total de archivos XML encontrados: {len(xml_files)}")
    print(f"📁 Directorio: {XML_DIR}")
    
    # Procesar cada XML
    exitosos = 0
    fallidos = 0
    
    for xml_file in xml_files:
        xml_path = os.path.join(XML_DIR, xml_file)
        if cargar_xml(xml_path):
            exitosos += 1
        else:
            fallidos += 1
    
    # Resumen
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE CARGA")
    print("=" * 80)
    print(f"✅ Exitosos: {exitosos}")
    print(f"❌ Fallidos: {fallidos}")
    print(f"📊 Total: {len(xml_files)}")
    print(f"📈 Tasa de éxito: {(exitosos/len(xml_files)*100):.1f}%")
    print("=" * 80)

if __name__ == "__main__":
    main()
