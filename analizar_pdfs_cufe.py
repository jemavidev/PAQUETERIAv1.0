#!/usr/bin/env python3
"""
Analizar PDFs de CUFE para entender estructura y mejorar parser
"""
import sys
sys.path.insert(0, '/home/stk/Documents/GIT/PAQUETEX v1.0/CODE')

import pdfplumber
import re

# Analizar el PDF problemático (2 productos según XML)
pdf_path = "/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE/CUFE-XML/90586381def1342a38806c310801a43659405240dcd445e0d640367591143dd4806cf6fca1ea21fb03b2ea47c62264a2.pdf"

print("=" * 80)
print("ANÁLISIS PDF PROBLEMÁTICO (2 productos según XML)")
print("CUFE: 90586381def1342a38806c310801a43659405240dcd445e0d640367591143dd4806cf6fca1ea21fb03b2ea47c62264a2")
print("=" * 80)

with pdfplumber.open(pdf_path) as pdf:
    print(f"\nTotal páginas: {len(pdf.pages)}\n")
    
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        print(f"\n{'='*60}")
        print(f"PÁGINA {i+1}")
        print(f"{'='*60}")
        print(text)
        print(f"\n{'='*60}\n")

print("\n\n")
print("=" * 80)
print("ANÁLISIS PDF CON 20 PRODUCTOS")
print("CUFE: 6ee372e238cc82c3d95fa44faa0869cd5c6e0e45d51cef31b9828697aad65af8f2e3a89ff13f799961ad968c89503f8e")
print("=" * 80)

pdf_path2 = "/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE/CUFE-XML/6ee372e238cc82c3d95fa44faa0869cd5c6e0e45d51cef31b9828697aad65af8f2e3a89ff13f799961ad968c89503f8e.pdf"

with pdfplumber.open(pdf_path2) as pdf:
    print(f"\nTotal páginas: {len(pdf.pages)}\n")
    
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        print(f"\n{'='*60}")
        print(f"PÁGINA {i+1}")
        print(f"{'='*60}")
        print(text[:2000])  # Primeros 2000 caracteres
        print(f"\n... (total {len(text)} caracteres)")
        print(f"\n{'='*60}\n")
