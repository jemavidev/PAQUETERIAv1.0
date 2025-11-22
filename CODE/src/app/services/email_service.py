# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Servicio de Email Unificado
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo

Servicio completo para envío de emails siguiendo mejores prácticas.
"""

import smtplib
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from sqlalchemy.orm import Session
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from pathlib import Path

from .base import BaseService
from app.models.notification import (
    Notification, NotificationType, NotificationStatus, 
    NotificationEvent, NotificationPriority
)
from app.models.package import Package
from app.models.customer import Customer
from app.models.user import User
from app.config import settings
from app.utils.datetime_utils import get_colombia_now
from app.utils.exceptions import ValidationException, ExternalServiceException

# Configurar logger específico para email
email_logger = logging.getLogger("email_service")
email_logger.setLevel(logging.INFO)


class EmailService(BaseService[Notification, Any, Any]):
    """
    Servicio completo para envío de emails con SMTP
    Sigue el mismo patrón que SMSService para consistencia
    """

    def __init__(self):
        super().__init__(Notification)
        self._setup_template_environment()

    def _setup_template_environment(self):
        """Configurar ambiente Jinja2 para templates de email"""
        template_path = Path(__file__).parent.parent.parent / "templates" / "emails"
        if template_path.exists():
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(template_path)),
                autoescape=True,
                trim_blocks=True,
                lstrip_blocks=True
            )
        else:
            email_logger.warning(f"Directorio de templates no encontrado: {template_path}")
            self.jinja_env = None

    # ========================================
    # CONFIGURACIÓN Y VALIDACIÓN
    # ========================================

    def _validate_smtp_config(self) -> bool:
        """Valida que la configuración SMTP esté completa"""
        required = [
            settings.smtp_host,
            settings.smtp_user,
            settings.smtp_password,
            settings.smtp_from_email
        ]
        
        if not all(required):
            missing = []
            if not settings.smtp_host:
                missing.append("SMTP_HOST")
            if not settings.smtp_user:
                missing.append("SMTP_USER")
            if not settings.smtp_password:
                missing.append("SMTP_PASSWORD")
            if not settings.smtp_from_email:
                missing.append("SMTP_FROM_EMAIL")
            
            email_logger.error(f"Configuración SMTP incompleta: faltan {', '.join(missing)}")
            return False
        
        return True

    async def test_smtp_connection(self) -> Dict[str, Any]:
        """
        Prueba la conexión SMTP con el servidor
        Útil para validar configuración al iniciar la aplicación
        """
        if not self._validate_smtp_config():
            return {
                "success": False,
                "message": "Configuración SMTP incompleta",
                "error": "Faltan variables de entorno requeridas"
            }

        try:
            server = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10)
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.quit()
            
            email_logger.info("✅ Conexión SMTP exitosa")
            return {
                "success": True,
                "message": "Conexión SMTP exitosa",
                "server": settings.smtp_host,
                "port": settings.smtp_port
            }
        except smtplib.SMTPAuthenticationError as e:
            email_logger.error(f"❌ Error de autenticación SMTP: {str(e)}")
            return {
                "success": False,
                "message": "Error de autenticación SMTP",
                "error": str(e)
            }
        except smtplib.SMTPConnectError as e:
            email_logger.error(f"❌ Error de conexión SMTP: {str(e)}")
            return {
                "success": False,
                "message": "No se pudo conectar al servidor SMTP",
                "error": str(e)
            }
        except Exception as e:
            email_logger.error(f"❌ Error probando SMTP: {str(e)}")
            return {
                "success": False,
                "message": "Error inesperado al probar SMTP",
                "error": str(e)
            }

    # ========================================
    # ENVÍO DE EMAILS
    # ========================================

    async def send_email(
        self,
        db: Session,
        recipient: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        event_type: NotificationEvent = NotificationEvent.CUSTOM_MESSAGE,
        priority: NotificationPriority = NotificationPriority.MEDIA,
        package_id: Optional[int] = None,
        customer_id: Optional[str] = None,
        announcement_id: Optional[str] = None,
        is_test: bool = False
    ) -> Dict[str, Any]:
        """
        Envía un email individual
        
        Args:
            db: Sesión de base de datos
            recipient: Email del destinatario
            subject: Asunto del email
            html_content: Contenido HTML del email
            text_content: Contenido en texto plano (opcional)
            event_type: Tipo de evento de notificación
            priority: Prioridad de la notificación
            package_id: ID del paquete relacionado (opcional)
            customer_id: ID del cliente relacionado (opcional)
            announcement_id: ID del anuncio relacionado (opcional)
            is_test: Si es modo de prueba
            
        Returns:
            Dict con resultado del envío
        """
        try:
            # Validar configuración
            if not self._validate_smtp_config():
                raise ExternalServiceException("Configuración SMTP incompleta")

            # Validar email
            self._validate_email(recipient)

            # Crear registro de notificación
            notification = Notification(
                notification_type=NotificationType.EMAIL,
                event_type=event_type,
                priority=priority,
                recipient=recipient,
                recipient_name=None,  # Se puede obtener del customer si está disponible
                subject=subject,
                message=text_content or html_content[:500],  # Primeros 500 chars para preview
                status=NotificationStatus.PENDING,
                package_id=package_id,
                customer_id=customer_id,
                announcement_id=announcement_id,
                is_test=is_test,
                cost_cents=0  # Emails no tienen costo por ahora
            )

            db.add(notification)
            db.commit()
            db.refresh(notification)

            # Enviar email real
            if is_test:
                result = await self._send_test_email(db, notification, subject, html_content, text_content)
            else:
                result = await self._send_real_email(recipient, subject, html_content, text_content)

            # Actualizar notificación
            if result["success"]:
                notification.mark_as_sent()
                email_logger.info(f"✅ Email enviado exitosamente a {recipient} (ID: {notification.id})")
            else:
                notification.mark_as_failed(
                    result.get("error", "Error desconocido"),
                    result.get("error_code")
                )
                email_logger.error(f"❌ Error enviando email a {recipient}: {result.get('error')}")

            db.commit()

            return {
                "success": result["success"],
                "notification_id": notification.id,
                "status": "sent" if result["success"] else "failed",
                "message": result.get("message", ""),
                "error": result.get("error") if not result["success"] else None
            }

        except Exception as e:
            db.rollback()
            email_logger.error(f"❌ Error al enviar email: {str(e)}")
            raise ExternalServiceException(f"Error al enviar email: {str(e)}")

    async def send_email_by_event(
        self,
        db: Session,
        event_type: NotificationEvent,
        recipient: str,
        variables: Dict[str, Any],
        package_id: Optional[int] = None,
        customer_id: Optional[str] = None,
        announcement_id: Optional[str] = None,
        priority: NotificationPriority = NotificationPriority.MEDIA,
        is_test: bool = False
    ) -> Dict[str, Any]:
        """
        Envía email usando template basado en evento
        
        Args:
            db: Sesión de base de datos
            event_type: Tipo de evento (determina el template)
            recipient: Email del destinatario
            variables: Variables para renderizar el template
            package_id: ID del paquete (opcional)
            customer_id: ID del cliente (opcional)
            announcement_id: ID del anuncio (opcional)
            priority: Prioridad de la notificación
            is_test: Si es modo de prueba
            
        Returns:
            Dict con resultado del envío
        """
        try:
            # Mapear evento a template (unificación de estados en una sola plantilla)
            template_map = {
                NotificationEvent.PACKAGE_ANNOUNCED: "status_change.html",
                NotificationEvent.PACKAGE_RECEIVED: "status_change.html",
                NotificationEvent.PACKAGE_DELIVERED: "status_change.html",
                NotificationEvent.PACKAGE_CANCELLED: "status_change.html",
                NotificationEvent.PAYMENT_DUE: "payment_reminder.html",
            }

            template_name = template_map.get(event_type)
            if not template_name:
                # Usar template genérico si no hay específico
                template_name = "generic_notification.html"
                email_logger.warning(f"No hay template específico para {event_type}, usando genérico")

            # Renderizar template
            html_content, text_content, subject = await self._render_template(
                template_name, 
                variables,
                event_type
            )

            # Enviar email
            return await self.send_email(
                db=db,
                recipient=recipient,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                event_type=event_type,
                priority=priority,
                package_id=package_id,
                customer_id=customer_id,
                announcement_id=announcement_id,
                is_test=is_test
            )

        except Exception as e:
            email_logger.error(f"❌ Error enviando email por evento: {str(e)}")
            raise ExternalServiceException(f"Error al enviar email por evento: {str(e)}")

    async def send_bulk_emails(
        self,
        db: Session,
        recipients: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        event_type: NotificationEvent = NotificationEvent.CUSTOM_MESSAGE,
        priority: NotificationPriority = NotificationPriority.MEDIA,
        is_test: bool = False
    ) -> Dict[str, Any]:
        """
        Envía emails masivos (útil para notificaciones generales)
        
        Args:
            db: Sesión de base de datos
            recipients: Lista de emails
            subject: Asunto del email
            html_content: Contenido HTML
            text_content: Contenido texto plano (opcional)
            event_type: Tipo de evento
            priority: Prioridad
            is_test: Si es modo de prueba
            
        Returns:
            Dict con estadísticas del envío masivo
        """
        sent_count = 0
        failed_count = 0
        results = []

        for recipient in recipients:
            try:
                result = await self.send_email(
                    db=db,
                    recipient=recipient,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                    event_type=event_type,
                    priority=priority,
                    is_test=is_test
                )
                
                if result["success"]:
                    sent_count += 1
                else:
                    failed_count += 1
                
                results.append({
                    "recipient": recipient,
                    "success": result["success"],
                    "notification_id": result.get("notification_id"),
                    "error": result.get("error")
                })
            except Exception as e:
                failed_count += 1
                results.append({
                    "recipient": recipient,
                    "success": False,
                    "error": str(e)
                })
                email_logger.error(f"❌ Error enviando email a {recipient}: {str(e)}")

        email_logger.info(f"📧 Envío masivo completado: {sent_count} enviados, {failed_count} fallidos")
        
        return {
            "sent_count": sent_count,
            "failed_count": failed_count,
            "total": len(recipients),
            "results": results
        }

    # ========================================
    # TEMPLATES Y RENDERIZADO
    # ========================================

    async def _render_template(
        self, 
        template_name: str, 
        variables: Dict[str, Any],
        event_type: NotificationEvent
    ) -> Tuple[str, str, str]:
        """
        Renderiza un template de email
        
        Returns:
            Tuple[html_content, text_content, subject]
        """
        # Variables comunes para todos los templates
        common_vars = {
            "company_name": settings.company_display_name,
            "company_phone": settings.company_phone,
            "company_email": settings.company_email,
            "company_website": settings.company_website,
            "current_date": get_colombia_now().strftime("%d/%m/%Y"),
            "current_time": get_colombia_now().strftime("%H:%M"),
            # Enlace de ayuda estándar (usado en footers y textos de soporte)
            "help_url": f"{settings.production_url}/help"
        }
        
        # Combinar variables comunes con las específicas
        all_vars = {**common_vars, **variables}

        # Intentar renderizar template HTML
        try:
            if self.jinja_env:
                template = self.jinja_env.get_template(template_name)
                html_content = template.render(**all_vars)
            else:
                # Fallback: usar template básico si no hay ambiente Jinja2
                email_logger.warning("Usando template básico (Jinja2 no disponible)")
                html_content = self._generate_basic_html(**all_vars)
        except TemplateNotFound:
            email_logger.error(f"Template no encontrado: {template_name}, usando básico")
            html_content = self._generate_basic_html(**all_vars)
        except Exception as e:
            email_logger.error(f"Error renderizando template: {str(e)}, usando básico")
            html_content = self._generate_basic_html(**all_vars)

        # Generar texto plano desde HTML básico
        text_content = self._html_to_text(html_content)

        # Obtener subject desde variables o generar uno por defecto
        subject = all_vars.get("email_subject", self._generate_default_subject(event_type, all_vars))

        return html_content, text_content, subject

    def _generate_basic_html(self, **kwargs) -> str:
        """Genera HTML básico cuando no hay template disponible"""
        company_name = kwargs.get("company_name", "PAQUETES EL CLUB")
        message = kwargs.get("message", kwargs.get("content", "Notificación del sistema"))
        
        return f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{company_name}</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #1e40af;">{company_name}</h1>
                <div style="margin-top: 20px;">
                    {message}
                </div>
                <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; font-size: 12px; color: #6b7280;">
                    <p>Este es un mensaje automático generado por nuestro sistema.</p>
                    <p>&copy; 2025 {company_name}. Todos los derechos reservados.</p>
                </div>
            </div>
        </body>
        </html>
        """

    def _html_to_text(self, html: str) -> str:
        """Convierte HTML básico a texto plano (implementación simple)"""
        import re
        # Remover tags HTML básicos
        text = re.sub(r'<[^>]+>', '', html)
        # Limpiar espacios múltiples
        text = re.sub(r'\s+', ' ', text)
        # Limpiar saltos de línea
        text = text.replace('\n', ' ').strip()
        return text[:500]  # Limitar longitud

    def _generate_default_subject(self, event_type: NotificationEvent, variables: Dict[str, Any]) -> str:
        """Genera subject por defecto basado en el evento"""
        company_name = variables.get("company_name", "PAQUETES EL CLUB")
        
        # Para eventos de estado de paquete, usar un asunto unificado
        estado_subject = "ACTUALIZACION ESTADO DE PAQUETE"

        subjects = {
            NotificationEvent.PACKAGE_ANNOUNCED: estado_subject,
            NotificationEvent.PACKAGE_RECEIVED: estado_subject,
            NotificationEvent.PACKAGE_DELIVERED: estado_subject,
            NotificationEvent.PACKAGE_CANCELLED: estado_subject,
            NotificationEvent.PAYMENT_DUE: f"{company_name} - Recordatorio de Pago",
            NotificationEvent.CUSTOM_MESSAGE: f"{company_name} - Notificación"
        }
        
        return subjects.get(event_type, f"{company_name} - Notificación")

    # ========================================
    # ENVÍO REAL DE EMAILS (SMTP)
    # ========================================

    async def _send_real_email(
        self,
        recipient: str,
        subject: str,
        html_content: str,
        text_content: Optional[str]
    ) -> Dict[str, Any]:
        """Envía email real usando SMTP"""
        try:
            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = formataddr((settings.smtp_from_name, settings.smtp_from_email))
            msg['To'] = recipient
            msg['X-Mailer'] = 'PAQUETES EL CLUB v1.0'

            # Adjuntar contenido
            if text_content:
                part1 = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(part1)
            
            part2 = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(part2)

            # Enviar email
            server = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30)
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.smtp_from_email, recipient, msg.as_string())
            server.quit()

            return {
                "success": True,
                "message": "Email enviado exitosamente"
            }

        except smtplib.SMTPAuthenticationError as e:
            return {
                "success": False,
                "error": f"Error de autenticación SMTP: {str(e)}",
                "error_code": "SMTP_AUTH_ERROR"
            }
        except smtplib.SMTPRecipientsRefused as e:
            return {
                "success": False,
                "error": f"Destinatario rechazado: {str(e)}",
                "error_code": "RECIPIENT_REFUSED"
            }
        except smtplib.SMTPServerDisconnected as e:
            return {
                "success": False,
                "error": f"Servidor SMTP desconectado: {str(e)}",
                "error_code": "SMTP_DISCONNECTED"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error inesperado: {str(e)}",
                "error_code": "UNKNOWN_ERROR"
            }

    async def _send_test_email(
        self,
        db: Session,
        notification: Notification,
        subject: str,
        html_content: str,
        text_content: Optional[str]
    ) -> Dict[str, Any]:
        """Simula envío de email para pruebas"""
        import asyncio
        await asyncio.sleep(0.1)  # Simular delay de red

        email_logger.info(f"[TEST] Email simulado a {notification.recipient}: {subject}")
        
        return {
            "success": True,
            "message": "[TEST MODE] Email simulado exitosamente"
        }

    # ========================================
    # UTILIDADES
    # ========================================

    def _validate_email(self, email: str) -> bool:
        """Valida formato de email básico"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, email):
            raise ValidationException(f"Email inválido: {email}")
        
        return True

    async def _prepare_event_variables(
        self,
        db: Session,
        event_type: NotificationEvent,
        package_id: Optional[int],
        customer_id: Optional[str],
        announcement_id: Optional[str],
        custom_variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepara variables para template basado en evento"""
        variables = dict(custom_variables)

        # Variables comunes
        variables.update({
            "company_name": settings.company_display_name,
            "company_phone": settings.company_phone,
            "company_email": settings.company_email,
            "company_website": settings.company_website,
            "tracking_base_url": settings.tracking_base_url,
            "current_date": get_colombia_now().strftime("%d/%m/%Y"),
            "current_time": get_colombia_now().strftime("%H:%M")
        })

        # Variables específicas por evento
        if event_type == NotificationEvent.PACKAGE_RECEIVED and package_id:
            package = db.query(Package).filter(Package.id == package_id).first()
            if package:
                variables.update({
                    "guide_number": package.tracking_number,
                    "tracking_code": getattr(package, 'tracking_code', package.tracking_number),
                    "customer_name": package.customer.full_name if package.customer else "Cliente",
                    "received_at": package.received_at.strftime("%d/%m/%Y %H:%M") if package.received_at else "",
                    "package_type": package.package_type.value if package.package_type else "normal",
                    "tracking_url": f"{settings.tracking_base_url}?auto_search={package.tracking_number}"
                })

        elif event_type == NotificationEvent.PACKAGE_DELIVERED and package_id:
            package = db.query(Package).filter(Package.id == package_id).first()
            if package:
                variables.update({
                    "guide_number": package.tracking_number,
                    "tracking_code": getattr(package, 'tracking_code', package.tracking_number),
                    "customer_name": package.customer.full_name if package.customer else "Cliente",
                    "delivered_at": package.delivered_at.strftime("%d/%m/%Y %H:%M") if package.delivered_at else "",
                    "recipient_name": getattr(package, 'delivered_to', 'Cliente'),
                    "tracking_url": f"{settings.tracking_base_url}?auto_search={package.tracking_number}"
                })

        elif event_type == NotificationEvent.PACKAGE_CANCELLED and package_id:
            package = db.query(Package).filter(Package.id == package_id).first()
            if package:
                variables.update({
                    "guide_number": package.tracking_number,
                    "tracking_code": getattr(package, 'tracking_code', package.tracking_number),
                    "customer_name": package.customer.full_name if package.customer else "Cliente",
                    "cancelled_at": get_colombia_now().strftime("%d/%m/%Y %H:%M"),
                    "tracking_url": f"{settings.tracking_base_url}?auto_search={package.tracking_number}"
                })

        # Obtener email del destinatario desde customer si está disponible
        if customer_id:
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            if customer and hasattr(customer, 'email') and customer.email:
                variables["customer_email"] = customer.email

        return variables

    async def _get_event_recipient(
        self,
        db: Session,
        event_type: NotificationEvent,
        package_id: Optional[int],
        customer_id: Optional[str],
        announcement_id: Optional[str]
    ) -> Optional[str]:
        """Determina el email del destinatario basado en el evento"""
        if customer_id:
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            if customer and hasattr(customer, 'email'):
                return customer.email

        if package_id:
            package = db.query(Package).filter(Package.id == package_id).first()
            if package and package.customer and hasattr(package.customer, 'email'):
                return package.customer.email

        return None

    # ========================================
    # REPORTES Y ESTADÍSTICAS
    # ========================================

    def get_email_stats(self, db: Session, days: int = 30) -> Dict[str, Any]:
        """Obtiene estadísticas de emails enviados"""
        from sqlalchemy import func
        from datetime import timedelta

        start_date = get_colombia_now() - timedelta(days=days)

        total_sent = db.query(func.count(Notification.id)).filter(
            Notification.notification_type == NotificationType.EMAIL,
            Notification.created_at >= start_date
        ).scalar()

        total_delivered = db.query(func.count(Notification.id)).filter(
            Notification.notification_type == NotificationType.EMAIL,
            Notification.status == NotificationStatus.DELIVERED,
            Notification.created_at >= start_date
        ).scalar()

        total_failed = db.query(func.count(Notification.id)).filter(
            Notification.notification_type == NotificationType.EMAIL,
            Notification.status == NotificationStatus.FAILED,
            Notification.created_at >= start_date
        ).scalar()

        return {
            "total_sent": total_sent or 0,
            "total_delivered": total_delivered or 0,
            "total_failed": total_failed or 0,
            "delivery_rate": (total_delivered / total_sent * 100) if total_sent > 0 else 0,
            "period_days": days
        }

