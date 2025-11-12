# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Rutas de Tarifas
Versión: 2.0.0
Fecha: 2025-09-21
Autor: Equipo de Desarrollo
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.models.rate import Rate, RateType
from app.models.user import User
from app.schemas.rate import (
    RateCreate, RateUpdate, RateResponse, RateListResponse,
    RateCalculationRequest, RateCalculationResponse,
    RateSummaryResponse, BulkRateUpdateRequest, BulkRateUpdateResponse
)
from app.services.rate_service import RateService
from app.dependencies import get_current_active_user, get_current_admin_user

router = APIRouter(
    tags=["Tarifas"],
    responses={404: {"description": "Tarifa no encontrada"}}
)

# ========================================
# ENDPOINTS BÁSICOS DE TARIFAS
# ========================================

@router.post("/", response_model=RateResponse, status_code=status.HTTP_201_CREATED)
async def create_rate(
    rate: RateCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Crear una nueva tarifa (Solo administradores)"""
    try:
        rate_service = RateService(db)
        rate_data = rate.dict()
        db_rate = rate_service.create_rate(rate_data, str(current_user.id))
        return RateResponse.model_validate(db_rate)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear tarifa: {str(e)}"
        )

@router.get("/{rate_id}", response_model=RateResponse)
async def get_rate(
    rate_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener una tarifa específica"""
    rate_service = RateService(db)
    rate = rate_service.get_rate_by_id(rate_id)

    if not rate:
        raise HTTPException(status_code=404, detail="Tarifa no encontrada")

    return RateResponse.model_validate(rate)

@router.put("/{rate_id}", response_model=RateResponse)
async def update_rate(
    rate_id: str,
    rate_update: RateUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Actualizar una tarifa (Solo administradores)"""
    try:
        rate_service = RateService(db)
        update_data = rate_update.dict(exclude_unset=True)
        updated_rate = rate_service.update_rate(rate_id, update_data, str(current_user.id))
        return RateResponse.model_validate(updated_rate)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar tarifa: {str(e)}"
        )

@router.delete("/{rate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rate(
    rate_id: str,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Eliminar (desactivar) una tarifa (Solo administradores)"""
    try:
        rate_service = RateService(db)
        rate_service.deactivate_rate(rate_id, str(current_user.id))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al eliminar tarifa: {str(e)}"
        )

# ========================================
# ENDPOINTS DE LISTADO Y BÚSQUEDA
# ========================================

@router.get("/", response_model=RateListResponse)
async def list_rates(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    rate_type: Optional[RateType] = None,
    active_only: bool = Query(True),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Listar tarifas con filtros opcionales"""
    rate_service = RateService(db)

    # Construir query
    query = db.query(Rate)

    if rate_type:
        query = query.filter(Rate.rate_type == rate_type)

    if active_only:
        query = query.filter(Rate.is_active == True)

    # Obtener total
    total = query.count()

    # Aplicar paginación
    rates = query.offset(skip).limit(limit).all()

    return RateListResponse(
        rates=[RateResponse.model_validate(rate) for rate in rates],
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/active", response_model=List[RateResponse])
async def get_active_rates(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener todas las tarifas activas"""
    rate_service = RateService(db)
    active_rates = rate_service.get_active_rates()

    return [RateResponse.model_validate(rate) for rate in active_rates.values()]

@router.get("/type/{rate_type}", response_model=List[RateResponse])
async def get_rates_by_type(
    rate_type: RateType,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener tarifas por tipo"""
    rate_service = RateService(db)
    rates = rate_service.get_rates_by_type(rate_type)

    return [RateResponse.model_validate(rate) for rate in rates]

# ========================================
# ENDPOINTS DE CÁLCULO
# ========================================

@router.post("/calculate", response_model=RateCalculationResponse)
async def calculate_rate(
    calculation: RateCalculationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Calcular tarifa para un paquete"""
    try:
        rate_service = RateService(db)

        # Convertir string a PackageType
        from app.models.package import PackageType
        package_type = PackageType(calculation.package_type)

        costs = rate_service.calculate_package_costs(
            package_type=package_type,
            storage_days=calculation.storage_days or 0,
            delivery_required=calculation.delivery_required
        )

        # Obtener tarifas aplicadas
        active_rates = rate_service.get_active_rates()

        return RateCalculationResponse(
            base_cost=costs["base_cost"],
            storage_cost=costs["storage_cost"],
            delivery_cost=costs["delivery_cost"],
            total_cost=costs["total_cost"],
            breakdown={
                "package_type": calculation.package_type,
                "storage_days": calculation.storage_days,
                "delivery_required": calculation.delivery_required
            },
            applied_rates={
                rate_type: {
                    "name": rate.name,
                    "base_price": float(rate.base_price),
                    "multiplier": float(rate.package_type_multiplier)
                }
                for rate_type, rate in active_rates.items()
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error en cálculo de tarifa: {str(e)}"
        )

# ========================================
# ENDPOINTS DE GESTIÓN MASIVA
# ========================================

@router.post("/bulk-update", response_model=BulkRateUpdateResponse)
async def bulk_update_rates(
    bulk_update: BulkRateUpdateRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Actualización masiva de tarifas (Solo administradores)"""
    try:
        rate_service = RateService(db)
        updates = bulk_update.updates.dict(exclude_unset=True)

        result = rate_service.bulk_update_rates(
            [str(rate_id) for rate_id in bulk_update.rate_ids],
            updates,
            str(current_user.id)
        )

        return BulkRateUpdateResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error en actualización masiva: {str(e)}"
        )

# ========================================
# ENDPOINTS DE ESTADÍSTICAS Y REPORTES
# ========================================

@router.get("/summary", response_model=RateSummaryResponse)
async def get_rate_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener resumen de tarifas"""
    rate_service = RateService(db)
    summary = rate_service.get_rate_summary()

    return RateSummaryResponse(**summary)

@router.get("/history", response_model=List[RateResponse])
async def get_rate_history(
    rate_type: Optional[RateType] = None,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener historial de cambios de tarifas"""
    rate_service = RateService(db)
    history = rate_service.get_rate_history(rate_type, limit)

    return [RateResponse.model_validate(rate) for rate in history]

# ========================================
# ENDPOINTS DE VALIDACIÓN
# ========================================

@router.post("/validate")
async def validate_rate_data(
    rate_data: RateCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Validar datos de tarifa sin crear"""
    try:
        rate_service = RateService(db)
        rate_service.validate_rate_data(rate_data.dict())

        return {
            "valid": True,
            "message": "Los datos de tarifa son válidos"
        }
    except Exception as e:
        return {
            "valid": False,
            "message": str(e)
        }
