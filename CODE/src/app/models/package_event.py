# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Modelo de Eventos de Paquete
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo

Tabla completa para historial detallado de todas las operaciones del ciclo de vida del paquete.
Registra datos completos en el momento de cada evento (anuncio, recepción, entrega, cancelación).
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Enum, DateTime, Numeric, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from .base import Base
from src.app.utils.datetime_utils import get_colombia_now
from decimal import Decimal
import enum
import uuid


class EventType(enum.Enum):
    """Tipos de eventos del ciclo de vida del paquete"""
    ANUNCIO = "ANUNCIO"                    # Formulario de anuncio público
    RECEPCION = "RECEPCION"                # Recibir paquete en bodega
    ENTREGA = "ENTREGA"                    # Entregar paquete al cliente
    CANCELACION = "CANCELACION"            # Cancelar paquete
    MODIFICACION = "MODIFICACION"          # Modificar datos del paquete
    IMAGEN_AGREGADA = "IMAGEN_AGREGADA"    # Subir imagen
    NOTA_AGREGADA = "NOTA_AGREGADA"        # Agregar observación


class PackageEvent(Base):
    """
    Historial completo de eventos del paquete.
    
    Esta tabla registra TODOS los datos relevantes de cada operación en el momento exacto
    en que ocurre, permitiendo:
    - Auditoría completa del ciclo de vida del paquete
    - Reconstrucción del estado del paquete en cualquier momento
    - Reportes financieros y operativos detallados
    - Trazabilidad de operadores y acciones
    """
    __tablename__ = "package_events"

    # ========================================
    # IDENTIFICADORES
    # ========================================
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id = Column(Integer, ForeignKey("packages.id"), nullable=True, index=True)
    announcement_id = Column(UUID(as_uuid=True), ForeignKey("package_announcements_new.id"), nullable=True)
    
    # ========================================
    # TIPO DE EVENTO Y TIMESTAMP
    # ========================================
    event_type = Column(Enum(EventType), nullable=False, index=True)
    event_timestamp = Column(DateTime(timezone=True), default=get_colombia_now, nullable=False, index=True)
    
    # ========================================
    # DATOS DEL PAQUETE EN ESE MOMENTO
    # ========================================
    # Identificación
    tracking_number = Column(String(50), nullable=True, index=True)  # Número de tracking del sistema
    guide_number = Column(String(50), nullable=True, index=True)     # Número de guía del transportador
    access_code = Column(String(20), nullable=True)                  # Código de acceso del paquete
    tracking_code = Column(String(10), nullable=True, index=True)    # Código de consulta público (4 caracteres)
    
    # Estado y tipo
    status_before = Column(String(50), nullable=True)                # Estado anterior
    status_after = Column(String(50), nullable=False)                # Estado nuevo
    package_type = Column(String(50), nullable=True)                 # NORMAL, EXTRA_DIMENSIONADO
    package_condition = Column(String(50), nullable=True)            # BUENO, ABIERTO, REGULAR
    
    # Ubicación física
    posicion = Column(String(2), nullable=True)                        # Posición física 00-99
    
    # ========================================
    # DATOS DEL CLIENTE
    # ========================================
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True)
    customer_name = Column(String(100), nullable=True)
    customer_phone = Column(String(20), nullable=True)
    customer_email = Column(String(100), nullable=True)
    
    # ========================================
    # DATOS FINANCIEROS
    # ========================================
    base_fee = Column(Numeric(10, 2), nullable=True)                 # Tarifa base de entrega
    storage_fee = Column(Numeric(10, 2), nullable=True)              # Tarifa de almacenamiento
    storage_days = Column(Integer, nullable=True)                    # Días de almacenamiento
    total_amount = Column(Numeric(10, 2), nullable=True)             # Monto total
    
    # Datos de pago (solo para ENTREGA)
    payment_method = Column(String(50), nullable=True)               # efectivo, tarjeta, transferencia
    payment_amount = Column(Numeric(10, 2), nullable=True)           # Monto pagado
    payment_received = Column(Boolean, default=False)                # Si se recibió el pago
    
    # ========================================
    # DATOS DE LA OPERACIÓN
    # ========================================
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    operator_name = Column(String(100), nullable=True)               # Nombre del operador
    operator_role = Column(String(50), nullable=True)                # Rol del operador (ADMIN, OPERADOR)
    
    # ========================================
    # IMÁGENES Y ARCHIVOS
    # ========================================
    # JSON con lista de IDs de archivos asociados a este evento
    file_ids = Column(JSON, nullable=True)
    # Ejemplo: {"images": [1, 2, 3], "documents": [4], "signature": [5]}
    
    # ========================================
    # OBSERVACIONES Y RAZONES
    # ========================================
    observations = Column(Text, nullable=True)                       # Observaciones generales
    cancellation_reason = Column(String(100), nullable=True)         # Razón de cancelación (solo para CANCELACION)
    
    # ========================================
    # DATOS ADICIONALES (JSON)
    # ========================================
    # Campo flexible para datos específicos de cada tipo de evento
    additional_data = Column(JSON, nullable=True)
    """
    Ejemplos de additional_data por tipo de evento:
    
    ANUNCIO:
    {
        "source": "web_public",
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0..."
    }
    
    RECEPCION:
    {
        "received_from": "DHL",
        "physical_inspection_notes": "Caja en buen estado",
        "weight_kg": 2.5,
        "dimensions_cm": "30x20x15",
        "images_count": 3
    }
    
    ENTREGA:
    {
        "recipient_name": "Juan Pérez",
        "recipient_dni": "123456789",
        "delivery_signature_url": "s3://...",
        "delivery_notes": "Entregado en mano propia",
        "payment_reference": "REF123456"
    }
    
    CANCELACION:
    {
        "refund_amount": 1500.00,
        "refund_method": "efectivo",
        "notification_sent": true,
        "cancellation_code": "CANCEL123"
    }
    """
    
    # ========================================
    # TIMESTAMPS DE CONTROL
    # ========================================
    created_at = Column(DateTime, default=get_colombia_now, nullable=False)
    
    # ========================================
    # RELACIONES
    # ========================================
    package = relationship("Package", foreign_keys=[package_id])
    announcement = relationship("PackageAnnouncementNew", foreign_keys=[announcement_id])
    customer = relationship("Customer", foreign_keys=[customer_id])
    operator = relationship("User", foreign_keys=[operator_id])
    
    def __repr__(self):
        return f"<PackageEvent(id={self.id}, type={self.event_type.value}, package_id={self.package_id}, timestamp={self.event_timestamp})>"
    
    def to_dict(self):
        """Convertir a diccionario para serialización JSON"""
        return {
            "id": str(self.id),
            "package_id": self.package_id,
            "announcement_id": str(self.announcement_id) if self.announcement_id else None,
            "event_type": self.event_type.value,
            "event_timestamp": self.event_timestamp.isoformat() if self.event_timestamp else None,
            
            # Identificadores
            "tracking_number": self.tracking_number,
            "guide_number": self.guide_number,
            "access_code": self.access_code,
            "tracking_code": self.tracking_code,
            
            # Estados
            "status_before": self.status_before,
            "status_after": self.status_after,
            "package_type": self.package_type,
            "package_condition": self.package_condition,
            "baroti": self.posicion,
            
            # Cliente
            "customer_id": str(self.customer_id) if self.customer_id else None,
            "customer_name": self.customer_name,
            "customer_phone": self.customer_phone,
            "customer_email": self.customer_email,
            
            # Financiero
            "base_fee": float(self.base_fee) if self.base_fee else None,
            "storage_fee": float(self.storage_fee) if self.storage_fee else None,
            "storage_days": self.storage_days,
            "total_amount": float(self.total_amount) if self.total_amount else None,
            "payment_method": self.payment_method,
            "payment_amount": float(self.payment_amount) if self.payment_amount else None,
            "payment_received": self.payment_received,
            
            # Operador
            "operator_id": self.operator_id,
            "operator_name": self.operator_name,
            "operator_role": self.operator_role,
            
            # Archivos y observaciones
            "file_ids": self.file_ids,
            "observations": self.observations,
            "cancellation_reason": self.cancellation_reason,
            
            # Adicionales
            "additional_data": self.additional_data,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_announcement(cls, announcement, operator_id=None, operator_name="Sistema", additional_data=None):
        """Crear evento de anuncio desde un objeto PackageAnnouncementNew"""
        return cls(
            announcement_id=announcement.id,
            event_type=EventType.ANUNCIO,
            tracking_code=announcement.tracking_code,
            guide_number=announcement.guide_number,
            status_after="ANUNCIADO",
            customer_name=announcement.customer_name,
            customer_phone=announcement.customer_phone,
            customer_id=announcement.customer_id,
            operator_id=operator_id,
            operator_name=operator_name,
            event_timestamp=announcement.announced_at or get_colombia_now(),
            additional_data=additional_data or {}
        )
    
    @classmethod
    def from_package_reception(cls, package, announcement, operator_id, operator_name, operator_role, 
                               fee_calculation, file_ids=None, observations=None, additional_data=None):
        """Crear evento de recepción desde un paquete recién recibido"""
        return cls(
            package_id=package.id,
            announcement_id=announcement.id if announcement else None,
            event_type=EventType.RECEPCION,
            tracking_number=package.tracking_number,
            guide_number=package.guide_number,
            access_code=package.access_code,
            tracking_code=announcement.tracking_code if announcement else None,
            posicion=package.posicion,
            status_before="ANUNCIADO",
            status_after="RECIBIDO",
            package_type=package.package_type.value if package.package_type else None,
            package_condition=package.package_condition.value if package.package_condition else None,
            customer_id=package.customer_id,
            customer_name=package.customer.full_name if package.customer else None,
            customer_phone=package.customer.phone if package.customer else None,
            base_fee=fee_calculation.base_fee,
            storage_fee=fee_calculation.storage_fee,
            storage_days=fee_calculation.storage_days,
            total_amount=fee_calculation.total_amount,
            operator_id=operator_id,
            operator_name=operator_name,
            operator_role=operator_role,
            file_ids=file_ids or {},
            observations=observations,
            event_timestamp=package.received_at or get_colombia_now(),
            additional_data=additional_data or {}
        )
    
    @classmethod
    def from_package_delivery(cls, package, payment_method, payment_amount, operator_id, operator_name, 
                             operator_role, file_ids=None, observations=None, additional_data=None):
        """Crear evento de entrega desde un paquete entregado"""
        return cls(
            package_id=package.id,
            event_type=EventType.ENTREGA,
            tracking_number=package.tracking_number,
            guide_number=package.guide_number,
            access_code=package.access_code,
            status_before="RECIBIDO",
            status_after="ENTREGADO",
            package_type=package.package_type.value if package.package_type else None,
            package_condition=package.package_condition.value if package.package_condition else None,
            customer_id=package.customer_id,
            customer_name=package.customer.full_name if package.customer else None,
            customer_phone=package.customer.phone if package.customer else None,
            base_fee=package.base_fee,
            storage_fee=package.storage_fee,
            storage_days=None,  # Se puede calcular si es necesario
            total_amount=package.total_amount,
            payment_method=payment_method,
            payment_amount=payment_amount,
            payment_received=True,
            operator_id=operator_id,
            operator_name=operator_name,
            operator_role=operator_role,
            file_ids=file_ids or {},
            observations=observations,
            event_timestamp=package.delivered_at or get_colombia_now(),
            additional_data=additional_data or {}
        )
    
    @classmethod
    def from_package_cancellation(cls, package, cancellation_reason, operator_id, operator_name, 
                                 operator_role, observations=None, additional_data=None):
        """Crear evento de cancelación desde un paquete cancelado"""
        status_before = "ANUNCIADO" if package.status.value == "ANUNCIADO" else "RECIBIDO"
        
        return cls(
            package_id=package.id,
            event_type=EventType.CANCELACION,
            tracking_number=package.tracking_number,
            guide_number=package.guide_number,
            access_code=package.access_code,
            status_before=status_before,
            status_after="CANCELADO",
            package_type=package.package_type.value if package.package_type else None,
            package_condition=package.package_condition.value if package.package_condition else None,
            customer_id=package.customer_id,
            customer_name=package.customer.full_name if package.customer else None,
            customer_phone=package.customer.phone if package.customer else None,
            operator_id=operator_id,
            operator_name=operator_name,
            operator_role=operator_role,
            cancellation_reason=cancellation_reason,
            observations=observations,
            event_timestamp=package.cancelled_at or get_colombia_now(),
            additional_data=additional_data or {}
        )


