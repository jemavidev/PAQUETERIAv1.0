#!/usr/bin/env python3
"""
Script para reprocesar facturas que no tienen productos extraídos
Usa el parser mejorado para extraer productos
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Cargar variables de entorno
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ Error: DATABASE_URL no está configurada")
    sys.exit(1)

engine = create_engine(DATABASE_URL)

def main():
    print("=" * 80)
    print("🔄 REPROCESAR FACTURAS SIN PRODUCTOS")
    print("=" * 80)
    print()
    
    with engine.connect() as conn:
        # Obtener facturas completas sin productos
        query = text('''
            SELECT 
                i.cufe,
                i.proveedor_nombre,
                i.numero_factura,
                i.dian_datos_raw
            FROM invoices_v2 i
            WHERE i.estado = 'completo' 
            AND i.cufe NOT IN (SELECT DISTINCT cufe FROM invoice_products_v2)
            ORDER BY i.created_at DESC
        ''')
        
        result = conn.execute(query)
        facturas = result.fetchall()
        
        if not facturas:
            print("✅ No hay facturas sin productos para reprocesar")
            return
        
        print(f"📊 Encontradas {len(facturas)} facturas sin productos")
        print()
        
        # Importar el parser
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from src.app.services.pdf_parser_service import PDFParserService
        
        parser = PDFParserService()
        
        total_productos_extraidos = 0
        
        for i, factura in enumerate(facturas, 1):
            cufe = factura[0]
            proveedor = factura[1] or 'Sin proveedor'
            numero = factura[2] or 'Sin número'
            datos_raw = factura[3]
            
            print(f"{i}. {proveedor[:40]:40s} | {numero[:15]:15s}")
            
            if not datos_raw or 'raw_text' not in datos_raw:
                print("   ⚠️  No hay texto raw guardado")
                continue
            
            raw_text = datos_raw['raw_text']
            
            # Extraer productos
            productos = parser._extract_productos(raw_text)
            
            if productos:
                print(f"   ✅ Extraídos {len(productos)} productos")
                
                # Insertar productos en la BD
                for prod in productos:
                    insert_query = text('''
                        INSERT INTO invoice_products_v2 
                        (cufe, codigo_producto, descripcion, cantidad, unidad_medida, 
                         precio_unitario, iva_porcentaje, total_item, fecha_compra)
                        VALUES 
                        (:cufe, :codigo, :descripcion, :cantidad, :unidad, 
                         :precio, :iva, :total, 
                         (SELECT fecha_emision FROM invoices_v2 WHERE cufe = :cufe))
                    ''')
                    
                    conn.execute(insert_query, {
                        'cufe': cufe,
                        'codigo': prod.get('codigo_producto'),
                        'descripcion': prod.get('descripcion'),
                        'cantidad': prod.get('cantidad'),
                        'unidad': prod.get('unidad_medida'),
                        'precio': prod.get('precio_unitario'),
                        'iva': prod.get('iva_porcentaje'),
                        'total': prod.get('total_item')
                    })
                
                conn.commit()
                total_productos_extraidos += len(productos)
                
                # Mostrar primeros 3 productos
                for j, prod in enumerate(productos[:3], 1):
                    codigo = prod.get('codigo_producto', 'N/A')
                    desc = prod.get('descripcion', 'N/A')[:40]
                    precio = prod.get('precio_unitario', 0)
                    print(f"      {j}. {codigo} - {desc}... (${precio:,.0f})")
                
                if len(productos) > 3:
                    print(f"      ... y {len(productos) - 3} más")
            else:
                print("   ❌ No se pudieron extraer productos")
            
            print()
        
        print("=" * 80)
        print(f"✅ Reprocesamiento completado")
        print(f"📦 Total de productos extraídos: {total_productos_extraidos}")
        print("=" * 80)

if __name__ == '__main__':
    main()
