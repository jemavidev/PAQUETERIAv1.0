#!/usr/bin/env python3
"""
Script para analizar los totales actuales vs los que se extraerían con el nuevo patrón
NO modifica la base de datos, solo muestra un reporte
"""
import sys
import os
from datetime import datetime

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.invoice_v2 import InvoiceV2
from app.services.pdf_parser_service import PDFParserService
from app.services.s3_storage_service import S3StorageService
import tempfile

def analizar_totales():
    """
    Analiza los totales actuales vs los nuevos sin modificar la BD
    """
    print(f"\n{'='*80}")
    print(f"🔍 ANÁLISIS DE TOTALES - ARCHIVOS DIAN EN S3")
    print(f"{'='*80}\n")
    
    db = SessionLocal()
    
    try:
        # Obtener todas las facturas que tienen archivo DIAN en S3
        facturas = db.query(InvoiceV2).filter(
            InvoiceV2.archivo_dian_s3_key.isnot(None)
        ).all()
        
        total_facturas = len(facturas)
        print(f"📊 Total de facturas con archivo DIAN en S3: {total_facturas}\n")
        
        if total_facturas == 0:
            print(f"⚠️ No hay facturas con archivos DIAN en S3")
            return
        
        # Inicializar servicio S3
        s3_service = S3StorageService()
        
        # Contadores
        diferencias = []
        sin_cambios = 0
        errores = []
        
        print(f"{'─'*80}")
        print(f"Analizando facturas...")
        print(f"{'─'*80}\n")
        
        # Analizar cada factura
        for i, factura in enumerate(facturas, 1):
            cufe_corto = factura.cufe[:16]
            total_actual = factura.dian_total_neto or 0
            
            print(f"[{i}/{total_facturas}] {cufe_corto}... ", end='')
            
            try:
                # Descargar archivo desde S3 usando el hash del CUFE
                file_content = s3_service.download_pdf(factura.cufe, prefix='invoices/dian')
                
                if not file_content:
                    raise Exception("No se pudo descargar desde S3")
                
                # Guardar temporalmente
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                    tmp_file.write(file_content)
                    tmp_path = tmp_file.name
                
                # Extraer datos con el nuevo patrón
                data = PDFParserService.parse_dian_document(tmp_path)
                
                # Limpiar archivo temporal
                os.unlink(tmp_path)
                
                if 'error' in data:
                    raise Exception(data['error'])
                
                totales = data.get('totales', {})
                total_nuevo = totales.get('total_neto') or 0
                
                # Comparar
                if total_actual != total_nuevo:
                    diferencia = {
                        'cufe': cufe_corto,
                        'cufe_completo': factura.cufe,
                        'numero': factura.numero_factura or '-',
                        'emisor': factura.dian_emisor_razon_social or '-',
                        'actual': float(total_actual),
                        'nuevo': float(total_nuevo),
                        'diferencia': float(total_nuevo - total_actual)
                    }
                    diferencias.append(diferencia)
                    print(f"⚠️ DIFERENCIA: ${total_actual:,.0f} → ${total_nuevo:,.0f}")
                else:
                    sin_cambios += 1
                    print(f"✅ OK: ${total_actual:,.0f}")
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                errores.append({
                    'cufe': cufe_corto,
                    'error': str(e)
                })
        
        # Resumen
        print(f"\n{'='*80}")
        print(f"📊 RESUMEN DEL ANÁLISIS")
        print(f"{'='*80}")
        print(f"   Total analizadas:        {total_facturas}")
        print(f"   ✅ Sin cambios:          {sin_cambios}")
        print(f"   ⚠️ Con diferencias:      {len(diferencias)}")
        print(f"   ❌ Errores:              {len(errores)}")
        print(f"{'='*80}")
        
        if diferencias:
            print(f"\n⚠️ FACTURAS CON DIFERENCIAS EN EL TOTAL:")
            print(f"{'─'*80}")
            print(f"{'CUFE':<18} {'Número':<15} {'Actual':>15} {'Nuevo':>15} {'Diferencia':>15}")
            print(f"{'─'*80}")
            
            for diff in diferencias:
                print(f"{diff['cufe']:<18} {diff['numero']:<15} ${diff['actual']:>13,.0f} ${diff['nuevo']:>13,.0f} ${diff['diferencia']:>13,.0f}")
            
            print(f"{'─'*80}")
            
            # Guardar reporte detallado
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            reporte_file = f"reporte_diferencias_totales_{timestamp}.txt"
            
            with open(reporte_file, 'w', encoding='utf-8') as f:
                f.write(f"REPORTE DE DIFERENCIAS EN TOTALES\n")
                f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*80}\n\n")
                
                for diff in diferencias:
                    f.write(f"CUFE: {diff['cufe_completo']}\n")
                    f.write(f"Número: {diff['numero']}\n")
                    f.write(f"Emisor: {diff['emisor']}\n")
                    f.write(f"Total Actual: ${diff['actual']:,.2f}\n")
                    f.write(f"Total Nuevo:  ${diff['nuevo']:,.2f}\n")
                    f.write(f"Diferencia:   ${diff['diferencia']:,.2f}\n")
                    f.write(f"{'-'*80}\n\n")
            
            print(f"\n📄 Reporte detallado guardado en: {reporte_file}")
        
        if errores:
            print(f"\n❌ ERRORES ENCONTRADOS:")
            print(f"{'─'*80}")
            for error in errores:
                print(f"   CUFE: {error['cufe']} - Error: {error['error']}")
            print(f"{'─'*80}")
        
        print(f"\n✅ Análisis completado")
        
        if diferencias:
            print(f"\n💡 SIGUIENTE PASO:")
            print(f"   Para aplicar los cambios, ejecuta:")
            print(f"   python CODE/reprocesar_archivos_dian_s3.py")
        
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    analizar_totales()
