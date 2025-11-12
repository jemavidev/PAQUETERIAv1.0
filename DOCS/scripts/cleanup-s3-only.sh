#!/bin/bash
# -*- coding: utf-8 -*-
# PAQUETES EL CLUB v4.0 - Limpieza Solo S3
# Versión: 1.0.0
# Fecha: 2025-01-24

echo "🧹 PAQUETES EL CLUB v4.0 - Limpieza Solo S3"
echo "============================================="

# Verificar archivo de entorno
if [ ! -f "CODE/LOCAL/.env" ]; then
    echo "❌ Error: Archivo CODE/LOCAL/.env no encontrado"
    echo "💡 Asegúrate de estar en la raíz del proyecto"
    exit 1
fi

# Cargar variables de entorno
if [ -f "CODE/LOCAL/.env" ]; then
    source CODE/LOCAL/.env
    echo "✅ Variables de entorno cargadas desde CODE/LOCAL/.env"
else
    echo "❌ Error: Archivo CODE/LOCAL/.env no encontrado"
    exit 1
fi

# Verificar variables AWS requeridas
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ] || [ -z "$AWS_S3_BUCKET" ]; then
    echo "❌ Error: Variables de entorno AWS no configuradas"
    echo "💡 Configura AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY y AWS_S3_BUCKET en CODE/LOCAL/.env"
    exit 1
fi

# Ejecutar limpieza solo de S3
echo "📁 Ejecutando limpieza solo de S3..."
python3 -c "
import boto3
import os

# Cargar variables de entorno
with open('CODE/LOCAL/.env', 'r') as f:
    for line in f:
        if line.strip() and not line.startswith('#'):
            if '=' in line:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value.strip('\"')

# Crear cliente S3
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION', 'us-east-1')
)

bucket_name = os.getenv('AWS_S3_BUCKET')
prefix = 'paquetes-recibidos-imagenes/'

print(f'🔍 Buscando archivos en: s3://{bucket_name}/{prefix}')

try:
    # Listar todos los archivos
    response = s3_client.list_objects_v2(
        Bucket=bucket_name,
        Prefix=prefix
    )
    
    if 'Contents' in response:
        files = [obj['Key'] for obj in response['Contents'] if not obj['Key'].endswith('/')]
        print(f'📊 Encontrados {len(files)} archivos para eliminar')
        
        if len(files) > 0:
            print('\\n⚠️  ADVERTENCIA: Se eliminarán TODOS los archivos S3')
            print('Esta acción NO SE PUEDE DESHACER')
            confirm = input('\\n¿Continuar? (escribe SI para confirmar): ').strip()
            
            if confirm == 'SI':
                deleted = 0
                errors = 0
                
                for file_key in files:
                    try:
                        s3_client.delete_object(Bucket=bucket_name, Key=file_key)
                        deleted += 1
                        print(f'✅ Eliminado: {file_key}')
                    except Exception as e:
                        errors += 1
                        print(f'❌ Error eliminando {file_key}: {e}')
                
                print(f'\\n📊 RESUMEN:')
                print(f'✅ Archivos eliminados: {deleted}')
                print(f'❌ Errores: {errors}')
                
                if errors == 0:
                    print('🎉 Limpieza S3 completada exitosamente!')
                else:
                    print('⚠️ Limpieza S3 completada con errores')
            else:
                print('❌ Operación cancelada')
        else:
            print('✅ No hay archivos para eliminar')
    else:
        print('📁 No hay archivos en el bucket')
        
except Exception as e:
    print(f'❌ Error: {e}')
"

echo "✅ Script de limpieza S3 completado"
