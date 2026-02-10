#!/usr/bin/env python3
"""
Probar el nuevo parser con los PDFs problemáticos
"""
import sys
sys.path.insert(0, '/home/stk/Documents/GIT/PAQUETEX v1.0/CODE')

from src.app.services.pdf_parser_service_new import PDFParserServiceNew

print("=" * 80)
print("TEST 1: PDF PROBLEMÁTICO (2 productos según XML)")
print("=" * 80)

pdf_path1 = "/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE/CUFE-XML/90586381def1342a38806c310801a43659405240dcd445e0d640367591143dd4806cf6fca1ea21fb03b2ea47c62264a2.pdf"

text1 = PDFParserServiceNew.extract_text_from_pdf(pdf_path1)
productos1 = PDFParserServiceNew._extract_productos(text1)

print(f"\n✅ Productos extraídos: {len(productos1)}")
print(f"📋 Esperado: 2 productos\n")

for i, prod in enumerate(productos1, 1):
    print(f"{i}. Código: {prod['codigo_producto']}")
    print(f"   Descripción: {prod['descripcion']}")
    print(f"   Cantidad: {prod['cantidad']} {prod['unidad_medida']}")
    print(f"   Precio Unit: ${prod['precio_unitario']:,.2f}")
    print(f"   IVA: {prod['iva_porcentaje']}%")
    print(f"   Total: ${prod['total_item']:,.2f}")
    print()

print("\n" + "=" * 80)
print("TEST 2: PDF CON 20 PRODUCTOS")
print("=" * 80)

pdf_path2 = "/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE/CUFE-XML/6ee372e238cc82c3d95fa44faa0869cd5c6e0e45d51cef31b9828697aad65af8f2e3a89ff13f799961ad968c89503f8e.pdf"

text2 = PDFParserServiceNew.extract_text_from_pdf(pdf_path2)
productos2 = PDFParserServiceNew._extract_productos(text2)

print(f"\n✅ Productos extraídos: {len(productos2)}")
print(f"📋 Esperado: 20 productos\n")

for i, prod in enumerate(productos2[:5], 1):  # Mostrar solo primeros 5
    print(f"{i}. Código: {prod['codigo_producto']}")
    print(f"   Descripción: {prod['descripcion'][:50]}...")
    print(f"   Cantidad: {prod['cantidad']} {prod['unidad_medida']}")
    print(f"   Total: ${prod['total_item']:,.2f}")
    print()

if len(productos2) > 5:
    print(f"... y {len(productos2) - 5} productos más")

print("\n" + "=" * 80)
print("RESUMEN")
print("=" * 80)
print(f"PDF 1 (2 productos esperados): {len(productos1)} extraídos - {'✅ CORRECTO' if len(productos1) == 2 else '❌ INCORRECTO'}")
print(f"PDF 2 (20 productos esperados): {len(productos2)} extraídos - {'✅ CORRECTO' if len(productos2) == 20 else '❌ INCORRECTO'}")
