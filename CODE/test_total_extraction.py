#!/usr/bin/env python3
"""
Script de prueba para verificar la extracción del total de facturas DIAN
"""
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.services.pdf_parser_service import PDFParserService

def test_total_extraction(pdf_path: str):
    """
    Prueba la extracción del total de una factura DIAN
    """
    print(f"\n{'='*80}")
    print(f"🧪 PRUEBA: Extracción de Total de Factura DIAN")
    print(f"{'='*80}\n")
    
    print(f"📄 Archivo: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: El archivo no existe")
        return
    
    try:
        # Parsear documento DIAN
        print(f"\n🔍 Parseando documento DIAN...")
        data = PDFParserService.parse_dian_document(pdf_path)
        
        if 'error' in data:
            print(f"❌ Error: {data['error']}")
            return
        
        # Mostrar totales extraídos
        totales = data.get('totales', {})
        
        print(f"\n💰 TOTALES EXTRAÍDOS:")
        print(f"{'─'*80}")
        print(f"   Subtotal:     ${totales.get('subtotal') or 0:,.2f}")
        print(f"   Total Bruto:  ${totales.get('total_bruto') or 0:,.2f}")
        print(f"   Total IVA:    ${totales.get('total_iva') or 0:,.2f}")
        print(f"   Total Neto:   ${totales.get('total_neto') or 0:,.2f}")
        print(f"{'─'*80}")
        
        # Buscar "Total factura (=)" o "Total documento" en el texto
        text = data.get('raw_text', '')
        
        print(f"\n🔎 Buscando 'Total factura (=)' o 'Total documento' en el texto...")
        
        import re
        
        # Buscar "Total factura (=)"
        matches = re.finditer(r'Total factura\s*\(=\)[\s:$COP]*([0-9,.]+)', text, re.IGNORECASE)
        
        found = False
        for match in matches:
            found = True
            value_str = match.group(1)
            print(f"   ✅ Encontrado: Total factura (=) {value_str}")
            
            # Convertir a número
            try:
                value_clean = value_str.replace('.', '').replace(',', '.')
                value_clean = re.sub(r'[^\d.]', '', value_clean)
                value_num = float(value_clean)
                print(f"   💵 Valor numérico: ${value_num:,.2f}")
            except Exception as e:
                print(f"   ⚠️ Error convirtiendo: {e}")
        
        # Buscar "Total documento"
        matches_doc = re.finditer(r'Total documento[\s:$COP]*([0-9,.]+)', text, re.IGNORECASE)
        
        for match in matches_doc:
            found = True
            value_str = match.group(1)
            print(f"   ✅ Encontrado: Total documento {value_str}")
            
            # Convertir a número
            try:
                value_clean = value_str.replace('.', '').replace(',', '.')
                value_clean = re.sub(r'[^\d.]', '', value_clean)
                value_num = float(value_clean)
                print(f"   💵 Valor numérico: ${value_num:,.2f}")
            except Exception as e:
                print(f"   ⚠️ Error convirtiendo: {e}")
        
        if not found:
            print(f"   ⚠️ No se encontró 'Total factura (=)' ni 'Total documento' en el texto")
            print(f"\n   Buscando patrones alternativos...")
            
            # Buscar patrones alternativos
            alt_patterns = [
                (r'Total factura[\s:$COP]*([0-9,.]+)', 'Total factura'),
                (r'Total neto[\s:$COP]*([0-9,.]+)', 'Total neto'),
                (r'Total documento[\s:$COP]*([0-9,.]+)', 'Total documento'),
                (r'TOTAL A PAGAR[\s:$COP]*([0-9,.]+)', 'TOTAL A PAGAR'),
                (r'Total[\s:$COP]*([0-9,.]+)', 'Total'),
            ]
            
            for pattern, name in alt_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    value_str = match.group(1)
                    print(f"   📌 Patrón '{name}': {value_str}")
        
        # Mostrar sección de totales del texto (últimas 2000 caracteres)
        print(f"\n📝 SECCIÓN DE TOTALES DEL PDF (últimos 2000 caracteres):")
        print(f"{'─'*80}")
        text_end = text[-2000:] if len(text) > 2000 else text
        # Buscar líneas que contengan "total" o números grandes
        lines = text_end.split('\n')
        for line in lines:
            line_lower = line.lower()
            if 'total' in line_lower or 'subtotal' in line_lower or 'iva' in line_lower:
                print(f"   {line.strip()}")
        print(f"{'─'*80}")
        
        # Mostrar información adicional
        print(f"\n📋 INFORMACIÓN ADICIONAL:")
        print(f"{'─'*80}")
        print(f"   CUFE:           {data.get('cufe', 'No encontrado')[:32]}...")
        print(f"   Número:         {data.get('numero_documento', 'No encontrado')}")
        print(f"   Fecha:          {data.get('fecha_emision', 'No encontrada')}")
        print(f"   Emisor:         {data.get('emisor', {}).get('razon_social', 'No encontrado')}")
        print(f"   Productos:      {len(data.get('productos', []))} items")
        print(f"   Longitud texto: {len(text)} caracteres")
        print(f"{'─'*80}")
        
        print(f"\n✅ Prueba completada")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python test_total_extraction.py <ruta_al_pdf>")
        print("\nEjemplo:")
        print("  python test_total_extraction.py CUFE/FACTURAS/factura.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    test_total_extraction(pdf_path)
