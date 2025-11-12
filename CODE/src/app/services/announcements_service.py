# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Servicio de Anuncios
Versión: 1.0.0
Fecha: 2025-09-21
Autor: Equipo de Desarrollo
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

# from app.models.announcement_new import Package  # Archivo eliminado
from app.models.customer import Customer
from app.models.package import Package
from app.schemas.announcements import (
    AnnouncementCreate, AnnouncementUpdate, AnnouncementResponse,
    AnnouncementListResponse, AnnouncementSearchRequest, AnnouncementStatsResponse
)
from .base import BaseService

class AnnouncementsService(BaseService[Package, AnnouncementCreate, AnnouncementUpdate]):
    """Servicio para gestión de anuncios de paquetes"""

    def __init__(self):
        super().__init__(Package)

    def create_announcement(self, db: Session, announcement_data: AnnouncementCreate, created_by_id: Optional[uuid.UUID] = None) -> Package:
        """Crear un nuevo anuncio"""
        # Generar tracking code único
        tracking_code = self._generate_tracking_code(db)

        announcement = Package(
            customer_name=announcement_data.customer_name.upper(),
            customer_phone=announcement_data.customer_phone,
            guide_number=announcement_data.guide_number.upper(),
            tracking_code=tracking_code,
            is_active=announcement_data.is_active,
            is_processed=announcement_data.is_processed,
            created_by_id=created_by_id
        )

        db.add(announcement)
        db.commit()
        db.refresh(announcement)
        return announcement

    def get_announcement_by_guide_number(self, db: Session, guide_number: str) -> Optional[Package]:
        """Obtener anuncio por número de guía"""
        return db.query(Package).filter(
            Package.guide_number == guide_number
        ).first()

    def get_announcement_by_tracking_code(self, db: Session, tracking_code: str) -> Optional[Package]:
        """Obtener anuncio por código de tracking"""
        return db.query(Package).filter(
            Package.tracking_number == tracking_code
        ).first()

    def search_announcements(self, db: Session, search_request: AnnouncementSearchRequest,
                           skip: int = 0, limit: int = 50) -> AnnouncementListResponse:
        """Buscar anuncios con filtros"""
        query = db.query(Package)

        # Aplicar filtros
        if search_request.query:
            search_term = f"%{search_request.query}%"
            query = query.filter(
                or_(
                    Package.guide_number.ilike(search_term),
                    Package.tracking_number.ilike(search_term),
                    Package.customer_name.ilike(search_term),
                    Package.customer_phone.ilike(search_term)
                )
            )

        if search_request.status:
            if search_request.status == "pending":
                query = query.filter(
                    and_(
                        Package.is_active == True,
                        Package.is_processed == False
                    )
                )
            elif search_request.status == "processed":
                query = query.filter(Package.is_processed == True)
            elif search_request.status == "cancelled":
                query = query.filter(Package.is_active == False)

        if search_request.date_from:
            query = query.filter(Package.created_at >= search_request.date_from)

        if search_request.date_to:
            query = query.filter(Package.created_at <= search_request.date_to)

        # Ordenar por fecha de creación descendente
        query = query.order_by(Package.created_at.desc())

        # Paginación
        total = query.count()
        announcements = query.offset(skip).limit(limit).all()

        # Convertir a respuestas
        announcement_responses = []
        for announcement in announcements:
            announcement_responses.append(AnnouncementResponse.model_validate(announcement))

        return AnnouncementListResponse(
            announcements=announcement_responses,
            total=total,
            skip=skip,
            limit=limit
        )

    def update_announcement_status(self, db: Session, announcement_id: uuid.UUID,
                                 is_processed: bool, processed_by_id: Optional[uuid.UUID] = None) -> Package:
        """Actualizar estado de procesamiento del anuncio"""
        announcement = self.get_by_id(db, announcement_id)
        if not announcement:
            raise ValueError("Anuncio no encontrado")

        announcement.is_processed = is_processed
        if is_processed:
            from app.utils.datetime_utils import get_colombia_now
            announcement.processed_at = get_colombia_now()

        db.commit()
        db.refresh(announcement)
        return announcement

    def get_announcement_stats(self, db: Session) -> AnnouncementStatsResponse:
        """Obtener estadísticas de anuncios"""
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())
        month_start = today_start.replace(day=1)

        # Totales
        total_announcements = db.query(func.count(Package.id)).scalar()

        # Por estado
        pending_count = db.query(func.count(Package.id)).filter(
            and_(
                Package.is_active == True,
                Package.is_processed == False
            )
        ).scalar()

        processed_count = db.query(func.count(Package.id)).filter(
            Package.is_processed == True
        ).scalar()

        cancelled_count = db.query(func.count(Package.id)).filter(
            Package.is_active == False
        ).scalar()

        # Por período
        today_count = db.query(func.count(Package.id)).filter(
            Package.created_at >= today_start
        ).scalar()

        this_week_count = db.query(func.count(Package.id)).filter(
            Package.created_at >= week_start
        ).scalar()

        this_month_count = db.query(func.count(Package.id)).filter(
            Package.created_at >= month_start
        ).scalar()

        return AnnouncementStatsResponse(
            total_announcements=total_announcements or 0,
            pending_count=pending_count or 0,
            processed_count=processed_count or 0,
            cancelled_count=cancelled_count or 0,
            today_count=today_count or 0,
            this_week_count=this_week_count or 0,
            this_month_count=this_month_count or 0
        )

    def _generate_tracking_code(self, db: Session) -> str:
        """Generar código de tracking único"""
        import random
        import string

        while True:
            # Generar código de 4 caracteres alfanuméricos
            # Excluye el número 0 y la letra O para evitar confusión
            allowed_chars = string.ascii_uppercase.replace('O', '') + string.digits.replace('0', '')
            tracking_code = ''.join(random.choices(allowed_chars, k=4))

            # Verificar que no exista
            existing = db.query(Package).filter(
                Package.tracking_number == tracking_code
            ).first()

            if not existing:
                return tracking_code