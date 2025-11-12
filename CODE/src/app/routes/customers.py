# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Rutas de Clientes
Versión: 2.0.0
Fecha: 2025-09-21
Autor: Equipo de Desarrollo
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
import io
import csv

from app.database import get_db
from app.models.customer import Customer
from app.schemas.customer import (
    CustomerCreate, CustomerUpdate, CustomerResponse,
    CustomerListResponse, CustomerStatsResponse,
    CustomerSearchRequest, CustomerBulkUpdateRequest,
    CustomerBulkUpdateResponse, CustomerImportRequest,
    CustomerImportResponse
)
from app.services.customer_service import CustomerService
from app.dependencies import get_current_active_user, get_current_admin_user, get_current_active_user_from_cookies
from fastapi import Request

router = APIRouter(
    tags=["Clientes"],
    responses={404: {"description": "Cliente no encontrado"}}
)

def get_user_from_request(request: Request, db: Session):
    """Obtener usuario desde cookies o Bearer token"""
    from app.models.user import User
    
    # Intentar desde cookies primero
    try:
        user = get_current_active_user_from_cookies(request, db)
        if user:
            return user
    except HTTPException as e:
        # Si es HTTPException 401, continuar para intentar Bearer token
        if e.status_code == 401:
            pass
        else:
            raise
    except Exception:
        # Si falla con cookies, intentar desde Bearer token
        pass
    
    # Intentar desde Bearer token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        from app.utils.auth import get_user_from_token
        from app.services.user_service import UserService
        user_data = get_user_from_token(token)
        if user_data:
            user_service = UserService()
            user = user_service.get_by_id(db, int(user_data["user_id"]))
            if user and user.is_active:
                return user
    
    return None

# ========================================
# ENDPOINTS BÁSICOS DE CRUD
# ========================================

@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer: CustomerCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Crear un nuevo cliente"""
    current_user = get_user_from_request(request, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    customer_service = CustomerService()
    try:
        db_customer = customer_service.create_customer(
            db=db,
            customer_data=customer,
            created_by_id=current_user.id
        )
        return CustomerResponse.model_validate(db_customer)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: UUID,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener un cliente específico"""
    customer_service = CustomerService()
    customer = customer_service.get_by_id(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return CustomerResponse.model_validate(customer)

@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: UUID,
    customer_update: CustomerUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Actualizar un cliente"""
    current_user = get_user_from_request(request, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    customer_service = CustomerService()
    try:
        db_customer = customer_service.update_customer(
            db=db,
            customer_id=customer_id,
            customer_data=customer_update,
            updated_by_id=current_user.id
        )
        return CustomerResponse.model_validate(db_customer)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: UUID,
    request: Request,
    db: Session = Depends(get_db)
):
    """Eliminar un cliente (solo administradores)"""
    current_user = get_user_from_request(request, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    # Verificar que sea administrador
    if current_user.role.value != "ADMIN":
        raise HTTPException(status_code=403, detail="Solo administradores pueden eliminar clientes")
    
    customer_service = CustomerService()
    # Buscar cliente por UUID
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # Eliminar cliente directamente
    db.delete(customer)
    db.commit()
    
    return None

# ========================================
# ENDPOINTS DE LISTADO Y BÚSQUEDA
# ========================================

@router.get("/", response_model=CustomerListResponse)
async def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    search_by: str = Query("all", regex="^(all|name|phone|email|document)$"),
    is_active: Optional[bool] = None,
    is_vip: Optional[bool] = None,
    city: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Listar clientes con filtros opcionales"""
    customer_service = CustomerService()
    customers, total = customer_service.search_customers_advanced(
        db=db,
        query=search or "",
        search_by=search_by,
        is_active=is_active,
        is_vip=is_vip,
        city=city,
        skip=skip,
        limit=limit
    )

    return CustomerListResponse(
        customers=[CustomerResponse.model_validate(customer) for customer in customers],
        total=total,
        skip=skip,
        limit=limit,
        search_term=search
    )

@router.post("/search", response_model=CustomerListResponse)
async def search_customers(
    search_request: CustomerSearchRequest,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Buscar clientes con criterios avanzados"""
    customer_service = CustomerService()
    customers, total = customer_service.search_customers_advanced(
        db=db,
        query=search_request.query,
        search_by=search_request.search_by,
        skip=skip,
        limit=limit
    )

    return CustomerListResponse(
        customers=[CustomerResponse.model_validate(customer) for customer in customers],
        total=total,
        skip=skip,
        limit=limit,
        search_term=search_request.query
    )

# ========================================
# ENDPOINTS DE ESTADÍSTICAS
# ========================================

@router.get("/stats/summary", response_model=CustomerStatsResponse)
async def get_customer_stats(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas generales de clientes"""
    customer_service = CustomerService()
    return customer_service.get_customer_stats(db)

@router.get("/vip/list")
async def get_vip_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener lista de clientes VIP"""
    customer_service = CustomerService()
    customers = customer_service.get_vip_customers(db, skip, limit)
    return {
        "customers": [CustomerResponse.model_validate(customer) for customer in customers],
        "total": len(customers),
        "skip": skip,
        "limit": limit
    }

# ========================================
# ENDPOINTS DE GESTIÓN AVANZADA
# ========================================

@router.post("/{customer_id}/deactivate", response_model=CustomerResponse)
async def deactivate_customer(
    customer_id: UUID,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Desactivar un cliente"""
    customer_service = CustomerService()
    try:
        customer = customer_service.deactivate_customer(
            db=db,
            customer_id=customer_id,
            updated_by_id=current_user.get("id")
        )
        return CustomerResponse.model_validate(customer)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{customer_id}/reactivate", response_model=CustomerResponse)
async def reactivate_customer(
    customer_id: UUID,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Reactivar un cliente"""
    customer_service = CustomerService()
    try:
        customer = customer_service.reactivate_customer(
            db=db,
            customer_id=customer_id,
            updated_by_id=current_user.get("id")
        )
        return CustomerResponse.model_validate(customer)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/merge")
async def merge_customers(
    primary_customer_id: UUID,
    duplicate_customer_id: UUID,
    strategy: str = Query("keep_primary", regex="^(keep_primary|keep_most_recent|manual)$"),
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Fusionar clientes duplicados (solo administradores)"""
    customer_service = CustomerService()
    try:
        merged_customer = customer_service.merge_customers(
            db=db,
            primary_id=primary_customer_id,
            duplicate_id=duplicate_customer_id,
            strategy=strategy
        )
        return {
            "message": "Clientes fusionados exitosamente",
            "customer": CustomerResponse.model_validate(merged_customer)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/bulk-update", response_model=CustomerBulkUpdateResponse)
async def bulk_update_customers(
    bulk_update: CustomerBulkUpdateRequest,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Actualización masiva de clientes (solo administradores)"""
    customer_service = CustomerService()
    try:
        result = customer_service.bulk_update_customers(
            db=db,
            customer_ids=bulk_update.customer_ids,
            updates=bulk_update.updates,
            updated_by_id=current_user.get("id")
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ========================================
# ENDPOINTS DE IMPORTACIÓN/EXPORTACIÓN
# ========================================

@router.post("/import/csv", response_model=CustomerImportResponse)
async def import_customers_csv(
    file: UploadFile = File(...),
    update_existing: bool = Query(False, description="Actualizar clientes existentes"),
    skip_duplicates: bool = Query(True, description="Omitir duplicados"),
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Importar clientes desde archivo CSV (solo administradores)"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="El archivo debe ser un CSV")

    try:
        content = await file.read()
        csv_data = content.decode('utf-8')

        customer_service = CustomerService()
        result = customer_service.import_customers_csv(
            db=db,
            csv_data=csv_data,
            update_existing=update_existing,
            skip_duplicates=skip_duplicates
        )

        return CustomerImportResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al importar CSV: {str(e)}")

@router.get("/export/csv")
async def export_customers_csv(
    is_active: Optional[bool] = None,
    is_vip: Optional[bool] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Exportar clientes a CSV"""
    customer_service = CustomerService()

    # Obtener clientes con filtros
    customers, _ = customer_service.search_customers_advanced(
        db=db,
        is_active=is_active,
        is_vip=is_vip,
        limit=10000  # Límite razonable para exportación
    )

    # Crear CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Headers
    headers = [
        'id', 'first_name', 'last_name', 'full_name', 'phone', 'email',
        'document_type', 'document_number', 'address_street', 'address_city',
        'building_name', 'tower', 'apartment', 'is_active', 'is_vip',
        'total_packages_received', 'total_packages_delivered', 'created_at'
    ]
    writer.writerow(headers)

    # Data
    for customer in customers:
        writer.writerow([
            str(customer.id),
            customer.first_name,
            customer.last_name,
            customer.full_name,
            customer.phone,
            customer.email,
            customer.document_type,
            customer.document_number,
            customer.address_street,
            customer.address_city,
            customer.building_name,
            customer.tower,
            customer.apartment,
            customer.is_active,
            customer.is_vip,
            customer.total_packages_received,
            customer.total_packages_delivered,
            customer.created_at.isoformat() if customer.created_at else ''
        ])

    output.seek(0)

    return StreamingResponse(
        io.StringIO(output.getvalue()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=customers.csv"}
    )

# ========================================
# ENDPOINTS DE VALIDACIÓN
# ========================================

@router.post("/validate")
async def validate_customer_data(
    customer_data: CustomerCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Validar datos de cliente sin crear"""
    try:
        customer_service = CustomerService()
        # Intentar crear el cliente para validar
        temp_customer = Customer(**customer_data.dict())
        # Aquí podríamos agregar validaciones adicionales

        return {
            "valid": True,
            "message": "Los datos del cliente son válidos"
        }
    except Exception as e:
        return {
            "valid": False,
            "message": str(e)
        }

# ========================================
# ENDPOINTS DE BÚSQUEDA RÁPIDA
# ========================================

@router.get("/search/phone/{phone}")
async def get_customer_by_phone(
    phone: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Buscar cliente por teléfono"""
    customer_service = CustomerService()
    customer = customer_service.get_customer_by_phone(db, phone)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return CustomerResponse.model_validate(customer)

@router.get("/search/email/{email}")
async def get_customer_by_email(
    email: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Buscar cliente por email"""
    customer_service = CustomerService()
    customer = customer_service.get_customer_by_email(db, email)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return CustomerResponse.model_validate(customer)

@router.get("/search/document/{document_number}")
async def get_customer_by_document(
    document_number: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Buscar cliente por número de documento"""
    customer_service = CustomerService()
    customer = customer_service.get_customer_by_document(db, document_number)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return CustomerResponse.model_validate(customer)