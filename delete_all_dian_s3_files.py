#!/usr/bin/env python3
"""
Script para eliminar TODOS los archivos DIAN de S3
ADVERTENCIA: Esto eliminará todos los archivos en invoices/dian/
"""
import sys
import os
import boto3
from botocore.exceptions import ClientError

def delete_all_dian_files():
    """
    Elimina TODOS los archivos DIAN de S3
    """
    print(f"\n{'='*80}")
    print(f"🗑️  ELIMINAR TODOS LOS ARCHIVOS DIAN DE S3")
    print(f"{'='*80}\n")
    
    bucket_name = os.getenv('AWS_S3_BUCKET_NAME', 'elclub-paqueteria')
    prefix = 'invoices/dian/'
    
    print(f"📦 Bucket: {bucket_name}")
    print(f"📁 Prefix: {prefix}\n")
    
    try:
        # Configurar cliente S3
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        
        # Listar todos los archivos
        print("🔍 Listando archivos DIAN en S3...")
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
        
        files_to_delete = []
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    files_to_delete.append({'Key': obj['Key']})
        
        total_files = len(files_to_delete)
        print(f"   Encontrados: {total_files} archivos\n")
        
        if total_files == 0:
            print("✅ No hay archivos DIAN en S3")
            return
        
        # Mostrar algunos archivos
        print(f"{'─'*80}")
        print(f"📋 ARCHIVOS A ELIMINAR (primeros 10):")
        print(f"{'─'*80}")
        for i, file in enumerate(files_to_delete[:10], 1):
            filename = file['Key'].split('/')[-1]
            cufe_short = filename.replace('.pdf', '')[:16]
            print(f"   {i}. {cufe_short}... ({file['Key']})")
        
        if total_files > 10:
            print(f"   ... y {total_files - 10} más")
        print(f"{'─'*80}\n")
        
        # Confirmar eliminación
        print(f"⚠️  ADVERTENCIA CRÍTICA:")
        print(f"   Se eliminarán TODOS los {total_files} archivos DIAN de S3")
        print(f"   Esta acción NO se puede deshacer")
        print(f"   Los archivos se perderán permanentemente\n")
        
        respuesta = input(f"¿Estás ABSOLUTAMENTE SEGURO? Escribe 'ELIMINAR TODO' para confirmar: ")
        
        if respuesta != 'ELIMINAR TODO':
            print(f"\n❌ Operación cancelada")
            return
        
        # Eliminar archivos en lotes de 1000 (límite de AWS)
        print(f"\n{'─'*80}")
        print(f"🗑️  ELIMINANDO ARCHIVOS...")
        print(f"{'─'*80}\n")
        
        deleted = 0
        failed = 0
        batch_size = 1000
        
        for i in range(0, len(files_to_delete), batch_size):
            batch = files_to_delete[i:i + batch_size]
            
            try:
                response = s3_client.delete_objects(
                    Bucket=bucket_name,
                    Delete={'Objects': batch}
                )
                
                # Contar eliminados
                if 'Deleted' in response:
                    batch_deleted = len(response['Deleted'])
                    deleted += batch_deleted
                    print(f"   Lote {i//batch_size + 1}: {batch_deleted} archivos eliminados")
                
                # Contar errores
                if 'Errors' in response:
                    batch_failed = len(response['Errors'])
                    failed += batch_failed
                    print(f"   Lote {i//batch_size + 1}: {batch_failed} errores")
                    
            except ClientError as e:
                print(f"   ❌ Error en lote {i//batch_size + 1}: {str(e)[:50]}")
                failed += len(batch)
        
        # Resumen final
        print(f"\n{'='*80}")
        print(f"📊 RESUMEN DE LA ELIMINACIÓN")
        print(f"{'='*80}")
        print(f"   Total archivos:    {total_files}")
        print(f"   ✅ Eliminados:     {deleted}")
        print(f"   ❌ Fallidos:       {failed}")
        print(f"{'='*80}")
        
        if deleted > 0:
            print(f"\n✅ Eliminación completada")
            print(f"   {deleted} archivos DIAN eliminados de S3")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    delete_all_dian_files()
