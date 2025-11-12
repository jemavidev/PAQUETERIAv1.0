# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Rutas de Notificaciones del Header
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.schemas.header_notification import (
    HeaderNotificationResponse, MarkAsReadRequest, MarkAsReadResponse
)
from app.services.header_notification_service import HeaderNotificationService
from app.services.message_service import MessageService
from app.models.package import Package, PackageStatus
from app.dependencies import get_current_active_user_from_cookies

router = APIRouter(
    tags=["Notificaciones del Header"],
    responses={404: {"description": "Notificación no encontrada"}}
)

header_notification_service = HeaderNotificationService()
message_service = MessageService()


@router.get("/notifications/header", response_model=HeaderNotificationResponse)
async def get_header_notifications(
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Obtener datos de notificaciones para el header"""
    try:
        # Obtener datos del badge
        badge_data = header_notification_service.get_notification_badge_data(
            db, current_user.id, current_user.role.value
        )
        
        # Obtener vista previa de mensajes recientes
        recent_messages = header_notification_service.get_recent_messages_preview(
            db, current_user.id, limit=3
        )
        
        return HeaderNotificationResponse(
            badge_data=badge_data,
            recent_messages=recent_messages,
            last_updated=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener notificaciones del header: {str(e)}"
        )


@router.get("/notifications/count")
async def get_notifications_count(
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Obtener solo el contador de notificaciones (para HTMX)"""
    try:
        badge_data = header_notification_service.get_notification_badge_data(
            db, current_user.id, current_user.role.value
        )
        
        return {
            "count": badge_data["total_notifications"],
            "show_badge": badge_data["show_badge"],
            "badge_text": badge_data["badge_text"],
            "badge_class": badge_data["badge_class"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener contador de notificaciones: {str(e)}"
        )


@router.post("/notifications/mark-read", response_model=MarkAsReadResponse)
async def mark_messages_as_read(
    request: MarkAsReadRequest,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Marcar mensajes como leídos"""
    try:
        if request.mark_all:
            # Marcar todos los mensajes como leídos
            success = header_notification_service.mark_all_as_read(db, current_user.id)
            if success:
                return MarkAsReadResponse(
                    success=True,
                    messages_updated=0,  # No sabemos cuántos se actualizaron
                    message="Todos los mensajes han sido marcados como leídos"
                )
            else:
                return MarkAsReadResponse(
                    success=False,
                    messages_updated=0,
                    message="No se pudieron marcar los mensajes como leídos"
                )
        else:
            # Marcar mensajes específicos
            if not request.message_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Debe proporcionar IDs de mensajes o marcar mark_all como True"
                )
            
            updated_count = 0
            for message_id in request.message_ids:
                try:
                    message_service.mark_as_read(db, message_id, current_user.id)
                    updated_count += 1
                except Exception as e:
                    print(f"Error marcando mensaje {message_id} como leído: {e}")
                    continue
            
            return MarkAsReadResponse(
                success=updated_count > 0,
                messages_updated=updated_count,
                message=f"Se marcaron {updated_count} mensajes como leídos"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al marcar mensajes como leídos: {str(e)}"
        )


@router.get("/packages/received/count")
async def get_received_packages_count(
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Obtener el contador de paquetes en estado RECIBIDO para mostrar en el header."""
    try:
        count = db.query(Package).filter(Package.status == PackageStatus.RECIBIDO).count()
        return {"count": count}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener contador de paquetes recibidos: {str(e)}"
        )


@router.get("/packages/announced/count")
async def get_announced_packages_count(
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Obtener el contador de paquetes en estado ANUNCIADO y anuncios no procesados para mostrar en el header."""
    try:
        from app.models.announcement_new import PackageAnnouncementNew
        
        # Contar paquetes en estado ANUNCIADO
        packages_announced = db.query(Package).filter(Package.status == PackageStatus.ANUNCIADO).count()
        
        # Contar anuncios no procesados y activos
        announcements_not_processed = db.query(PackageAnnouncementNew).filter(
            PackageAnnouncementNew.is_processed == False,
            PackageAnnouncementNew.is_active == True
        ).count()
        
        # Total: paquetes anunciados + anuncios no procesados
        total_count = packages_announced + announcements_not_processed
        
        return {"count": total_count}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener contador de paquetes anunciados: {str(e)}"
        )
