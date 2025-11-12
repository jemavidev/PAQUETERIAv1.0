# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Servicio de Mensajes Expandido
Versión: 2.0.0
Fecha: 2025-09-21
Autor: Equipo de Desarrollo
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, or_, desc, text
from datetime import datetime, timedelta
import uuid

from .base import BaseService
from app.models.message import Message, MessageStatus, MessageType, MessagePriority
from app.models.user import User
from app.schemas.message import (
    MessageCreate, MessageUpdate, MessageResponse,
    MessageSearchFilters, MessageStats, MessageListResponse
)
from app.utils.datetime_utils import get_colombia_now
from sqlalchemy.orm import joinedload


class MessageService(BaseService[Message, MessageCreate, MessageUpdate]):
    """
    Servicio expandido para gestión completa de mensajes
    """

    def __init__(self):
        super().__init__(Message)

    def get_by_id(self, db: Session, id: int) -> Optional[Message]:
        """Obtener mensaje por ID con información del usuario que respondió"""
        return db.query(Message).options(
            joinedload(Message.answered_by_user)
        ).filter(Message.id == id).first()

    def create_message(self, db: Session, message_in: MessageCreate, sender_id: Optional[int] = None) -> Message:
        """Crear nuevo mensaje con validaciones completas"""
        message_data = message_in.model_dump()

        # Asignar sender_id si no viene en los datos
        if sender_id and not message_data.get('sender_id'):
            message_data['sender_id'] = sender_id

        # Generar tracking code único si no se proporciona
        if not message_data.get('tracking_code') and message_data.get('package_id'):
            message_data['tracking_code'] = f"MSG-{uuid.uuid4().hex[:8].upper()}"

        db_message = Message(**message_data)
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message

    def answer_message(self, db: Session, message_id: int, answer: str, answered_by: int) -> Message:
        """Responder mensaje con actualización completa de estado"""
        message = self.get_by_id(db, message_id)
        if not message:
            raise ValueError("Mensaje no encontrado")

        if message.status == MessageStatus.CERRADO:
            raise ValueError("No se puede responder un mensaje cerrado")

        message.answer = answer
        message.status = MessageStatus.RESPONDIDO
        message.answered_at = get_colombia_now()
        message.answered_by = answered_by
        message.is_read = True

        db.commit()
        db.refresh(message)
        return message

    def mark_as_read(self, db: Session, message_id: int, user_id: int) -> Message:
        """Marcar mensaje como leído"""
        message = self.get_by_id(db, message_id)
        if not message:
            raise ValueError("Mensaje no encontrado")

        # Verificar que el usuario sea el destinatario
        if message.recipient_id and message.recipient_id != user_id:
            raise ValueError("No tienes permisos para marcar este mensaje como leído")

        message.is_read = True
        if message.status == MessageStatus.ABIERTO:
            message.status = MessageStatus.LEIDO

        db.commit()
        db.refresh(message)
        return message

    def close_message(self, db: Session, message_id: int, closed_by: int) -> Message:
        """Cerrar mensaje"""
        message = self.get_by_id(db, message_id)
        if not message:
            raise ValueError("Mensaje no encontrado")

        message.status = MessageStatus.CERRADO
        message.is_read = True

        db.commit()
        db.refresh(message)
        return message

    def get_messages_by_package(self, db: Session, package_id: int) -> List[Message]:
        """Obtener mensajes de un paquete"""
        return db.query(Message).filter(Message.package_id == package_id).order_by(Message.created_at.desc()).all()

    def get_messages_by_customer(self, db: Session, customer_id: int) -> List[Message]:
        """Obtener mensajes de un cliente"""
        return db.query(Message).filter(Message.customer_id == customer_id).order_by(Message.created_at.desc()).all()

    def get_messages_by_user(self, db: Session, user_id: int, user_role: Optional[str] = None) -> List[Message]:
        """Obtener mensajes de un usuario (enviados o recibidos)"""
        query = db.query(Message).filter(
            or_(Message.sender_id == user_id, Message.recipient_id == user_id)
        )

        # Si es operador, mostrar mensajes según rol
        if user_role in ['OPERADOR', 'ADMIN']:
            # Los operadores ven todos los mensajes de clientes
            pass
        else:
            # Los usuarios normales solo ven sus propios mensajes
            query = query.filter(Message.sender_id == user_id)

        return query.order_by(Message.created_at.desc()).all()

    def search_messages(self, db: Session, filters: MessageSearchFilters, skip: int = 0, limit: int = 50) -> MessageListResponse:
        """Búsqueda avanzada de mensajes con filtros"""
        query = db.query(Message)

        # Aplicar filtros
        if filters.status:
            query = query.filter(Message.status == filters.status)
        if filters.message_type:
            query = query.filter(Message.message_type == filters.message_type)
        if filters.priority:
            query = query.filter(Message.priority == filters.priority)
        # TEMPORAL: Deshabilitar filtro de sender_id completamente para debug
        # if filters.sender_id is not None:
        #     query = query.filter(Message.sender_id == filters.sender_id)
        if filters.recipient_id:
            query = query.filter(Message.recipient_id == filters.recipient_id)
        if filters.package_id:
            query = query.filter(Message.package_id == filters.package_id)
        if filters.customer_id:
            query = query.filter(Message.customer_id == filters.customer_id)
        if filters.category:
            query = query.filter(Message.category == filters.category)
        if filters.is_read is not None:
            query = query.filter(Message.is_read == filters.is_read)
        if filters.date_from:
            query = query.filter(Message.created_at >= filters.date_from)
        if filters.date_to:
            query = query.filter(Message.created_at <= filters.date_to)
        if filters.search_text:
            search_term = f"%{filters.search_text}%"
            query = query.filter(
                or_(
                    Message.subject.ilike(search_term),
                    Message.content.ilike(search_term),
                    Message.answer.ilike(search_term),
                    Message.sender_name.ilike(search_term),
                    Message.sender_email.ilike(search_term),
                    Message.sender_phone.ilike(search_term),
                    Message.tracking_code.ilike(search_term),
                    Message.reference_number.ilike(search_term)
                )
            )

        # Obtener total
        total = query.count()

        # Aplicar paginación y ordenamiento
        messages = query.order_by(desc(Message.created_at)).offset(skip).limit(limit).all()

        # Calcular páginas
        page = (skip // limit) + 1
        total_pages = (total + limit - 1) // limit

        return MessageListResponse(
            messages=[MessageResponse.model_validate(msg) for msg in messages],
            total=total,
            page=page,
            page_size=limit,
            total_pages=total_pages
        )

    def get_pending_messages(self, db: Session, recipient_role: Optional[str] = None, skip: int = 0, limit: int = 50) -> List[Message]:
        """Obtener mensajes pendientes con filtros por rol"""
        query = db.query(Message).filter(Message.status == MessageStatus.ABIERTO)

        if recipient_role:
            query = query.filter(Message.recipient_role == recipient_role)

        return query.order_by(Message.priority.desc(), Message.created_at.asc()).offset(skip).limit(limit).all()

    def get_unread_messages(self, db: Session, user_id: int) -> List[Message]:
        """Obtener mensajes no leídos de un usuario"""
        return db.query(Message).filter(
            and_(
                Message.recipient_id == user_id,
                Message.is_read == False
            )
        ).order_by(desc(Message.created_at)).all()

    def get_message_thread(self, db: Session, package_id: Optional[int] = None, customer_id: Optional[int] = None) -> List[Message]:
        """Obtener hilo de conversación por paquete o cliente"""
        query = db.query(Message)

        if package_id:
            query = query.filter(Message.package_id == package_id)
        elif customer_id:
            query = query.filter(Message.customer_id == customer_id)
        else:
            raise ValueError("Debe proporcionar package_id o customer_id")

        return query.order_by(Message.created_at.asc()).all()

    def get_message_stats(self, db: Session) -> MessageStats:
        """Obtener estadísticas detalladas de mensajes"""
        # Estadísticas básicas
        total_messages = db.query(Message).count()
        pending_count = db.query(Message).filter(Message.status == MessageStatus.ABIERTO).count()
        read_count = db.query(Message).filter(Message.status == MessageStatus.LEIDO).count()
        answered_count = db.query(Message).filter(Message.status == MessageStatus.RESPONDIDO).count()
        closed_count = db.query(Message).filter(Message.status == MessageStatus.CERRADO).count()

        # Tiempo promedio de respuesta
        avg_response_time = db.query(
            func.avg(func.extract('epoch', Message.answered_at - Message.created_at))
        ).filter(
            and_(Message.status == MessageStatus.RESPONDIDO, Message.answered_at.isnot(None))
        ).scalar()

        # Estadísticas por tipo
        messages_by_type = db.query(
            Message.message_type,
            func.count(Message.id).label('count')
        ).group_by(Message.message_type).all()

        # Estadísticas por prioridad
        messages_by_priority = db.query(
            Message.priority,
            func.count(Message.id).label('count')
        ).group_by(Message.priority).all()

        # Estadísticas por estado
        messages_by_status = db.query(
            Message.status,
            func.count(Message.id).label('count')
        ).group_by(Message.status).all()

        # Mensajes por período
        now = get_colombia_now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())
        month_start = today_start.replace(day=1)

        messages_today = db.query(Message).filter(Message.created_at >= today_start).count()
        messages_this_week = db.query(Message).filter(Message.created_at >= week_start).count()
        messages_this_month = db.query(Message).filter(Message.created_at >= month_start).count()

        return MessageStats(
            total_messages=total_messages,
            pending_count=pending_count,
            read_count=read_count,
            answered_count=answered_count,
            closed_count=closed_count,
            average_response_time_hours=avg_response_time / 3600 if avg_response_time else None,
            messages_by_type=dict(messages_by_type),
            messages_by_priority=dict(messages_by_priority),
            messages_by_status=dict(messages_by_status),
            messages_today=messages_today,
            messages_this_week=messages_this_week,
            messages_this_month=messages_this_month
        )

    def bulk_update_status(self, db: Session, message_ids: List[int], status: MessageStatus, updated_by: int) -> int:
        """Actualizar estado de múltiples mensajes"""
        updated = db.query(Message).filter(Message.id.in_(message_ids)).update({
            "status": status,
            "updated_at": get_colombia_now()
        })
        db.commit()
        return updated

    def assign_message(self, db: Session, message_id: int, recipient_id: int, assigned_by: int) -> Message:
        """Asignar mensaje a un destinatario"""
        message = self.get_by_id(db, message_id)
        if not message:
            raise ValueError("Mensaje no encontrado")

        message.recipient_id = recipient_id
        message.updated_at = get_colombia_now()

        db.commit()
        db.refresh(message)
        return message

    def get_messages_by_priority(self, db: Session, priority: MessagePriority, limit: int = 20) -> List[Message]:
        """Obtener mensajes por prioridad"""
        return db.query(Message).filter(
            and_(
                Message.priority == priority,
                Message.status.in_([MessageStatus.ABIERTO, MessageStatus.LEIDO])
            )
        ).order_by(desc(Message.created_at)).limit(limit).all()