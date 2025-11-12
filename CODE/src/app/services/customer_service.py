# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Servicio de Clientes Expandido
Versión: 2.0.0
Fecha: 2025-09-21
Autor: Equipo de Desarrollo
"""

from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, desc
from uuid import UUID
import csv
import io

from .base import BaseService
from app.models.customer import Customer
from app.schemas.customer import (
    CustomerCreate, CustomerUpdate, CustomerResponse,
    CustomerListResponse, CustomerStatsResponse,
    CustomerBulkUpdateResponse
)
from app.utils.datetime_utils import get_colombia_now
from app.utils.exceptions import ValidationException

class CustomerService(BaseService[Customer, CustomerCreate, CustomerUpdate]):
    """
    Servicio expandido para gestión completa de clientes
    """

    def __init__(self):
        super().__init__(Customer)

    def create_customer(self, db: Session, customer_data: CustomerCreate, created_by_id: Optional[UUID] = None) -> Customer:
        """Crear un nuevo cliente con validaciones"""
        # Verificar duplicados
        self._check_duplicates(db, customer_data.phone, customer_data.email, customer_data.document_number)

        # Crear nombre completo
        full_name = f"{customer_data.first_name} {customer_data.last_name}"

        # Preparar datos
        customer_dict = customer_data.dict()
        customer_dict.update({
            'full_name': full_name,
            'created_by_id': created_by_id,
            'updated_by_id': created_by_id
        })

        db_customer = Customer(**customer_dict)
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        return db_customer

    def update_customer(self, db: Session, customer_id: UUID, customer_data: CustomerUpdate, updated_by_id: Optional[UUID] = None) -> Customer:
        """Actualizar cliente con validaciones"""
        customer = self.get_by_id(db, customer_id)
        if not customer:
            raise ValidationException(f"Cliente con ID {customer_id} no encontrado")

        update_data = customer_data.dict(exclude_unset=True)

        # Verificar duplicados si se actualizan campos únicos
        if 'phone' in update_data:
            existing = db.query(Customer).filter(
                and_(Customer.phone == update_data['phone'], Customer.id != customer_id)
            ).first()
            if existing:
                raise ValidationException("Ya existe un cliente con este número de teléfono")

        if 'email' in update_data and update_data['email']:
            existing = db.query(Customer).filter(
                and_(Customer.email == update_data['email'], Customer.id != customer_id)
            ).first()
            if existing:
                raise ValidationException("Ya existe un cliente con este email")

        if 'document_number' in update_data and update_data['document_number']:
            existing = db.query(Customer).filter(
                and_(Customer.document_number == update_data['document_number'], Customer.id != customer_id)
            ).first()
            if existing:
                raise ValidationException("Ya existe un cliente con este número de documento")

        # Actualizar nombre completo si cambian nombres
        if 'first_name' in update_data or 'last_name' in update_data:
            first_name = update_data.get('first_name', customer.first_name)
            last_name = update_data.get('last_name', customer.last_name)
            # Asegurar que last_name no sea None para evitar errores
            if last_name is None:
                last_name = customer.last_name or ''
            update_data['full_name'] = f"{first_name} {last_name}".strip()

        update_data['updated_by_id'] = updated_by_id
        
        # Actualizar campos directamente en el objeto
        for field, value in update_data.items():
            if hasattr(customer, field):
                setattr(customer, field, value)
        
        db.commit()
        db.refresh(customer)
        return customer

    def _check_duplicates(self, db: Session, phone: str, email: Optional[str] = None, document: Optional[str] = None):
        """Verificar duplicados antes de crear"""
        # Verificar teléfono
        existing = db.query(Customer).filter(Customer.phone == phone).first()
        if existing:
            raise ValidationException("Ya existe un cliente con este número de teléfono")

        # Verificar email
        if email:
            existing = db.query(Customer).filter(Customer.email == email).first()
            if existing:
                raise ValidationException("Ya existe un cliente con este email")

        # Verificar documento
        if document:
            existing = db.query(Customer).filter(Customer.document_number == document).first()
            if existing:
                raise ValidationException("Ya existe un cliente con este número de documento")

    def search_customers_advanced(
        self,
        db: Session,
        query: str = "",
        search_by: str = "all",
        is_active: Optional[bool] = None,
        is_vip: Optional[bool] = None,
        city: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[Customer], int]:
        """Búsqueda avanzada de clientes"""
        base_query = db.query(Customer)

        # Aplicar filtros de estado
        if is_active is not None:
            base_query = base_query.filter(Customer.is_active == is_active)
        if is_vip is not None:
            base_query = base_query.filter(Customer.is_vip == is_vip)
        if city:
            base_query = base_query.filter(Customer.address_city.ilike(f"%{city}%"))

        # Aplicar búsqueda por texto
        if query:
            search_filters = []
            if search_by in ["all", "name"]:
                search_filters.extend([
                    Customer.first_name.ilike(f"%{query}%"),
                    Customer.last_name.ilike(f"%{query}%"),
                    Customer.full_name.ilike(f"%{query}%")
                ])
            if search_by in ["all", "phone"]:
                search_filters.append(Customer.phone.ilike(f"%{query}%"))
            if search_by in ["all", "email"]:
                search_filters.append(Customer.email.ilike(f"%{query}%"))
            if search_by in ["all", "document"]:
                search_filters.append(Customer.document_number.ilike(f"%{query}%"))

            if search_filters:
                base_query = base_query.filter(or_(*search_filters))

        # Obtener total
        total = base_query.count()

        # Aplicar paginación y ordenamiento
        customers = base_query.order_by(desc(Customer.created_at)).offset(skip).limit(limit).all()

        return customers, total

    def get_customer_stats(self, db: Session) -> CustomerStatsResponse:
        """Obtener estadísticas generales de clientes"""
        # Estadísticas básicas
        total_customers = db.query(func.count(Customer.id)).scalar()
        active_customers = db.query(func.count(Customer.id)).filter(Customer.is_active == True).scalar()
        vip_customers = db.query(func.count(Customer.id)).filter(Customer.is_vip == True).scalar()

        # Clientes por ciudad
        city_stats = db.query(
            Customer.address_city,
            func.count(Customer.id).label('count')
        ).filter(
            and_(Customer.address_city.isnot(None), Customer.is_active == True)
        ).group_by(Customer.address_city).all()

        customers_by_city = {city: count for city, count in city_stats if city}

        # Top clientes por paquetes
        top_customers = db.query(
            Customer.id,
            Customer.full_name,
            Customer.total_packages_received,
            Customer.total_packages_delivered
        ).filter(Customer.is_active == True).order_by(
            desc(Customer.total_packages_received)
        ).limit(10).all()

        top_customers_by_packages = [
            {
                "id": str(customer.id),
                "name": customer.full_name,
                "packages_received": customer.total_packages_received,
                "packages_delivered": customer.total_packages_delivered
            }
            for customer in top_customers
        ]

        # Nuevos registros en el último mes
        from datetime import datetime, timedelta
        last_month = datetime.now() - timedelta(days=30)
        recent_registrations = db.query(func.count(Customer.id)).filter(
            Customer.created_at >= last_month
        ).scalar()

        return CustomerStatsResponse(
            total_customers=total_customers,
            active_customers=active_customers,
            vip_customers=vip_customers,
            customers_by_city=customers_by_city,
            top_customers_by_packages=top_customers_by_packages,
            recent_registrations=recent_registrations
        )

    def merge_customers(self, db: Session, primary_id: UUID, duplicate_id: UUID, strategy: str = "keep_primary") -> Customer:
        """Fusionar clientes duplicados"""
        primary = self.get_by_id(db, primary_id)
        duplicate = self.get_by_id(db, duplicate_id)

        if not primary or not duplicate:
            raise ValidationException("Uno o ambos clientes no existen")

        # Lógica de fusión según estrategia
        if strategy == "keep_primary":
            # Mantener datos del cliente primario
            pass
        elif strategy == "keep_most_recent":
            # Mantener datos del cliente más reciente
            if duplicate.created_at > primary.created_at:
                primary, duplicate = duplicate, primary

        # Transferir paquetes y anuncios
        for package in duplicate.packages:
            package.customer_id = primary.id
        for announcement in duplicate.announcements:
            announcement.customer_id = primary.id

        # Actualizar contadores
        primary.update_package_counts()

        # Eliminar cliente duplicado
        db.delete(duplicate)
        db.commit()
        db.refresh(primary)

        return primary

    def bulk_update_customers(self, db: Session, customer_ids: List[UUID], updates: CustomerUpdate, updated_by_id: Optional[UUID] = None) -> CustomerBulkUpdateResponse:
        """Actualización masiva de clientes"""
        updated_count = 0
        errors = []

        for customer_id in customer_ids:
            try:
                self.update_customer(db, customer_id, updates, updated_by_id)
                updated_count += 1
            except Exception as e:
                errors.append({
                    "customer_id": str(customer_id),
                    "error": str(e)
                })

        return CustomerBulkUpdateResponse(
            updated_count=updated_count,
            failed_count=len(errors),
            errors=errors
        )

    def import_customers_csv(self, db: Session, csv_data: str, update_existing: bool = False, skip_duplicates: bool = True) -> Dict[str, Any]:
        """Importar clientes desde CSV"""
        imported_count = 0
        updated_count = 0
        skipped_count = 0
        errors = []

        # Parsear CSV
        csv_reader = csv.DictReader(io.StringIO(csv_data))

        for row_num, row in enumerate(csv_reader, start=2):  # +2 porque header es línea 1
            try:
                # Mapear campos del CSV
                customer_data = {
                    'first_name': row.get('first_name', '').strip(),
                    'last_name': row.get('last_name', '').strip(),
                    'phone': row.get('phone', '').strip(),
                    'email': row.get('email', '').strip() or None,
                    'document_type': row.get('document_type', '').strip() or None,
                    'document_number': row.get('document_number', '').strip() or None,
                    'address_street': row.get('address_street', '').strip() or None,
                    'address_city': row.get('address_city', '').strip() or None,
                    'building_name': row.get('building_name', '').strip() or None,
                    'tower': row.get('tower', '').strip() or None,
                    'apartment': row.get('apartment', '').strip() or None,
                }

                # Validar campos requeridos
                if not customer_data['first_name'] or not customer_data['last_name'] or not customer_data['phone']:
                    errors.append({
                        "row": row_num,
                        "error": "Campos requeridos faltantes: first_name, last_name, phone"
                    })
                    continue

                # Verificar si ya existe
                existing = None
                if customer_data['phone']:
                    existing = db.query(Customer).filter(Customer.phone == customer_data['phone']).first()

                if existing:
                    if skip_duplicates:
                        skipped_count += 1
                        continue
                    elif update_existing:
                        # Actualizar cliente existente
                        update_data = CustomerUpdate(**{k: v for k, v in customer_data.items() if v is not None})
                        self.update_customer(db, existing.id, update_data)
                        updated_count += 1
                        continue

                # Crear nuevo cliente
                create_data = CustomerCreate(**customer_data)
                self.create_customer(db, create_data)
                imported_count += 1

            except Exception as e:
                errors.append({
                    "row": row_num,
                    "error": str(e)
                })

        return {
            "imported_count": imported_count,
            "updated_count": updated_count,
            "skipped_count": skipped_count,
            "errors": errors
        }

    def get_customer_by_phone(self, db: Session, phone: str) -> Optional[Customer]:
        """Obtener cliente por teléfono"""
        return db.query(Customer).filter(Customer.phone == phone).first()

    def get_customer_by_email(self, db: Session, email: str) -> Optional[Customer]:
        """Obtener cliente por email"""
        return db.query(Customer).filter(Customer.email == email).first()

    def get_customer_by_document(self, db: Session, document_number: str) -> Optional[Customer]:
        """Obtener cliente por número de documento"""
        return db.query(Customer).filter(Customer.document_number == document_number).first()

    def get_customers_with_packages(self, db: Session, skip: int = 0, limit: int = 50) -> List[Customer]:
        """Obtener clientes que tienen paquetes"""
        from app.models.package import Package
        return db.query(Customer).join(Package).distinct().offset(skip).limit(limit).all()

    def get_vip_customers(self, db: Session, skip: int = 0, limit: int = 50) -> List[Customer]:
        """Obtener clientes VIP"""
        return db.query(Customer).filter(
            and_(Customer.is_vip == True, Customer.is_active == True)
        ).order_by(desc(Customer.total_spent)).offset(skip).limit(limit).all()

    def deactivate_customer(self, db: Session, customer_id: UUID, updated_by_id: Optional[UUID] = None) -> Customer:
        """Desactivar un cliente"""
        customer = self.get_by_id(db, customer_id)
        if not customer:
            raise ValidationException(f"Cliente con ID {customer_id} no encontrado")

        customer.is_active = False
        customer.updated_by_id = updated_by_id
        customer.updated_at = get_colombia_now()

        db.commit()
        db.refresh(customer)

        return customer

    def reactivate_customer(self, db: Session, customer_id: UUID, updated_by_id: Optional[UUID] = None) -> Customer:
        """Reactivar un cliente"""
        customer = self.get_by_id(db, customer_id)
        if not customer:
            raise ValidationException(f"Cliente con ID {customer_id} no encontrado")

        customer.is_active = True
        customer.updated_by_id = updated_by_id
        customer.updated_at = get_colombia_now()

        db.commit()
        db.refresh(customer)

        return customer