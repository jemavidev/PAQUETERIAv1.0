#!/usr/bin/env python3
"""
Script de debug para ver qué está pasando con la extracción
"""
import sys
import os
import re

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extrae texto del PDF"""
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        print(f"Error: {e}")
        return ""

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 test_parser_debug.py <pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    text = extract_text_from_pdf(pdf_path)
    
    print("="*80)
    print("TEXTO COMPLETO DEL PDF:")
    print("="*80)
    print(text)
    print("\n" + "="*80)
    print("BUSCANDO SECCIONES DE PRODUCTOS:")
    print("="*80)
    
    # Probar diferentes patrones
    patterns = [
        (r'(?:Detalles de productos|Detalle de Ítems|DETALLE DE PRODUCTOS|DETALLE)([\s\S]{0,8000}?)(?:Notas finales|Datos totales|Observaciones|OBSERVACIONES|Total factura|TOTAL FACTURA)', "Patrón 1"),
        (r'(?:DESCRIPCIÓN|DESCRIPCION|Descripción)([\s\S]{0,8000}?)(?:Notas|NOTAS|Total|TOTAL)', "Patrón 2"),
        (r'(?:Item|ITEM|Ítem|ÍTEM)([\s\S]{0,8000}?)(?:Subtotal|SUBTOTAL|Total|TOTAL)', "Patrón 3"),
        (r'(?:Código|CODIGO|Código Cantidad)([\s\S]{0,8000}?)(?:Subtotal|SUBTOTAL|Total|TOTAL|Observaciones)', "Patrón 4 - Nuevo"),
    ]
    
    for pattern, nombre in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            print(f"\n✅ {nombre} ENCONTRÓ MATCH:")
            print("-"*80)
            print(match.group(1)[:500])
            print("-"*80)
        else:
            print(f"\n❌ {nombre} NO encontró match")
    
    # Buscar líneas con códigos de producto
    print("\n" + "="*80)
    print("LÍNEAS QUE PARECEN PRODUCTOS (con códigos numéricos):")
    print("="*80)
    lines = text.split('\n')
    for i, line in enumerate(lines):
        # Buscar líneas con códigos de 6+ dígitos
        if re.search(r'\b\d{6,}\b', line) and len(line) > 20:
            print(f"{i}: {line}")

if __name__ == "__main__":
    main()
