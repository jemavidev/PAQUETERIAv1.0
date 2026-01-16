#!/usr/bin/env python3
"""
Script para verificar el estado de una supplier_invoice
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.database import SessionLocal
from app.models.invoice import SupplierInvoice

def verificar_invoice(invoice_id: int):
    db = SessionLocal()
    
    try:
        invoice = db.query(SupplierInvoice).filter(SupplierInvoice.id == invoice_id).first()
        
        if not invoice:
            print(f"❌ No se encontró supplier_invoice con ID {invoice_id}")
            return
        
        print("\n" + "=" * 70)
        print(f"SUPPLIER INVOICE #{invoice_id}")
        print("=" * 70)
        
        print(f"\n📄 Archivo:")
        print(f"  Nombre: {invoice.original_filename}")
        print(f"  Hash: {invoice.original_file_hash}")
        print(f"  Path S3: {invoice.original_file_path or 'NO GUARDADO'}")
        
        print(f"\n📊 Datos:")
        print(f"  Proveedor: {invoice.supplier_name or 'N/A'}")
        print(f"  NIT: {invoice.supplier_nit or 'N/A'}")
        print(f"  Número: {invoice.invoice_number or 'N/A'}")
        print(f"  Fecha: {invoice.invoice_date or 'N/A'}")
        
        print(f"\n🔑 CUFE:")
        print(f"  CUFE: {invoice.cufe or 'NO EXTRAÍDO'}")
        print(f"  Fuente: {invoice.cufe_source or 'N/A'}")
        
        print(f"\n📈 Estado:")
        print(f"  Status: {invoice.status.value}")
        print(f"  Mensaje: {invoice.status_message or 'N/A'}")
        
        print(f"\n🔗 Procesamiento:")
        print(f"  Factura procesada ID: {invoice.processed_invoice_id or 'NO PROCESADA'}")
        print(f"  Procesada en: {invoice.processed_at or 'N/A'}")
        
        print(f"\n📅 Fechas:")
        print(f"  Subida: {invoice.uploaded_at}")
        print(f"  Actualizada: {invoice.updated_at}")
        
        # Verificar si el archivo existe en S3
        print(f"\n🔍 Verificación de archivo:")
        
        if invoice.original_file_hash:
            from app.services.s3_storage_service import S3StorageService
            s3 = S3StorageService()
            
            if s3.is_enabled():
                print(f"  S3 habilitado: ✅")
                
                # Intentar generar URL
                if invoice.original_file_path:
                    url = s3.generate_presigned_url(invoice.original_file_path, expiration=60, is_full_key=True)
                    if url:
                        print(f"  URL firmada (usando path): ✅")
                        print(f"  URL: {url[:100]}...")
                    else:
                        print(f"  URL firmada (usando path): ❌")
                
                # Intentar con construcción manual
                url2 = s3.generate_presigned_url(f"supplier-invoices/{invoice.original_file_hash}.pdf", expiration=60, is_full_key=True)
                if url2:
                    print(f"  URL firmada (construida): ✅")
                    print(f"  URL: {url2[:100]}...")
                else:
                    print(f"  URL firmada (construida): ❌")
                
                # Intentar descarga directa
                content = s3.download_pdf(invoice.original_file_hash, prefix="supplier-invoices")
                if content:
                    print(f"  Descarga directa S3: ✅ ({len(content):,} bytes)")
                else:
                    print(f"  Descarga directa S3: ❌")
            else:
                print(f"  S3 habilitado: ❌")
            
            # Verificar local
            local_paths = [
                f"/app/src/uploads/supplier-invoices/{invoice.original_file_hash}.pdf",
                f"/app/src/uploads/invoices/{invoice.original_file_hash}.pdf",
            ]
            
            for path in local_paths:
                if os.path.exists(path):
                    size = os.path.getsize(path)
                    print(f"  Archivo local: ✅ {path} ({size:,} bytes)")
                else:
                    print(f"  Archivo local: ❌ {path}")
        else:
            print(f"  ❌ No hay hash de archivo")
        
        print("\n" + "=" * 70)
        
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python verificar_supplier_invoice.py <invoice_id>")
        sys.exit(1)
    
    invoice_id = int(sys.argv[1])
    verificar_invoice(invoice_id)
