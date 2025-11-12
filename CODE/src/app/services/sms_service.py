# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Servicio SMS con Liwa.co
Versión: 2.0.0
Fecha: 2025-09-21
Autor: Equipo de Desarrollo
"""

import httpx
import json
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import uuid

from .base import BaseService
from app.models.notification import (
    Notification, SMSMessageTemplate, SMSConfiguration,
    NotificationType, NotificationStatus, NotificationEvent, NotificationPriority
)
from app.models.package import Package
# from app.models.announcement_new import PackageAnnouncementNew  # Archivo eliminado
from app.models.customer import Customer
from app.schemas.notification import (
    SMSSendRequest, SMSBulkSendRequest, SMSByEventRequest,
    SMSSendResponse, SMSBulkSendResponse, SMSTestRequest, SMSTestResponse
)
from app.utils.datetime_utils import get_colombia_now
from app.utils.exceptions import ValidationException, ExternalServiceException
from app.config import settings

class SMSService(BaseService[Notification, Any, Any]):
    """
    Servicio completo para envío de SMS con integración Liwa.co
    """

    def __init__(self):
        super().__init__(Notification)

    # ========================================
    # CONFIGURACIÓN Y AUTENTICACIÓN
    # ========================================

    def get_sms_config(self, db: Session) -> SMSConfiguration:
        """Obtiene la configuración SMS activa"""
        config = db.query(SMSConfiguration).filter(SMSConfiguration.is_active == True).first()
        if not config:
            # Crear configuración por defecto si no existe
            config = SMSConfiguration(
                provider="liwa",
                api_key=settings.liwa_api_key,
                account_id=settings.liwa_account,
                password=settings.liwa_password,
                auth_url=settings.liwa_auth_url or "https://api.liwa.co/v2/auth/login",
                api_url="https://api.liwa.co/v2/sms/send",
                default_sender="PAQUETES",
                cost_per_sms_cents=50  # 50 centavos por SMS
            )
            db.add(config)
            db.commit()
            db.refresh(config)
        return config

    async def authenticate_liwa(self, config: SMSConfiguration) -> str:
        """Autentica con Liwa.co y obtiene token"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = {
                    "account": config.account_id,
                    "password": config.password
                }

                response = await client.post(config.auth_url, json=payload)
                response.raise_for_status()

                data = response.json()
                if data.get("success") and data.get("token"):
                    return data["token"]
                else:
                    raise ExternalServiceException(f"Autenticación Liwa fallida: {data.get('message', 'Respuesta inválida')}")

        except httpx.HTTPStatusError as e:
            raise ExternalServiceException(f"Error HTTP en autenticación Liwa: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise ExternalServiceException(f"Error de conexión con Liwa: {str(e)}")

    # ========================================
    # ENVÍO DE SMS
    # ========================================

    async def send_sms(
        self,
        db: Session,
        recipient: str,
        message: str,
        event_type: NotificationEvent = NotificationEvent.CUSTOM_MESSAGE,
        priority: NotificationPriority = NotificationPriority.MEDIA,
        package_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        announcement_id: Optional[str] = None,
        is_test: bool = False
    ) -> SMSSendResponse:
        """Envía un SMS individual"""
        try:
            # Validar número de teléfono
            self._validate_phone_number(recipient)

            # Obtener configuración
            config = self.get_sms_config(db)

            if config.enable_test_mode or is_test:
                # Modo de prueba - simular envío
                return await self._send_test_sms(db, recipient, message, event_type, priority, package_id, customer_id, announcement_id)

            # Crear registro de notificación
            notification = Notification(
                notification_type=NotificationType.SMS,
                event_type=event_type,
                priority=priority,
                recipient=recipient,
                message=message,
                status=NotificationStatus.ABIERTO,
                package_id=package_id,
                customer_id=customer_id,
                announcement_id=announcement_id,
                is_test=is_test,
                cost_cents=config.cost_per_sms_cents
            )

            db.add(notification)
            db.commit()
            db.refresh(notification)

            # Enviar SMS real
            result = await self._send_liwa_sms(config, recipient, message)

            # Actualizar notificación
            if result["success"]:
                notification.mark_as_sent(result.get("message_id"), config.cost_per_sms_cents)
            else:
                notification.mark_as_failed(result.get("error", "Error desconocido"))

            db.commit()

            return SMSSendResponse(
                notification_id=notification.id,
                status="sent" if result["success"] else "failed",
                message=result.get("message", "SMS enviado exitosamente" if result["success"] else "Error al enviar SMS"),
                cost_cents=config.cost_per_sms_cents
            )

        except Exception as e:
            db.rollback()
            raise ExternalServiceException(f"Error al enviar SMS: {str(e)}")

    async def send_bulk_sms(
        self,
        db: Session,
        recipients: List[str],
        message: str,
        event_type: NotificationEvent = NotificationEvent.CUSTOM_MESSAGE,
        priority: NotificationPriority = NotificationPriority.MEDIA,
        is_test: bool = False
    ) -> SMSBulkSendResponse:
        """Envía SMS masivo"""
        sent_count = 0
        failed_count = 0
        total_cost = 0
        results = []

        for recipient in recipients:
            try:
                result = await self.send_sms(
                    db=db,
                    recipient=recipient,
                    message=message,
                    event_type=event_type,
                    priority=priority,
                    is_test=is_test
                )
                sent_count += 1
                total_cost += result.cost_cents
                results.append({
                    "recipient": recipient,
                    "status": "sent",
                    "notification_id": str(result.notification_id),
                    "cost_cents": result.cost_cents
                })
            except Exception as e:
                failed_count += 1
                results.append({
                    "recipient": recipient,
                    "status": "failed",
                    "error": str(e)
                })

        return SMSBulkSendResponse(
            sent_count=sent_count,
            failed_count=failed_count,
            total_cost_cents=total_cost,
            results=results
        )

    async def send_sms_by_event(
        self,
        db: Session,
        event_request: SMSByEventRequest
    ) -> SMSSendResponse:
        """Envía SMS basado en evento usando plantilla"""
        try:
            # Obtener plantilla
            template = self.get_template_by_event(db, event_request.event_type)
            if not template:
                raise ValidationException(f"No se encontró plantilla para el evento {event_request.event_type.value}")

            # Preparar variables
            variables = await self._prepare_event_variables(
                db,
                event_request.event_type,
                event_request.package_id,
                event_request.customer_id,
                event_request.announcement_id,
                event_request.custom_variables or {}
            )

            # Renderizar mensaje
            message = template.render_message(variables)

            # Determinar destinatario
            recipient = await self._get_event_recipient(
                db,
                event_request.event_type,
                event_request.package_id,
                event_request.customer_id,
                event_request.announcement_id
            )

            if not recipient:
                raise ValidationException("No se pudo determinar el destinatario del SMS")

            # Enviar SMS
            return await self.send_sms(
                db=db,
                recipient=recipient,
                message=message,
                event_type=event_request.event_type,
                priority=event_request.priority,
                package_id=str(event_request.package_id) if event_request.package_id else None,
                customer_id=str(event_request.customer_id) if event_request.customer_id else None,
                announcement_id=str(event_request.announcement_id) if event_request.announcement_id else None,
                is_test=event_request.is_test
            )

        except Exception as e:
            raise ExternalServiceException(f"Error al enviar SMS por evento: {str(e)}")

    # ========================================
    # PLANTILLAS
    # ========================================

    def get_template_by_event(self, db: Session, event_type: NotificationEvent, language: str = "es") -> Optional[SMSMessageTemplate]:
        """Obtiene plantilla por evento"""
        return db.query(SMSMessageTemplate).filter(
            SMSMessageTemplate.event_type == event_type,
            SMSMessageTemplate.language == language,
            SMSMessageTemplate.is_active == True
        ).order_by(SMSMessageTemplate.is_default.desc()).first()

    def create_default_templates(self, db: Session) -> List[SMSMessageTemplate]:
        """Crea plantillas por defecto para eventos comunes"""
        templates_data = [
            {
                "template_id": "package_announced",
                "name": "Paquete Anunciado",
                "event_type": NotificationEvent.PACKAGE_ANNOUNCED,
                "message_template": "PAQUETES EL CLUB: Su paquete con guía {guide_number} ha sido anunciado. Código: {tracking_code}. Más info: https://paquetes.com.co/seguimiento/{tracking_code}",
                "available_variables": json.dumps(["guide_number", "tracking_code", "customer_name"]),
                "is_default": True
            },
            {
                "template_id": "package_received",
                "name": "Paquete Recibido",
                "event_type": NotificationEvent.PACKAGE_RECEIVED,
                "message_template": "PAQUETES EL CLUB: Su paquete {guide_number} ha sido RECIBIDO en nuestras instalaciones. Código: {tracking_code}. Procesaremos su entrega pronto.",
                "available_variables": json.dumps(["guide_number", "tracking_code", "customer_name", "received_at"]),
                "is_default": True
            },
            {
                "template_id": "package_delivered",
                "name": "Paquete Entregado",
                "event_type": NotificationEvent.PACKAGE_DELIVERED,
                "message_template": "PAQUETES EL CLUB: ¡Su paquete {guide_number} ha sido ENTREGADO exitosamente! Código: {tracking_code}. Gracias por confiar en nosotros.",
                "available_variables": json.dumps(["guide_number", "tracking_code", "customer_name", "delivered_at"]),
                "is_default": True
            },
            {
                "template_id": "package_cancelled",
                "name": "Paquete Cancelado",
                "event_type": NotificationEvent.PACKAGE_CANCELLED,
                "message_template": "PAQUETES EL CLUB: Su paquete {guide_number} ha sido CANCELADO. Código: {tracking_code}. Contacte con nosotros para más información.",
                "available_variables": json.dumps(["guide_number", "tracking_code", "customer_name", "cancelled_at"]),
                "is_default": True
            },
            {
                "template_id": "payment_due",
                "name": "Pago Pendiente",
                "event_type": NotificationEvent.PAYMENT_DUE,
                "message_template": "PAQUETES EL CLUB: Tiene un pago pendiente por ${amount} COP para el paquete {guide_number}. Realice el pago para continuar con la entrega.",
                "available_variables": json.dumps(["guide_number", "tracking_code", "customer_name", "amount", "due_date"]),
                "is_default": True
            }
        ]

        templates = []
        for template_data in templates_data:
            # Verificar si ya existe
            existing = db.query(SMSMessageTemplate).filter(
                SMSMessageTemplate.template_id == template_data["template_id"]
            ).first()

            if not existing:
                template = SMSMessageTemplate(**template_data)
                db.add(template)
                templates.append(template)

        db.commit()
        return templates

    # ========================================
    # INTEGRACIÓN LIWA.CO
    # ========================================

    async def _send_liwa_sms(self, config: SMSConfiguration, recipient: str, message: str) -> Dict[str, Any]:
        """Envía SMS usando Liwa.co API"""
        try:
            # Autenticar
            token = await self.authenticate_liwa(config)

            # Preparar payload
            payload = {
                "to": recipient,
                "message": message,
                "from": config.default_sender
            }

            # Enviar SMS
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }

                response = await client.post(config.api_url, json=payload, headers=headers)
                response.raise_for_status()

                data = response.json()

                if data.get("success"):
                    return {
                        "success": True,
                        "message_id": data.get("message_id", str(uuid.uuid4())),
                        "message": "SMS enviado exitosamente"
                    }
                else:
                    return {
                        "success": False,
                        "error": data.get("message", "Error en respuesta de Liwa")
                    }

        except httpx.HTTPStatusError as e:
            error_data = e.response.json() if e.response.content else {}
            return {
                "success": False,
                "error": f"Error HTTP {e.response.status_code}: {error_data.get('message', str(e))}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error de conexión: {str(e)}"
            }

    async def _send_test_sms(
        self,
        db: Session,
        recipient: str,
        message: str,
        event_type: NotificationEvent,
        priority: NotificationPriority,
        package_id: Optional[str],
        customer_id: Optional[str],
        announcement_id: Optional[str]
    ) -> SMSSendResponse:
        """Simula envío de SMS para pruebas"""
        import asyncio
        await asyncio.sleep(0.1)  # Simular delay de red

        # Crear notificación de prueba
        notification = Notification(
            notification_type=NotificationType.SMS,
            event_type=event_type,
            priority=priority,
            recipient=recipient,
            message=f"[TEST] {message}",
            status=NotificationStatus.SENT,
            sent_at=get_colombia_now(),
            package_id=package_id,
            customer_id=customer_id,
            announcement_id=announcement_id,
            is_test=True,
            cost_cents=0  # SMS de prueba sin costo
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        return SMSSendResponse(
            notification_id=notification.id,
            status="sent",
            message="[TEST MODE] SMS simulado exitosamente",
            cost_cents=0
        )

    # ========================================
    # UTILIDADES
    # ========================================

    def _validate_phone_number(self, phone: str) -> bool:
        """Valida formato de número de teléfono colombiano"""
        # Remover espacios, guiones y paréntesis
        clean_phone = re.sub(r'[\s\-\(\)]', '', phone)

        # Verificar formato +57XXXXXXXXXX o 57XXXXXXXXXX o XXXXXXXXXX
        if clean_phone.startswith('+57'):
            clean_phone = clean_phone[3:]
        elif clean_phone.startswith('57'):
            clean_phone = clean_phone[2:]

        if not clean_phone.isdigit() or len(clean_phone) != 10:
            raise ValidationException("Número de teléfono inválido. Debe tener 10 dígitos para Colombia.")

        if not clean_phone.startswith(('3', '30', '31', '32', '35')):
            raise ValidationException("Número de teléfono debe comenzar con indicativo válido de Colombia (3xx).")

        return True

    async def _prepare_event_variables(
        self,
        db: Session,
        event_type: NotificationEvent,
        package_id: Optional[str],
        customer_id: Optional[str],
        announcement_id: Optional[str],
        custom_variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepara variables para plantilla basado en evento"""
        variables = dict(custom_variables)

        # Variables comunes
        variables.update({
            "company_name": "PAQUETES EL CLUB",
            "company_phone": "3334004007",
            "current_date": get_colombia_now().strftime("%d/%m/%Y"),
            "current_time": get_colombia_now().strftime("%H:%M")
        })

        # Variables específicas por evento
        if event_type == NotificationEvent.PACKAGE_ANNOUNCED and announcement_id:
            announcement = db.query(PackageAnnouncementNew).filter(PackageAnnouncementNew.id == announcement_id).first()
            if announcement:
                variables.update({
                    "guide_number": announcement.guide_number,
                    "tracking_code": announcement.tracking_code,
                    "customer_name": announcement.customer_name,
                    "announced_at": announcement.announced_at.strftime("%d/%m/%Y %H:%M") if announcement.announced_at else ""
                })

        elif event_type in [NotificationEvent.PACKAGE_RECEIVED, NotificationEvent.PACKAGE_DELIVERED] and package_id:
            package = db.query(Package).filter(Package.id == package_id).first()
            if package:
                variables.update({
                    "guide_number": package.tracking_number,
                    "customer_name": package.customer.full_name if package.customer else "",
                    "received_at": package.received_at.strftime("%d/%m/%Y %H:%M") if package.received_at else "",
                    "delivered_at": package.delivered_at.strftime("%d/%m/%Y %H:%M") if package.delivered_at else "",
                    "package_type": package.package_type.value if package.package_type else "",
                    "package_condition": package.package_condition.value if package.package_condition else ""
                })

        return variables

    async def _get_event_recipient(
        self,
        db: Session,
        event_type: NotificationEvent,
        package_id: Optional[str],
        customer_id: Optional[str],
        announcement_id: Optional[str]
    ) -> Optional[str]:
        """Determina el destinatario basado en el evento"""
        if customer_id:
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            return customer.phone if customer else None

        if package_id:
            package = db.query(Package).filter(Package.id == package_id).first()
            return package.customer.phone if package and package.customer else None

        if announcement_id:
            announcement = db.query(PackageAnnouncementNew).filter(PackageAnnouncementNew.id == announcement_id).first()
            return announcement.customer_phone if announcement else None

        return None

    # ========================================
    # TESTING Y DIAGNÓSTICO
    # ========================================

    async def test_sms_configuration(self, db: Session, test_request: SMSTestRequest) -> SMSTestResponse:
        """Prueba la configuración SMS"""
        try:
            config = self.get_sms_config(db)

            if not config.api_key or not config.account_id:
                return SMSTestResponse(
                    success=False,
                    message="Configuración incompleta: faltan credenciales de Liwa.co",
                    error_details="Verifique LIWA_API_KEY y LIWA_ACCOUNT en las variables de entorno"
                )

            # Enviar SMS de prueba
            result = await self.send_sms(
                db=db,
                recipient=test_request.recipient,
                message=test_request.message,
                is_test=True
            )

            # Actualizar configuración con resultado de prueba
            config.last_test_at = get_colombia_now()
            config.last_test_result = "SUCCESS" if result.status == "sent" else "FAILED"
            db.commit()

            return SMSTestResponse(
                success=result.status == "sent",
                message="Prueba exitosa" if result.status == "sent" else "Prueba fallida",
                notification_id=result.notification_id,
                provider_response={"status": result.status, "message": result.message}
            )

        except Exception as e:
            return SMSTestResponse(
                success=False,
                message=f"Error en prueba: {str(e)}",
                error_details=str(e)
            )

    # ========================================
    # REPORTES Y ESTADÍSTICAS
    # ========================================

    def get_sms_stats(self, db: Session, days: int = 30) -> Dict[str, Any]:
        """Obtiene estadísticas de SMS"""
        from sqlalchemy import func

        start_date = get_colombia_now() - timedelta(days=days)

        # Consultas de estadísticas
        total_sent = db.query(func.count(Notification.id)).filter(
            Notification.notification_type == NotificationType.SMS,
            Notification.created_at >= start_date
        ).scalar()

        total_delivered = db.query(func.count(Notification.id)).filter(
            Notification.notification_type == NotificationType.SMS,
            Notification.status == NotificationStatus.ENTREGADO,
            Notification.created_at >= start_date
        ).scalar()

        total_failed = db.query(func.count(Notification.id)).filter(
            Notification.notification_type == NotificationType.SMS,
            Notification.status == NotificationStatus.FAILED,
            Notification.created_at >= start_date
        ).scalar()

        total_cost = db.query(func.sum(Notification.cost_cents)).filter(
            Notification.notification_type == NotificationType.SMS,
            Notification.created_at >= start_date
        ).scalar() or 0

        return {
            "total_sent": total_sent,
            "total_delivered": total_delivered,
            "total_failed": total_failed,
            "total_cost_cents": total_cost,
            "delivery_rate": (total_delivered / total_sent * 100) if total_sent > 0 else 0,
            "average_cost_per_sms": (total_cost / total_sent) if total_sent > 0 else 0
        }