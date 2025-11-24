# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Helper para Preferencias de Cliente
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo
"""

from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from app.models.customer import Customer
from app.models.customer_preferences import CustomerPreferences
from app.config import settings


def get_or_create_customer_preferences(db: Session, customer_id: UUID) -> CustomerPreferences:
    """
    Obtiene o crea preferencias para un cliente
    
    Args:
        db: Sesión de base de datos
        customer_id: ID del cliente
    
    Returns:
        CustomerPreferences: Preferencias del cliente
    """
    # Buscar preferencias existentes
    prefs = db.query(CustomerPreferences).filter(
        CustomerPreferences.customer_id == customer_id
    ).first()
    
    if prefs:
        return prefs
    
    # Crear nuevas preferencias con token único
    prefs = CustomerPreferences(
        customer_id=customer_id,
        token=CustomerPreferences.generate_token()
    )
    
    db.add(prefs)
    db.commit()
    db.refresh(prefs)
    
    return prefs


def get_preferences_url(db: Session, customer_id: UUID) -> str:
    """
    Obtiene la URL de preferencias para un cliente
    
    Args:
        db: Sesión de base de datos
        customer_id: ID del cliente
    
    Returns:
        str: URL completa para gestionar preferencias
    """
    prefs = get_or_create_customer_preferences(db, customer_id)
    
    # Determinar URL base según ambiente
    base_url = (
        settings.production_url 
        if settings.environment == "production" 
        else settings.development_url
    )
    
    return f"{base_url}/customer/preferences?token={prefs.token}"


def add_preferences_footer_to_sms(message: str, preferences_url: str) -> str:
    """
    Agrega footer con link de preferencias a un SMS
    
    Args:
        message: Mensaje original
        preferences_url: URL de preferencias
    
    Returns:
        str: Mensaje con footer
    """
    # Acortar URL si es muy larga (opcional: usar servicio de acortamiento)
    footer = f"\n\nGestiona tus notificaciones: {preferences_url}"
    
    # Verificar que no exceda límite de SMS (160 caracteres por SMS)
    # Si es muy largo, omitir el footer o usar URL corta
    if len(message + footer) > 320:  # 2 SMS
        return message  # Omitir footer si es muy largo
    
    return message + footer


def add_preferences_footer_to_email(html_content: str, preferences_url: str) -> str:
    """
    Agrega footer con link de preferencias a un email HTML
    
    Args:
        html_content: Contenido HTML original
        preferences_url: URL de preferencias
    
    Returns:
        str: HTML con footer
    """
    footer = f"""
    <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; font-size: 12px; color: #6b7280; text-align: center;">
        <p>¿Quieres controlar qué notificaciones recibes?</p>
        <p><a href="{preferences_url}" style="color: #1e40af; text-decoration: underline;">Gestiona tus preferencias de notificaciones</a></p>
    </div>
    """
    
    # Insertar antes del cierre de body o al final
    if '</body>' in html_content:
        html_content = html_content.replace('</body>', f'{footer}</body>')
    else:
        html_content += footer
    
    return html_content
