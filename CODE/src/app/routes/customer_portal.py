# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Rutas del Portal de Clientes
Versión: 1.0.0
Fecha: 2025-01-30
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.database import get_db
from app.schemas.customer_portal import (
    OTPRequest, OTPResponse, OTPVerifyRequest, OTPVerifyResponse,
    CustomerPortalData, CustomerPortalUpdate, CustomerPackageHistoryResponse
)
from app.services.customer_portal_service import CustomerPortalService
from app.utils.exceptions import ValidationException

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/customer-portal",
    tags=["Portal de Clientes"]
)


# ========================================
# Dependency: Verificar Token
# ========================================

def get_current_customer(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> dict:
    """Verifica el token JWT y retorna los datos del cliente"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado. Token requerido.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.split(" ")[1]
    service = CustomerPortalService()
    customer_data = service.verify_token(token)
    
    if not customer_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return customer_data


# ========================================
# Endpoints Públicos (sin autenticación)
# ========================================

@router.post("/request-otp", response_model=OTPResponse)
async def request_otp(
    request: OTPRequest,
    db: Session = Depends(get_db)
):
    """
    Solicita un código OTP para acceder al portal
    
    - Verifica que el cliente existe
    - Envía código de 6 dígitos por SMS
    - Válido por 5 minutos
    - Máximo 3 intentos por hora
    """
    try:
        service = CustomerPortalService()
        response = await service.request_otp(db, request)
        return response
    
    except ValidationException as e:
        # Si el mensaje contiene "no encontrado", usar 404
        status_code = 404 if "no encontrado" in str(e).lower() or "not found" in str(e).lower() else 400
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error en request_otp: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error al procesar solicitud. Intente nuevamente."
        )


@router.post("/verify-otp", response_model=OTPVerifyResponse)
async def verify_otp(
    request: OTPVerifyRequest,
    db: Session = Depends(get_db)
):
    """
    Verifica el código OTP y genera token de acceso
    
    - Valida el código de 6 dígitos
    - Genera token JWT válido por 1 hora
    - Máximo 3 intentos por código
    """
    try:
        service = CustomerPortalService()
        response = await service.verify_otp(db, request)
        return response
    
    except ValidationException as e:
        status_code = 404 if "no encontrado" in str(e).lower() or "not found" in str(e).lower() else 400
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error en verify_otp: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error al verificar código. Intente nuevamente."
        )


# ========================================
# Endpoints Protegidos (requieren token)
# ========================================

@router.get("/me", response_model=CustomerPortalData)
async def get_my_data(
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Obtiene los datos del cliente autenticado
    
    Incluye:
    - Información personal
    - Dirección
    - Estadísticas de paquetes
    """
    try:
        service = CustomerPortalService()
        customer_data = service.get_customer_data(
            db, 
            current_customer["customer_id"]
        )
        return customer_data
    
    except ValidationException as e:
        status_code = 404 if "no encontrado" in str(e).lower() or "not found" in str(e).lower() else 400
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error en get_my_data: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al obtener datos")


@router.put("/me", response_model=CustomerPortalData)
async def update_my_data(
    update_data: CustomerPortalUpdate,
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Actualiza los datos del cliente autenticado
    
    Campos editables:
    - Nombre y apellido
    - Email
    - Dirección completa
    - Información del edificio
    
    NO editable:
    - Teléfono (es el identificador único)
    """
    try:
        service = CustomerPortalService()
        updated_customer = service.update_customer_data(
            db,
            current_customer["customer_id"],
            update_data
        )
        return updated_customer
    
    except ValidationException as e:
        status_code = 404 if "no encontrado" in str(e).lower() or "not found" in str(e).lower() else 400
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error en update_my_data: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al actualizar datos")


@router.get("/packages", response_model=CustomerPackageHistoryResponse)
async def get_my_packages(
    limit: int = 20,
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Obtiene el historial de paquetes del cliente
    
    - Últimos 20 paquetes por defecto
    - Estados: Anunciado, Recibido, Entregado, Cancelado
    - Ordenados por fecha (más recientes primero)
    """
    try:
        service = CustomerPortalService()
        packages_data = service.get_customer_packages(
            db,
            current_customer["customer_id"],
            limit=min(limit, 50)  # Máximo 50
        )
        return packages_data
    
    except ValidationException as e:
        status_code = 404 if "no encontrado" in str(e).lower() or "not found" in str(e).lower() else 400
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error en get_my_packages: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al obtener paquetes")


@router.get("/preferences/notifications")
async def get_notification_preferences(
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Obtiene las preferencias de notificación del cliente
    
    Incluye:
    - Preferencias de SMS
    - Preferencias de Email
    - Horarios de silencio
    """
    try:
        service = CustomerPortalService()
        preferences = service.get_notification_preferences(
            db,
            current_customer["customer_id"]
        )
        # Envolver en objeto para que el frontend lo procese correctamente
        return {"preferences": preferences}
    
    except ValidationException as e:
        status_code = 404 if "no encontrado" in str(e).lower() else 400
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error en get_notification_preferences: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al obtener preferencias")


@router.put("/preferences/notifications")
async def update_notification_preferences(
    preferences: dict,
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Actualiza las preferencias de notificación del cliente
    
    Campos editables:
    - sms_notifications_enabled
    - email_notifications_enabled
    - notify_package_announced
    - notify_package_received
    - notify_package_delivered
    - notify_payment_due
    - marketing_enabled
    """
    try:
        service = CustomerPortalService()
        updated_preferences = service.update_notification_preferences(
            db,
            current_customer["customer_id"],
            preferences
        )
        # Envolver en objeto para que el frontend lo procese correctamente
        return {"preferences": updated_preferences}
    
    except ValidationException as e:
        status_code = 404 if "no encontrado" in str(e).lower() else 400
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error en update_notification_preferences: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al actualizar preferencias")


@router.post("/logout")
async def logout(
    current_customer: dict = Depends(get_current_customer)
):
    """
    Cierra la sesión del cliente
    
    Nota: Como usamos JWT stateless, el cliente debe eliminar
    el token localmente. El token expirará automáticamente.
    """
    logger.info(f"Cliente cerró sesión: {current_customer['phone']}")
    return JSONResponse(
        content={
            "success": True,
            "message": "Sesión cerrada exitosamente"
        }
    )
