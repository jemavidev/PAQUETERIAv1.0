# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Servicio de Paquetes
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo
"""

import secrets
import string
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
from decimal import Decimal

from .base import BaseService
from app.models.package import Package, PackageStatus, PackageType, PackageCondition
from app.models.customer import Customer
from app.models.package_history import PackageHistory
from app.models.message import Message
from app.models.notification import Notification
from app.models.file_upload import FileUpload
# from app.models.announcement_new import PackageAnnouncementNew  # Archivo eliminado
from app.schemas.package import (
    PackageCreate, PackageUpdate, PackageResponse,
    PackageStatusUpdate, PackageSearch, PackageAnnouncement
)
from app.schemas.customer import CustomerCreate
from .customer_service import CustomerService
import uuid


class PackageService(BaseService[Package, PackageCreate, PackageUpdate]):
    """
    Servicio para gestión de paquetes
    """

    def __init__(self):
        super().__init__(Package)
        self.customer_service = CustomerService()

    def create_package(self, db: Session, package_in: PackageCreate, user_id: int) -> Package:
        """Crear nuevo paquete con cliente y tracking number"""
        # Buscar o crear cliente
        customer = self._get_or_create_customer(db, package_in.customer_name, package_in.customer_phone)

        # Generar tracking number único
        tracking_number = self._generate_tracking_number(db)

        # Generar código de acceso único
        access_code = self._generate_access_code()

        # Calcular tarifas
        base_fee, storage_fee, total_amount = self._calculate_fees(package_in.package_type)

        # Crear paquete
        package_data = package_in.model_dump()
        package_data.update({
            'customer_id': customer.id,
            'tracking_number': tracking_number,
            'guide_number': package_in.guide_number,
            'access_code': access_code,
            'base_fee': base_fee,
            'storage_fee': storage_fee,
            'total_amount': total_amount,
            'announced_at': datetime.utcnow(),
            'created_by': user_id
        })

        db_package = Package(**package_data)
        db.add(db_package)
        db.commit()
        db.refresh(db_package)
        return db_package

    def announce_package(self, db: Session, announcement: PackageAnnouncement) -> Dict[str, Any]:
        """Anunciar paquete (versión simplificada para clientes)"""
        # Buscar o crear cliente
        customer = self._get_or_create_customer(db, announcement.customer_name, announcement.customer_phone)

        # Usar tracking number proporcionado o generar uno nuevo
        if announcement.tracking_number:
            tracking_number = announcement.tracking_number
            # Verificar que no exista ya
            existing = db.query(Package).filter(Package.tracking_number == tracking_number).first()
            if existing:
                raise ValueError(f"El número de tracking {tracking_number} ya existe")
        else:
            tracking_number = self._generate_tracking_number(db)

        # Generar código de acceso único
        access_code = self._generate_access_code()

        # Calcular tarifas (tarifa normal por defecto)
        base_fee, storage_fee, total_amount = self._calculate_fees(PackageType.NORMAL)

        # Crear paquete
        package_data = {
            'customer_id': customer.id,
            'guide_number': announcement.guide_number,
            'tracking_number': tracking_number,
            'access_code': access_code,
            'package_type': PackageType.NORMAL,
            'status': PackageStatus.ANUNCIADO,
            'package_condition': PackageCondition.BUENO,
            'base_fee': base_fee,
            'storage_fee': storage_fee,
            'total_amount': total_amount,
            'announced_at': datetime.utcnow()
        }

        db_package = Package(**package_data)
        db.add(db_package)
        db.commit()
        db.refresh(db_package)

        return {
            'success': True,
            'message': 'Paquete anunciado exitosamente',
            'tracking_number': tracking_number,
            'access_code': access_code,
            'package_id': db_package.id,
            'customer_name': announcement.customer_name,
            'customer_phone': announcement.customer_phone,
            'guide_number': announcement.guide_number,
            'base_fee': float(db_package.base_fee),
            'storage_fee': float(db_package.storage_fee),
            'total_amount': float(db_package.total_amount)
        }

    def create_package_from_announcement(self, db: Session, customer_name: str, customer_phone: str, guide_number: str, tracking_number: Optional[str] = None) -> Package:
        """Crear paquete desde anuncio sin validaciones Pydantic (para datos existentes)"""
        # Buscar o crear cliente (sin validaciones de teléfono)
        customer = self._get_or_create_customer_unvalidated(db, customer_name, customer_phone)

        # Usar tracking number proporcionado o generar uno nuevo
        if tracking_number:
            # Verificar que no exista ya
            existing = db.query(Package).filter(Package.tracking_number == tracking_number).first()
            if existing:
                # En lugar de lanzar error, retornar el paquete existente
                print(f"⚠️ Tracking {tracking_number} ya existe, retornando paquete existente")
                return existing
        else:
            tracking_number = self._generate_tracking_number(db)

        # Generar código de acceso único
        access_code = self._generate_access_code()

        # Calcular tarifas (tarifa normal por defecto)
        base_fee, storage_fee, total_amount = self._calculate_fees(PackageType.NORMAL)

        # Crear paquete
        package_data = {
            'customer_id': customer.id,
            'guide_number': guide_number,
            'tracking_number': tracking_number,
            'access_code': access_code,
            'package_type': PackageType.NORMAL,
            'status': PackageStatus.ANUNCIADO,
            'package_condition': PackageCondition.BUENO,
            'base_fee': base_fee,
            'storage_fee': storage_fee,
            'total_amount': total_amount,
            'announced_at': datetime.utcnow()
        }

        db_package = Package(**package_data)
        db.add(db_package)
        db.commit()
        db.refresh(db_package)

        return db_package

    def _get_or_create_customer_unvalidated(self, db: Session, name: str, phone: str) -> Customer:
        """Buscar cliente existente o crear uno nuevo sin validaciones de teléfono"""
        customer = db.query(Customer).filter(Customer.phone == phone).first()
        if customer:
            return customer

        # Crear nuevo cliente sin validaciones
        from app.models.customer import Customer as CustomerModel

        # Dividir el nombre en first_name y last_name
        name_parts = name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        customer_data = {
            'first_name': first_name,
            'last_name': last_name,
            'full_name': name,  # Agregar full_name para evitar error de NULL
            'phone': phone,
            'email': None,
            'address_street': None,
            'address_city': None,
            'address_state': None,
            'address_zip': None,
            'address_country': 'Colombia'
        }

        db_customer = CustomerModel(**customer_data)
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        return db_customer

    def update_package_status(self, db: Session, package_id: int, status_update: PackageStatusUpdate, user_id: int) -> Package:
        """Actualizar estado del paquete usando PackageStateService para asegurar historial"""
        from app.services.package_state_service import PackageStateService

        package = self.get_by_id(db, package_id)
        if not package:
            raise ValueError("Paquete no encontrado")

        old_status = package.status
        new_status = status_update.status

        # Asegurar que new_status sea el Enum del modelo (app.models.package.PackageStatus)
        # status_update.status proviene del esquema (app.schemas.package.PackageStatus - str Enum)
        # Convertimos por valor para evitar comparaciones fallidas entre distintos Enum classes
        if not isinstance(new_status, PackageStatus):
            try:
                new_status = PackageStatus(new_status.value if hasattr(new_status, 'value') else str(new_status))
            except Exception as e:
                raise ValueError(f"Estado inválido: {new_status}") from e

        # Validar transición de estados
        self._validate_status_transition(old_status, new_status)

        # Preparar datos adicionales para el historial
        additional_data = {}
        observations = status_update.observations or ""

        # Actualizar tipo y condición del paquete si se proporcionan
        if status_update.package_type:
            package.package_type = status_update.package_type
            additional_data['package_type'] = status_update.package_type.value

        if status_update.package_condition:
            package.package_condition = status_update.package_condition
            additional_data['package_condition'] = status_update.package_condition.value

        # Usar PackageStateService para cambiar el estado y crear historial
        history_entry = PackageStateService.update_package_status(
            db=db,
            package=package,
            new_status=new_status,
            changed_by=f"user_{user_id}",
            additional_data=additional_data,
            observations=observations
        )

        return package

    def search_packages(self, db: Session, search: PackageSearch) -> List[Package]:
        """Buscar paquetes por tracking, nombre o teléfono"""
        query = db.query(Package).join(Customer)

        # Aplicar filtros de búsqueda
        if search.query:
            search_filters = [
                Package.tracking_number.ilike(f"%{search.query}%"),
                Customer.full_name.ilike(f"%{search.query}%"),
                Customer.phone.ilike(f"%{search.query}%")
            ]
            query = query.filter(or_(*search_filters))

        if search.status:
            query = query.filter(Package.status == search.status)

        return query.offset(search.offset).limit(search.limit).all()

    def get_package_by_tracking(self, db: Session, tracking_number: str) -> Optional[Package]:
        """Obtener paquete por número de tracking"""
        return db.query(Package).filter(Package.tracking_number == tracking_number).first()

    def get_packages_by_status(self, db: Session, status: PackageStatus, skip: int = 0, limit: int = 100) -> List[Package]:
        """Obtener paquetes por estado"""
        return db.query(Package).filter(Package.status == status).offset(skip).limit(limit).all()

    def get_packages_by_customer(self, db: Session, customer_id: int, skip: int = 0, limit: int = 50) -> List[Package]:
        """Obtener paquetes de un cliente"""
        return db.query(Package).filter(Package.customer_id == customer_id).offset(skip).limit(limit).all()

    def get_package_stats(self, db: Session) -> Dict[str, Any]:
        """Obtener estadísticas de paquetes"""
        # Contar por estado
        status_counts = db.query(
            Package.status,
            func.count(Package.id).label('count')
        ).group_by(Package.status).all()

        # Calcular ingresos totales
        total_revenue = db.query(func.sum(Package.total_amount)).scalar() or Decimal('0.00')

        # Estadísticas por tipo
        type_counts = db.query(
            Package.package_type,
            func.count(Package.id).label('count')
        ).group_by(Package.package_type).all()

        return {
            'total_packages': sum(count for _, count in status_counts),
            'status_breakdown': {status.value: count for status, count in status_counts},
            'total_revenue': total_revenue,
            'type_breakdown': {pkg_type.value: count for pkg_type, count in type_counts}
        }

    def _get_or_create_customer(self, db: Session, name: str, phone: str) -> Customer:
        """Buscar cliente existente o crear uno nuevo"""
        customer = db.query(Customer).filter(Customer.phone == phone).first()
        if customer:
            return customer

        # Dividir el nombre en first_name y last_name
        name_parts = name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        # Crear nuevo cliente usando el servicio correcto
        customer_data = CustomerCreate(
            first_name=first_name,
            last_name=last_name,
            phone=phone
        )
        return self.customer_service.create_customer(db, customer_data)

    def _generate_tracking_number(self, db: Session) -> str:
        """Generar número de tracking único"""
        while True:
            # Formato: PAP + YYYYMMDD + 4 caracteres alfanuméricos
            today = datetime.utcnow().strftime('%Y%m%d')
            random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
            tracking_number = f"PAP{today}{random_part}"

            # Verificar unicidad
            if not db.query(Package).filter(Package.tracking_number == tracking_number).first():
                return tracking_number

    def _generate_access_code(self) -> str:
        """Generar código de acceso único"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))

    def _calculate_fees(self, package_type: PackageType) -> tuple[Decimal, Decimal, Decimal]:
        """Calcular tarifas según el tipo de paquete - DINÁMICO desde .env"""
        from app.config import settings
        
        # Tarifa base de entrega según tipo de paquete (dinámico desde .env)
        if package_type == PackageType.NORMAL:
            base_fee = Decimal(str(settings.base_delivery_rate_normal))
        elif package_type == PackageType.EXTRA_DIMENSIONADO:
            base_fee = Decimal(str(settings.base_delivery_rate_extra_dimensioned))
        else:
            # Fallback para tipos no reconocidos
            base_fee = Decimal(str(settings.base_delivery_rate_normal))
        
        # Tarifa de almacenamiento inicial es 0 (se calcula por días después)
        storage_fee = Decimal('0.00')

        # Total inicial es solo la tarifa base
        total_amount = base_fee
        return base_fee, storage_fee, total_amount

    def recalculate_package_fees(self, db: Session, package: Package) -> Package:
        """Recalcular tarifas de un paquete existente según su tipo"""
        from app.config import settings
        
        # Recalcular tarifa base según tipo de paquete
        if package.package_type == PackageType.NORMAL:
            new_base_fee = Decimal(str(settings.base_delivery_rate_normal))
        elif package.package_type == PackageType.EXTRA_DIMENSIONADO:
            new_base_fee = Decimal(str(settings.base_delivery_rate_extra_dimensioned))
        else:
            new_base_fee = Decimal(str(settings.base_delivery_rate_normal))
        
        # Actualizar tarifa base
        package.base_fee = new_base_fee
        
        # Recalcular total_amount
        package.total_amount = package.base_fee + package.storage_fee
        
        # Guardar cambios
        db.commit()
        db.refresh(package)
        
        return package

    def get_package_with_correct_fees(self, db: Session, package_id: int) -> Optional[Package]:
        """Obtener paquete y corregir tarifas automáticamente si es necesario"""
        from sqlalchemy.orm import joinedload
        
        package = db.query(Package).options(joinedload(Package.customer)).filter(Package.id == package_id).first()
        
        if package:
            # Usar el método del modelo para corregir tarifas
            if package.update_fees_if_needed():
                db.commit()
                db.refresh(package)
        
        return package

    def fix_all_packages_fees(self, db: Session) -> int:
        """Corregir tarifas de todos los paquetes que tengan valores incorrectos"""
        packages = db.query(Package).all()
        fixed_count = 0
        
        for package in packages:
            if package.update_fees_if_needed():
                fixed_count += 1
        
        if fixed_count > 0:
            db.commit()
        
        return fixed_count

    def _validate_status_transition(self, old_status: PackageStatus, new_status: PackageStatus):
        """Validar transición de estados"""
        valid_transitions = {
            PackageStatus.ANUNCIADO: [PackageStatus.RECIBIDO, PackageStatus.CANCELADO],
            PackageStatus.RECIBIDO: [PackageStatus.ENTREGADO, PackageStatus.CANCELADO],
            PackageStatus.ENTREGADO: [],  # Estado final
            PackageStatus.CANCELADO: []   # Estado final
        }

        if new_status not in valid_transitions.get(old_status, []):
            raise ValueError(f"Transición de estado no válida: {old_status.value} -> {new_status.value}")

    # ========================================
    # FUNCIONALIDAD DE ELIMINACIÓN
    # ========================================

    def delete_guide_by_number(self, db: Session, guide_number: str, deleted_by: str = "system") -> Dict[str, Any]:
        """Eliminar una guía y todas sus referencias relacionadas"""
        try:
            from sqlalchemy import text

            # Buscar el anuncio por número de guía usando consulta SQL directa
            announcement_query = text("""
                SELECT id, customer_name, customer_phone, tracking_code, is_processed, package_id
                FROM package_announcements_new
                WHERE guide_number = :guide_number
            """)
            result = db.execute(announcement_query, {"guide_number": guide_number})
            announcement_data = result.fetchone()

            if not announcement_data:
                raise ValueError(f"No se encontró la guía: {guide_number}")

            # Verificar que no esté procesada (tiene paquete asociado)
            if announcement_data[4] and announcement_data[5]:  # is_processed and package_id
                raise ValueError(f"No se puede eliminar la guía {guide_number}: ya fue procesada y tiene un paquete asociado")

            # Recopilar información para el log
            deletion_info = {
                "guide_number": guide_number,
                "customer_name": announcement_data[1],  # customer_name
                "customer_phone": announcement_data[2],  # customer_phone
                "tracking_code": announcement_data[3],  # tracking_code
                "deleted_by": deleted_by,
                "deleted_at": self._get_current_timestamp()
            }

            # Eliminar mensajes relacionados con esta guía
            messages_deleted = self._delete_messages_by_guide_number(db, guide_number)

            # Eliminar el anuncio usando consulta SQL directa
            delete_query = text("""
                DELETE FROM package_announcements_new WHERE id = :announcement_id
            """)
            db.execute(delete_query, {"announcement_id": announcement_data[0]})  # id
            db.commit()

            deletion_info["messages_deleted"] = messages_deleted

            return {
                "success": True,
                "message": f"Guía {guide_number} eliminada exitosamente",
                "guide_number": guide_number,
                "messages_deleted": messages_deleted,
                "deletion_info": deletion_info
            }

        except Exception as e:
            db.rollback()
            raise e

    def delete_guide_by_tracking_code(self, db: Session, tracking_code: str, deleted_by: str = "system") -> Dict[str, Any]:
        """Eliminar una guía por tracking_code y todas sus referencias relacionadas"""
        try:
            from sqlalchemy import text

            # Buscar el anuncio por tracking_code usando consulta SQL directa
            announcement_query = text("""
                SELECT id, customer_name, customer_phone, tracking_code, is_processed, package_id, guide_number
                FROM package_announcements_new
                WHERE tracking_code = :tracking_code
            """)
            result = db.execute(announcement_query, {"tracking_code": tracking_code})
            announcement_data = result.fetchone()

            if not announcement_data:
                raise ValueError(f"No se encontró la guía con tracking code: {tracking_code}")

            # Verificar que no esté procesada (tiene paquete asociado)
            if announcement_data[4] and announcement_data[5]:  # is_processed and package_id
                raise ValueError(f"No se puede eliminar la guía {announcement_data[6]}: ya fue procesada y tiene un paquete asociado")

            # Recopilar información para el log
            deletion_info = {
                "tracking_code": tracking_code,
                "guide_number": announcement_data[6],  # guide_number
                "customer_name": announcement_data[1],  # customer_name
                "customer_phone": announcement_data[2],  # customer_phone
                "deleted_by": deleted_by,
                "deleted_at": self._get_current_timestamp()
            }

            # Eliminar mensajes relacionados con esta guía
            messages_deleted = self._delete_messages_by_guide_number(db, announcement_data[6])

            # Eliminar el anuncio usando consulta SQL directa
            delete_query = text("""
                DELETE FROM package_announcements_new WHERE id = :announcement_id
            """)
            db.execute(delete_query, {"announcement_id": announcement_data[0]})  # id
            db.commit()

            deletion_info["messages_deleted"] = messages_deleted

            return {
                "success": True,
                "message": f"Guía {announcement_data[6]} (tracking: {tracking_code}) eliminada exitosamente",
                "tracking_code": tracking_code,
                "guide_number": announcement_data[6],
                "messages_deleted": messages_deleted,
                "deletion_info": deletion_info
            }

        except Exception as e:
            db.rollback()
            raise e

    def delete_package_by_id(self, db: Session, package_id: int, deleted_by: str = "system") -> Dict[str, Any]:
        """Eliminar un paquete y todas sus referencias relacionadas"""
        try:
            # Buscar el paquete
            package = self.get_by_id(db, package_id)
            if not package:
                raise ValueError(f"No se encontró el paquete con ID: {package_id}")

            # Verificar permisos - solo ADMIN puede eliminar paquetes
            # Esta validación se hace en el endpoint, no aquí

            # Recopilar información para el log
            deletion_info = {
                "package_id": package_id,
                "tracking_number": package.tracking_number,
                "guide_number": package.guide_number,
                "status": package.status.value,
                "customer_id": str(package.customer_id) if package.customer_id else None,
                "deleted_by": deleted_by,
                "deleted_at": self._get_current_timestamp()
            }

            # Eliminar historial de paquetes
            history_deleted = self._delete_package_history(db, package_id)

            # Eliminar mensajes relacionados
            messages_deleted = self._delete_messages_by_package_id(db, package_id)

            # Eliminar notificaciones relacionadas
            notifications_deleted = self._delete_notifications_by_package_id(db, package_id)

            # Eliminar archivos subidos relacionados
            files_deleted = self._delete_files_by_package_id(db, package_id)

            # Desvincular el anuncio si existe
            announcement_updated = self._unlink_announcement_from_package(db, package_id)

            # Eliminar el paquete
            db.delete(package)
            db.commit()

            deletion_info.update({
                "history_deleted": history_deleted,
                "messages_deleted": messages_deleted,
                "notifications_deleted": notifications_deleted,
                "files_deleted": files_deleted,
                "announcement_updated": announcement_updated
            })

            return {
                "success": True,
                "message": f"Paquete {package.tracking_number} eliminado exitosamente",
                "package_id": package_id,
                "tracking_number": package.tracking_number,
                "history_deleted": history_deleted,
                "messages_deleted": messages_deleted,
                "notifications_deleted": notifications_deleted,
                "files_deleted": files_deleted,
                "announcement_updated": announcement_updated,
                "deletion_info": deletion_info
            }

        except Exception as e:
            db.rollback()
            raise e

    def delete_package_by_tracking_number(self, db: Session, tracking_number: str, deleted_by: str = "system") -> Dict[str, Any]:
        """Eliminar un paquete por número de tracking"""
        package = self.get_package_by_tracking(db, tracking_number)
        if not package:
            raise ValueError(f"No se encontró el paquete con tracking number: {tracking_number}")

        return self.delete_package_by_id(db, package.id, deleted_by)

    # ========================================
    # MÉTODOS AUXILIARES PARA ELIMINACIÓN
    # ========================================

    def _delete_messages_by_guide_number(self, db: Session, guide_number: str) -> int:
        """Eliminar mensajes relacionados con una guía"""
        # Eliminar mensajes donde tracking_code coincida con guide_number
        messages = db.query(Message).filter(
            Message.tracking_code == guide_number
        ).all()

        count = len(messages)
        for message in messages:
            db.delete(message)

        return count

    def _delete_messages_by_package_id(self, db: Session, package_id: int) -> int:
        """Eliminar mensajes relacionados con un paquete"""
        messages = db.query(Message).filter(
            Message.package_id == package_id
        ).all()

        count = len(messages)
        for message in messages:
            db.delete(message)

        return count

    def _delete_package_history(self, db: Session, package_id: int) -> int:
        """Eliminar historial de un paquete"""
        # Convertir package_id a UUID para la consulta
        history_entries = db.query(PackageHistory).filter(
            PackageHistory.package_id == package_id
        ).all()

        count = len(history_entries)
        for entry in history_entries:
            db.delete(entry)

        return count

    def _delete_notifications_by_package_id(self, db: Session, package_id: int) -> int:
        """Eliminar notificaciones relacionadas con un paquete"""
        notifications = db.query(Notification).filter(
            Notification.package_id == package_id
        ).all()

        count = len(notifications)
        for notification in notifications:
            db.delete(notification)

        return count

    def _delete_files_by_package_id(self, db: Session, package_id: int) -> int:
        """Eliminar archivos subidos relacionados con un paquete"""
        files = db.query(FileUpload).filter(
            FileUpload.package_id == package_id
        ).all()

        count = len(files)
        for file in files:
            db.delete(file)

        return count

    def _unlink_announcement_from_package(self, db: Session, package_id: int) -> bool:
        """Desvincular anuncio de un paquete (poner package_id = NULL)"""
        from sqlalchemy import text

        # Usar consulta SQL directa con INTEGER
        update_query = text("""
            UPDATE package_announcements_new
            SET package_id = NULL, is_processed = false, processed_at = NULL, updated_at = :updated_at
            WHERE package_id = :package_id
        """)

        result = db.execute(update_query, {
            "package_id": package_id,
            "updated_at": self._get_current_timestamp()
        })

        return result.rowcount > 0

    def _get_current_timestamp(self):
        """Obtener timestamp actual"""
        from app.utils.datetime_utils import get_colombia_now
        return get_colombia_now()
