#!/usr/bin/env python3
"""
Script para reprocesar todos los archivos DIAN desde S3
Actualiza los totales con el patrón de extracción mejorado
"""
import sys
import os
from datetime import datetime

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.invoice_v2 import InvoiceV2
from app.services.invoice_v2_service import InvoiceV2Service
from app.services.s3_storage_service import S3StorageService
import tempfile

def reprocesar_archivos_dian():
    """
    Reprocesa todos los archivos DIAN desde S3
    """
    print(f"\n{'='*80}")
    print(f"🔄 REPROCESAMIENTO DE ARCHIVOS DIAN DESDE S3")
    print(f"{'='*80}\n")
    
    db = SessionLocal()
    
    try:
        # Obtener todas las facturas que tienen archivo DIAN en S3
        facturas = db.query(InvoiceV2).filter(
            InvoiceV2.archivo_dian_s3_key.isnot(None)
        ).all()
        
        total_facturas = len(facturas)
        print(f"📊 Total de facturas con archivo DIAN en S3: {total_facturas}")
        
        if total_facturas == 0:
            print(f"\n⚠️ No hay facturas con archivos DIAN en S3")
            return
        
        # Confirmar antes de proceder
        print(f"\n⚠️ ADVERTENCIA: Este proceso reprocesará {total_facturas} facturas")
        print(f"   Esto actualizará todos los datos extraídos del archivo DIAN")
        respuesta = input(f"\n¿Deseas continuar? (si/no): ")
        
        if respuesta.lower() not in ['si', 's', 'yes', 'y']:
            print(f"\n❌ Proceso cancelado por el usuario")
            return
        
        print(f"\n{'─'*80}")
        print(f"🚀 Iniciando reprocesamiento...")
        print(f"{'─'*80}\n")
        
        # Inicializar servicio S3
        s3_service = S3StorageService()
        invoice_service = InvoiceV2Service(db)
        
        # Contadores
        exitosos = 0
        fallidos = 0
        errores = []
        
        # Procesar cada factura
        for i, factura in enumerate(facturas, 1):
            cufe_corto = factura.cufe[:16]
            print(f"\n[{i}/{total_facturas}] Procesando: {cufe_corto}...")
            print(f"   S3 Key: {factura.archivo_dian_s3_key}")
            
            try:
                # Descargar archivo desde S3
                print(f"   📥 Descargando desde S3...")
                file_content = s3_service.download_pdf(factura.cufe, prefix='invoices/dian')
                
                if not file_content:
                    raise Exception("No se pudo descargar el archivo desde S3")
                
                # Guardar temporalmente
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                    tmp_file.write(file_content)
                    tmp_path = tmp_file.name
                
                print(f"   🔍 Reprocesando archivo DIAN...")
                
                # Reprocesar con el servicio (sin subir de nuevo a S3)
                invoice_service.process_dian_document(
                    cufe=factura.cufe,
                    pdf_path=tmp_path,
                    file_obj=None  # No subir de nuevo
                )
                
                # Limpiar archivo temporal
                os.unlink(tmp_path)
                
                # Obtener datos actualizados
                db.refresh(factura)
                
                print(f"   ✅ Reprocesado exitosamente")
                print(f"      Total actualizado: ${factura.dian_total_neto:,.2f}" if factura.dian_total_neto else "      Total: No disponible")
                
                exitosos += 1
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                fallidos += 1
                errores.append({
                    'cufe': cufe_corto,
                    'error': str(e)
                })
        
        # Resumen final
        print(f"\n{'='*80}")
        print(f"📊 RESUMEN DEL REPROCESAMIENTO")
        print(f"{'='*80}")
        print(f"   Total procesadas:  {total_facturas}")
        print(f"   ✅ Exitosas:       {exitosos}")
        print(f"   ❌ Fallidas:       {fallidos}")
        print(f"{'='*80}")
        
        if errores:
            print(f"\n⚠️ ERRORES ENCONTRADOS:")
            print(f"{'─'*80}")
            for error in errores:
                print(f"   CUFE: {error['cufe']} - Error: {error['error']}")
            print(f"{'─'*80}")
        
        print(f"\n✅ Reprocesamiento completado")
        print(f"   Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    reprocesar_archivos_dian()
