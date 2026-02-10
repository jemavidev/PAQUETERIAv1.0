#!/usr/bin/env python3
"""
Probar el parser actualizado en el archivo principal
"""
import sys
sys.path.insert(0, '/home/stk/Documents/GIT/PAQUETEX v1.0/CODE/src')

from app.services.pdf_parser_service import PDFParserService

print("=" * 80)
print("TEST CON PARSER ACTUALIZADO")
print("=" * 80)

# Test 1: PDF problemático (2 productos)
pdf_path1 = "/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE/CUFE-XML/90586381def1342a38806c310801a43659405240dcd445e0d640367591143dd4806cf6fca1ea21fb03b2ea47c62264a2.pdf"

print("\nTEST 1: PDF con 2 productos")
print("-" * 80)

text1 = PDFParserService.extract_text_from_pdf(pdf_path1)
productos1 = PDFParserService._extract_productos(text1)

print(f"✅ Productos extraídos: {len(productos1)}")
print(f"📋 Esperado: 2 productos")
print(f"Resultado: {'✅ CORRECTO' if len(productos1) == 2 else '❌ INCORRECTO'}\n")

for i, prod in enumerate(productos1, 1):
    print(f"{i}. {prod['codigo_producto']} - {prod['descripcion'][:40]}...")

# Test 2: PDF con 20 productos
pdf_path2 = "/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE/CUFE-XML/6ee372e238cc82c3d95fa44faa0869cd5c6e0e45d51cef31b9828697aad65af8f2e3a89ff13f799961ad968c89503f8e.pdf"

print("\n\nTEST 2: PDF con 20 productos")
print("-" * 80)

text2 = PDFParserService.extract_text_from_pdf(pdf_path2)
productos2 = PDFParserService._extract_productos(text2)

print(f"✅ Productos extraídos: {len(productos2)}")
print(f"📋 Esperado: 20 productos")
print(f"Resultado: {'✅ CORRECTO' if len(productos2) == 20 else '❌ INCORRECTO'}\n")

for i, prod in enumerate(productos2[:5], 1):
    print(f"{i}. {prod['codigo_producto']} - {prod['descripcion'][:40]}...")

if len(productos2) > 5:
    print(f"... y {len(productos2) - 5} productos más")

print("\n" + "=" * 80)
print("RESUMEN FINAL")
print("=" * 80)
print(f"PDF 1: {len(productos1)}/2 productos - {'✅ CORRECTO' if len(productos1) == 2 else '❌ INCORRECTO'}")
print(f"PDF 2: {len(productos2)}/20 productos - {'✅ CORRECTO' if len(productos2) == 20 else '❌ INCORRECTO'}")

if len(productos1) == 2 and len(productos2) == 20:
    print("\n🎉 ¡PARSER COMPLETAMENTE CORREGIDO!")
else:
    print("\n⚠️ Aún hay problemas con el parser")
