# ========================================
# PAQUETES EL CLUB v4.0 - Servicio de Tarifas
# ========================================

from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime, timedelta
import uuid

from app.models.rate import Rate, RateType
from app.models.package import Package, PackageType
from app.utils.exceptions import RateCalculationException
from app.utils.datetime_utils import get_colombia_now
from app.config import settings

class RateService:
    """Servicio para la lógica de negocio de tarifas"""

    def __init__(self, db: Session):
        self.db = db

    def calculate_package_costs(
        self,
        package_type: PackageType,
        storage_days: int = 0,
        delivery_required: bool = True
    ) -> Dict[str, Decimal]:
        """Calcular costos de un paquete con el nuevo sistema de tarifas"""

        # Obtener tarifas activas
        active_rates = self.get_active_rates()

        # Tarifas base según configuración
        base_rates = {
            PackageType.NORMAL: Decimal(str(settings.base_delivery_rate)),
            PackageType.EXTRA_DIMENSIONADO: Decimal(str(settings.base_delivery_rate * settings.normal_package_multiplier)),
        }

        # Costo base según tipo de paquete
        base_cost = base_rates.get(package_type, Decimal(str(settings.base_delivery_rate)))

        # Costo de almacenamiento
        storage_cost = Decimal('0')
        if storage_days > 0:
            daily_rate = Decimal(str(settings.base_storage_rate))
            storage_cost = Decimal(storage_days) * daily_rate

        # Costo de entrega
        delivery_cost = base_cost if delivery_required else Decimal('0')

        # Aplicar multiplicadores de tarifa activa si existe
        if 'package_type' in active_rates:
            rate = active_rates['package_type']
            multiplier = Decimal(str(rate.package_type_multiplier))
            base_cost *= multiplier
            delivery_cost *= multiplier

        total_cost = base_cost + storage_cost + delivery_cost

        return {
            "base_cost": base_cost,
            "storage_cost": storage_cost,
            "delivery_cost": delivery_cost,
            "total_cost": total_cost
        }

    def calculate_total_package_cost(
        self,
        package_type: PackageType,
        storage_days: int = 0,
        delivery_required: bool = True,
        grace_period_hours: int = 24,
        overtime_rate_per_24h: float = 1000.0
    ) -> Dict[str, Any]:
        """Calcular costo total incluyendo tiempo excedido"""

        base_costs = self.calculate_package_costs(package_type, storage_days, delivery_required)

        # Calcular tiempo excedido (lógica simplificada)
        overtime_cost = Decimal('0')
        overtime_days = 0

        # Aquí iría la lógica para calcular tiempo excedido
        # basado en announced_at vs received_at vs delivered_at

        total_cost = base_costs["total_cost"] + overtime_cost

        return {
            "base_cost": base_costs["base_cost"],
            "storage_cost": base_costs["storage_cost"],
            "delivery_cost": base_costs["delivery_cost"],
            "overtime_cost": overtime_cost,
            "total_cost": total_cost,
            "overtime_days": overtime_days,
            "grace_period_hours": grace_period_hours,
            "overtime_rate_per_24h": Decimal(str(overtime_rate_per_24h))
        }

    def get_active_rates(self) -> Dict[str, Rate]:
        """Obtener todas las tarifas activas"""
        rates = self.db.query(Rate).filter(Rate.is_active == True).all()
        return {rate.rate_type.value: rate for rate in rates}

    def create_rate(self, rate_data: Dict[str, Any], created_by_id: Optional[str] = None) -> Rate:
        """Crear nueva tarifa"""
        # Desactivar tarifas anteriores del mismo tipo
        existing_rates = self.db.query(Rate).filter(
            Rate.rate_type == rate_data["rate_type"],
            Rate.is_active == True
        ).all()

        for rate in existing_rates:
            rate.deactivate()
            rate.updated_by_id = created_by_id

        # Crear nueva tarifa
        new_rate = Rate(**rate_data)
        if created_by_id:
            new_rate.created_by_id = created_by_id

        self.db.add(new_rate)
        self.db.commit()
        self.db.refresh(new_rate)

        return new_rate

    def update_rate(self, rate_id: str, rate_data: Dict[str, Any], updated_by_id: Optional[str] = None) -> Rate:
        """Actualizar tarifa existente"""
        rate = self.db.query(Rate).filter(Rate.id == rate_id).first()

        if not rate:
            raise RateCalculationException(f"Tarifa con ID {rate_id} no encontrada")

        # Actualizar campos
        for field, value in rate_data.items():
            if hasattr(rate, field):
                setattr(rate, field, value)

        if updated_by_id:
            rate.updated_by_id = updated_by_id

        self.db.commit()
        self.db.refresh(rate)

        return rate

    def deactivate_rate(self, rate_id: str, updated_by_id: Optional[str] = None) -> Rate:
        """Desactivar una tarifa"""
        rate = self.db.query(Rate).filter(Rate.id == rate_id).first()

        if not rate:
            raise RateCalculationException(f"Tarifa con ID {rate_id} no encontrada")

        rate.deactivate()
        if updated_by_id:
            rate.updated_by_id = updated_by_id

        self.db.commit()
        self.db.refresh(rate)

        return rate

    def get_rate_history(self, rate_type: Optional[RateType] = None, limit: int = 50) -> List[Rate]:
        """Obtener historial de cambios de tarifas"""
        query = self.db.query(Rate)

        if rate_type:
            query = query.filter(Rate.rate_type == rate_type)

        return query.order_by(Rate.created_at.desc()).limit(limit).all()

    def get_rate_by_id(self, rate_id: str) -> Optional[Rate]:
        """Obtener tarifa por ID"""
        return self.db.query(Rate).filter(Rate.id == rate_id).first()

    def get_rates_by_type(self, rate_type: RateType) -> List[Rate]:
        """Obtener todas las tarifas de un tipo"""
        return self.db.query(Rate).filter(Rate.rate_type == rate_type).order_by(Rate.created_at.desc()).all()

    def bulk_update_rates(self, rate_ids: List[str], updates: Dict[str, Any], updated_by_id: Optional[str] = None) -> Dict[str, Any]:
        """Actualización masiva de tarifas"""
        updated_count = 0
        errors = []

        for rate_id in rate_ids:
            try:
                self.update_rate(rate_id, updates, updated_by_id)
                updated_count += 1
            except Exception as e:
                errors.append({
                    "rate_id": rate_id,
                    "error": str(e)
                })

        return {
            "updated_count": updated_count,
            "failed_count": len(errors),
            "errors": errors
        }

    def get_rate_summary(self) -> Dict[str, Any]:
        """Obtener resumen de tarifas actuales"""
        active_rates = self.get_active_rates()
        all_rates = self.db.query(Rate).all()

        summary = {
            "active_rates": len(active_rates),
            "total_rates": len(all_rates),
            "rates_by_type": {}
        }

        # Agrupar por tipo
        for rate_type in RateType:
            type_rates = [r for r in active_rates.values() if r.rate_type == rate_type]
            summary["rates_by_type"][rate_type.value] = {
                "count": len(type_rates),
                "rates": [
                    {
                        "id": str(rate.id),
                        "name": rate.name,
                        "base_price": float(rate.base_price),
                        "is_active": rate.is_active
                    }
                    for rate in type_rates
                ]
            }

        # Última actualización
        last_rate = self.db.query(Rate).order_by(Rate.updated_at.desc()).first()
        summary["last_updated"] = last_rate.updated_at if last_rate else None

        return summary

    def validate_rate_data(self, rate_data: Dict[str, Any]) -> None:
        """Validar datos de tarifa"""
        required_fields = ['rate_type', 'name', 'base_price']

        for field in required_fields:
            if field not in rate_data or rate_data[field] is None:
                raise RateCalculationException(f"El campo {field} es requerido")

        if rate_data['base_price'] <= 0:
            raise RateCalculationException("El precio base debe ser mayor a 0")

        if rate_data.get('daily_storage_rate', 0) < 0:
            raise RateCalculationException("La tarifa de almacenamiento diaria no puede ser negativa")

        if rate_data.get('delivery_rate', 0) < 0:
            raise RateCalculationException("La tarifa de entrega no puede ser negativa")

        if rate_data.get('package_type_multiplier', 1.0) <= 0:
            raise RateCalculationException("El multiplicador de tipo de paquete debe ser mayor a 0")

    def calculate_storage_fee(self, days: int) -> Decimal:
        """Calcular tarifa de almacenamiento"""
        if days <= 0:
            return Decimal('0')

        daily_rate = Decimal(str(settings.base_storage_rate))
        return Decimal(days) * daily_rate

    def calculate_delivery_fee(self, package_type: PackageType) -> Decimal:
        """Calcular tarifa de entrega"""
        base_rates = {
            PackageType.NORMAL: Decimal(str(settings.base_delivery_rate)),
            PackageType.EXTRA_DIMENSIONADO: Decimal(str(settings.base_delivery_rate * settings.normal_package_multiplier)),
        }

        return base_rates.get(package_type, Decimal(str(settings.base_delivery_rate)))