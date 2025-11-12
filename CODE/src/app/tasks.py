# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Tareas de Celery
Versión: 1.0.0
Fecha: 2025-09-21
Autor: Equipo de Desarrollo
"""

from .celery_app import celery_app
from .database import SessionLocal
from .services.report_service import ReportService
from .services.sms_service import SMSService
from .services.email_service import EmailService
from .services.file_management_service import FileManagementService
from .services.admin_service import AdminService
from .models.user import User
from .models.notification import Notification
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

# ========================================
# TAREAS DE REPORTES
# ========================================

@celery_app.task(bind=True, name="src.tasks.generate_report")
def generate_report(self, report_type: str, parameters: Dict[str, Any] = None, user_id: str = None):
    """Generar reporte de forma asíncrona"""
    logger.info(f"Iniciando generación de reporte: {report_type}")

    db = SessionLocal()
    try:
        report_service = ReportService()

        # Actualizar estado del reporte a "processing"
        if user_id:
            # Aquí iría la lógica para actualizar el estado en la BD
            pass

        # Generar el reporte
        result = report_service.generate_report(report_type, parameters)

        logger.info(f"Reporte {report_type} generado exitosamente")
        return result

    except Exception as e:
        logger.error(f"Error generando reporte {report_type}: {str(e)}")
        raise self.retry(countdown=60, max_retries=3, exc=e)
    finally:
        db.close()

@celery_app.task(bind=True, name="src.tasks.generate_bulk_reports")
def generate_bulk_reports(self, report_requests: List[Dict[str, Any]]):
    """Generar múltiples reportes en lote"""
    logger.info(f"Generando {len(report_requests)} reportes en lote")

    results = []
    for request in report_requests:
        try:
            result = generate_report.apply(args=[
                request["report_type"],
                request.get("parameters"),
                request.get("user_id")
            ]).get(timeout=300)  # 5 minutos timeout
            results.append({"success": True, "result": result})
        except Exception as e:
            logger.error(f"Error en reporte lote: {str(e)}")
            results.append({"success": False, "error": str(e)})

    return results

# ========================================
# TAREAS DE SMS
# ========================================

@celery_app.task(bind=True, name="src.tasks.send_bulk_sms")
def send_bulk_sms(self, sms_requests: List[Dict[str, Any]], user_id: str = None):
    """Enviar SMS masivos de forma asíncrona"""
    logger.info(f"Enviando {len(sms_requests)} SMS masivos")

    db = SessionLocal()
    try:
        sms_service = SMSService()

        results = []
        for sms_data in sms_requests:
            try:
                # Enviar SMS individual
                result = sms_service.send_sms(
                    recipient=sms_data["recipient"],
                    message=sms_data["message"],
                    sender_id=user_id
                )
                results.append({"success": True, "result": result})
            except Exception as e:
                logger.error(f"Error enviando SMS a {sms_data.get('recipient')}: {str(e)}")
                results.append({"success": False, "error": str(e), "recipient": sms_data.get("recipient")})

        logger.info(f"SMS masivos completados: {len([r for r in results if r['success']])} exitosos")
        return results

    except Exception as e:
        logger.error(f"Error en envío masivo de SMS: {str(e)}")
        raise self.retry(countdown=120, max_retries=2, exc=e)
    finally:
        db.close()

@celery_app.task(bind=True, name="src.tasks.send_sms_by_event")
def send_sms_by_event(self, event_type: str, entity_id: str, user_id: str = None):
    """Enviar SMS basado en eventos (anuncio creado, paquete recibido, etc.)"""
    logger.info(f"Enviando SMS por evento: {event_type} para entidad {entity_id}")

    db = SessionLocal()
    try:
        sms_service = SMSService()

        # Lógica para determinar el destinatario y mensaje basado en el evento
        if event_type == "announcement_created":
            # Enviar confirmación de anuncio
            result = sms_service.send_sms_by_event("announcement_created", entity_id)
        elif event_type == "package_received":
            # Notificar recepción de paquete
            result = sms_service.send_sms_by_event("package_received", entity_id)
        elif event_type == "package_delivered":
            # Confirmar entrega
            result = sms_service.send_sms_by_event("package_delivered", entity_id)
        else:
            raise ValueError(f"Evento no soportado: {event_type}")

        logger.info(f"SMS por evento {event_type} enviado exitosamente")
        return result

    except Exception as e:
        logger.error(f"Error enviando SMS por evento {event_type}: {str(e)}")
        raise self.retry(countdown=60, max_retries=3, exc=e)
    finally:
        db.close()

# ========================================
# TAREAS DE ARCHIVOS
# ========================================

@celery_app.task(bind=True, name="src.tasks.process_file_upload")
def process_file_upload(self, file_id: int, operations: List[str] = None):
    """Procesar archivo subido (generar thumbnails, convertir formatos, etc.)"""
    logger.info(f"Procesando archivo ID: {file_id}")

    db = SessionLocal()
    try:
        file_service = FileManagementService()

        # Operaciones a realizar
        operations = operations or ["thumbnail", "validate", "index"]

        results = {}
        for operation in operations:
            try:
                if operation == "thumbnail":
                    # Generar thumbnail
                    thumbnail_path = file_service._create_thumbnail(file_id)
                    results["thumbnail"] = thumbnail_path
                elif operation == "validate":
                    # Validar integridad
                    is_valid = file_service.validate_file_integrity(file_id)
                    results["validation"] = is_valid
                elif operation == "index":
                    # Indexar para búsqueda
                    file_service.index_file_for_search(file_id)
                    results["indexed"] = True
            except Exception as e:
                logger.error(f"Error en operación {operation} para archivo {file_id}: {str(e)}")
                results[operation] = {"error": str(e)}

        logger.info(f"Procesamiento de archivo {file_id} completado")
        return results

    except Exception as e:
        logger.error(f"Error procesando archivo {file_id}: {str(e)}")
        raise self.retry(countdown=30, max_retries=2, exc=e)
    finally:
        db.close()

@celery_app.task(bind=True, name="src.tasks.cleanup_temp_files")
def cleanup_temp_files(self, hours_old: int = 24):
    """Limpiar archivos temporales antiguos"""
    logger.info(f"Limpiando archivos temporales de más de {hours_old} horas")

    try:
        file_service = FileManagementService()
        result = file_service.cleanup_temp_files(hours_old)

        logger.info(f"Limpieza completada: {result.get('deleted_count', 0)} archivos eliminados")
        return result

    except Exception as e:
        logger.error(f"Error limpiando archivos temporales: {str(e)}")
        raise self.retry(countdown=3600, max_retries=3, exc=e)

# ========================================
# TAREAS DE MANTENIMIENTO
# ========================================

@celery_app.task(bind=True, name="src.tasks.cleanup_old_reports")
def cleanup_old_reports(self, days_old: int = 30):
    """Limpiar reportes antiguos"""
    logger.info(f"Limpiando reportes de más de {days_old} días")

    db = SessionLocal()
    try:
        admin_service = AdminService()
        result = admin_service.cleanup_old_reports(days_old)

        logger.info(f"Limpieza de reportes completada: {result.get('deleted_count', 0)} reportes eliminados")
        return result

    except Exception as e:
        logger.error(f"Error limpiando reportes antiguos: {str(e)}")
        raise self.retry(countdown=86400, max_retries=2, exc=e)
    finally:
        db.close()

@celery_app.task(bind=True, name="src.tasks.update_dashboard_metrics")
def update_dashboard_metrics(self):
    """Actualizar métricas del dashboard"""
    logger.info("Actualizando métricas del dashboard")

    db = SessionLocal()
    try:
        admin_service = AdminService()
        result = admin_service.update_dashboard_metrics()

        logger.info("Métricas del dashboard actualizadas exitosamente")
        return result

    except Exception as e:
        logger.error(f"Error actualizando métricas del dashboard: {str(e)}")
        raise self.retry(countdown=300, max_retries=3, exc=e)
    finally:
        db.close()

@celery_app.task(bind=True, name="src.tasks.send_daily_reminders")
def send_daily_reminders(self):
    """Enviar recordatorios diarios (ejemplo de tarea programada)"""
    logger.info("Enviando recordatorios diarios")

    db = SessionLocal()
    try:
        # Lógica para enviar recordatorios
        # Por ejemplo: paquetes sin recoger, mensajes sin responder, etc.
        reminder_count = 0

        # Aquí iría la lógica específica de recordatorios
        # ...

        logger.info(f"Recordatorios diarios enviados: {reminder_count}")
        return {"reminders_sent": reminder_count}

    except Exception as e:
        logger.error(f"Error enviando recordatorios diarios: {str(e)}")
        raise self.retry(countdown=3600, max_retries=2, exc=e)
    finally:
        db.close()

# ========================================
# TAREAS DE NOTIFICACIONES
# ========================================

@celery_app.task(bind=True, name="src.tasks.process_notifications_queue")
def process_notifications_queue(self, batch_size: int = 50):
    """Procesar cola de notificaciones pendientes"""
    logger.info(f"Procesando cola de notificaciones (batch: {batch_size})")

    db = SessionLocal()
    try:
        # Obtener notificaciones pendientes
        from .models.notification import NotificationStatus, NotificationType
        pending_notifications = db.query(Notification).filter(
            Notification.status == NotificationStatus.PENDING
        ).limit(batch_size).all()

        processed = 0
        for notification in pending_notifications:
            try:
                # Procesar notificación según tipo
                if notification.notification_type == NotificationType.EMAIL:
                    email_service = EmailService()
                    # Re-enviar email si está pendiente
                    # (implementación simplificada - normalmente se procesaría según el evento)
                    logger.info(f"Procesando email notification {notification.id}")
                elif notification.notification_type == NotificationType.SMS:
                    sms_service = SMSService()
                    logger.info(f"Procesando SMS notification {notification.id}")

                processed += 1

            except Exception as e:
                logger.error(f"Error procesando notificación {notification.id}: {str(e)}")
                notification.mark_as_failed(str(e))

        db.commit()

        logger.info(f"Procesamiento de notificaciones completado: {processed}/{len(pending_notifications)}")
        return {"processed": processed, "total": len(pending_notifications)}

    except Exception as e:
        logger.error(f"Error procesando cola de notificaciones: {str(e)}")
        db.rollback()
        raise self.retry(countdown=60, max_retries=3, exc=e)
    finally:
        db.close()

# ========================================
# TAREAS DE EMAIL
# ========================================

@celery_app.task(bind=True, name="src.tasks.send_email")
def send_email(self, recipient: str, subject: str, html_content: str, text_content: str = None, 
               event_type: str = "custom_message", package_id: int = None, customer_id: str = None):
    """Enviar email de forma asíncrona"""
    import asyncio
    logger.info(f"Enviando email a {recipient}: {subject}")

    db = SessionLocal()
    try:
        from .models.notification import NotificationEvent, NotificationPriority
        email_service = EmailService()
        
        event_enum = NotificationEvent[event_type.upper()] if hasattr(NotificationEvent, event_type.upper()) else NotificationEvent.CUSTOM_MESSAGE
        
        # Celery no soporta async directamente, usar asyncio.run
        result = asyncio.run(email_service.send_email(
            db=db,
            recipient=recipient,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            event_type=event_enum,
            priority=NotificationPriority.MEDIA,
            package_id=package_id,
            customer_id=customer_id
        ))
        
        logger.info(f"Email enviado exitosamente: {result.get('notification_id')}")
        return result

    except Exception as e:
        logger.error(f"Error enviando email a {recipient}: {str(e)}")
        raise self.retry(countdown=60, max_retries=3, exc=e)
    finally:
        db.close()

@celery_app.task(bind=True, name="src.tasks.send_bulk_emails")
def send_bulk_emails(self, email_requests: List[Dict[str, Any]], user_id: str = None):
    """Enviar emails masivos de forma asíncrona"""
    logger.info(f"Enviando {len(email_requests)} emails masivos")

    db = SessionLocal()
    try:
        email_service = EmailService()
        results = []

        import asyncio
        for request in email_requests:
            try:
                from .models.notification import NotificationEvent
                event_type = request.get("event_type", NotificationEvent.CUSTOM_MESSAGE)
                if isinstance(event_type, str):
                    event_type = NotificationEvent[event_type.upper()] if hasattr(NotificationEvent, event_type.upper()) else NotificationEvent.CUSTOM_MESSAGE
                
                result = asyncio.run(email_service.send_email(
                    db=db,
                    recipient=request["recipient"],
                    subject=request["subject"],
                    html_content=request["html_content"],
                    text_content=request.get("text_content"),
                    event_type=event_type,
                    package_id=request.get("package_id"),
                    customer_id=request.get("customer_id")
                ))
                results.append({"success": True, "recipient": request["recipient"], "result": result})
            except Exception as e:
                logger.error(f"Error enviando email a {request['recipient']}: {str(e)}")
                results.append({"success": False, "recipient": request["recipient"], "error": str(e)})

        logger.info(f"Envio masivo de emails completado: {len([r for r in results if r['success']])}/{len(results)}")
        return {"sent": len([r for r in results if r["success"]]), "failed": len([r for r in results if not r["success"]]), "results": results}

    except Exception as e:
        logger.error(f"Error en envío masivo de emails: {str(e)}")
        raise self.retry(countdown=300, max_retries=2, exc=e)
    finally:
        db.close()

@celery_app.task(bind=True, name="src.tasks.process_email_queue")
def process_email_queue(self, batch_size: int = 50):
    """Procesar cola de emails pendientes"""
    logger.info(f"Procesando cola de emails (batch: {batch_size})")

    db = SessionLocal()
    try:
        from .models.notification import NotificationStatus, NotificationType
        pending_emails = db.query(Notification).filter(
            Notification.notification_type == NotificationType.EMAIL,
            Notification.status == NotificationStatus.PENDING
        ).limit(batch_size).all()

        processed = 0
        email_service = EmailService()

        import asyncio
        for notification in pending_emails:
            try:
                # Re-intentar envío de email
                result = asyncio.run(email_service.send_email(
                    db=db,
                    recipient=notification.recipient,
                    subject=notification.subject or "Notificación",
                    html_content=notification.message,
                    event_type=notification.event_type,
                    package_id=notification.package_id,
                    customer_id=str(notification.customer_id) if notification.customer_id else None
                ))
                
                if result.get("success"):
                    processed += 1
            except Exception as e:
                logger.error(f"Error procesando email {notification.id}: {str(e)}")
                notification.mark_as_failed(str(e))

        db.commit()

        logger.info(f"Procesamiento de emails completado: {processed}/{len(pending_emails)}")
        return {"processed": processed, "total": len(pending_emails)}

    except Exception as e:
        logger.error(f"Error procesando cola de emails: {str(e)}")
        db.rollback()
        raise self.retry(countdown=60, max_retries=3, exc=e)
    finally:
        db.close()