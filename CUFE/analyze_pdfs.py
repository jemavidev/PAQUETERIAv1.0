#!/usr/bin/env python3
"""
Script para analizar los 19 PDFs y detectar cuáles tienen problemas.
Extrae CUFE, NIT, y número de items de cada archivo.
"""

import os
import sys
import pdfplumber
import re
from pathlib import Path

# Directorio de PDFs
PDF_DIR = Path(__file__).parent / "PDF"

def extract_cufe(text):
    """Extrae CUFE/CUDE del texto"""
    # Buscar patrón CUFE/CUDE
    patterns = [
        re.compile(r'CUFE\s*:?\s*\n?\s*([a-f0-9]{64,96})', re.IGNORECASE),
        re.compile(r'CUDE\s*:?\s*\n?\s*([a-f0-9]{64,96})', re.IGNORECASE),
        re.compile(r'\b([a-f0-9]{64,96})\b', re.IGNORECASE),
    ]
    
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            return match.group(1)
    return None

def extract_nit(text):
    """Extrae NIT del proveedor"""
    patterns = [
        re.compile(r'(?:Nit\s+del\s+Emisor|NIT|N\.I\.T\.?)\s*:?\s*(\d[\d\.\-]*\d)', re.IGNORECASE),
        re.compile(r'(?:Número\s+de\s+documento|Documento)\s*:?\s*(\d{5,15})', re.IGNORECASE),
    ]
    
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            nit = re.sub(r'[^\d]', '', match.group(1))
            return nit
    return None

def extract_razon_social(text):
    """Extrae razón social del proveedor"""
    patterns = [
        re.compile(r'(?:Razón\s+Social|Nombre\s+o\s+razón)\s*:?\s*([^\n]+)', re.IGNORECASE),
        re.compile(r'(?:Datos\s+del\s+Emisor|Emisor).*?(?:Razón\s+Social|Nombre)\s*:?\s*([^\n]+)', re.DOTALL | re.IGNORECASE),
    ]
    
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            return match.group(1).strip()[:50]
    return None

def extract_numero_doc(text):
    """Extrae número de documento"""
    patterns = [
        re.compile(r'(?:Número\s+de\s+Factura|No\.\s*Factura|Factura\s+No\.?)\s*:?\s*([A-Z0-9\-]+)', re.IGNORECASE),
        re.compile(r'(?:Número\s+de\s+documento|Doc\.?\s*No\.?)\s*:?\s*([A-Z0-9\-]+)', re.IGNORECASE),
    ]
    
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
    return None

def count_tables(pdf):
    """Cuenta tablas en todas las páginas"""
    total_tables = 0
    for page in pdf.pages:
        tables = page.extract_tables()
        total_tables += len(tables)
    return total_tables

def analyze_pdf(pdf_path):
    """Analiza un PDF y retorna información"""
    result = {
        'filename': pdf_path.name,
        'pages': 0,
        'text_length': 0,
        'cufe': None,
        'nit': None,
        'razon_social': None,
        'numero_doc': None,
        'tables': 0,
        'error': None,
    }
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            result['pages'] = len(pdf.pages)
            
            # Extraer texto de todas las páginas
            all_text = []
            for page in pdf.pages:
                text = page.extract_text() or ''
                all_text.append(text)
            
            full_text = '\n'.join(all_text)
            result['text_length'] = len(full_text)
            
            # Extraer datos
            result['cufe'] = extract_cufe(full_text)
            result['nit'] = extract_nit(full_text)
            result['razon_social'] = extract_razon_social(full_text)
            result['numero_doc'] = extract_numero_doc(full_text)
            result['tables'] = count_tables(pdf)
            
    except Exception as e:
        result['error'] = str(e)
    
    return result

def main():
    print("=" * 80)
    print("ANÁLISIS DE PDFs EN CUFE/PDF/")
    print("=" * 80)
    
    if not PDF_DIR.exists():
        print(f"ERROR: Directorio {PDF_DIR} no existe")
        return
    
    pdf_files = sorted(PDF_DIR.glob("*.pdf"))
    print(f"\nEncontrados {len(pdf_files)} archivos PDF\n")
    
    results = []
    problematic = []
    
    for pdf_path in pdf_files:
        result = analyze_pdf(pdf_path)
        results.append(result)
        
        # Determinar si tiene problemas
        has_problem = False
        problems = []
        
        if result['error']:
            has_problem = True
            problems.append(f"ERROR: {result['error']}")
        if not result['cufe']:
            has_problem = True
            problems.append("Sin CUFE/CUDE")
        if not result['nit']:
            has_problem = True
            problems.append("Sin NIT")
        if result['text_length'] < 100:
            has_problem = True
            problems.append("Texto muy corto")
        
        status = "❌ PROBLEMA" if has_problem else "✓ OK"
        
        print(f"\n{status}: {result['filename'][:60]}...")
        print(f"   Páginas: {result['pages']}, Texto: {result['text_length']} chars, Tablas: {result['tables']}")
        print(f"   CUFE: {result['cufe'][:30] if result['cufe'] else 'NO ENCONTRADO'}...")
        print(f"   NIT: {result['nit'] or 'NO ENCONTRADO'}")
        print(f"   Razón Social: {result['razon_social'] or 'NO ENCONTRADO'}")
        print(f"   Número Doc: {result['numero_doc'] or 'NO ENCONTRADO'}")
        
        if has_problem:
            problematic.append({**result, 'problems': problems})
    
    # Resumen
    print("\n" + "=" * 80)
    print("RESUMEN")
    print("=" * 80)
    print(f"Total archivos: {len(results)}")
    print(f"Con problemas: {len(problematic)}")
    print(f"OK: {len(results) - len(problematic)}")
    
    if problematic:
        print("\n" + "-" * 40)
        print("ARCHIVOS CON PROBLEMAS:")
        print("-" * 40)
        for p in problematic:
            print(f"\n  {p['filename'][:50]}...")
            for prob in p['problems']:
                print(f"    - {prob}")
    
    # Listar todos los CUFEs encontrados
    print("\n" + "-" * 40)
    print("CUFEs ENCONTRADOS:")
    print("-" * 40)
    for r in results:
        if r['cufe']:
            print(f"  {r['cufe']}")

if __name__ == "__main__":
    main()
