#!/usr/bin/env python3
"""
Script para actualizar SOLO las fechas de los documentos DIAN
Sin reprocesar todo el documento ni subir a S3
"""
import sys
import os
from datetime import datetime
import glob

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'CODE/src'))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.invoice_v2 import InvoiceV2
from app.services.pdf_parser_service import PDFParserService

def actualizar_fechas_dian():
    """
    Actualiza SOLO las fechas de los documentos DIAN
    """
    print(f"\n{'='*80}")
    print(f"📅 ACTUALIZACIÓN DIRECTA DE FECHAS DIAN")
    print(f"{'='*80}\n")
    
    # Buscar archivos PDF en la carpeta CUFE/CUFE/
    pdf_files = glob.glob("CUFE/CUFE/*.pdf")
    
    if not pdf_files:
        print(f"❌ No se encontraron archivos PDF en CUFE/CUFE/")
        return
    
    print(f"📊 Total de archivos PDF encontrados: {len(pdf_files)}\n")
    
    db = SessionLocal()
    
    try:
        # Confirmar antes de proceder
        print(f"ℹ️  Este proceso actualizará SOLO las fechas de {len(pdf_files)} archivos")
        print(f"   Buscará 'Fecha y hora de expedición' > 'Fecha de Emisión' > 'Documento generado el'")
        print(f"   NO reprocesará todo el documento ni subirá a S3")
        respuesta = input(f"\n¿Deseas continuar? (si/no): ")
        
        if respuesta.lower() not in ['si', 's', 'yes', 'y']:
            print(f"\n❌ Proceso cancelado por el usuario")
            return
        
        print(f"\n{'─'*80}")
        print(f"🚀 Iniciando actualización...")
        print(f"{'─'*80}\n")
        
        # Contadores
        actualizados = 0
        sin_cambios = 0
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
                
                # Guardar fecha anterior
                fecha_anterior = factura.fecha_emision
                
                # Extraer texto del PDF
                text = PDFParserService.extract_text_from_pdf(pdf_path, max_pages=999)
                
                if not text:
                    print(f"❌ No se pudo extraer texto")
                    errores.append({
                        'cufe': cufe_corto,
                        'error': 'No se pudo extraer texto del PDF'
                    })
                    continue
                
                # Extraer fecha usando el método mejorado
                fecha_nueva = PDFParserService.extract_dian_date(text)
                
                if not fecha_nueva:
                    print(f"⚠️ No se pudo extraer fecha")
                    errores.append({
                        'cufe': cufe_corto,
                        'error': 'No se pudo extraer fecha del PDF'
                    })
                    continue
                
                # Actualizar solo si cambió
                if fecha_anterior != fecha_nueva:
                    factura.fecha_emision = fecha_nueva
                    db.commit()
                    
                    fecha_ant_str = fecha_anterior.strftime('%d/%m/%Y') if fecha_anterior else 'Sin fecha'
                    fecha_nue_str = fecha_nueva.strftime('%d/%m/%Y')
                    print(f"✅ {fecha_ant_str} → {fecha_nue_str}")
                    actualizados += 1
                else:
                    fecha_str = fecha_nueva.strftime('%d/%m/%Y')
                    print(f"➖ Sin cambios ({fecha_str})")
                    sin_cambios += 1
                
            except Exception as e:
                print(f"❌ Error: {str(e)[:50]}")
                errores.append({
                    'cufe': cufe_corto,
                    'error': str(e)
                })
        
        # Resumen final
        print(f"\n{'='*80}")
        print(f"📊 RESUMEN DE LA ACTUALIZACIÓN")
        print(f"{'='*80}")
        print(f"   Total archivos:        {len(pdf_files)}")
        print(f"   ✅ Actualizados:       {actualizados}")
        print(f"   ➖ Sin cambios:        {sin_cambios}")
        print(f"   ⚠️ No encontrados:     {no_encontrados}")
        print(f"   ❌ Errores:            {len(errores)}")
        print(f"{'='*80}")
        
        if errores:
            print(f"\n⚠️ ERRORES ENCONTRADOS:")
            print(f"{'─'*80}")
            for error in errores[:10]:  # Mostrar solo los primeros 10
                print(f"   CUFE: {error['cufe']} - Error: {error['error']}")
            if len(errores) > 10:
                print(f"   ... y {len(errores) - 10} errores más")
            print(f"{'─'*80}")
        
        if actualizados > 0:
            print(f"\n✅ Actualización completada")
            print(f"   {actualizados} fechas actualizadas correctamente")
        
        print(f"   Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    actualizar_fechas_dian()
