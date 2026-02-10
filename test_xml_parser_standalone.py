#!/usr/bin/env python3
"""
Probar el parser XML con archivos reales - STANDALONE
"""
import xml.etree.ElementTree as ET
from pathlib import Path
from decimal import Decimal
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class XMLParserDIAN:
    """Parser robusto para archivos XML de facturas electrónicas DIAN"""
    
    NAMESPACES = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'sts': 'dian:gov:co:facturaelectronica:Structures-2-1',
    }
    
    UNIDAD_MEDIDA_MAP = {
        '94': 'NIU', '10': 'PK', '11': 'BX', '01': 'UND',
        'EA': 'EA', 'PC': 'PC', 'UN': 'UN', 'NIU': 'NIU',
        'PK': 'PK', 'BX': 'BX', 'UND': 'UND',
    }
    
    @classmethod
    def parse_xml(cls, xml_path: str):
        """Parsea un archivo XML DIAN y extrae toda la información"""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            for prefix, uri in cls.NAMESPACES.items():
                ET.register_namespace(prefix, uri)
            
            datos = {
                'fuente': 'XML',
                'archivo_xml': Path(xml_path).name,
                'cufe': cls._extract_cufe(root),
                'numero_factura': cls._extract_numero_factura(root),
                'fecha_emision': cls._extract_fecha_emision(root),
                'emisor': cls._extract_emisor(root),
                'cliente': cls._extract_cliente(root),
                'totales': cls._extract_totales(root),
                'productos': cls._extract_productos(root),
            }
            
            logger.info(f"✅ XML parseado: {datos['numero_factura']} - {len(datos['productos'])} productos")
            return datos
            
        except Exception as e:
            logger.error(f"❌ Error parseando XML {xml_path}: {e}")
            import traceback
            logger.error(traceback.format_exc())
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
    def _extract_emisor(cls, root):
        emisor = {}
        supplier = root.find('.//cac:AccountingSupplierParty', cls.NAMESPACES)
        if supplier is not None:
            party = supplier.find('.//cac:Party', cls.NAMESPACES)
            if party is not None:
                nit_elem = party.find('.//cac:PartyTaxScheme/cbc:CompanyID', cls.NAMESPACES)
                if nit_elem is not None:
                    emisor['nit'] = nit_elem.text.strip()
                
                razon_elem = party.find('.//cac:PartyTaxScheme/cbc:RegistrationName', cls.NAMESPACES)
                if razon_elem is not None:
                    emisor['razon_social'] = razon_elem.text.strip()
        return emisor
    
    @classmethod
    def _extract_cliente(cls, root):
        cliente = {}
        customer = root.find('.//cac:AccountingCustomerParty', cls.NAMESPACES)
        if customer is not None:
            party = customer.find('.//cac:Party', cls.NAMESPACES)
            if party is not None:
                nit_elem = party.find('.//cac:PartyTaxScheme/cbc:CompanyID', cls.NAMESPACES)
                if nit_elem is not None:
                    cliente['nit'] = nit_elem.text.strip()
                
                razon_elem = party.find('.//cac:PartyTaxScheme/cbc:RegistrationName', cls.NAMESPACES)
                if razon_elem is not None:
                    cliente['razon_social'] = razon_elem.text.strip()
        return cliente
    
    @classmethod
    def _extract_totales(cls, root):
        totales = {}
        monetary = root.find('.//cac:LegalMonetaryTotal', cls.NAMESPACES)
        if monetary is not None:
            subtotal_elem = monetary.find('.//cbc:LineExtensionAmount', cls.NAMESPACES)
            if subtotal_elem is not None and subtotal_elem.text:
                totales['subtotal'] = float(subtotal_elem.text)
            
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
            
            id_elem = line.find('.//cbc:ID', cls.NAMESPACES)
            if id_elem is not None and id_elem.text:
                try:
                    producto['linea'] = int(float(id_elem.text))
                except:
                    producto['linea'] = id_elem.text
            
            qty_elem = line.find('.//cbc:InvoicedQuantity', cls.NAMESPACES)
            if qty_elem is not None and qty_elem.text:
                producto['cantidad'] = float(qty_elem.text)
                unit_code = qty_elem.get('unitCode', 'NIU')
                producto['unidad_medida'] = cls.UNIDAD_MEDIDA_MAP.get(unit_code, unit_code)
            
            line_ext_elem = line.find('.//cbc:LineExtensionAmount', cls.NAMESPACES)
            if line_ext_elem is not None and line_ext_elem.text:
                producto['total_item'] = float(line_ext_elem.text)
            
            item = line.find('.//cac:Item', cls.NAMESPACES)
            if item is not None:
                desc_elem = item.find('.//cbc:Description', cls.NAMESPACES)
                if desc_elem is not None and desc_elem.text:
                    producto['descripcion'] = desc_elem.text.strip()
                
                std_id = item.find('.//cac:StandardItemIdentification/cbc:ID', cls.NAMESPACES)
                if std_id is not None and std_id.text:
                    producto['codigo_estandar'] = std_id.text.strip()
                
                seller_id = item.find('.//cac:SellersItemIdentification/cbc:ID', cls.NAMESPACES)
                if seller_id is not None and seller_id.text:
                    producto['codigo_vendedor'] = seller_id.text.strip()
            
            if 'codigo_estandar' in producto:
                producto['codigo_producto'] = producto['codigo_estandar']
            elif 'codigo_vendedor' in producto:
                producto['codigo_producto'] = producto['codigo_vendedor']
            else:
                desc = producto.get('descripcion', f"PROD{producto.get('linea', '0')}")
                palabras = desc.split()[:2]
                producto['codigo_producto'] = ''.join(palabras).upper()[:20]
            
            price = line.find('.//cac:Price', cls.NAMESPACES)
            if price is not None:
                price_amount_elem = price.find('.//cbc:PriceAmount', cls.NAMESPACES)
                if price_amount_elem is not None and price_amount_elem.text:
                    producto['precio_unitario'] = float(price_amount_elem.text)
            
            producto['iva_porcentaje'] = 0.0
            producto['iva_valor'] = 0.0
            
            tax_total_line = line.find('.//cac:TaxTotal', cls.NAMESPACES)
            if tax_total_line is not None:
                for tax_sub in tax_total_line.findall('.//cac:TaxSubtotal', cls.NAMESPACES):
                    percent = tax_sub.find('.//cac:TaxCategory/cbc:Percent', cls.NAMESPACES)
                    if percent is not None and percent.text:
                        producto['iva_porcentaje'] = float(percent.text)
                    
                    amount = tax_sub.find('.//cbc:TaxAmount', cls.NAMESPACES)
                    if amount is not None and amount.text:
                        producto['iva_valor'] = float(amount.text)
            
            productos.append(producto)
        
        return productos


# EJECUTAR PRUEBAS
xml_dir = Path("/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE/CUFE-XML")
xml_files = list(xml_dir.glob("*.xml"))

print("=" * 80)
print("TEST DEL PARSER XML DIAN")
print("=" * 80)

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

print("\n✅ Test completado!")
