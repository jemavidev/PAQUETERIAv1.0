#!/usr/bin/env python3
"""
Prueba de integración para verificar la extracción de productos CUFE
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'CODE/src'))

from app.services.pdf_parser_service import PDFParserService
from pathlib import Path

def test_cufe_extraction():
    """Prueba la extracción de productos de archivos CUFE"""
    
    cufe_dir = Path("/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE/CUFE")
    
    if not cufe_dir.exists():
        print(f"✗ Directorio no encontrado: {cufe_dir}")
        return
    
    pdf_files = list(cufe_dir.glob("*.pdf"))
    print(f"\n{'='*80}")
    print(f"Prueba de Integración - Extracción de Productos CUFE")
    print(f"{'='*80}\n")
    print(f"Archivos encontrados: {len(pdf_files)}")
    
    # Probar con 3 archivos
    for i, pdf_file in enumerate(pdf_files[:3], 1):
        print(f"\n{'='*80}")
        print(f"Archivo {i}: {pdf_file.name[:60]}...")
        print(f"{'='*80}")
        
        try:
            # Usar el servicio real
            result = PDFParserService.parse_dian_document(str(pdf_file))
            
            if result:
                print(f"✓ PDF parseado exitosamente")
                print(f"\nInformación General:")
                print(f"  - CUFE: {result.get('cufe', 'N/A')[:60]}...")
                print(f"  - Número Factura: {result.get('numero_factura', 'N/A')}")
                print(f"  - Fecha Emisión: {result.get('fecha_emision', 'N/A')}")
                print(f"  - Emisor: {result.get('emisor_nombre', 'N/A')}")
                print(f"  - Adquiriente: {result.get('adquiriente_nombre', 'N/A')}")
                
                productos = result.get('productos', [])
                print(f"\n✓ Productos extraídos: {len(productos)}")
                
                if productos:
                    print(f"\nPrimeros 5 productos:")
                    for j, prod in enumerate(productos[:5], 1):
                        print(f"\n  {j}. Código: {prod.get('codigo_producto', 'N/A')}")
                        desc = prod.get('descripcion', 'N/A')
                        print(f"     Descripción: {desc[:80]}{'...' if len(desc) > 80 else ''}")
                        print(f"     Cantidad: {prod.get('cantidad', 0)} {prod.get('unidad_medida', 'NIU')}")
                        print(f"     Precio Unit: ${prod.get('precio_unitario', 0):,.2f}")
                        print(f"     IVA: {prod.get('iva_porcentaje', 0)}%")
                        print(f"     Total: ${prod.get('total_item', 0):,.2f}")
                else:
                    print("  ⚠ No se extrajeron productos")
                
                # Verificar totales
                totales = result.get('totales', {})
                if totales:
                    print(f"\nTotales:")
                    print(f"  - Subtotal: ${totales.get('subtotal', 0):,.2f}")
                    print(f"  - IVA: ${totales.get('iva', 0):,.2f}")
                    print(f"  - Total: ${totales.get('total_factura', 0):,.2f}")
            else:
                print("✗ No se pudo parsear el PDF")
                
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_cufe_extraction()
