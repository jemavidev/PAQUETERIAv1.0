# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Esquemas de Notificaciones del Header
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class MessagePreview(BaseModel):
    """Vista previa de un mensaje para el dropdown"""
    id: int
    subject: str
    content: str
    sender_name: str
    created_at: datetime
    priority: str
    message_type: str


class NotificationBadgeData(BaseModel):
    """Datos del badge de notificaciones"""
    unread_messages: int
    pending_messages: int
    total_notifications: int
    has_notifications: bool
    show_badge: bool
    badge_text: str
    badge_class: str


class HeaderNotificationResponse(BaseModel):
    """Respuesta completa de notificaciones del header"""
    badge_data: NotificationBadgeData
    recent_messages: List[MessagePreview]
    last_updated: datetime


class MarkAsReadRequest(BaseModel):
    """Request para marcar mensajes como leídos"""
    message_ids: Optional[List[int]] = None  # Si es None, marca todos
    mark_all: bool = False


class MarkAsReadResponse(BaseModel):
    """Respuesta al marcar mensajes como leídos"""
    success: bool
    messages_updated: int
    message: str
