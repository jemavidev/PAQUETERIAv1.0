#!/usr/bin/env python3
"""
Script para migrar PDFs existentes desde almacenamiento local a AWS S3
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.s3_storage_service import S3StorageService
from app.database import SessionLocal
from app.models.invoice import Invoice

def main():
    print("=" * 60)
    print("MIGRACIÓN DE PDFs A AWS S3")
    print("=" * 60)
    print()
    
    # Inicializar servicio S3
    s3_service = S3StorageService()
    
    if not s3_service.is_enabled():
        print("✗ AWS S3 no está habilitado")
        print("  Verifica las variables de entorno:")
        print("  - AWS_S3_ENABLED=true")
        print("  - AWS_ACCESS_KEY_ID")
        print("  - AWS_SECRET_ACCESS_KEY")
        print("  - AWS_S3_BUCKET_NAME")
        return
    
    print(f"✓ S3 habilitado")
    print(f"  Bucket: {s3_service.bucket_name}")
    print(f"  Región: {s3_service.region}")
    print(f"  Prefijo: {s3_service.prefix}")
    print()
    
    # Directorio local de PDFs
    local_directory = "/app/src/uploads/invoices"
    
    if not os.path.exists(local_directory):
        local_directory = str(Path(__file__).parent / "src" / "uploads" / "invoices")
    
    if not os.path.exists(local_directory):
        print(f"✗ Directorio local no existe: {local_directory}")
        return
    
    print(f"📁 Directorio local: {local_directory}")
    print()
    
    # Contar archivos
    pdf_files = [f for f in os.listdir(local_directory) if f.endswith('.pdf')]
    total_files = len(pdf_files)
    
    if total_files == 0:
        print("✓ No hay archivos PDF para migrar")
        return
    
    print(f"📊 Archivos encontrados: {total_files}")
    print()
    
    respuesta = input("¿Deseas continuar con la migración? (escribe 'SI' para confirmar): ")
    
    if respuesta.strip().upper() != 'SI':
        print("\n✗ Migración cancelada")
        return
    
    print("\n🚀 Iniciando migración...\n")
    
    # Obtener metadata de facturas desde la base de datos
    db = SessionLocal()
    invoices_by_hash = {}
    
    try:
        invoices = db.query(Invoice).all()
        for invoice in invoices:
            if invoice.file_hash:
                invoices_by_hash[invoice.file_hash] = {
                    'numero_documento': invoice.numero_documento,
                    'supplier_nit': invoice.supplier.nit if invoice.supplier else 'unknown',
                    'fecha_emision': invoice.fecha_emision.isoformat() if invoice.fecha_emision else None,
                    'document_type': invoice.document_type.value if invoice.document_type else 'unknown'
                }
    finally:
        db.close()
    
    # Migrar archivos
    results = {
        'success': 0,
        'failed': 0,
        'skipped': 0,
        'errors': []
    }
    
    for i, filename in enumerate(pdf_files, 1):
        file_hash = filename.replace('.pdf', '')
        local_path = os.path.join(local_directory, filename)
        
        print(f"[{i}/{total_files}] Procesando: {filename}")
        
        # Verificar si ya existe en S3
        if s3_service.exists(file_hash):
            results['skipped'] += 1
            print(f"  ⊙ Ya existe en S3, omitiendo")
            continue
        
        # Leer archivo
        try:
            with open(local_path, 'rb') as f:
                content = f.read()
            
            # Obtener metadata si existe
            metadata = invoices_by_hash.get(file_hash, {})
            
            # Subir a S3
            if s3_service.upload_pdf(content, file_hash, metadata):
                results['success'] += 1
                print(f"  ✓ Subido exitosamente")
            else:
                results['failed'] += 1
                results['errors'].append(f"Error subiendo {filename}")
                print(f"  ✗ Error subiendo")
                
        except Exception as e:
            results['failed'] += 1
            results['errors'].append(f"Error procesando {filename}: {str(e)}")
            print(f"  ✗ Error: {e}")
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE MIGRACIÓN")
    print("=" * 60)
    print(f"Total de archivos: {total_files}")
    print(f"Subidos exitosamente: {results['success']}")
    print(f"Omitidos (ya existían): {results['skipped']}")
    print(f"Fallidos: {results['failed']}")
    
    if results['errors']:
        print("\nErrores:")
        for error in results['errors'][:10]:  # Mostrar solo los primeros 10
            print(f"  - {error}")
        if len(results['errors']) > 10:
            print(f"  ... y {len(results['errors']) - 10} errores más")
    
    print("=" * 60)
    
    if results['failed'] == 0:
        print("\n✅ Migración completada exitosamente")
        print("\n⚠️  IMPORTANTE:")
        print("   - Los archivos locales NO fueron eliminados")
        print("   - Puedes eliminarlos manualmente después de verificar")
        print("   - O mantenerlos como backup local")
    else:
        print("\n⚠️  Migración completada con errores")
        print("   Revisa los errores antes de eliminar archivos locales")
    
    print()

if __name__ == "__main__":
    main()
