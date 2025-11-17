# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Rutas de Anuncios
Versión: 1.0.0
Fecha: 2025-09-21
Autor: Equipo de Desarrollo
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID

from app.database import get_db
# from app.models.announcement_new import PackageAnnouncementNew  # Archivo eliminado
from app.models.user import User
from app.models.notification import NotificationEvent
from app.schemas.announcements import (
    AnnouncementCreate, AnnouncementUpdate, AnnouncementResponse,
    AnnouncementListResponse, AnnouncementSearchRequest, AnnouncementStatsResponse
)
from app.services.announcements_service import AnnouncementsService
from app.services.sms_service import SMSService
from app.services.email_service import EmailService
from app.models.customer import Customer
from app.dependencies import get_current_active_user, get_current_admin_user
from app.config import settings
from app.utils.phone_utils import normalize_phone

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/announcements",
    tags=["Anuncios"],
    responses={404: {"description": "Anuncio no encontrado"}}
)

announcements_service = AnnouncementsService()

# ========================================
# ENDPOINTS PÚBLICOS
# ========================================

@router.post("/", response_model=AnnouncementResponse, status_code=status.HTTP_201_CREATED)
async def create_announcement(
    announcement: AnnouncementCreate,
    db: Session = Depends(get_db)
):
    """Crear un nuevo anuncio de paquete (público)"""
    try:
        # Verificar que no exista el número de guía
        existing = announcements_service.get_announcement_by_guide_number(db, announcement.guide_number)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un anuncio con el número de guía: {announcement.guide_number}"
            )

        db_announcement = announcements_service.create_announcement(db, announcement)
        
        # Enviar SMS de confirmación
        try:
            sms_service = SMSService()
            await sms_service.send_sms_by_event(
                db=db,
                event_type=NotificationEvent.ANNOUNCEMENT,
                recipient=db_announcement.customer_phone,
                announcement_id=db_announcement.id
            )
        except Exception as sms_error:
            logger.warning(f"No se pudo enviar SMS para anuncio {db_announcement.id}: {sms_error}")
        
        # Enviar EMAIL de confirmación si el cliente existe y tiene email
        try:
            # Normalizar número de teléfono para búsqueda
            # El número del anuncio puede venir como "3002596319"
            # El número en la BD de clientes está como "+573002596319"
            normalized_announcement_phone = normalize_phone(db_announcement.customer_phone)
            
            logger.info(f"Buscando cliente para anuncio {db_announcement.id}: teléfono original='{db_announcement.customer_phone}', normalizado='{normalized_announcement_phone}'")
            
            # Buscar cliente por número de teléfono normalizado
            customer = db.query(Customer).filter(
                Customer.phone == normalized_announcement_phone
            ).first()
            
            # Si el cliente existe y tiene email, enviar notificación
            if customer and customer.email:
                logger.info(f"Cliente encontrado: {customer.full_name} (email: {customer.email})")
                
                email_service = EmailService()
                
                # Preparar variables para la plantilla
                first_name = customer.full_name.split(" ")[0] if customer.full_name else "Cliente"
                consult_code = db_announcement.tracking_code
                tracking_base = settings.tracking_base_url.rstrip("/")
                tracking_url = f"{tracking_base}?auto_search={consult_code}"
                
                variables = {
                    "first_name": first_name,
                    "current_status": "ANUNCIADO",
                    "guide_number": db_announcement.guide_number,
                    "consult_code": consult_code,
                    "tracking_url": tracking_url,
                }
                
                # Enviar email usando el evento PACKAGE_ANNOUNCED
                await email_service.send_email_by_event(
                    db=db,
                    event_type=NotificationEvent.PACKAGE_ANNOUNCED,
                    recipient=customer.email,  # CORREGIDO: era recipient_email, debe ser recipient
                    variables=variables
                )
                
                logger.info(f"✅ Email de anuncio enviado exitosamente a {customer.email} para anuncio {db_announcement.id}")
            elif customer and not customer.email:
                logger.info(f"Cliente encontrado ({customer.full_name}) pero no tiene email registrado")
            else:
                logger.info(f"No se encontró cliente con teléfono {normalized_announcement_phone}")
                
        except Exception as email_error:
            logger.warning(f"No se pudo enviar email para anuncio {db_announcement.id}: {email_error}")
        
        return AnnouncementResponse.model_validate(db_announcement)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear anuncio: {str(e)}"
        )

# ========================================
# ENDPOINTS PROTEGIDOS (ADMIN/OPERADOR)
# ========================================

@router.get("/", response_model=AnnouncementListResponse)
async def list_announcements(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search_query: Optional[str] = None,
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Listar anuncios con filtros (requiere autenticación)"""
    # Solo admin y operadores pueden ver anuncios
    if current_user.role.value not in ["ADMIN", "OPERADOR"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver anuncios"
        )

    try:
        search_request = AnnouncementSearchRequest(
            query=search_query,
            status=status_filter
        )
        return announcements_service.search_announcements(db, search_request, skip, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar anuncios: {str(e)}"
        )

@router.get("/{announcement_id}", response_model=AnnouncementResponse)
async def get_announcement(
    announcement_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener un anuncio específico"""
    # Solo admin y operadores pueden ver detalles de anuncios
    if current_user.role.value not in ["ADMIN", "OPERADOR"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver detalles de anuncios"
        )

    announcement = announcements_service.get_by_id(db, announcement_id)
    if not announcement:
        raise HTTPException(status_code=404, detail="Anuncio no encontrado")

    return AnnouncementResponse.model_validate(announcement)

@router.put("/{announcement_id}", response_model=AnnouncementResponse)
async def update_announcement(
    announcement_id: UUID,
    announcement_update: AnnouncementUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Actualizar un anuncio (solo administradores)"""
    try:
        updated_announcement = announcements_service.update(db, announcement_id, announcement_update)
        return AnnouncementResponse.model_validate(updated_announcement)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar anuncio: {str(e)}"
        )

@router.delete("/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_announcement(
    announcement_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Eliminar un anuncio (solo administradores)"""
    announcement = announcements_service.get_by_id(db, announcement_id)
    if not announcement:
        raise HTTPException(status_code=404, detail="Anuncio no encontrado")

    try:
        announcements_service.delete(db, announcement_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar anuncio: {str(e)}"
        )

# ========================================
# ENDPOINTS ESPECIALES
# ========================================

@router.post("/{announcement_id}/process", response_model=AnnouncementResponse)
async def process_announcement(
    announcement_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Marcar anuncio como procesado (convertir a paquete)"""
    # Solo admin y operadores pueden procesar anuncios
    if current_user.role.value not in ["ADMIN", "OPERADOR"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para procesar anuncios"
        )

    try:
        announcement = announcements_service.update_announcement_status(
            db, announcement_id, True, current_user.id
        )
        return AnnouncementResponse.model_validate(announcement)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar anuncio: {str(e)}"
        )

@router.get("/stats/overview", response_model=AnnouncementStatsResponse)
async def get_announcement_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas de anuncios"""
    # Solo admin y operadores pueden ver estadísticas
    if current_user.role.value not in ["ADMIN", "OPERADOR"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver estadísticas de anuncios"
        )

    try:
        return announcements_service.get_announcement_stats(db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )

@router.get("/search/guide/{guide_number}", response_model=AnnouncementResponse)
async def get_announcement_by_guide(
    guide_number: str,
    db: Session = Depends(get_db)
):
    """Buscar anuncio por número de guía (público para consultas)"""
    announcement = announcements_service.get_announcement_by_guide_number(db, guide_number)
    if not announcement:
        raise HTTPException(status_code=404, detail="Anuncio no encontrado")

    return AnnouncementResponse.model_validate(announcement)

@router.get("/search/tracking/{tracking_code}", response_model=AnnouncementResponse)
async def get_announcement_by_tracking(
    tracking_code: str,
    db: Session = Depends(get_db)
):
    """Buscar anuncio por código de tracking (público para consultas)"""
    announcement = announcements_service.get_announcement_by_tracking_code(db, tracking_code)
    if not announcement:
        raise HTTPException(status_code=404, detail="Anuncio no encontrado")

    return AnnouncementResponse.model_validate(announcement)
