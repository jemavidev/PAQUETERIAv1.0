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
            return T