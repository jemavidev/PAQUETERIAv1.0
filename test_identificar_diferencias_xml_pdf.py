#!/usr/bin/env python3
"""
Test para identificar exactamente qué datos difieren entre XML y PDF
"""
import sys
sys.path.insert(0, '/home/stk/Documents/GIT/PAQUETEX v1.0/CODE/src')

from pathlib import Path
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Importar parsers
from app.services.xml_parser_service import XMLParserDIAN
from app.services.pdf_parser_service import PDFParserService

print("=" * 80)
print("ANÁLISIS DE DIFERENCIAS XML vs PDF")
print("=" * 80)

xml_dir = Path("/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE/CUFE-XML")
xml_files = list(xml_dir.glob("*.xml"))[:10]  # Probar con 10 archivos

# Estadísticas globales
stats = {
    'total_archivos': 0,
    'total_productos': 0,
    
    # Campos de factura
    'cufe_coincide': 0,
    'numero_coincide': 0,
    'fecha_coincide': 0,
    'total_coincide': 0,
    'subtotal_coincide': 0,
    'iva_coincide': 0,
    
    # Campos de productos
    'productos_cantidad_coincide': 0,
    'productos_descripcion_coincide': 0,
    'productos_precio_coincide': 0,
    'productos_iva_coincide': 0,
    'productos_codigo_coincide': 0,
    
    # Problemas específicos
    'pdf_sin_total': 0,
    'pdf_sin_subtotal': 0,
    'pdf_sin_iva': 0,
    'pdf_productos_menos': 0,
    'pdf_productos_mas': 0,
    'pdf_iva_producto_faltante': 0,
}

diferencias_detalladas = []

print(f"\n📊 Analizando {len(xml_files)} archivos...")
print("-" * 80)

for xml_file in xml_files:
    cufe = xml_file.stem
    pdf_file = xml_dir / f"{cufe}.pdf"
    
    if not pdf_file.exists():
        continue
    
    stats['total_archivos'] += 1
    
    try:
        # Parsear ambos
        datos_xml = XMLParserDIAN.parse_xml(str(xml_file))
        datos_pdf = PDFParserService.parse_dian_document(str(pdf_file))
        
        if not datos_xml or 'error' in datos_pdf:
            continue
        
        print(f"\n📄 [{stats['total_archivos']}] {datos_xml['numero_factura']}")
        print(f"   CUFE: {cufe[:40]}...")
        
        diferencias_archivo = {
            'cufe': cufe[:40],
            'numero_factura': datos_xml['numero_factura'],
            'problemas': []
        }
        
        # ===== COMPARAR CUFE =====
        cufe_xml = datos_xml.get('cufe', '')
        cufe_pdf = datos_pdf.get('cufe', '')
        
        if cufe_xml and cufe_pdf and cufe_xml == cufe_pdf:
            stats['cufe_coincide'] += 1
            print(f"   ✅ CUFE: Coincide")
        elif not cufe_pdf:
            print(f"   ⚠️ CUFE: PDF no extrajo CUFE")
            diferencias_archivo['problemas'].append('CUFE no extraído del PDF')
        else:
            print(f"   ❌ CUFE: No coincide")
            diferencias_archivo['problemas'].append('CUFE diferente')
        
        # ===== COMPARAR NÚMERO DE FACTURA =====
        num_xml = datos_xml.get('numero_factura', '')
        num_pdf = datos_pdf.get('numero_documento', '')
        
        if num_xml and num_pdf and num_xml == num_pdf:
            stats['numero_coincide'] += 1
            print(f"   ✅ Número: Coincide ({num_xml})")
        elif not num_pdf:
            print(f"   ⚠️ Número: PDF no extrajo número")
            diferencias_archivo['problemas'].append('Número no extraído del PDF')
        else:
            print(f"   ⚠️ Número: XML={num_xml}, PDF={num_pdf}")
            diferencias_archivo['problemas'].append(f'Número diferente: XML={num_xml}, PDF={num_pdf}')
        
        # ===== COMPARAR FECHA =====
        fecha_xml = datos_xml.get('fecha_emision', '')
        fecha_pdf = datos_pdf.get('fecha_emision')
        
        if fecha_xml and fecha_pdf:
            # Convertir a string para comparar
            fecha_pdf_str = str(fecha_pdf).split()[0] if fecha_pdf else ''
            if fecha_xml == fecha_pdf_str:
                stats['fecha_coincide'] += 1
                print(f"   ✅ Fecha: Coincide ({fecha_xml})")
            else:
                print(f"   ⚠️ Fecha: XML={fecha_xml}, PDF={fecha_pdf_str}")
                diferencias_archivo['problemas'].append(f'Fecha diferente: XML={fecha_xml}, PDF={fecha_pdf_str}')
        elif not fecha_pdf:
            print(f"   ⚠️ Fecha: PDF no extrajo fecha")
            diferencias_archivo['problemas'].append('Fecha no extraída del PDF')
        
        # ===== COMPARAR TOTALES =====
        totales_xml = datos_xml.get('totales', {})
        totales_pdf = datos_pdf.get('totales', {})
        
        # Total a pagar
        total_xml = totales_xml.get('total_pagar', 0)
        total_pdf = totales_pdf.get('total_pagar', 0)
        
        if total_xml and total_pdf:
            diferencia = abs(total_xml - total_pdf)
            if diferencia < 1:
                stats['total_coincide'] += 1
                print(f"   ✅ Total: Coincide (${total_xml:,.2f})")
            else:
                print(f"   ❌ Total: XML=${total_xml:,.2f}, PDF=${total_pdf:,.2f} (Dif: ${diferencia:,.2f})")
                diferencias_archivo['problemas'].append(f'Total diferente: XML=${total_xml:,.2f}, PDF=${total_pdf:,.2f}')
        elif not total_pdf:
            stats['pdf_sin_total'] += 1
            print(f"   ❌ Total: PDF no extrajo total (XML=${total_xml:,.2f})")
            diferencias_archivo['problemas'].append(f'Total no extraído del PDF (XML=${total_xml:,.2f})')
        
        # Subtotal
        subtotal_xml = totales_xml.get('subtotal', 0)
        subtotal_pdf = totales_pdf.get('subtotal', 0)
        
        if subtotal_xml and subtotal_pdf:
            diferencia = abs(subtotal_xml - subtotal_pdf)
            if diferencia < 1:
                stats['subtotal_coincide'] += 1
                print(f"   ✅ Subtotal: Coincide (${subtotal_xml:,.2f})")
            else:
                print(f"   ⚠️ Subtotal: XML=${subtotal_xml:,.2f}, PDF=${subtotal_pdf:,.2f}")
                diferencias_archivo['problemas'].append(f'Subtotal diferente: Dif=${diferencia:,.2f}')
        elif not subtotal_pdf:
            stats['pdf_sin_subtotal'] += 1
            print(f"   ⚠️ Subtotal: PDF no extrajo subtotal")
            diferencias_archivo['problemas'].append('Subtotal no extraído del PDF')
        
        # IVA
        iva_xml = totales_xml.get('total_impuestos', 0)
        iva_pdf = totales_pdf.get('total_impuestos', 0)
        
        if iva_xml and iva_pdf:
            diferencia = abs(iva_xml - iva_pdf)
            if diferencia < 1:
                stats['iva_coincide'] += 1
                print(f"   ✅ IVA: Coincide (${iva_xml:,.2f})")
            else:
                print(f"   ⚠️ IVA: XML=${iva_xml:,.2f}, PDF=${iva_pdf:,.2f}")
                diferencias_archivo['problemas'].append(f'IVA diferente: Dif=${diferencia:,.2f}')
        elif not iva_pdf:
            stats['pdf_sin_iva'] += 1
            print(f"   ⚠️ IVA: PDF no extrajo IVA")
            diferencias_archivo['problemas'].append('IVA no extraído del PDF')
        
        # ===== COMPARAR PRODUCTOS =====
        productos_xml = datos_xml.get('productos', [])
        productos_pdf = datos_pdf.get('productos', [])
        
        num_prod_xml = len(productos_xml)
        num_prod_pdf = len(productos_pdf)
        
        stats['total_productos'] += num_prod_xml
        
        if num_prod_xml == num_prod_pdf:
            stats['productos_cantidad_coincide'] += 1
            print(f"   ✅ Productos: Cantidad coincide ({num_prod_xml})")
        elif num_prod_pdf < num_prod_xml:
            stats['pdf_productos_menos'] += 1
            print(f"   ❌ Productos: PDF tiene menos (XML={num_prod_xml}, PDF={num_prod_pdf})")
            diferencias_archivo['problemas'].append(f'PDF extrae menos productos: XML={num_prod_xml}, PDF={num_prod_pdf}')
        else:
            stats['pdf_productos_mas'] += 1
            print(f"   ⚠️ Productos: PDF tiene más (XML={num_prod_xml}, PDF={num_prod_pdf})")
            diferencias_archivo['problemas'].append(f'PDF extrae más productos: XML={num_prod_xml}, PDF={num_prod_pdf}')
        
        # Comparar productos individuales (primeros 3)
        productos_sin_iva = 0
        for i in range(min(3, num_prod_xml, num_prod_pdf)):
            prod_xml = productos_xml[i]
            prod_pdf = productos_pdf[i]
            
            # IVA del producto
            iva_prod_xml = prod_xml.get('iva_porcentaje', 0)
            iva_prod_pdf = prod_pdf.get('iva_porcentaje', 0)
            
            if iva_prod_xml > 0 and iva_prod_pdf == 0:
                productos_sin_iva += 1
        
        if productos_sin_iva > 0:
            stats['pdf_iva_producto_faltante'] += productos_sin_iva
            print(f"   ⚠️ IVA Productos: {productos_sin_iva} productos sin IVA en PDF")
            diferencias_archivo['problemas'].append(f'{productos_sin_iva} productos sin IVA extraído')
        
        # Guardar si hay problemas
        if diferencias_archivo['problemas']:
            diferencias_detalladas.append(diferencias_archivo)
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

# ===== RESUMEN ESTADÍSTICO =====
print("\n" + "=" * 80)
print("RESUMEN ESTADÍSTICO")
print("=" * 80)

if stats['total_archivos'] > 0:
    print(f"\n📊 Archivos analizados: {stats['total_archivos']}")
    print(f"📦 Productos totales: {stats['total_productos']}")
    
    print(f"\n🎯 PRECISIÓN POR CAMPO:")
    print(f"   CUFE:           {stats['cufe_coincide']}/{stats['total_archivos']} ({stats['cufe_coincide']/stats['total_archivos']*100:.1f}%)")
    print(f"   Número:         {stats['numero_coincide']}/{stats['total_archivos']} ({stats['numero_coincide']/stats['total_archivos']*100:.1f}%)")
    print(f"   Fecha:          {stats['fecha_coincide']}/{stats['total_archivos']} ({stats['fecha_coincide']/stats['total_archivos']*100:.1f}%)")
    print(f"   Total:          {stats['total_coincide']}/{stats['total_archivos']} ({stats['total_coincide']/stats['total_archivos']*100:.1f}%)")
    print(f"   Subtotal:       {stats['subtotal_coincide']}/{stats['total_archivos']} ({stats['subtotal_coincide']/stats['total_archivos']*100:.1f}%)")
    print(f"   IVA:            {stats['iva_coincide']}/{stats['total_archivos']} ({stats['iva_coincide']/stats['total_archivos']*100:.1f}%)")
    print(f"   Cant. Productos: {stats['productos_cantidad_coincide']}/{stats['total_archivos']} ({stats['productos_cantidad_coincide']/stats['total_archivos']*100:.1f}%)")
    
    print(f"\n⚠️ PROBLEMAS IDENTIFICADOS:")
    print(f"   PDF sin total:           {stats['pdf_sin_total']} archivos")
    print(f"   PDF sin subtotal:        {stats['pdf_sin_subtotal']} archivos")
    print(f"   PDF sin IVA:             {stats['pdf_sin_iva']} archivos")
    print(f"   PDF con menos productos: {stats['pdf_productos_menos']} archivos")
    print(f"   PDF con más productos:   {stats['pdf_productos_mas']} archivos")
    print(f"   Productos sin IVA:       {stats['pdf_iva_producto_faltante']} productos")
    
    # Calcular precisión global
    campos_totales = stats['total_archivos'] * 7  # 7 campos principales
    campos_correctos = (
        stats['cufe_coincide'] +
        stats['numero_coincide'] +
        stats['fecha_coincide'] +
        stats['total_coincide'] +
        stats['subtotal_coincide'] +
        stats['iva_coincide'] +
        stats['productos_cantidad_coincide']
    )
    
    precision_global = (campos_correctos / campos_totales) * 100
    
    print(f"\n📈 PRECISIÓN GLOBAL DEL PDF:")
    print(f"   {campos_correctos}/{campos_totales} campos correctos")
    print(f"   {precision_global:.1f}% de precisión")
    
    # Identificar el 5% problemático
    campos_problematicos = campos_totales - campos_correctos
    porcentaje_problematico = (campos_problematicos / campos_totales) * 100
    
    print(f"\n🎯 EL {porcentaje_problematico:.1f}% PROBLEMÁTICO:")
    
    problemas_ordenados = [
        ('Total no extraído', stats['pdf_sin_total']),
        ('Subtotal no extraído', stats['pdf_sin_subtotal']),
        ('IVA no extraído', stats['pdf_sin_iva']),
        ('Menos productos', stats['pdf_productos_menos']),
        ('Más productos', stats['pdf_productos_mas']),
        ('IVA productos faltante', stats['pdf_iva_producto_faltante']),
    ]
    
    problemas_ordenados.sort(key=lambda x: x[1], reverse=True)
    
    for problema, cantidad in problemas_ordenados:
        if cantidad > 0:
            porcentaje = (cantidad / stats['total_archivos']) * 100
            print(f"   • {problema}: {cantidad} casos ({porcentaje:.1f}%)")

# ===== DETALLE DE ARCHIVOS CON PROBLEMAS =====
if diferencias_detalladas:
    print(f"\n" + "=" * 80)
    print(f"ARCHIVOS CON PROBLEMAS ({len(diferencias_detalladas)})")
    print("=" * 80)
    
    for i, diff in enumerate(diferencias_detalladas[:5], 1):  # Mostrar primeros 5
        print(f"\n[{i}] {diff['numero_factura']} (CUFE: {diff['cufe']}...)")
        for problema in diff['problemas']:
            print(f"    • {problema}")

print("\n✅ Análisis completado!")
