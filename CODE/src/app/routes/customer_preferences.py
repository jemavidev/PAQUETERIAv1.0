# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Rutas de Preferencias de Cliente
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.models.customer import Customer
from app.models.customer_preferences import CustomerPreferences

router = APIRouter(prefix="/api/customer/preferences", tags=["customer_preferences"])


# === SCHEMAS ===

class CustomerPreferencesUpdate(BaseModel):
    sms_notifications_enabled: bool = True
    email_notifications_enabled: bool = True
    notify_package_received: bool = True
    notify_package_delivered: bool = True
    notify_package_announced: bool = True
    notify_payment_due: bool = True
    marketing_enabled: bool = False


# === ENDPOINTS ===

@router.get("")
async def get_customer_preferences(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Obtener preferencias de un cliente usando su token único
    No requiere autenticación - el token es la credencial
    """
    try:
        # Buscar preferencias por token
        prefs = db.query(CustomerPreferences).filter(
            CustomerPreferences.token == token
        ).first()
        
        if not prefs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Token inválido o preferencias no encontradas"
            )
        
        # Obtener información del cliente
        customer = prefs.customer
        
        return {
            "success": True,
            "customer": {
                "full_name": customer.full_name,
                "phone": customer.phone,
                "email": customer.email
            },
            "preferences": prefs.to_dict()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener preferencias: {str(e)}"
        )


@router.put("")
async def update_customer_preferences(
    token: str,
    preferences: CustomerPreferencesUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar preferencias de un cliente usando su token único
    No requiere autenticación - el token es la credencial
    """
    try:
        # Buscar preferencias por token
        prefs = db.query(CustomerPreferences).filter(
            CustomerPreferences.token == token
        ).first()
        
        if not prefs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Token inválido o preferencias no encontradas"
            )
        
        # Actualizar preferencias
        prefs.sms_notifications_enabled = preferences.sms_notifications_enabled
        prefs.email_notifications_enabled = preferences.email_notifications_enabled
        prefs.notify_package_received = preferences.notify_package_received
        prefs.notify_package_delivered = preferences.notify_package_delivered
        prefs.notify_package_announced = preferences.notify_package_announced
        prefs.notify_payment_due = preferences.notify_payment_due
        prefs.marketing_enabled = preferences.marketing_enabled
        
        db.commit()
        db.refresh(prefs)
        
        return {
            "success": True,
            "message": "Preferencias actualizadas correctamente",
            "preferences": prefs.to_dict()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar preferencias: {str(e)}"
        )


class CustomerIdRequest(BaseModel):
    customer_id: UUID


@router.post("/create")
async def create_customer_preferences(
    request: CustomerIdRequest,
    db: Session = Depends(get_db)
):
    """
    Crear preferencias para un cliente (uso interno)
    Retorna el token único para que el cliente pueda gestionar sus preferencias
    """
    customer_id = request.customer_id
    try:
        # Verificar que el cliente existe
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado"
            )
        
        # Verificar si ya tiene preferencias
        existing_prefs = db.query(CustomerPreferences).filter(
            CustomerPreferences.customer_id == customer_id
        ).first()
        
        if existing_prefs:
            return {
                "success": True,
                "message": "El cliente ya tiene preferencias",
                "token": existing_prefs.token,
                "preferences_url": f"/customer/preferences?token={existing_prefs.token}"
            }
        
        # Crear nuevas preferencias con token único
        prefs = CustomerPreferences(
            customer_id=customer_id,
            token=CustomerPreferences.generate_token()
        )
        
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
        
        return {
            "success": True,
            "message": "Preferencias creadas exitosamente",
            "token": prefs.token,
            "preferences_url": f"/customer/preferences?token={prefs.token}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear preferencias: {str(e)}"
        )
