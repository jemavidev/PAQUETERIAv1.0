"""
Servicio de almacenamiento en AWS S3 para PDFs de facturas
"""

import os
import logging
from typing import Optional, BinaryIO
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)


class S3StorageService:
    """Servicio para gestionar almacenamiento de PDFs en AWS S3"""
    
    def __init__(self):
        """Inicializa el cliente de S3"""
        self.bucket_name = os.getenv('AWS_S3_BUCKET_NAME', 'paquetex-invoices')
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        self.prefix = os.getenv('AWS_S3_PREFIX', 'invoices/')  # Carpeta dentro del bucket
        
        # Inicializar cliente S3
        try:
            self.s3_client = boto3.client(
                's3',
                region_name=self.region,
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            logger.info(f"Cliente S3 inicializado - Bucket: {self.bucket_name}")
        except NoCredentialsError:
            logger.error("Credenciales de AWS no configuradas")
            self.s3_client = None
    
    def is_enabled(self) -> bool:
        """Verifica si S3 está habilitado y configurado"""
        return (
            self.s3_client is not None and 
            os.getenv('AWS_S3_ENABLED', 'false').lower() == 'true'
        )
    
    def upload_pdf(
        self, 
        file_content: bytes, 
        file_hash: str,
        metadata: Optional[dict] = None
    ) -> bool:
        """
        Sube un PDF a S3
        
        Args:
            file_content: Contenido del archivo en bytes
            file_hash: Hash SHA256 del archivo (usado como nombre)
            metadata: Metadata adicional (proveedor, fecha, etc)
        
        Returns:
            True si se subió exitosamente, False en caso contrario
        """
        if not self.is_enabled():
            logger.warning("S3 no está habilitado")
            return False
        
        try:
            key = f"{self.prefix}{file_hash}.pdf"
            
            # Preparar metadata
            s3_metadata = {
                'uploaded_at': datetime.now().isoformat(),
                'file_hash': file_hash,
            }
            if metadata:
                s3_metadata.update({k: str(v) for k, v in metadata.items()})
            
            # Subir archivo
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_content,
                ContentType='application/pdf',
                Metadata=s3_metadata,
                ServerSideEncryption='AES256',  # Encriptación en reposo
            )
            
            logger.info(f"PDF subido a S3: {key}")
            return True
            
        except ClientError as e:
            logger.error(f"Error subiendo PDF a S3: {e}")
            return False
    
    def download_pdf(self, file_hash: str) -> Optional[bytes]:
        """
        Descarga un PDF desde S3
        
        Args:
            file_hash: Hash del archivo
        
        Returns:
            Contenido del archivo en bytes, o None si no existe
        """
        if not self.is_enabled():
            return None
        
        try:
            key = f"{self.prefix}{file_hash}.pdf"
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            content = response['Body'].read()
            logger.info(f"PDF descargado desde S3: {key}")
            return content
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.warning(f"PDF no encontrado en S3: {file_hash}")
            else:
                logger.error(f"Error descargando PDF desde S3: {e}")
            return None
    
    def exists(self, file_hash: str) -> bool:
        """
        Verifica si un PDF existe en S3
        
        Args:
            file_hash: Hash del archivo
        
        Returns:
            True si existe, False en caso contrario
        """
        if not self.is_enabled():
            return False
        
        try:
            key = f"{self.prefix}{file_hash}.pdf"
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return True
        except ClientError:
            return False
    
    def delete_pdf(self, file_hash: str) -> bool:
        """
        Elimina un PDF de S3
        
        Args:
            file_hash: Hash del archivo
        
        Returns:
            True si se eliminó exitosamente, False en caso contrario
        """
        if not self.is_enabled():
            return False
        
        try:
            key = f"{self.prefix}{file_hash}.pdf"
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            logger.info(f"PDF eliminado de S3: {key}")
            return True
            
        except ClientError as e:
            logger.error(f"Error eliminando PDF de S3: {e}")
            return False
    
    def generate_presigned_url(
        self, 
        file_hash: str, 
        expiration: int = 3600
    ) -> Optional[str]:
        """
        Genera una URL firmada temporal para descargar un PDF
        
        Args:
            file_hash: Hash del archivo
            expiration: Tiempo de expiración en segundos (default: 1 hora)
        
        Returns:
            URL firmada, o None si hay error
        """
        if not self.is_enabled():
            return None
        
        try:
            key = f"{self.prefix}{file_hash}.pdf"
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key
                },
                ExpiresIn=expiration
            )
            logger.info(f"URL firmada generada para: {key}")
            return url
            
        except ClientError as e:
            logger.error(f"Error generando URL firmada: {e}")
            return None
    
    def list_pdfs(self, prefix: Optional[str] = None, max_keys: int = 1000) -> list:
        """
        Lista PDFs en S3
        
        Args:
            prefix: Prefijo adicional para filtrar
            max_keys: Máximo número de resultados
        
        Returns:
            Lista de diccionarios con información de archivos
        """
        if not self.is_enabled():
            return []
        
        try:
            search_prefix = self.prefix
            if prefix:
                search_prefix = f"{self.prefix}{prefix}"
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=search_prefix,
                MaxKeys=max_keys
            )
            
            if 'Contents' not in response:
                return []
            
            files = []
            for obj in response['Contents']:
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'file_hash': obj['Key'].replace(self.prefix, '').replace('.pdf', '')
                })
            
            return files
            
        except ClientError as e:
            logger.error(f"Error listando PDFs en S3: {e}")
            return []
    
    def get_storage_stats(self) -> dict:
        """
        Obtiene estadísticas de almacenamiento en S3
        
        Returns:
            Diccionario con estadísticas
        """
        if not self.is_enabled():
            return {'enabled': False}
        
        try:
            files = self.list_pdfs()
            total_size = sum(f['size'] for f in files)
            
            return {
                'enabled': True,
                'bucket': self.bucket_name,
                'region': self.region,
                'total_files': len(files),
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'prefix': self.prefix
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {'enabled': True, 'error': str(e)}
    
    def migrate_from_local(self, local_directory: str) -> dict:
        """
        Migra PDFs desde almacenamiento local a S3
        
        Args:
            local_directory: Directorio local con los PDFs
        
        Returns:
            Diccionario con resultados de la migración
        """
        if not self.is_enabled():
            return {'error': 'S3 no está habilitado'}
        
        results = {
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
        
        if not os.path.exists(local_directory):
            return {'error': f'Directorio no existe: {local_directory}'}
        
        for filename in os.listdir(local_directory):
            if not filename.endswith('.pdf'):
                continue
            
            file_hash = filename.replace('.pdf', '')
            local_path = os.path.join(local_directory, filename)
            
            # Verificar si ya existe en S3
            if self.exists(file_hash):
                results['skipped'] += 1
                logger.info(f"PDF ya existe en S3, omitiendo: {file_hash}")
                continue
            
            # Leer y subir archivo
            try:
                with open(local_path, 'rb') as f:
                    content = f.read()
                
                if self.upload_pdf(content, file_hash):
                    results['success'] += 1
                    logger.info(f"PDF migrado a S3: {file_hash}")
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Error subiendo {file_hash}")
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Error procesando {filename}: {str(e)}")
                logger.error(f"Error migrando {filename}: {e}")
        
        return results
