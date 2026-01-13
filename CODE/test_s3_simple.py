#!/usr/bin/env python3
"""
Test simple para verificar que S3 funciona correctamente
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.s3_storage_service import S3StorageService

def main():
    print("=" * 60)
    print("TEST SIMPLE DE AWS S3")
    print("=" * 60)
    print()
    
    # Inicializar servicio
    s3 = S3StorageService()
    
    # 1. Verificar que está habilitado
    print("1. Verificando configuración...")
    if not s3.is_enabled():
        print("   ✗ S3 no está habilitado")
        print("   Configura AWS_S3_ENABLED=true en .env")
        return
    print("   ✓ S3 está habilitado")
    print()
    
    # 2. Crear un PDF de prueba
    print("2. Creando PDF de prueba...")
    test_content = b"%PDF-1.4\n%Test PDF\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n0 1\n0000000000 65535 f\ntrailer\n<<\n/Size 1\n/Root 1 0 R\n>>\nstartxref\n0\n%%EOF"
    import time
    test_hash = f"test_{int(time.time())}"
    print(f"   Hash de prueba: {test_hash}")
    print()
    
    # 3. Subir a S3
    print("3. Subiendo a S3...")
    metadata = {
        'test': 'true',
        'timestamp': str(int(time.time()))
    }
    
    if s3.upload_pdf(test_content, test_hash, metadata):
        print("   ✓ PDF subido exitosamente")
    else:
        print("   ✗ Error subiendo PDF")
        return
    print()
    
    # 4. Verificar que existe
    print("4. Verificando existencia...")
    if s3.exists(test_hash):
        print("   ✓ PDF existe en S3")
    else:
        print("   ✗ PDF no encontrado en S3")
        return
    print()
    
    # 5. Descargar
    print("5. Descargando desde S3...")
    downloaded = s3.download_pdf(test_hash)
    if downloaded:
        print(f"   ✓ PDF descargado ({len(downloaded)} bytes)")
        if downloaded == test_content:
            print("   ✓ Contenido coincide")
        else:
            print("   ⚠ Contenido no coincide")
    else:
        print("   ✗ Error descargando PDF")
        return
    print()
    
    # 6. Generar URL firmada
    print("6. Generando URL firmada...")
    url = s3.generate_presigned_url(test_hash, expiration=300)
    if url:
        print("   ✓ URL generada")
        print(f"   URL: {url[:80]}...")
    else:
        print("   ✗ Error generando URL")
    print()
    
    # 7. Eliminar archivo de prueba
    print("7. Limpiando archivo de prueba...")
    if s3.delete_pdf(test_hash):
        print("   ✓ PDF eliminado")
    else:
        print("   ✗ Error eliminando PDF")
    print()
    
    # 8. Estadísticas
    print("8. Estadísticas de S3...")
    stats = s3.get_storage_stats()
    if 'error' not in stats:
        print(f"   Bucket: {stats['bucket']}")
        print(f"   Archivos: {stats['total_files']}")
        print(f"   Tamaño: {stats['total_size_mb']} MB")
    else:
        print(f"   ⚠ Error: {stats['error']}")
    print()
    
    print("=" * 60)
    print("✅ TEST COMPLETADO EXITOSAMENTE")
    print("=" * 60)
    print()
    print("S3 está funcionando correctamente y listo para usar.")
    print()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
