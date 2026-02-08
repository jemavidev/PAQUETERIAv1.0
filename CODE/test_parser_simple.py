#!/usr/bin/env python3
"""
Script simple para probar el parser de productos con un PDF local
Sin dependencias de base de datos
"""
import sys
import os
import re
from decimal import Decimal
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str, max_pages: int = 999) -> str:
    """Extrae texto del PDF usando pdfplumber"""
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            num_pages = min(len(pdf.pages), max_pages)
            for page_num in range(num_pages):
                page = pdf.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except ImportError:
        logger.error("❌ pdfplumber no está instalado. Instala con: pip install pdfplumber")
        return ""
    except Exception as e:
        logger.error(f"❌ Error extrayendo texto: {e}")
        return ""


def extract_productos(text: str) -> List[Dict[str, Any]]:
    """
    Extrae productos del documento DIAN con TODA la información
    """
    productos = []
    
    # Buscar sección de productos con más variantes
    patterns = [
        r'(?:Detalles de productos|Detalle de Ítems|DETALLE DE PRODUCTOS|DETALLE)([\s\S]{0,8000}?)(?:Notas finales|Datos totales|Observaciones|OBSERVACIONES|Total factura|TOTAL FACTURA)',
        r'(?:DESCRIPCIÓN|DESCRIPCION|Descripción)([\s\S]{0,8000}?)(?:Notas|NOTAS|Total|TOTAL)',
        r'(?:Item|ITEM|Ítem|ÍTEM)([\s\S]{0,8000}?)(?:Subtotal|SUBTOTAL|Total|TOTAL)',
    ]
    
    productos_section = None
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            productos_section = match.group(1)
            break
    
    if not productos_section:
        logger.warning("⚠️ No se encontró sección de productos en el PDF")
        return productos
    
    # Dividir en líneas y procesar
    lines = productos_section.split('\n')
    
    for i, line in enumerate(lines[:200]):
        line = line.strip()
        if len(line) < 3:
            continue
        
        # Buscar código de producto
        codigo_match = re.search(r'\b([A-Z0-9]{6,13})\b', line)
        
        # Buscar valores monetarios en la línea
        valores_monetarios = re.findall(r'[\$]?\s*([0-9]{1,3}(?:[.,][0-9]{3})*(?:[.,][0-9]{2})?)', line)
        
        # Buscar cantidad
        cantidad_match = re.search(r'\b([0-9]{1,4}(?:[.,][0-9]{1,3})?)\b', line)
        
        # Buscar porcentaje de IVA
        iva_match = re.search(r'(\d{1,2}(?:[.,]\d{1,2})?)\s*%', line)
        
        if codigo_match:
            codigo = codigo_match.group(1)
            
            # Extraer descripción
            desc_start = line.find(codigo) + len(codigo)
            desc_text = line[desc_start:].strip()
            desc_clean = re.sub(r'[\d\$,.\s]+$', '', desc_text).strip()
            desc_clean = re.sub(r'\s+', ' ', desc_clean)
            
            # Intentar extraer valores numéricos
            cantidad = None
            precio_unitario = None
            iva_porcentaje = None
            total_item = None
            
            if cantidad_match:
                try:
                    cant_str = cantidad_match.group(1).replace(',', '.')
                    cant_val = float(cant_str)
                    if cant_val < 10000:
                        cantidad = cant_val
                except:
                    pass
            
            if iva_match:
                try:
                    iva_porcentaje = float(iva_match.group(1).replace(',', '.'))
                except:
                    pass
            
            if len(valores_monetarios) >= 2:
                try:
                    total_str = valores_monetarios[-1].replace('.', '').replace(',', '.')
                    total_item = float(total_str)
                    
                    precio_str = valores_monetarios[-2].replace('.', '').replace(',', '.')
                    precio_unitario = float(precio_str)
                except:
                    pass
            elif len(valores_monetarios) == 1:
                try:
                    total_str = valores_monetarios[0].replace('.', '').replace(',', '.')
                    total_item = float(total_str)
                except:
                    pass
            
            if not desc_clean or len(desc_clean) < 3:
                desc_clean = line.replace(codigo, '').strip()[:200]
            
            if codigo and desc_clean and len(desc_clean) > 3:
                productos.append({
                    'codigo_producto': codigo,
                    'descripcion': desc_clean[:250],
                    'cantidad': cantidad,
                    'precio_unitario': precio_unitario,
                    'iva_porcentaje': iva_porcentaje,
                    'total_item': total_item,
                })
                
                if len(productos) >= 100:
                    break
    
    return productos


def test_pdf(pdf_path: str):
    """Prueba el parser con un PDF"""
    if not os.path.exists(pdf_path):
        logger.error(f"❌ Archivo no encontrado: {pdf_path}")
        return
    
    logger.info(f"\n{'='*80}")
    logger.info(f"🧪 PRUEBA DE EXTRACCIÓN DE PRODUCTOS")
    logger.info(f"{'='*80}")
    logger.info(f"Archivo: {pdf_path}")
    logger.info(f"Tamaño: {os.path.getsize(pdf_path) / 1024:.2f} KB")
    logger.info("")
    
    # Extraer texto
    logger.info("📄 Extrayendo texto del PDF...")
    text = extract_text_from_pdf(pdf_path)
    
    if not text:
        logger.error("❌ No se pudo extraer texto del PDF")
        return
    
    logger.info(f"✅ Texto extraído ({len(text)} caracteres)")
    
    # Extraer productos
    logger.info(f"\n🔍 Buscando productos...")
    productos = extract_productos(text)
    
    logger.info(f"\n📦 PRODUCTOS EXTRAÍDOS: {len(productos)}")
    logger.info(f"{'='*80}\n")
    
    if not productos:
        logger.warning("⚠️ No se extrajeron productos del PDF")
        logger.info("\n💡 Mostrando muestra del texto para debug:")
        logger.info(text[:1000])
    else:
        for i, prod in enumerate(productos, 1):
            logger.info(f"{i}. Producto:")
            logger.info(f"   Código: {prod.get('codigo_producto', 'N/A')}")
            logger.info(f"   Descripción: {prod.get('descripcion', 'N/A')[:80]}")
            logger.info(f"   Cantidad: {prod.get('cantidad', 'N/A')}")
            logger.info(f"   Precio Unit.: ${prod.get('precio_unitario', 0):,.2f}" if prod.get('precio_unitario') else "   Precio Unit.: N/A")
            logger.info(f"   IVA: {prod.get('iva_porcentaje', 'N/A')}%")
            logger.info(f"   Total: ${prod.get('total_item', 0):,.2f}" if prod.get('total_item') else "   Total: N/A")
            logger.info("")
            
            if i >= 10:
                logger.info(f"... y {len(productos) - 10} productos más\n")
                break
        
        # Resumen
        productos_completos = sum(1 for p in productos if p.get('cantidad') and p.get('precio_unitario'))
        productos_parciales = len(productos) - productos_completos
        
        logger.info(f"{'='*80}")
        logger.info(f"📊 RESUMEN:")
        logger.info(f"   Total productos: {len(productos)}")
        logger.info(f"   ✅ Con datos completos: {productos_completos}")
        logger.info(f"   ⚠️  Con datos parciales: {productos_parciales}")
        logger.info(f"{'='*80}\n")


def main():
    """Función principal"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                   PRUEBA SIMPLE DE EXTRACCIÓN DE PRODUCTOS                   ║
║                         Parser Mejorado V2                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    if len(sys.argv) < 2:
        logger.error("❌ Uso: python3 test_parser_simple.py <ruta_pdf>")
        logger.info("\n💡 Ejemplo:")
        logger.info("   python3 test_parser_simple.py ../CUFE/FACTURAS/FE15778.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    test_pdf(pdf_path)
    
    print("✅ Prueba completada\n")


if __name__ == "__main__":
    main()
