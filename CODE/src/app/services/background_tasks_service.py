# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Servicio de Tareas en Background
Versión: 1.0.0
Fecha: 2026-01-08
Autor: Equipo de Desarrollo

Este servicio maneja tareas que no deben bloquear las operaciones CRUD principales,
como envío de SMS, emails y otras notificaciones.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from app.models.package import Package, PackageStatus
from app.models.notification import NotificationEvent, NotificationPriority
from app.database import SessionLocal
from app.config import settings

logger = logging.getLogger(__name__)


class BackgroundTasksService:
    """
    Servicio para ejecutar tareas en background sin bloquear operaciones CRUD
    """
    
    @staticmethod
    async def send_package_notifications(
        package_id: int,
        new_status: PackageStatus,
        changed_by: str = "system"
    ):
        """
        Enviar notificaciones (SMS y Email) para un cambio de estado de paquete.
        Esta función se ejecuta en background y no bloquea la operación principal.
        """
        db = SessionLocal()
        try:
            # Obtener el paquete con sus relaciones
            from sqlalchemy.orm import joinedload
            package = db.query(Package).options(
                joinedload(Package.customer)
            ).filter(Package.id == package_id).first()
            
            if not package:
                logger.warning(f"⚠️ [BG] Paquete {package_id} no encontrado para notificaciones")
                return
            
            # Enviar SMS
            await BackgroundTasksService._send_sms_notification(db, package, new_status, changed_by)
            
            # Enviar Email
            await BackgroundTasksService._send_email_notification(db, package, new_status, changed_by)
            
        except Exception as e:
            logger.error(f"❌ [BG] Error en notificaciones para paquete {package_id}: {str(e)}")
        finally:
            db.close()
    
    @staticmethod
    async def _send_sms_notification(
        db,
        package: Package,
        new_status: PackageStatus,
        changed_by: str
    ):
        """Enviar notificación SMS"""
        try:
            # Solo enviar SMS si el paquete tiene un cliente asociado
            if not package.customer_id or not package.customer:
                logger.debug(f"[BG-SMS] Paquete {package.id} sin cliente, omitiendo SMS")
                return
            
            customer_phone = package.customer.phone
            if not customer_phone:
                logger.debug(f"[BG-SMS] Cliente sin teléfono, omitiendo SMS")
                return
            
            # Mapear estados a eventos
            event_mapping = {
                PackageStatus.ANUNCIADO: NotificationEvent.PACKAGE_ANNOUNCED,
                PackageStatus.RECIBIDO: NotificationEvent.PACKAGE_RECEIVED,
                PackageStatus.ENTREGADO: NotificationEvent.PACKAGE_DELIVERED,
                PackageStatus.CANCELADO: NotificationEvent.PACKAGE_CANCELLED
            }
            
            event_type = event_mapping.get(new_status)
            if not event_type:
                return
            
            # Preparar variables
            variables = {
                "guide_number": package.tracking_number,
                "tracking_code": getattr(package, 'tracking_code', package.tracking_number),
                "customer_name": package.customer.full_name if package.customer else "Cliente",
                "package_type": package.package_type.value if package.package_type else "normal",
                "package_condition": package.package_condition.value if package.package_condition else "ok"
            }
            
            # Agregar timestamps
            if new_status == PackageStatus.RECIBIDO and package.received_at:
                variables["received_at"] = package.received_at.strftime("%d/%m/%Y %H:%M")
            elif new_status == PackageStatus.ENTREGADO and package.delivered_at:
                variables["delivered_at"] = package.delivered_at.strftime("%d/%m/%Y %H:%M")
            
            # Enviar SMS
            from app.services.sms_service import SMSService
            from app.schemas.notification import SMSByEventRequest
            
            sms_service = SMSService()
            await sms_service.send_sms_by_event(
                db=db,
                event_request=SMSByEventRequest(
                    event_type=event_type,
                    package_id=package.id,
                    customer_id=package.customer_id,
                    custom_variables=variables,
                    priority=NotificationPriority.MEDIA,
                    is_test=False
                )
            )
            logger.info(f"✅ [BG-SMS] SMS enviado para paquete {package.id} -> {new_status.value}")
            
        except Exception as e:
            logger.warning(f"⚠️ [BG-SMS] Error enviando SMS para paquete {package.id}: {str(e)}")
    
    @staticmethod
    async def _send_email_notification(
        db,
        package: Package,
        new_status: PackageStatus,
        changed_by: str
    ):
        """Enviar notificación por Email"""
        try:
            # Solo enviar email si el paquete tiene un cliente con email
            if not package.customer_id or not package.customer:
                logger.debug(f"[BG-EMAIL] Paquete {package.id} sin cliente, omitiendo email")
                return
            
            customer_email = package.customer.email if hasattr(package.customer, 'email') else None
            if not customer_email:
                logger.debug(f"[BG-EMAIL] Cliente sin email, omitiendo notificación")
                return
            
            # Mapear estados a eventos
            event_mapping = {
                PackageStatus.ANUNCIADO: NotificationEvent.PACKAGE_ANNOUNCED,
                PackageStatus.RECIBIDO: NotificationEvent.PACKAGE_RECEIVED,
                PackageStatus.ENTREGADO: NotificationEvent.PACKAGE_DELIVERED,
                PackageStatus.CANCELADO: NotificationEvent.PACKAGE_CANCELLED
            }
            
            event_type = event_mapping.get(new_status)
            if not event_type:
                return
            
            # Preparar variables
            full_name = package.customer.full_name if package.customer else "Cliente"
            first_name = full_name.split(" ")[0]
            consult_code = package.tracking_number
            tracking_base = settings.tracking_base_url.rstrip("/")
            tracking_url = f"{tracking_base}?auto_search={consult_code}"
            
            variables = {
                "first_name": first_name,
                "current_status": new_status.value if hasattr(new_status, "value") else str(new_status),
                "guide_number": package.guide_number or None,
                "consult_code": consult_code,
                "tracking_url": tracking_url,
            }
            
            # Enviar email
            from app.services.email_service import EmailService
            
            email_service = EmailService()
            await email_service.send_email_by_event(
                db=db,
                event_type=event_type,
                recipient=customer_email,
                variables=variables,
                package_id=package.id,
                customer_id=str(package.customer_id) if package.customer_id else None,
                priority=NotificationPriority.MEDIA,
                is_test=False
            )
            logger.info(f"✅ [BG-EMAIL] Email enviado para paquete {package.id} -> {new_status.value}")
            
        except Exception as e:
            logger.warning(f"⚠️ [BG-EMAIL] Error enviando email para paquete {package.id}: {str(e)}")
    
    @staticmethod
    def schedule_notification(
        package_id: int,
        new_status: PackageStatus,
        changed_by: str = "system"
    ):
        """
        Programar envío de notificaciones en background.
        Esta función retorna inmediatamente y las notificaciones se envían de forma asíncrona.
        """
        try:
            # Crear tarea asíncrona
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Si ya hay un loop corriendo, crear tarea
                asyncio.create_task(
                    BackgroundTasksService.send_package_notifications(
                        package_id, new_status, changed_by
                    )
                )
            else:
                # Si no hay loop, ejecutar de forma síncrona (fallback)
                asyncio.run(
                    BackgroundTasksService.send_package_notifications(
                        package_id, new_status, changed_by
                    )
                )
            logger.debug(f"📤 [BG] Notificaciones programadas para paquete {package_id}")
        except Exception as e:
            logger.warning(f"⚠️ [BG] Error programando notificaciones: {str(e)}")


# Instancia global para uso fácil
background_tasks = BackgroundTasksService()
