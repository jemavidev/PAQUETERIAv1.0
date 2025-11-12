# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Servicio S3
Versión: 1.0.0
Fecha: 2025-09-26
Autor: KiloCode
"""

import boto3
import os
import time
from typing import Optional
from botocore.exceptions import ClientError
from pathlib import Path


class S3Service:
    """
    Servicio para gestión de archivos en AWS S3
    """

    def __init__(self):
        # Usar configuración centralizada desde CODE/LOCAL/.env ÚNICAMENTE
        from app.config import settings
        
        self.bucket_name = settings.aws_s3_bucket
        self.region = settings.aws_region
        self.base_path = 'paquetes-recibidos-imagenes'
        
        print(f"🪣 S3Service inicializado:")
        print(f"   Bucket: {self.bucket_name}")
        print(f"   Región: {self.region}")
        print(f"   Base Path: {self.base_path}")

        # Verificar que las credenciales estén configuradas en CODE/LOCAL/.env
        if not settings.aws_access_key_id or not settings.aws_secret_access_key:
            raise ValueError("❌ Credenciales AWS no configuradas en CODE/LOCAL/.env")
        
        if settings.aws_access_key_id in ['your-aws-access-key', ''] or settings.aws_secret_access_key in ['your-aws-secret-key', '']:
            raise ValueError("❌ Credenciales AWS de ejemplo detectadas. Configure credenciales reales en CODE/LOCAL/.env")

        # Crear cliente S3 usando configuración centralizada
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=self.region
        )

    def upload_file(self, file_content: bytes, s3_key: str, content_type: str = None) -> str:
        """
        Subir archivo a S3 con key específica

        Args:
            file_content: Contenido del archivo en bytes
            s3_key: Key completa para S3 (incluyendo path)
            content_type: Tipo de contenido MIME

        Returns:
            str: URL del archivo en S3
        """
        try:
            # Determinar content type si no se proporciona
            if not content_type:
                filename = s3_key.split('/')[-1]
                content_type = self._get_content_type(filename)

            print(f"🔄 Subiendo archivo a S3:")
            print(f"   📦 Bucket: {self.bucket_name}")
            print(f"   🔑 Key: {s3_key}")
            print(f"   📏 Tamaño: {len(file_content)} bytes")
            print(f"   🏷️ Content-Type: {content_type}")

            # Subir archivo a S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type,
                ACL='private'  # Archivos privados, accesibles solo con URL firmada
            )

            # Generar URL del archivo
            s3_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
            print(f"✅ Archivo subido exitosamente:")
            print(f"   🔗 URL: {s3_url}")
            print(f"   📍 Ubicación: s3://{self.bucket_name}/{s3_key}")

            return s3_url

        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            print(f"❌ Error de S3 - Código: {error_code}, Mensaje: {error_message}")
            raise Exception(f"Error uploading to S3 ({error_code}): {error_message}")
        except Exception as e:
            print(f"❌ Error inesperado en S3: {str(e)}")
            raise Exception(f"Error uploading to S3: {str(e)}")

    def upload_file_legacy(self, file_content: bytes, filename: str, package_id: int, file_type: str = 'reception_image') -> dict:
        """
        Método legacy para compatibilidad - Subir archivo a S3 con generación automática de key

        Args:
            file_content: Contenido del archivo en bytes
            filename: Nombre original del archivo
            package_id: ID del paquete
            file_type: Tipo de archivo (reception_image, delivery_image, document)

        Returns:
            dict: Información del archivo subido con s3_key y s3_url
        """
        try:
            # Generar nombre único para el archivo
            import uuid
            file_extension = Path(filename).suffix.lower()
            unique_filename = f"{uuid.uuid4()}{file_extension}"

            # Crear la key S3 con estructura de carpetas
            s3_key = f"{self.base_path}/packages/{package_id}/{file_type}s/{unique_filename}"
            print(f"🔧 Método legacy - Key generada: {s3_key}")

            # Subir archivo usando el nuevo método
            s3_url = self.upload_file(file_content, s3_key, self._get_content_type(filename))

            return {
                's3_key': s3_key,
                's3_url': s3_url,
                'filename': filename,
                'unique_filename': unique_filename
            }

        except ClientError as e:
            raise Exception(f"Error uploading to S3: {str(e)}")

    def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> str:
        """
        OPCIÓN 1: Generar URL firmada mejorada con validaciones y retry logic
        Maneja tanto la estructura antigua como la nueva de imágenes

        Args:
            s3_key: Key del archivo en S3
            expiration: Tiempo de expiración en segundos (default 1 hora)

        Returns:
            str: URL firmada para acceso privado
        """
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            # Validar entrada
            if not s3_key or not s3_key.strip():
                raise ValueError("s3_key no puede estar vacío")
            
            if expiration <= 0 or expiration > 604800:  # Máximo 7 días
                raise ValueError("expiration debe estar entre 1 segundo y 7 días")
            
            # Normalizar la key S3
            actual_key = self._normalize_s3_key(s3_key)
            logger.info(f"🔄 Generando URL presignada para: {actual_key}")
            
            # Verificar que el archivo existe antes de generar URL (opcional pero recomendado)
            file_exists = False
            try:
                head_response = self.s3_client.head_object(Bucket=self.bucket_name, Key=actual_key)
                file_exists = True
                file_size = head_response.get('ContentLength', 0)
                logger.info(f"✅ Archivo confirmado en S3: {actual_key} ({file_size} bytes)")
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == '404':
                    logger.warning(f"⚠️ Archivo no encontrado en S3: {actual_key}")
                    # Continuar generando URL aunque el archivo no exista (para casos edge)
                elif error_code in ['AccessDenied', 'Forbidden']:
                    logger.error(f"❌ Sin permisos para verificar archivo: {actual_key}")
                    raise Exception(f"Access denied to S3 file: {actual_key}")
                else:
                    logger.warning(f"⚠️ No se pudo verificar archivo (continuando): {e}")
            
            # Generar URL presignada con retry logic y backoff exponencial
            last_error = None
            for attempt in range(3):
                try:
                    logger.info(f"🔄 Generando URL presignada - intento {attempt + 1}/3")
                    
                    url = self.s3_client.generate_presigned_url(
                        'get_object',
                        Params={
                            'Bucket': self.bucket_name,
                            'Key': actual_key
                        },
                        ExpiresIn=expiration
                    )
                    
                    # Validar que la URL generada es válida
                    if not url or not url.startswith('https://'):
                        raise Exception("URL presignada inválida generada")
                    
                    logger.info(f"✅ URL presignada generada exitosamente (intento {attempt + 1})")
                    logger.info(f"🔗 URL length: {len(url)} chars")
                    
                    return url
                    
                except Exception as retry_error:
                    last_error = retry_error
                    logger.error(f"❌ Error en intento {attempt + 1}: {retry_error}")
                    if attempt == 2:  # Último intento
                        break
                    
                    # Backoff exponencial
                    wait_time = (2 ** attempt) * 0.5  # 0.5s, 1s, 2s
                    logger.info(f"⏳ Esperando {wait_time}s antes del siguiente intento")
                    time.sleep(wait_time)
            
            # Si llegamos aquí, todos los intentos fallaron
            raise Exception(f"Failed to generate presigned URL after 3 attempts. Last error: {last_error}")
            
        except ValueError as ve:
            logger.error(f"❌ Error de validación: {ve}")
            raise ve
        except Exception as e:
            logger.error(f"❌ Error generando URL presignada: {str(e)}")
            raise Exception(f"Error generating presigned URL: {str(e)}")

    def _normalize_s3_key(self, s3_key: str) -> str:
        """
        Normalizar key S3 para compatibilidad con estructuras antiguas y nuevas
        NUEVO: Método para manejar diferentes formatos de keys
        
        Args:
            s3_key: Key original del archivo
            
        Returns:
            str: Key normalizada para S3
        """
        if not s3_key:
            raise ValueError("s3_key no puede estar vacío")
        
        # Si ya incluye el base_path, usar tal como está
        if self.base_path in s3_key:
            print(f"🔧 Key con base_path detectada: {s3_key}")
            return s3_key
        
        # Si es estructura nueva (YYYY/MM/DD/packages/...), usar tal como está
        import re
        if re.match(r'^\d{4}/\d{2}/\d{2}/packages/', s3_key):
            print(f"🔧 Estructura nueva detectada: {s3_key}")
            return s3_key
        
        # Si es estructura antigua sin base_path, agregarlo
        normalized_key = f"{self.base_path}/{s3_key}"
        print(f"🔧 Key normalizada (estructura antigua): {normalized_key}")
        return normalized_key
    
    def _is_new_structure(self, s3_key: str) -> bool:
        """
        Detectar si la imagen usa la nueva estructura de almacenamiento
        
        Nueva estructura: {year}/{month}/{day}/packages/{package_id}/{package_type}/{filename}
        Antigua estructura: packages/{package_id}/reception_images/{filename}
        
        Args:
            s3_key: Key del archivo en S3
            
        Returns:
            bool: True si es estructura nueva, False si es antigua
        """
        # Patrón para nueva estructura: YYYY/MM/DD/packages/...
        import re
        new_structure_pattern = r'^\d{4}/\d{2}/\d{2}/packages/'
        
        if re.match(new_structure_pattern, s3_key):
            return True
        
        # Si contiene el base_path de la estructura antigua
        if self.base_path in s3_key:
            return False
            
        # Si no contiene base_path, asumir que es estructura nueva
        return True

    def delete_file(self, s3_key: str) -> bool:
        """
        Eliminar archivo de S3

        Args:
            s3_key: Key del archivo en S3

        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError as e:
            print(f"Error deleting file from S3: {str(e)}")
            return False

    def _get_content_type(self, filename: str) -> str:
        """
        Determinar el content type basado en la extensión del archivo
        """
        extension = Path(filename).suffix.lower()

        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain'
        }

        return content_types.get(extension, 'application/octet-stream')

    def test_connection(self) -> bool:
        """
        OPCIÓN 1: Probar conexión con S3 con validaciones completas
        """
        import logging
        from datetime import datetime
        
        logger = logging.getLogger(__name__)
        
        try:
            logger.info("🔄 Iniciando test de conexión S3...")
            
            # Test 1: Verificar acceso al bucket
            try:
                self.s3_client.head_bucket(Bucket=self.bucket_name)
                logger.info("✅ Test 1: Acceso al bucket confirmado")
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == '404':
                    logger.error(f"❌ Test 1: Bucket no encontrado: {self.bucket_name}")
                    return False
                elif error_code in ['AccessDenied', 'Forbidden']:
                    logger.error(f"❌ Test 1: Sin permisos para acceder al bucket: {self.bucket_name}")
                    return False
                else:
                    logger.error(f"❌ Test 1: Error accediendo al bucket: {error_code}")
                    return False
            
            # Test 2: Probar escritura
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            test_key = f"{self.base_path}/connection_test/test_{timestamp}.txt"
            test_content = f"Connection test - {timestamp}".encode('utf-8')
            
            try:
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=test_key,
                    Body=test_content,
                    ContentType='text/plain',
                    ACL='private'
                )
                logger.info(f"✅ Test 2: Escritura exitosa - {test_key}")
            except ClientError as e:
                logger.error(f"❌ Test 2: Error de escritura: {e}")
                return False
            
            # Test 3: Probar lectura
            try:
                response = self.s3_client.get_object(
                    Bucket=self.bucket_name,
                    Key=test_key
                )
                read_content = response['Body'].read()
                if read_content == test_content:
                    logger.info("✅ Test 3: Lectura exitosa y contenido verificado")
                else:
                    logger.error("❌ Test 3: Contenido leído no coincide")
                    return False
            except ClientError as e:
                logger.error(f"❌ Test 3: Error de lectura: {e}")
                return False
            
            # Test 4: Probar eliminación (limpiar archivo de prueba)
            try:
                self.s3_client.delete_object(
                    Bucket=self.bucket_name,
                    Key=test_key
                )
                logger.info("✅ Test 4: Eliminación exitosa - archivo de prueba limpiado")
            except ClientError as e:
                logger.warning(f"⚠️ Test 4: No se pudo eliminar archivo de prueba: {e}")
                # No fallar el test por esto
            
            # Test 5: Probar generación de URL presignada
            try:
                # Usar un archivo existente o crear uno temporal
                temp_key = f"{self.base_path}/connection_test/presigned_test_{timestamp}.txt"
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=temp_key,
                    Body=b"Presigned URL test",
                    ContentType='text/plain'
                )
                
                presigned_url = self.generate_presigned_url(temp_key, expiration=300)
                if presigned_url and presigned_url.startswith('https://'):
                    logger.info("✅ Test 5: Generación de URL presignada exitosa")
                else:
                    logger.error("❌ Test 5: URL presignada inválida")
                    return False
                
                # Limpiar archivo temporal
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=temp_key)
                
            except Exception as e:
                logger.error(f"❌ Test 5: Error generando URL presignada: {e}")
                return False
            
            logger.info("🎉 Todos los tests de conexión S3 pasaron exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error general en test de conexión S3: {str(e)}")
            return False