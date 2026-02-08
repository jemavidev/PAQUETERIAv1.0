#!/usr/bin/env python3
"""
Script para reprocesar las facturas con productos faltantes
"""
import sys
import os
sys.path.insert(0, 'src')

from app.database import SessionLocal
from app.models.invoice_v2 import InvoiceV2, InvoiceProductV2
from app.services.pdf_parser_service import PDFParserService
from app.services.s3_service import S3Service
import tempfile

db = SessionLocal()
parser = PDFParserService()
s3_service = S3Service()

print('=' * 80)
print('REPROCESANDO FACTURAS CON PRODUCTOS FALTANTES')
print('=' * 80)

# Facturas a reprocesar (con CUFEs correctos de la BD)
facturas_a_reprocesar = [
    {
        'numero': '2FE-438',
        'cufe': '88f565e6a165010edd2680ea0f37c2453f3d2a11e2b58fcff298241c760f260cafef0dbed0b6214df2e67a3895ea6132',
        'productos_actuales': 3,
        'productos_esperados': 10,
    },
    {
        'numero': 'FE-15778',
        'cufe': '7569152b6d0396f9e5079cbac6bc56df5b0cd68fb260984838efb60f74d3f5ad1c33a597f92eed3e2318402d2eb418d2',
        'productos_actuales': 28,
        'productos_esperados': 58,
    },
]

total_productos_antes = 0
total_productos_despues = 0

for factura_info in facturas_a_reprocesar:
    cufe = factura_info['cufe']
    numero = factura_info['numero']
    
    print(f'\n📄 {numero} ({cufe[:20]}...)')
    print(f'   Productos actuales: {factura_info["productos_actuales"]}')
    print(f'   Productos esperados: {factura_info["productos_esperados"]}')
    
    # Obtener factura de la BD
    factura = db.query(InvoiceV2).filter_by(cufe=cufe).first()
    if not factura:
        print(f'   ❌ Factura no encontrada en BD')
        continue
    
    productos_antes = len(factura.productos)
    total_productos_antes += productos_antes
    
    # Descargar archivo DIAN desde S3
    if not factura.archivo_dian_s3_key:
        print(f'   ❌ No hay archivo DIAN en S3')
        continue
    
    print(f'   📥 Descargando desde S3: {factura.archivo_dian_s3_key}')
    
    try:
        # Descargar desde S3
        file_bytes = s3_service.download_file(factura.archivo_dian_s3_key)
        
        if not file_bytes:
            print(f'   ❌ Error descargando archivo desde S3')
            continue
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(file_bytes)
            tmp_path = tmp_file.name
        
        print(f'   ✅ Archivo descargado: {tmp_path}')
        
        # Parsear el archivo DIAN nuevamente
        print(f'   📄 Parseando archivo con parser mejorado...')
        data = parser.parse_dian_document(tmp_path)
        
        if 'error' in data:
            print(f'   ❌ Error: {data["error"]}')
            os.unlink(tmp_path)
            continue
        
        productos_nuevos = data.get('productos', [])
        print(f'   📦 Productos extraídos: {len(productos_nuevos)}')
        
        if len(productos_nuevos) == productos_antes:
            print(f'   ⚠️ Misma cantidad de productos, no hay cambios')
            os.unlink(tmp_path)
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
        
        # Limpiar archivo temporal
        os.unlink(tmp_path)
        
    except Exception as e:
        print(f'   ❌ Error: {e}')
        import traceback
        traceback.print_exc()
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        continue

print('\n' + '=' * 80)
print('RESUMEN')
print('=' * 80)
print(f'Total productos antes: {total_productos_antes}')
print(f'Total productos después: {total_productos_despues}')
print(f'Diferencia: +{total_productos_despues - total_productos_antes}')
print('\n📊 TOTAL EN BD:')
total_bd = db.query(InvoiceProductV2).count()
print(f'   {total_bd} productos')
print(f'   Esperado: 90')
print(f'   Faltantes: {90 - total_bd}')
print('=' * 80)

db.close()
