# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Rutas Avanzadas de Gestión de Archivos
Versión: 2.0.0
Fecha: 2025-09-21
Autor: Equipo de Desarrollo
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pathlib import Path
import uuid

from app.database import get_db
from app.services.file_management_service import FileManagementService
from app.dependencies import get_current_active_user_from_cookies, get_current_admin_user
from app.models.file_upload import FileUpload, FileType
from app.models.user import User
from app.utils.datetime_utils import get_colombia_now

router = APIRouter(tags=["Gestión de Archivos"])


# === SUBIDA Y GESTIÓN BÁSICA DE ARCHIVOS ===

@router.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    folder_path: str = Form(""),
    description: str = Form(""),
    tags: str = Form(""),  # JSON string
    is_public: bool = Form(False),
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Subida avanzada de archivos con metadatos completos"""
    try:
        # Leer contenido del archivo
        file_content = await file.read()

        # Parsear tags
        file_tags = []
        if tags:
            try:
                import json
                file_tags = json.loads(tags)
            except:
                file_tags = [tag.strip() for tag in tags.split(",") if tag.strip()]

        # Usar servicio avanzado
        service = FileManagementService()

        uploaded_file = service.upload_file_advanced(
            db=db,
            file_content=file_content,
            filename=file.filename,
            uploaded_by=str(current_user.id),
            folder_path=folder_path,
            description=description,
            tags=file_tags,
            is_public=is_public
        )

        return {
            "success": True,
            "message": "Archivo subido exitosamente",
            "file": {
                "id": uploaded_file.id,
                "filename": uploaded_file.filename,
                "file_path": uploaded_file.file_path,
                "file_size": uploaded_file.file_size,
                "file_type": uploaded_file.file_type.value if uploaded_file.file_type else None,
                "folder_path": uploaded_file.folder_path,
                "description": uploaded_file.description,
                "tags": uploaded_file.tags,
                "is_public": uploaded_file.is_public,
                "version": uploaded_file.version,
                "uploaded_at": uploaded_file.created_at.isoformat()
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error subiendo archivo: {str(e)}")


@router.get("/")
async def list_files(
    folder_path: str = Query("", description="Carpeta específica"),
    file_type: Optional[str] = None,
    search: str = Query("", description="Término de búsqueda"),
    sort_by: str = Query("created_at", description="Campo de ordenamiento"),
    sort_order: str = Query("desc", description="Orden: asc o desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Listar archivos con filtros avanzados"""
    try:
        service = FileManagementService()

        filters = {}
        if file_type:
            filters["file_type"] = file_type
        if folder_path:
            filters["folder_path"] = folder_path

        files, total = service.search_files(
            db=db,
            query=search,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            skip=skip,
            limit=limit
        )

        return {
            "files": [
                {
                    "id": file.id,
                    "filename": file.filename,
                    "file_path": file.file_path,
                    "file_size": file.file_size,
                    "file_type": file.file_type.value if file.file_type else None,
                    "folder_path": file.folder_path,
                    "description": file.description,
                    "tags": file.tags,
                    "is_public": file.is_public,
                    "version": file.version,
                    "thumbnail_path": file.thumbnail_path,
                    "uploaded_by": file.uploaded_by,
                    "created_at": file.created_at.isoformat(),
                    "updated_at": file.updated_at.isoformat()
                } for file in files
            ],
            "total": total,
            "skip": skip,
            "limit": limit
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando archivos: {str(e)}")


@router.get("/{file_id}")
async def get_file_details(
    file_id: int,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Obtener detalles completos de un archivo"""
    try:
        service = FileManagementService()
        file_upload = service.get_by_id(db, file_id)

        if not file_upload:
            raise HTTPException(status_code=404, detail="Archivo no encontrado")

        # Verificar permisos (público o propio)
        if not file_upload.is_public and file_upload.uploaded_by != str(current_user.id):
            raise HTTPException(status_code=403, detail="No tienes permisos para ver este archivo")

        return {
            "id": file_upload.id,
            "filename": file_upload.filename,
            "file_path": file_upload.file_path,
            "file_size": file_upload.file_size,
            "file_type": file_upload.file_type.value if file_upload.file_type else None,
            "mime_type": file_upload.mime_type,
            "file_hash": file_upload.file_hash,
            "folder_path": file_upload.folder_path,
            "description": file_upload.description,
            "tags": file_upload.tags,
            "is_public": file_upload.is_public,
            "version": file_upload.version,
            "thumbnail_path": file_upload.thumbnail_path,
            "metadata": file_upload.metadata,
            "uploaded_by": file_upload.uploaded_by,
            "created_at": file_upload.created_at.isoformat(),
            "updated_at": file_upload.updated_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo detalles del archivo: {str(e)}")


@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Descargar archivo"""
    try:
        service = FileManagementService()
        file_upload = service.get_by_id(db, file_id)

        if not file_upload:
            raise HTTPException(status_code=404, detail="Archivo no encontrado")

        # Verificar permisos
        if not file_upload.is_public and file_upload.uploaded_by != str(current_user.id):
            raise HTTPException(status_code=403, detail="No tienes permisos para descargar este archivo")

        file_path = service.upload_dir / file_upload.file_path
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Archivo no encontrado en el sistema de archivos")

        return FileResponse(
            path=file_path,
            filename=file_upload.filename,
            media_type=file_upload.mime_type
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error descargando archivo: {str(e)}")


@router.get("/{file_id}/thumbnail")
async def get_file_thumbnail(
    file_id: int,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Obtener thumbnail del archivo (si existe)"""
    try:
        service = FileManagementService()
        file_upload = service.get_by_id(db, file_id)

        if not file_upload or not file_upload.thumbnail_path:
            raise HTTPException(status_code=404, detail="Thumbnail no encontrado")

        # Verificar permisos
        if not file_upload.is_public and file_upload.uploaded_by != str(current_user.id):
            raise HTTPException(status_code=403, detail="No tienes permisos para ver este thumbnail")

        thumbnail_path = service.upload_dir / file_upload.thumbnail_path
        if not thumbnail_path.exists():
            raise HTTPException(status_code=404, detail="Thumbnail no encontrado")

        return FileResponse(path=thumbnail_path, media_type="image/jpeg")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo thumbnail: {str(e)}")


@router.put("/{file_id}")
async def update_file_metadata(
    file_id: int,
    update_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Actualizar metadatos del archivo"""
    try:
        service = FileManagementService()
        file_upload = service.get_by_id(db, file_id)

        if not file_upload:
            raise HTTPException(status_code=404, detail="Archivo no encontrado")

        # Verificar permisos (solo propietario)
        if file_upload.uploaded_by != str(current_user.id):
            raise HTTPException(status_code=403, detail="Solo puedes editar tus propios archivos")

        # Actualizar campos permitidos
        allowed_fields = ["description", "tags", "is_public", "folder_path"]
        for field in allowed_fields:
            if field in update_data:
                setattr(file_upload, field, update_data[field])

        file_upload.updated_at = get_colombia_now()
        db.commit()
        db.refresh(file_upload)

        return {
            "success": True,
            "message": "Archivo actualizado exitosamente",
            "file": {
                "id": file_upload.id,
                "filename": file_upload.filename,
                "description": file_upload.description,
                "tags": file_upload.tags,
                "is_public": file_upload.is_public,
                "folder_path": file_upload.folder_path,
                "updated_at": file_upload.updated_at.isoformat()
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando archivo: {str(e)}")


@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Eliminar archivo"""
    try:
        service = FileManagementService()
        file_upload = service.get_by_id(db, file_id)

        if not file_upload:
            raise HTTPException(status_code=404, detail="Archivo no encontrado")

        # Verificar permisos (solo propietario)
        if file_upload.uploaded_by != str(current_user.id):
            raise HTTPException(status_code=403, detail="Solo puedes eliminar tus propios archivos")

        success = service.delete_file(db, file_id)

        if success:
            return {"success": True, "message": "Archivo eliminado exitosamente"}
        else:
            raise HTTPException(status_code=500, detail="Error eliminando archivo")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando archivo: {str(e)}")


# === GESTIÓN DE CARPETAS ===

@router.post("/folders")
async def create_folder(
    folder_data: Dict[str, str],
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Crear nueva carpeta"""
    try:
        folder_path = folder_data.get("path", "").strip()
        if not folder_path:
            raise HTTPException(status_code=400, detail="Ruta de carpeta requerida")

        service = FileManagementService()
        folder = service.create_folder(folder_path, str(current_user.id))

        return {
            "success": True,
            "message": "Carpeta creada exitosamente",
            "folder": folder.to_dict()
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando carpeta: {str(e)}")


@router.get("/folders/list")
async def list_folders(
    parent_path: str = Query("", description="Carpeta padre"),
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Listar carpetas"""
    try:
        service = FileManagementService()
        folders = service.list_folders(parent_path)

        return {
            "folders": [folder.to_dict() for folder in folders]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando carpetas: {str(e)}")


@router.delete("/folders/{folder_path:path}")
async def delete_folder(
    folder_path: str,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Eliminar carpeta (solo si está vacía)"""
    try:
        service = FileManagementService()

        # Verificar que no haya archivos en la carpeta
        files_in_folder, _ = service.get_files_by_folder(db, folder_path)
        if files_in_folder:
            raise HTTPException(status_code=400, detail="No se puede eliminar carpeta que contiene archivos")

        success = service.delete_folder(folder_path)

        if success:
            return {"success": True, "message": "Carpeta eliminada exitosamente"}
        else:
            raise HTTPException(status_code=404, detail="Carpeta no encontrada")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando carpeta: {str(e)}")


# === GESTIÓN DE VERSIONES ===

@router.get("/{file_id}/versions")
async def get_file_versions(
    file_id: int,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Obtener versiones de un archivo"""
    try:
        service = FileManagementService()
        file_upload = service.get_by_id(db, file_id)

        if not file_upload:
            raise HTTPException(status_code=404, detail="Archivo no encontrado")

        # Verificar permisos
        if file_upload.uploaded_by != str(current_user.id):
            raise HTTPException(status_code=403, detail="Solo puedes ver versiones de tus propios archivos")

        versions = service.get_file_versions(db, file_id)

        return {
            "file_id": file_id,
            "current_version": file_upload.version,
            "versions": versions
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo versiones: {str(e)}")


@router.post("/{file_id}/versions/{version}/restore")
async def restore_file_version(
    file_id: int,
    version: int,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Restaurar una versión anterior del archivo"""
    try:
        service = FileManagementService()
        file_upload = service.get_by_id(db, file_id)

        if not file_upload:
            raise HTTPException(status_code=404, detail="Archivo no encontrado")

        # Verificar permisos
        if file_upload.uploaded_by != str(current_user.id):
            raise HTTPException(status_code=403, detail="Solo puedes restaurar versiones de tus propios archivos")

        success = service.restore_file_version(db, file_id, version)

        if success:
            return {"success": True, "message": f"Versión {version} restaurada exitosamente"}
        else:
            raise HTTPException(status_code=404, detail="Versión no encontrada")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error restaurando versión: {str(e)}")


# === COMPARTIR Y PERMISOS ===

@router.post("/{file_id}/share")
async def share_file(
    file_id: int,
    share_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Compartir archivo con otros usuarios"""
    try:
        service = FileManagementService()
        file_upload = service.get_by_id(db, file_id)

        if not file_upload:
            raise HTTPException(status_code=404, detail="Archivo no encontrado")

        # Verificar permisos
        if file_upload.uploaded_by != str(current_user.id):
            raise HTTPException(status_code=403, detail="Solo puedes compartir tus propios archivos")

        shared_with = share_data.get("shared_with", 0)  # 0 = público
        permissions = share_data.get("permissions", ["read"])
        expires_at = share_data.get("expires_at")

        success = service.share_file(
            db=db,
            file_id=file_id,
            shared_with_user_id=shared_with,
            permissions=permissions,
            expires_at=expires_at
        )

        if success:
            return {"success": True, "message": "Archivo compartido exitosamente"}
        else:
            raise HTTPException(status_code=500, detail="Error compartiendo archivo")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error compartiendo archivo: {str(e)}")


@router.get("/shared/list")
async def get_shared_files(
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Obtener archivos compartidos conmigo"""
    try:
        service = FileManagementService()
        shared_files = service.get_shared_files(db, str(current_user.id))

        return {
            "shared_files": [
                {
                    "id": file.id,
                    "filename": file.filename,
                    "file_size": file.file_size,
                    "file_type": file.file_type.value if file.file_type else None,
                    "uploaded_by": file.uploaded_by,
                    "shared_at": file.updated_at.isoformat()
                } for file in shared_files
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo archivos compartidos: {str(e)}")


# === ESTADÍSTICAS Y REPORTES ===

@router.get("/stats/overview")
async def get_file_statistics(
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas de archivos"""
    try:
        service = FileManagementService()
        stats = service.get_file_statistics(db)

        return {
            "success": True,
            "statistics": stats
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")


# === MANTENIMIENTO ===

@router.post("/maintenance/cleanup")
async def cleanup_old_files(
    days_old: int = Query(90, ge=30, le=365),
    dry_run: bool = Query(True, description="Si es True, solo muestra qué se eliminaría"),
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Limpiar archivos antiguos (solo administradores)"""
    try:
        service = FileManagementService()
        result = service.cleanup_old_files(db, days_old, dry_run)

        return {
            "success": True,
            "message": f"Limpieza {'simulada' if dry_run else 'ejecutada'} exitosamente",
            "result": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en limpieza: {str(e)}")


@router.post("/maintenance/cleanup-temp")
async def cleanup_temp_files(
    hours_old: int = Query(24, ge=1, le=168),
    current_user: dict = Depends(get_current_admin_user)
):
    """Limpiar archivos temporales (solo administradores)"""
    try:
        service = FileManagementService()
        result = service.cleanup_temp_files(hours_old)

        return {
            "success": True,
            "message": "Limpieza de archivos temporales ejecutada exitosamente",
            "result": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error limpiando archivos temporales: {str(e)}")


# === ENDPOINT LEGACY PARA COMPATIBILIDAD ===

@router.get("/legacy/list")
async def get_files_legacy(
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Endpoint legacy para compatibilidad"""
    try:
        service = FileManagementService()
        files, total = service.search_files(db=db, skip=0, limit=100)

        return {
            "files": [
                {
                    "id": file.id,
                    "filename": file.filename,
                    "size": file.file_size,
                    "type": file.file_type.value if file.file_type else None,
                    "uploaded_at": file.created_at.isoformat()
                } for file in files
            ],
            "total": total
        }

    except Exception as e:
        return {"files": [], "total": 0, "error": str(e)}
