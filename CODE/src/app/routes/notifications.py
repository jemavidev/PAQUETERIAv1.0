# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Rutas de Notificaciones SMS
Versión: 2.0.0
Fecha: 2025-09-21
Autor: Equipo de Desarrollo
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
import io
import csv

from app.database import get_db
from app.models.notification import Notification, SMSMessageTemplate, SMSConfiguration
from app.schemas.notification import (
    NotificationResponse, NotificationListResponse, NotificationStatsResponse,
    SMSMessageTemplateCreate, SMSMessageTemplateUpdate, SMSMessageTemplateResponse,
    SMSMessageTemplateListResponse, SMSConfigurationUpdate, SMSConfigurationResponse,
    SMSSendRequest, SMSBulkSendRequest, SMSByEventRequest,
    SMSSendResponse, SMSBulkSendResponse, SMSTestRequest, SMSTestResponse,
    SMSReportRequest, SMSReportResponse
)
from app.services.sms_service import SMSService
from app.dependencies import get_current_active_user, get_current_admin_user

router = APIRouter(
    prefix="/notifications",
    tags=["Notificaciones SMS"],
    responses={404: {"description": "Notificación no encontrada"}}
)

# ========================================
# ENDPOINTS PARA GESTIÓN DE NOTIFICACIONES
# ========================================

@router.get("/", response_model=NotificationListResponse)
async def list_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    notification_type: Optional[str] = None,
    status: Optional[str] = None,
    event_type: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Listar notificaciones con filtros"""
    service = SMSService()

    # Construir filtros
    filters = {}
    if notification_type:
        filters["notification_type"] = notification_type
    if status:
        filters["status"] = status
    if event_type:
        filters["event_type"] = event_type

    notifications, total = service.get_filtered(
        db=db,
        skip=skip,
        limit=limit,
        filters=filters,
        order_by="created_at DESC"
    )

    return NotificationListResponse(
        notifications=[NotificationResponse.model_validate(n) for n in notifications],
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: UUID,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener notificación específica"""
    service = SMSService()
    notification = service.get_by_id(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    return NotificationResponse.model_validate(notification)

@router.post("/retry/{notification_id}")
async def retry_notification(
    notification_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Reintentar envío de notificación fallida"""
    service = SMSService()
    notification = service.get_by_id(db, notification_id)

    if not notification:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")

    if not notification.can_retry:
        raise HTTPException(status_code=400, detail="La notificación no puede ser reintentada")

    # Programar reintento en background
    background_tasks.add_task(service.retry_notification, db, notification_id)

    return {"message": "Reintento programado", "notification_id": str(notification_id)}

# ========================================
# ENDPOINTS PARA PLANTILLAS SMS
# ========================================

@router.get("/templates/", response_model=SMSMessageTemplateListResponse)
async def list_sms_templates(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Listar plantillas SMS"""
    service = SMSService()
    templates = db.query(SMSMessageTemplate).filter(SMSMessageTemplate.is_active == True).all()

    return SMSMessageTemplateListResponse(
        templates=[SMSMessageTemplateResponse.model_validate(t) for t in templates],
        total=len(templates)
    )

@router.post("/templates/", response_model=SMSMessageTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_sms_template(
    template: SMSMessageTemplateCreate,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Crear nueva plantilla SMS (solo administradores)"""
    # Verificar que no exista template_id duplicado
    existing = db.query(SMSMessageTemplate).filter(
        SMSMessageTemplate.template_id == template.template_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Ya existe una plantilla con este ID")

    template_data = template.dict()
    template_data["created_by_id"] = current_user.get("id")
    template_data["updated_by_id"] = current_user.get("id")

    new_template = SMSMessageTemplate(**template_data)
    db.add(new_template)
    db.commit()
    db.refresh(new_template)

    return SMSMessageTemplateResponse.model_validate(new_template)

@router.put("/templates/{template_id}", response_model=SMSMessageTemplateResponse)
async def update_sms_template(
    template_id: str,
    template_update: SMSMessageTemplateUpdate,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Actualizar plantilla SMS (solo administradores)"""
    template = db.query(SMSMessageTemplate).filter(
        SMSMessageTemplate.template_id == template_id
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")

    update_data = template_update.dict(exclude_unset=True)
    update_data["updated_by_id"] = current_user.get("id")

    for field, value in update_data.items():
        setattr(template, field, value)

    db.commit()
    db.refresh(template)

    return SMSMessageTemplateResponse.model_validate(template)

@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sms_template(
    template_id: str,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Eliminar plantilla SMS (solo administradores)"""
    template = db.query(SMSMessageTemplate).filter(
        SMSMessageTemplate.template_id == template_id
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")

    # Verificar que no sea la plantilla por defecto
    if template.is_default:
        raise HTTPException(status_code=400, detail="No se puede eliminar la plantilla por defecto")

    db.delete(template)
    db.commit()

# ========================================
# ENDPOINTS PARA CONFIGURACIÓN SMS
# ========================================

@router.get("/config/", response_model=SMSConfigurationResponse)
async def get_sms_config(
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Obtener configuración SMS (solo administradores)"""
    service = SMSService()
    config = service.get_sms_config(db)
    return SMSConfigurationResponse.model_validate(config)

@router.put("/config/", response_model=SMSConfigurationResponse)
async def update_sms_config(
    config_update: SMSConfigurationUpdate,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Actualizar configuración SMS (solo administradores)"""
    service = SMSService()
    config = service.get_sms_config(db)

    update_data = config_update.dict(exclude_unset=True)
    update_data["updated_by_id"] = current_user.get("id")

    for field, value in update_data.items():
        setattr(config, field, value)

    db.commit()
    db.refresh(config)

    return SMSConfigurationResponse.model_validate(config)

@router.post("/config/test/", response_model=SMSTestResponse)
async def test_sms_config(
    test_request: SMSTestRequest,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Probar configuración SMS (solo administradores)"""
    service = SMSService()
    return await service.test_sms_configuration(db, test_request)

# ========================================
# ENDPOINTS PARA ENVÍO DE SMS
# ========================================

@router.post("/send/", response_model=SMSSendResponse)
async def send_sms(
    sms_request: SMSSendRequest,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Enviar SMS individual"""
    service = SMSService()
    return await service.send_sms(
        db=db,
        recipient=sms_request.recipient,
        message=sms_request.message,
        priority=sms_request.priority,
        is_test=sms_request.is_test
    )

@router.post("/send/bulk/", response_model=SMSBulkSendResponse)
async def send_bulk_sms(
    bulk_request: SMSBulkSendRequest,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Enviar SMS masivo"""
    service = SMSService()
    return await service.send_bulk_sms(
        db=db,
        recipients=bulk_request.recipients,
        message=bulk_request.message,
        priority=bulk_request.priority,
        is_test=bulk_request.is_test
    )

@router.post("/send/event/", response_model=SMSSendResponse)
async def send_sms_by_event(
    event_request: SMSByEventRequest,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Enviar SMS basado en evento usando plantilla"""
    service = SMSService()
    return await service.send_sms_by_event(db, event_request)

# ========================================
# ENDPOINTS PARA REPORTES Y ESTADÍSTICAS
# ========================================

@router.get("/stats/", response_model=NotificationStatsResponse)
async def get_notification_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas de notificaciones"""
    service = SMSService()
    stats = service.get_sms_stats(db, days)

    # Obtener notificaciones recientes para fallos
    recent_failures = []
    from app.models.notification import NotificationStatus
    failed_notifications = db.query(Notification).filter(
        Notification.status == NotificationStatus.FAILED,
        Notification.created_at >= service.get_colombia_now() - timedelta(days=days)
    ).order_by(Notification.created_at.desc()).limit(10).all()

    for notification in failed_notifications:
        recent_failures.append({
            "id": str(notification.id),
            "recipient": notification.recipient,
            "error_message": notification.error_message,
            "created_at": notification.created_at.isoformat() if notification.created_at else None
        })

    return NotificationStatsResponse(
        total_notifications=stats["total_sent"],
        sent_notifications=stats["total_sent"],
        delivered_notifications=stats["total_delivered"],
        failed_notifications=stats["total_failed"],
        pending_notifications=0,  # TODO: calcular pendientes
        total_cost_cents=stats["total_cost_cents"],
        average_cost_per_sms=stats["average_cost_per_sms"],
        notifications_by_type={"sms": stats["total_sent"]},
        notifications_by_event={},  # TODO: implementar
        recent_failures=recent_failures
    )

@router.post("/reports/", response_model=SMSReportResponse)
async def generate_sms_report(
    report_request: SMSReportRequest,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generar reporte detallado de SMS"""
    # TODO: Implementar reporte detallado
    # Por ahora devolver estadísticas básicas
    service = SMSService()
    stats = service.get_sms_stats(db, 30)  # Últimos 30 días

    return SMSReportResponse(
        total_sent=stats["total_sent"],
        total_delivered=stats["total_delivered"],
        total_failed=stats["total_failed"],
        total_cost_cents=stats["total_cost_cents"],
        average_delivery_rate=stats["delivery_rate"],
        messages_by_day=[],  # TODO: implementar
        failures_by_reason={},  # TODO: implementar
        top_recipients=[]  # TODO: implementar
    )

# ========================================
# ENDPOINTS PARA EXPORTACIÓN
# ========================================

@router.get("/export/csv/")
async def export_notifications_csv(
    notification_type: Optional[str] = None,
    status: Optional[str] = None,
    days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Exportar notificaciones a CSV"""
    service = SMSService()

    # Calcular fecha de inicio
    from app.utils.datetime_utils import get_colombia_now
    start_date = get_colombia_now() - timedelta(days=days)

    # Obtener notificaciones
    filters = {"created_at__gte": start_date}
    if notification_type:
        filters["notification_type"] = notification_type
    if status:
        filters["status"] = status

    notifications, _ = service.get_filtered(
        db=db,
        filters=filters,
        limit=10000  # Límite razonable para exportación
    )

    # Crear CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Headers
    headers = [
        'id', 'type', 'event_type', 'recipient', 'recipient_name', 'message',
        'status', 'sent_at', 'delivered_at', 'error_message', 'cost_cents',
        'created_at', 'package_id', 'customer_id'
    ]
    writer.writerow(headers)

    # Data
    for notification in notifications:
        writer.writerow([
            str(notification.id),
            notification.notification_type.value,
            notification.event_type.value,
            notification.recipient,
            notification.recipient_name or '',
            notification.message[:100] + '...' if len(notification.message) > 100 else notification.message,
            notification.status.value,
            notification.sent_at.isoformat() if notification.sent_at else '',
            notification.delivered_at.isoformat() if notification.delivered_at else '',
            notification.error_message or '',
            notification.cost_cents,
            notification.created_at.isoformat() if notification.created_at else '',
            str(notification.package_id) if notification.package_id else '',
            str(notification.customer_id) if notification.customer_id else ''
        ])

    output.seek(0)

    return StreamingResponse(
        io.StringIO(output.getvalue()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=notifications.csv"}
    )

# ========================================
# ENDPOINTS PARA WEBHOOKS (CALLBACKS DE PROVEEDOR)
# ========================================

@router.post("/webhook/liwa/")
async def liwa_webhook(
    webhook_data: dict,
    db: Session = Depends(get_db)
):
    """Webhook para recibir actualizaciones de estado de Liwa.co"""
    try:
        # TODO: Implementar procesamiento de webhook
        # Actualizar estado de notificaciones basado en callbacks del proveedor

        message_id = webhook_data.get("message_id")
        status = webhook_data.get("status")
        delivered_at = webhook_data.get("delivered_at")

        if message_id:
            # Buscar notificación por provider_id
            notification = db.query(Notification).filter(
                Notification.provider_id == message_id
            ).first()

            if notification:
                if status == "delivered":
                    notification.mark_as_delivered()
                elif status == "failed":
                    notification.mark_as_failed("Error reportado por proveedor")

                db.commit()

        return {"received": True, "message": "Webhook procesado"}

    except Exception as e:
        # Log error but don't fail the webhook
        print(f"Error procesando webhook Liwa: {str(e)}")
        return {"received": False, "error": str(e)}

# ========================================
# ENDPOINTS PARA INICIALIZACIÓN
# ========================================

@router.post("/setup/templates/")
async def setup_default_templates(
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Crear plantillas por defecto (solo administradores)"""
    service = SMSService()
    templates = service.create_default_templates(db)

    return {
        "message": f"Se crearon {len(templates)} plantillas por defecto",
        "templates": [t.template_id for t in templates]
    }
