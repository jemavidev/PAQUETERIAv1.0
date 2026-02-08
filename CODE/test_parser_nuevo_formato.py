#!/usr/bin/env python3
"""
Script para probar el parser con el nuevo formato de productos
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app.services.pdf_parser_service import PDFParserService

# Texto de ejemplo del formato nuevo
texto_ejemplo = """
Descripción U/M Cantidad Precio unitario Descuento detalle Recargo detalle IVA % INC %
venta
BOLSA DE PAPEL SELVA 33
1 631668 94 6,00 $ 840,34 $ 0,00 $ 0,00 $ 957,99 19.00 $ 5.042,04
H-20CTG-25 A9 REF:9141
BOLSA PAPEL CARROS 33
2 631669 94 2,00 $ 840,34 $ 0,00 $ 0,00 $ 319,33 19.00 $ 1.680,68
H-23CTG-25 A9 REF:3141
BOLSA PAPEL TROPICAL 3
3 631655 3H-24CTG-25 A9 REF:314 94 2,00 $ 840,34 $ 0,00 $ 0,00 $ 319,33 19.00 $ 1.680,68
1
BOLSA DE PAPEL ABEJA 3
4 631657 3H-17CTG-25 A9 REF:914 94 2,00 $ 840,34 $ 0,00 $ 0,00 $ 319,33 19.00 $ 1.680,68
1
BOLSA PAPEL FRESA 33H-
5 631656 94 2,00 $ 840,34 $ 0,00 $ 0,00 $ 319,33 19.00 $ 1.680,68
26CTG-25 A9 REF:3141
Datos Totales
"""

print("=" * 80)
print("🧪 PRUEBA DEL PARSER CON NUEVO FORMATO")
print("=" * 80)
print()

parser = PDFParserService()
productos = parser._extract_productos(texto_ejemplo)

print(f"✅ Productos extraídos: {len(productos)}")
print()

if productos:
    print("📦 PRODUCTOS:")
    print("-" * 80)
    for i, prod in enumerate(productos, 1):
        print(f"{i:2d}. Código: {prod.get('codigo_producto', 'N/A')}")
        print(f"    Descripción: {prod.get('descripcion', 'N/A')[:60]}...")
        print(f"    Cantidad: {prod.get('cantidad', 0)} {prod.get('unidad_medida', 'NIU')}")
        print(f"    Precio: ${prod.get('precio_unitario', 0):,.2f}")
        print(f"    IVA: {prod.get('iva_porcentaje', 0)}%")
        print(f"    Total: ${prod.get('total_item', 0):,.2f}")
        print()
else:
    print("❌ No se extrajeron productos")
    print()
    print("Posibles causas:")
    print("1. El patrón regex no coincide con el formato")
    print("2. La sección de productos no se detectó")
    print("3. Error en el procesamiento de líneas")

print("=" * 80)
