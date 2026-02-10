#!/usr/bin/env python3
"""
Test standalone del sistema XML/PDF (sin dependencias de SQLAlchemy)
"""
from pathlib import Path
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

print("=" * 80)
print("TEST COMPLETO DEL SISTEMA XML/PDF (STANDALONE)")
print("=" * 80)

# ===== TEST 1: DETECTOR DE ARCHIVOS =====
print("\n" + "=" * 80)
print("TEST 1: DETECTOR DE ARCHIVOS")
print("=" * 80)

class FileDetectorService:
    """Detector de archivos standalone"""
    
    @staticmethod
    def detect_file_type(file_path: str):
        try:
            path = Path(file_path)
            
            if not path.exists():
                return 'UNKNOWN'
            
            # Por extensión
            extension = path.suffix.lower()
            
            if extension == '.xml':
                return 'XML'
            elif extension == '.pdf':
                return 'PDF'
            
            # Por magic bytes
            try:
                with open(file_path, 'rb') as f:
                    header = f.read(8)
                    
                    if header.startswith(b'%PDF'):
                        return 'PDF'
                    
                    if header.startswith(b'<?xml') or header.startswith(b'<'):
                        return 'XML'
            except:
                pass
            
            return 'UNKNOWN'
            
        except Exception as e:
            return 'UNKNOWN'

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

test1_exitoso = (xml_detected == 5 and pdf_detected == 5)
if test1_exitoso:
    print("   ✅ DETECTOR FUNCIONANDO PERFECTAMENTE")
else:
    print("   ⚠️ Hay problemas con la detección")

# ===== TEST 2: PARSER XML =====
print("\n" + "=" * 80)
print("TEST 2: PARSER XML")
print("=" * 80)

# Importar parser XML standalone
import xml.etree.ElementTree as ET

class XMLParserDIAN:
    """Parser XML standalone"""
    
    NAMESPACES = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    }
    
    @classmethod
    def parse_xml(cls, xml_path: str):
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            datos = {
                'cufe': cls._extract_cufe(root),
                'numero_factura': cls._extract_numero_factura(root),
                'fecha_emision': cls._extract_fecha_emision(root),
                'totales': cls._extract_totales(root),
                'productos': cls._extract_productos(root),
            }
            
            return datos
        except Exception as e:
            logger.error(f"Error parseando XML: {e}")
            return None
    
    @classmethod
    def _extract_cufe(cls, root):
        elem = root.find('.//cbc:UUID', cls.NAMESPACES)
        return elem.text.strip() if elem is not None and elem.text else None
    
    @classmethod
    def _extract_numero_factura(cls, root):
        elem = root.find('.//cbc:ID', cls.NAMESPACES)
        return elem.text.strip() if elem is not None and elem.text else None
    
    @classmethod
    def _extract_fecha_emision(cls, root):
        elem = root.find('.//cbc:IssueDate', cls.NAMESPACES)
        return elem.text.strip() if elem is not None and elem.text else None
    
    @classmethod
    def _extract_totales(cls, root):
        totales = {}
        monetary = root.find('.//cac:LegalMonetaryTotal', cls.NAMESPACES)
        if monetary is not None:
            payable_elem = monetary.find('.//cbc:PayableAmount', cls.NAMESPACES)
            if payable_elem is not None and payable_elem.text:
                totales['total_pagar'] = float(payable_elem.text)
        
        tax_total = root.find('.//cac:TaxTotal', cls.NAMESPACES)
        if tax_total is not None:
            tax_amount_elem = tax_total.find('.//cbc:TaxAmount', cls.NAMESPACES)
            if tax_amount_elem is not None and tax_amount_elem.text:
                totales['total_impuestos'] = float(tax_amount_elem.text)
        
        return totales
    
    @classmethod
    def _extract_productos(cls, root):
        productos = []
        for line in root.findall('.//cac:InvoiceLine', cls.NAMESPACES):
            producto = {}
            
            item = line.find('.//cac:Item', cls.NAMESPACES)
            if item is not None:
                desc_elem = item.find('.//cbc:Description', cls.NAMESPACES)
                if desc_elem is not None and desc_elem.text:
                    producto['descripcion'] = desc_elem.text.strip()
            
            qty_elem = line.find('.//cbc:InvoicedQuantity', cls.NAMESPACES)
            if qty_elem is not None and qty_elem.text:
                producto['cantidad'] = float(qty_elem.text)
            
            productos.append(producto)
        
        return productos

print(f"\n📄 Probando parser XML con 3 archivos...")

xml_exitosos = 0
xml_errores = 0

for i, xml_file in enumerate(xml_files[:3], 1):
    print(f"\n[{i}/3] {xml_file.name[:50]}...")
    
    try:
        datos = XMLParserDIAN.parse_xml(str(xml_file))
        
        if datos and datos.get('cufe'):
            xml_exitosos += 1
            print(f"   ✅ CUFE: {datos['cufe'][:40]}...")
            print(f"   📄 Factura: {datos['numero_factura']}")
            print(f"   📅 Fecha: {datos['fecha_emision']}")
            print(f"   📦 Productos: {len(datos['productos'])}")
            print(f"   💰 Total: ${datos['totales'].get('total_pagar', 0):,.2f}")
            
            # Validar estructura
            assert 'total_pagar' in datos['totales'], "Falta 'total_pagar'"
            assert 'total_impuestos' in datos['totales'], "Falta 'total_impuestos'"
            
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

test2_exitoso = (xml_exitosos == 3)
if test2_exitoso:
    print("   ✅ PARSER XML FUNCIONANDO PERFECTAMENTE")
else:
    print("   ⚠️ Hay problemas con el parser XML")

# ===== TEST 3: VALIDAR ESTRUCTURA PDF =====
print("\n" + "=" * 80)
print("TEST 3: VALIDAR ARCHIVOS PDF")
print("=" * 80)

print(f"\n📄 Validando 3 archivos PDF...")

pdf_validos = 0

for i, pdf_file in enumerate(pdf_files[:3], 1):
    print(f"\n[{i}/3] {pdf_file.name[:50]}...")
    
    try:
        # Verificar que es PDF válido
        with open(pdf_file, 'rb') as f:
            header = f.read(8)
            if header.startswith(b'%PDF'):
                pdf_validos += 1
                print(f"   ✅ PDF válido")
                print(f"   📊 Tamaño: {pdf_file.stat().st_size / 1024:.1f} KB")
            else:
                print(f"   ❌ No es un PDF válido")
    except Exception as e:
        print(f"   ❌ Error: {e}")

print(f"\n📊 Resultado Validación PDF:")
print(f"   PDFs válidos: {pdf_validos}/3")

test3_exitoso = (pdf_validos == 3)
if test3_exitoso:
    print("   ✅ ARCHIVOS PDF VÁLIDOS")
else:
    print("   ⚠️ Hay problemas con los archivos PDF")

# ===== TEST 4: VERIFICAR PARES XML/PDF =====
print("\n" + "=" * 80)
print("TEST 4: VERIFICAR PARES XML/PDF")
print("=" * 80)

print(f"\n📄 Verificando que existan pares XML/PDF...")

pares_encontrados = 0
pares_totales = 0

for xml_file in xml_files[:3]:
    cufe = xml_file.stem
    pdf_file = xml_dir / f"{cufe}.pdf"
    
    pares_totales += 1
    print(f"\n[{pares_totales}] CUFE: {cufe[:40]}...")
    
    if pdf_file.exists():
        pares_encontrados += 1
        print(f"   ✅ XML: {xml_file.name[:40]}...")
        print(f"   ✅ PDF: {pdf_file.name[:40]}...")
        print(f"   ✅ Par completo")
    else:
        print(f"   ✅ XML: {xml_file.name[:40]}...")
        print(f"   ❌ PDF: No encontrado")

print(f"\n📊 Resultado Pares:")
print(f"   Pares completos: {pares_encontrados}/{pares_totales}")

test4_exitoso = (pares_encontrados == pares_totales)
if test4_exitoso:
    print("   ✅ TODOS LOS PARES EXISTEN")
else:
    print("   ⚠️ Faltan algunos PDFs")

# ===== RESUMEN FINAL =====
print("\n" + "=" * 80)
print("RESUMEN FINAL")
print("=" * 80)

total_tests = 4
tests_exitosos = 0

if test1_exitoso:
    tests_exitosos += 1
    print("✅ TEST 1: Detector de archivos - EXITOSO")
else:
    print("❌ TEST 1: Detector de archivos - FALLIDO")

if test2_exitoso:
    tests_exitosos += 1
    print("✅ TEST 2: Parser XML - EXITOSO")
else:
    print("❌ TEST 2: Parser XML - FALLIDO")

if test3_exitoso:
    tests_exitosos += 1
    print("✅ TEST 3: Validación PDF - EXITOSO")
else:
    print("❌ TEST 3: Validación PDF - FALLIDO")

if test4_exitoso:
    tests_exitosos += 1
    print("✅ TEST 4: Pares XML/PDF - EXITOSO")
else:
    print("❌ TEST 4: Pares XML/PDF - FALLIDO")

print(f"\n📊 RESULTADO GLOBAL: {tests_exitosos}/{total_tests} tests exitosos")

if tests_exitosos == total_tests:
    print("\n🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
    print("✅ Detector de archivos: OK")
    print("✅ Parser XML: OK")
    print("✅ Archivos PDF: OK")
    print("✅ Pares XML/PDF: OK")
    print("\n📝 PRÓXIMO PASO:")
    print("   Probar el sistema completo con el servidor en ejecución")
else:
    print(f"\n⚠️ Sistema parcialmente funcional ({tests_exitosos}/{total_tests})")
    print("Revisar los tests fallidos arriba")

print("\n✅ Test completado!")
