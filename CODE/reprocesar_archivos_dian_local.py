#!/usr/bin/env python3
"""
Script para reprocesar archivos DIAN desde archivos locales
Actualiza los totales con el patrón de extracción mejorado
"""
import sys
import os
from datetime import datetime
import glob

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.invoice_v2 import InvoiceV2
from app.services.invoice_v2_service import InvoiceV2Service

def reprocesar_archivos_dian_local():
    """
    Reprocesa archivos DIAN desde la carpeta local CUFE/CUFE/
    """
    print(f"\n{'='*80}")
    print(f"🔄 REPROCESAMIENTO DE ARCHIVOS DIAN LOCALES")
    print(f"{'='*80}\n")
    
    # Buscar archivos PDF en la carpeta CUFE/CUFE/
    pdf_files = glob.glob("CUFE/CUFE/*.pdf")
    
    if not pdf_files:
        print(f"❌ No se encontraron archivos PDF en CUFE/CUFE/")
        return
    
    print(f"📊 Total de archivos PDF encontrados: {len(pdf_files)}\n")
    
    db = SessionLocal()
    invoice_service = InvoiceV2Service(db)
    
    try:
        # Confirmar antes de proceder
        print(f"⚠️ ADVERTENCIA: Este proceso reprocesará {len(pdf_files)} archivos")
        print(f"   Esto actualizará todos los datos extraídos del archivo DIAN")
        respuesta = input(f"\n¿Deseas continuar? (si/no): ")
        
        if respuesta.lower() not in ['si', 's', 'yes', 'y']:
            print(f"\n❌ Proceso cancelado por el usuario")
            return
        
        print(f"\n{'─'*80}")
        print(f"🚀 Iniciando reprocesamiento...")
        print(f"{'─'*80}\n")
        
        # Contadores
        exitosos = 0
        fallidos = 0
        no_encontrados = 0
        errores = []
        
        # Procesar cada archivo
        for i, pdf_path in enumerate(pdf_files, 1):
            # Extraer CUFE del nombre del archivo
            filename = os.path.basename(pdf_path)
            cufe = filename.replace('.pdf', '')
            cufe_corto = cufe[:16]
            
            print(f"[{i}/{len(pdf_files)}] {cufe_corto}... ", end='', flush=True)
            
            try:
                # Buscar factura en la BD
                factura = db.query(InvoiceV2).filter_by(cufe=cufe).first()
                
                if not factura:
                    print(f"⚠️ No encontrada en BD")
                    no_encontrados += 1
                    continue
                
                # Reprocesar con el servicio
                invoice_service.process_dian_document(
                    cufe=cufe,
                    pdf_path=pdf_path,
                    file_obj=None  # No subir de nuevo a S3
                )
                
                # Obtener datos actualizados
                db.refresh(factura)
                
                total = factura.dian_total_neto or 0
                print(f"✅ ${total:,.0f}")
                
                exitosos += 1
                
            except Exception as e:
                print(f"❌ Error: {str(e)[:50]}")
                fallidos += 1
                errores.append({
                    'cufe': cufe_corto,
                    'error': str(e)
                })
        
        # Resumen final
        print(f"\n{'='*80}")
        print(f"📊 RESUMEN DEL REPROCESAMIENTO")
        print(f"{'='*80}")
        print(f"   Total archivos:        {len(pdf_files)}")
        print(f"   ✅ Exitosos:           {exitosos}")
        print(f"   ⚠️ No encontrados:     {no_encontrados}")
        print(f"   ❌ Fallidos:           {fallidos}")
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
    reprocesar_archivos_dian_local()
