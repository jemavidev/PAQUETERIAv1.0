#!/usr/bin/env python3
"""
Script para probar la extracción mejorada de productos
Analiza archivos DIAN existentes y muestra los productos extraídos
"""
import sys
import os
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from app.services.pdf_parser_service import PDFParserService
from app.database import SessionLocal
from app.models.invoice_v2 import InvoiceV2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_product_extraction_from_db():
    """
    Prueba la extracción de productos de facturas que ya tienen archivo DIAN
    """
    db = SessionLocal()
    
    try:
        # Buscar facturas con archivo DIAN
        facturas_con_dian = db.query(InvoiceV2).filter(
            InvoiceV2.archivo_dian_s3_key.isnot(None)
        ).limit(5).all()
        
        if not facturas_con_dian:
            logger.warning("⚠️ No se encontraron facturas con archivo DIAN en la base de datos")
            return
        
        logger.info(f"📊 Encontradas {len(facturas_con_dian)} facturas con archivo DIAN")
        logger.info("="*80)
        
        for i, factura in enumerate(facturas_con_dian, 1):
            logger.info(f"\n{'='*80}")
            logger.info(f"🧾 FACTURA {i}/{len(facturas_con_dian)}")
            logger.info(f"{'='*80}")
            logger.info(f"CUFE: {factura.cufe[:32]}...")
            logger.info(f"Proveedor: {factura.dian_emisor_razon_social or factura.proveedor_nombre}")
            logger.info(f"Número: {factura.numero_factura}")
            logger.info(f"Fecha: {factura.fecha_emision}")
            logger.info(f"Total: ${factura.dian_total_neto or factura.total_factura:,.2f}")
            logger.info(f"Archivo S3: {factura.archivo_dian_s3_key}")
            
            # Contar productos actuales
            productos_actuales = len(factura.productos)
            logger.info(f"Productos en DB actualmente: {productos_actuales}")
            
            # Intentar descargar y parsear el archivo
            logger.info(f"\n📄 Intentando parsear archivo DIAN...")
            
            # Nota: Aquí necesitaríamos descargar el archivo de S3
            # Por ahora, solo mostramos la info
            logger.info(f"⚠️ Para probar la extracción, necesitamos descargar el archivo de S3")
            logger.info(f"   Archivo: {factura.archivo_dian_s3_key}")
            
            # Mostrar productos actuales
            if productos_actuales > 0:
                logger.info(f"\n📦 Productos actuales en DB:")
                for j, prod in enumerate(factura.productos[:5], 1):
                    logger.info(f"   {j}. {prod.codigo_producto or 'SIN CÓDIGO'} - {prod.descripcion[:50]}...")
                    logger.info(f"      Cantidad: {prod.cantidad}, Precio: ${prod.precio_unitario or 0:,.2f}, Total: ${prod.total_item or 0:,.2f}")
                
                if productos_actuales > 5:
                    logger.info(f"   ... y {productos_actuales - 5} productos más")
            
            logger.info("")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def test_product_extraction_from_local_pdf(pdf_path: str):
    """
    Prueba la extracción de productos de un PDF local
    """
    if not os.path.exists(pdf_path):
        logger.error(f"❌ Archivo no encontrado: {pdf_path}")
        return
    
    logger.info(f"{'='*80}")
    logger.info(f"🧪 PRUEBA DE EXTRACCIÓN DE PRODUCTOS")
    logger.info(f"{'='*80}")
    logger.info(f"Archivo: {pdf_path}")
    logger.info("")
    
    try:
        # Parsear documento
        logger.info("📄 Parseando documento DIAN...")
        data = PDFParserService.parse_dian_document(pdf_path)
        
        if 'error' in data:
            logger.error(f"❌ Error al parsear: {data['error']}")
            return
        
        # Mostrar información general
        logger.info(f"\n📋 INFORMACIÓN GENERAL:")
        logger.info(f"   CUFE: {data.get('cufe', 'NO ENCONTRADO')[:32]}...")
        logger.info(f"   Tipo: {data.get('tipo_documento', 'N/A')}")
        logger.info(f"   Número: {data.get('numero_documento', 'N/A')}")
        logger.info(f"   Fecha: {data.get('fecha_emision', 'N/A')}")
        
        emisor = data.get('emisor', {})
        logger.info(f"\n🏢 EMISOR:")
        logger.info(f"   Razón Social: {emisor.get('razon_social', 'N/A')}")
        logger.info(f"   NIT: {emisor.get('nit', 'N/A')}")
        
        totales = data.get('totales', {})
        logger.info(f"\n💰 TOTALES:")
        logger.info(f"   Subtotal: ${totales.get('subtotal', 0):,.2f}")
        logger.info(f"   IVA: ${totales.get('total_iva', 0):,.2f}")
        logger.info(f"   Total Neto: ${totales.get('total_neto', 0):,.2f}")
        
        # Mostrar productos extraídos
        productos = data.get('productos', [])
        logger.info(f"\n📦 PRODUCTOS EXTRAÍDOS: {len(productos)}")
        logger.info(f"{'='*80}")
        
        if not productos:
            logger.warning("⚠️ No se extrajeron productos del PDF")
            logger.info("\n💡 Posibles razones:")
            logger.info("   - El PDF no tiene una sección de productos clara")
            logger.info("   - El formato de la tabla es diferente al esperado")
            logger.info("   - Los productos están en un formato no estándar")
        else:
            for i, prod in enumerate(productos, 1):
                logger.info(f"\n{i}. Producto:")
                logger.info(f"   Código: {prod.get('codigo_producto', 'N/A')}")
                logger.info(f"   Descripción: {prod.get('descripcion', 'N/A')[:80]}")
                logger.info(f"   Cantidad: {prod.get('cantidad', 'N/A')}")
                logger.info(f"   Precio Unit.: ${prod.get('precio_unitario', 0):,.2f}" if prod.get('precio_unitario') else "   Precio Unit.: N/A")
                logger.info(f"   IVA: {prod.get('iva_porcentaje', 'N/A')}%")
                logger.info(f"   Total: ${prod.get('total_item', 0):,.2f}" if prod.get('total_item') else "   Total: N/A")
                
                if i >= 10:
                    logger.info(f"\n... y {len(productos) - 10} productos más")
                    break
        
        # Resumen
        logger.info(f"\n{'='*80}")
        logger.info(f"📊 RESUMEN:")
        logger.info(f"   Total productos extraídos: {len(productos)}")
        
        productos_completos = sum(1 for p in productos if p.get('cantidad') and p.get('precio_unitario'))
        productos_parciales = len(productos) - productos_completos
        
        logger.info(f"   Productos con datos completos: {productos_completos}")
        logger.info(f"   Productos con datos parciales: {productos_parciales}")
        
        if productos_completos > 0:
            logger.info(f"\n✅ Extracción exitosa!")
        elif productos_parciales > 0:
            logger.info(f"\n⚠️ Extracción parcial - algunos productos no tienen todos los datos")
        else:
            logger.info(f"\n❌ No se pudieron extraer productos con datos completos")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """
    Función principal
    """
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                   PRUEBA DE EXTRACCIÓN DE PRODUCTOS                          ║
║                         Parser Mejorado V2                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    if len(sys.argv) > 1:
        # Modo: probar con archivo específico
        pdf_path = sys.argv[1]
        test_product_extraction_from_local_pdf(pdf_path)
    else:
        # Modo: analizar facturas en DB
        logger.info("🔍 Modo: Analizar facturas existentes en la base de datos")
        logger.info("💡 Para probar con un PDF específico: python test_new_product_extraction.py <ruta_pdf>")
        logger.info("")
        test_product_extraction_from_db()
    
    print(f"\n{'='*80}")
    print("✅ Prueba completada")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
