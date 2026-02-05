#!/usr/bin/env python3
"""
Script para limpiar archivos huérfanos en S3
Elimina archivos DIAN que ya no tienen registro en la base de datos
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'CODE/src'))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.invoice_v2 import InvoiceV2
from app.services.s3_service import S3Service
import boto3
from botocore.exceptions import ClientError

def cleanup_orphaned_dian_files():
    """
    Limpia archivos DIAN huérfanos en S3
    """
    print(f"\n{'='*80}")
    print(f"🧹 LIMPIEZA DE ARCHIVOS DIAN HUÉRFANOS EN S3")
    print(f"{'='*80}\n")
    
    # Inicializar servicios
    db = SessionLocal()
    s3_service = S3Service()
    
    # Configurar cliente S3 directo para listar archivos
    bucket_name = os.getenv('AWS_S3_BUCKET_NAME', 'elclub-paqueteria')
    
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        
        print(f"📦 Bucket: {bucket_name}")
        print(f"📁 Prefix: invoices/dian/\n")
        
        # Listar todos los archivos DIAN en S3
        print("🔍 Listando archivos DIAN en S3...")
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_name, Prefix='invoices/dian/')
        
        s3_files = []
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    s3_files.append(obj['Key'])
        
        print(f"   Encontrados: {len(s3_files)} archivos en S3\n")
        
        if len(s3_files) == 0:
            print("✅ No hay archivos DIAN en S3")
            return
        
        # Obtener todos los CUFEs de la base de datos
        print("🔍 Obteniendo CUFEs de la base de datos...")
        invoices = db.query(InvoiceV2).all()
        db_cufes = set(invoice.cufe for invoice in invoices)
        print(f"   Encontrados: {len(db_cufes)} registros en BD\n")
        
        # Identificar archivos huérfanos
        print("🔍 Identificando archivos huérfanos...")
        orphaned_files = []
        
        for s3_key in s3_files:
            # Extraer CUFE del nombre del archivo
            # Formato: invoices/dian/CUFE.pdf
            filename = s3_key.split('/')[-1]
            cufe = filename.replace('.pdf', '')
            
            # Verificar si el CUFE existe en la BD
            if cufe not in db_cufes:
                orphaned_files.append({
                    'key': s3_key,
                    'cufe': cufe[:16] + '...',
                    'size': 0  # Podríamos obtener el tamaño si es necesario
                })
        
        print(f"   Archivos huérfanos: {len(orphaned_files)}\n")
        
        if len(orphaned_files) == 0:
            print("✅ No hay archivos huérfanos en S3")
            return
        
        # Mostrar archivos huérfanos
        print(f"{'─'*80}")
        print(f"📋 ARCHIVOS HUÉRFANOS ENCONTRADOS:")
        print(f"{'─'*80}")
        for i, file in enumerate(orphaned_files[:10], 1):
            print(f"   {i}. CUFE: {file['cufe']}")
            print(f"      S3 Key: {file['key']}")
        
        if len(orphaned_files) > 10:
            print(f"   ... y {len(orphaned_files) - 10} más")
        print(f"{'─'*80}\n")
        
        # Confirmar eliminación
        print(f"⚠️  ADVERTENCIA: Se eliminarán {len(orphaned_files)} archivos de S3")
        print(f"   Estos archivos no tienen registro en la base de datos")
        respuesta = input(f"\n¿Deseas continuar? (si/no): ")
        
        if respuesta.lower() not in ['si', 's', 'yes', 'y']:
            print(f"\n❌ Operación cancelada por el usuario")
            return
        
        # Eliminar archivos huérfanos
        print(f"\n{'─'*80}")
        print(f"🗑️  ELIMINANDO ARCHIVOS HUÉRFANOS...")
        print(f"{'─'*80}\n")
        
        deleted = 0
        failed = 0
        
        for i, file in enumerate(orphaned_files, 1):
            cufe_short = file['cufe']
            s3_key = file['key']
            
            print(f"[{i}/{len(orphaned_files)}] {cufe_short}... ", end='', flush=True)
            
            try:
                # Eliminar archivo de S3
                s3_client.delete_object(Bucket=bucket_name, Key=s3_key)
                print(f"✅ Eliminado")
                deleted += 1
            except ClientError as e:
                print(f"❌ Error: {str(e)[:50]}")
                failed += 1
        
        # Resumen final
        print(f"\n{'='*80}")
        print(f"📊 RESUMEN DE LA LIMPIEZA")
        print(f"{'='*80}")
        print(f"   Total archivos en S3:     {len(s3_files)}")
        print(f"   Archivos huérfanos:       {len(orphaned_files)}")
        print(f"   ✅ Eliminados:            {deleted}")
        print(f"   ❌ Fallidos:              {failed}")
        print(f"{'='*80}")
        
        if deleted > 0:
            print(f"\n✅ Limpieza completada exitosamente")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    cleanup_orphaned_dian_files()
