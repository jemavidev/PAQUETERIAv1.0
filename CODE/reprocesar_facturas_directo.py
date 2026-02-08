#!/usr/bin/env python3
"""
Script para reprocesar facturas directamente en la BD
Sin necesidad de resubir archivos por la interfaz web
"""
import os
import sys
import re
from decimal import Decimal
from datetime import datetime

# Configurar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ Error: DATABASE_URL no está configurada")
    sys.exit(1)

engine = create_engine(DATABASE_URL)

# Copiar la función _extract_productos actualizada directamente aquí
def extract_productos(text: str):
    """
    Extrae productos del documento DIAN con el parser actualizado
    """
    import logging
    logger = logging.getLogger(__name__)
    
    productos = []
    
    # Buscar sección de productos
    patterns = [
        r'(?:Detalles de [Pp]roductos|Detalle de Ítems|DETALLE DE PRODUCTOS|DETALLE)([\s\S]{0,15000}?)(?:Notas [Ff]inales|Datos [Tt]otales|Observaciones|OBSERVACIONES|Total factura|TOTAL FACTURA|IVA=)',
        r'(?:DESCRIPCIÓN|DESCRIPCION|Descripción del Producto)([\s\S]{0,15000}?)(?:Notas|NOTAS|Total|TOTAL|IVA=|Observaciones)',
        r'(?:Item|ITEM|Ítem|ÍTEM)([\s\S]{0,15000}?)(?:Subtotal|SUBTOTAL|Total|TOTAL|IVA=)',
        r'(?:Código\s+Cantidad|CODIGO\s+CANTIDAD)([\s\S]{0,15000}?)(?:Subtotal|SUBTOTAL|Total|TOTAL|IVA=|Observaciones|DESPUES DE)',
        r'(?:No\.\s+Código\s+Descripción|Código\s+Descripción\s+U/M)([\s\S]{0,15000}?)(?:Subtotal|SUBTOTAL|Total|TOTAL|Observaciones|OBSERVACIONES)',
    ]
    
    productos_section = None
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            productos_section = match.group(1)
            print(f"   ✅ Sección de productos encontrada")
            break
    
    if not productos_section:
        print(f"   ❌ No se encontró sección de productos")
        return productos
    
    lines = productos_section.split('\n')
    
    i = 0
    while i < len(lines) and len(productos) < 200:
        line = lines[i].strip()
        
        # FORMATO 0: Nuevo formato con descripción entre código y U/M
        match_formato_nuevo = re.match(
            r'^(\d{1,3})\s+(\d{3,13})\s+(.+?)\s+(\d{2,3})\s+([0-9]+[.,][0-9]{2})\s+\$\s*([0-9.,]+)',
            line
        )
        
        if match_formato_nuevo:
            try:
                nro = match_formato_nuevo.group(1)
                codigo = match_formato_nuevo.group(2)
                descripcion = match_formato_nuevo.group(3).strip()
                unidad_codigo = match_formato_nuevo.group(4)
                cantidad_str = match_formato_nuevo.group(5).replace(',', '.')
                precio_unit_str = match_formato_nuevo.group(6).replace('.', '').replace(',', '.')
                
                cantidad = float(cantidad_str)
                precio_unitario = float(precio_unit_str)
                
                # Mapear código de unidad
                unidad_map = {'94': 'NIU', '10': 'PK', '11': 'BX', '01': 'UND'}
                unidad = unidad_map.get(unidad_codigo, 'NIU')
                
                # Limpiar descripción
                descripcion = re.sub(r'\s+', ' ', descripcion)
                descripcion = descripcion[:250]
                
                # Buscar todos los valores monetarios
                valores = re.findall(r'\$\s*([0-9]{1,3}(?:[.,][0-9]{3})*(?:[.,][0-9]{2})?)', line)
                
                # Buscar IVA porcentaje
                iva_porcentaje = 0.0
                iva_match = re.search(r'\$\s*[0-9.,]+\s+(\d{1,2})[.,]00\s+\$', line)
                if iva_match:
                    iva_porcentaje = float(iva_match.group(1))
                
                # Total es el último valor monetario
                total_item = None
                if valores:
                    try:
                        total_str = valores[-1].replace('.', '').replace(',', '.')
                        total_item = float(total_str)
                    except:
                        pass
                
                if not total_item:
                    total_item = precio_unitario * cantidad
                
                productos.append({
                    'codigo_producto': codigo,
                    'descripcion': descripcion,
                    'cantidad': cantidad,
                    'unidad_medida': unidad,
                    'precio_unitario': precio_unitario,
                    'iva_porcentaje': iva_porcentaje,
                    'total_item': total_item,
                })
                
            except Exception as e:
                pass
                
            i += 1
            continue
        
        # FORMATO 1: CUFE original
        match_producto = re.match(
            r'^(\d{1,3})\s+(\d{3,13})?\s+(NIU|PK|BX|UND|UN)?\s+([0-9]+[.,][0-9]{2})\s+\$\s*([0-9.,]+)',
            line
        )
        
        if match_producto:
            try:
                nro = match_producto.group(1)
                codigo = match_producto.group(2) if match_producto.group(2) else ""
                unidad = match_producto.group(3) if match_producto.group(3) else "NIU"
                cantidad_str = match_producto.group(4).replace(',', '.')
                precio_unit_str = match_producto.group(5).replace('.', '').replace(',', '.')
                
                cantidad = float(cantidad_str)
                precio_unitario = float(precio_unit_str)
                
                # Buscar descripción en línea anterior
                descripcion = ""
                if i > 0:
                    prev_line = lines[i-1].strip()
                    if prev_line and not re.match(r'^\d+\s', prev_line):
                        descripcion = prev_line
                
                if not descripcion and i + 1 < len(lines):
                    next_line = lines[i+1].strip()
                    if next_line and not re.match(r'^\d+\s', next_line):
                        descripcion = next_line
                
                descripcion = re.sub(r'\s+', ' ', descripcion)
                descripcion = descripcion[:250]
                
                # Buscar total
                valores = re.findall(r'\$\s*([0-9]{1,3}(?:[.,][0-9]{3})*(?:[.,][0-9]{2})?)', line)
                total_item = None
                if valores:
                    try:
                        total_str = valores[-1].replace('.', '').replace(',', '.')
                        total_item = float(total_str)
                    except:
                        pass
                
                # Buscar IVA
                iva_porcentaje = 0.0
                iva_match = re.search(r'(\d{1,2})[.,]00\s+', line)
                if iva_match:
                    iva_porcentaje = float(iva_match.group(1))
                
                if not codigo:
                    codigo = f"ITEM-{nro}"
                
                productos.append({
                    'codigo_producto': codigo,
                    'descripcion': descripcion if descripcion else f"Producto {nro}",
                    'cantidad': cantidad,
                    'unidad_medida': unidad,
                    'precio_unitario': precio_unitario,
                    'iva_porcentaje': iva_porcentaje,
                    'total_item': total_item if total_item else (precio_unitario * cantidad),
                })
                
            except Exception as e:
                pass
        
        i += 1
    
    return productos


def main():
    print("=" * 80)
    print("🔄 REPROCESAMIENTO AUTOMÁTICO DE FACTURAS")
    print("=" * 80)
    print()
    
    with engine.connect() as conn:
        # Obtener facturas completas sin productos
        query = text('''
            SELECT 
                i.cufe,
                i.proveedor_nombre,
                i.numero_factura,
                i.dian_datos_raw,
                i.fecha_emision
            FROM invoices_v2 i
            WHERE i.estado = 'completo' 
            AND i.cufe NOT IN (
                SELECT DISTINCT cufe 
                FROM invoice_products_v2 
                WHERE cufe LIKE '6ee372e2%'
            )
            ORDER BY i.created_at DESC
        ''')
        
        result = conn.execute(query)
        facturas = result.fetchall()
        
        if not facturas:
            print("✅ No hay facturas sin productos para reprocesar")
            print()
            # Mostrar resumen actual
            result = conn.execute(text('SELECT COUNT(*) FROM invoice_products_v2'))
            total = result.scalar()
            print(f"📦 Total de productos actuales: {total}")
            return
        
        print(f"📊 Encontradas {len(facturas)} facturas sin productos")
        print()
        
        total_productos_extraidos = 0
        
        for i, factura in enumerate(facturas, 1):
            cufe = factura[0]
            proveedor = factura[1] or 'Sin proveedor'
            numero = factura[2] or 'Sin número'
            datos_raw = factura[3]
            fecha_emision = factura[4]
            
            print(f"{i}. {proveedor[:40]:40s} | {numero[:15]:15s}")
            
            if not datos_raw or 'raw_text' not in datos_raw:
                print("   ⚠️  No hay texto raw guardado")
                continue
            
            raw_text = datos_raw['raw_text']
            
            # Extraer productos
            productos = extract_productos(raw_text)
            
            if productos:
                print(f"   ✅ Extraídos {len(productos)} productos")
                
                # Insertar productos en la BD
                for prod in productos:
                    insert_query = text('''
                        INSERT INTO invoice_products_v2 
                        (cufe, codigo_producto, descripcion, cantidad, unidad_medida, 
                         precio_unitario, iva_porcentaje, total_item, fecha_compra, created_at)
                        VALUES 
                        (:cufe, :codigo, :descripcion, :cantidad, :unidad, 
                         :precio, :iva, :total, :fecha, :created_at)
                    ''')
                    
                    conn.execute(insert_query, {
                        'cufe': cufe,
                        'codigo': prod.get('codigo_producto'),
                        'descripcion': prod.get('descripcion'),
                        'cantidad': prod.get('cantidad'),
                        'unidad': prod.get('unidad_medida'),
                        'precio': prod.get('precio_unitario'),
                        'iva': prod.get('iva_porcentaje'),
                        'total': prod.get('total_item'),
                        'fecha': fecha_emision,
                        'created_at': datetime.now()
                    })
                
                conn.commit()
                total_productos_extraidos += len(productos)
                
                # Mostrar primeros 3 productos
                for j, prod in enumerate(productos[:3], 1):
                    codigo = prod.get('codigo_producto', 'N/A')
                    desc = prod.get('descripcion', 'N/A')[:40]
                    precio = prod.get('precio_unitario', 0)
                    print(f"      {j}. {codigo:10s} - {desc:40s} (${precio:,.0f})")
                
                if len(productos) > 3:
                    print(f"      ... y {len(productos) - 3} más")
            else:
                print("   ❌ No se pudieron extraer productos")
            
            print()
        
        print("=" * 80)
        print(f"✅ Reprocesamiento completado")
        print(f"📦 Productos extraídos en esta ejecución: {total_productos_extraidos}")
        print()
        
        # Mostrar resumen final
        result = conn.execute(text('SELECT COUNT(*) FROM invoice_products_v2'))
        total_final = result.scalar()
        print(f"📊 TOTAL DE PRODUCTOS EN BD: {total_final}")
        print()
        
        # Productos por proveedor
        result = conn.execute(text('''
            SELECT i.proveedor_nombre, COUNT(p.id) as total
            FROM invoices_v2 i 
            LEFT JOIN invoice_products_v2 p ON i.cufe = p.cufe 
            WHERE i.estado = 'completo' 
            GROUP BY i.proveedor_nombre
            ORDER BY total DESC
        '''))
        
        print("📦 Productos por proveedor:")
        for row in result:
            proveedor = row[0] or 'Sin nombre'
            total = row[1]
            print(f"   - {proveedor[:45]:45s}: {total:3d} productos")
        
        print("=" * 80)

if __name__ == '__main__':
    main()
