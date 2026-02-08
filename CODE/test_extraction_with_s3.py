#!/usr/bin/env python3
"""
Script para probar la extracción de productos descargando archivos de S3
"""
import sys
import os
from pathlib import Path
import tempfile

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from app.services.pdf_parser_service import PDFParserService
from app.services.s3_service import S3Service
from app.database import SessionLocal
from app.models.invoice_v2 import InvoiceV2
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def test_extraction_with_s3_download(limit=3):
    """
    Descarga archivos DIAN de S3 y prueba la extracción de productos
    """
    db = SessionLocal()
    s3_service = S3Service()
    
    try:
        # Buscar facturas con archivo DIAN
        facturas = db.query(InvoiceV2).filter(
            InvoiceV2.archivo_dian_s3_key.isnot(None)
        ).limit(limit).all()
        
        if not facturas:
            logger.warning("⚠️ No se encontraron facturas con archivo DIAN")
            return
        
        logger.info(f"\n{'='*80}")
        logger.info(f"🧪 PRUEBA DE EXTRACCIÓN CON {len(facturas)} FACTURAS")
        logger.info(f"{'='*80}\n")
        
        resultados = []
        
        for i, factura in enumerate(facturas, 1):
            logger.info(f"\n{'─'*80}")
            logger.info(f"📄 FACTURA {i}/{len(facturas)}")
            logger.info(f"{'─'*80}")
            logger.info(f"CUFE: {factura.cufe[:32]}...")
            logger.info(f"Proveedor: {factura.dian_emisor_razon_social or factura.proveedor_nombre or 'N/A'}")
            logger.info(f"Número: {factura.numero_factura or 'N/A'}")
            logger.info(f"Fecha: {factura.fecha_emision or 'N/A'}")
            logger.info(f"Total: ${(factura.dian_total_neto or factura.total_factura or 0):,.2f}")
            logger.info(f"Productos en DB: {len(factura.productos)}")
            
            # Descargar archivo de S3
            try:
                logger.info(f"\n📥 Descargando archivo de S3...")
                logger.info(f"   Key: {factura.archivo_dian_s3_key}")
                
                file_content = s3_service.download_file(factura.archivo_dian_s3_key)
                
                if not file_content:
                    logger.error(f"❌ No se pudo descargar el archivo")
                    resultados.append({
                        'factura': i,
                        'cufe': factura.cufe[:16],
                        'status': 'error_descarga',
                        'productos_db': len(factura.productos),
                        'productos_extraidos': 0
                    })
                    continue
                
                logger.info(f"✅ Archivo descargado ({len(file_content)} bytes)")
                
                # Guardar temporalmente
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                    tmp.write(file_content)
                    tmp_path = tmp.name
                
                # Parsear documento
                logger.info(f"\n🔍 Parseando documento...")
                data = PDFParserService.parse_dian_document(tmp_path)
                
                # Limpiar archivo temporal
                os.unlink(tmp_path)
                
                if 'error' in data:
                    logger.error(f"❌ Error al parsear: {data['error']}")
                    resultados.append({
                        'factura': i,
                        'cufe': factura.cufe[:16],
                        'status': 'error_parser',
                        'productos_db': len(factura.productos),
                        'productos_extraidos': 0
                    })
                    continue
                
                # Analizar productos extraídos
                productos = data.get('productos', [])
                logger.info(f"\n📦 PRODUCTOS EXTRAÍDOS: {len(productos)}")
                
                if productos:
                    productos_completos = sum(1 for p in productos if p.get('cantidad') and p.get('precio_unitario'))
                    productos_parciales = len(productos) - productos_completos
                    
                    logger.info(f"   ✅ Con datos completos: {productos_completos}")
                    logger.info(f"   ⚠️  Con datos parciales: {productos_parciales}")
                    
                    # Mostrar primeros 3 productos
                    logger.info(f"\n   Muestra de productos:")
                    for j, prod in enumerate(productos[:3], 1):
                        logger.info(f"   {j}. {prod.get('codigo_producto', 'SIN CÓDIGO')}")
                        logger.info(f"      Desc: {prod.get('descripcion', 'N/A')[:60]}")
                        logger.info(f"      Cant: {prod.get('cantidad', 'N/A')} | Precio: ${prod.get('precio_unitario', 0):,.2f} | Total: ${prod.get('total_item', 0):,.2f}")
                    
                    if len(productos) > 3:
                        logger.info(f"   ... y {len(productos) - 3} más")
                    
                    resultados.append({
                        'factura': i,
                        'cufe': factura.cufe[:16],
                        'status': 'ok',
                        'productos_db': len(factura.productos),
                        'productos_extraidos': len(productos),
                        'productos_completos': productos_completos,
                        'productos_parciales': productos_parciales
                    })
                else:
                    logger.warning(f"⚠️ No se extrajeron productos")
                    resultados.append({
                        'factura': i,
                        'cufe': factura.cufe[:16],
                        'status': 'sin_productos',
                        'productos_db': len(factura.productos),
                        'productos_extraidos': 0
                    })
                
            except Exception as e:
                logger.error(f"❌ Error procesando factura: {e}")
                import traceback
                traceback.print_exc()
                resultados.append({
                    'factura': i,
                    'cufe': factura.cufe[:16],
                    'status': 'error_excepcion',
                    'productos_db': len(factura.productos),
                    'productos_extraidos': 0
                })
        
        # Resumen final
        logger.info(f"\n{'='*80}")
        logger.info(f"📊 RESUMEN FINAL")
        logger.info(f"{'='*80}\n")
        
        logger.info(f"{'Factura':<10} {'CUFE':<18} {'Status':<20} {'DB':<6} {'Extraídos':<12} {'Completos':<10}")
        logger.info(f"{'-'*80}")
        
        for r in resultados:
            completos = r.get('productos_completos', '-')
            logger.info(f"{r['factura']:<10} {r['cufe']:<18} {r['status']:<20} {r['productos_db']:<6} {r['productos_extraidos']:<12} {completos:<10}")
        
        # Estadísticas
        total_ok = sum(1 for r in resultados if r['status'] == 'ok')
        total_sin_productos = sum(1 for r in resultados if r['status'] == 'sin_productos')
        total_errores = len(resultados) - total_ok - total_sin_productos
        
        logger.info(f"\n{'='*80}")
        logger.info(f"✅ Exitosas: {total_ok}/{len(resultados)}")
        logger.info(f"⚠️  Sin productos: {total_sin_productos}/{len(resultados)}")
        logger.info(f"❌ Errores: {total_errores}/{len(resultados)}")
        
        if total_ok > 0:
            total_extraidos = sum(r.get('productos_extraidos', 0) for r in resultados if r['status'] == 'ok')
            total_completos = sum(r.get('productos_completos', 0) for r in resultados if r['status'] == 'ok')
            logger.info(f"\n📦 Total productos extraídos: {total_extraidos}")
            logger.info(f"✅ Con datos completos: {total_completos}")
            logger.info(f"⚠️  Con datos parciales: {total_extraidos - total_completos}")
        
        logger.info(f"{'='*80}\n")
        
    except Exception as e:
        logger.error(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def main():
    """
    Función principal
    """
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║              PRUEBA DE EXTRACCIÓN DE PRODUCTOS CON S3                        ║
║                         Parser Mejorado V2                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    limit = 3
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except:
            logger.warning(f"⚠️ Argumento inválido, usando límite por defecto: {limit}")
    
    logger.info(f"🔍 Probando con {limit} facturas")
    logger.info(f"💡 Para cambiar el límite: python test_extraction_with_s3.py <numero>")
    
    test_extraction_with_s3_download(limit)
    
    print("\n✅ Prueba completada\n")


if __name__ == "__main__":
    main()
