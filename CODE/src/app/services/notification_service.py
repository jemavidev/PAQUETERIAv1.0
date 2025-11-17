# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Servicio de Notificaciones
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime
import logging

from .base import BaseService
from app.models.notification import Notification, NotificationStatus, NotificationType, NotificationPriority, NotificationEvent
from app.models.user import User
from app.schemas.notification import NotificationCreate, NotificationResponse
from app.config import settings

# Configurar logger
logger = logging.getLogger("notification_service")


class NotificationService(BaseService[Notification, NotificationCreate, dict]):
    """
    Servicio para gestión de notificaciones
    """

    def __init__(self):
        super().__init__(Notification)

    def create_notification(self, db: Session, notification_in: NotificationCreate) -> Notification:
        """Crear nueva notificación"""
        notification_data = notification_in.model_dump()
        db_notification = Notification(**notification_data)
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        return db_notification

    def send_notification(self, db: Session, notification_id: int) -> bool:
        """Marcar notificación como enviada"""
        notification = self.get_by_id(db, notification_id)
        if not notification:
            return False

        notification.status = NotificationStatus.SENT
        notification.sent_at = datetime.utcnow()
        db.commit()
        return True

    def mark_delivered(self, db: Session, notification_id: int) -> bool:
        """Marcar notificación como entregada"""
        notification = self.get_by_id(db, notification_id)
        if not notification:
            return False

        notification.status = NotificationStatus.DELIVERED
        notification.delivered_at = datetime.utcnow()
        db.commit()
        return True

    def get_notifications_by_package(self, db: Session, package_id: int) -> List[Notification]:
        """Obtener notificaciones de un paquete"""
        return db.query(Notification).filter(Notification.package_id == package_id).all()

    def get_pending_notifications(self, db: Session, skip: int = 0, limit: int = 50) -> List[Notification]:
        """Obtener notificaciones pendientes"""
        return db.query(Notification).filter(Notification.status == NotificationStatus.PENDING).offset(skip).limit(limit).all()

    def get_notification_stats(self, db: Session) -> dict:
        """Obtener estadísticas de notificaciones"""
        total_notifications = db.query(Notification).count()
        sent_count = db.query(Notification).filter(Notification.status == NotificationStatus.SENT).count()
        failed_count = db.query(Notification).filter(Notification.status == NotificationStatus.FAILED).count()
        delivered_count = db.query(Notification).filter(Notification.status == NotificationStatus.DELIVERED).count()

        # Por tipo
        sms_count = db.query(Notification).filter(Notification.type == NotificationType.SMS).count()
        email_count = db.query(Notification).filter(Notification.type == NotificationType.EMAIL).count()
        whatsapp_count = db.query(Notification).filter(Notification.type == NotificationType.WHATSAPP).count()

        return {
            "total_notifications": total_notifications,
            "sent_count": sent_count,
            "failed_count": failed_count,
            "delivered_count": delivered_count,
            "sms_count": sms_count,
            "email_count": email_count,
            "whatsapp_count": whatsapp_count
        }

    async def send_password_reset_email(self, db: Session, user: User, reset_token: str) -> bool:
        """
        Enviar email de restablecimiento de contraseña usando EmailService

        Args:
            db: Sesión de base de datos
            user: Usuario que solicita el reset
            reset_token: Token de reset generado

        Returns:
            bool: True si se envió exitosamente
        """
        try:
            from app.services.email_service import EmailService
            
            email_service = EmailService()
            
            # Determinar URL base según ambiente (NUNCA hardcodear URLs)
            base_url = (
                settings.production_url 
                if settings.environment == "production" 
                else settings.development_url
            )
            
            # Crear URL de reset (sin valores hardcodeados)
            reset_url = f"{base_url}/auth/reset-password?token={reset_token}"
            
            # Preparar variables para el template
            variables = {
                "user_name": user.full_name,
                "reset_url": reset_url,
                "email_subject": f"Restablecimiento de contraseña - {settings.company_display_name}"
            }
            
            # Renderizar template usando EmailService
            html_content, text_content, subject = await email_service._render_template(
                "password_reset.html",
                variables,
                NotificationEvent.CUSTOM_MESSAGE
            )
            
            # Enviar email usando EmailService
            result = await email_service.send_email(
                db=db,
                recipient=user.email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                event_type=NotificationEvent.CUSTOM_MESSAGE,
                priority=NotificationPriority.ALTA
            )
            
            return result.get("success", False)

        except Exception as e:
            import logging
            logger = logging.getLogger("notification_service")
            logger.error(f"Error enviando email de reset a {user.email}: {str(e)}")
            return False