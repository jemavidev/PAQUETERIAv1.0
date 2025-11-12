# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Calculador Dinámico de Tarifas
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo
"""

import os
from decimal import Decimal
from typing import Dict, Any
from app.models.package import PackageType
from app.config import settings

class DynamicFeeCalculator:
    """Calculador dinámico de tarifas que lee directamente de CODE/LOCAL/.env"""
    
    @staticmethod
    def get_rates_from_env() -> Dict[str, int]:
        """Obtener tarifas directamente desde variables de entorno"""
        return {
            'normal': settings.base_delivery_rate_normal,
            'extra_dimensioned': settings.base_delivery_rate_extra_dimensioned,
            'storage_per_day': settings.base_storage_rate
        }
    
    @staticmethod
    def calculate_base_fee(package_type: PackageType) -> Decimal:
        """Calcular tarifa base según tipo de paquete desde CODE/LOCAL/.env"""
        rates = DynamicFeeCalculator.get_rates_from_env()
        
        if package_type == PackageType.NORMAL:
            return Decimal(str(rates['normal']))
        elif package_type == PackageType.EXTRA_DIMENSIONADO:
            return Decimal(str(rates['extra_dimensioned']))
        else:
            return Decimal(str(rates['normal']))  # Fallback
    
    @staticmethod
    def calculate_storage_fee(storage_days: int) -> Decimal:
        """Calcular tarifa de almacenamiento desde CODE/LOCAL/.env"""
        rates = DynamicFeeCalculator.get_rates_from_env()
        return Decimal(str(rates['storage_per_day'])) * Decimal(str(storage_days))
    
    @staticmethod
    def calculate_total_fee(package_type: PackageType, storage_days: int = 0) -> Dict[str, Any]:
        """Calcular tarifa total completa desde CODE/LOCAL/.env"""
        base_fee = DynamicFeeCalculator.calculate_base_fee(package_type)
        storage_fee = DynamicFeeCalculator.calculate_storage_fee(storage_days)
        total_fee = base_fee + storage_fee
        
        return {
            'base_fee': base_fee,
            'storage_fee': storage_fee,
            'storage_days': storage_days,
            'total_fee': total_fee,
            'package_type': package_type.value,
            'rates_source': 'env_v4'
        }
    
    @staticmethod
    def get_current_rates() -> Dict[str, Any]:
        """Obtener tarifas actuales para mostrar en el frontend"""
        rates = DynamicFeeCalculator.get_rates_from_env()
        return {
            'normal_package_rate': rates['normal'],
            'extra_dimensioned_package_rate': rates['extra_dimensioned'],
            'storage_per_day_rate': rates['storage_per_day'],
            'currency': settings.currency,
            'source': 'env_v4'
        }
