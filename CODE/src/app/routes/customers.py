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
from sqlalchemy import or_, and_, func
from typing import Optional, List
from uuid import UUID
import io
import csv

from app.database import get_db
from app.models.customer import Customer
from app.models.package import Package, PackageStatus
from app.models.message import Message
from app.models.notification import Notification
from app.models.announcement_new import PackageAnnouncementNew
from app.schemas.customer import (
    CustomerCreate, CustomerUpdate, CustomerResponse,
    CustomerListResponse, CustomerStatsResponse,
    CustomerSearchRequest, CustomerBulkUpdateRequest,
    CustomerBulkUpdateResponse, CustomerImportRequest,
    CustomerImportResponse
)
from app.services.customer_service import CustomerService
from app.services.package_service import PackageService
from app.dependencies import get_current_active_user, get_current_admin_user, get_current_active_user_from_cookies
from fastapi import Request
import logging

logger = logging.getLogger(__name__)

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
    try:
        current_user = get_user_from_request(request, db)
        if not current_user:
            raise HTTPException(status_code=401, detail="No autenticado")
        
        # Verificar que sea administrador
        if current_user.role.value != "ADMIN":
            raise HTTPException(status_code=403, detail="Solo administradores pueden eliminar clientes")
        
        # Buscar cliente por UUID
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        # Contar paquetes asociados al cliente
        packages_count = db.query(Package).filter(
            Package.customer_id == customer_id
        ).count()
        
        if packages_count > 0:
            logger.info(f"Cliente {customer_id} tiene {packages_count} paquete(s) asociado(s). Desvinculando paquetes...")
            
            # Desvincular todos los paquetes del cliente estableciendo customer_id a NULL
            # Esto es más seguro que eliminar los paquetes, ya que los paquetes pueden tener
            # su propio ciclo de vida independiente del cliente
            try:
                packages_updated = db.query(Package).filter(
                    Package.customer_id == customer_id
                ).update(
                    {Package.customer_id: None},
                    synchronize_session=False
                )
                db.commit()
                logger.info(f"Desvinculados {packages_updated} paquete(s) del cliente {customer_id} (customer_id establecido a NULL)")
            except Exception as e:
                db.rollback()
                logger.error(f"Error al desvincular paquetes del cliente {customer_id}: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail=f"Error al desvincular {packages_count} paquete(s) del cliente: {str(e)}"
                )
        
        # Ahora eliminar el cliente
        # Las relaciones como messages, notifications, announcements se eliminarán
        # automáticamente por cascade="all, delete-orphan" en SQLAlchemy
        try:
            db.delete(customer)
            db.commit()
            logger.info(f"Cliente {customer_id} ({customer.first_name} {customer.last_name}) eliminado exitosamente. Paquetes desvinculados: {packages_count}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error al eliminar cliente {customer_id}: {str(e)}", exc_info=True)
            
            # Si el error es por restricción de clave foránea, intentar una estrategia alternativa
            if "foreign key constraint" in str(e).lower() or "constraint" in str(e).lower() or "violates foreign key" in str(e).lower():
                # Intentar eliminar primero las relaciones que no se eliminan automáticamente
                try:
                    # Eliminar mensajes del cliente
                    messages_deleted = db.query(Message).filter(Message.customer_id == customer_id).delete(synchronize_session=False)
                    logger.info(f"Eliminados {messages_deleted} mensaje(s) del cliente {customer_id}")
                    
                    # Eliminar notificaciones del cliente
                    notifications_deleted = db.query(Notification).filter(Notification.customer_id == customer_id).delete(synchronize_session=False)
                    logger.info(f"Eliminadas {notifications_deleted} notificación(es) del cliente {customer_id}")
                    
                    # Eliminar anuncios del cliente
                    announcements_deleted = db.query(PackageAnnouncementNew).filter(PackageAnnouncementNew.customer_id == customer_id).delete(synchronize_session=False)
                    logger.info(f"Eliminados {announcements_deleted} anuncio(s) del cliente {customer_id}")
                    
                    # Intentar eliminar el cliente nuevamente
                    db.delete(customer)
                    db.commit()
                    logger.info(f"Cliente {customer_id} eliminado exitosamente después de limpiar relaciones manualmente")
                except Exception as e2:
                    db.rollback()
                    logger.error(f"Error al eliminar cliente después de limpiar relaciones: {str(e2)}", exc_info=True)
                    raise HTTPException(
                        status_code=500,
                        detail=f"Error al eliminar el cliente: {str(e2)}"
                    )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error al eliminar el cliente: {str(e)}"
                )
        
        return None
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        db.rollback()
        # Log the error for debugging
        logger.error(f"Error al eliminar cliente {customer_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Ocurrió un error al eliminar el cliente: {str(e)}"
        )

@router.get("/cleanup/invalid/list", status_code=status.HTTP_200_OK)
async def list_invalid_customers(
    request: Request,
    db: Session = Depends(get_db)
):
    """Listar clientes inválidos que pueden ser eliminados (solo administradores)
    
    Lista clientes que:
    - Se llamen "Sin cliente" (en first_name, last_name, full_name o combinación)
    - No tengan número de teléfono válido (NULL, vacío, o "Sin teléfono" en cualquier variación)
    
    NOTA: Los paquetes que muestran "Sin cliente" y "Sin teléfono" en la interfaz
    son paquetes sin cliente asociado (customer_id = NULL), no clientes reales.
    """
    try:
        current_user = get_user_from_request(request, db)
        if not current_user:
            raise HTTPException(status_code=401, detail="No autenticado")
        
        # Verificar que sea administrador
        if current_user.role.value != "ADMIN":
            raise HTTPException(status_code=403, detail="Solo administradores pueden ver clientes inválidos")
        
        # Buscar clientes inválidos usando SQL directo para mayor flexibilidad
        from sqlalchemy import text
        invalid_customers_query = text("""
            SELECT * FROM customers
            WHERE 
                -- Clientes con "Sin cliente" en cualquier campo de nombre
                (
                    LOWER(TRIM(first_name)) LIKE '%sin cliente%' OR
                    LOWER(TRIM(last_name)) LIKE '%sin cliente%' OR
                    LOWER(TRIM(COALESCE(full_name, ''))) LIKE '%sin cliente%' OR
                    LOWER(TRIM(CONCAT(first_name, ' ', last_name))) LIKE '%sin cliente%' OR
                    LOWER(REPLACE(first_name, ' ', '')) LIKE '%sincliente%' OR
                    LOWER(REPLACE(last_name, ' ', '')) LIKE '%sincliente%' OR
                    LOWER(REPLACE(COALESCE(full_name, ''), ' ', '')) LIKE '%sincliente%'
                )
                OR
                -- Clientes sin teléfono válido
                (
                    phone IS NULL OR
                    TRIM(phone) = '' OR
                    LOWER(TRIM(phone)) LIKE '%sin teléfono%' OR
                    LOWER(TRIM(phone)) LIKE '%sin telefono%' OR
                    LOWER(TRIM(phone)) LIKE '%sintelefono%' OR
                    LOWER(REPLACE(phone, ' ', '')) LIKE '%sintelefono%' OR
                    LOWER(REPLACE(phone, 'é', 'e')) LIKE '%sin telefono%' OR
                    LOWER(REPLACE(REPLACE(phone, ' ', ''), 'é', 'e')) LIKE '%sintelefono%'
                )
        """)
        
        result = db.execute(invalid_customers_query)
        invalid_customers_rows = result.fetchall()
        
        # Convertir resultados a objetos Customer usando los IDs
        invalid_customers = []
        for row in invalid_customers_rows:
            customer_id = row[0]  # El primer campo es el ID
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            if customer:
                invalid_customers.append(customer)
        
        # Si no hay clientes inválidos, verificar si hay paquetes sin cliente
        # y mostrar información sobre ellos
        packages_without_customer = 0
        if not invalid_customers:
            packages_without_customer = db.query(Package).filter(Package.customer_id.is_(None)).count()
            if packages_without_customer > 0:
                logger.info(f"Se encontraron {packages_without_customer} paquete(s) sin cliente asociado")
        
        customers_info = []
        for customer in invalid_customers:
            customer_id = customer.id
            customer_name = f"{customer.first_name} {customer.last_name or ''}".strip()
            phone = customer.phone or "Sin teléfono"
            
            # Contar relaciones
            packages_count = db.query(Package).filter(Package.customer_id == customer_id).count()
            messages_count = db.query(Message).filter(Message.customer_id == customer_id).count()
            notifications_count = db.query(Notification).filter(Notification.customer_id == customer_id).count()
            announcements_count = db.query(PackageAnnouncementNew).filter(PackageAnnouncementNew.customer_id == customer_id).count()
            
            # Determinar razón
            reasons = []
            if "Sin cliente" in customer_name:
                reasons.append("Nombre: 'Sin cliente'")
            if not customer.phone or customer.phone == '' or "Sin teléfono" in phone or "sin telefono" in phone.lower():
                reasons.append("Sin teléfono válido")
            
            customers_info.append({
                "id": str(customer_id),
                "name": customer_name,
                "phone": phone,
                "email": customer.email or None,
                "address": customer.address_street or None,
                "packages_count": packages_count,
                "messages_count": messages_count,
                "notifications_count": notifications_count,
                "announcements_count": announcements_count,
                "reasons": reasons
            })
        
        response = {
            "success": True,
            "count": len(customers_info),
            "customers": customers_info
        }
        
        # Si hay paquetes sin cliente, agregar información adicional
        if packages_without_customer > 0:
            response["packages_without_customer"] = packages_without_customer
            response["message"] = f"No hay clientes inválidos, pero hay {packages_without_customer} paquete(s) sin cliente asociado. Al ejecutar la limpieza, se crearán clientes 'Sin cliente' para estos paquetes y luego se eliminarán."
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en list_invalid_customers: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al listar clientes inválidos: {str(e)}"
        )

@router.delete("/cleanup/invalid", status_code=status.HTTP_200_OK)
async def cleanup_invalid_customers(
    request: Request,
    db: Session = Depends(get_db)
):
    """Eliminar clientes inválidos (solo administradores)
    
    Elimina clientes que:
    - Se llamen "Sin cliente"
    - No tengan número de teléfono (NULL, vacío, o "Sin teléfono")
    """
    try:
        current_user = get_user_from_request(request, db)
        if not current_user:
            raise HTTPException(status_code=401, detail="No autenticado")
        
        # Verificar que sea administrador
        if current_user.role.value != "ADMIN":
            raise HTTPException(status_code=403, detail="Solo administradores pueden eliminar clientes")
        
        # Buscar clientes inválidos usando SQL directo para mayor flexibilidad
        from sqlalchemy import text
        invalid_customers_query = text("""
            SELECT id FROM customers
            WHERE 
                -- Clientes con "Sin cliente" en cualquier campo de nombre
                (
                    LOWER(TRIM(first_name)) LIKE '%sin cliente%' OR
                    LOWER(TRIM(last_name)) LIKE '%sin cliente%' OR
                    LOWER(TRIM(COALESCE(full_name, ''))) LIKE '%sin cliente%' OR
                    LOWER(TRIM(CONCAT(first_name, ' ', last_name))) LIKE '%sin cliente%' OR
                    LOWER(REPLACE(first_name, ' ', '')) LIKE '%sincliente%' OR
                    LOWER(REPLACE(last_name, ' ', '')) LIKE '%sincliente%' OR
                    LOWER(REPLACE(COALESCE(full_name, ''), ' ', '')) LIKE '%sincliente%'
                )
                OR
                -- Clientes sin teléfono válido
                (
                    phone IS NULL OR
                    TRIM(phone) = '' OR
                    LOWER(TRIM(phone)) LIKE '%sin teléfono%' OR
                    LOWER(TRIM(phone)) LIKE '%sin telefono%' OR
                    LOWER(TRIM(phone)) LIKE '%sintelefono%' OR
                    LOWER(REPLACE(phone, ' ', '')) LIKE '%sintelefono%' OR
                    LOWER(REPLACE(phone, 'é', 'e')) LIKE '%sin telefono%' OR
                    LOWER(REPLACE(REPLACE(phone, ' ', ''), 'é', 'e')) LIKE '%sintelefono%'
                )
        """)
        
        result = db.execute(invalid_customers_query)
        invalid_customers_ids = [row[0] for row in result.fetchall()]
        
        # Obtener objetos Customer
        invalid_customers = db.query(Customer).filter(Customer.id.in_(invalid_customers_ids)).all() if invalid_customers_ids else []
        
        # Si no hay clientes inválidos, verificar si hay paquetes sin cliente
        # y crear clientes "Sin cliente" para ellos (luego los eliminaremos)
        if not invalid_customers:
            packages_without_customer = db.query(Package).filter(Package.customer_id.is_(None)).count()
            if packages_without_customer > 0:
                logger.info(f"Se encontraron {packages_without_customer} paquete(s) sin cliente. Creando clientes 'Sin cliente' para limpiarlos...")
                
                # Verificar si ya existe un cliente "Sin cliente" con teléfono "Sin teléfono"
                # Si existe, usarlo; si no, crearlo
                from uuid import uuid4
                from datetime import datetime
                
                # Buscar cliente "Sin cliente" existente usando LIKE para ser más flexible
                existing_sin_cliente = db.query(Customer).filter(
                    func.lower(func.trim(Customer.first_name)).like('%sin cliente%'),
                    or_(
                        func.lower(func.trim(Customer.phone)).like('%sin teléfono%'),
                        func.lower(func.trim(Customer.phone)).like('%sin telefono%')
                    )
                ).first()
                
                if existing_sin_cliente:
                    logger.info(f"Ya existe un cliente 'Sin cliente' (ID: {existing_sin_cliente.id}). Usándolo para asociar paquetes...")
                    sin_cliente_id = existing_sin_cliente.id
                    sin_cliente = existing_sin_cliente
                else:
                    # Crear un cliente "Sin cliente" único para todos los paquetes huérfanos
                    # Usar un teléfono único para evitar conflictos con la restricción unique
                    # El campo phone tiene límite de 20 caracteres, así que usamos solo los primeros 4 caracteres del UUID
                    sin_cliente_id = uuid4()
                    unique_phone = f"SinTel-{sin_cliente_id.hex[:4]}"  # Máximo 13 caracteres
                    
                    sin_cliente = Customer(
                        id=sin_cliente_id,
                        first_name="Sin cliente",
                        last_name="",
                        full_name="Sin cliente",
                        phone=unique_phone,  # Teléfono único para evitar conflictos (máx 20 chars)
                        email=None,
                        address_street="",
                        is_active=False
                    )
                    db.add(sin_cliente)
                    db.flush()  # Para obtener el ID sin hacer commit
                    logger.info(f"Creado nuevo cliente 'Sin cliente' (ID: {sin_cliente_id}) con teléfono único: {unique_phone}")
                
                # Asociar todos los paquetes huérfanos a este cliente
                updated_packages = db.query(Package).filter(Package.customer_id.is_(None)).update(
                    {Package.customer_id: sin_cliente_id},
                    synchronize_session=False
                )
                db.commit()
                
                logger.info(f"Asociados {updated_packages} paquete(s) al cliente 'Sin cliente' (ID: {sin_cliente_id})")
                
                # Refrescar el objeto desde la base de datos para asegurar que esté en la sesión correcta
                sin_cliente = db.query(Customer).filter(Customer.id == sin_cliente_id).first()
                
                if sin_cliente:
                    # Agregar este cliente a la lista de inválidos para eliminarlo
                    invalid_customers = [sin_cliente]
                    logger.info(f"Cliente 'Sin cliente' (ID: {sin_cliente_id}) agregado a la lista de eliminación")
                else:
                    logger.error(f"No se pudo recuperar el cliente 'Sin cliente' después de crearlo/asociarlo (ID: {sin_cliente_id})")
                    raise HTTPException(
                        status_code=500,
                        detail="Error al crear/recuperar cliente temporal para limpieza"
                    )
        
        if not invalid_customers:
            return {
                "success": True,
                "message": "No se encontraron clientes inválidos para eliminar",
                "deleted_count": 0,
                "error_count": 0,
                "deleted_customers": [],
                "error_customers": []
            }
        
        logger.info(f"Encontrados {len(invalid_customers)} cliente(s) inválido(s) para eliminar")
        
        deleted_customers = []
        error_customers = []
        
        for customer in invalid_customers:
            customer_id = customer.id
            customer_name = f"{customer.first_name} {customer.last_name or ''}".strip()
            
            try:
                logger.info(f"Iniciando eliminación de cliente {customer_name} (ID: {customer_id})")
                
                # Contar relaciones
                packages_count = db.query(Package).filter(Package.customer_id == customer_id).count()
                messages_count = db.query(Message).filter(Message.customer_id == customer_id).count()
                notifications_count = db.query(Notification).filter(Notification.customer_id == customer_id).count()
                announcements_count = db.query(PackageAnnouncementNew).filter(PackageAnnouncementNew.customer_id == customer_id).count()
                
                logger.info(f"Cliente {customer_name}: {packages_count} paquete(s), {messages_count} mensaje(s), {notifications_count} notificación(es), {announcements_count} anuncio(s)")
                
                # Desvincular paquetes
                if packages_count > 0:
                    updated = db.query(Package).filter(Package.customer_id == customer_id).update(
                        {Package.customer_id: None},
                        synchronize_session=False
                    )
                    logger.info(f"Desvinculados {updated} paquete(s) del cliente {customer_name}")
                
                # Eliminar relaciones
                if messages_count > 0:
                    deleted_messages = db.query(Message).filter(Message.customer_id == customer_id).delete(synchronize_session=False)
                    logger.info(f"Eliminados {deleted_messages} mensaje(s) del cliente {customer_name}")
                
                if notifications_count > 0:
                    deleted_notifications = db.query(Notification).filter(Notification.customer_id == customer_id).delete(synchronize_session=False)
                    logger.info(f"Eliminadas {deleted_notifications} notificación(es) del cliente {customer_name}")
                
                if announcements_count > 0:
                    deleted_announcements = db.query(PackageAnnouncementNew).filter(PackageAnnouncementNew.customer_id == customer_id).delete(synchronize_session=False)
                    logger.info(f"Eliminados {deleted_announcements} anuncio(s) del cliente {customer_name}")
                
                # Eliminar el cliente
                db.delete(customer)
                db.commit()
                
                # Verificar que el cliente fue eliminado
                customer_exists = db.query(Customer).filter(Customer.id == customer_id).first()
                if customer_exists:
                    logger.error(f"⚠️ El cliente {customer_name} (ID: {customer_id}) NO fue eliminado correctamente")
                    raise Exception("El cliente no fue eliminado correctamente de la base de datos")
                
                deleted_customers.append({
                    "id": str(customer_id),
                    "name": customer_name,
                    "phone": customer.phone or "Sin teléfono",
                    "packages_detached": packages_count,
                    "messages_deleted": messages_count,
                    "notifications_deleted": notifications_count,
                    "announcements_deleted": announcements_count
                })
                
                logger.info(f"✅ Cliente {customer_name} (ID: {customer_id}) eliminado exitosamente")
                
            except Exception as e:
                db.rollback()
                error_message = str(e)
                logger.error(f"❌ Error al eliminar cliente {customer_name} (ID: {customer_id}): {error_message}", exc_info=True)
                error_customers.append({
                    "id": str(customer_id),
                    "name": customer_name,
                    "phone": customer.phone or "Sin teléfono",
                    "error": error_message
                })
        
        return {
            "success": True,
            "message": f"Limpieza completada: {len(deleted_customers)} cliente(s) eliminado(s), {len(error_customers)} error(es)",
            "deleted_count": len(deleted_customers),
            "error_count": len(error_customers),
            "deleted_customers": deleted_customers,
            "error_customers": error_customers
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error en cleanup_invalid_customers: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al limpiar clientes inválidos: {str(e)}"
        )

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