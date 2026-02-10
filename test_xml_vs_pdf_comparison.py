#!/usr/bin/env python3
"""
Comparar extracción XML vs PDF para validar el parser PDF
"""
import sys
sys.path.insert(0, '/home/stk/Documents/GIT/PAQUETEX v1.0/CODE/src')

from pathlib import Path
import logging

# Importar parser XML standalone
exec(open('test_xml_parser_standalone.py').read().split('# EJECUTAR PRUEBAS')[0])

# Importar parser PDF
from app.services.pdf_parser_service import PDFParserService

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

xml_dir = Path("/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE/CUFE-XML")
xml_files = list(xml_dir.glob("*.xml"))

print("=" * 80)
print("COMPARACIÓN XML vs PDF - VALIDACIÓN DE PARSERS")
print("=" * 80)

# Probar con 5 archivos
test_files = xml_files[:5]

resultados = []

for i, xml_file in enumerate(test_files, 1):
    cufe = xml_file.stem
    pdf_file = xml_dir / f"{cufe}.pdf"
    
    print(f"\n[{i}/{len(test_files)}] Archivo: {cufe[:40]}...")
    print("-" * 80)
    
    # Parsear XML
    datos_xml = XMLParserDIAN.parse_xml(str(xml_file))
    
    # Parsear PDF
    datos_pdf = None
    if pdf_file.exists():
        try:
            text_pdf = PDFParserService.extract_text_from_pdf(str(pdf_file), max_pages=999)
            productos_pdf = PDFParserService._extract_productos(text_pdf)
            totales_pdf = PDFParserService._extract_totales(text_pdf)
            
            datos_pdf = {
                'productos': productos_pdf,
                'totales': totales_pdf,
            }
        except Exception as e:
            print(f"   ❌ Error parseando PDF: {e}")
    else:
        print(f"   ⚠️ PDF no encontrado")
    
    if datos_xml and datos_pdf:
        # Comparar productos
        num_productos_xml = len(datos_xml['productos'])
        num_productos_pdf = len(datos_pdf['productos'])
        
        print(f"\n   📦 PRODUCTOS:")
        print(f"      XML: {num_productos_xml} productos")
        print(f"      PDF: {num_productos_pdf} productos")
        
        if num_productos_xml == num_productos_pdf:
            print(f"      ✅ Cantidad coincide!")
        else:
            print(f"      ⚠️ Diferencia: {abs(num_productos_xml - num_productos_pdf)} productos")
        
        # Comparar totales
        total_xml = datos_xml['totales'].get('total_pagar', 0)
        total_pdf = datos_pdf['totales'].get('total_neto', 0)
        
        print(f"\n   💰 TOTALES:")
        print(f"      XML: ${total_xml:,.2f}")
        print(f"      PDF: ${total_pdf:,.2f}" if total_pdf else "      PDF: No extraído")
        
        if total_pdf and abs(total_xml - total_pdf) < 1:
            print(f"      ✅ Totales coinciden!")
        elif total_pdf:
            print(f"      ⚠️ Diferencia: ${abs(total_xml - total_pdf):,.2f}")
        else:
            print(f"      ⚠️ Total no extraído del PDF")
        
        # Comparar primer producto
        if datos_xml['productos'] and datos_pdf['productos']:
            prod_xml = datos_xml['productos'][0]
            prod_pdf = datos_pdf['productos'][0]
            
            print(f"\n   📦 PRIMER PRODUCTO:")
            print(f"      XML:")
            print(f"         Código: {prod_xml.get('codigo_producto', 'N/A')}")
            print(f"         Descripción: {prod_xml.get('descripcion', 'N/A')[:50]}...")
            print(f"         Cantidad: {prod_xml.get('cantidad', 0)} {prod_xml.get('unidad_medida', '')}")
            print(f"         Precio: ${prod_xml.get('precio_unitario', 0):,.2f}")
            
            print(f"      PDF:")
            print(f"         Código: {prod_pdf.get('codigo_producto', 'N/A')}")
            print(f"         Descripción: {prod_pdf.get('descripcion', 'N/A')[:50]}...")
            print(f"         Cantidad: {prod_pdf.get('cantidad', 0)} {prod_pdf.get('unidad_medida', '')}")
            print(f"         Precio: ${prod_pdf.get('precio_unitario', 0):,.2f}")
        
        # Guardar resultado
        resultado = {
            'cufe': cufe[:40],
            'factura': datos_xml['numero_factura'],
            'productos_xml': num_productos_xml,
            'productos_pdf': num_productos_pdf,
            'productos_match': num_productos_xml == num_productos_pdf,
            'total_xml': total_xml,
            'total_pdf': total_pdf,
            'total_match': total_pdf and abs(total_xml - total_pdf) < 1,
        }
        resultados.append(resultado)

# RESUMEN FINAL
print("\n" + "=" * 80)
print("RESUMEN COMPARATIVO")
print("=" * 80)

productos_match = sum(1 for r in resultados if r['productos_match'])
totales_match = sum(1 for r in resultados if r['total_match'])

print(f"\n✅ Productos coinciden: {productos_match}/{len(resultados)}")
print(f"✅ Totales coinciden: {totales_match}/{len(resultados)}")

print(f"\n📊 DETALLE:")
for r in resultados:
    print(f"\n   {r['factura']}:")
    print(f"      Productos: XML={r['productos_xml']}, PDF={r['productos_pdf']} {'✅' if r['productos_match'] else '⚠️'}")
    print(f"      Total: XML=${r['total_xml']:,.2f}, PDF=${r['total_pdf']:,.2f} {'✅' if r['total_match'] else '⚠️'}")

if productos_match == len(resultados) and totales_match == len(resultados):
    print(f"\n🎉 ¡PARSER PDF VALIDADO! Coincide 100% con XML")
else:
    print(f"\n⚠️ Parser PDF necesita ajustes en algunos casos")

print("\n✅ Comparación completada!")
