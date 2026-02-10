#!/usr/bin/env python3
import re
import pdfplumber

pdf_path = "/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE/CUFE-XML/6ee372e238cc82c3d95fa44faa0869cd5c6e0e45d51cef31b9828697aad65af8f2e3a89ff13f799961ad968c89503f8e.pdf"

text_parts = []
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)

text = '\n'.join(text_parts)

# Buscar sección de productos
match = re.search(r'Detalles de Productos([\s\S]+?)(?:Notas Finales|Datos Totales)', text, re.IGNORECASE)

if match:
    productos_section = match.group(1)
    lines = productos_section.split('\n')
    
    print("TODAS LAS LÍNEAS DE LA SECCIÓN DE PRODUCTOS:")
    print("=" * 80)
    
    for i, line in enumerate(lines):
        if line.strip():
            # Marcar líneas que empiezan con número
            if re.match(r'^\d{1,3}\s', line):
                print(f">>> {i:3d}: {line}")
            else:
                print(f"    {i:3d}: {line}")
