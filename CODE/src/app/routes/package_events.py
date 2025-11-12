# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Rutas de Eventos de Paquetes
Versión: 1.0.0
Fecha: 2025-10-26
Autor: Equipo de Desarrollo

Endpoints para consultar el historial completo de eventos de paquetes.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.models.package_event import EventType
from app.schemas.package_event import (
    PackageEventResponse, PackageEventListResponse, PackageEventFilter,
    PackageEventStats, PackageHistoryResponse
)
from app.services.package_event_service import PackageEventService
from app.dependencies import get_current_active_user
from app.utils.datetime_utils import get_colombia_now


router = APIRouter(
    prefix="/api/package-events",
    tags=["package-events"]
)

event_service = PackageEventService()


# ========================================
# ENDPOINTS DE CONSULTA DE EVENTOS
# ========================================

@router.get("/package/{package_id}", response_model=PackageHistoryResponse)
async def get_package_history(
    package_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener el historial completo de un paquete.
    
    Retorna todos los eventos del ciclo de vida del paquete ordenados cronológicamente.
    """
    try:
        history = event_service.get_package_full_history(db, package_id)
        return history
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener historial: {str(e)}"
        )


@router.get("/tracking/{tracking_number}", response_model=List[PackageEventResponse])
async def get_events_by_tracking(
    tracking_number: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener eventos por número de tracking.
    """
    try:
        events = event_service.get_events_by_tracking_number(db, tracking_number)
        return [PackageEventResponse.model_validate(event) for event in events]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener eventos: {str(e)}"
        )


@router.get("/guide/{guide_number}", response_model=List[PackageEventResponse])
async def get_events_by_guide(
    guide_number: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener eventos por número de guía del transportador.
    """
    try:
        events = event_service.get_events_by_guide_number(db, guide_number)
        return [PackageEventResponse.model_validate(event) for event in events]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener eventos: {str(e)}"
        )


@router.get("/code/{tracking_code}", response_model=List[PackageEventResponse])
async def get_events_by_code(
    tracking_code: str,
    db: Session = Depends(get_db)
):
    """
    Obtener eventos por código de consulta público (4 caracteres).
    
    Este endpoint NO requiere autenticación para permitir consultas públicas.
    """
    try:
        events = event_service.get_events_by_tracking_code(db, tracking_code.upper())
        if not events:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontraron eventos para el código: {tracking_code}"
            )
        return [PackageEventResponse.model_validate(event) for event in events]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener eventos: {str(e)}"
        )


@router.get("/customer/phone/{phone}", response_model=List[PackageEventResponse])
async def get_events_by_customer_phone(
    phone: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener eventos por teléfono del cliente.
    """
    try:
        events = event_service.get_events_by_customer_phone(db, phone)
        return [PackageEventResponse.model_validate(event) for event in events]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener eventos: {str(e)}"
        )


@router.get("/operator/{operator_id}", response_model=PackageEventListResponse)
async def get_operator_events(
    operator_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener eventos realizados por un operador específico.
    """
    try:
        # Verificar permisos (solo admin puede ver de otros operadores)
        if current_user.role.value not in ["ADMIN"] and current_user.id != operator_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para ver eventos de otros operadores"
            )
        
        events, total = event_service.get_events_by_operator(db, operator_id, page, page_size)
        event_responses = [PackageEventResponse.model_validate(event) for event in events]
        
        return PackageEventListResponse(
            total=total,
            events=event_responses,
            page=page,
            page_size=page_size
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener eventos: {str(e)}"
        )


@router.post("/filter", response_model=PackageEventListResponse)
async def filter_events(
    filters: PackageEventFilter,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Filtrar eventos con múltiples criterios.
    
    Permite búsqueda avanzada combinando:
    - package_id
    - tracking_number
    - guide_number
    - tracking_code
    - event_type
    - customer_phone
    - operator_id
    - date_from / date_to
    - status
    """
    try:
        result = event_service.filter_events(db, filters)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al filtrar eventos: {str(e)}"
        )


@router.get("/search", response_model=List[PackageEventResponse])
async def search_events(
    q: str = Query(..., min_length=3, description="Término de búsqueda"),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Búsqueda general de eventos por múltiples campos.
    
    Busca en: tracking_number, guide_number, tracking_code, customer_name, 
    customer_phone, access_code.
    """
    try:
        events = event_service.search_events(db, q, limit)
        return [PackageEventResponse.model_validate(event) for event in events]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en búsqueda: {str(e)}"
        )


@router.get("/recent", response_model=List[PackageEventResponse])
async def get_recent_events(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener los eventos más recientes del sistema.
    """
    try:
        events = event_service.get_recent_events(db, limit)
        return [PackageEventResponse.model_validate(event) for event in events]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener eventos: {str(e)}"
        )


# ========================================
# ENDPOINTS DE ESTADÍSTICAS
# ========================================

@router.get("/statistics", response_model=PackageEventStats)
async def get_event_statistics(
    date_from: Optional[datetime] = Query(None, description="Fecha inicial"),
    date_to: Optional[datetime] = Query(None, description="Fecha final"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas de eventos.
    
    Si no se especifica rango de fechas, retorna estadísticas del mes actual.
    Incluye:
    - Total de eventos por tipo
    - Eventos hoy, esta semana, este mes
    - Ingresos (solo entregas con pago recibido)
    """
    try:
        # Verificar permisos (solo admin y operadores)
        if current_user.role.value not in ["ADMIN", "OPERADOR"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para ver estadísticas"
            )
        
        stats = event_service.get_events_statistics(db, date_from, date_to)
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


@router.get("/deliveries", response_model=List[PackageEventResponse])
async def get_delivery_events(
    date_from: Optional[datetime] = Query(None, description="Fecha inicial"),
    date_to: Optional[datetime] = Query(None, description="Fecha final"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener eventos de entrega con información de pago.
    
    Útil para reportes financieros y cuadre de caja.
    """
    try:
        # Verificar permisos (solo admin y operadores)
        if current_user.role.value not in ["ADMIN", "OPERADOR"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para ver entregas"
            )
        
        events = event_service.get_delivery_events_with_payment(db, date_from, date_to)
        return [PackageEventResponse.model_validate(event) for event in events]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener entregas: {str(e)}"
        )


@router.get("/operator/{operator_id}/summary")
async def get_operator_summary(
    operator_id: int,
    date_from: datetime = Query(..., description="Fecha inicial"),
    date_to: datetime = Query(..., description="Fecha final"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener resumen de actividad de un operador en un período específico.
    
    Incluye:
    - Total de eventos realizados
    - Eventos por tipo
    - Total recaudado en entregas
    """
    try:
        # Verificar permisos
        if current_user.role.value not in ["ADMIN"] and current_user.id != operator_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para ver el resumen de otros operadores"
            )
        
        summary = event_service.get_operator_activity_summary(db, operator_id, date_from, date_to)
        return summary
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener resumen: {str(e)}"
        )


# ========================================
# ENDPOINT ESPECÍFICO POR ID
# ========================================

@router.get("/{event_id}", response_model=PackageEventResponse)
async def get_event_by_id(
    event_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener un evento específico por su ID.
    """
    try:
        event = event_service.get_event_by_id(db, str(event_id))
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evento {event_id} no encontrado"
            )
        return PackageEventResponse.model_validate(event)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener evento: {str(e)}"
        )


