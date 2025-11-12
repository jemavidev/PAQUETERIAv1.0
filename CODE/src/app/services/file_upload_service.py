# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Servicio de File Uploads
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo
"""

import os
import mimetypes
from typing import Optional, List
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import func

from .base import BaseService
from .s3_service import S3Service
from app.models.file_upload import FileUpload, FileType
from app.schemas.file_upload import FileUploadCreate, FileUploadResponse


class FileUploadService(BaseService[FileUpload, FileUploadCreate, dict]):
    """
    Servicio para gestión de archivos subidos
    """

    def __init__(self, upload_dir: str = "uploads"):
        super().__init__(FileUpload)
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
        self.s3_service = S3Service()

    def create_file_upload(self, db: Session, file_upload_in: FileUploadCreate, uploaded_by: int) -> FileUpload:
        """Crear registro de file upload"""
        file_upload_data = file_upload_in.model_dump()
        file_upload_data['uploaded_by'] = uploaded_by

        db_file_upload = FileUpload(**file_upload_data)
        db.add(db_file_upload)
        db.commit()
        db.refresh(db_file_upload)
        return db_file_upload

    def get_files_by_package(self, db: Session, package_id: int) -> List[FileUpload]:
        """Obtener archivos de un paquete"""
        return db.query(FileUpload).filter(FileUpload.package_id == package_id).all()

    def get_files_by_type(self, db: Session, file_type: FileType, skip: int = 0, limit: int = 50) -> List[FileUpload]:
        """Obtener archivos por tipo"""
        return db.query(FileUpload).filter(FileUpload.file_type == file_type).offset(skip).limit(limit).all()

    def delete_file(self, db: Session, file_id: int) -> bool:
        """Eliminar archivo y su registro"""
        file_upload = self.get_by_id(db, file_id)
        if not file_upload:
            return False

        # Eliminar archivo de S3 si existe s3_key
        if file_upload.s3_key:
            self.s3_service.delete_file(file_upload.s3_key)

        # Eliminar archivo físico como fallback
        if hasattr(file_upload, 'file_path') and file_upload.file_path:
            file_path = self.upload_dir / file_upload.file_path
            if file_path.exists():
                file_path.unlink()

        # Eliminar registro de BD
        return self.delete(db, file_id)

    def get_file_stats(self, db: Session) -> dict:
        """Obtener estadísticas de archivos"""
        total_files = db.query(FileUpload).count()
        total_size = db.query(func.sum(FileUpload.file_size)).scalar() or 0

        # Por tipo
        images_count = db.query(FileUpload).filter(FileUpload.file_type == FileType.IMAGEN).count()
        documents_count = db.query(FileUpload).filter(FileUpload.file_type == FileType.DOCUMENTO).count()
        receipts_count = db.query(FileUpload).filter(FileUpload.file_type == FileType.RECIBO).count()

        return {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "images_count": images_count,
            "documents_count": documents_count,
            "receipts_count": receipts_count
        }

    def validate_file_type(self, filename: str, content_type: str) -> FileType:
        """Validar y determinar tipo de archivo"""
        # Determinar tipo por extensión y MIME type
        extension = Path(filename).suffix.lower()

        # Imágenes
        if extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp'] or content_type.startswith('image/'):
            return FileType.IMAGEN

        # Documentos
        if extension in ['.pdf', '.doc', '.docx', '.txt', '.xls', '.xlsx'] or content_type in [
            'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ]:
            return FileType.DOCUMENTO

        # Recibos (por defecto si no se reconoce)
        return FileType.RECIBO

    def generate_unique_filename(self, original_filename: str) -> str:
        """Generar nombre de archivo único"""
        import uuid
        extension = Path(original_filename).suffix
        return f"{uuid.uuid4()}{extension}"

    def save_file(self, file_content: bytes, filename: str) -> str:
        """Guardar archivo en el sistema de archivos (fallback)"""
        unique_filename = self.generate_unique_filename(filename)
        file_path = self.upload_dir / unique_filename

        with open(file_path, 'wb') as f:
            f.write(file_content)

        return unique_filename

    def upload_to_s3(self, file_content: bytes, filename: str, package_id: int, file_type: str = 'reception_image') -> dict:
        """Subir archivo a S3"""
        return self.s3_service.upload_file(file_content, filename, package_id, file_type)