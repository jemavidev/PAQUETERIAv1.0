#!/usr/bin/env python3
"""
Test para verificar que el fix funciona correctamente
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'CODE/src'))

from app.services.pdf_parser_service import PDFParserService

def test_pdf(pdf_path):
    """Test de extracción de total"""
    print(f"\n{'='*80}")
    print(f"🧪 Probando: {os.path.basename(pdf_path)}")
    print(f"{'='*80}\n")
    
    result = PDFParserService.parse_dian_document(pdf_path)
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        return
    
    totales = result.get('totales', {})
    total_neto = totales.get('total_neto')
    
    print(f"💰 Total extraído: ${total_neto:,.2f}" if total_neto else "❌ Total no encontrado")
    print(f"   Subtotal: ${totales.get('subtotal') or 0:,.2f}")
    print(f"   IVA: ${totales.get('total_iva') or 0:,.2f}")
    print(f"   Total Neto: ${total_neto or 0:,.2f}")
    
    return total_neto

if __name__ == "__main__":
    # Probar los 5 PDFs problemáticos
    pdfs = [
        "CUFE/CUFE/fd7892b8723009bb46c2f065caa325144d76ee5e3eada87cf2dce405dc23b0b4e5938e060c94fa4c3f846220c56dc4e1.pdf",
        "CUFE/CUFE/dce84f5f446f8c609791c431e785b550a2d63cd81fa2ccd4f429ac8c3a7ba442b7137b4727dbcfb151862e7ad9f5b1ce.pdf",
        "CUFE/CUFE/b95d05e6ff51cbaf53e1510b1d213af6a0ec838d1e4420e708b99e9c723c984926586ce3a64de8d5a621b2eeea9ec051.pdf",
    ]
    
    print(f"\n{'='*80}")
    print(f"🔧 VERIFICACIÓN DEL FIX - EXTRACCIÓN DE TOTALES")
    print(f"{'='*80}")
    
    resultados = []
    for pdf in pdfs:
        if os.path.exists(pdf):
            total = test_pdf(pdf)
            resultados.append((os.path.basename(pdf)[:20], total))
        else:
            print(f"\n⚠️ Archivo no encontrado: {pdf}")
    
    print(f"\n{'='*80}")
    print(f"📊 RESUMEN:")
    print(f"{'='*80}")
    for nombre, total in resultados:
        status = "✅" if total and total > 0 else "❌"
        print(f"{status} {nombre}... → ${total:,.2f}" if total else f"{status} {nombre}... → No encontrado")
    print(f"{'='*80}\n")
