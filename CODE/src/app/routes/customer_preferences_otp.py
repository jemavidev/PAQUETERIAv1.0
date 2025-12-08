# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Rutas OTP para Preferencias de Cliente
Versión: 1.0.0
Fecha: 2025-02-07
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from sqlalchemy import desc
import logging

from app.database import get_db
from app.models.customer import Customer
from app.models.customer_otp import CustomerOTP
from app.models.customer_preferences import CustomerPreferences
from app.services.sms_service import SMSService
from app.utils.phone_utils import normalize_phone, validate_phone
from app.utils.datetime_utils import get_colombia_now

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/customer/preferences-otp", tags=["customer_preferences_otp"])


# === SCHEMAS ===

class PreferencesOTPRequest(BaseModel):
    phone: str


class PreferencesOTPResponse(BaseModel):
    success: bool
    message: str
    expires_in_seconds: int = 300


class PreferencesOTPVerifyRequest(BaseModel):
    phone: str
    code: str


class PreferencesOTPVerifyResponse(BaseModel):
    success: bool
    message: str
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    redirect_url: str


class SendLinkRequest(BaseModel):
    customer_id: str
    phone: str


class SendLinkResponse(BaseModel):
    success: bool
    message: str


# === ENDPOINTS ===

@router.post("/request", response_model=PreferencesOTPResponse)
async def request_preferences_otp(
    request: PreferencesOTPRequest,
    db: Session = Depends(get_db)
):
    """
    Solicita un código OTP para acceder a preferencias
    
    - Verifica que el cliente existe
    - Envía código de 6 dígitos por SMS
    - Válido por 5 minutos
    """
    try:
        # Normalizar teléfono
        phone = normalize_phone(request.phone)
        if not phone or not validate_phone(phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Número de teléfono inválido"
            )

        # Verificar que el cliente existe
        customer = db.query(Customer).filter(
            Customer.phone == phone,
            Customer.is_active == True
        ).first()

        if not customer:
            logger.warning(f"Intento de acceso a preferencias con teléfono no registrado: {phone}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No encontramos un cliente registrado con este número. Por favor contacte al administrador."
            )

        # Invalidar OTPs anteriores no verificados
        db.query(CustomerOTP).filter(
            CustomerOTP.customer_phone == phone,
            CustomerOTP.is_verified == False
        ).update({"is_expired": True})
        db.commit()

        # Crear nuevo OTP
        otp = CustomerOTP(customer_phone=phone)
        db.add(otp)
        db.commit()
        db.refresh(otp)

        # Enviar SMS con contraseña temporal
        from app.models.notification import NotificationEvent
        
        sms_service = SMSService()
        sms_message = (
            f"PAQUETEX: Su contraseña temporal es: {otp.otp_code}. "
            f"Válida por 5 minutos. No comparta esta contraseña."
        )

        # IMPORTANTE: No pasar customer_id para OTP de autenticación
        # Los OTPs de acceso deben enviarse SIEMPRE, sin verificar preferencias
        await sms_service.send_sms(
            db=db,
            recipient=phone,
            message=sms_message,
            event_type=NotificationEvent.CUSTOM_MESSAGE,
            customer_id=None,  # No verificar preferencias para OTP de autenticación
            is_test=False
        )

        logger.info(f"✅ Contraseña temporal enviada por SMS a {phone} (código: {otp.otp_code})")
        
        # OPCIONAL: También enviar por Email si el cliente tiene email (canal adicional)
        if customer.email:
            try:
                from app.services.email_service import EmailService
                email_service = EmailService()
                await email_service.send_otp_email(
                    recipient_email=customer.email,
                    recipient_name=customer.full_name,
                    otp_code=otp.otp_code,
                    expires_minutes=5
                )
                logger.info(f"✅ Contraseña temporal también enviada por Email a {customer.email}")
            except Exception as e:
                # Email es opcional, si falla no importa
                logger.warning(f"⚠️ No se pudo enviar email (opcional): {str(e)}")

        return PreferencesOTPResponse(
            success=True,
            message="Contraseña temporal enviada por SMS",
            expires_in_seconds=300
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al solicitar OTP para preferencias: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al enviar contraseña temporal: {str(e)}"
        )


@router.post("/verify", response_model=PreferencesOTPVerifyResponse)
async def verify_preferences_otp(
    request: PreferencesOTPVerifyRequest,
    db: Session = Depends(get_db)
):
    """
    Verifica el código OTP y genera token JWT para acceder al portal completo
    
    - Valida el código de 6 dígitos
    - Genera token JWT válido por 1 hora
    - Redirige al dashboard completo del portal
    - Máximo 3 intentos por código
    """
    try:
        # Normalizar teléfono
        phone = normalize_phone(request.phone)
        if not phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Número de teléfono inválido"
            )

        # Buscar OTP más reciente no expirado
        otp = db.query(CustomerOTP).filter(
            CustomerOTP.customer_phone == phone,
            CustomerOTP.is_expired == False,
            CustomerOTP.is_verified == False
        ).order_by(desc(CustomerOTP.created_at)).first()

        if not otp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contraseña no encontrada o expirada. Solicite una nueva contraseña."
            )

        # Verificar contraseña temporal
        logger.info(f"🔍 Verificando contraseña temporal para portal - Recibido: '{request.code}' vs Esperado: '{otp.otp_code}'")
        
        if not otp.verify(request.code):
            db.commit()  # Guardar intento fallido
            
            remaining = otp.max_attempts - otp.attempts
            if remaining > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Contraseña incorrecta. Le quedan {remaining} intentos."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ha excedido el número de intentos. Solicite una nueva contraseña."
                )

        # Contraseña correcta - guardar verificación
        db.commit()
        
        # Limpiar OTPs antiguos del teléfono
        logger.info(f"🧹 Limpiando contraseñas temporales antiguas para {phone}")
        db.query(CustomerOTP).filter(
            CustomerOTP.customer_phone == phone,
            CustomerOTP.id != otp.id
        ).update({"is_expired": True})
        db.commit()

        # Verificar que el cliente existe
        customer = db.query(Customer).filter(
            Customer.phone == phone,
            Customer.is_active == True
        ).first()

        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado"
            )

        # Generar token JWT para acceso al portal completo
        from jose import jwt
        from datetime import timedelta
        from app.config import settings
        from app.utils.datetime_utils import get_colombia_now
        
        SECRET_KEY = settings.secret_key
        ALGORITHM = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hora
        
        expire = get_colombia_now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "customer_id": str(customer.id),
            "phone": phone,
            "exp": expire,
            "type": "customer_portal"
        }
        access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        # Obtener o crear preferencias del cliente (para tenerlas listas)
        preferences = db.query(CustomerPreferences).filter(
            CustomerPreferences.customer_id == customer.id
        ).first()

        if not preferences:
            # Crear preferencias con token único
            preferences = CustomerPreferences(
                customer_id=customer.id,
                token=CustomerPreferences.generate_token()
            )
            db.add(preferences)
            db.commit()
            db.refresh(preferences)
            logger.info(f"✅ Preferencias creadas para cliente: {customer.full_name}")

        # Redirigir al dashboard completo del portal
        redirect_url = "/customer-portal/dashboard"
        
        logger.info(f"✅ Cliente verificado para portal completo: {customer.full_name} ({phone})")

        return PreferencesOTPVerifyResponse(
            success=True,
            message="Verificación exitosa",
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            redirect_url=redirect_url
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al verificar OTP para portal: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en verificación: {str(e)}"
        )


@router.post("/send-link", response_model=SendLinkResponse)
async def send_verify_link(
    request: SendLinkRequest,
    db: Session = Depends(get_db)
):
    """
    Envía un SMS al cliente con el link de verificación para acceder a preferencias
    (Uso interno - para administradores)
    """
    try:
        # Normalizar teléfono
        phone = normalize_phone(request.phone)
        if not phone or not validate_phone(phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Número de teléfono inválido"
            )

        # Verificar que el cliente existe
        customer = db.query(Customer).filter(
            Customer.phone == phone,
            Customer.is_active == True
        ).first()

        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado"
            )

        # Generar link de verificación
        from app.config import settings
        base_url = settings.base_url or "https://staging.jemavi.co"
        verify_link = f"{base_url}/customer/verify"

        # Enviar SMS con link
        from app.models.notification import NotificationEvent
        
        sms_service = SMSService()
        message = (
            f"PAQUETEX: Accede a tu portal de cliente (datos, paquetes y preferencias). "
            f"Ingresa aquí: {verify_link}"
        )

        await sms_service.send_sms(
            db=db,
            recipient=phone,
            message=message,
            event_type=NotificationEvent.CUSTOM_MESSAGE,
            customer_id=str(customer.id),
            is_test=False
        )

        logger.info(f"✅ Link de verificación enviado a {phone} ({customer.full_name})")

        return SendLinkResponse(
            success=True,
            message="Link de verificación enviado por SMS"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al enviar link de verificación: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al enviar SMS: {str(e)}"
        )
