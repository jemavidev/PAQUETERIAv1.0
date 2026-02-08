#!/usr/bin/env python3
"""
Test FORMATO_5 parser implementation
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.services.pdf_parser_service import PDFParserService

def test_formato5():
    pdf_path = '/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE/CUFE/fd7892b8723009bb46c2f065caa325144d76ee5e3eada87cf2dce405dc23b0b4e5938e060c94fa4c3f846220c56dc4e1.pdf'
    
    print("="*100)
    print("🧪 TEST FORMATO_5 - Sin código de producto")
    print("="*100)
    print(f"Archivo: {pdf_path.split('/')[-1]}")
    print()
    
    # Parse document
    result = PDFParserService.parse_dian_document(pdf_path)
    
    productos = result.get('productos', [])
    
    print(f"📦 PRODUCTOS EXTRAÍDOS: {len(productos)}")
    print("="*100)
    
    if not productos:
        print("❌ No se extrajeron productos")
        return
    
    # Show first 10 products
    for i, prod in enumerate(productos[:15], 1):
        print(f"\n{i}. Producto:")
        print(f"   Código: {prod.get('codigo_producto', 'N/A')}")
        print(f"   Descripción: {prod.get('descripcion', 'N/A')[:60]}...")
        print(f"   Cantidad: {prod.get('cantidad', 'N/A')}")
        print(f"   Unidad: {prod.get('unidad_medida', 'N/A')}")
        print(f"   Precio Unit.: ${prod.get('precio_unitario', 0):,.2f}")
        print(f"   IVA: {prod.get('iva_porcentaje', 0)}%")
        print(f"   Total: ${prod.get('total_item', 0):,.2f}")
    
    if len(productos) > 15:
        print(f"\n... y {len(productos) - 15} productos más")
    
    print("\n" + "="*100)
    print(f"✅ Test completado - {len(productos)} productos extraídos")
    print("="*100)

if __name__ == '__main__':
    test_formato5()
