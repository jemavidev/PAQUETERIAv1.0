# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Modelo de OTP para Portal de Clientes
Versión: 1.0.0
Fecha: 2025-01-30
"""

from sqlalchemy import Column, String, DateTime, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timedelta
import uuid
import secrets

from .base import Base
from app.utils.datetime_utils import get_colombia_now


class CustomerOTP(Base):
    """
    Modelo para códigos OTP de verificación de clientes
    """
    __tablename__ = "customer_otps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_phone = Column(String(20), nullable=False, index=True)
    otp_code = Column(String(6), nullable=False)
    
    # Control de intentos
    attempts = Column(Integer, default=0, nullable=False)
    max_attempts = Column(Integer, default=3, nullable=False)
    
    # Estado
    is_verified = Column(Boolean, default=False, nullable=False)
    is_expired = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=get_colombia_now, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    verified_at = Column(DateTime, nullable=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.otp_code:
            self.otp_code = self.generate_otp()
        if not self.expires_at:
            self.expires_at = get_colombia_now() + timedelta(minutes=5)

    @staticmethod
    def generate_otp() -> str:
        """Genera un código OTP de 6 dígitos"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(6)])

    def is_valid(self) -> bool:
        """Verifica si el OTP es válido"""
        from datetime import timezone
        
        now = get_colombia_now()
        
        # Asegurar que expires_at tenga timezone para comparación
        expires_at = self.expires_at
        if expires_at.tzinfo is None:
            # Si no tiene timezone, asumir UTC y convertir a Colombia
            expires_at = expires_at.replace(tzinfo=timezone.utc)
            colombia_offset = timezone(timedelta(hours=-5))
            expires_at = expires_at.astimezone(colombia_offset)
        
        return (
            not self.is_verified and
            not self.is_expired and
            now < expires_at and
            self.attempts < self.max_attempts
        )

    def verify(self, code: str) -> bool:
        """Verifica el código OTP"""
        # Verificar validez ANTES de incrementar intentos
        if not self.is_valid():
            return False
        
        # Incrementar intentos
        self.attempts += 1
        
        # Verificar código
        if self.otp_code == code:
            self.is_verified = True
            self.verified_at = get_colombia_now()
            return True
        
        # Si alcanzó el máximo de intentos, marcar como expirado
        if self.attempts >= self.max_attempts:
            self.is_expired = True
        
        return False

    def mark_as_expired(self):
        """Marca el OTP como expirado"""
        self.is_expired = True

    def __repr__(self):
        return f"<CustomerOTP(phone='{self.customer_phone}', verified={self.is_verified}, expires_at='{self.expires_at}')>"
