#!/usr/bin/env python3
"""
Script para reprocesar las facturas DIAN con el parser mejorado
"""
import sys
import os
sys.path.insert(0, 'src')

from app.database import SessionLocal
from app.models.invoice_v2 import InvoiceV2, InvoiceProductV2
from app.services.pdf_parser_service import PDFParserService

db = SessionLocal()
parser = PDFParserService()

print('=' * 80)
print('REPROCESANDO FACTURAS CON PARSER MEJORADO')
print('=' * 80)

# CUFEs de las facturas a reprocesar
facturas_a_reprocesar = [
    {
        'cufe': '6ee372e238cc82c3d95fa44faa0869cd5c6e0e45d51cef31b9828697aad65af8f2e3a89ff13f799961ad968c89503f8e',
        'numero': '006D-611',
        'productos_actuales': 18,
        'productos_esperados': 20,
        'archivo': '../CUFE/FACTURAS/6ee372e238cc82c3d95fa44faa0869cd5c6e0e45d51cef31b9828697aad65af8f2e3a89ff13f799961ad968c89503f8e_20250724151930.pdf'
    },
    # Agregar las otras facturas aquí cuando tengamos sus archivos
]

total_productos_antes = 0
total_productos_despues = 0

for factura_info in facturas_a_reprocesar:
    cufe = factura_info['cufe']
    numero = factura_info['numero']
    archivo = factura_info['archivo']
    
    print(f'\n{numero} ({cufe[:20]}...)')
    print(f'   Productos actuales: {factura_info["productos_actuales"]}')
    print(f'   Productos esperados: {factura_info["productos_esperados"]}')
    
    if not os.path.exists(archivo):
        print(f'   ❌ Archivo no encontrado: {archivo}')
        continue
    
    # Obtener factura de la BD
    factura = db.query(InvoiceV2).filter_by(cufe=cufe).first()
    if not factura:
        print(f'   ❌ Factura no encontrada en BD')
        continue
    
    productos_antes = len(factura.productos)
    total_productos_antes += productos_antes
    
    # Parsear el archivo DIAN nuevamente
    print(f'   📄 Parseando archivo...')
    data = parser.parse_dian_document(archivo)
    
    if 'error' in data:
        print(f'   ❌ Error: {data["error"]}')
        continue
    
    productos_nuevos = data.get('productos', [])
    print(f'   📦 Productos extraídos: {len(productos_nuevos)}')
    
    if len(productos_nuevos) == productos_antes:
        print(f'   ⚠️ Misma cantidad de productos, no hay cambios')
        continue
    
    # Eliminar productos antiguos
    print(f'   🗑️ Eliminando {productos_antes} productos antiguos...')
    db.query(InvoiceProductV2).filter_by(cufe=cufe).delete()
    
    # Insertar productos nuevos
    print(f'   ➕ Insertando {len(productos_nuevos)} productos nuevos...')
    fecha_compra = factura.fecha_emision.date() if factura.fecha_emision else None
    
    for i, prod_data in enumerate(productos_nuevos):
        producto = InvoiceProductV2(
            cufe=cufe,
            linea_numero=i + 1,
            codigo_producto=prod_data.get('codigo_producto'),
            descripcion=prod_data.get('descripcion'),
            cantidad=prod_data.get('cantidad'),
            unidad_medida=prod_data.get('unidad_medida'),
            precio_unitario=prod_data.get('precio_unitario'),
            iva_porcentaje=prod_data.get('iva_porcentaje'),
            total_item=prod_data.get('total_item'),
            fecha_compra=fecha_compra,
            datos_raw=prod_data
        )
        db.add(producto)
    
    db.commit()
    
    productos_despues = len(productos_nuevos)
    total_productos_despues += productos_despues
    
    print(f'   ✅ Completado: {productos_antes} → {productos_despues} productos')

print('\n' + '=' * 80)
print('RESUMEN')
print('=' * 80)
print(f'Total productos antes: {total_productos_antes}')
print(f'Total productos después: {total_productos_despues}')
print(f'Diferencia: +{total_productos_despues - total_productos_antes}')
print('=' * 80)

db.close()
