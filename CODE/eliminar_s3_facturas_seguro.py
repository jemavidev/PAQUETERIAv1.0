#!/usr/bin/env python3
"""
Script para eliminar TODOS los archivos de facturas en S3
Lee credenciales de forma segura desde .env
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import boto3
from botocore.exceptions import ClientError
from app.config import settings

def eliminar_archivos_s3():
    """
    Elimina todos los archivos de facturas en S3
    """
    print("\n" + "="*80)
    print("🗑️  ELIMINACIÓN COMPLETA DE ARCHIVOS DE FACTURAS EN S3")
    print("="*80)
    
    try:
        # Crear cliente S3 usando configuración segura
        print("\n🔄 Conectando a S3...")
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )
        print(f"✅ Conectado a bucket: {settings.aws_s3_bucket}")
        
        # Buscar TODOS los archivos que empiecen con "invoices/"
        prefix = "invoices/"
        
        print(f"\n🔍 Buscando todos los archivos en: {prefix}")
        
        # Listar todos los objetos con paginación
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=settings.aws_s3_bucket, Prefix=prefix)
        
        archivos_a_eliminar = []
        for page in pages:
            if 'Contents' in page:
                archivos_a_eliminar.extend(page['Contents'])
        
        if not archivos_a_eliminar:
            print(f"  ℹ️  No hay archivos de facturas en S3")
            return 0
        
        total_archivos = len(archivos_a_eliminar)
        print(f"  📊 Encontrados {total_archivos} archivos")
        
        # Calcular tamaño total
        total_size = sum(obj['Size'] for obj in archivos_a_eliminar)
        total_size_mb = total_size / (1024 * 1024)
        print(f"  📏 Tamaño total: {total_size_mb:.2f} MB")
        
        # Eliminar archivos
        archivos_eliminados = 0
        archivos_fallidos = 0
        
        print(f"\n🗑️  Eliminando {total_archivos} archivos...")
        
        for i, obj in enumerate(archivos_a_eliminar, 1):
            key = obj['Key']
            size = obj['Size']
            
            try:
                # Mostrar progreso cada 10 archivos
                if i % 10 == 0 or i == 1 or i == total_archivos:
                    print(f"  [{i}/{total_archivos}] Eliminando: {key[:80]}...")
                
                s3_client.delete_object(Bucket=settings.aws_s3_bucket, Key=key)
                archivos_eliminados += 1
                
            except ClientError as e:
                archivos_fallidos += 1
                print(f"    ✗ Error eliminando {key}: {e}")
        
        # Resumen
        print("\n" + "="*80)
        print("✅ ELIMINACIÓN DE S3 COMPLETADA")
        print("="*80)
        print(f"\n📊 Resumen:")
        print(f"  • Archivos encontrados: {total_archivos}")
        print(f"  • Archivos eliminados: {archivos_eliminados}")
        print(f"  • Tamaño liberado: {total_size_mb:.2f} MB")
        
        if archivos_fallidos > 0:
            print(f"  • Archivos fallidos: {archivos_fallidos}")
        
        if archivos_eliminados == total_archivos:
            print("\n✅ Todos los archivos de facturas fueron eliminados de S3")
        else:
            print(f"\n⚠️  {archivos_fallidos} archivos no pudieron ser eliminados")
        
        # Verificar que no queden archivos
        print("\n🔍 Verificando eliminación...")
        response = s3_client.list_objects_v2(
            Bucket=settings.aws_s3_bucket,
            Prefix=prefix,
            MaxKeys=1
        )
        
        if 'Contents' not in response:
            print("✅ Verificado: No quedan archivos de facturas en S3")
        else:
            remaining = len(response.get('Contents', []))
            print(f"⚠️  Aún quedan {remaining} archivos en S3")
        
    except ClientError as e:
        print(f"\n❌ Error de S3: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(eliminar_archivos_s3())
