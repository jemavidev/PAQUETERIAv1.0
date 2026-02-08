#!/usr/bin/env python3
"""
Script de migración para reprocesar productos de facturas existentes
Descarga archivos DIAN de S3 y extrae productos con el parser mejorado
"""
import sys
import os
from pathlib import Path
import tempfile
from datetime import datetime

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from app.services.pdf_parser_service import PDFParserService
from app.services.s3_service import S3Service
from app.database import SessionLocal
from app.models.invoice_v2 import InvoiceV2, InvoiceProductV2
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProductMigration:
    """Clase para manejar la migración de productos"""
    
    def __init__(self, dry_run=False):
        self.db = SessionLocal()
        self.s3_service = S3Service()
        self.dry_run = dry_run
        self.stats = {
            'total_facturas': 0,
            'procesadas': 0,
            'con_productos': 0,
            'sin_productos': 0,
            'errores': 0,
            'productos_totales': 0,
            'productos_completos': 0,
            'productos_parciales': 0,
        }
    
    def get_facturas_con_dian(self, limit=None):
        """Obtiene facturas que tienen archivo DIAN"""
        query = self.db.query(InvoiceV2).filter(
            InvoiceV2.archivo_dian_s3_key.isnot(None)
        )
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def process_factura(self, factura: InvoiceV2):
        """Procesa una factura individual"""
        try:
            logger.info(f"\n{'='*80}")
            logger.info(f"📄 Procesando factura: {factura.cufe[:32]}...")
            logger.info(f"   Proveedor: {factura.dian_emisor_razon_social or factura.proveedor_nombre or 'N/A'}")
            logger.info(f"   Número: {factura.numero_factura or 'N/A'}")
            logger.info(f"   Fecha: {factura.fecha_emision or 'N/A'}")
            logger.info(f"   Productos actuales en DB: {len(factura.productos)}")
            
            # Descargar archivo de S3
            logger.info(f"📥 Descargando archivo de S3...")
            file_content = self.s3_service.download_file(factura.archivo_dian_s3_key)
            
            if not file_content:
                logger.error(f"❌ No se pudo descargar el archivo")
                self.stats['errores'] += 1
                return False
            
            logger.info(f"✅ Archivo descargado ({len(file_content)} bytes)")
            
            # Guardar temporalmente
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                tmp.write(file_content)
                tmp_path = tmp.name
            
            try:
                # Parsear documento
                logger.info(f"🔍 Parseando documento con parser mejorado...")
                data = PDFParserService.parse_dian_document(tmp_path)
                
                if 'error' in data:
                    logger.error(f"❌ Error al parsear: {data['error']}")
                    self.stats['errores'] += 1
                    return False
                
                # Obtener productos
                productos = data.get('productos', [])
                logger.info(f"📦 Productos extraídos: {len(productos)}")
                
                if not productos:
                    logger.warning(f"⚠️ No se extrajeron productos")
                    self.stats['sin_productos'] += 1
                    return True
                
                # Analizar calidad de productos
                productos_completos = sum(1 for p in productos if p.get('cantidad') and p.get('precio_unitario'))
                productos_parciales = len(productos) - productos_completos
                
                logger.info(f"   ✅ Con datos completos: {productos_completos}")
                logger.info(f"   ⚠️  Con datos parciales: {productos_parciales}")
                
                # Mostrar muestra
                logger.info(f"\n   Muestra de productos:")
                for i, prod in enumerate(productos[:3], 1):
                    logger.info(f"   {i}. {prod.get('codigo_producto', 'SIN CÓDIGO')} - {prod.get('descripcion', 'N/A')[:50]}")
                    logger.info(f"      Cant: {prod.get('cantidad', 'N/A')} | Precio: ${prod.get('precio_unitario', 0):,.2f} | Total: ${prod.get('total_item', 0):,.2f}")
                
                if len(productos) > 3:
                    logger.info(f"   ... y {len(productos) - 3} más")
                
                # Actualizar base de datos (si no es dry-run)
                if not self.dry_run:
                    logger.info(f"\n💾 Actualizando base de datos...")
                    
                    # Eliminar productos anteriores
                    productos_eliminados = self.db.query(InvoiceProductV2).filter_by(cufe=factura.cufe).delete()
                    logger.info(f"   🗑️  Eliminados {productos_eliminados} productos anteriores")
                    
                    # Insertar nuevos productos
                    for i, prod_data in enumerate(productos):
                        producto = InvoiceProductV2(
                            cufe=factura.cufe,
                            linea_numero=i + 1,
                            codigo_producto=prod_data.get('codigo_producto'),
                            descripcion=prod_data.get('descripcion'),
                            cantidad=prod_data.get('cantidad'),
                            unidad_medida=prod_data.get('unidad_medida'),
                            precio_unitario=prod_data.get('precio_unitario'),
                            iva_porcentaje=prod_data.get('iva_porcentaje'),
                            total_item=prod_data.get('total_item'),
                            fecha_compra=factura.fecha_emision.date() if factura.fecha_emision else None,
                            datos_raw=prod_data
                        )
                        self.db.add(producto)
                    
                    self.db.commit()
                    logger.info(f"   ✅ Insertados {len(productos)} productos nuevos")
                else:
                    logger.info(f"\n🔍 DRY-RUN: No se actualizó la base de datos")
                
                # Actualizar estadísticas
                self.stats['con_productos'] += 1
                self.stats['productos_totales'] += len(productos)
                self.stats['productos_completos'] += productos_completos
                self.stats['productos_parciales'] += productos_parciales
                
                return True
                
            finally:
                # Limpiar archivo temporal
                os.unlink(tmp_path)
            
        except Exception as e:
            logger.error(f"❌ Error procesando factura: {e}")
            import traceback
            traceback.print_exc()
            self.stats['errores'] += 1
            return False
    
    def run(self, limit=None):
        """Ejecuta la migración"""
        try:
            logger.info(f"\n{'='*80}")
            logger.info(f"🚀 MIGRACIÓN DE PRODUCTOS - PARSER MEJORADO")
            logger.info(f"{'='*80}")
            logger.info(f"Modo: {'DRY-RUN (sin cambios en DB)' if self.dry_run else 'PRODUCCIÓN (actualiza DB)'}")
            logger.info(f"Límite: {limit if limit else 'Sin límite'}")
            logger.info(f"{'='*80}\n")
            
            # Obtener facturas
            logger.info(f"🔍 Buscando facturas con archivo DIAN...")
            facturas = self.get_facturas_con_dian(limit)
            self.stats['total_facturas'] = len(facturas)
            
            if not facturas:
                logger.warning(f"⚠️ No se encontraron facturas con archivo DIAN")
                return
            
            logger.info(f"✅ Encontradas {len(facturas)} facturas para procesar\n")
            
            # Procesar cada factura
            for i, factura in enumerate(facturas, 1):
                logger.info(f"\n{'─'*80}")
                logger.info(f"Factura {i}/{len(facturas)}")
                
                success = self.process_factura(factura)
                if success:
                    self.stats['procesadas'] += 1
                
                # Pausa cada 10 facturas
                if i % 10 == 0:
                    logger.info(f"\n⏸️  Pausa - Procesadas {i}/{len(facturas)} facturas")
                    logger.info(f"   Exitosas: {self.stats['procesadas']}, Errores: {self.stats['errores']}")
            
            # Resumen final
            self.print_summary()
            
        except Exception as e:
            logger.error(f"❌ Error general: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.db.close()
    
    def print_summary(self):
        """Imprime resumen de la migración"""
        logger.info(f"\n{'='*80}")
        logger.info(f"📊 RESUMEN DE MIGRACIÓN")
        logger.info(f"{'='*80}\n")
        
        logger.info(f"Total facturas: {self.stats['total_facturas']}")
        logger.info(f"✅ Procesadas exitosamente: {self.stats['procesadas']}")
        logger.info(f"❌ Errores: {self.stats['errores']}")
        logger.info(f"")
        logger.info(f"📦 Con productos extraídos: {self.stats['con_productos']}")
        logger.info(f"⚠️  Sin productos: {self.stats['sin_productos']}")
        logger.info(f"")
        logger.info(f"Total productos extraídos: {self.stats['productos_totales']}")
        logger.info(f"   ✅ Con datos completos: {self.stats['productos_completos']}")
        logger.info(f"   ⚠️  Con datos parciales: {self.stats['productos_parciales']}")
        
        if self.stats['productos_totales'] > 0:
            porcentaje_completos = (self.stats['productos_completos'] / self.stats['productos_totales']) * 100
            logger.info(f"   📈 Porcentaje completos: {porcentaje_completos:.1f}%")
        
        logger.info(f"\n{'='*80}")
        
        if self.dry_run:
            logger.info(f"🔍 DRY-RUN: No se realizaron cambios en la base de datos")
        else:
            logger.info(f"✅ Migración completada - Base de datos actualizada")
        
        logger.info(f"{'='*80}\n")


def main():
    """Función principal"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║              MIGRACIÓN DE PRODUCTOS - PARSER MEJORADO V2                     ║
║                                                                              ║
║  Este script reprocesa facturas existentes para extraer productos           ║
║  con el parser mejorado que incluye cantidad, precio, IVA, etc.             ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Parsear argumentos
    dry_run = '--dry-run' in sys.argv or '-d' in sys.argv
    limit = None
    
    for arg in sys.argv[1:]:
        if arg.isdigit():
            limit = int(arg)
    
    # Confirmar si no es dry-run
    if not dry_run:
        print("⚠️  ADVERTENCIA: Este script modificará la base de datos")
        print("   - Eliminará productos existentes")
        print("   - Insertará productos nuevos extraídos con el parser mejorado")
        print("")
        respuesta = input("¿Deseas continuar? (escribe 'SI' para confirmar): ")
        
        if respuesta.upper() != 'SI':
            print("\n❌ Migración cancelada")
            return
    
    print("")
    logger.info(f"Iniciando migración...")
    logger.info(f"Modo: {'DRY-RUN' if dry_run else 'PRODUCCIÓN'}")
    logger.info(f"Límite: {limit if limit else 'Sin límite'}")
    
    # Ejecutar migración
    migration = ProductMigration(dry_run=dry_run)
    migration.run(limit=limit)
    
    print("\n✅ Script completado\n")


if __name__ == "__main__":
    main()
