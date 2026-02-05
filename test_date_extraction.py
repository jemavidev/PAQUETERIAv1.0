#!/usr/bin/env python3
"""
Script para probar la extracción de fecha de documentos DIAN
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'CODE/src'))

from app.services.pdf_parser_service import PDFParserService

def test_date_extraction(pdf_path):
    """Test de extracción de fecha"""
    print(f"\n{'='*80}")
    print(f"🧪 Probando extracción de fecha: {os.path.basename(pdf_path)}")
    print(f"{'='*80}\n")
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: El archivo no existe")
        return
    
    try:
        # Parsear documento DIAN
        print(f"🔍 Parseando documento DIAN...")
        result = PDFParserService.parse_dian_document(pdf_path)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return
        
        # Mostrar fecha extraída
        fecha = result.get('fecha_emision')
        
        print(f"\n📅 FECHA EXTRAÍDA:")
        print(f"{'─'*80}")
        if fecha:
            print(f"   ✅ Fecha: {fecha.strftime('%d/%m/%Y')}")
            print(f"   📆 Formato ISO: {fecha.strftime('%Y-%m-%d')}")
        else:
            print(f"   ❌ No se pudo extraer la fecha")
        print(f"{'─'*80}")
        
        # Buscar manualmente en el texto para debugging
        text = result.get('raw_text', '')
        
        print(f"\n🔎 BÚSQUEDA MANUAL EN EL TEXTO:")
        print(f"{'─'*80}")
        
        # Buscar "Fecha de Emisión"
        import re
        match_emision = re.search(r'Fecha\s+de\s+[Ee]misi[oó]n[\s:]+([^\n]+)', text, re.IGNORECASE)
        if match_emision:
            print(f"   ✅ 'Fecha de Emisión' encontrada: {match_emision.group(1).strip()}")
        else:
            print(f"   ⚠️ 'Fecha de Emisión' NO encontrada")
        
        # Buscar "Documento generado el"
        match_generado = re.search(r'Documento\s+generado\s+el[\s:]+([^\n]+)', text, re.IGNORECASE)
        if match_generado:
            print(f"   ✅ 'Documento generado el' encontrada: {match_generado.group(1).strip()}")
        else:
            print(f"   ⚠️ 'Documento generado el' NO encontrada")
        
        print(f"{'─'*80}")
        
        # Mostrar información adicional
        print(f"\n📋 INFORMACIÓN ADICIONAL:")
        print(f"{'─'*80}")
        print(f"   CUFE:           {result.get('cufe', 'No encontrado')[:32]}...")
        print(f"   Número:         {result.get('numero_documento', 'No encontrado')}")
        print(f"   Emisor:         {result.get('emisor', {}).get('razon_social', 'No encontrado')}")
        print(f"   Total Neto:     ${result.get('totales', {}).get('total_neto') or 0:,.2f}")
        print(f"{'─'*80}")
        
        print(f"\n✅ Prueba completada")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 test_date_extraction.py <ruta_al_pdf>")
        print("\nEjemplo:")
        print("  python3 test_date_extraction.py CUFE/CUFE/fd7892b8723009bb46c2f065caa325144d76ee5e3eada87cf2dce405dc23b0b4e5938e060c94fa4c3f846220c56dc4e1.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    test_date_extraction(pdf_path)
