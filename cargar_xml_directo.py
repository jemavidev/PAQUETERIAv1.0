#!/usr/bin/env python3
"""
Script para cargar archivos XML de la DIAN directamente a la base de datos
Sin necesidad de autenticación HTTP
"""
import os
import sys
from pathlib import Path

# Agregar el directorio CODE/src al path
sys.path.insert(0, '/home/stk/Documents/GIT/PAQUETEX v1.0/CODE/src')

from app.database import SessionLocal
from app.services.invoice_v2_service import InvoiceV2Service

# Configuración
XML_DIR = "/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE/CUFE-XML"

def cargar_xml(xml_path: str, db):
    """Carga un archivo XML a su factura correspondiente"""
    filename = Path(xml_path).name
    cufe = filename.replace('.xml', '')
    
    print(f"\n📄 Procesando: {filename}")
    print(f"   CUFE: {cufe[:20]}...")
    
    try:
        service = InvoiceV2Service(db)
        
        # Verificar que la factura existe
        invoice = service.get_invoice_by_cufe(cufe)
        if not invoice:
            print(f"   ⚠️  Factura no encontrada en BD, saltando...")
            return False
        
        # Procesar XML
        invoice = service.process_xml_document(cufe, xml_path)
        
        print(f"   ✅ XML cargado exitosamente")
        print(f"      Emisor: {invoice.dian_emisor_razon_social or 'N/A'}")
        print(f"      Total: ${float(invoice.dian_total_neto or 0):,.2f}")
        print(f"      Productos: {len(invoice.productos)}")
        return True
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def main():
    """Procesa todos los XMLs en el directorio"""
    print("=" * 80)
    print("🚀 CARGA MASIVA DE ARCHIVOS XML DIAN (DIRECTO A BD)")
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
    
    # Crear sesión de BD
    db = SessionLocal()
    
    try:
        # Procesar cada XML
        exitosos = 0
        fallidos = 0
        
        for xml_file in xml_files:
            xml_path = os.path.join(XML_DIR, xml_file)
            if cargar_xml(xml_path, db):
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
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
