# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Servicio Avanzado de Gestión de Archivos
Versión: 2.0.0
Fecha: 2025-09-21
Autor: Equipo de Desarrollo
"""

import os
import shutil
import hashlib
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc, text
from PIL import Image
import uuid

from .base import BaseService
from app.models.file_upload import FileUpload, FileType
from app.models.user import User
from app.schemas.file_upload import FileUploadCreate, FileUploadResponse
from app.utils.datetime_utils import get_colombia_now


class FileFolder:
    """Clase auxiliar para representar carpetas"""
    def __init__(self, name: str, path: str, parent_path: str = ""):
        self.name = name
        self.path = path
        self.parent_path = parent_path
        self.full_path = f"{parent_path}/{path}" if parent_path else path
        self.created_at = get_colombia_now()
        self.updated_at = get_colombia_now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "path": self.path,
            "parent_path": self.parent_path,
            "full_path": self.full_path,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class FileManagementService(BaseService[FileUpload, FileUploadCreate, dict]):
    """
    Servicio avanzado para gestión completa de archivos
    Incluye carpetas, búsqueda, permisos, versiones, previews
    """

    def __init__(self, upload_dir: str = "uploads", max_file_size: int = 10485760):  # 10MB
        super().__init__(FileUpload)
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
        self.max_file_size = max_file_size

        # Crear directorios base
        self._create_base_directories()

    def _create_base_directories(self):
        """Crear estructura de directorios base"""
        base_dirs = [
            self.upload_dir / "images",
            self.upload_dir / "documents",
            self.upload_dir / "receipts",
            self.upload_dir / "temp",
            self.upload_dir / "thumbnails",
            self.upload_dir / "previews"
        ]
        for dir_path in base_dirs:
            dir_path.mkdir(exist_ok=True)

    # === GESTIÓN AVANZADA DE ARCHIVOS ===

    def upload_file_advanced(self, db: Session, file_content: bytes, filename: str,
                           uploaded_by: int, folder_path: str = "",
                           description: str = "", tags: List[str] = None,
                           is_public: bool = False) -> FileUpload:
        """Subida avanzada de archivos con metadatos completos"""

        # Validar tamaño del archivo
        if len(file_content) > self.max_file_size:
            raise ValueError(f"Archivo demasiado grande. Máximo: {self.max_file_size} bytes")

        # Validar y determinar tipo
        file_type = self.validate_file_type(filename, self._get_mime_type(file_content))

        # Crear estructura de carpetas
        folder_dir = self._ensure_folder_exists(folder_path, file_type)

        # Generar nombre único y guardar
        unique_filename = self.generate_unique_filename(filename)
        file_path = folder_dir / unique_filename

        # Calcular hash para integridad
        file_hash = hashlib.sha256(file_content).hexdigest()

        # Verificar duplicados
        existing_file = db.query(FileUpload).filter(
            and_(FileUpload.file_hash == file_hash, FileUpload.uploaded_by == uploaded_by)
        ).first()

        if existing_file:
            # Crear nueva versión del archivo
            return self._create_file_version(db, existing_file, file_content, file_path,
                                           description, tags, is_public)

        # Guardar archivo
        with open(file_path, 'wb') as f:
            f.write(file_content)

        # Crear thumbnail/preview si es imagen
        thumbnail_path = None
        if file_type == FileType.IMAGEN:
            thumbnail_path = self._create_thumbnail(file_path, unique_filename)

        # Crear registro en BD
        file_upload_data = {
            "filename": filename,
            "file_path": str(file_path.relative_to(self.upload_dir)),
            "file_size": len(file_content),
            "file_type": file_type,
            "mime_type": self._get_mime_type(file_content),
            "file_hash": file_hash,
            "uploaded_by": uploaded_by,
            "folder_path": folder_path,
            "description": description,
            "tags": tags or [],
            "is_public": is_public,
            "thumbnail_path": thumbnail_path,
            "version": 1,
            "metadata": self._extract_metadata(file_content, filename, file_type)
        }

        db_file_upload = FileUpload(**file_upload_data)
        db.add(db_file_upload)
        db.commit()
        db.refresh(db_file_upload)

        return db_file_upload

    def _create_file_version(self, db: Session, existing_file: FileUpload,
                           file_content: bytes, file_path: Path,
                           description: str, tags: List[str], is_public: bool) -> FileUpload:
        """Crear nueva versión de un archivo existente"""

        # Guardar nueva versión
        with open(file_path, 'wb') as f:
            f.write(file_content)

        # Actualizar archivo existente
        existing_file.version += 1
        existing_file.updated_at = get_colombia_now()
        existing_file.description = description or existing_file.description
        existing_file.tags = tags or existing_file.tags
        existing_file.is_public = is_public

        # Crear backup de versión anterior
        self._backup_file_version(existing_file, existing_file.version - 1)

        db.commit()
        db.refresh(existing_file)

        return existing_file

    def _ensure_folder_exists(self, folder_path: str, file_type: FileType) -> Path:
        """Asegurar que la carpeta existe"""
        if folder_path:
            folder_dir = self.upload_dir / folder_path
        else:
            # Carpeta por defecto según tipo
            type_folders = {
                FileType.IMAGEN: "images",
                FileType.DOCUMENTO: "documents",
                FileType.RECIBO: "receipts"
            }
            folder_dir = self.upload_dir / type_folders.get(file_type, "misc")

        folder_dir.mkdir(parents=True, exist_ok=True)
        return folder_dir

    def _create_thumbnail(self, file_path: Path, filename: str) -> Optional[str]:
        """Crear thumbnail para imágenes"""
        try:
            thumbnail_dir = self.upload_dir / "thumbnails"
            thumbnail_dir.mkdir(exist_ok=True)

            with Image.open(file_path) as img:
                # Crear thumbnail 150x150
                img.thumbnail((150, 150))
                thumbnail_filename = f"thumb_{filename}"
                thumbnail_path = thumbnail_dir / thumbnail_filename
                img.save(thumbnail_path, "JPEG", quality=85)

                return str(thumbnail_path.relative_to(self.upload_dir))

        except Exception as e:
            print(f"Error creando thumbnail: {e}")
            return None

    def _extract_metadata(self, file_content: bytes, filename: str, file_type: FileType) -> Dict[str, Any]:
        """Extraer metadatos del archivo"""
        metadata = {
            "original_filename": filename,
            "upload_date": get_colombia_now().isoformat()
        }

        if file_type == FileType.IMAGEN:
            try:
                from PIL import Image
                import io

                img = Image.open(io.BytesIO(file_content))
                metadata.update({
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode
                })
            except:
                pass

        return metadata

    def _backup_file_version(self, file_upload: FileUpload, version: int):
        """Crear backup de versión anterior"""
        try:
            backup_dir = self.upload_dir / "backups" / str(file_upload.id)
            backup_dir.mkdir(parents=True, exist_ok=True)

            source_path = self.upload_dir / file_upload.file_path
            backup_path = backup_dir / f"v{version}_{file_upload.filename}"

            if source_path.exists():
                shutil.copy2(source_path, backup_path)

        except Exception as e:
            print(f"Error creando backup de versión: {e}")

    # === GESTIÓN DE CARPETAS ===

    def create_folder(self, folder_path: str, created_by: int) -> FileFolder:
        """Crear nueva carpeta"""
        folder = FileFolder(
            name=Path(folder_path).name,
            path=folder_path,
            parent_path=str(Path(folder_path).parent) if Path(folder_path).parent != Path(".") else ""
        )

        # Crear directorio físico
        folder_dir = self.upload_dir / folder_path
        folder_dir.mkdir(parents=True, exist_ok=True)

        return folder

    def list_folders(self, parent_path: str = "") -> List[FileFolder]:
        """Listar carpetas en un directorio"""
        base_path = self.upload_dir / parent_path if parent_path else self.upload_dir

        folders = []
        if base_path.exists():
            for item in base_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    folders.append(FileFolder(
                        name=item.name,
                        path=item.name,
                        parent_path=parent_path
                    ))

        return folders

    def delete_folder(self, folder_path: str) -> bool:
        """Eliminar carpeta (solo si está vacía)"""
        folder_dir = self.upload_dir / folder_path

        if not folder_dir.exists():
            return False

        # Verificar si está vacía
        if any(folder_dir.iterdir()):
            raise ValueError("No se puede eliminar carpeta que contiene archivos")

        folder_dir.rmdir()
        return True

    # === BÚSQUEDA Y FILTRADO AVANZADO ===

    def search_files(self, db: Session, query: str = "", filters: Dict[str, Any] = None,
                    sort_by: str = "created_at", sort_order: str = "desc",
                    skip: int = 0, limit: int = 50) -> Tuple[List[FileUpload], int]:
        """Búsqueda avanzada de archivos"""

        search_query = db.query(FileUpload)

        # Búsqueda por texto
        if query:
            search_term = f"%{query}%"
            search_query = search_query.filter(
                or_(
                    FileUpload.filename.ilike(search_term),
                    FileUpload.description.ilike(search_term),
                    FileUpload.folder_path.ilike(search_term),
                    FileUpload.tags.contains([query])  # Búsqueda en tags
                )
            )

        # Aplicar filtros
        if filters:
            if filters.get("file_type"):
                # Normalizar string a Enum (acepta español e inglés por compatibilidad)
                ft = filters["file_type"]
                try:
                    if isinstance(ft, str):
                        normalized = ft.upper()
                        mapping = {
                            "IMAGEN": FileType.IMAGEN,
                            "IMAGE": FileType.IMAGEN,
                            "DOCUMENTO": FileType.DOCUMENTO,
                            "DOCUMENT": FileType.DOCUMENTO,
                            "RECIBO": FileType.RECIBO,
                            "RECEIPT": FileType.RECIBO
                        }
                        enum_value = mapping.get(normalized)
                        if enum_value is not None:
                            search_query = search_query.filter(FileUpload.file_type == enum_value)
                        else:
                            search_query = search_query.filter(FileUpload.file_type == ft)
                    else:
                        search_query = search_query.filter(FileUpload.file_type == ft)
                except Exception:
                    search_query = search_query.filter(FileUpload.file_type == filters["file_type"])
            if filters.get("uploaded_by"):
                search_query = search_query.filter(FileUpload.uploaded_by == filters["uploaded_by"])
            if filters.get("folder_path"):
                search_query = search_query.filter(FileUpload.folder_path == filters["folder_path"])
            if filters.get("is_public") is not None:
                search_query = search_query.filter(FileUpload.is_public == filters["is_public"])
            if filters.get("date_from"):
                search_query = search_query.filter(FileUpload.created_at >= filters["date_from"])
            if filters.get("date_to"):
                search_query = search_query.filter(FileUpload.created_at <= filters["date_to"])
            if filters.get("min_size"):
                search_query = search_query.filter(FileUpload.file_size >= filters["min_size"])
            if filters.get("max_size"):
                search_query = search_query.filter(FileUpload.file_size <= filters["max_size"])

        # Ordenamiento
        order_column = getattr(FileUpload, sort_by, FileUpload.created_at)
        if sort_order == "desc":
            search_query = search_query.order_by(desc(order_column))
        else:
            search_query = search_query.order_by(asc(order_column))

        # Paginación
        total = search_query.count()
        files = search_query.offset(skip).limit(limit).all()

        return files, total

    def get_files_by_folder(self, db: Session, folder_path: str,
                           skip: int = 0, limit: int = 50) -> Tuple[List[FileUpload], int]:
        """Obtener archivos de una carpeta específica"""
        query = db.query(FileUpload).filter(FileUpload.folder_path == folder_path)
        total = query.count()
        files = query.order_by(desc(FileUpload.created_at)).offset(skip).limit(limit).all()

        return files, total

    # === PERMISOS Y COMPARTIR ===

    def share_file(self, db: Session, file_id: int, shared_with_user_id: int,
                  permissions: List[str] = None, expires_at: Optional[datetime] = None) -> bool:
        """Compartir archivo con otro usuario"""

        file_upload = self.get_by_id(db, file_id)
        if not file_upload:
            return False

        # Aquí iría la lógica de compartir (requeriría una tabla de permisos de archivos)
        # Por ahora, solo marcamos como público si se comparte con todos
        if shared_with_user_id == 0:  # Compartir públicamente
            file_upload.is_public = True
            db.commit()

        return True

    def get_shared_files(self, db: Session, user_id: int) -> List[FileUpload]:
        """Obtener archivos compartidos con un usuario"""
        # Por ahora, retornamos archivos públicos
        return db.query(FileUpload).filter(FileUpload.is_public == True).all()

    # === ESTADÍSTICAS Y REPORTES ===

    def get_file_statistics(self, db: Session) -> Dict[str, Any]:
        """Obtener estadísticas completas de archivos"""

        # Estadísticas básicas
        total_files = db.query(func.count(FileUpload.id)).scalar()
        total_size = db.query(func.sum(FileUpload.file_size)).scalar() or 0

        # Por tipo
        type_stats = db.query(
            FileUpload.file_type, func.count(FileUpload.id), func.sum(FileUpload.file_size)
        ).group_by(FileUpload.file_type).all()

        files_by_type = {str(ftype): {"count": count, "size": size or 0}
                        for ftype, count, size in type_stats}

        # Por usuario
        user_stats = db.query(
            FileUpload.uploaded_by, func.count(FileUpload.id), func.sum(FileUpload.file_size)
        ).group_by(FileUpload.uploaded_by).all()

        # Actividad reciente (últimos 30 días)
        thirty_days_ago = get_colombia_now() - timedelta(days=30)
        recent_files = db.query(func.count(FileUpload.id)).filter(
            FileUpload.created_at >= thirty_days_ago
        ).scalar()

        # Archivos por carpeta
        folder_stats = db.query(
            FileUpload.folder_path, func.count(FileUpload.id), func.sum(FileUpload.file_size)
        ).group_by(FileUpload.folder_path).all()

        folders_summary = {folder or "root": {"count": count, "size": size or 0}
                          for folder, count, size in folder_stats}

        # Uso de almacenamiento
        storage_used = self._calculate_storage_usage()
        storage_limit = 1073741824  # 1GB por defecto
        storage_available = storage_limit - storage_used

        return {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "files_by_type": files_by_type,
            "files_by_user": {str(user_id): {"count": count, "size": size or 0}
                            for user_id, count, size in user_stats},
            "files_by_folder": folders_summary,
            "recent_files_count": recent_files,
            "storage": {
                "used_bytes": storage_used,
                "used_mb": round(storage_used / (1024 * 1024), 2),
                "available_bytes": storage_available,
                "available_mb": round(storage_available / (1024 * 1024), 2),
                "usage_percentage": round((storage_used / storage_limit) * 100, 2)
            }
        }

    def _calculate_storage_usage(self) -> int:
        """Calcular uso total de almacenamiento"""
        total_size = 0
        for file_path in self.upload_dir.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size

    # === GESTIÓN DE VERSIONES ===

    def get_file_versions(self, db: Session, file_id: int) -> List[Dict[str, Any]]:
        """Obtener versiones de un archivo"""
        file_upload = self.get_by_id(db, file_id)
        if not file_upload:
            return []

        versions = [{
            "version": file_upload.version,
            "filename": file_upload.filename,
            "file_size": file_upload.file_size,
            "created_at": file_upload.created_at.isoformat(),
            "updated_at": file_upload.updated_at.isoformat(),
            "description": file_upload.description,
            "current": True
        }]

        # Buscar versiones anteriores en backups
        backup_dir = self.upload_dir / "backups" / str(file_id)
        if backup_dir.exists():
            for backup_file in backup_dir.glob("v*_*"):
                version_num = int(backup_file.name.split('_')[0][1:])
                versions.append({
                    "version": version_num,
                    "filename": backup_file.name,
                    "file_size": backup_file.stat().st_size,
                    "created_at": datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat(),
                    "current": False
                })

        return sorted(versions, key=lambda x: x["version"], reverse=True)

    def restore_file_version(self, db: Session, file_id: int, version: int) -> bool:
        """Restaurar una versión anterior del archivo"""
        file_upload = self.get_by_id(db, file_id)
        if not file_upload:
            return False

        backup_dir = self.upload_dir / "backups" / str(file_id)
        backup_pattern = f"v{version}_*"

        for backup_file in backup_dir.glob(backup_pattern):
            # Restaurar archivo
            target_path = self.upload_dir / file_upload.file_path
            shutil.copy2(backup_file, target_path)

            # Actualizar metadata
            file_upload.version = version + 1
            file_upload.updated_at = get_colombia_now()

            db.commit()
            return True

        return False

    # === LIMPIEZA Y MANTENIMIENTO ===

    def cleanup_old_files(self, db: Session, days_old: int = 90, dry_run: bool = True) -> Dict[str, Any]:
        """Limpiar archivos antiguos"""

        cutoff_date = get_colombia_now() - timedelta(days=days_old)

        # Encontrar archivos candidatos para eliminación
        old_files = db.query(FileUpload).filter(
            and_(
                FileUpload.created_at < cutoff_date,
                FileUpload.is_public == False  # No eliminar archivos públicos
            )
        ).all()

        deleted_files = []
        total_size_freed = 0

        for file_upload in old_files:
            if not dry_run:
                # Eliminar archivo físico
                file_path = self.upload_dir / file_upload.file_path
                if file_path.exists():
                    file_path.unlink()
                    total_size_freed += file_upload.file_size

                # Eliminar registro de BD
                db.delete(file_upload)

            deleted_files.append({
                "id": file_upload.id,
                "filename": file_upload.filename,
                "size": file_upload.file_size,
                "created_at": file_upload.created_at.isoformat()
            })

        if not dry_run:
            db.commit()

        return {
            "files_to_delete": len(deleted_files),
            "total_size_freed": total_size_freed,
            "dry_run": dry_run,
            "cutoff_date": cutoff_date.isoformat(),
            "files": deleted_files
        }

    def cleanup_temp_files(self, hours_old: int = 24) -> Dict[str, Any]:
        """Limpiar archivos temporales"""

        temp_dir = self.upload_dir / "temp"
        if not temp_dir.exists():
            return {"temp_files_deleted": 0, "size_freed": 0}

        cutoff_time = get_colombia_now() - timedelta(hours=hours_old)

        deleted_files = []
        total_size_freed = 0

        for file_path in temp_dir.glob("*"):
            if file_path.is_file() and datetime.fromtimestamp(file_path.stat().st_mtime) < cutoff_time:
                size = file_path.stat().st_size
                file_path.unlink()

                deleted_files.append({
                    "filename": file_path.name,
                    "size": size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
                total_size_freed += size

        return {
            "temp_files_deleted": len(deleted_files),
            "size_freed": total_size_freed,
            "files": deleted_files
        }

    # === UTILIDADES ===

    def _get_mime_type(self, file_content: bytes) -> str:
        """Determinar MIME type del archivo"""
        import magic
        try:
            return magic.from_buffer(file_content, mime=True)
        except:
            return "application/octet-stream"

    def validate_file_type(self, filename: str, mime_type: str) -> FileType:
        """Validar y determinar tipo de archivo (versión avanzada)"""
        extension = Path(filename).suffix.lower()

        # Imágenes
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff']
        image_mimes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp', 'image/tiff']

        if extension in image_extensions or mime_type in image_mimes:
            return FileType.IMAGEN

        # Documentos
        doc_extensions = ['.pdf', '.doc', '.docx', '.txt', '.xls', '.xlsx', '.ppt', '.pptx', '.odt']
        doc_mimes = [
            'application/pdf', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain', 'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ]

        if extension in doc_extensions or mime_type in doc_mimes:
            return FileType.DOCUMENTO

        # Recibos por defecto
        return FileType.RECIBO

    def generate_unique_filename(self, original_filename: str) -> str:
        """Generar nombre de archivo único con timestamp"""
        timestamp = get_colombia_now().strftime("%Y%m%d_%H%M%S")
        extension = Path(original_filename).suffix
        unique_id = str(uuid.uuid4())[:8]
        return f"{timestamp}_{unique_id}{extension}"