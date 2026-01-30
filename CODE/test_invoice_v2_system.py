#!/usr/bin/env python3
"""
Script de prueba para el sistema de facturas V2
Prueba la extracción de datos de PDFs de proveedores y DIAN
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.app.services.pdf_parser_service import PDFParserService


def test_provider_invoice(pdf_path: str):
    """Prueba extracción de factura de proveedor"""
    print(f"\n{'='*80}")
    print(f"PROBANDO FACTURA DE PROVEEDOR: {os.path.basename(pdf_path)}")
    print(f"{'='*80}\n")
    
    parser = PDFParserService()
    result = parser.parse_provider_invoice(pdf_path)
    
    if 'error' in result:
        print(f"❌ ERROR: {result['error']}")
        return
    
    print("✅ DATOS EXTRAÍDOS:")
    print(f"   CUFE: {result.get('cufe', 'NO ENCONTRADO')}")
    print(f"   Proveedor: {result.get('proveedor_nombre', 'NO ENCONTRADO')}")
    print(f"   NIT: {result.get('proveedor_nit', 'NO ENCONTRADO')}")
    print(f"   Fecha: {result.get('fecha_emision', 'NO ENCONTRADO')}")
    print(f"   Número: {result.get('numero_factura', 'NO ENCONTRADO')}")
    print(f"   Total: ${result.get('total_factura', 'NO ENCONTRADO')}")
    print()


def test_dian_document(pdf_path: str):
    """Prueba extracción de documento DIAN"""
    print(f"\n{'='*80}")
    print(f"PROBANDO DOCUMENTO DIAN: {os.path.basename(pdf_path)}")
    print(f"{'='*80}\n")
    
    parser = PDFParserService()
    result = parser.parse_dian_document(pdf_path)
    
    if 'error' in result:
        print(f"❌ ERROR: {result['error']}")
        return
    
    print("✅ DATOS EXTRAÍDOS:")
    print(f"\n📄 DOCUMENTO:")
    print(f"   CUFE: {result.get('cufe', 'NO ENCONTRADO')}")
    print(f"   Tipo: {result.get('tipo_documento', 'NO ENCONTRADO')}")
    print(f"   Número: {result.get('numero_documento', 'NO ENCONTRADO')}")
    print(f"   Fecha: {result.get('fecha_emision', 'NO ENCONTRADO')}")
    
    emisor = result.get('emisor', {})
    print(f"\n🏢 EMISOR:")
    print(f"   Razón Social: {emisor.get('razon_social', 'NO ENCONTRADO')}")
    print(f"   NIT: {emisor.get('nit', 'NO ENCONTRADO')}")
    print(f"   Dirección: {emisor.get('direccion', 'NO ENCONTRADO')}")
    print(f"   Teléfono: {emisor.get('telefono', 'NO ENCONTRADO')}")
    print(f"   Email: {emisor.get('email', 'NO ENCONTRADO')}")
    
    adquiriente = result.get('adquiriente', {})
    print(f"\n👤 ADQUIRIENTE:")
    print(f"   Razón Social: {adquiriente.get('razon_social', 'NO ENCONTRADO')}")
    print(f"   NIT: {adquiriente.get('nit', 'NO ENCONTRADO')}")
    
    print(f"\n💰 CONDICIONES:")
    print(f"   Forma de Pago: {result.get('forma_pago', 'NO ENCONTRADO')}")
    print(f"   Medio de Pago: {result.get('medio_pago', 'NO ENCONTRADO')}")
    print(f"   Moneda: {result.get('moneda', 'NO ENCONTRADO')}")
    
    totales = result.get('totales', {})
    print(f"\n💵 TOTALES:")
    print(f"   Subtotal: ${totales.get('subtotal', 'NO ENCONTRADO')}")
    print(f"   IVA: ${totales.get('total_iva', 'NO ENCONTRADO')}")
    print(f"   Total Neto: ${totales.get('total_neto', 'NO ENCONTRADO')}")
    
    productos = result.get('productos', [])
    print(f"\n📦 PRODUCTOS ({len(productos)}):")
    for i, prod in enumerate(productos[:5], 1):  # Mostrar solo los primeros 5
        print(f"   {i}. {prod.get('descripcion', 'SIN DESCRIPCIÓN')[:50]}")
        print(f"      Código: {prod.get('codigo_producto', 'NO ENCONTRADO')}")
    
    if len(productos) > 5:
        print(f"   ... y {len(productos) - 5} productos más")
    
    print(f"\n🔧 TÉCNICO:")
    print(f"   Proveedor Tecnológico: {result.get('proveedor_tecnologico', 'NO ENCONTRADO')}")
    resolucion = result.get('resolucion', {})
    print(f"   Resolución: {resolucion.get('numero', 'NO ENCONTRADO')}")
    print()


def main():
    """Función principal"""
    print("\n" + "="*80)
    print("SISTEMA DE FACTURAS V2 - PRUEBA DE EXTRACCIÓN DE PDFs")
    print("="*80)
    
    # Rutas de ejemplo (ajustar según tus archivos)
    facturas_proveedor = [
        "CUFE/FACTURAS/4fd2e062479406514410645181a51db2e951f2524ff8725694e09ae48993d4a762e85ec23981ab6f9203c0ad9a3c4a8d_20250718184935.pdf",
        "CUFE/FACTURAS/ad00454539650892500016738.pdf",
        "CUFE/FACTURAS/f-0e343f465a14be839f22266faf42b928203c20058ab340cdbc97dd74fd63ec7d0d8eabd261062ccd23cfb20944650265_20250922121213.pdf",
    ]
    
    documentos_dian = [
        "CUFE/CUFE/7fc31ab6fa2617965c9e21ea4072a282e6961402dc3771453384c41f715d990b1808460c2d91c7fc7690c3db726555f1.pdf",
        "CUFE/CUFE/6840c2056a31229d87fcf4b4619dce5c231142fefecd37da454cd160b028541dbe5a58e480cfd9690d1a863ab1bb6d08.pdf",
        "CUFE/CUFE/c1f9ee537c5ba528a05b5bc4de0c3476900d6dd0968a1803ad298a789f98449eb1147bce6e1200cb49f57c0cfd944c96.pdf",
    ]
    
    # Probar facturas de proveedores
    print("\n" + "🔵"*40)
    print("PROBANDO FACTURAS DE PROVEEDORES")
    print("🔵"*40)
    
    for pdf in facturas_proveedor:
        if os.path.exists(pdf):
            test_provider_invoice(pdf)
        else:
            print(f"\n⚠️  Archivo no encontrado: {pdf}")
    
    # Probar documentos DIAN
    print("\n" + "🟢"*40)
    print("PROBANDO DOCUMENTOS DIAN")
    print("🟢"*40)
    
    for pdf in documentos_dian:
        if os.path.exists(pdf):
            test_dian_document(pdf)
        else:
            print(f"\n⚠️  Archivo no encontrado: {pdf}")
    
    print("\n" + "="*80)
    print("PRUEBAS COMPLETADAS")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
