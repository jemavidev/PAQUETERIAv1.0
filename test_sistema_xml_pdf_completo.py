#!/usr/bin/env python3
"""
Test completo del sistema XML/PDF con archivos reales
"""
import sys
sys.path.insert(0, '/home/stk/Documents/GIT/PAQUETEX v1.0/CODE/src')

from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

print("=" * 80)
print("TEST COMPLETO DEL SISTEMA XML/PDF")
print("=" * 80)

# ===== TEST 1: DETECTOR DE ARCHIVOS =====
print("\n" + "=" * 80)
print("TEST 1: DETECTOR DE ARCHIVOS")
print("=" * 80)

from app.services.file_detector_service import FileDetectorService

xml_dir = Path("/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE/CUFE-XML")
xml_files = list(xml_dir.glob("*.xml"))[:5]
pdf_files = list(xml_dir.glob("*.pdf"))[:5]

print(f"\n📄 Probando detección con 5 XML y 5 PDF...")

xml_detected = 0
pdf_detected = 0

for xml_file in xml_files:
    file_type = FileDetectorService.detect_file_type(str(xml_file))
    if file_type == 'XML':
        xml_detected += 1
        print(f"   ✅ {xml_file.name[:40]}... → {file_type}")
    else:
        print(f"   ❌ {xml_file.name[:40]}... → {file_type} (esperado XML)")

for pdf_file in pdf_files:
    file_type = FileDetectorService.detect_file_type(str(pdf_file))
    if file_type == 'PDF':
        pdf_detected += 1
        print(f"   ✅ {pdf_file.name[:40]}... → {file_type}")
    else:
        print(f"   ❌ {pdf_file.name[:40]}... → {file_type} (esperado PDF)")

print(f"\n📊 Resultado Detector:")
print(f"   XML detectados: {xml_detected}/5")
print(f"   PDF detectados: {pdf_detected}/5")

if xml_detected == 5 and pdf_detected == 5:
    print("   ✅ DETECTOR FUNCIONANDO PERFECTAMENTE")
else:
    print("   ⚠️ Hay problemas con la detección")

# ===== TEST 2: PARSER XML =====
print("\n" + "=" * 80)
print("TEST 2: PARSER XML")
print("=" * 80)

from app.services.xml_parser_service import XMLParserDIAN

print(f"\n📄 Probando parser XML con 3 archivos...")

xml_exitosos = 0
xml_errores = 0

for i, xml_file in enumerate(xml_files[:3], 1):
    print(f"\n[{i}/3] {xml_file.name[:50]}...")
    
    try:
        datos = XMLParserDIAN.parse_xml(str(xml_file))
        
        if datos:
            xml_exitosos += 1
            print(f"   ✅ CUFE: {datos['cufe'][:40]}...")
            print(f"   📄 Factura: {datos['numero_factura']}")
            print(f"   📅 Fecha: {datos['fecha_emision']}")
            print(f"   📦 Productos: {len(datos['productos'])}")
            print(f"   💰 Total: ${datos['totales'].get('total_pagar', 0):,.2f}")
            
            # Validar estructura
            assert 'cufe' in datos, "Falta campo 'cufe'"
            assert 'numero_factura' in datos, "Falta campo 'numero_factura'"
            assert 'totales' in datos, "Falta campo 'totales'"
            assert 'productos' in datos, "Falta campo 'productos'"
            assert 'total_pagar' in datos['totales'], "Falta 'total_pagar' en totales"
            assert 'total_impuestos' in datos['totales'], "Falta 'total_impuestos' en totales"
            
            print(f"   ✅ Estructura validada")
        else:
            xml_errores += 1
            print(f"   ❌ Error: No se pudo parsear")
    except Exception as e:
        xml_errores += 1
        print(f"   ❌ Error: {e}")

print(f"\n📊 Resultado Parser XML:")
print(f"   Exitosos: {xml_exitosos}/3")
print(f"   Errores: {xml_errores}/3")

if xml_exitosos == 3:
    print("   ✅ PARSER XML FUNCIONANDO PERFECTAMENTE")
else:
    print("   ⚠️ Hay problemas con el parser XML")

# ===== TEST 3: PARSER PDF MEJORADO =====
print("\n" + "=" * 80)
print("TEST 3: PARSER PDF MEJORADO")
print("=" * 80)

from app.services.pdf_parser_service import PDFParserService

print(f"\n📄 Probando parser PDF con 3 archivos...")

pdf_exitosos = 0
pdf_errores = 0

for i, pdf_file in enumerate(pdf_files[:3], 1):
    print(f"\n[{i}/3] {pdf_file.name[:50]}...")
    
    try:
        datos = PDFParserService.parse_dian_document(str(pdf_file))
        
        if 'error' not in datos:
            pdf_exitosos += 1
            print(f"   ✅ CUFE: {datos.get('cufe', 'N/A')[:40]}...")
            print(f"   📄 Factura: {datos.get('numero_documento', 'N/A')}")
            print(f"   📅 Fecha: {datos.get('fecha_emision', 'N/A')}")
            print(f"   📦 Productos: {len(datos.get('productos', []))}")
            
            totales = datos.get('totales', {})
            print(f"   💰 Totales:")
            print(f"      Subtotal: ${totales.get('subtotal', 0) or 0:,.2f}")
            print(f"      IVA: ${totales.get('total_impuestos', 0) or 0:,.2f}")
            print(f"      Total: ${totales.get('total_pagar', 0) or 0:,.2f}")
            
            # Validar estructura (idéntica al XML)
            assert 'totales' in datos, "Falta campo 'totales'"
            assert 'productos' in datos, "Falta campo 'productos'"
            assert 'total_pagar' in datos['totales'], "Falta 'total_pagar' en totales"
            assert 'total_impuestos' in datos['totales'], "Falta 'total_impuestos' en totales"
            
            # Validar IVA en productos
            productos_con_iva = 0
            for prod in datos.get('productos', []):
                if 'iva_porcentaje' in prod and 'iva_valor' in prod:
                    productos_con_iva += 1
            
            print(f"   📊 Productos con IVA: {productos_con_iva}/{len(datos.get('productos', []))}")
            print(f"   ✅ Estructura validada")
        else:
            pdf_errores += 1
            print(f"   ❌ Error: {datos['error']}")
    except Exception as e:
        pdf_errores += 1
        print(f"   ❌ Error: {e}")
        import traceback
        print(f"   {traceback.format_exc()}")

print(f"\n📊 Resultado Parser PDF:")
print(f"   Exitosos: {pdf_exitosos}/3")
print(f"   Errores: {pdf_errores}/3")

if pdf_exitosos == 3:
    print("   ✅ PARSER PDF FUNCIONANDO PERFECTAMENTE")
else:
    print("   ⚠️ Hay problemas con el parser PDF")

# ===== TEST 4: COMPARACIÓN XML vs PDF =====
print("\n" + "=" * 80)
print("TEST 4: COMPARACIÓN XML vs PDF")
print("=" * 80)

print(f"\n📄 Comparando 2 archivos (mismo CUFE)...")

comparaciones_exitosas = 0
comparaciones_totales = 0

for xml_file in xml_files[:2]:
    cufe = xml_file.stem
    pdf_file = xml_dir / f"{cufe}.pdf"
    
    if not pdf_file.exists():
        continue
    
    comparaciones_totales += 1
    print(f"\n[{comparaciones_totales}] CUFE: {cufe[:40]}...")
    
    try:
        # Parsear ambos
        datos_xml = XMLParserDIAN.parse_xml(str(xml_file))
        datos_pdf = PDFParserService.parse_dian_document(str(pdf_file))
        
        if datos_xml and 'error' not in datos_pdf:
            # Comparar productos
            num_productos_xml = len(datos_xml['productos'])
            num_productos_pdf = len(datos_pdf['productos'])
            
            print(f"   📦 Productos:")
            print(f"      XML: {num_productos_xml}")
            print(f"      PDF: {num_productos_pdf}")
            
            if num_productos_xml == num_productos_pdf:
                print(f"      ✅ Cantidad coincide")
            else:
                print(f"      ⚠️ Diferencia: {abs(num_productos_xml - num_productos_pdf)}")
            
            # Comparar totales
            total_xml = datos_xml['totales'].get('total_pagar', 0)
            total_pdf = datos_pdf['totales'].get('total_pagar', 0)
            
            print(f"   💰 Totales:")
            print(f"      XML: ${total_xml:,.2f}")
            print(f"      PDF: ${total_pdf or 0:,.2f}")
            
            if total_pdf and abs(total_xml - total_pdf) < 1:
                print(f"      ✅ Totales coinciden")
                comparaciones_exitosas += 1
            elif total_pdf:
                print(f"      ⚠️ Diferencia: ${abs(total_xml - total_pdf):,.2f}")
            else:
                print(f"      ⚠️ Total PDF no extraído")
            
            # Comparar estructura
            print(f"   📋 Estructura:")
            print(f"      XML tiene 'total_impuestos': {'total_impuestos' in datos_xml['totales']}")
            print(f"      PDF tiene 'total_impuestos': {'total_impuestos' in datos_pdf['totales']}")
            print(f"      XML tiene 'total_pagar': {'total_pagar' in datos_xml['totales']}")
            print(f"      PDF tiene 'total_pagar': {'total_pagar' in datos_pdf['totales']}")
            
            if ('total_impuestos' in datos_xml['totales'] and 
                'total_impuestos' in datos_pdf['totales'] and
                'total_pagar' in datos_xml['totales'] and 
                'total_pagar' in datos_pdf['totales']):
                print(f"      ✅ Estructura idéntica")
            else:
                print(f"      ⚠️ Estructura diferente")
        else:
            print(f"   ❌ Error parseando archivos")
    except Exception as e:
        print(f"   ❌ Error: {e}")

print(f"\n📊 Resultado Comparación:")
print(f"   Comparaciones exitosas: {comparaciones_exitosas}/{comparaciones_totales}")

if comparaciones_exitosas == comparaciones_totales and comparaciones_totales > 0:
    print("   ✅ XML Y PDF COINCIDEN PERFECTAMENTE")
else:
    print("   ⚠️ Hay diferencias entre XML y PDF")

# ===== RESUMEN FINAL =====
print("\n" + "=" * 80)
print("RESUMEN FINAL")
print("=" * 80)

total_tests = 4
tests_exitosos = 0

if xml_detected == 5 and pdf_detected == 5:
    tests_exitosos += 1
    print("✅ TEST 1: Detector de archivos - EXITOSO")
else:
    print("❌ TEST 1: Detector de archivos - FALLIDO")

if xml_exitosos == 3:
    tests_exitosos += 1
    print("✅ TEST 2: Parser XML - EXITOSO")
else:
    print("❌ TEST 2: Parser XML - FALLIDO")

if pdf_exitosos == 3:
    tests_exitosos += 1
    print("✅ TEST 3: Parser PDF - EXITOSO")
else:
    print("❌ TEST 3: Parser PDF - FALLIDO")

if comparaciones_exitosas == comparaciones_totales and comparaciones_totales > 0:
    tests_exitosos += 1
    print("✅ TEST 4: Comparación XML vs PDF - EXITOSO")
else:
    print("❌ TEST 4: Comparación XML vs PDF - FALLIDO")

print(f"\n📊 RESULTADO GLOBAL: {tests_exitosos}/{total_tests} tests exitosos")

if tests_exitosos == total_tests:
    print("\n🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
    print("✅ Detector de archivos: OK")
    print("✅ Parser XML: OK")
    print("✅ Parser PDF: OK")
    print("✅ Estructura idéntica: OK")
else:
    print(f"\n⚠️ Sistema parcialmente funcional ({tests_exitosos}/{total_tests})")
    print("Revisar los tests fallidos arriba")

print("\n✅ Test completado!")
