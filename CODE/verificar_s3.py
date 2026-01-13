#!/usr/bin/env python3
"""
Script para verificar la configuración y estado de AWS S3
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.s3_storage_service import S3StorageService

def main():
    print("=" * 60)
    print("VERIFICACIÓN DE AWS S3")
    print("=" * 60)
    print()
    
    # Verificar variables de entorno
    print("📋 Variables de entorno:")
    print(f"  AWS_S3_ENABLED: {os.getenv('AWS_S3_ENABLED', 'no configurado')}")
    print(f"  AWS_ACCESS_KEY_ID: {'✓ configurado' if os.getenv('AWS_ACCESS_KEY_ID') else '✗ no configurado'}")
    print(f"  AWS_SECRET_ACCESS_KEY: {'✓ configurado' if os.getenv('AWS_SECRET_ACCESS_KEY') else '✗ no configurado'}")
    print(f"  AWS_S3_BUCKET_NAME: {os.getenv('AWS_S3_BUCKET_NAME', 'no configurado')}")
    print(f"  AWS_REGION: {os.getenv('AWS_REGION', 'no configurado')}")
    print(f"  AWS_S3_PREFIX: {os.getenv('AWS_S3_PREFIX', 'no configurado')}")
    print()
    
    # Inicializar servicio
    s3_service = S3StorageService()
    
    if not s3_service.is_enabled():
        print("✗ AWS S3 NO está habilitado")
        print()
        print("Para habilitar S3, configura las siguientes variables:")
        print("  AWS_S3_ENABLED=true")
        print("  AWS_ACCESS_KEY_ID=tu_access_key")
        print("  AWS_SECRET_ACCESS_KEY=tu_secret_key")
        print("  AWS_S3_BUCKET_NAME=nombre_del_bucket")
        print("  AWS_REGION=us-east-1")
        print("  AWS_S3_PREFIX=invoices/")
        return
    
    print("✓ AWS S3 está habilitado")
    print()
    
    # Obtener estadísticas
    print("📊 Estadísticas de almacenamiento:")
    stats = s3_service.get_storage_stats()
    
    if 'error' in stats:
        print(f"  ✗ Error: {stats['error']}")
        return
    
    print(f"  Bucket: {stats['bucket']}")
    print(f"  Región: {stats['region']}")
    print(f"  Prefijo: {stats['prefix']}")
    print(f"  Total de archivos: {stats['total_files']}")
    print(f"  Tamaño total: {stats['total_size_mb']} MB ({stats['total_size_bytes']:,} bytes)")
    print()
    
    # Listar algunos archivos
    if stats['total_files'] > 0:
        print("📄 Últimos archivos (máximo 10):")
        files = s3_service.list_pdfs(max_keys=10)
        for file in files[:10]:
            print(f"  - {file['file_hash']}.pdf")
            print(f"    Tamaño: {file['size']:,} bytes")
            print(f"    Modificado: {file['last_modified']}")
        
        if stats['total_files'] > 10:
            print(f"  ... y {stats['total_files'] - 10} archivos más")
    else:
        print("📄 No hay archivos en S3")
    
    print()
    print("=" * 60)
    print("✅ Verificación completada")
    print("=" * 60)
    print()

if __name__ == "__main__":
    main()
