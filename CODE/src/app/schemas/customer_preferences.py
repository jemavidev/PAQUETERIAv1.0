# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Esquemas para Preferencias de Cliente
Versión: 1.0.0
Fecha: 2025-11-30
"""

from typing import Optional
from pydantic import BaseModel, Field


class CustomerNotificationPreferences(BaseModel):
    """Preferencias de notificación del cliente"""
    
    # Notificaciones por SMS
    sms_on_package_announced: bool = Field(
        default=True,
        description="Recibir SMS cuando se anuncia un paquete"
    )
    sms_on_package_received: bool = Field(
        default=True,
        description="Recibir SMS cuando el paquete llega a bodega"
    )
    sms_on_package_ready: bool = Field(
        default=True,
        description="Recibir SMS cuando el paquete está listo para recoger"
    )
    sms_on_package_delivered: bool = Field(
        default=True,
        description="Recibir SMS cuando el paquete es entregado"
    )
    
    # Notificaciones por Email (si tiene email)
    email_on_package_announced: bool = Field(
        default=False,
        description="Recibir email cuando se anuncia un paquete"
    )
    email_on_package_received: bool = Field(
        default=False,
        description="Recibir email cuando el paquete llega a bodega"
    )
    email_on_package_ready: bool = Field(
        default=False,
        description="Recibir email cuando el paquete está listo para recoger"
    )
    email_on_package_delivered: bool = Field(
        default=False,
        description="Recibir email cuando el paquete es entregado"
    )
    
    # Preferencias generales
    notify_on_weekends: bool = Field(
        default=True,
        description="Recibir notificaciones los fines de semana"
    )
    notify_on_holidays: bool = Field(
        default=True,
        description="Recibir notificaciones en días festivos"
    )
    quiet_hours_enabled: bool = Field(
        default=False,
        description="Activar horario de silencio"
    )
    quiet_hours_start: Optional[str] = Field(
        default=None,
        description="Hora de inicio del silencio (formato HH:MM)"
    )
    quiet_hours_end: Optional[str] = Field(
        default=None,
        description="Hora de fin del silencio (formato HH:MM)"
    )

    class Config:
        from_attributes = True


class CustomerNotificationPreferencesUpdate(BaseModel):
    """Actualización de preferencias de notificación"""
    
    sms_on_package_announced: Optional[bool] = None
    sms_on_package_received: Optional[bool] = None
    sms_on_package_ready: Optional[bool] = None
    sms_on_package_delivered: Optional[bool] = None
    
    email_on_package_announced: Optional[bool] = None
    email_on_package_received: Optional[bool] = None
    email_on_package_ready: Optional[bool] = None
    email_on_package_delivered: Optional[bool] = None
    
    notify_on_weekends: Optional[bool] = None
    notify_on_holidays: Optional[bool] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
