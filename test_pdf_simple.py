#!/usr/bin/env python3
"""
Script simple para analizar PDFs sin dependencias de la app
"""
import sys
import re

try:
    import pdfplumber
except ImportError:
    print("❌ Error: pdfplumber no está instalado")
    print("   Instalar con: pip install pdfplumber")
    sys.exit(1)

def analyze_pdf(pdf_path):
    """Analiza un PDF y busca patrones de total"""
    print(f"\n{'='*80}")
    print(f"📄 Analizando: {pdf_path}")
    print(f"{'='*80}\n")
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"📊 Total de páginas: {len(pdf.pages)}\n")
            
            # Extraer texto de todas las páginas
            all_text = ""
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    all_text += text + "\n"
                    print(f"   Página {i+1}: {len(text)} caracteres")
            
            print(f"\n📝 Total de texto extraído: {len(all_text)} caracteres\n")
            
            # Buscar patrones de total
            print(f"{'─'*80}")
            print(f"🔍 BUSCANDO PATRONES DE TOTAL:")
            print(f"{'─'*80}\n")
            
            patterns = [
                (r'Total factura\s*\(=\)[\s\$COP\u3164]*([0-9,.]+)', 'Total factura (=)'),
                (r'Total documento[\s\$COP\u3164]*([0-9,.]+)', 'Total documento'),
                (r'Total neto factura[\s\$COP\u3164]*([0-9,.]+)', 'Total neto factura'),
                (r'TOTAL A PAGAR[\s\$COP\u3164]*([0-9,.]+)', 'TOTAL A PAGAR'),
                (r'Total factura[\s\$COP\u3164]*([0-9,.]+)', 'Total factura'),
                (r'Total[\s\$COP\u3164]*([0-9,.]+)', 'Total'),
            ]
            
            found_any = False
            for pattern, name in patterns:
                matches = list(re.finditer(pattern, all_text, re.IGNORECASE))
                if matches:
                    found_any = True
                    print(f"✅ Patrón '{name}' encontrado {len(matches)} veces:")
                    for i, match in enumerate(matches[:5], 1):  # Mostrar máximo 5
                        value_str = match.group(1)
                        # Convertir a número
                        try:
                            value_clean = value_str.replace('.', '').replace(',', '.')
                            value_clean = re.sub(r'[^\d.]', '', value_clean)
                            value_num = float(value_clean)
                            print(f"   {i}. {value_str} → ${value_num:,.2f}")
                        except:
                            print(f"   {i}. {value_str} → Error al convertir")
                    print()
            
            if not found_any:
                print("⚠️ No se encontraron patrones de total\n")
            
            # Mostrar últimas 3000 caracteres (donde suelen estar los totales)
            print(f"{'─'*80}")
            print(f"📝 ÚLTIMAS 3000 CARACTERES DEL PDF:")
            print(f"{'─'*80}\n")
            
            text_end = all_text[-3000:] if len(all_text) > 3000 else all_text
            lines = text_end.split('\n')
            
            # Filtrar líneas relevantes
            for line in lines:
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in ['total', 'subtotal', 'iva', 'neto', 'pagar']):
                    print(f"   {line.strip()}")
            
            print(f"\n{'─'*80}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 test_pdf_simple.py <ruta_al_pdf>")
        sys.exit(1)
    
    analyze_pdf(sys.argv[1])
