#!/usr/bin/env python3
"""
Script para re-calcular la calidad de extracción de facturas existentes
"""

import sys
import os
sys.path.insert(0, '/app/src')

from app.database import SessionLocal
from app.models.invoice import SupplierInvoice
from app.services.supplier_invoice_service import SupplierInvoiceService
from app.services.s3_storage_service import S3StorageService
import tempfile

def recalcular_calidad():
    """Re-calcula la calidad de todas las facturas existentes"""
    print("=" * 70)
    print("🔄 RE-CALCULANDO CALIDAD DE FACTURAS EXISTENTES")
    print("=" * 70)
    
    db = SessionLocal()
    service = SupplierInvoiceService(db)
    s3_service = S3StorageService()
    
    try:
        # Obtener todas las facturas con calidad 0 o NULL
        facturas = db.query(SupplierInvoice).filter(
            (SupplierInvoice.extraction_quality == 0.0) | 
            (SupplierInvoice.extraction_quality == None)
        ).all()
        
        total = len(facturas)
        print(f"\n📊 Total de facturas a procesar: {total}\n")
        
        if total == 0:
            print("✅ No hay facturas pendientes de procesar")
            return
        
        actualizadas = 0
        errores = 0
        
        for i, factura in enumerate(facturas, 1):
            print(f"[{i}/{total}] Procesando factura ID {factura.id}: {factura.original_filename}")
            
            try:
                # Obtener PDF
                pdf_content = None
                
                # Intentar desde S3
                if s3_service.is_enabled() and factura.original_file_hash:
                    try:
                        pdf_content = s3_service.download_pdf(
                            factura.original_file_hash, 
                            prefix="supplier-invoices"
                        )
                        print(f"  ✓ PDF descargado desde S3")
                    except Exception as e:
                        print(f"  ⚠️  Error descargando desde S3: {e}")
                
                # Fallback a local
                if not pdf_content:
                    local_paths = [
                        f"/app/src/uploads/supplier-invoices/{factura.original_file_hash}.pdf",
                        f"/app/src/uploads/invoices/{factura.original_file_hash}.pdf",
                    ]
                    
                    for path in local_paths:
                        if os.path.exists(path):
                            with open(path, 'rb') as f:
                                pdf_content = f.read()
                            print(f"  ✓ PDF encontrado localmente")
                            break
                
                if not pdf_content:
                    print(f"  ❌ PDF no encontrado")
                    errores += 1
                    continue
                
                # Guardar temporalmente
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                    tmp.write(pdf_content)
                    tmp_path = tmp.name
                
                try:
                    # Re-extraer con extractor mejorado
                    enhanced_data = service.enhanced_extractor.extract_from_pdf(tmp_path)
                    
                    # Actualizar calidad
                    factura.extraction_quality = enhanced_data.overall_quality
                    
                    # Opcionalmente actualizar datos si están vacíos
                    if not factura.supplier_name and enhanced_data.supplier_name.value:
                        factura.supplier_name = enhanced_data.supplier_name.value
                    if not factura.supplier_nit and enhanced_data.supplier_nit.value:
                        factura.supplier_nit = enhanced_data.supplier_nit.value
                    if not factura.invoice_number and enhanced_data.invoice_number.value:
                        factura.invoice_number = enhanced_data.invoice_number.value
                    if not factura.invoice_date and enhanced_data.invoice_date.value:
                        factura.invoice_date = enhanced_data.invoice_date.value
                    if not factura.total_amount and enhanced_data.total_amount.value:
                        factura.total_amount = enhanced_data.total_amount.value
                    
                    db.commit()
                    
                    quality_pct = int(enhanced_data.overall_quality * 100)
                    print(f"  ✅ Calidad actualizada: {quality_pct}%")
                    actualizadas += 1
                    
                finally:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                errores += 1
                continue
        
        print("\n" + "=" * 70)
        print("📊 RESUMEN")
        print("=" * 70)
        print(f"  Total procesadas: {total}")
        print(f"  ✅ Actualizadas: {actualizadas}")
        print(f"  ❌ Errores: {errores}")
        print("=" * 70)
        
    finally:
        db.close()

if __name__ == "__main__":
    recalcular_calidad()
