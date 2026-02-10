#!/usr/bin/env python3
"""
Analizar estructura completa de archivos XML DIAN
"""
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict
import json

# Namespaces comunes en facturas DIAN
NAMESPACES = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'sts': 'dian:gov:co:facturaelectronica:Structures-2-1',
}

def analizar_xml(xml_path):
    """Analiza un archivo XML y extrae toda la información relevante"""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Registrar namespaces
        for prefix, uri in NAMESPACES.items():
            ET.register_namespace(prefix, uri)
        
        datos = {
            'archivo': xml_path.name,
            'cufe': None,
            'numero_factura': None,
            'fecha_emision': None,
            'tipo_factura': None,
            'moneda': None,
            'emisor': {},
            'cliente': {},
            'totales': {},
            'productos': [],
            'impuestos': [],
            'forma_pago': None,
            'medio_pago': None,
        }
        
        # CUFE
        cufe_elem = root.find('.//cbc:UUID', NAMESPACES)
        if cufe_elem is not None:
            datos['cufe'] = cufe_elem.text
        
        # Número de factura
        num_elem = root.find('.//cbc:ID', NAMESPACES)
        if num_elem is not None:
            datos['numero_factura'] = num_elem.text
        
        # Fecha de emisión
        fecha_elem = root.find('.//cbc:IssueDate', NAMESPACES)
        if fecha_elem is not None:
            datos['fecha_emision'] = fecha_elem.text
        
        # Tipo de factura
        tipo_elem = root.find('.//cbc:InvoiceTypeCode', NAMESPACES)
        if tipo_elem is not None:
            datos['tipo_factura'] = tipo_elem.text
        
        # Moneda
        moneda_elem = root.find('.//cbc:DocumentCurrencyCode', NAMESPACES)
        if moneda_elem is not None:
            datos['moneda'] = moneda_elem.text
        
        # Cantidad de líneas (productos)
        line_count_elem = root.find('.//cbc:LineCountNumeric', NAMESPACES)
        if line_count_elem is not None:
            try:
                datos['cantidad_productos_declarada'] = int(float(line_count_elem.text))
            except:
                datos['cantidad_productos_declarada'] = line_count_elem.text
        
        # EMISOR
        supplier = root.find('.//cac:AccountingSupplierParty', NAMESPACES)
        if supplier is not None:
            party = supplier.find('.//cac:Party', NAMESPACES)
            if party is not None:
                # NIT
                nit_elem = party.find('.//cac:PartyTaxScheme/cbc:CompanyID', NAMESPACES)
                if nit_elem is not None:
                    datos['emisor']['nit'] = nit_elem.text
                
                # Razón social
                razon_elem = party.find('.//cac:PartyTaxScheme/cbc:RegistrationName', NAMESPACES)
                if razon_elem is not None:
                    datos['emisor']['razon_social'] = razon_elem.text
                
                # Nombre comercial
                nombre_elem = party.find('.//cac:PartyName/cbc:Name', NAMESPACES)
                if nombre_elem is not None:
                    datos['emisor']['nombre_comercial'] = nombre_elem.text
        
        # CLIENTE
        customer = root.find('.//cac:AccountingCustomerParty', NAMESPACES)
        if customer is not None:
            party = customer.find('.//cac:Party', NAMESPACES)
            if party is not None:
                # NIT
                nit_elem = party.find('.//cac:PartyTaxScheme/cbc:CompanyID', NAMESPACES)
                if nit_elem is not None:
                    datos['cliente']['nit'] = nit_elem.text
                
                # Razón social
                razon_elem = party.find('.//cac:PartyTaxScheme/cbc:RegistrationName', NAMESPACES)
                if razon_elem is not None:
                    datos['cliente']['razon_social'] = razon_elem.text
        
        # TOTALES
        monetary = root.find('.//cac:LegalMonetaryTotal', NAMESPACES)
        if monetary is not None:
            # Subtotal
            subtotal_elem = monetary.find('.//cbc:LineExtensionAmount', NAMESPACES)
            if subtotal_elem is not None:
                datos['totales']['subtotal'] = float(subtotal_elem.text)
            
            # Total sin impuestos
            tax_exclusive_elem = monetary.find('.//cbc:TaxExclusiveAmount', NAMESPACES)
            if tax_exclusive_elem is not None:
                datos['totales']['total_sin_impuestos'] = float(tax_exclusive_elem.text)
            
            # Total con impuestos
            tax_inclusive_elem = monetary.find('.//cbc:TaxInclusiveAmount', NAMESPACES)
            if tax_inclusive_elem is not None:
                datos['totales']['total_con_impuestos'] = float(tax_inclusive_elem.text)
            
            # Total a pagar
            payable_elem = monetary.find('.//cbc:PayableAmount', NAMESPACES)
            if payable_elem is not None:
                datos['totales']['total_pagar'] = float(payable_elem.text)
        
        # IMPUESTOS TOTALES
        tax_total = root.find('.//cac:TaxTotal', NAMESPACES)
        if tax_total is not None:
            tax_amount_elem = tax_total.find('.//cbc:TaxAmount', NAMESPACES)
            if tax_amount_elem is not None:
                datos['totales']['total_impuestos'] = float(tax_amount_elem.text)
            
            # Desglose de impuestos
            for tax_subtotal in tax_total.findall('.//cac:TaxSubtotal', NAMESPACES):
                impuesto = {}
                
                taxable_elem = tax_subtotal.find('.//cbc:TaxableAmount', NAMESPACES)
                if taxable_elem is not None:
                    impuesto['base_imponible'] = float(taxable_elem.text)
                
                amount_elem = tax_subtotal.find('.//cbc:TaxAmount', NAMESPACES)
                if amount_elem is not None:
                    impuesto['valor'] = float(amount_elem.text)
                
                percent_elem = tax_subtotal.find('.//cac:TaxCategory/cbc:Percent', NAMESPACES)
                if percent_elem is not None:
                    impuesto['porcentaje'] = float(percent_elem.text)
                
                scheme_elem = tax_subtotal.find('.//cac:TaxCategory/cac:TaxScheme/cbc:Name', NAMESPACES)
                if scheme_elem is not None:
                    impuesto['tipo'] = scheme_elem.text
                
                if impuesto:
                    datos['impuestos'].append(impuesto)
        
        # PRODUCTOS (InvoiceLine)
        for line in root.findall('.//cac:InvoiceLine', NAMESPACES):
            producto = {}
            
            # ID de línea
            id_elem = line.find('.//cbc:ID', NAMESPACES)
            if id_elem is not None:
                try:
                    producto['linea'] = int(float(id_elem.text))  # Convertir a float primero por si tiene decimales
                except:
                    producto['linea'] = id_elem.text  # Guardar como string si falla
            
            # Cantidad
            qty_elem = line.find('.//cbc:InvoicedQuantity', NAMESPACES)
            if qty_elem is not None:
                producto['cantidad'] = float(qty_elem.text)
                producto['unidad_medida'] = qty_elem.get('unitCode', 'NIU')
            
            # Total de línea
            line_ext_elem = line.find('.//cbc:LineExtensionAmount', NAMESPACES)
            if line_ext_elem is not None:
                producto['total_linea'] = float(line_ext_elem.text)
            
            # Impuestos del producto
            producto['impuestos'] = []
            tax_total_line = line.find('.//cac:TaxTotal', NAMESPACES)
            if tax_total_line is not None:
                for tax_sub in tax_total_line.findall('.//cac:TaxSubtotal', NAMESPACES):
                    imp = {}
                    
                    taxable = tax_sub.find('.//cbc:TaxableAmount', NAMESPACES)
                    if taxable is not None:
                        imp['base'] = float(taxable.text)
                    
                    amount = tax_sub.find('.//cbc:TaxAmount', NAMESPACES)
                    if amount is not None:
                        imp['valor'] = float(amount.text)
                    
                    percent = tax_sub.find('.//cac:TaxCategory/cbc:Percent', NAMESPACES)
                    if percent is not None:
                        imp['porcentaje'] = float(percent.text)
                    
                    producto['impuestos'].append(imp)
            
            # Información del item
            item = line.find('.//cac:Item', NAMESPACES)
            if item is not None:
                # Descripción
                desc_elem = item.find('.//cbc:Description', NAMESPACES)
                if desc_elem is not None:
                    producto['descripcion'] = desc_elem.text
                
                # Código del vendedor
                seller_id = item.find('.//cac:SellersItemIdentification/cbc:ID', NAMESPACES)
                if seller_id is not None:
                    producto['codigo_producto'] = seller_id.text
                
                # Código estándar (GTIN, EAN, etc.)
                std_id = item.find('.//cac:StandardItemIdentification/cbc:ID', NAMESPACES)
                if std_id is not None:
                    producto['codigo_estandar'] = std_id.text
                    producto['tipo_codigo_estandar'] = std_id.get('schemeID', 'GTIN')
            
            # Precio
            price = line.find('.//cac:Price', NAMESPACES)
            if price is not None:
                price_amount_elem = price.find('.//cbc:PriceAmount', NAMESPACES)
                if price_amount_elem is not None:
                    producto['precio_unitario'] = float(price_amount_elem.text)
            
            datos['productos'].append(producto)
        
        # FORMA DE PAGO
        payment_means = root.find('.//cac:PaymentMeans', NAMESPACES)
        if payment_means is not None:
            code_elem = payment_means.find('.//cbc:PaymentMeansCode', NAMESPACES)
            if code_elem is not None:
                datos['forma_pago'] = code_elem.text
            
            id_elem = payment_means.find('.//cbc:PaymentID', NAMESPACES)
            if id_elem is not None:
                datos['medio_pago'] = id_elem.text
        
        return datos
        
    except Exception as e:
        print(f"❌ Error procesando {xml_path.name}: {e}")
        return None

# Analizar múltiples archivos
xml_dir = Path("/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE/CUFE-XML")
xml_files = list(xml_dir.glob("*.xml"))

print("=" * 80)
print(f"ANÁLISIS DE ESTRUCTURA XML - {len(xml_files)} ARCHIVOS")
print("=" * 80)

# Analizar TODOS los archivos
print(f"\n📊 ANALIZANDO {len(xml_files)} ARCHIVOS...")
print("-" * 80)

resultados = []
errores = []
for i, xml_file in enumerate(xml_files, 1):
    if i % 20 == 0 or i == len(xml_files):
        print(f"   Procesando: {i}/{len(xml_files)}...")
    
    datos = analizar_xml(xml_file)
    if datos:
        resultados.append(datos)
    else:
        errores.append(xml_file.name)

print(f"\n✅ Archivos procesados: {len(resultados)}/{len(xml_files)}")
if errores:
    print(f"❌ Errores: {len(errores)}")

# Mostrar detalle de primeros 5
print("\n📊 DETALLE DE PRIMEROS 5 ARCHIVOS:")
print("-" * 80)
for i, datos in enumerate(resultados[:5], 1):
    if datos:
        print(f"   ✅ CUFE: {datos['cufe'][:40]}...")
        print(f"   📄 Factura: {datos['numero_factura']}")
        print(f"   📅 Fecha: {datos['fecha_emision']}")
        print(f"   👤 Emisor: {datos['emisor'].get('razon_social', 'N/A')[:40]}")
        print(f"   👥 Cliente: {datos['cliente'].get('razon_social', 'N/A')[:40]}")
        print(f"   📦 Productos declarados: {datos.get('cantidad_productos_declarada', 0)}")
        print(f"   📦 Productos encontrados: {len(datos['productos'])}")
        print(f"   💰 Total: ${datos['totales'].get('total_pagar', 0):,.2f}")

# Guardar análisis completo
output_file = "analisis_estructura_xml_detallado.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(resultados, f, indent=2, ensure_ascii=False)

print(f"\n✅ Análisis guardado en: {output_file}")

# Estadísticas generales
print("\n" + "=" * 80)
print("ESTADÍSTICAS GENERALES")
print("=" * 80)

# Campos presentes
campos_presentes = defaultdict(int)
for resultado in resultados:
    if resultado['cufe']: campos_presentes['CUFE'] += 1
    if resultado['numero_factura']: campos_presentes['Número Factura'] += 1
    if resultado['fecha_emision']: campos_presentes['Fecha Emisión'] += 1
    if resultado['emisor'].get('nit'): campos_presentes['NIT Emisor'] += 1
    if resultado['emisor'].get('razon_social'): campos_presentes['Razón Social Emisor'] += 1
    if resultado['cliente'].get('nit'): campos_presentes['NIT Cliente'] += 1
    if resultado['cliente'].get('razon_social'): campos_presentes['Razón Social Cliente'] += 1
    if resultado['totales'].get('total_pagar'): campos_presentes['Total a Pagar'] += 1
    if resultado.get('cantidad_productos_declarada'): campos_presentes['Cantidad Productos (LineCountNumeric)'] += 1
    if resultado['productos']: campos_presentes['Productos (InvoiceLine)'] += 1

print("\n📋 Campos presentes en archivos analizados:")
for campo, count in sorted(campos_presentes.items()):
    porcentaje = (count / len(resultados)) * 100
    print(f"   {campo:40s}: {count}/{len(resultados)} ({porcentaje:.0f}%)")

# Análisis de productos
print("\n📦 ANÁLISIS DE PRODUCTOS:")
total_productos = sum(len(r['productos']) for r in resultados)
print(f"   Total productos en {len(resultados)} facturas: {total_productos}")
print(f"   Promedio por factura: {total_productos / len(resultados):.1f}")

# Campos en productos
campos_productos = defaultdict(int)
for resultado in resultados:
    for prod in resultado['productos']:
        if prod.get('codigo_producto'): campos_productos['Código Producto'] += 1
        if prod.get('codigo_estandar'): campos_productos['Código Estándar (GTIN/EAN)'] += 1
        if prod.get('descripcion'): campos_productos['Descripción'] += 1
        if prod.get('cantidad'): campos_productos['Cantidad'] += 1
        if prod.get('unidad_medida'): campos_productos['Unidad Medida'] += 1
        if prod.get('precio_unitario'): campos_productos['Precio Unitario'] += 1
        if prod.get('total_linea'): campos_productos['Total Línea'] += 1
        if prod.get('impuestos'): campos_productos['Impuestos'] += 1

print("\n   Campos en productos:")
for campo, count in sorted(campos_productos.items()):
    porcentaje = (count / total_productos) * 100 if total_productos > 0 else 0
    print(f"      {campo:35s}: {count}/{total_productos} ({porcentaje:.0f}%)")

print("\n✅ Análisis completado!")
