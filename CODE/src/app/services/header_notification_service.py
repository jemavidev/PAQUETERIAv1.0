# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Servicio de Notificaciones del Header
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo
"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, or_
from datetime import datetime, timedelta

from app.models.message import Message, MessageStatus
from app.models.user import User
from app.utils.datetime_utils import get_colombia_now


class HeaderNotificationService:
    """
    Servicio para gestionar notificaciones del header (badges, contadores, etc.)
    """

    def __init__(self):
        pass

    def get_unread_messages_count(self, db: Session, user_id: int) -> int:
        """
        Obtener contador de mensajes no leídos para un usuario
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            
        Returns:
            int: Número de mensajes no leídos
        """
        try:
            count = db.query(Message).filter(
                and_(
                    Message.recipient_id == user_id,
                    Message.is_read == False,
                    Message.status.in_([
                        MessageStatus.ABIERTO,
                        MessageStatus.LEIDO
                    ])
                )
            ).count()
            
            return count
        except Exception as e:
            print(f"Error obteniendo contador de mensajes no leídos: {e}")
            return 0

    def get_pending_messages_count(self, db: Session, user_role: Optional[str] = None) -> int:
        """
        Obtener contador de mensajes pendientes (para operadores y admins)
        
        Args:
            db: Sesión de base de datos
            user_role: Rol del usuario (operator, admin, etc.)
            
        Returns:
            int: Número de mensajes pendientes
        """
        try:
            query = db.query(Message).filter(Message.status == MessageStatus.ABIERTO)
            
            # Si es operador, mostrar mensajes asignados a operadores (soportar variantes de casing)
            if user_role == 'OPERADOR':
                query = query.filter(
                    or_(
                        Message.recipient_role.in_(['OPERADOR', 'operator', 'OPERATOR']),
                        Message.recipient_role.is_(None)
                    )
                )
            elif user_role == 'ADMIN':
                # Los admins ven todos los mensajes pendientes
                pass
            else:
                # Usuarios normales no ven mensajes pendientes
                return 0
                
            count = query.count()
            return count
        except Exception as e:
            print(f"Error obteniendo contador de mensajes pendientes: {e}")
            return 0

    def get_notification_badge_data(self, db: Session, user_id: int, user_role: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtener datos completos para el badge de notificaciones del header
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            user_role: Rol del usuario
            
        Returns:
            Dict con datos del badge de notificaciones
        """
        try:
            # Contador de mensajes no leídos
            unread_count = self.get_unread_messages_count(db, user_id)
            
            # Contador de mensajes pendientes (solo para operadores y admins)
            pending_count = 0
            if user_role in ['OPERADOR', 'ADMIN']:
                pending_count = self.get_pending_messages_count(db, user_role)
            
            # Total de notificaciones
            total_notifications = unread_count + pending_count
            
            return {
                "unread_messages": unread_count,
                "pending_messages": pending_count,
                "total_notifications": total_notifications,
                "has_notifications": total_notifications > 0,
                "show_badge": total_notifications > 0,
                "badge_text": str(total_notifications) if total_notifications > 0 else "",
                "badge_class": self._get_badge_class(total_notifications)
            }
        except Exception as e:
            print(f"Error obteniendo datos del badge de notificaciones: {e}")
            return {
                "unread_messages": 0,
                "pending_messages": 0,
                "total_notifications": 0,
                "has_notifications": False,
                "show_badge": False,
                "badge_text": "",
                "badge_class": ""
            }

    def _get_badge_class(self, count: int) -> str:
        """
        Obtener clase CSS para el badge según el número de notificaciones
        
        Args:
            count: Número de notificaciones
            
        Returns:
            str: Clase CSS para el badge
        """
        if count == 0:
            return ""
        else:
            return "bg-papyrus-red text-white"

    def get_recent_messages_preview(self, db: Session, user_id: int, limit: int = 3) -> list:
        """
        Obtener vista previa de mensajes recientes para el dropdown
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            limit: Número máximo de mensajes a mostrar
            
        Returns:
            list: Lista de mensajes recientes
        """
        try:
            messages = db.query(Message).filter(
                and_(
                    Message.recipient_id == user_id,
                    Message.is_read == False
                )
            ).order_by(Message.created_at.desc()).limit(limit).all()
            
            return [
                {
                    "id": msg.id,
                    "subject": msg.subject,
                    "content": msg.content[:100] + "..." if len(msg.content) > 100 else msg.content,
                    "sender_name": msg.sender_name or "Sistema",
                    "created_at": msg.created_at,
                    "priority": msg.priority.value,
                    "message_type": msg.message_type.value
                }
                for msg in messages
            ]
        except Exception as e:
            print(f"Error obteniendo vista previa de mensajes: {e}")
            return []

    def mark_all_as_read(self, db: Session, user_id: int) -> bool:
        """
        Marcar todos los mensajes como leídos para un usuario
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            
        Returns:
            bool: True si se marcaron correctamente
        """
        try:
            updated = db.query(Message).filter(
                and_(
                    Message.recipient_id == user_id,
                    Message.is_read == False
                )
            ).update({
                "is_read": True,
                "status": MessageStatus.LEIDO,
                "updated_at": get_colombia_now()
            })
            
            db.commit()
            return updated > 0
        except Exception as e:
            print(f"Error marcando mensajes como leídos: {e}")
            db.rollback()
            return False
