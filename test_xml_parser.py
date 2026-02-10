#!/usr/bin/env python3
"""
Probar el parser XML con archivos reales
"""
import sys
sys.path.insert(0, '/home/stk/Documents/GIT/PAQUETEX v1.0/CODE/src')

from app.services.xml_parser_service import XMLParserDIAN
from pathlib import Path

xml_dir = Path("/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE/CUFE-XML")
xml_files = list(xml_dir.glob("*.xml"))

print("=" * 80)
print("TEST DEL PARSER XML DIAN")
print("=" * 80)

# Probar con 10 archivos
print(f"\n📊 Probando con 10 archivos XML...")
print("-" * 80)

exitosos = 0
errores = 0

for i, xml_file in enumerate(xml_files[:10], 1):
    print(f"\n[{i}/10] {xml_file.name[:50]}...")
    
    datos = XMLParserDIAN.parse_xml(str(xml_file))
    
    if datos:
        exitosos += 1
        print(f"   ✅ CUFE: {datos['cufe'][:40]}...")
        print(f"   📄 Factura: {datos['numero_factura']}")
        print(f"   📅 Fecha: {datos['fecha_emision']}")
        print(f"   👤 Emisor: {datos['emisor'].get('razon_social', 'N/A')[:40]}")
        print(f"   👥 Cliente: {datos['cliente'].get('razon_social', 'N/A')[:40]}")
        print(f"   📦 Productos: {len(datos['productos'])}")
        print(f"   💰 Total: ${datos['totales'].get('total_pagar', 0):,.2f}")
        
        # Mostrar primer producto
        if datos['productos']:
            prod = datos['productos'][0]
            print(f"\n   📦 Producto 1:")
            print(f"      Código: {prod.get('codigo_producto', 'N/A')}")
            print(f"      Descripción: {prod.get('descripcion', 'N/A')[:50]}...")
            print(f"      Cantidad: {prod.get('cantidad', 0)} {prod.get('unidad_medida', '')}")
            print(f"      Precio: ${prod.get('precio_unitario', 0):,.2f}")
            print(f"      IVA: {prod.get('iva_porcentaje', 0)}%")
            print(f"      Total: ${prod.get('total_item', 0):,.2f}")
    else:
        errores += 1
        print(f"   ❌ Error parseando archivo")

print("\n" + "=" * 80)
print("RESUMEN")
print("=" * 80)
print(f"✅ Exitosos: {exitosos}/10")
print(f"❌ Errores: {errores}/10")

if exitosos == 10:
    print("\n🎉 ¡PARSER XML FUNCIONANDO PERFECTAMENTE!")
else:
    print(f"\n⚠️ Hay {errores} archivos con problemas")

# Comparar XML vs PDF para un archivo
print("\n" + "=" * 80)
print("COMPARACIÓN XML vs PDF")
print("=" * 80)

# Usar el archivo problemático que sabemos tiene 2 productos
cufe_test = "90586381def1342a38806c310801a43659405240dcd445e0d640367591143dd4806cf6fca1ea21fb03b2ea47c62264a2"
xml_path = xml_dir / f"{cufe_test}.xml"
pdf_path = xml_dir / f"{cufe_test}.pdf"

if xml_path.exists():
    print(f"\n📄 Archivo: {cufe_test[:40]}...")
    
    # Parsear XML
    datos_xml = XMLParserDIAN.parse_xml(str(xml_path))
    
    if datos_xml:
        print(f"\n✅ XML Parser:")
        print(f"   Productos: {len(datos_xml['productos'])}")
        for i, prod in enumerate(datos_xml['productos'], 1):
            print(f"   {i}. {prod['codigo_producto']} - {prod['descripcion'][:40]}...")
            print(f"      Cantidad: {prod['cantidad']} {prod['unidad_medida']}")
            print(f"      Precio: ${prod['precio_unitario']:,.2f}")
            print(f"      Total: ${prod['total_item']:,.2f}")
    
    # Parsear PDF (con el parser mejorado)
    if pdf_path.exists():
        from app.services.pdf_parser_service import PDFParserService
        
        text_pdf = PDFParserService.extract_text_from_pdf(str(pdf_path))
        productos_pdf = PDFParserService._extract_productos(text_pdf)
        
        print(f"\n✅ PDF Parser:")
        print(f"   Productos: {len(productos_pdf)}")
        for i, prod in enumerate(productos_pdf, 1):
            print(f"   {i}. {prod['codigo_producto']} - {prod['descripcion'][:40]}...")
            print(f"      Cantidad: {prod['cantidad']} {prod['unidad_medida']}")
            print(f"      Precio: ${prod['precio_unitario']:,.2f}")
            print(f"      Total: ${prod['total_item']:,.2f}")
        
        # Comparar
        print(f"\n📊 COMPARACIÓN:")
        print(f"   XML: {len(datos_xml['productos'])} productos")
        print(f"   PDF: {len(productos_pdf)} productos")
        
        if len(datos_xml['productos']) == len(productos_pdf):
            print(f"   ✅ Cantidad de productos coincide!")
        else:
            print(f"   ⚠️ Diferencia en cantidad de productos")

print("\n✅ Test completado!")
