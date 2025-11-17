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
                api_url="https://api.liwa.co/v2/sms/single",  # Endpoint correcto
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
                status=NotificationStatus.PENDING,
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
    # PLANTILLAS (UNIFICADAS - Similar a EmailService)
    # ========================================

    def get_template_by_event(self, db: Session, event_type: NotificationEvent, language: str = "es") -> Optional[SMSMessageTemplate]:
        """
        Obtiene plantilla por evento
        UNIFICADO: Usa plantilla única para cambios de estado de paquetes
        """
        # Mapear eventos a plantillas (unificación de estados en una sola plantilla)
        template_map = {
            NotificationEvent.PACKAGE_ANNOUNCED: "status_change_unified",
            NotificationEvent.PACKAGE_RECEIVED: "status_change_unified",
            NotificationEvent.PACKAGE_DELIVERED: "status_change_unified",
            NotificationEvent.PACKAGE_CANCELLED: "status_change_unified",
            NotificationEvent.PAYMENT_DUE: "payment_due",
            NotificationEvent.CUSTOM_MESSAGE: "custom_message"
        }

        template_id = template_map.get(event_type, "custom_message")

        return db.query(SMSMessageTemplate).filter(
            SMSMessageTemplate.template_id == template_id,
            SMSMessageTemplate.language == language,
            SMSMessageTemplate.is_active == True
        ).first()

    def create_default_templates(self, db: Session) -> List[SMSMessageTemplate]:
        """
        Crea plantillas por defecto UNIFICADAS
        Similar al patrón de EmailService con status_change.html
        """
        templates_data = [
            {
                "template_id": "status_change_unified",
                "name": "Cambio de Estado Unificado",
                "event_type": NotificationEvent.PACKAGE_RECEIVED,  # Evento base (se usa para todos los estados)
                "message_template": "PAQUETES: Su paquete {guide_number} está {status_text}. Código: {consult_code}. Info: {tracking_url}",
                "available_variables": json.dumps([
                    "guide_number", "consult_code", "tracking_code", "status_text", 
                    "customer_name", "tracking_url", "company_name", "company_phone"
                ]),
                "description": "Plantilla unificada para todos los cambios de estado de paquetes (anunciado, recibido, entregado, cancelado)",
                "is_default": True,
                "is_active": True
            },
            {
                "template_id": "payment_due",
                "name": "Recordatorio de Pago",
                "event_type": NotificationEvent.PAYMENT_DUE,
                "message_template": "PAQUETES: Tiene un pago pendiente de ${amount} COP para el paquete {guide_number}. Realice el pago para continuar con la entrega.",
                "available_variables": json.dumps([
                    "guide_number", "consult_code", "amount", "due_date", 
                    "customer_name", "company_phone"
                ]),
                "description": "Plantilla para recordatorios de pago pendiente",
                "is_default": True,
                "is_active": True
            },
            {
                "template_id": "custom_message",
                "name": "Mensaje Personalizado",
                "event_type": NotificationEvent.CUSTOM_MESSAGE,
                "message_template": "PAQUETES: {message}",
                "available_variables": json.dumps(["message", "customer_name", "company_phone"]),
                "description": "Plantilla genérica para mensajes personalizados",
                "is_default": True,
                "is_active": True
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
            else:
                # Actualizar plantilla existente para migrar al nuevo formato
                existing.message_template = template_data["message_template"]
                existing.available_variables = template_data["available_variables"]
                existing.description = template_data.get("description")
                templates.append(existing)

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

            # Preparar payload con formato correcto de Liwa.co
            # Asegurar que el número tenga código de país
            phone_number = recipient
            if not phone_number.startswith("57"):
                phone_number = f"57{phone_number}"
            
            payload = {
                "number": phone_number,
                "message": message,
                "type": 1  # Tipo 1 para SMS estándar
            }

            # Enviar SMS usando endpoint correcto /v2/sms/single
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {
                    "Authorization": f"Bearer {token}",
                    "API-KEY": config.api_key,  # Header API-KEY requerido
                    "Content-Type": "application/json"
                }

                # Usar endpoint correcto
                sms_url = config.api_url.replace("/sms/send", "/sms/single")
                
                response = await client.post(sms_url, json=payload, headers=headers)
                response.raise_for_status()

                data = response.json()

                if data.get("success"):
                    return {
                        "success": True,
                        "message_id": data.get("menssageId", str(uuid.uuid4())),  # Nota: "menssageId" con doble 's'
                        "message": data.get("message", "SMS enviado exitosamente")
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
        """
        Prepara variables para plantilla basado en evento
        UNIFICADO: Incluye status_text dinámico para plantilla unificada
        """
        variables = dict(custom_variables)

        # Variables comunes
        variables.update({
            "company_name": settings.company_display_name or "PAQUETES EL CLUB",
            "company_phone": settings.company_phone or "3334004007",
            "current_date": get_colombia_now().strftime("%d/%m/%Y"),
            "current_time": get_colombia_now().strftime("%H:%M")
        })

        # Mapeo de eventos a texto de estado (UNIFICADO)
        status_text_map = {
            NotificationEvent.PACKAGE_ANNOUNCED: "ANUNCIADO",
            NotificationEvent.PACKAGE_RECEIVED: "RECIBIDO en nuestras instalaciones",
            NotificationEvent.PACKAGE_DELIVERED: "ENTREGADO exitosamente",
            NotificationEvent.PACKAGE_CANCELLED: "CANCELADO"
        }

        # Agregar status_text para plantilla unificada
        variables["status_text"] = status_text_map.get(event_type, "en proceso")

        # Variables específicas por evento
        if event_type == NotificationEvent.PACKAGE_ANNOUNCED and announcement_id:
            # Obtener datos del anuncio
            from app.models.announcement_new import PackageAnnouncementNew
            announcement = db.query(PackageAnnouncementNew).filter(
                PackageAnnouncementNew.id == announcement_id
            ).first()
            if announcement:
                variables.update({
                    "guide_number": announcement.guide_number,
                    "consult_code": announcement.tracking_code,
                    "tracking_code": announcement.tracking_code,
                    "customer_name": announcement.customer_name,
                    "tracking_url": f"{settings.tracking_base_url or 'https://paquetes.com.co'}?auto_search={announcement.tracking_code}"
                })

        elif event_type in [NotificationEvent.PACKAGE_RECEIVED, NotificationEvent.PACKAGE_DELIVERED, NotificationEvent.PACKAGE_CANCELLED] and package_id:
            package = db.query(Package).filter(Package.id == package_id).first()
            if package:
                variables.update({
                    "guide_number": package.tracking_number,
                    "consult_code": getattr(package, 'consult_code', package.tracking_number),
                    "tracking_code": package.tracking_number,
                    "customer_name": package.customer.full_name if package.customer else "Cliente",
                    "received_at": package.received_at.strftime("%d/%m/%Y %H:%M") if hasattr(package, 'received_at') and package.received_at else "",
                    "delivered_at": package.delivered_at.strftime("%d/%m/%Y %H:%M") if hasattr(package, 'delivered_at') and package.delivered_at else "",
                    "package_type": package.package_type.value if hasattr(package, 'package_type') and package.package_type else "normal",
                    "package_condition": package.package_condition.value if hasattr(package, 'package_condition') and package.package_condition else "bueno",
                    "tracking_url": f"{settings.tracking_base_url or 'https://paquetes.com.co'}/seguimiento/{package.tracking_number}"
                })

        elif event_type == NotificationEvent.PAYMENT_DUE and package_id:
            package = db.query(Package).filter(Package.id == package_id).first()
            if package:
                variables.update({
                    "guide_number": package.tracking_number,
                    "consult_code": getattr(package, 'consult_code', package.tracking_number),
                    "customer_name": package.customer.full_name if package.customer else "Cliente",
                    "amount": custom_variables.get("amount", "0"),
                    "due_date": custom_variables.get("due_date", get_colombia_now().strftime("%d/%m/%Y"))
                })

        # Asegurar que siempre haya valores por defecto
        variables.setdefault("guide_number", "N/A")
        variables.setdefault("consult_code", "N/A")
        variables.setdefault("tracking_code", "N/A")
        variables.setdefault("customer_name", "Cliente")
        variables.setdefault("tracking_url", settings.tracking_base_url or "https://paquetes.com.co")

        return variables

    async def _get_event_recipient(
        self,
        db: Session,
        event_type: NotificationEvent,
        package_id: Optional[str],
        customer_id: Optional[str],
        announcement_id: Optional[str]
    ) -> Optional[str]:
        """
        Determina el destinatario basado en el evento
        Prioridad: customer_id > package_id > announcement_id
        """
        if customer_id:
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            if customer and hasattr(customer, 'phone'):
                return customer.phone

        if package_id:
            package = db.query(Package).filter(Package.id == package_id).first()
            if package and package.customer and hasattr(package.customer, 'phone'):
                return package.customer.phone

        # Obtener teléfono del anuncio si está disponible
        if announcement_id:
            from app.models.announcement_new import PackageAnnouncementNew
            announcement = db.query(PackageAnnouncementNew).filter(
                PackageAnnouncementNew.id == announcement_id
            ).first()
            if announcement and hasattr(announcement, 'customer_phone'):
                return announcement.customer_phone

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
            Notification.status == NotificationStatus.DELIVERED,
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