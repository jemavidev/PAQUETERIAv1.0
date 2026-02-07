#!/usr/bin/env python3
"""
Script simplificado para corregir el intercambio de emisor/adquiriente
Ejecuta directamente desde el directorio CODE
"""
import sys
import os

# Cambiar al directorio CODE
os.chdir('/home/stk/Documents/GIT/PAQUETEX v1.0/CODE')
sys.path.insert(0, '/home/stk/Documents/GIT/PAQUETEX v1.0/CODE')

# Ahora importar
from sqlalchemy.orm import Session
from src.app.database import SessionLocal
from src.app.models.invoice_v2 import InvoiceV2
from src.app.services.pdf_parser_service import PDFParserService
from src.app.services.s3_service import S3Service
import logging
from datetime import datetime
import tempfile

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def fix_invoice_emisor_adquiriente(db: Session, invoice: InvoiceV2, s3_service: S3Service) -> bool:
    """
    Reprocesa un archivo DIAN para corregir emisor/adquiriente
    """
    try:
        # Verificar que tenga archivo DIAN
        if not invoice.archivo_dian_s3_key:
            logger.warning(f"⚠️ Factura {invoice.cufe[:16]}... no tiene archivo DIAN")
            return False
        
        logger.info(f"🔄 Reprocesando factura {invoice.cufe[:16]}...")
        logger.info(f"   Emisor actual: {invoice.dian_emisor_razon_social}")
        logger.info(f"   Adquiriente actual: {invoice.dian_adquiriente_razon_social}")
        
        # Descargar archivo DIAN desde S3
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_path = tmp_file.name
            
            # Descargar de S3
            file_content = s3_service.download_file(invoice.archivo_dian_s3_key)
            if not file_content:
                logger.error(f"❌ No se pudo descargar archivo DIAN de S3: {invoice.archivo_dian_s3_key}")
                return False
            
            tmp_file.write(file_content)
            tmp_file.flush()
            
            # Parsear con la lógica corregida
            logger.info(f"📄 Parseando archivo DIAN...")
            data = PDFParserService.parse_dian_document(tmp_path)
            
            # Limpiar archivo temporal
            os.unlink(tmp_path)
            
            if 'error' in data:
                logger.error(f"❌ Error parseando: {data['error']}")
                return False
            
            # Extraer datos corregidos
            emisor = data.get('emisor', {})
            adquiriente = data.get('adquiriente', {})
            
            nuevo_emisor = emisor.get('razon_social')
            nuevo_adquiriente = adquiriente.get('razon_social')
            
            logger.info(f"   Nuevo emisor: {nuevo_emisor}")
            logger.info(f"   Nuevo adquiriente: {nuevo_adquiriente}")
            
            # Verificar si realmente cambió
            if nuevo_emisor == invoice.dian_emisor_razon_social and nuevo_adquiriente == invoice.dian_adquiriente_razon_social:
                logger.info(f"✅ Datos ya están correctos, no se requiere actualización")
                return True
            
            # Actualizar emisor
            invoice.dian_emisor_razon_social = emisor.get('razon_social')
            invoice.dian_emisor_nit = emisor.get('nit')
            invoice.dian_emisor_regimen_fiscal = emisor.get('regimen_fiscal')
            invoice.dian_emisor_direccion = emisor.get('direccion')
            invoice.dian_emisor_telefono = emisor.get('telefono')
            invoice.dian_emisor_email = emisor.get('email')
            
            # Actualizar adquiriente
            invoice.dian_adquiriente_razon_social = adquiriente.get('razon_social')
            invoice.dian_adquiriente_nit = adquiriente.get('nit')
            
            # Actualizar otros datos si están disponibles
            if data.get('numero_documento'):
                invoice.numero_factura = data.get('numero_documento')
            
            if data.get('fecha_emision'):
                invoice.fecha_emision = data.get('fecha_emision')
            
            # Actualizar totales
            totales = data.get('totales', {})
            if totales.get('total_neto'):
                invoice.dian_total_neto = totales.get('total_neto')
            if totales.get('subtotal'):
                invoice.dian_subtotal = totales.get('subtotal')
            if totales.get('total_iva'):
                invoice.dian_total_iva = totales.get('total_iva')
            
            # Marcar como validado
            invoice.dian_validado = True
            invoice.dian_fecha_validacion = datetime.utcnow()
            
            db.commit()
            
            logger.info(f"✅ Factura {invoice.cufe[:16]}... actualizada correctamente")
            logger.info(f"   ✓ Emisor corregido: {invoice.dian_emisor_razon_social}")
            logger.info(f"   ✓ Adquiriente corregido: {invoice.dian_adquiriente_razon_social}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error procesando factura {invoice.cufe[:16]}...: {e}")
        import traceback
        logger.error(traceback.format_exc())
        db.rollback()
        return False


def main():
    """
    Reprocesa todas las facturas con archivos DIAN
    """
    logger.info("=" * 80)
    logger.info("🔧 SCRIPT DE CORRECCIÓN: Emisor/Adquiriente en Facturas DIAN")
    logger.info("=" * 80)
    
    db = SessionLocal()
    s3_service = S3Service()
    
    try:
        # Obtener todas las facturas con archivo DIAN
        facturas = db.query(InvoiceV2).filter(
            InvoiceV2.archivo_dian_s3_key.isnot(None)
        ).all()
        
        total = len(facturas)
        logger.info(f"\n📊 Total de facturas con archivo DIAN: {total}")
        
        if total == 0:
            logger.info("ℹ️ No hay facturas con archivos DIAN para procesar")
            return
        
        # Confirmar antes de proceder
        print(f"\n⚠️ Se van a reprocesar {total} facturas.")
        print("   Esto actualizará los datos de emisor y adquiriente desde los archivos DIAN.")
        respuesta = input("\n¿Deseas continuar? (s/n): ")
        
        if respuesta.lower() != 's':
            logger.info("❌ Operación cancelada por el usuario")
            return
        
        logger.info("\n🚀 Iniciando reprocesamiento...\n")
        
        exitosas = 0
        fallidas = 0
        sin_cambios = 0
        
        for i, factura in enumerate(facturas, 1):
            logger.info(f"\n[{i}/{total}] Procesando factura...")
            
            # Guardar datos originales para comparar
            emisor_original = factura.dian_emisor_razon_social
            
            resultado = fix_invoice_emisor_adquiriente(db, factura, s3_service)
            
            if resultado:
                # Verificar si hubo cambio
                if factura.dian_emisor_razon_social != emisor_original:
                    exitosas += 1
                else:
                    sin_cambios += 1
            else:
                fallidas += 1
        
        # Resumen final
        logger.info("\n" + "=" * 80)
        logger.info("📊 RESUMEN FINAL")
        logger.info("=" * 80)
        logger.info(f"✅ Facturas corregidas: {exitosas}")
        logger.info(f"ℹ️ Facturas sin cambios: {sin_cambios}")
        logger.info(f"❌ Facturas fallidas: {fallidas}")
        logger.info(f"📈 Total procesadas: {total}")
        logger.info("=" * 80)
        
        if exitosas > 0:
            logger.info("\n✅ Corrección completada exitosamente")
            logger.info("   Los datos de emisor/adquiriente han sido actualizados correctamente")
        
    except Exception as e:
        logger.error(f"❌ Error en el script principal: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        db.close()


if __name__ == "__main__":
    main()
