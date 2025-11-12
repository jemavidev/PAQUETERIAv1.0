# ========================================
# PAQUETES EL CLUB v4.0 - Router de Paquetes
# ========================================
# Archivo: CODE/LOCAL/src/app/routes/packages.py (siguiendo reglas de AGENTS.md)
# Versión: 2.0.0
# Fecha: 2025-09-24
# Autor: Equipo de Desarrollo
# ========================================

"""
Router de paquetes para PAQUETES EL CLUB
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.dependencies import get_current_active_user, get_current_active_user_from_cookies
from app.models.user import User
from app.models.file_upload import FileUpload, FileType
from app.config import settings
from app.models.package import Package, PackageStatus, PackageType, PackageCondition
from app.services.s3_service import S3Service
from app.schemas.package import (
    PackageCreate, PackageUpdate, PackageResponse,
    PackageStatusUpdate, PackageSearch, PackageStats,
    PackageAnnouncement, PackageReceiveRequest, PackageReceiveResponse,
    PackageDeliverRequest, PackageDeliverResponse,
    PackageCancelRequest, PackageCancelResponse,
    PackageFeeCalculation
)
from app.services.package_state_service import PackageStateService
from app.services.package_service import PackageService
from app.services.email_service import EmailService
from app.models.notification import NotificationEvent, NotificationPriority
from app.utils.datetime_utils import get_colombia_now
from app.utils.normalization import normalize_package_item, normalize_status, normalize_type, normalize_condition

# Crear router
router = APIRouter(
    tags=["Paquetes"],
    responses={404: {"description": "Paquete no encontrado"}}
)


# ========================================
# ENDPOINTS BÁSICOS DE CRUD
# ========================================

@router.post("/", response_model=PackageResponse, status_code=status.HTTP_201_CREATED)
async def create_package(
    package: PackageCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Crear un nuevo paquete"""
    package_service = PackageService()
    try:
        db_package = package_service.create_package(
            db=db,
            package_in=package,
            user_id=current_user.get("id")
        )
        return PackageResponse.model_validate(db_package)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{package_id}")
async def get_package(
    package_id: str,  # Changed to str to handle announcement IDs
    # Temporarily disabled for testing: current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener un paquete específico o datos de anuncio"""
    from sqlalchemy import text
    
    # Check if this is an announcement ID
    if package_id.startswith('announcement_'):
        tracking_code = package_id.replace('announcement_', '')
        
        # Get announcement data
        announcement_query = text("""
            SELECT customer_name, customer_phone, guide_number, tracking_code, announced_at
            FROM package_announcements_new
            WHERE tracking_code = :tracking_code AND is_processed = false
        """)
        result = db.execute(announcement_query, {"tracking_code": tracking_code})
        announcement = result.fetchone()
        
        if not announcement:
            raise HTTPException(status_code=404, detail="Anuncio no encontrado o ya procesado")
        
        # Return announcement data in package format
        return {
            'id': package_id,
            'tracking_number': announcement[3],
            'customer_name': announcement[0],
            'customer_phone': announcement[1],
            'guide_number': announcement[2],
            'package_type': 'normal',
            'status': 'announced',
            'package_condition': 'ok',
            'access_code': '',
            'baroti': None,
            'observations': None,
            'announced_at': announcement[4].isoformat() if announcement[4] else None,
            'received_at': None,
            'delivered_at': None,
            'cancelled_at': None,
            'base_fee': float(settings.base_delivery_rate_normal),
            'storage_fee': 0.00,
            'total_amount': float(settings.base_delivery_rate_normal),
            'customer_id': None,
            'created_at': announcement[4].isoformat() if announcement[4] else None,
            'updated_at': announcement[4].isoformat() if announcement[4] else None,
            'is_announcement': True
        }
    else:
        # Handle regular package
        try:
            package_id_int = int(package_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="ID de paquete inválido")
            
        package_service = PackageService()
        package = package_service.get_package_with_correct_fees(db, package_id_int)
        if not package:
            raise HTTPException(status_code=404, detail="Paquete no encontrado")

        # Create custom response with customer data
        package_dict = {
            'id': package.id,
            'tracking_number': package.tracking_number,
            'customer_name': package.customer.full_name if package.customer else 'Sin cliente',
            'customer_phone': package.customer.phone if package.customer else 'Sin teléfono',
            'package_type': package.package_type.value,
            'status': package.status.value,
            'package_condition': package.package_condition.value,
            'access_code': package.access_code,
            'baroti': package.posicion,
            # 'observations': package.observations,  # Campo eliminado del modelo
            'announced_at': package.announced_at.isoformat() if package.announced_at else None,
            'received_at': package.received_at.isoformat() if package.received_at else None,
            'delivered_at': package.delivered_at.isoformat() if package.delivered_at else None,
            'cancelled_at': package.cancelled_at.isoformat() if package.cancelled_at else None,
            'base_fee': float(package.base_fee or 0),
            'storage_fee': float(package.storage_fee or 0),
            'total_amount': float(package.total_amount or 0),
            'customer_id': package.customer_id,
            'created_by': package.created_by,
            'updated_by': package.updated_by,
            'created_at': package.created_at.isoformat() if package.created_at else None,
            'updated_at': package.updated_at.isoformat() if package.updated_at else None,
            'is_announcement': False
        }
        return package_dict


@router.put("/{package_id}", response_model=PackageResponse)
async def update_package(
    package_id: int,
    package_update: PackageUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Actualizar un paquete"""
    package_service = PackageService()
    try:
        db_package = package_service.update(
            db=db,
            id=package_id,
            obj_in=package_update
        )
        return PackageResponse.model_validate(db_package)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{package_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_package(
    package_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Eliminar un paquete"""
    package_service = PackageService()
    package = package_service.get_by_id(db, package_id)
    if not package:
        raise HTTPException(status_code=404, detail="Paquete no encontrado")

    package_service.delete(db, package_id)


# ========================================
# ENDPOINTS DE LISTADO Y BÚSQUEDA
# ========================================

@router.get("/")
async def list_packages(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status_filter: Optional[str] = Query(None, description="Filtrar por estado"),
    customer_id: Optional[int] = Query(None, description="Filtrar por cliente"),
    # Temporarily disabled for testing: current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Listar paquetes con filtros opcionales y paginación (10 por página)"""
    # Get both packages and unprocessed package announcements
    from sqlalchemy import text
    import logging
    logger = logging.getLogger(__name__)

    # Get packages
    packages_query = """
        SELECT
            p.id, p.tracking_number, p.guide_number, p.package_type, p.status, p.package_condition,
            p.access_code, p.posicion, NULL as observations, p.announced_at, p.received_at,
            p.delivered_at, p.cancelled_at, p.base_fee, p.storage_fee, p.total_amount,
            p.customer_id, p.created_at, p.updated_at,
            COALESCE(c.full_name, 'Sin cliente') as customer_name,
            COALESCE(c.phone, 'Sin teléfono') as customer_phone,
            c.email as customer_email,
            CASE 
                WHEN p.received_at IS NOT NULL THEN 
                    FLOOR(EXTRACT(EPOCH FROM (NOW() - p.received_at)) / 86400)
                ELSE 0
            END as storage_days
        FROM packages p
        LEFT JOIN customers c ON p.customer_id = c.id
        ORDER BY p.created_at DESC
    """

    packages_result = db.execute(text(packages_query))
    packages_data = packages_result.fetchall()

    # Get unprocessed package announcements (including cancelled ones)
    announcements_query = f"""
        SELECT
            CONCAT('announcement_', a.tracking_code) as id,
            a.tracking_code as tracking_number,
            'normal' as package_type,
            CASE 
                WHEN a.is_active = false THEN 'cancelado'
                ELSE 'announced'
            END as status,
            'ok' as package_condition,
            '' as access_code,
            NULL as posicion,
            NULL as observations,
            a.announced_at,
            NULL as received_at,
            NULL as delivered_at,
            CASE 
                WHEN a.is_active = false THEN a.updated_at
                ELSE NULL
            END as cancelled_at,
            {settings.base_delivery_rate_normal} as base_fee,
            0.00 as storage_fee,
            {settings.base_delivery_rate_normal} as total_amount,
            NULL as customer_id,
            a.announced_at as created_at,
            a.announced_at as updated_at,
            a.customer_name,
            a.customer_phone,
            a.guide_number
        FROM package_announcements_new a
        WHERE a.is_processed = false
        ORDER BY a.announced_at DESC
    """

    announcements_result = db.execute(text(announcements_query))
    announcements_data = announcements_result.fetchall()

    # Combine packages and announcements
    all_items = []

    # Add packages
    for row in packages_data:
        # Calcular storage_fee actualizado basado en storage_days
        storage_days = int(row[22] or 0)  # storage_days es el índice 22 (después de customer_email)
        storage_fee = float(storage_days * settings.base_storage_rate)  # Tarifa por día desde configuración
        total_amount = float(row[13] or 0) + storage_fee  # base_fee + storage_fee
        
        item_dict = {
            'id': str(row[0]),  # Convert to string for frontend
            'tracking_number': row[1],
            'guide_number': row[2],
            'customer_name': row[19],
            'customer_phone': row[20],
            'customer_email': row[21],  # Email del cliente (puede ser None)
            'package_type': row[3] or 'normal',
            'status': row[4] or 'ANUNCIADO',
            'package_condition': row[5] or 'BUENO',
            'access_code': row[6] or '',
            'baroti': row[7],
            'observations': row[8],
            'announced_at': row[9].isoformat() if row[9] else None,
            'received_at': row[10].isoformat() if row[10] else None,
            'delivered_at': row[11].isoformat() if row[11] else None,
            'cancelled_at': row[12].isoformat() if row[12] else None,
            'base_fee': float(row[13] or 0),
            'storage_fee': storage_fee,
            'storage_days': storage_days,
            'total_amount': total_amount,
            'customer_id': row[16],
            'created_at': row[17].isoformat() if row[17] else None,
            'updated_at': row[18].isoformat() if row[18] else None,
            'is_announcement': False  # Flag to identify if it's an announcement
        }
        all_items.append(normalize_package_item(item_dict))

    # Add announcements
    for row in announcements_data:
        item_dict = {
            'id': row[0],  # This will be 'announcement_uuid'
            'tracking_number': row[1],
            'customer_name': row[18],
            'customer_phone': row[19],
            'guide_number': row[20],  # Guide number from announcement
            'package_type': row[2],  # normalized later
            'status': row[3],        # normalized later
            'package_condition': row[4],
            'access_code': row[5],
            'baroti': row[6],
            'observations': row[7],
            'announced_at': row[8].isoformat() if row[8] else None,
            'received_at': row[9],
            'delivered_at': row[10],
            'cancelled_at': row[11],
            'base_fee': float(row[12]),
            'storage_fee': float(row[13]),
            'storage_days': 0,  # Los anuncios no tienen días de almacenamiento
            'total_amount': float(row[14]),
            'customer_id': row[15],
            'created_at': row[16].isoformat() if row[16] else None,
            'updated_at': row[17].isoformat() if row[17] else None,
            'is_announcement': True  # Flag to identify if it's an announcement
        }
        all_items.append(normalize_package_item(item_dict))

    # Aplicar filtro de estado si se proporciona (ANTES de la paginación)
    if status_filter:
        # Normalizar el estado del filtro usando la función de normalización
        status_filter_normalized = normalize_status(status_filter)
        
        # Filtrar items por estado
        # Los estados ya están normalizados por normalize_package_item a formato MAYÚSCULAS
        filtered_items = []
        for item in all_items:
            item_status = item.get('status', '')
            # Comparar el estado normalizado del item con el estado normalizado del filtro
            if item_status and item_status.upper() == status_filter_normalized:
                filtered_items.append(item)
        
        all_items = filtered_items

    # Sort by creation date (most recent first)
    all_items.sort(key=lambda x: x['created_at'] or '', reverse=True)

    # Calcular información de paginación (después del filtro)
    total_items = len(all_items)
    total_pages = (total_items + limit - 1) // limit if total_items > 0 else 1
    current_page = (skip // limit) + 1
    has_prev = skip > 0
    has_next = skip + limit < total_items

    # Apply pagination
    start_idx = skip
    end_idx = skip + limit
    paginated_items = all_items[start_idx:end_idx]

    # Retornar con información de paginación
    return {
        "packages": paginated_items,
        "pagination": {
            "page": current_page,
            "limit": limit,
            "total": total_items,
            "total_pages": total_pages,
            "has_prev": has_prev,
            "has_next": has_next
        }
    }


@router.post("/search", response_model=List[PackageResponse])
async def search_packages(
    search_request: PackageSearch,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Buscar paquetes por tracking, nombre o teléfono"""
    package_service = PackageService()
    packages = package_service.search_packages(
        db=db,
        search=search_request
    )

    # Aplicar paginación manual ya que search_packages no la maneja
    start_idx = skip
    end_idx = skip + limit
    paginated_packages = packages[start_idx:end_idx]

    return [PackageResponse.model_validate(package) for package in paginated_packages]


# ========================================
# ENDPOINTS DE ESTADO Y GESTIÓN
# ========================================

@router.put("/{package_id}/status")
async def update_package_status(
    package_id: str,  # Changed to str to handle announcement IDs
    status_update: PackageStatusUpdate,
    # Temporarily disabled for testing: current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Actualizar el estado de un paquete o procesar un anuncio"""
    print(f"🚀🚀🚀 ENDPOINT CALLED: update_package_status with package_id={package_id}")
    print(f"🚀🚀🚀 ENDPOINT CALLED: status_update={status_update}")
    print(f"🚀🚀🚀 ENDPOINT CALLED: status_update.status={status_update.status}")
    print(f"🚀🚀🚀 ENDPOINT CALLED: status_update.dict()={status_update.dict()}")
    package_service = PackageService()

    try:
        # Check if this is an announcement ID
        if package_id.startswith('announcement_'):
            tracking_code = package_id.replace('announcement_', '')

            # Only allow 'received' status for announcements (to process them)
            if status_update.status != PackageStatus.RECIBIDO:
                raise HTTPException(status_code=400, detail="Los anuncios solo pueden ser marcados como recibidos")

            # Process the announcement into a package
            from sqlalchemy import text

            # Get announcement data
            announcement_query = text("""
                SELECT customer_name, customer_phone, guide_number, tracking_code, id
                FROM package_announcements_new
                WHERE tracking_code = :tracking_code AND is_processed = false
            """)
            result = db.execute(announcement_query, {"tracking_code": tracking_code})
            announcement = result.fetchone()

            if not announcement:
                raise HTTPException(status_code=404, detail="Anuncio no encontrado o ya procesado")

            # Create package from announcement
            announcement_data = PackageAnnouncement(
                customer_name=announcement[0],
                customer_phone=announcement[1],
                guide_number=announcement[2],
                tracking_number=announcement[3]  # Use the original tracking_code
            )

            # Create the package
            db_package = package_service.announce_package(db=db, announcement=announcement_data)

            # Mark announcement as processed
            import uuid
            update_query = text("""
                UPDATE package_announcements_new
                SET is_processed = true, package_id = :package_id
                WHERE tracking_code = :tracking_code
            """)
            db.execute(update_query, {
                "package_id": db_package['package_id'],
                "tracking_code": tracking_code
            })
            db.commit()

            # Return the created package data
            return {
                'id': db_package['package_id'],
                'tracking_number': db_package['tracking_number'],
                'customer_name': announcement[0],
                'customer_phone': announcement[1],
                'package_type': 'normal',
                'status': 'announced',
                'package_condition': 'ok',
                'access_code': db_package['access_code'],
                'announced_at': None,  # No longer available in the response
                'base_fee': db_package['base_fee'],
                'storage_fee': db_package['storage_fee'],
                'total_amount': db_package['total_amount'],
                'is_announcement': False
            }

        else:
            # Handle regular package status updates
            package_id_int = int(package_id)
            print(f"🔄 DEBUG: Updating package {package_id_int} status to {status_update.status}")
            
            # Get current package status for debugging
            current_package = db.query(Package).filter(Package.id == package_id_int).first()
            if current_package:
                print(f"🔄 DEBUG: Current package status: {current_package.status}")
                print(f"🔄 DEBUG: Current package status value: {current_package.status.value}")
                print(f"🔄 DEBUG: Current package status type: {type(current_package.status)}")
                print(f"🔄 DEBUG: New status: {status_update.status}")
                print(f"🔄 DEBUG: New status value: {status_update.status.value}")
                print(f"🔄 DEBUG: New status type: {type(status_update.status)}")
                print(f"🔄 DEBUG: Transition: {current_package.status.value} -> {status_update.status.value}")
                
                # Check if transition is allowed
                from app.services.package_state_service import PackageStateService
                print(f"🔄 DEBUG: Current status enum: {current_package.status}")
                print(f"🔄 DEBUG: Current status enum type: {type(current_package.status)}")
                print(f"🔄 DEBUG: Current status enum value: {current_package.status.value}")
                print(f"🔄 DEBUG: New status enum: {status_update.status}")
                print(f"🔄 DEBUG: New status enum type: {type(status_update.status)}")
                print(f"🔄 DEBUG: New status enum value: {status_update.status.value}")
                
                # Check allowed transitions for current status
                allowed_transitions = PackageStateService.ALLOWED_TRANSITIONS.get(current_package.status, [])
                print(f"🔄 DEBUG: Allowed transitions for {current_package.status.value}: {[t.value for t in allowed_transitions]}")
                
                is_allowed = PackageStateService.is_transition_allowed(current_package.status, status_update.status)
                print(f"🔄 DEBUG: Is transition allowed? {is_allowed}")
            else:
                print(f"🔄 DEBUG: Package {package_id_int} not found!")
            
            db_package = package_service.update_package_status(
                db=db,
                package_id=package_id_int,
                status_update=status_update,
                user_id=1  # Temporarily hardcoded for testing
            )

            # Determinar mensaje según el estado
            status_messages = {
                'ENTREGADO': f'✅ Paquete entregado exitosamente a {db_package.customer.full_name if db_package.customer else "cliente"}',
                'RECIBIDO': f'✅ Paquete recibido exitosamente',
                'ANUNCIADO': f'✅ Paquete anunciado exitosamente',
                'CANCELADO': f'⚠️ Paquete cancelado'
            }
            
            success_message = status_messages.get(
                status_update.status.upper(), 
                f'✅ Estado actualizado a {status_update.status}'
            )

            # Return package data with success message
            return {
                'success': True,
                'message': success_message,
                'id': db_package.id,
                'tracking_number': db_package.tracking_number,
                'customer_name': db_package.customer.full_name if db_package.customer else 'Sin cliente',
                'customer_phone': db_package.customer.phone if db_package.customer else 'Sin teléfono',
                'package_type': db_package.package_type.value if db_package.package_type else 'normal',
                'status': db_package.status.value if db_package.status else 'announced',
                'package_condition': db_package.package_condition.value if db_package.package_condition else 'ok',
                'access_code': db_package.access_code,
                'baroti': db_package.posicion,
                # 'observations': db_package.observations,  # Campo eliminado del modelo
                'announced_at': db_package.announced_at.isoformat() if db_package.announced_at else None,
                'received_at': db_package.received_at.isoformat() if db_package.received_at else None,
                'delivered_at': db_package.delivered_at.isoformat() if db_package.delivered_at else None,
                'cancelled_at': db_package.cancelled_at.isoformat() if db_package.cancelled_at else None,
                'base_fee': float(db_package.base_fee or 0),
                'storage_fee': float(db_package.storage_fee or 0),
                'total_amount': float(db_package.total_amount or 0),
                'customer_id': db_package.customer_id,
                'created_at': db_package.created_at.isoformat() if db_package.created_at else None,
                'updated_at': db_package.updated_at.isoformat() if db_package.updated_at else None,
                'is_announcement': False
            }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar: {str(e)}")


# ========================================
# ENDPOINTS DE ESTADÍSTICAS
# ========================================

@router.get("/stats/summary", response_model=PackageStats)
async def get_package_stats(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas de paquetes"""
    package_service = PackageService()
    stats = package_service.get_package_stats(db)

    return PackageStats(
        total_packages=stats.get('total_packages', 0),
        announced_count=stats.get('status_breakdown', {}).get('announced', 0),
        received_count=stats.get('status_breakdown', {}).get('received', 0),
        delivered_count=stats.get('status_breakdown', {}).get('delivered', 0),
        cancelled_count=stats.get('status_breakdown', {}).get('cancelled', 0),
        total_revenue=stats.get('total_revenue', 0)
    )


# ========================================
# ENDPOINTS DE BÚSQUEDA RÁPIDA
# ========================================

@router.get("/tracking/{tracking_number}", response_model=PackageResponse)
async def get_package_by_tracking(
    tracking_number: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Buscar paquete por número de tracking"""
    package_service = PackageService()
    package = package_service.get_package_by_tracking(db, tracking_number)
    if not package:
        raise HTTPException(status_code=404, detail="Paquete no encontrado")
    return PackageResponse.model_validate(package)


@router.get("/customer/{customer_id}/packages", response_model=List[PackageResponse])
async def get_customer_packages(
    customer_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener paquetes de un cliente específico"""
    package_service = PackageService()
    packages = package_service.get_packages_by_customer(
        db=db,
        customer_id=customer_id,
        skip=skip,
        limit=limit
    )

    return [PackageResponse.model_validate(package) for package in packages]


# ========================================
# NUEVOS ENDPOINTS PARA TRANSICIONES AVANZADAS
# ========================================

@router.post("/receive", response_model=PackageReceiveResponse, status_code=status.HTTP_201_CREATED)
async def receive_package_from_announcement(
    request: PackageReceiveRequest,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Recibir paquete desde anuncio con verificación completa"""
    try:
        # Verificar permisos (solo operadores y admin)
        if current_user.role.value not in ["ADMIN", "OPERADOR"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para recibir paquetes"
            )

        result = PackageStateService.receive_package_from_announcement(
            db=db,
            request=request
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al recibir paquete: {str(e)}"
        )


@router.post("/{package_id}/deliver", response_model=PackageDeliverResponse)
async def deliver_package_with_payment(
    package_id: int,
    request: PackageDeliverRequest,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Entregar paquete con registro de pago"""
    try:
        # Verificar permisos (solo operadores y admin)
        if current_user.role.value not in ["ADMIN", "OPERADOR"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para entregar paquetes"
            )

        result = await PackageStateService.deliver_package_with_payment(
            db=db,
            package_id=package_id,
            request=request
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al entregar paquete: {str(e)}"
        )


@router.post("/{package_id}/cancel", response_model=PackageCancelResponse)
async def cancel_package_with_reason(
    package_id: str,  # Changed to str to handle announcement IDs
    request: PackageCancelRequest,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Cancelar paquete o anuncio con razón específica"""
    try:
        # Verificar permisos (solo operadores y admin)
        if current_user.role.value not in ["ADMIN", "OPERADOR"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para cancelar paquetes"
            )

        # Check if this is an announcement ID
        if package_id.startswith('announcement_'):
            tracking_code = package_id.replace('announcement_', '')
            
            # Cancel the announcement instead of a package
            from sqlalchemy import text
            from app.utils.datetime_utils import get_colombia_now
            from app.models.announcement_new import PackageAnnouncementNew
            
            # Find the announcement (must not be processed, but can be cancelled)
            announcement = db.query(PackageAnnouncementNew).filter(
                PackageAnnouncementNew.tracking_code == tracking_code,
                PackageAnnouncementNew.is_processed == False
            ).first()
            
            # Si ya está cancelado, permitir cancelarlo de nuevo o informar que ya está cancelado
            if announcement and not announcement.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El anuncio ya está cancelado"
                )
            
            if not announcement:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Anuncio no encontrado o ya procesado"
                )
            
            # Mark announcement as inactive (cancelled)
            announcement.is_active = False
            announcement.updated_at = get_colombia_now()
            db.commit()
            db.refresh(announcement)
            
            # Return a response compatible with PackageCancelResponse
            return PackageCancelResponse(
                success=True,
                package_id=0,  # No package_id for announcements
                tracking_number=announcement.tracking_code,
                cancelled_at=get_colombia_now(),
                reason=request.reason,
                refund_amount=request.refund_amount,
                message=f"Anuncio {announcement.tracking_code} cancelado exitosamente"
            )
        
        # If it's a regular package ID, parse it as int
        try:
            package_id_int = int(package_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"ID de paquete inválido: {package_id}"
            )

        result = await PackageStateService.cancel_package_with_reason(
            db=db,
            package_id=package_id_int,
            request=request
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cancelar paquete: {str(e)}"
        )


@router.post("/receive-with-images")
async def receive_package_with_images(
    announcement_id: str = Form(...),
    package_type: str = Form(...),
    package_condition: str = Form(...),
    observations: str = Form(""),
    images: List[UploadFile] = File(None),
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Recibir paquete desde anuncio con subida de imágenes a S3"""
    try:
        # Verificar que el announcement_id tenga el prefijo correcto
        if not announcement_id.startswith('announcement_'):
            raise HTTPException(status_code=400, detail="ID de anuncio inválido")

        tracking_code = announcement_id.replace('announcement_', '')

        # Verificar que el anuncio existe y no está procesado
        from sqlalchemy import text
        announcement_query = text("""
            SELECT customer_name, customer_phone, guide_number, tracking_code, id
            FROM package_announcements_new
            WHERE tracking_code = :tracking_code AND is_processed = false
        """)
        result = db.execute(announcement_query, {"tracking_code": tracking_code})
        announcement = result.fetchone()

        if not announcement:
            raise HTTPException(status_code=404, detail="Anuncio no encontrado o ya procesado")

        # Crear el paquete directamente desde los datos del anuncio (sin validaciones Pydantic)
        customer_name = announcement[0]
        customer_phone = announcement[1]
        guide_number = announcement[2]

        # Convertir strings a enums con mapeo de valores
        # Mapeo de valores del frontend a valores del enum
        package_type_map = {
            'NORMAL': 'NORMAL',
            'EXTRA_DIMENSIONED': 'EXTRA_DIMENSIONADO',  # Inglés → Español
            'EXTRA_DIMENSIONADO': 'EXTRA_DIMENSIONADO'  # Ya en español
        }
        
        package_condition_map = {
            'OK': 'BUENO',           # Inglés → Español
            'BUENO': 'BUENO',        # Ya en español
            'REGULAR': 'REGULAR',    # Igual en ambos
            'OPENED': 'ABIERTO',     # Inglés → Español
            'ABIERTO': 'ABIERTO'     # Ya en español
        }
        
        try:
            # Normalizar y mapear valores
            package_type_normalized = package_type_map.get(package_type.upper())
            package_condition_normalized = package_condition_map.get(package_condition.upper())
            
            if not package_type_normalized:
                raise HTTPException(status_code=400, detail=f"Valor inválido para tipo de paquete: '{package_type}'. Valores permitidos: NORMAL, EXTRA_DIMENSIONED")
            
            if not package_condition_normalized:
                raise HTTPException(status_code=400, detail=f"Valor inválido para condición: '{package_condition}'. Valores permitidos: OK, REGULAR, OPENED")
            
            package_type_enum = PackageType[package_type_normalized]
            package_condition_enum = PackageCondition[package_condition_normalized]
        except KeyError as e:
            raise HTTPException(status_code=400, detail=f"Valor inválido para tipo o condición: {str(e)}")

        # Crear solicitud de recepción usando PackageStateService (genera BAROTI automáticamente)
        from app.schemas.package import PackageReceiveRequest
        receive_request = PackageReceiveRequest(
            announcement_id=tracking_code,
            package_type=package_type_enum,
            package_condition=package_condition_enum,
            baroti=None,  # Se genera automáticamente (el schema usa 'baroti', no 'posicion')
            observations=observations,
            operator_id=current_user.id
        )

        # Procesar recepción usando el servicio que genera BAROTI
        result = PackageStateService.receive_package_from_announcement(
            db=db,
            request=receive_request
        )
        
        # Obtener el paquete creado
        db_package = db.query(Package).filter(Package.id == result.package_id).first()
        
        # NOTA: Campo 'observations' eliminado del modelo Package
        # Las observaciones ahora deben gestionarse mediante el modelo Message
        # if observations.strip():
        #     db_package.observations = observations.strip()
        #     db.commit()

        # Procesar imágenes si existen (método tradicional)
        uploaded_images = []
        if images and len(images) > 0:
            s3_service = S3Service()

            for i, image_file in enumerate(images[:3]):  # Máximo 3 imágenes
                if not image_file.filename:
                    continue

                # Leer contenido del archivo
                image_content = await image_file.read()

                # Generar nombre único para S3 con estructura dinámica basada en fecha
                import uuid
                from datetime import datetime
                
                # Detectar tipo MIME y extensión correcta
                content_type = image_file.content_type or 'image/jpeg'
                if content_type == 'image/webp':
                    file_extension = 'webp'
                elif content_type == 'image/jpeg':
                    file_extension = 'jpg'
                elif content_type == 'image/png':
                    file_extension = 'png'
                else:
                    # Fallback: usar extensión del filename o jpg por defecto
                    file_extension = image_file.filename.split('.')[-1].lower() if '.' in image_file.filename else 'jpg'
                
                # Generar estructura dinámica basada en fecha (igual que el frontend)
                now = datetime.now()
                year = now.year
                month = now.month
                day = now.day
                
                # Generar nombre de archivo con timestamp
                timestamp_str = now.strftime("%Y%m%d_%H%M%S")
                filename = f"{tracking_code}_{timestamp_str}_{i+1:03d}.{file_extension}"
                
                # Estructura dinámica: YYYY/MM/DD/packages/announcement_{tracking_code}/receive/
                s3_key = f"{year}/{month:02d}/{day:02d}/packages/announcement_{tracking_code}/receive/{filename}"

                # Subir a S3
                s3_url = None
                s3_key_final = None
                try:
                    s3_url = s3_service.upload_file(image_content, s3_key, content_type)
                    s3_key_final = s3_key  # Solo asignar si upload fue exitoso
                    print(f"✅ Imagen {i+1} subida exitosamente a S3: {s3_url}")
                    print(f"   📊 Formato: {content_type} | Extensión: {file_extension}")
                except Exception as s3_error:
                    print(f"❌ Error subiendo imagen {i+1} a S3: {str(s3_error)}")
                    # No guardar en base de datos si S3 falla
                    continue

                # Solo guardar en base de datos si S3 fue exitoso
                if s3_url and s3_key_final:
                    try:
                        file_upload = FileUpload(
                            package_id=db_package.id,
                            filename=image_file.filename,
                            s3_key=s3_key_final,
                            s3_url=s3_url,
                            file_type=FileType.IMAGEN,
                            file_size=len(image_content),
                            content_type=f"image/{file_extension}"
                        )

                        db.add(file_upload)
                        uploaded_images.append({
                            "filename": image_file.filename,
                            "s3_key": s3_key_final,
                            "s3_url": s3_url
                        })
                        print(f"✅ Archivo {image_file.filename} guardado en base de datos")
                    except Exception as db_error:
                        print(f"❌ Error guardando archivo en base de datos: {str(db_error)}")
                        # Continuar con el siguiente archivo
                        continue

            # Hacer commit de las imágenes después de agregarlas a la sesión
            if uploaded_images:
                db.commit()
                print(f"✅ {len(uploaded_images)} imágenes guardadas en BD")

        # NUEVO: Registrar imágenes que ya están en S3 (flujo frontend actual)
        if not uploaded_images:  # Solo si no se procesaron imágenes por el método tradicional
            try:
                s3_service = S3Service()
                from datetime import datetime
                
                # Generar la ruta base donde deberían estar las imágenes
                now = datetime.now()
                year = now.year
                month = now.month
                day = now.day
                s3_base_path = f"{year}/{month:02d}/{day:02d}/packages/announcement_{tracking_code}/receive/"
                
                print(f"🔍 Buscando imágenes en S3: {s3_base_path}")
                
                # Listar objetos en S3 que coincidan con el patrón
                response = s3_service.s3_client.list_objects_v2(
                    Bucket=s3_service.bucket_name,
                    Prefix=s3_base_path
                )
                
                if 'Contents' in response:
                    s3_images = []
                    for obj in response['Contents']:
                        s3_key = obj['Key']
                        # Solo procesar archivos de imagen (no metadata.json)
                        if s3_key.endswith(('.jpg', '.jpeg', '.png', '.webp')) and tracking_code in s3_key:
                            s3_images.append({
                                'key': s3_key,
                                'size': obj['Size'],
                                'last_modified': obj['LastModified']
                            })
                    
                    print(f"📷 Encontradas {len(s3_images)} imágenes en S3")
                    
                    # Registrar cada imagen en la base de datos
                    for s3_img in s3_images:
                        try:
                            # Generar URL de S3
                            s3_url = f"https://{s3_service.bucket_name}.s3.amazonaws.com/{s3_img['key']}"
                            
                            # Extraer filename del s3_key
                            filename = s3_img['key'].split('/')[-1]
                            
                            # Detectar content_type basado en extensión
                            if filename.endswith('.webp'):
                                content_type = 'image/webp'
                            elif filename.endswith('.png'):
                                content_type = 'image/png'
                            else:
                                content_type = 'image/jpeg'
                            
                            # Crear registro en file_uploads
                            file_upload = FileUpload(
                                package_id=db_package.id,
                                filename=filename,
                                s3_key=s3_img['key'],
                                s3_url=s3_url,
                                file_type=FileType.IMAGEN,
                                file_size=s3_img['size'],
                                content_type=content_type
                            )
                            
                            db.add(file_upload)
                            uploaded_images.append({
                                "filename": filename,
                                "s3_key": s3_img['key'],
                                "s3_url": s3_url
                            })
                            
                            print(f"✅ Imagen registrada en BD: {filename}")
                            
                        except Exception as img_error:
                            print(f"❌ Error registrando imagen {s3_img['key']}: {str(img_error)}")
                            continue
                    
                    # Commit de las imágenes registradas
                    if uploaded_images:
                        db.commit()
                        print(f"✅ {len(uploaded_images)} imágenes de S3 registradas en BD")
                else:
                    print("📷 No se encontraron imágenes en S3")
                    
            except Exception as s3_error:
                print(f"⚠️  Error buscando imágenes en S3: {str(s3_error)}")
                # No fallar el proceso por esto

        # El anuncio ya fue marcado como procesado por PackageStateService
        # No es necesario hacerlo nuevamente

        return {
            "success": True,
            "message": "Paquete recibido exitosamente",
            "baroti": db_package.posicion,  # Incluir número de posición generado
            "package": {
                "id": db_package.id,
                "tracking_number": db_package.tracking_number,
                "customer_name": announcement[0],
                "customer_phone": announcement[1],
                "package_type": package_type,
                "package_condition": package_condition,
                "status": "received",
                "received_at": db_package.received_at.isoformat() if db_package.received_at else None,
                "baroti": db_package.posicion,  # También incluir en package
                "images_uploaded": len(uploaded_images),
                "images": uploaded_images
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error en recepción de paquete: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al recibir paquete: {str(e)}"
        )


@router.get("/{package_id}/fees", response_model=PackageFeeCalculation)
async def calculate_package_fees(
    package_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Calcular tarifas finales de un paquete"""
    try:
        # Verificar permisos (solo operadores y admin)
        if current_user.role.value not in ["ADMIN", "OPERADOR"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para calcular tarifas"
            )

        # Obtener paquete
        package = db.query(Package).filter(Package.id == package_id).first()
        if not package:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paquete no encontrado")

        # Calcular tarifas
        fee_calculation = PackageStateService.calculate_final_fees(db=db, package=package)

        return fee_calculation

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular tarifas: {str(e)}"
        )


@router.put("/{package_id}/recalculate-fees", response_model=PackageResponse)
async def recalculate_package_fees(
    package_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Recalcular y actualizar tarifas de un paquete existente"""
    try:
        # Verificar permisos (solo admin)
        if current_user.role.value != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los administradores pueden recalcular tarifas"
            )

        # Obtener paquete
        package = db.query(Package).filter(Package.id == package_id).first()
        if not package:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paquete no encontrado")

        # Recalcular tarifas
        package_service = PackageService()
        updated_package = package_service.recalculate_package_fees(db=db, package=package)

        return PackageResponse.model_validate(updated_package)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al recalcular tarifas: {str(e)}"
        )


@router.post("/fix-all-fees")
async def fix_all_packages_fees(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Corregir tarifas de todos los paquetes que tengan valores incorrectos"""
    try:
        # Verificar permisos (solo admin)
        if current_user.role.value != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los administradores pueden corregir tarifas"
            )

        # Corregir todas las tarifas
        package_service = PackageService()
        fixed_count = package_service.fix_all_packages_fees(db=db)

        return {
            "message": f"Se corrigieron {fixed_count} paquetes",
            "fixed_count": fixed_count,
            "status": "success"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al corregir tarifas: {str(e)}"
        )


@router.get("/rates/dynamic")
async def get_dynamic_rates():
    """Obtener tarifas dinámicas desde .env"""
    try:
        from app.config import settings
        
        rates = {
            "normal": int(settings.base_delivery_rate_normal),
            "extra_dimensioned": int(settings.base_delivery_rate_extra_dimensioned),
            "storage_per_day": int(settings.base_storage_rate),
            "currency": settings.currency
        }
        
        return {
            "success": True,
            "rates": rates,
            "message": "Tarifas obtenidas dinámicamente desde .env"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tarifas dinámicas: {str(e)}"
        )


@router.post("/calculate-dynamic-fee")
async def calculate_dynamic_fee(
    request: dict,
    db: Session = Depends(get_db)
):
    """Calcular tarifa dinámicamente desde CODE/LOCAL/.env"""
    try:
        from app.utils.dynamic_fee_calculator import DynamicFeeCalculator
        from app.models.package import PackageType
        
        # Extraer parámetros del request
        package_type = request.get('package_type', 'normal')
        storage_days = request.get('storage_days', 0)
        
        # Convertir string a enum
        try:
            package_type_enum = PackageType(package_type.upper())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de paquete inválido: {package_type}"
            )
        
        # Calcular tarifa
        fee_calculation = DynamicFeeCalculator.calculate_total_fee(
            package_type_enum, 
            storage_days
        )
        
        return {
            "success": True,
            "calculation": fee_calculation,
            "message": "Tarifa calculada dinámicamente desde CODE/LOCAL/.env"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular tarifa dinámica: {str(e)}"
        )


# ========================================
# ENDPOINTS DE ELIMINACIÓN
# ========================================

@router.delete("/guide/{tracking_code}")
async def delete_guide_by_tracking_code(
    tracking_code: str,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Eliminar una guía y todas sus referencias relacionadas (solo ADMIN)"""
    try:
        # Verificar permisos - solo ADMIN puede eliminar guías
        if current_user.role.value != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los administradores pueden eliminar guías"
            )

        package_service = PackageService()
        result = package_service.delete_guide_by_tracking_code(
            db=db,
            tracking_code=tracking_code,
            deleted_by=f"admin_{current_user.id}"
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar guía: {str(e)}"
        )


@router.delete("/package/{package_id}")
async def delete_package_by_id(
    package_id: int,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Eliminar un paquete y todas sus referencias relacionadas (solo ADMIN)"""
    try:
        # Verificar permisos - solo ADMIN puede eliminar paquetes
        if current_user.role.value != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los administradores pueden eliminar paquetes"
            )

        package_service = PackageService()
        result = package_service.delete_package_by_id(
            db=db,
            package_id=package_id,
            deleted_by=f"admin_{current_user.id}"
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar paquete: {str(e)}"
        )


@router.get("/with-email")
async def list_packages_with_email(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    Listar paquetes donde el cliente tiene email registrado
    
    Retorna todos los paquetes del sistema donde el cliente asociado
    tiene una dirección de correo electrónico registrada.
    """
    from sqlalchemy import text
    
    query = """
        SELECT
            p.id,
            p.tracking_number,
            p.guide_number,
            p.package_type,
            p.status,
            p.package_condition,
            p.posicion,
            p.announced_at,
            p.received_at,
            p.delivered_at,
            p.cancelled_at,
            p.base_fee,
            p.storage_fee,
            p.total_amount,
            p.created_at,
            p.updated_at,
            c.id as customer_id,
            c.full_name as customer_name,
            c.phone as customer_phone,
            c.email as customer_email,
            c.tower as customer_tower,
            c.apartment as customer_apartment,
            c.address as customer_address
        FROM packages p
        INNER JOIN customers c ON p.customer_id = c.id
        WHERE c.email IS NOT NULL AND c.email != ''
        ORDER BY p.created_at DESC
        LIMIT :limit OFFSET :skip
    """
    
    result = db.execute(text(query), {"limit": limit, "skip": skip})
    rows = result.fetchall()
    
    # Contar total
    count_query = """
        SELECT COUNT(*)
        FROM packages p
        INNER JOIN customers c ON p.customer_id = c.id
        WHERE c.email IS NOT NULL AND c.email != ''
    """
    total_result = db.execute(text(count_query))
    total = total_result.scalar()
    
    packages = []
    for row in rows:
        packages.append({
            "id": str(row[0]),
            "tracking_number": row[1],
            "guide_number": row[2],
            "package_type": row[3].value if row[3] else None,
            "status": row[4].value if row[4] else None,
            "package_condition": row[5].value if row[5] else None,
            "baroti": row[6],
            "announced_at": row[7].isoformat() if row[7] else None,
            "received_at": row[8].isoformat() if row[8] else None,
            "delivered_at": row[9].isoformat() if row[9] else None,
            "cancelled_at": row[10].isoformat() if row[10] else None,
            "base_fee": float(row[11]) if row[11] else 0,
            "storage_fee": float(row[12]) if row[12] else 0,
            "total_amount": float(row[13]) if row[13] else 0,
            "created_at": row[14].isoformat() if row[14] else None,
            "updated_at": row[15].isoformat() if row[15] else None,
            "customer": {
                "id": str(row[16]) if row[16] else None,
                "full_name": row[17],
                "phone": row[18],
                "email": row[19],
                "tower": row[20],
                "apartment": row[21],
                "address": row[22]
            }
        })
    
    return {
        "success": True,
        "total": total,
        "count": len(packages),
        "packages": packages,
        "pagination": {
            "skip": skip,
            "limit": limit,
            "has_more": (skip + limit) < total
        }
    }


@router.post("/{package_id}/send-email")
async def send_package_email_notification(
    package_id: str,
    event_type: str = Query(..., description="Tipo de evento: received, delivered, cancelled"),
    db: Session = Depends(get_db)
):
    """
    Enviar email de notificación manual para un paquete
    
    Solo envía email si el cliente tiene email registrado.
    El email debe estar asociado al mismo cliente que tiene el teléfono.
    """
    try:
        # Convertir package_id a int
        package_id_int = int(package_id)
        
        # Obtener el paquete
        package_service = PackageService()
        package = package_service.get_by_id(db, package_id_int)
        
        if not package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paquete con ID {package_id} no encontrado"
            )
        
        # Verificar que el paquete tiene cliente asociado
        if not package.customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El paquete no tiene un cliente asociado"
            )
        
        # Verificar que el cliente tiene email registrado
        if not package.customer or not package.customer.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El cliente no tiene una dirección de correo electrónico registrada. No se puede enviar el email."
            )
        
        # Mapear event_type a NotificationEvent
        event_mapping = {
            "received": NotificationEvent.PACKAGE_RECEIVED,
            "delivered": NotificationEvent.PACKAGE_DELIVERED,
            "cancelled": NotificationEvent.PACKAGE_CANCELLED
        }
        
        notification_event = event_mapping.get(event_type.lower())
        if not notification_event:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de evento inválido: {event_type}. Debe ser: received, delivered, o cancelled"
            )
        
        # Verificar que el estado del paquete coincide con el evento
        status_mapping = {
            NotificationEvent.PACKAGE_RECEIVED: PackageStatus.RECIBIDO,
            NotificationEvent.PACKAGE_DELIVERED: PackageStatus.ENTREGADO,
            NotificationEvent.PACKAGE_CANCELLED: PackageStatus.CANCELADO
        }
        
        expected_status = status_mapping.get(notification_event)
        if package.status != expected_status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El paquete está en estado {package.status.value}, no puede enviarse email para evento {event_type}"
            )
        
        # Preparar variables para el template
        variables = {
            "guide_number": package.tracking_number,
            "tracking_code": getattr(package, 'tracking_code', package.tracking_number),
            "customer_name": package.customer.full_name if package.customer else "Cliente",
            "package_type": package.package_type.value if package.package_type else "normal",
            "tracking_url": f"{settings.tracking_base_url}/{package.tracking_number}"
        }
        
        # Agregar timestamps según el estado
        if notification_event == NotificationEvent.PACKAGE_RECEIVED and package.received_at:
            variables["received_at"] = package.received_at.strftime("%d/%m/%Y %H:%M")
        elif notification_event == NotificationEvent.PACKAGE_DELIVERED and package.delivered_at:
            variables["delivered_at"] = package.delivered_at.strftime("%d/%m/%Y %H:%M")
            variables["recipient_name"] = getattr(package, 'delivered_to', 'Cliente')
        elif notification_event == NotificationEvent.PACKAGE_CANCELLED:
            from app.utils.datetime_utils import get_colombia_now
            variables["cancelled_at"] = get_colombia_now().strftime("%d/%m/%Y %H:%M")
        
        # Enviar email usando EmailService
        email_service = EmailService()
        
        result = await email_service.send_email_by_event(
            db=db,
            event_type=notification_event,
            recipient=package.customer.email,
            variables=variables,
            package_id=package.id,
            customer_id=str(package.customer_id) if package.customer_id else None,
            priority=NotificationPriority.MEDIA,
            is_test=False
        )
        
        if result.get("success"):
            return {
                "success": True,
                "message": f"Email enviado exitosamente a {package.customer.email}",
                "notification_id": result.get("notification_id"),
                "recipient_email": package.customer.email,
                "customer_phone": package.customer.phone,  # Confirmar que email está asociado a este teléfono
                "event_type": event_type
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al enviar email: {result.get('error', 'Error desconocido')}"
            )
            
    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ID de paquete inválido: {package_id}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al enviar email de notificación: {str(e)}"
        )


@router.delete("/tracking/{tracking_number}")
async def delete_package_by_tracking(
    tracking_number: str,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Eliminar un paquete por número de tracking (solo ADMIN)"""
    try:
        # Verificar permisos - solo ADMIN puede eliminar paquetes
        if current_user.role.value != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los administradores pueden eliminar paquetes"
            )

        package_service = PackageService()
        result = package_service.delete_package_by_tracking_number(
            db=db,
            tracking_number=tracking_number,
            deleted_by=f"admin_{current_user.id}"
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar paquete: {str(e)}"
        )