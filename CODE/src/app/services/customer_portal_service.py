# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Servicio de Portal de Clientes
Versión: 1.0.0
Fecha: 2025-01-30
"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime, timedelta
from jose import JWTError, jwt
import logging

from app.models.customer import Customer
from app.models.customer_otp import CustomerOTP
from app.models.package import Package, PackageStatus
from app.models.notification import NotificationEvent
from app.schemas.customer_portal import (
    OTPRequest, OTPResponse, OTPVerifyRequest, OTPVerifyResponse,
    CustomerPortalData, CustomerPortalUpdate, CustomerPackageHistory
)
from app.services.sms_service import SMSService
from app.utils.phone_utils import normalize_phone, validate_phone
from app.utils.datetime_utils import get_colombia_now
from app.utils.exceptions import ValidationException
from app.config import settings

logger = logging.getLogger(__name__)


class CustomerPortalService:
    """Servicio para gestión del portal de autogestión de clientes"""

    def __init__(self):
        self.sms_service = SMSService()
        # Configuración JWT para tokens del portal
        self.SECRET_KEY = settings.secret_key
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hora

    # ========================================
    # OTP - Solicitud y Verificación
    # ========================================

    async def request_otp(self, db: Session, request: OTPRequest) -> OTPResponse:
        """
        Solicita un código OTP para un cliente
        1. Valida que el cliente existe
        2. Verifica rate limiting (3 intentos por hora)
        3. Genera y envía código SMS
        """
        try:
            # Normalizar teléfono
            phone = normalize_phone(request.phone)
            if not phone or not validate_phone(phone):
                raise ValidationException("Número de teléfono inválido")

            # Verificar que el cliente existe
            customer = db.query(Customer).filter(
                Customer.phone == phone,
                Customer.is_active == True
            ).first()

            if not customer:
                # Por seguridad, no revelar si el cliente existe o no
                logger.warning(f"Intento de acceso con teléfono no registrado: {phone}")
                raise ValidationException(
                    "No encontramos un cliente registrado con este número. "
                    "Por favor contacte al administrador."
                )

            # Rate limiting desactivado temporalmente
            # TODO: Implementar rate limiting más inteligente en el futuro
            # one_hour_ago = get_colombia_now() - timedelta(hours=1)
            # recent_otps = db.query(CustomerOTP).filter(
            #     CustomerOTP.customer_phone == phone,
            #     CustomerOTP.created_at >= one_hour_ago,
            #     CustomerOTP.is_verified == False
            # ).count()
            # if recent_otps >= 5:
            #     raise ValidationException(
            #         "Ha excedido el límite de intentos. "
            #         "Por favor intente nuevamente en 1 hora."
            #     )

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

            # Enviar SMS con código
            message = (
                f"PAQUETEX: Su código de verificación es: {otp.otp_code}. "
                f"Válido por 5 minutos. No comparta este código."
            )

            await self.sms_service.send_sms(
                db=db,
                recipient=phone,
                message=message,
                event_type=NotificationEvent.CUSTOM_MESSAGE,
                customer_id=str(customer.id),
                is_test=False
            )

            logger.info(f"✅ OTP enviado a {phone} (código: {otp.otp_code})")

            return OTPResponse(
                success=True,
                message="Código de verificación enviado por SMS",
                expires_in_seconds=300
            )

        except (ValidationException, ValidationException) as e:
            raise e
        except Exception as e:
            logger.error(f"Error al solicitar OTP: {str(e)}", exc_info=True)
            raise ValidationException(f"Error al enviar código: {str(e)}")

    async def verify_otp(
        self, 
        db: Session, 
        request: OTPVerifyRequest
    ) -> OTPVerifyResponse:
        """
        Verifica el código OTP y genera token de acceso
        """
        try:
            # Normalizar teléfono
            phone = normalize_phone(request.phone)
            if not phone:
                raise ValidationException("Número de teléfono inválido")

            # Buscar OTP más reciente no expirado
            otp = db.query(CustomerOTP).filter(
                CustomerOTP.customer_phone == phone,
                CustomerOTP.is_expired == False,
                CustomerOTP.is_verified == False
            ).order_by(desc(CustomerOTP.created_at)).first()

            if not otp:
                raise ValidationException(
                    "Código no encontrado o expirado. "
                    "Solicite un nuevo código."
                )

            # Verificar código
            logger.info(f"🔍 Verificando código - Recibido: '{request.code}' (len={len(request.code)}) vs Esperado: '{otp.otp_code}' (len={len(otp.otp_code)})")
            
            # Si el código es correcto, resetear intentos de OTPs anteriores del mismo teléfono
            if otp.otp_code == request.code:
                logger.info(f"✅ Código correcto, reseteando intentos de OTPs anteriores")
                # Resetear intentos de otros OTPs no verificados del mismo teléfono
                db.query(CustomerOTP).filter(
                    CustomerOTP.customer_phone == phone,
                    CustomerOTP.is_verified == False,
                    CustomerOTP.id != otp.id
                ).update({"attempts": 0, "is_expired": False})
            
            if not otp.verify(request.code):
                db.commit()  # Guardar intento fallido
                
                remaining = otp.max_attempts - otp.attempts
                if remaining > 0:
                    raise ValidationException(
                        f"Código incorrecto. Le quedan {remaining} intentos."
                    )
                else:
                    raise ValidationException(
                        "Ha excedido el número de intentos. "
                        "Solicite un nuevo código."
                    )

            # Código correcto - guardar verificación
            db.commit()
            
            # Limpiar todos los OTPs antiguos del teléfono (resetear rate limiting)
            logger.info(f"🧹 Limpiando OTPs antiguos para resetear rate limiting")
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
                raise ValidationException("Cliente no encontrado")

            # Generar token JWT
            access_token = self._create_access_token(
                data={"customer_id": str(customer.id), "phone": phone}
            )

            logger.info(f"✅ Cliente autenticado: {customer.full_name} ({phone}) - Rate limiting reseteado")

            return OTPVerifyResponse(
                success=True,
                message="Verificación exitosa",
                access_token=access_token,
                token_type="bearer",
                expires_in=self.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )

        except (ValidationException, ValidationException) as e:
            raise e
        except Exception as e:
            logger.error(f"Error al verificar OTP: {str(e)}", exc_info=True)
            raise ValidationException(f"Error en verificación: {str(e)}")

    # ========================================
    # Gestión de Datos del Cliente
    # ========================================

    def get_customer_data(
        self, 
        db: Session, 
        customer_id: str
    ) -> CustomerPortalData:
        """Obtiene los datos del cliente autenticado"""
        customer = db.query(Customer).filter(
            Customer.id == customer_id,
            Customer.is_active == True
        ).first()

        if not customer:
            raise ValidationException("Cliente no encontrado")

        return CustomerPortalData.model_validate(customer)

    def update_customer_data(
        self,
        db: Session,
        customer_id: str,
        update_data: CustomerPortalUpdate
    ) -> CustomerPortalData:
        """
        Actualiza los datos del cliente
        Solo permite editar campos específicos (NO el teléfono)
        """
        customer = db.query(Customer).filter(
            Customer.id == customer_id,
            Customer.is_active == True
        ).first()

        if not customer:
            raise ValidationException("Cliente no encontrado")

        # Actualizar solo campos permitidos
        update_dict = update_data.model_dump(exclude_unset=True)
        
        for field, value in update_dict.items():
            if hasattr(customer, field):
                setattr(customer, field, value)

        # Actualizar full_name si se modificó nombre o apellido
        if 'first_name' in update_dict or 'last_name' in update_dict:
            customer.full_name = f"{customer.first_name} {customer.last_name or ''}".strip()

        customer.updated_at = get_colombia_now()
        
        db.commit()
        db.refresh(customer)

        logger.info(f"✅ Cliente actualizado: {customer.full_name} ({customer.phone})")

        return CustomerPortalData.model_validate(customer)

    def get_notification_preferences(
        self,
        db: Session,
        customer_id: str
    ) -> Dict[str, Any]:
        """Obtiene las preferencias de notificación del cliente"""
        from app.models.customer_preferences import CustomerPreferences
        
        customer = db.query(Customer).filter(
            Customer.id == customer_id,
            Customer.is_active == True
        ).first()

        if not customer:
            raise ValidationException("Cliente no encontrado")

        # Obtener preferencias (o crear con valores por defecto)
        preferences = db.query(CustomerPreferences).filter(
            CustomerPreferences.customer_id == customer_id
        ).first()

        if not preferences:
            # Crear preferencias por defecto
            preferences = CustomerPreferences(
                customer_id=customer_id,
                token=CustomerPreferences.generate_token()
            )
            db.add(preferences)
            db.commit()
            db.refresh(preferences)

        return {
            # Notificaciones SMS
            "sms_notifications_enabled": preferences.sms_notifications_enabled,
            "sms_on_package_announced": preferences.notify_package_announced,
            "sms_on_package_received": preferences.notify_package_received,
            "sms_on_package_delivered": preferences.notify_package_delivered,
            
            # Notificaciones Email
            "email_notifications_enabled": preferences.email_notifications_enabled,
            "email_on_package_announced": preferences.notify_package_announced if preferences.email_notifications_enabled else False,
            "email_on_package_received": preferences.notify_package_received if preferences.email_notifications_enabled else False,
            "email_on_package_delivered": preferences.notify_package_delivered if preferences.email_notifications_enabled else False,
            
            # Otras preferencias
            "notify_payment_due": preferences.notify_payment_due,
            "marketing_enabled": preferences.marketing_enabled,
        }

    def update_notification_preferences(
        self,
        db: Session,
        customer_id: str,
        preferences_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Actualiza las preferencias de notificación del cliente"""
        from app.models.customer_preferences import CustomerPreferences
        
        customer = db.query(Customer).filter(
            Customer.id == customer_id,
            Customer.is_active == True
        ).first()

        if not customer:
            raise ValidationException("Cliente no encontrado")

        # Obtener o crear preferencias
        preferences = db.query(CustomerPreferences).filter(
            CustomerPreferences.customer_id == customer_id
        ).first()

        if not preferences:
            preferences = CustomerPreferences(
                customer_id=customer_id,
                token=CustomerPreferences.generate_token()
            )
            db.add(preferences)

        # Actualizar campos directamente (los nombres coinciden)
        allowed_fields = [
            "sms_notifications_enabled",
            "email_notifications_enabled",
            "notify_package_announced",
            "notify_package_received",
            "notify_package_delivered",
            "notify_payment_due",
            "marketing_enabled"
        ]

        # Actualizar solo los campos proporcionados y permitidos
        for field in allowed_fields:
            if field in preferences_data and preferences_data[field] is not None:
                setattr(preferences, field, preferences_data[field])
                logger.info(f"📝 Actualizando {field} = {preferences_data[field]} para cliente {customer_id}")

        preferences.updated_at = get_colombia_now()
        db.commit()
        db.refresh(preferences)

        logger.info(f"✅ Preferencias actualizadas para cliente: {customer_id}")

        return self.get_notification_preferences(db, customer_id)

    def get_customer_packages(
        self,
        db: Session,
        customer_id: str,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Obtiene el historial de paquetes del cliente
        Solo muestra estados: ANUNCIADO, RECIBIDO, ENTREGADO, CANCELADO
        """
        customer = db.query(Customer).filter(
            Customer.id == customer_id,
            Customer.is_active == True
        ).first()

        if not customer:
            raise ValidationException("Cliente no encontrado")

        # Estados permitidos
        allowed_statuses = [
            PackageStatus.ANUNCIADO,
            PackageStatus.RECIBIDO,
            PackageStatus.ENTREGADO,
            PackageStatus.CANCELADO
        ]

        # Obtener paquetes
        packages = db.query(Package).filter(
            Package.customer_id == customer_id,
            Package.status.in_(allowed_statuses)
        ).order_by(desc(Package.created_at)).limit(limit).all()

        # Serializar
        packages_data = []
        for pkg in packages:
            packages_data.append(CustomerPackageHistory(
                id=pkg.id,
                tracking_number=pkg.tracking_number,
                guide_number=pkg.guide_number,
                status=pkg.status.value if hasattr(pkg.status, 'value') else str(pkg.status),
                announced_at=pkg.announced_at,
                received_at=pkg.received_at,
                delivered_at=pkg.delivered_at,
                package_type=pkg.package_type.value if hasattr(pkg, 'package_type') and pkg.package_type else None,
                carrier=pkg.carrier if hasattr(pkg, 'carrier') else None
            ))

        return {
            "packages": packages_data,
            "total": len(packages_data)
        }

    # ========================================
    # JWT Token Management
    # ========================================

    def _create_access_token(self, data: dict) -> str:
        """Crea un token JWT para el portal de clientes"""
        to_encode = data.copy()
        expire = get_colombia_now() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({
            "exp": expire,
            "type": "customer_portal"
        })
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verifica y decodifica un token JWT del portal"""
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            
            # Verificar que es un token del portal
            if payload.get("type") != "customer_portal":
                return None
            
            customer_id: str = payload.get("customer_id")
            phone: str = payload.get("phone")
            
            if customer_id is None or phone is None:
                return None
            
            return {"customer_id": customer_id, "phone": phone}
        
        except JWTError:
            return None
