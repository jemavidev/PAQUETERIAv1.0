# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Servicio de Eventos de Paquete
Versión: 1.0.0
Fecha: 2025-10-26
Autor: Equipo de Desarrollo

Servicio para gestionar y consultar el historial completo de eventos de paquetes.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal

from app.models.package_event import PackageEvent, EventType
from app.models.package import Package
from app.models.announcement_new import PackageAnnouncementNew
from app.models.user import User
from app.schemas.package_event import (
    PackageEventCreate, PackageEventResponse, PackageEventListResponse,
    PackageEventFilter, PackageEventStats, PackageHistoryResponse
)
from app.utils.datetime_utils import get_colombia_now


class PackageEventService:
    """Servicio para gestionar eventos de paquetes"""
    
    @staticmethod
    def create_event(db: Session, event_data: PackageEventCreate) -> PackageEvent:
        """Crear un nuevo evento de paquete"""
        event = PackageEvent(
            package_id=event_data.package_id,
            announcement_id=event_data.announcement_id,
            event_type=event_data.event_type,
            tracking_number=event_data.tracking_number,
            guide_number=event_data.guide_number,
            access_code=event_data.access_code,
            tracking_code=event_data.tracking_code,
            status_before=event_data.status_before,
            status_after=event_data.status_after,
            package_type=event_data.package_type,
            package_condition=event_data.package_condition,
            posicion=event_data.posicion,
            customer_id=event_data.customer_id,
            customer_name=event_data.customer_name,
            customer_phone=event_data.customer_phone,
            customer_email=event_data.customer_email,
            base_fee=event_data.base_fee,
            storage_fee=event_data.storage_fee,
            storage_days=event_data.storage_days,
            total_amount=event_data.total_amount,
            payment_method=event_data.payment_method,
            payment_amount=event_data.payment_amount,
            payment_received=event_data.payment_received,
            operator_id=event_data.operator_id,
            operator_name=event_data.operator_name,
            operator_role=event_data.operator_role,
            file_ids=event_data.file_ids,
            observations=event_data.observations,
            cancellation_reason=event_data.cancellation_reason,
            additional_data=event_data.additional_data
        )
        
        db.add(event)
        db.commit()
        db.refresh(event)
        
        return event
    
    @staticmethod
    def get_event_by_id(db: Session, event_id: str) -> Optional[PackageEvent]:
        """Obtener un evento por su ID"""
        return db.query(PackageEvent).filter(PackageEvent.id == event_id).first()
    
    @staticmethod
    def get_package_history(db: Session, package_id: int) -> List[PackageEvent]:
        """Obtener el historial completo de un paquete ordenado cronológicamente"""
        return db.query(PackageEvent).filter(
            PackageEvent.package_id == package_id
        ).order_by(PackageEvent.event_timestamp.asc()).all()
    
    @staticmethod
    def get_package_history_paginated(
        db: Session, 
        package_id: int, 
        page: int = 1, 
        page_size: int = 50
    ) -> Tuple[List[PackageEvent], int]:
        """Obtener historial de paquete con paginación"""
        query = db.query(PackageEvent).filter(PackageEvent.package_id == package_id)
        
        total = query.count()
        
        events = query.order_by(
            desc(PackageEvent.event_timestamp)
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        return events, total
    
    @staticmethod
    def get_events_by_tracking_number(db: Session, tracking_number: str) -> List[PackageEvent]:
        """Obtener eventos por número de tracking"""
        return db.query(PackageEvent).filter(
            PackageEvent.tracking_number == tracking_number
        ).order_by(PackageEvent.event_timestamp.asc()).all()
    
    @staticmethod
    def get_events_by_guide_number(db: Session, guide_number: str) -> List[PackageEvent]:
        """Obtener eventos por número de guía"""
        return db.query(PackageEvent).filter(
            PackageEvent.guide_number == guide_number
        ).order_by(PackageEvent.event_timestamp.asc()).all()
    
    @staticmethod
    def get_events_by_tracking_code(db: Session, tracking_code: str) -> List[PackageEvent]:
        """Obtener eventos por código de consulta público"""
        return db.query(PackageEvent).filter(
            PackageEvent.tracking_code == tracking_code
        ).order_by(PackageEvent.event_timestamp.asc()).all()
    
    @staticmethod
    def get_events_by_customer_phone(db: Session, customer_phone: str) -> List[PackageEvent]:
        """Obtener eventos por teléfono del cliente"""
        return db.query(PackageEvent).filter(
            PackageEvent.customer_phone == customer_phone
        ).order_by(desc(PackageEvent.event_timestamp)).all()
    
    @staticmethod
    def get_events_by_operator(
        db: Session, 
        operator_id: int, 
        page: int = 1, 
        page_size: int = 50
    ) -> Tuple[List[PackageEvent], int]:
        """Obtener eventos realizados por un operador específico"""
        query = db.query(PackageEvent).filter(PackageEvent.operator_id == operator_id)
        
        total = query.count()
        
        events = query.order_by(
            desc(PackageEvent.event_timestamp)
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        return events, total
    
    @staticmethod
    def filter_events(db: Session, filters: PackageEventFilter) -> PackageEventListResponse:
        """Filtrar eventos con múltiples criterios"""
        query = db.query(PackageEvent)
        
        # Aplicar filtros
        if filters.package_id:
            query = query.filter(PackageEvent.package_id == filters.package_id)
        
        if filters.tracking_number:
            query = query.filter(PackageEvent.tracking_number.ilike(f"%{filters.tracking_number}%"))
        
        if filters.guide_number:
            query = query.filter(PackageEvent.guide_number.ilike(f"%{filters.guide_number}%"))
        
        if filters.tracking_code:
            query = query.filter(PackageEvent.tracking_code.ilike(f"%{filters.tracking_code}%"))
        
        if filters.event_type:
            query = query.filter(PackageEvent.event_type == filters.event_type)
        
        if filters.customer_phone:
            query = query.filter(PackageEvent.customer_phone.ilike(f"%{filters.customer_phone}%"))
        
        if filters.operator_id:
            query = query.filter(PackageEvent.operator_id == filters.operator_id)
        
        if filters.date_from:
            query = query.filter(PackageEvent.event_timestamp >= filters.date_from)
        
        if filters.date_to:
            query = query.filter(PackageEvent.event_timestamp <= filters.date_to)
        
        if filters.status:
            query = query.filter(PackageEvent.status_after == filters.status)
        
        # Contar total
        total = query.count()
        
        # Aplicar paginación
        events = query.order_by(
            desc(PackageEvent.event_timestamp)
        ).offset((filters.page - 1) * filters.page_size).limit(filters.page_size).all()
        
        # Convertir a esquemas de respuesta
        event_responses = [PackageEventResponse.model_validate(event) for event in events]
        
        return PackageEventListResponse(
            total=total,
            events=event_responses,
            page=filters.page,
            page_size=filters.page_size
        )
    
    @staticmethod
    def get_package_full_history(db: Session, package_id: int) -> PackageHistoryResponse:
        """Obtener el historial completo formateado de un paquete"""
        # Obtener paquete
        package = db.query(Package).filter(Package.id == package_id).first()
        if not package:
            raise ValueError(f"Paquete {package_id} no encontrado")
        
        # Obtener eventos
        events = PackageEventService.get_package_history(db, package_id)
        
        # Convertir a esquemas de respuesta
        timeline = [PackageEventResponse.model_validate(event) for event in events]
        
        return PackageHistoryResponse(
            package_id=package.id,
            tracking_number=package.tracking_number,
            guide_number=package.guide_number,
            current_status=package.status.value,
            timeline=timeline,
            total_events=len(timeline)
        )
    
    @staticmethod
    def get_events_statistics(db: Session, date_from: Optional[datetime] = None, date_to: Optional[datetime] = None) -> PackageEventStats:
        """Obtener estadísticas de eventos"""
        
        # Si no se especifica rango, usar el mes actual
        if not date_from:
            now = get_colombia_now()
            date_from = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if not date_to:
            date_to = get_colombia_now()
        
        # Total de eventos en el rango
        total_query = db.query(func.count(PackageEvent.id)).filter(
            and_(
                PackageEvent.event_timestamp >= date_from,
                PackageEvent.event_timestamp <= date_to
            )
        )
        total_events = total_query.scalar() or 0
        
        # Eventos por tipo
        events_by_type_query = db.query(
            PackageEvent.event_type,
            func.count(PackageEvent.id)
        ).filter(
            and_(
                PackageEvent.event_timestamp >= date_from,
                PackageEvent.event_timestamp <= date_to
            )
        ).group_by(PackageEvent.event_type).all()
        
        events_by_type = {event_type.value: count for event_type, count in events_by_type_query}
        
        # Eventos hoy
        today_start = get_colombia_now().replace(hour=0, minute=0, second=0, microsecond=0)
        events_today = db.query(func.count(PackageEvent.id)).filter(
            PackageEvent.event_timestamp >= today_start
        ).scalar() or 0
        
        # Eventos esta semana
        week_start = get_colombia_now() - timedelta(days=get_colombia_now().weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        events_this_week = db.query(func.count(PackageEvent.id)).filter(
            PackageEvent.event_timestamp >= week_start
        ).scalar() or 0
        
        # Eventos este mes
        month_start = get_colombia_now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        events_this_month = db.query(func.count(PackageEvent.id)).filter(
            PackageEvent.event_timestamp >= month_start
        ).scalar() or 0
        
        # Ingresos (solo eventos de ENTREGA con pago recibido)
        revenue_today = db.query(func.sum(PackageEvent.payment_amount)).filter(
            and_(
                PackageEvent.event_type == EventType.ENTREGA,
                PackageEvent.payment_received == True,
                PackageEvent.event_timestamp >= today_start
            )
        ).scalar() or Decimal('0.00')
        
        revenue_this_week = db.query(func.sum(PackageEvent.payment_amount)).filter(
            and_(
                PackageEvent.event_type == EventType.ENTREGA,
                PackageEvent.payment_received == True,
                PackageEvent.event_timestamp >= week_start
            )
        ).scalar() or Decimal('0.00')
        
        revenue_this_month = db.query(func.sum(PackageEvent.payment_amount)).filter(
            and_(
                PackageEvent.event_type == EventType.ENTREGA,
                PackageEvent.payment_received == True,
                PackageEvent.event_timestamp >= month_start
            )
        ).scalar() or Decimal('0.00')
        
        return PackageEventStats(
            total_events=total_events,
            events_by_type=events_by_type,
            events_today=events_today,
            events_this_week=events_this_week,
            events_this_month=events_this_month,
            revenue_today=revenue_today,
            revenue_this_week=revenue_this_week,
            revenue_this_month=revenue_this_month
        )
    
    @staticmethod
    def get_recent_events(db: Session, limit: int = 50) -> List[PackageEvent]:
        """Obtener los eventos más recientes"""
        return db.query(PackageEvent).order_by(
            desc(PackageEvent.event_timestamp)
        ).limit(limit).all()
    
    @staticmethod
    def get_events_by_date_range(
        db: Session, 
        date_from: datetime, 
        date_to: datetime,
        event_type: Optional[EventType] = None
    ) -> List[PackageEvent]:
        """Obtener eventos en un rango de fechas específico"""
        query = db.query(PackageEvent).filter(
            and_(
                PackageEvent.event_timestamp >= date_from,
                PackageEvent.event_timestamp <= date_to
            )
        )
        
        if event_type:
            query = query.filter(PackageEvent.event_type == event_type)
        
        return query.order_by(desc(PackageEvent.event_timestamp)).all()
    
    @staticmethod
    def search_events(db: Session, search_term: str, limit: int = 50) -> List[PackageEvent]:
        """Búsqueda general de eventos por múltiples campos"""
        search_pattern = f"%{search_term.upper()}%"
        
        return db.query(PackageEvent).filter(
            or_(
                PackageEvent.tracking_number.ilike(search_pattern),
                PackageEvent.guide_number.ilike(search_pattern),
                PackageEvent.tracking_code.ilike(search_pattern),
                PackageEvent.customer_name.ilike(search_pattern),
                PackageEvent.customer_phone.ilike(search_pattern),
                PackageEvent.access_code.ilike(search_pattern)
            )
        ).order_by(desc(PackageEvent.event_timestamp)).limit(limit).all()
    
    @staticmethod
    def get_delivery_events_with_payment(
        db: Session, 
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[PackageEvent]:
        """Obtener eventos de entrega con información de pago"""
        query = db.query(PackageEvent).filter(
            and_(
                PackageEvent.event_type == EventType.ENTREGA,
                PackageEvent.payment_received == True
            )
        )
        
        if date_from:
            query = query.filter(PackageEvent.event_timestamp >= date_from)
        
        if date_to:
            query = query.filter(PackageEvent.event_timestamp <= date_to)
        
        return query.order_by(desc(PackageEvent.event_timestamp)).all()
    
    @staticmethod
    def get_operator_activity_summary(db: Session, operator_id: int, date_from: datetime, date_to: datetime) -> Dict[str, Any]:
        """Obtener resumen de actividad de un operador"""
        
        # Total de eventos
        total_events = db.query(func.count(PackageEvent.id)).filter(
            and_(
                PackageEvent.operator_id == operator_id,
                PackageEvent.event_timestamp >= date_from,
                PackageEvent.event_timestamp <= date_to
            )
        ).scalar() or 0
        
        # Eventos por tipo
        events_by_type = db.query(
            PackageEvent.event_type,
            func.count(PackageEvent.id)
        ).filter(
            and_(
                PackageEvent.operator_id == operator_id,
                PackageEvent.event_timestamp >= date_from,
                PackageEvent.event_timestamp <= date_to
            )
        ).group_by(PackageEvent.event_type).all()
        
        # Total recaudado en entregas
        total_collected = db.query(func.sum(PackageEvent.payment_amount)).filter(
            and_(
                PackageEvent.operator_id == operator_id,
                PackageEvent.event_type == EventType.ENTREGA,
                PackageEvent.payment_received == True,
                PackageEvent.event_timestamp >= date_from,
                PackageEvent.event_timestamp <= date_to
            )
        ).scalar() or Decimal('0.00')
        
        # Obtener información del operador
        operator = db.query(User).filter(User.id == operator_id).first()
        operator_name = operator.username if operator else f"Operador {operator_id}"
        
        return {
            "operator_id": operator_id,
            "operator_name": operator_name,
            "total_events": total_events,
            "events_by_type": {event_type.value: count for event_type, count in events_by_type},
            "total_collected": float(total_collected),
            "period": {
                "from": date_from.isoformat(),
                "to": date_to.isoformat()
            }
        }


