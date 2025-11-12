# ========================================
# PAQUETES EL CLUB v4.0 - Servicio de Estados
# ========================================

from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID
import uuid

from app.models.package import Package, PackageStatus, PackageType, PackageCondition
from app.models.package_history import PackageHistory
from app.models.package_event import PackageEvent, EventType
from app.models.announcement_new import PackageAnnouncementNew
from app.models.notification import NotificationEvent
from app.models.user import User
from app.models.customer import Customer
from app.services.sms_service import SMSService
from app.utils.datetime_utils import get_colombia_now
from app.schemas.package import (
    PackageReceiveRequest, PackageDeliverRequest, PackageCancelRequest,
    PackageReceiveResponse, PackageDeliverResponse, PackageCancelResponse,
    PackageFeeCalculation, PaymentMethod, CancellationReason
)
from decimal import Decimal
from typing import Tuple


class PackageStateService:
    """Servicio para manejar las transiciones de estado de los paquetes"""

    # Transiciones de estado permitidas
    ALLOWED_TRANSITIONS = {
        PackageStatus.ANUNCIADO: [PackageStatus.RECIBIDO, PackageStatus.CANCELADO],
        PackageStatus.RECIBIDO: [PackageStatus.ENTREGADO, PackageStatus.CANCELADO],
        PackageStatus.ENTREGADO: [],  # Estado final
        PackageStatus.CANCELADO: []   # Estado final
    }

    @classmethod
    def is_transition_allowed(cls, current_status: PackageStatus, new_status: PackageStatus) -> bool:
        """Verificar si una transición de estado está permitida"""
        allowed = cls.ALLOWED_TRANSITIONS.get(current_status, [])
        
        # Comparar por valor (string) en lugar de por referencia de objeto
        current_value = current_status.value if hasattr(current_status, 'value') else str(current_status)
        new_value = new_status.value if hasattr(new_status, 'value') else str(new_status)
        allowed_values = [status.value if hasattr(status, 'value') else str(status) for status in allowed]
        
        print(f"🔍 VALIDATION: current_status={current_status} (value: {current_value})")
        print(f"🔍 VALIDATION: new_status={new_status} (value: {new_value})")
        print(f"🔍 VALIDATION: allowed transitions={allowed} (values: {allowed_values})")
        print(f"🔍 VALIDATION: new_value in allowed_values? {new_value in allowed_values}")
        
        # Usar comparación por valor
        return new_value in allowed_values

    @classmethod
    async def update_package_status(
        cls,
        db: Session,
        package: Package,
        new_status: PackageStatus,
        changed_by: str = "system",
        additional_data: Optional[Dict[str, Any]] = None,
        observations: Optional[str] = None
    ) -> PackageHistory:
        """Actualizar el estado de un paquete y registrar el cambio en el historial"""

        # Verificar si la transición está permitida
        if not cls.is_transition_allowed(package.status, new_status):
            raise ValueError(f"Transición no permitida: {package.status.value} -> {new_status.value}")

        # Guardar el estado anterior
        previous_status = package.status

        # Actualizar el estado del paquete
        package.status = new_status
        package.updated_at = get_colombia_now()

        # Actualizar timestamps específicos según el estado
        now = get_colombia_now()
        if new_status == PackageStatus.RECIBIDO and not package.received_at:
            package.received_at = now
        elif new_status == PackageStatus.ENTREGADO and not package.delivered_at:
            package.delivered_at = now
        elif new_status == PackageStatus.CANCELADO and not package.cancelled_at:
            package.cancelled_at = now

        # Crear entrada en el historial
        history_entry = PackageHistory(
            id=uuid.uuid4(),
            package_id=package.id,  # Usar Integer directamente
            previous_status=previous_status.value if previous_status else None,
            new_status=new_status.value,
            changed_at=now,
            changed_by=changed_by,
            additional_data=additional_data or {},
            observations=observations
        )

        # Guardar en la base de datos
        db.add(history_entry)
        db.commit()
        db.refresh(history_entry)
        db.refresh(package)

        # Enviar notificación SMS automáticamente si hay un cliente asociado
        # NOTA: Email se envía manualmente mediante botón en la interfaz
        try:
            await cls._send_sms_notification(db, package, new_status, changed_by)
        except Exception as e:
            # Log error but don't fail the package update
            import logging
            logger = logging.getLogger("package_state_service")
            logger.warning(f"Error enviando SMS para paquete {package.id}: {str(e)}")

        return history_entry

    @classmethod
    def get_package_history(cls, db: Session, package_id: int) -> List[PackageHistory]:
        """Obtener el historial completo de un paquete"""
        return db.query(PackageHistory).filter(
            PackageHistory.package_id == package_id
        ).order_by(PackageHistory.changed_at.desc()).all()

    @classmethod
    def get_announcement_history(cls, db: Session, guide_number: str) -> List[PackageHistory]:
        """Obtener el historial completo de un anuncio por número de guía"""
        # Buscar el anuncio
        announcement = cls.get_announcement_by_guide_number(db, guide_number)
        if not announcement:
            return []

        # Si el anuncio tiene un paquete asociado, obtener su historial
        if announcement.package_id:
            return cls.get_package_history(db, str(announcement.package_id))

        # Si no tiene paquete asociado, buscar historial por guide_number en additional_data
        return db.query(PackageHistory).filter(
            PackageHistory.additional_data['guide_number'].astext == guide_number
        ).order_by(PackageHistory.changed_at.desc()).all()

    @classmethod
    def get_package_by_tracking_number(cls, db: Session, tracking_number: str) -> Optional[Package]:
        """Obtener un paquete por su número de seguimiento"""
        return db.query(Package).filter(Package.tracking_number == tracking_number).first()

    @classmethod
    def get_announcement_by_guide_number(cls, db: Session, guide_number: str) -> Optional[Package]:
        """Obtener un anuncio por su número de guía"""
        return db.query(Package).filter(Package.guide_number == guide_number).first()

    @classmethod
    def create_announcement(cls, db: Session, customer_name: str, customer_phone: str, guide_number: str, tracking_code: str, created_by: str = "system") -> Package:
        """Crear un nuevo anuncio de paquete"""
        announcement = Package(
            id=uuid.uuid4(),
            customer_name=customer_name.upper(),
            customer_phone=customer_phone,
            guide_number=guide_number.upper(),
            tracking_code=tracking_code,
            is_active=True,
            is_processed=False,
            announced_at=get_colombia_now(),
            created_at=get_colombia_now(),
            updated_at=get_colombia_now()
        )

        db.add(announcement)
        db.commit()
        db.refresh(announcement)

        # Crear entrada inicial en el historial
        history_entry = PackageHistory(
            id=uuid.uuid4(),
            package_id=None,  # No hay paquete aún
            previous_status=None,
            new_status=PackageStatus.ANUNCIADO.value,
            changed_at=get_colombia_now(),
            changed_by=created_by,
            additional_data={
                "customer_name": customer_name,
                "customer_phone": customer_phone,
                "guide_number": guide_number,
                "tracking_code": tracking_code
            },
            observations=f"Anuncio creado para {customer_name}"
        )

        db.add(history_entry)
        db.commit()
        db.refresh(history_entry)

        return announcement

    @classmethod
    def process_announcement_to_received(
        cls,
        db: Session,
        guide_number: str,
        package_type: PackageType,
        package_condition: PackageCondition,
        observations: str = "",
        changed_by: str = "system"
    ) -> Dict[str, Any]:
        """Procesar un anuncio y cambiarlo a estado RECIBIDO - Maneja ambas tablas"""

        # Buscar el anuncio existente
        announcement = cls.get_announcement_by_guide_number(db, guide_number)
        if not announcement:
            raise ValueError(f"No se encontró un anuncio con el número de guía: {guide_number}")

        # Verificar que el anuncio no esté procesado
        if announcement.is_processed:
            raise ValueError(f"El anuncio {guide_number} ya fue procesado")

        # Buscar si ya existe un paquete con este tracking_number
        # Usar guide_number como tracking_number del paquete
        package = cls.get_package_by_tracking_number(db, guide_number)

        if package:
            # Paquete ya existe - verificar que esté en estado ANUNCIADO
            if package.status != PackageStatus.ANUNCIADO:
                raise ValueError(f"El paquete {guide_number} no está en estado ANUNCIADO. Estado actual: {package.status.value}")

            # Actualizar el paquete existente
            package.package_type = package_type
            package.package_condition = package_condition
            # package.observations = observations  # Campo eliminado del modelo Package

            # Cambiar el estado a RECIBIDO
            history_entry = cls.update_package_status(
                db=db,
                package=package,
                new_status=PackageStatus.RECIBIDO,
                changed_by=changed_by,
                additional_data={
                    "package_type": package_type.value,
                    "package_condition": package_condition.value,
                    "observations": observations
                },
                observations=f"Paquete recibido. Tipo: {package_type.value}, Condición: {package_condition.value}"
            )

            package_id = str(package.id)
        else:
            # Crear nuevo paquete
            # TODO: Buscar o crear cliente basado en customer_name y customer_phone
            # Por ahora, asignar un customer_id temporal para testing
            customer_id = None  # NULL temporal hasta implementar búsqueda de cliente

            # Generar access_code único
            import secrets
            import string
            access_code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))

            new_package = Package(
                tracking_number=guide_number,
                customer_id=customer_id,  # TODO: Implementar búsqueda/creación de cliente
                status=PackageStatus.RECIBIDO,
                package_type=package_type,
                package_condition=package_condition,
                access_code=access_code,
                announced_at=announcement.announced_at,
                received_at=get_colombia_now(),
                created_at=get_colombia_now(),
                updated_at=get_colombia_now()
            )

            db.add(new_package)
            db.commit()
            db.refresh(new_package)

            # Obtener nombre real del operador si es un ID de usuario
            operator_name = changed_by
            if changed_by and changed_by.startswith("user_"):
                try:
                    user_id = int(changed_by.replace("user_", ""))
                    operator = db.query(User).filter(User.id == user_id).first()
                    if operator:
                        operator_name = operator.username or operator.first_name or f"Usuario {user_id}"
                except (ValueError, AttributeError):
                    operator_name = changed_by

            # **IMPORTANTE: Crear primero el evento ANUNCIADO si no existe**
            existing_announced = db.query(PackageHistory).filter(
                PackageHistory.package_id == new_package.id,
                PackageHistory.new_status == PackageStatus.ANUNCIADO.value
            ).first()
            
            if not existing_announced:
                # Crear evento ANUNCIADO
                announced_entry = PackageHistory(
                    id=uuid.uuid4(),
                    package_id=new_package.id,
                    previous_status=None,
                    new_status=PackageStatus.ANUNCIADO.value,
                    changed_at=announcement.announced_at,  # Usar fecha del anuncio
                    changed_by="system",
                    additional_data={
                        "customer_name": announcement.customer_name,
                        "customer_phone": announcement.customer_phone,
                        "guide_number": announcement.guide_number,
                        "tracking_code": announcement.tracking_code
                    },
                    observations=f"Paquete anunciado por {announcement.customer_name}"
                )
                db.add(announced_entry)

            # Crear entrada en el historial para RECIBIDO
            history_entry = PackageHistory(
                id=uuid.uuid4(),
                package_id=new_package.id,  # Usar Integer directamente
                previous_status=PackageStatus.ANUNCIADO.value,
                new_status=PackageStatus.RECIBIDO.value,
                changed_at=get_colombia_now(),
                changed_by=operator_name,  # Usar nombre real del operador
                additional_data={
                    "package_type": package_type.value,
                    "package_condition": package_condition.value,
                    "observations": observations,
                    "operator_name": operator_name
                },
                observations=f"Paquete recibido por {operator_name}. Tipo: {package_type.value}, Condición: {package_condition.value}"
            )

            db.add(history_entry)

        # Actualizar el anuncio como procesado
        announcement.is_processed = True
        announcement.processed_at = get_colombia_now()
        announcement.updated_at = get_colombia_now()

        # Determinar el package_id correcto
        if package:
            # Paquete ya existía
            announcement.package_id = package.id  # Usar INTEGER directamente
            package_id = str(package.id)
        else:
            # Paquete fue creado
            announcement.package_id = new_package.id  # Usar INTEGER directamente
            package_id = str(new_package.id)

        db.commit()
        db.refresh(announcement)

        return {
            "success": True,
            "message": f"Anuncio {guide_number} procesado y paquete actualizado a estado RECIBIDO",
            "announcement_id": str(announcement.id),
            "package_id": package_id,
            "status": PackageStatus.RECIBIDO.value,
            "history_entry_id": str(history_entry.id)
        }

    @classmethod
    async def _send_sms_notification(
        cls,
        db: Session,
        package: Package,
        new_status: PackageStatus,
        changed_by: str
    ):
        """Enviar notificación SMS cuando cambia el estado del paquete"""
        # Solo enviar SMS si el paquete tiene un cliente asociado
        if not package.customer_id:
            return

        # Mapear estados de paquete a eventos de notificación
        event_mapping = {
            PackageStatus.ANUNCIADO: NotificationEvent.PACKAGE_ANNOUNCED,
            PackageStatus.RECIBIDO: NotificationEvent.PACKAGE_RECEIVED,
            PackageStatus.ENTREGADO: NotificationEvent.PACKAGE_DELIVERED,
            PackageStatus.CANCELADO: NotificationEvent.PACKAGE_CANCELLED
        }

        event_type = event_mapping.get(new_status)
        if not event_type:
            return  # No hay evento definido para este estado

        # Obtener el número de teléfono del cliente
        customer_phone = None
        if package.customer:
            customer_phone = package.customer.phone

        if not customer_phone:
            return  # No hay teléfono para enviar SMS

        # Preparar variables para la plantilla
        variables = {
            "guide_number": package.tracking_number,
            "tracking_code": getattr(package, 'tracking_code', 'N/A'),
            "customer_name": package.customer.full_name if package.customer else "Sin cliente",
            "package_type": package.package_type.value if package.package_type else "normal",
            "package_condition": package.package_condition.value if package.package_condition else "ok"
        }

        # Agregar timestamps según el estado
        if new_status == PackageStatus.RECIBIDO and package.received_at:
            variables["received_at"] = package.received_at.strftime("%d/%m/%Y %H:%M")
        elif new_status == PackageStatus.ENTREGADO and package.delivered_at:
            variables["delivered_at"] = package.delivered_at.strftime("%d/%m/%Y %H:%M")

        # Enviar SMS usando el servicio
        sms_service = SMSService()
        try:
            from app.schemas.notification import SMSByEventRequest
            await sms_service.send_sms_by_event(
                db=db,
                event_request=SMSByEventRequest(
                    event_type=event_type,
                    package_id=package.id,
                    customer_id=package.customer_id,
                    custom_variables=variables,
                    priority="normal",
                    is_test=False
                )
            )
        except Exception as e:
            # Log error but don't fail the package update
            import logging
            logger = logging.getLogger("package_state_service")
            logger.warning(f"No se pudo enviar SMS para paquete {package.id}: {str(e)}")

    @classmethod
    async def _send_email_notification(
        cls,
        db: Session,
        package: Package,
        new_status: PackageStatus,
        changed_by: str
    ):
        """Enviar notificación por email cuando cambia el estado del paquete"""
        # Solo enviar email si el paquete tiene un cliente asociado con email
        if not package.customer_id:
            return

        # Obtener email del cliente
        customer_email = None
        if package.customer and hasattr(package.customer, 'email'):
            customer_email = package.customer.email

        if not customer_email:
            return  # No hay email para enviar

        # Mapear estados de paquete a eventos de notificación
        event_mapping = {
            PackageStatus.ANUNCIADO: NotificationEvent.PACKAGE_ANNOUNCED,
            PackageStatus.RECIBIDO: NotificationEvent.PACKAGE_RECEIVED,
            PackageStatus.ENTREGADO: NotificationEvent.PACKAGE_DELIVERED,
            PackageStatus.CANCELADO: NotificationEvent.PACKAGE_CANCELLED
        }

        event_type = event_mapping.get(new_status)
        if not event_type:
            return  # No hay evento definido para este estado

        # Preparar variables para la plantilla
        variables = {
            "guide_number": package.tracking_number,
            "tracking_code": getattr(package, 'tracking_code', package.tracking_number),
            "customer_name": package.customer.full_name if package.customer else "Cliente",
            "package_type": package.package_type.value if package.package_type else "normal",
            "tracking_url": f"{settings.tracking_base_url}/{package.tracking_number}"
        }

        # Agregar timestamps según el estado
        if new_status == PackageStatus.RECIBIDO and package.received_at:
            variables["received_at"] = package.received_at.strftime("%d/%m/%Y %H:%M")
        elif new_status == PackageStatus.ENTREGADO and package.delivered_at:
            variables["delivered_at"] = package.delivered_at.strftime("%d/%m/%Y %H:%M")
            variables["recipient_name"] = getattr(package, 'delivered_to', 'Cliente')
        elif new_status == PackageStatus.CANCELADO:
            from app.utils.datetime_utils import get_colombia_now
            variables["cancelled_at"] = get_colombia_now().strftime("%d/%m/%Y %H:%M")

        # Enviar email usando el servicio
        try:
            from app.services.email_service import EmailService
            email_service = EmailService()
            
            await email_service.send_email_by_event(
                db=db,
                event_type=event_type,
                recipient=customer_email,
                variables=variables,
                package_id=package.id,
                customer_id=str(package.customer_id) if package.customer_id else None,
                priority=NotificationPriority.MEDIA,
                is_test=False
            )
        except Exception as e:
            # Log error but don't fail the package update
            import logging
            logger = logging.getLogger("package_state_service")
            logger.warning(f"No se pudo enviar email para paquete {package.id}: {str(e)}")

    # ========================================
    # NUEVOS MÉTODOS PARA TRANSICIONES AVANZADAS
    # ========================================

    @classmethod
    def calculate_final_fees(
        cls,
        db: Session,
        package: Package,
        current_time: datetime = None
    ) -> PackageFeeCalculation:
        """Calcular tarifas finales incluyendo almacenamiento por días - DINÁMICO desde .env"""

        if current_time is None:
            current_time = get_colombia_now()

        # Calcular días de almacenamiento
        storage_days = cls._calculate_storage_days(package, current_time)

        # Tarifas base por tipo - DINÁMICO usando configuración desde .env
        from app.config import settings
        
        if package.package_type == PackageType.NORMAL:
            base_fee = Decimal(str(settings.base_delivery_rate_normal))
            print(f"💰 Tarifa NORMAL aplicada: {base_fee} COP (desde .env)")
        elif package.package_type == PackageType.EXTRA_DIMENSIONADO:
            base_fee = Decimal(str(settings.base_delivery_rate_extra_dimensioned))
            print(f"💰 Tarifa EXTRA DIMENSIONADO aplicada: {base_fee} COP (desde .env)")
        else:
            # Fallback para tipos no reconocidos
            base_fee = Decimal(str(settings.base_delivery_rate_normal))
            print(f"⚠️ Tipo no reconocido, usando tarifa NORMAL: {base_fee} COP")

        # Tarifa de almacenamiento por día - usando configuración desde .env
        storage_fee_per_day = Decimal(str(settings.base_storage_rate))
        storage_fee = storage_fee_per_day * storage_days
        
        print(f"📦 Días de almacenamiento: {storage_days} | Tarifa por día: {storage_fee_per_day} COP | Total almacenamiento: {storage_fee} COP")

        # Total final
        total_amount = base_fee + storage_fee

        return PackageFeeCalculation(
            base_fee=base_fee,
            storage_fee=storage_fee,
            storage_days=storage_days,
            total_amount=total_amount,
            breakdown={
                "entrega": float(base_fee),
                "almacenamiento": float(storage_fee),
                "dias": storage_days
            },
            calculated_at=current_time
        )

    @classmethod
    def receive_package_from_announcement(
        cls,
        db: Session,
        request: PackageReceiveRequest
    ) -> PackageReceiveResponse:
        """Método completo para recepción de paquetes desde anuncios"""

        # Validar anuncio
        announcement = cls._validate_announcement_for_receipt(db, request.announcement_id)

        # Verificar si ya existe un paquete con este tracking_code (que se usa como tracking_number)
        # IMPORTANTE: El tracking_code del anuncio se convierte en tracking_number del paquete
        existing_package = cls.get_package_by_tracking_number(db, announcement.tracking_code)
        if existing_package:
            # Si ya existe un paquete con este tracking_code, verificar si el anuncio ya fue procesado
            if announcement.is_processed:
                raise ValueError(f"El anuncio {announcement.tracking_code} ya fue procesado")
            else:
                # El paquete existe pero el anuncio no está marcado como procesado
                # Esto indica un estado inconsistente - marcar el anuncio como procesado y actualizar el paquete existente
                announcement.is_processed = True
                announcement.processed_at = get_colombia_now()
                announcement.updated_at = get_colombia_now()
                announcement.package_id = existing_package.id
                db.commit()
                
                # Actualizar el paquete existente en lugar de crear uno nuevo
                # IMPORTANTE: Guardar el estado anterior ANTES de modificarlo
                previous_status = existing_package.status
                # Convertir a string si es un enum, siguiendo el patrón de update_package_status
                if previous_status is None:
                    previous_status_value = None
                elif hasattr(previous_status, 'value'):
                    previous_status_value = previous_status.value
                elif isinstance(previous_status, str):
                    previous_status_value = previous_status
                else:
                    previous_status_value = str(previous_status)
                
                existing_package.package_type = request.package_type.value
                existing_package.package_condition = request.package_condition.value
                
                # Solo cambiar estado si aún no está recibido
                new_status_value = PackageStatus.RECIBIDO.value
                if previous_status_value != new_status_value:
                    existing_package.status = new_status_value
                    existing_package.received_at = get_colombia_now()
                
                existing_package.updated_at = get_colombia_now()
                
                # Calcular tarifas actualizadas
                fee_calculation = cls._calculate_fees_for_new_package(request.package_type)
                existing_package.base_fee = fee_calculation.base_fee
                existing_package.storage_fee = fee_calculation.storage_fee
                existing_package.total_amount = fee_calculation.total_amount
                
                # Si no tiene posición, generar una
                if not existing_package.posicion:
                    existing_package.posicion = cls._generate_baroti(db)
                
                # Actualizar cliente si es necesario
                customer = cls._find_or_create_customer_from_announcement(db, announcement)
                if customer:
                    existing_package.customer_id = customer.id
                
                db.commit()
                db.refresh(existing_package)
                
                # Obtener nombre del operador
                operator_name = "Sistema"
                if request.operator_id:
                    try:
                        operator = db.query(User).filter(User.id == request.operator_id).first()
                        if operator:
                            operator_name = operator.username or operator.first_name or f"Usuario {request.operator_id}"
                    except Exception as e:
                        print(f"⚠️ Error obteniendo nombre del operador: {e}")
                        operator_name = f"Operador {request.operator_id}"
                
                # Registrar en historial si cambió de estado
                # Comparar correctamente considerando None
                # Si previous_status_value es None o vacío, usar None explícitamente
                prev_status_for_history = None
                if previous_status_value and isinstance(previous_status_value, str) and previous_status_value.strip():
                    prev_status_for_history = previous_status_value
                
                if prev_status_for_history != new_status_value:
                    history_entry = PackageHistory(
                        id=uuid.uuid4(),
                        package_id=existing_package.id,
                        previous_status=prev_status_for_history,  # None o string válido
                        new_status=new_status_value,
                        changed_at=get_colombia_now(),
                        changed_by=operator_name,
                        additional_data={
                            "announcement_id": str(request.announcement_id),
                            "package_type": request.package_type.value,
                            "package_condition": request.package_condition.value,
                            "posicion": existing_package.posicion,
                            "operator_id": request.operator_id,
                            "operator_name": operator_name,
                        },
                        observations=request.observations
                    )
                    db.add(history_entry)
                    db.commit()
                
                # Retornar respuesta
                return PackageReceiveResponse(
                    success=True,
                    package_id=existing_package.id,
                    tracking_number=existing_package.tracking_number,
                    access_code=existing_package.access_code,
                    baroti=existing_package.posicion,  # baroti es el nombre en el schema, posicion es el campo en la BD
                    total_amount=existing_package.total_amount,
                    base_fee=existing_package.base_fee,
                    storage_fee=existing_package.storage_fee,
                    storage_days=0,
                    message=f"Paquete {announcement.guide_number} actualizado exitosamente",
                    received_at=existing_package.received_at or get_colombia_now()
                )

        # Calcular tarifas basadas en el anuncio (sin días de almacenamiento aún)
        fee_calculation = cls._calculate_fees_for_new_package(request.package_type)

        # Generar access code único
        access_code = cls._generate_access_code(db)
        
        # Generar BAROTI automáticamente
        posicion = cls._generate_baroti(db)

        # Buscar o crear cliente basado en los datos del anuncio
        customer = cls._find_or_create_customer_from_announcement(db, announcement)
        
        # Crear paquete desde anuncio
        new_package = Package(
            tracking_number=announcement.tracking_code,  # Código único del paquete
            guide_number=announcement.guide_number,      # Número de guía del transportador
            customer_id=customer.id if customer else None,
            status=PackageStatus.RECIBIDO.value,
            package_type=request.package_type.value,
            package_condition=request.package_condition.value,
            access_code=access_code,
            posicion=posicion,
            announced_at=announcement.announced_at,
            received_at=get_colombia_now(),
            base_fee=fee_calculation.base_fee,
            storage_fee=fee_calculation.storage_fee,
            total_amount=fee_calculation.total_amount,
            created_at=get_colombia_now(),
            updated_at=get_colombia_now()
        )

        db.add(new_package)
        db.commit()  # Commit package first to get ID
        db.refresh(new_package)

        # Actualizar anuncio
        announcement.is_processed = True
        announcement.processed_at = get_colombia_now()
        announcement.package_id = new_package.id  # Usar INTEGER directamente
        announcement.updated_at = get_colombia_now()

        # Obtener nombre real del operador
        operator_name = "Sistema"
        if request.operator_id:
            try:
                operator = db.query(User).filter(User.id == request.operator_id).first()
                if operator:
                    operator_name = operator.username or operator.first_name or f"Usuario {request.operator_id}"
            except Exception as e:
                print(f"⚠️ Error obteniendo nombre del operador: {e}")
                operator_name = f"Operador {request.operator_id}"

        # Registrar en historial
        history_entry = PackageHistory(
            id=uuid.uuid4(),
            package_id=new_package.id,  # Usar Integer directamente
            previous_status=PackageStatus.ANUNCIADO.value,
            new_status=PackageStatus.RECIBIDO.value,
            changed_at=get_colombia_now(),
            changed_by=operator_name,  # Usar nombre real del operador
            additional_data={
                "announcement_id": str(request.announcement_id),
                "package_type": request.package_type.value,
                "package_condition": request.package_condition.value,
                "posicion": posicion,  # Usar la posición generada, no del request
                "operator_id": request.operator_id,
                "operator_name": operator_name,  # Incluir nombre del operador
                "fee_calculation": {
                    "base_fee": float(fee_calculation.base_fee),
                    "storage_fee": float(fee_calculation.storage_fee),
                    "storage_days": fee_calculation.storage_days,
                    "total_amount": float(fee_calculation.total_amount)
                }
            },
            observations=f"Paquete recibido por {operator_name}. {request.observations or ''}"
        )

        db.add(history_entry)

        # NUEVO: Registrar evento completo en package_events
        try:
            # Obtener rol del operador
            operator_role = "SISTEMA"
            if request.operator_id:
                operator = db.query(User).filter(User.id == request.operator_id).first()
                if operator:
                    operator_role = operator.role.value if hasattr(operator.role, 'value') else str(operator.role)
            
            package_event = PackageEvent.from_package_reception(
                package=new_package,
                announcement=announcement,
                operator_id=request.operator_id,
                operator_name=operator_name,
                operator_role=operator_role,
                fee_calculation=fee_calculation,
                file_ids=None,  # Se actualizará cuando se suban las imágenes
                observations=request.observations,
                additional_data={
                    "received_from": "anuncio",
                    "baroti_generated": baroti
                }
            )
            db.add(package_event)
        except Exception as e:
            print(f"⚠️ Error registrando evento de recepción: {e}")

        # Commit announcement and history changes
        db.commit()
        db.refresh(announcement)
        db.refresh(history_entry)

        # Enviar notificación SMS
        try:
            cls._send_sms_notification(db, new_package, PackageStatus.RECIBIDO, f"operator_{request.operator_id}")
        except Exception as e:
            print(f"Error sending SMS for package {new_package.id}: {str(e)}")

        return PackageReceiveResponse(
            success=True,
            package_id=new_package.id,
            tracking_number=new_package.tracking_number,
            access_code=new_package.access_code,
            baroti=new_package.posicion,  # baroti es el nombre en el schema, posicion es el campo en la BD
            total_amount=fee_calculation.total_amount,
            base_fee=fee_calculation.base_fee,
            storage_fee=fee_calculation.storage_fee,
            storage_days=fee_calculation.storage_days,
            message=f"Paquete {announcement.guide_number} recibido exitosamente",
            received_at=new_package.received_at
        )

    @classmethod
    async def deliver_package_with_payment(
        cls,
        db: Session,
        package_id: int,
        request: PackageDeliverRequest
    ) -> PackageDeliverResponse:
        """Método completo para entrega con registro de pago"""

        # Obtener paquete
        package = db.query(Package).filter(Package.id == package_id).first()
        if not package:
            raise ValueError(f"Paquete {package_id} no encontrado")

        # Validar que se puede entregar
        cls._validate_package_for_delivery(package, request.customer_id)

        # Obtener operador
        operator = db.query(User).filter(User.id == request.operator_id).first()
        operator_name = operator.full_name if operator else f"Operador {request.operator_id}"

        # Cambiar estado a DELIVERED
        # Guardar datetime antes de actualizar estado para asegurar que delivered_at esté disponible
        from app.utils.datetime_utils import get_colombia_now
        delivery_datetime = get_colombia_now()
        
        history_entry = await cls.update_package_status(
            db=db,
            package=package,
            new_status=PackageStatus.ENTREGADO,
            changed_by=f"operator_{request.operator_id}",
            additional_data={
                "payment_method": request.payment_method.value,
                "payment_amount": float(request.payment_amount),
                "customer_id": str(request.customer_id) if request.customer_id else None,  # UUID se serializa como string
                "operator_id": request.operator_id,
                "customer_signature": request.customer_signature
            },
            observations=f"Entregado por {operator_name}. Pago: {request.payment_method.value} - ${request.payment_amount}"
        )
        
        # NUEVO: Registrar evento completo de entrega
        try:
            operator_role = operator.role.value if hasattr(operator.role, 'value') else str(operator.role) if operator else "OPERADOR"
            
            package_event = PackageEvent.from_package_delivery(
                package=package,
                payment_method=request.payment_method.value,
                payment_amount=request.payment_amount,
                operator_id=request.operator_id,
                operator_name=operator_name,
                operator_role=operator_role,
                file_ids={"signature": []} if request.customer_signature else None,
                observations=f"Entregado por {operator_name}. Pago: {request.payment_method.value}",
                additional_data={
                    "customer_signature": request.customer_signature,
                    "delivery_completed": True
                }
            )
            db.add(package_event)
        except Exception as e:
            print(f"⚠️ Error registrando evento de entrega: {e}")
        
        # Liberar código BAROTI
        if package.posicion:
            package.posicion = None
        
        # Asegurar commit final y refresh para obtener delivered_at actualizado
        db.commit()
        db.refresh(package)
        
        # Usar delivered_at del paquete si está disponible, sino usar el datetime que guardamos
        final_delivered_at = package.delivered_at if package.delivered_at else delivery_datetime

        return PackageDeliverResponse(
            success=True,
            package_id=package.id,
            tracking_number=package.tracking_number,
            delivered_at=final_delivered_at,  # Asegurado que siempre tenga valor
            payment_method=request.payment_method,
            payment_amount=request.payment_amount,
            operator_name=operator_name,
            message=f"Paquete {package.tracking_number} entregado exitosamente"
        )

    @classmethod
    async def cancel_package_with_reason(
        cls,
        db: Session,
        package_id: int,
        request: PackageCancelRequest
    ) -> PackageCancelResponse:
        """Método completo para cancelación con lógica de reembolso"""

        # Obtener paquete
        package = db.query(Package).filter(Package.id == package_id).first()
        if not package:
            raise ValueError(f"Paquete {package_id} no encontrado")

        # Verificar que se puede cancelar
        if package.status == PackageStatus.ENTREGADO:
            raise ValueError("No se puede cancelar un paquete ya entregado")

        # Cambiar estado a CANCELLED
        # Guardar datetime antes de actualizar estado para asegurar que cancelled_at esté disponible
        from app.utils.datetime_utils import get_colombia_now
        cancellation_datetime = get_colombia_now()
        
        history_entry = await cls.update_package_status(
            db=db,
            package=package,
            new_status=PackageStatus.CANCELADO,
            changed_by=f"operator_{request.operator_id}",
            additional_data={
                "cancellation_reason": request.reason.value,
                "refund_amount": float(request.refund_amount),
                "operator_id": request.operator_id
            },
            observations=f"Cancelado por: {request.reason.value}. {request.observations or ''}"
        )
        
        # NUEVO: Registrar evento completo de cancelación
        try:
            operator = db.query(User).filter(User.id == request.operator_id).first()
            operator_name = operator.username if operator else f"Operador {request.operator_id}"
            operator_role = operator.role.value if hasattr(operator.role, 'value') else str(operator.role) if operator else "OPERADOR"
            
            package_event = PackageEvent.from_package_cancellation(
                package=package,
                cancellation_reason=request.reason.value,
                operator_id=request.operator_id,
                operator_name=operator_name,
                operator_role=operator_role,
                observations=request.observations,
                additional_data={
                    "refund_amount": float(request.refund_amount),
                    "cancellation_code": request.reason.value
                }
            )
            db.add(package_event)
        except Exception as e:
            print(f"⚠️ Error registrando evento de cancelación: {e}")
        
        # Liberar código BAROTI
        if package.posicion:
            package.posicion = None
        
        # Asegurar commit final y refresh para obtener cancelled_at actualizado
        db.commit()
        db.refresh(package)
        
        # Usar cancelled_at del paquete si está disponible, sino usar el datetime que guardamos
        final_cancelled_at = package.cancelled_at if package.cancelled_at else cancellation_datetime

        return PackageCancelResponse(
            success=True,
            package_id=package.id,
            tracking_number=package.tracking_number,
            cancelled_at=final_cancelled_at,  # Asegurado que siempre tenga valor
            reason=request.reason,
            refund_amount=request.refund_amount,
            message=f"Paquete {package.tracking_number} cancelado exitosamente"
        )

    # ========================================
    # MÉTODOS DE VALIDACIÓN Y UTILIDADES
    # ========================================

    @classmethod
    def _validate_announcement_for_receipt(cls, db: Session, tracking_code: str) -> PackageAnnouncementNew:
        """Validar que un anuncio se puede procesar para recepción"""

        announcement = db.query(PackageAnnouncementNew).filter(
            PackageAnnouncementNew.tracking_code == tracking_code
        ).first()

        if not announcement:
            raise ValueError(f"Anuncio con tracking code {tracking_code} no encontrado")

        if announcement.is_processed:
            raise ValueError(f"Anuncio {announcement.guide_number} ya fue procesado")

        if not announcement.is_active:
            raise ValueError(f"Anuncio {announcement.guide_number} está cancelado")

        # Verificar tiempo máximo de espera (30 días)
        max_wait_days = 30
        announced_date = announcement.announced_at.replace(tzinfo=None) if announcement.announced_at.tzinfo else announcement.announced_at
        current_date = get_colombia_now().replace(tzinfo=None)

        if (current_date - announced_date).days > max_wait_days:
            raise ValueError(f"Anuncio expirado (más de {max_wait_days} días)")

        return announcement

    @classmethod
    def _validate_package_for_delivery(cls, package: Package, customer_id: Optional[UUID] = None) -> None:
        """Validar que un paquete se puede entregar"""

        if package.status != PackageStatus.RECIBIDO:
            raise ValueError(f"Paquete no está en estado RECIBIDO (estado actual: {package.status.value})")

        # Validar que el customer_id coincide con el propietario del paquete (si se proporciona)
        if customer_id and package.customer_id and package.customer_id != customer_id:
            raise ValueError("Cliente no coincide con el propietario del paquete")

    @classmethod
    def _calculate_storage_days(cls, package: Package, current_time: datetime) -> int:
        """Calcular días de almacenamiento basado en horas completas (cada 24 horas = 1 día)"""

        if not package.received_at:
            # Si aún no se ha recibido, no hay días de almacenamiento
            return 0
        else:
            # Si ya se recibió, calcular desde la recepción
            received_date = package.received_at.replace(tzinfo=None) if package.received_at.tzinfo else package.received_at
            current_date = current_time.replace(tzinfo=None)
            
            # Calcular diferencia en horas
            time_diff = current_date - received_date
            total_hours = time_diff.total_seconds() / 3600
            
            # Calcular días completos (cada 24 horas = 1 día)
            # 22 horas = 0 días, 25 horas = 1 día, 47 horas = 1 día, 48 horas = 2 días
            import math
            storage_days = math.floor(total_hours / 24)
            
            return max(0, storage_days)  # No días negativos

    @classmethod
    def _calculate_fees_for_new_package(cls, package_type: PackageType) -> PackageFeeCalculation:
        """Calcular tarifas para un paquete nuevo (sin días de almacenamiento) - DINÁMICO desde .env"""
        from app.config import settings
        
        # Tarifas base por tipo usando configuración DINÁMICA desde .env
        if package_type == PackageType.NORMAL:
            base_fee = Decimal(str(settings.base_delivery_rate_normal))
            print(f"💰 Tarifa NORMAL aplicada: {base_fee} COP (desde .env: BASE_DELIVERY_RATE_NORMAL)")
        elif package_type == PackageType.EXTRA_DIMENSIONADO:
            base_fee = Decimal(str(settings.base_delivery_rate_extra_dimensioned))
            print(f"💰 Tarifa EXTRA DIMENSIONADO aplicada: {base_fee} COP (desde .env: BASE_DELIVERY_RATE_EXTRA_DIMENSIONED)")
        else:
            base_fee = Decimal(str(settings.base_delivery_rate_normal))
            print(f"⚠️ Tipo de paquete no reconocido, usando tarifa NORMAL: {base_fee} COP")

        storage_fee = Decimal('0.00')  # Sin almacenamiento para paquetes nuevos
        total_amount = base_fee + storage_fee

        return PackageFeeCalculation(
            base_fee=base_fee,
            storage_fee=storage_fee,
            storage_days=0,
            total_amount=total_amount,
            breakdown={
                "entrega": float(base_fee),
                "almacenamiento": float(storage_fee),
                "dias": 0
            },
            calculated_at=get_colombia_now()
        )

    @classmethod
    def _generate_access_code(cls, db: Session) -> str:
        """Generar código de acceso único"""
        import secrets
        import string

        while True:
            access_code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))

            # Verificar unicidad
            existing = db.query(Package).filter(Package.access_code == access_code).first()
            if not existing:
                return access_code

    @classmethod
    def _find_or_create_customer_from_announcement(cls, db: Session, announcement) -> Optional[Customer]:
        """Buscar o crear cliente basado en los datos del anuncio"""
        from app.models.customer import Customer
        
        # Buscar cliente existente por teléfono
        if announcement.customer_phone:
            customer = db.query(Customer).filter(Customer.phone == announcement.customer_phone).first()
            if customer:
                return customer
        
        # Si no existe, crear nuevo cliente
        if announcement.customer_name or announcement.customer_phone:
            # Dividir el nombre en first_name y last_name
            name_parts = (announcement.customer_name or "Cliente Sin Nombre").split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            new_customer = Customer(
                first_name=first_name,
                last_name=last_name,
                full_name=announcement.customer_name or "Cliente Sin Nombre",
                phone=announcement.customer_phone or None,
                email=None,
                address_street=None,
                address_city=None,
                address_state=None,
                address_zip=None,
                address_country="Colombia",
                tower=None,
                apartment=None,
                created_at=get_colombia_now(),
                updated_at=get_colombia_now()
            )
            db.add(new_customer)
            db.commit()
            db.refresh(new_customer)
            return new_customer
        
        return None

    @classmethod
    def _generate_baroti(cls, db: Session) -> str:
        """Generar código BAROTI único (00-99)"""
        import random
        import time
        
        # Obtener TODOS los códigos BAROTI ocupados (sin importar el estado)
        # La restricción de unicidad aplica a todos los paquetes
        occupied_posiciones = db.query(Package.posicion).filter(
            Package.posicion.isnot(None)
        ).all()
        
        occupied_set = {posicion[0] for posicion in occupied_posiciones if posicion[0]}
        
        # Si todos los BAROTIs están ocupados (00-99), lanzar error
        if len(occupied_set) >= 100:
            raise ValueError(
                "No hay códigos BAROTI disponibles. Todos los códigos (00-99) están ocupados. "
                "Por favor, libere algunos BAROTIs de paquetes entregados o cancelados."
            )
        
        # Generar código único con reintentos limitados
        max_attempts = 200  # Limitar reintentos para evitar loops infinitos
        attempts = 0
        
        while attempts < max_attempts:
            posicion = f"{random.randint(0, 99):02d}"
            if posicion not in occupied_set:
                # Verificar una vez más directamente en la BD antes de retornar (race condition)
                exists = db.query(Package).filter(Package.posicion == posicion).first()
                if not exists:
                    return posicion
                # Si existe, agregarlo al set y continuar
                occupied_set.add(posicion)
            
            attempts += 1
            # Pequeña pausa si hay muchos intentos (evitar carga excesiva)
            if attempts % 50 == 0:
                time.sleep(0.01)
        
        # Si llegamos aquí, algo salió mal
        raise ValueError(
            f"No se pudo generar un código BAROTI único después de {max_attempts} intentos. "
            f"Códigos ocupados: {len(occupied_set)}/100"
        )

    @classmethod
    def _is_posicion_available(cls, db: Session, posicion: str) -> bool:
        """Verificar si un código de posición está disponible"""
        existing = db.query(Package).filter(
            Package.posicion == posicion,
            Package.status.in_([PackageStatus.RECIBIDO, PackageStatus.ANUNCIADO])
        ).first()
        return existing is None