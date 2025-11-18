from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session, joinedload
import uuid
import logging
from app.database import get_db
from app.models import User, Package, PackageAnnouncementNew
from app.models.file_upload import FileUpload, FileType
from app.models.package_history import PackageHistory
from app.utils.auth import get_password_hash
from app.dependencies import get_current_active_user_from_cookies
# from app.utils.auth_context import get_auth_context_from_request  # Módulo no existe
from app.services.package_state_service import PackageStateService
from sqlalchemy import or_

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def api_root():
    """Endpoint raíz de la API"""
    return {
        "success": True,
        "message": "API de PAQUETES EL CLUB v1.0",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/auth/",
            "packages": "/api/packages/",
            "announcements": "/api/announcements/",
            "search": "/api/search",
            "health": "/api/health",
            "docs": "/docs"
        }
    }

@router.post("/auth/set-cookies")
async def set_auth_cookies(request: Request):
    """Endpoint temporal para establecer cookies de autenticación - Solo para desarrollo"""
    try:
        body = await request.json()
        username = body.get("username", "jesus")
        
        response = JSONResponse({
            "success": True,
            "message": "Cookies establecidas",
            "user": {
                "username": username,
                "first_name": username.title(),
                "last_name": "Usuario"
            }
        })
        
        response.set_cookie("access_token", "fake_token_for_development", max_age=86400)  # 24 horas = 86400 segundos
        response.set_cookie("user_id", "1", max_age=86400)
        response.set_cookie("user_name", username, max_age=86400)
        response.set_cookie("user_role", "admin", max_age=86400)
        
        return response
            
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Error al establecer cookies: {str(e)}"
        }, status_code=500)

@router.get("/auth/check")
async def check_auth(request: Request):
    """Verificar estado de autenticación desde frontend"""
    access_token = request.cookies.get("access_token")
    user_name = request.cookies.get("user_name")
    
    if access_token and user_name:
        return {
            "is_authenticated": True,
            "user_name": user_name
        }
    else:
        return {
            "is_authenticated": False,
            "user_name": None
        }

@router.get("/admin/users/search")
async def search_users(
    request: Request,
    q: str = None,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """API endpoint para búsqueda de usuarios - Solo para administradores"""
    if current_user.role.value != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo los administradores pueden acceder a esta función."
        )
    
    if not q or q.strip() == "":
        users = db.query(User).order_by(User.created_at.desc()).all()
    else:
        search_term = f"%{q.strip()}%"
        users = db.query(User).filter(
            or_(
                User.email.ilike(search_term),
                User.phone.ilike(search_term),
                User.role.ilike(search_term),
                User.full_name.ilike(search_term),
                User.username.ilike(search_term),
                User.is_active == (q.strip().lower() in ['activo', 'active', 'true', '1']),
                User.is_active == (q.strip().lower() in ['inactivo', 'inactive', 'false', '0'])
            )
        ).order_by(User.created_at.desc()).all()
    
    users_data = [
        {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
            "role": user.role.value if user.role else None,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        for user in users
    ]
    
    return {
        "users": users_data,
        "total": len(users_data),
        "search_term": q
    }

@router.post("/admin/users/create")
async def create_user(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Crear un nuevo usuario - Solo para administradores (Endpoint legacy - delega a AdminService)"""
    if current_user.role.value != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo administradores pueden crear usuarios."
        )
    
    try:
        from app.services.admin_service import AdminService
        
        data = await request.json()
        
        # Validar datos requeridos
        required_fields = ["username", "email", "full_name", "role"]
        for field in required_fields:
            if field not in data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Campo requerido: {field}"
                )
        
        # Validar rol
        if data["role"] not in ["ADMIN", "OPERADOR", "USUARIO"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rol inválido. Solo se permiten roles 'OPERADOR', 'USUARIO' o 'ADMIN'"
            )
        
        # Si el rol requiere contraseña, validarla
        if data["role"] in ["OPERADOR", "ADMIN"]:
            if "password" not in data or not data["password"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La contraseña es requerida para roles OPERADOR y ADMIN"
                )
        
        # Usar AdminService para crear el usuario
        service = AdminService(db)
        user = service.create_user(data, created_by_user_id=current_user.id)
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "success": True,
                "message": "Usuario creado exitosamente",
                "user_id": str(user.id),
                "username": user.username
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear usuario: {str(e)}"
        )

@router.post("/admin/users/update")
async def update_user(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Actualizar un usuario existente - Solo para administradores (Endpoint legacy - delega a AdminService)"""
    if current_user.role.value != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo administradores pueden actualizar usuarios."
        )
    
    try:
        from app.services.admin_service import AdminService
        import logging
        logger = logging.getLogger(__name__)
        
        data = await request.json()
        user_id_str = data.get("user_id")
        
        # Logging para debug
        logger.info(f"Update user request - user_id_str: {user_id_str}, type: {type(user_id_str)}, data keys: {list(data.keys())}")
        
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de usuario requerido"
            )
        
        # Convertir a string si no lo es y limpiar
        if not isinstance(user_id_str, str):
            user_id_str = str(user_id_str)
        user_id_str = user_id_str.strip()
        
        # El modelo User usa Integer, no UUID
        try:
            user_id = int(user_id_str)
            if user_id <= 0:
                raise ValueError("ID debe ser un número positivo")
        except (ValueError, TypeError) as e:
            logger.error(f"Error converting user_id to Integer: {user_id_str}, error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"ID de usuario inválido: {user_id_str}. Error: {str(e)}"
            )
        
        # Preparar datos para AdminService
        update_data = {
            "username": data.get("username"),
            "email": data.get("email"),
            "full_name": data.get("full_name"),
            "phone": data.get("phone"),
            "role": data.get("role"),
            "is_active": data.get("is_active", True)
        }
        
        # Validar rol si se proporciona
        if "role" in update_data and update_data["role"] not in ["OPERADOR", "USUARIO", "ADMIN"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rol inválido. Solo se permiten roles 'OPERADOR', 'USUARIO' o 'ADMIN'"
            )
        
        # Usar AdminService para actualizar el usuario
        service = AdminService(db)
        user = service.update_user(user_id, update_data, updated_by_user_id=current_user.id)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": "Usuario actualizado exitosamente",
                "user_id": str(user.id),
                "username": user.username
            }
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar usuario: {str(e)}"
        )

@router.post("/profile/update")
async def update_current_user_profile(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Actualizar perfil del usuario actual"""
    try:
        data = await request.json()
        
        username = data.get("username", "").strip()
        email = data.get("email", "").strip()
        full_name = data.get("full_name", "").strip()
        phone = data.get("phone", "").strip() or None
        
        if not all([username, email, full_name]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Los campos username, email y full_name son obligatorios"
            )
        
        if username.lower() != current_user.username:
            existing = db.query(User).filter(
                (User.username == username.lower()) & (User.id != current_user.id)
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El nombre de usuario '{username}' ya existe"
                )
        
        if email.lower() != current_user.email:
            existing = db.query(User).filter(
                (User.email == email.lower()) & (User.id != current_user.id)
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El email '{email}' ya está registrado"
                )
        
        current_user.username = username.lower()
        current_user.email = email.lower()
        current_user.full_name = full_name
        current_user.phone = phone
        
        from ..utils.datetime_utils import get_colombia_now
        current_user.updated_at = get_colombia_now()
        
        db.commit()
        db.refresh(current_user)
        
        return {
            "message": "Perfil actualizado exitosamente",
            "user": {
                "id": str(current_user.id),
                "username": current_user.username,
                "email": current_user.email,
                "full_name": current_user.full_name,
                "phone": current_user.phone
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar perfil: {str(e)}"
        )

@router.post("/admin/users/delete")
async def delete_user(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Eliminar un usuario - Solo para administradores (Endpoint legacy - delega a AdminService)"""
    if current_user.role.value != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo administradores pueden eliminar usuarios."
        )
    
    try:
        from app.services.admin_service import AdminService
        
        data = await request.json()
        user_id_str = data.get("user_id")
        
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de usuario requerido"
            )
        
        # Convertir a string si no lo es y limpiar
        if not isinstance(user_id_str, str):
            user_id_str = str(user_id_str)
        user_id_str = user_id_str.strip()
        
        # El modelo User usa Integer, no UUID
        try:
            user_id = int(user_id_str)
            if user_id <= 0:
                raise ValueError("ID debe ser un número positivo")
        except (ValueError, TypeError) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"ID de usuario inválido: {user_id_str}"
            )
        
        # Verificar que no se elimine a sí mismo
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes eliminar tu propio usuario"
            )
        
        # Usar AdminService para eliminar el usuario
        service = AdminService(db)
        service.delete_user(user_id, deleted_by_user_id=current_user.id)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": "Usuario eliminado exitosamente"
            }
        )
        
    except HTTPException as e:
        # Asegurar que HTTPException devuelva JSONResponse con formato consistente
        return JSONResponse(
            status_code=e.status_code,
            content={
                "success": False,
                "detail": e.detail,
                "message": e.detail
            }
        )
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "success": False,
                "detail": str(e),
                "message": str(e)
            }
        )
    except Exception as e:
        db.rollback()
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error al eliminar usuario: {e}", exc_info=True)
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "detail": f"Error al eliminar usuario: {str(e)}",
                "message": f"Error al eliminar usuario: {str(e)}"
            }
        )

@router.post("/admin/users/toggle-status")
async def toggle_user_status(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Activar/Desactivar un usuario - Solo para administradores (Endpoint legacy - delega a AdminService)"""
    if current_user.role.value != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo administradores pueden cambiar el estado de usuarios."
        )
    
    try:
        from app.services.admin_service import AdminService
        
        data = await request.json()
        user_id_str = data.get("user_id")
        
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de usuario requerido"
            )
        
        # Convertir a string si no lo es y limpiar
        if not isinstance(user_id_str, str):
            user_id_str = str(user_id_str)
        user_id_str = user_id_str.strip()
        
        # El modelo User usa Integer, no UUID
        try:
            user_id = int(user_id_str)
            if user_id <= 0:
                raise ValueError("ID debe ser un número positivo")
        except (ValueError, TypeError) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"ID de usuario inválido: {user_id_str}"
            )
        
        # Verificar que no se desactive a sí mismo
        user_to_check = db.query(User).filter(User.id == user_id).first()
        if user_to_check and user_to_check.id == current_user.id and not user_to_check.is_active:
            # Si está intentando desactivarse a sí mismo, prevenir
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes desactivar tu propio usuario"
            )
        
        # Usar AdminService para toggle del estado
        service = AdminService(db)
        user = service.toggle_user_status(user_id, changed_by_user_id=current_user.id)
        
        status_text = "activado" if user.is_active else "desactivado"
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": f"Usuario {status_text} exitosamente",
                "user_id": str(user.id),
                "is_active": user.is_active
            }
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cambiar estado del usuario: {str(e)}"
        )

@router.post("/admin/users/reset-password")
async def reset_user_password(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Restablecer contraseña de un usuario - Solo para administradores (Endpoint legacy - delega a AdminService)"""
    if current_user.role.value != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo administradores pueden restablecer contraseñas."
        )
    
    try:
        from app.services.admin_service import AdminService
        import secrets
        import string
        
        data = await request.json()
        user_id_str = data.get("user_id")
        
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de usuario requerido"
            )
        
        # Convertir a string si no lo es y limpiar
        if not isinstance(user_id_str, str):
            user_id_str = str(user_id_str)
        user_id_str = user_id_str.strip()
        
        # El modelo User usa Integer, no UUID
        try:
            user_id = int(user_id_str)
            if user_id <= 0:
                raise ValueError("ID debe ser un número positivo")
        except (ValueError, TypeError) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"ID de usuario inválido: {user_id_str}"
            )
        
        # Verificar que el usuario existe y tiene un rol válido para reset
        user_to_reset = db.query(User).filter(User.id == user_id).first()
        if not user_to_reset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        if user_to_reset.role.value not in ["ADMIN", "OPERADOR"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden restablecer contraseñas de usuarios con rol Administrador u Operador"
            )
        
        # Generar nueva contraseña
        new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        
        # Usar AdminService para resetear la contraseña
        service = AdminService(db)
        service.reset_user_password(user_id, new_password, reset_by_user_id=current_user.id)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": "Contraseña restablecida exitosamente",
                "new_password": new_password
            }
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al restablecer contraseña: {str(e)}"
        )

@router.post("/announcements/")
async def create_announcement_direct(request: Request, db: Session = Depends(get_db)):
    """Crear un nuevo anuncio de paquete - Endpoint directo"""
    try:
        body = await request.json()
        customer_name = body.get("customer_name", "").strip().upper()
        customer_phone = body.get("customer_phone", "").strip()
        guide_number = body.get("guide_number", "").strip().upper()
        
        if not customer_name:
            return JSONResponse(
                status_code=400,
                content={"detail": "El nombre del cliente es requerido"}
            )
        
        if not customer_phone:
            return JSONResponse(
                status_code=400,
                content={"detail": "El teléfono del cliente es requerido"}
            )
        
        # Normalizar y validar teléfono
        from app.utils.phone_utils import normalize_phone, validate_phone
        customer_phone = normalize_phone(customer_phone)
        if not validate_phone(customer_phone):
            return JSONResponse(
                status_code=400,
                content={"detail": "Número de teléfono inválido. Use formato: +573001234567 o 3001234567"}
            )
        
        if not guide_number:
            return JSONResponse(
                status_code=400,
                content={"detail": "El número de guía es requerido"}
            )
        
        # Generar código de tracking único
        # Excluye el número 0 y la letra O para evitar confusión
        import string
        import random
        allowed_chars = string.ascii_uppercase.replace('O', '') + string.digits.replace('0', '')
        tracking_code = ''.join(random.choice(allowed_chars) for _ in range(4))
        
        from ..utils.datetime_utils import get_colombia_now
        
        existing_announcement = db.query(PackageAnnouncementNew).filter(
            PackageAnnouncementNew.guide_number == guide_number
        ).first()
        
        if existing_announcement:
            return JSONResponse(
                status_code=409,
                content={"detail": f"Ya existe un anuncio con el número de guía: {guide_number}"}
            )
        
        # ========================================
        # BUSCAR O CREAR CLIENTE AUTOMÁTICAMENTE
        # ========================================
        customer_id = None
        try:
            from app.services.customer_service import CustomerService
            from app.schemas.customer import CustomerCreate
            
            customer_service = CustomerService()
            
            # Buscar cliente existente por teléfono
            existing_customer = customer_service.get_customer_by_phone(db, customer_phone)
            
            if existing_customer:
                # Cliente ya existe, usar su ID
                customer_id = existing_customer.id
                print(f"✅ Cliente existente encontrado: {existing_customer.id} - {existing_customer.full_name}")
            else:
                # Cliente nuevo, crear con datos mínimos (nombre + teléfono)
                # Separar nombre y apellido del customer_name con valores por defecto válidos
                name_parts = [part.strip() for part in customer_name.split() if part.strip()]
                first_name = name_parts[0] if name_parts else (customer_name.strip() or "CLIENTE")
                last_name = (
                    name_parts[1]
                    if len(name_parts) > 1
                    else (name_parts[0] if name_parts else "PENDIENTE")
                )

                # Respetar longitudes máximas del esquema
                first_name = first_name[:50]
                last_name = last_name[:50] or "PENDIENTE"
                
                customer_data = CustomerCreate(
                    first_name=first_name,
                    last_name=last_name,
                    phone=customer_phone,
                    # email, address, etc. quedan None hasta que se completen
                )
                
                new_customer = customer_service.create_customer(db, customer_data)
                customer_id = new_customer.id
                print(f"✅ Cliente nuevo creado: {new_customer.id} - {new_customer.full_name}")
                
        except Exception as customer_error:
            # Si falla la creación del cliente, continuar sin romper el anuncio
            print(f"⚠️ Error gestionando cliente: {customer_error}")
            import traceback
            traceback.print_exc()
            # customer_id quedará None, pero el anuncio se creará igual
        
        announcement = PackageAnnouncementNew(
            id=uuid.uuid4(),
            customer_name=customer_name,
            customer_phone=customer_phone,
            guide_number=guide_number,
            tracking_code=tracking_code,
            customer_id=customer_id,  # ✅ Vincular con el cliente
            is_active=True,
            is_processed=False,
            announced_at=get_colombia_now(),
            created_at=get_colombia_now(),
            updated_at=get_colombia_now()
        )
        
        db.add(announcement)
        db.commit()
        db.refresh(announcement)
        
        # ========================================
        # ENVIAR SMS DE CONFIRMACIÓN AUTOMÁTICAMENTE
        # ========================================
        try:
            from app.services.sms_service import SMSService
            from app.models.notification import NotificationEvent, NotificationPriority
            from app.schemas.notification import SMSByEventRequest

            sms_service = SMSService()
            event_request = SMSByEventRequest(
                event_type=NotificationEvent.PACKAGE_ANNOUNCED,
                announcement_id=announcement.id,
                custom_variables={
                    "guide_number": announcement.guide_number,
                    "tracking_code": announcement.tracking_code,
                    "customer_name": announcement.customer_name
                },
                priority=NotificationPriority.ALTA,
                is_test=False
            )
            sms_result = await sms_service.send_sms_by_event(db=db, event_request=event_request)
            
            if sms_result.status == "sent":
                print(f"✅ SMS de anuncio enviado exitosamente para anuncio {announcement.id} al {announcement.customer_phone}")
            else:
                print(f"⚠️ SMS de anuncio falló para anuncio {announcement.id}: {sms_result.message}")
                
        except Exception as sms_error:
            print(f"❌ Error al enviar SMS para anuncio {announcement.id}: {sms_error}")
            import traceback
            traceback.print_exc()
        
        return {
            "success": True,
            "message": "Anuncio creado exitosamente",
            "announcement": {
                "id": str(announcement.id),
                "tracking_code": announcement.tracking_code,
                "guide_number": announcement.guide_number,
                "customer_name": announcement.customer_name,
                "customer_phone": announcement.customer_phone,
                "announced_at": announcement.announced_at.isoformat() if announcement.announced_at else None,
                "status": announcement.status
            }
        }
        
    except Exception as e:
        db.rollback()
        import traceback
        error_detail = str(e)
        print(f"Error al crear anuncio: {error_detail}")
        traceback.print_exc()
        
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Error del sistema. Por favor, comuníquese con el administrador.",
                "error": error_detail if "debug" in str(e).lower() else "Error interno"
            }
        )


@router.get("/search")
async def search_packages_and_announcements(
    q: str = None,
    db: Session = Depends(get_db)
):
    """Buscar paquetes y anuncios - DEPRECATED: Use /api/announcements/search/package instead"""
    # Redirect to the new search endpoint for consistency
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"/api/announcements/search/package?query={q or ''}", status_code=302)

@router.get("/announcements/search/package")
async def search_package_endpoint(
    query: str = None,
    db: Session = Depends(get_db)
):
    """Endpoint de búsqueda específico para el frontend - Busca paquetes y anuncios con coincidencia exacta para guías y códigos"""
    try:
        if not query or query.strip() == "":
            logger.warning("Búsqueda sin query proporcionado")
            return {
                "success": False,
                "message": "NOT_FOUND",
                "results": []
            }

        clean_query = query.strip()
        logger.info(f"Búsqueda de paquete: {clean_query}")
        results = []

        # Determinar el tipo de búsqueda
        query_type = determine_query_type(clean_query)

        # Para guías y códigos de tracking: búsqueda exacta
        # Para nombres y teléfonos: búsqueda parcial
        # Para queries inválidos: no buscar nada
        if query_type.get("type") in ["guide_number", "tracking_code"]:
            # Búsqueda exacta para guías y códigos de tracking
            announcements = db.query(PackageAnnouncementNew).filter(
                or_(
                    PackageAnnouncementNew.guide_number == clean_query,
                    PackageAnnouncementNew.tracking_code == clean_query
                )
            ).all()

            packages = db.query(Package).filter(
                Package.tracking_number == clean_query
            ).all()
        elif query_type.get("type") in ["name", "phone"]:
            # Búsqueda parcial para nombres y teléfonos
            search_term = f"%{clean_query}%"
            announcements = db.query(PackageAnnouncementNew).filter(
                or_(
                    PackageAnnouncementNew.customer_name.ilike(search_term),
                    PackageAnnouncementNew.customer_phone.ilike(search_term)
                )
            ).all()

            packages = db.query(Package).join(Package.customer, isouter=True).filter(
                or_(
                    Package.customer.full_name.ilike(search_term),
                    Package.customer.phone.ilike(search_term)
                )
            ).all()
        else:
            # Para queries inválidos (números cortos, caracteres especiales, etc.): no buscar
            announcements = []
            packages = []

        for announcement in announcements:
            results.append({
                "type": "announcement",
                "id": str(announcement.id),
                "guide_number": announcement.guide_number,
                "tracking_code": announcement.tracking_code,
                "customer_name": announcement.customer_name,
                "customer_phone": announcement.customer_phone,
                "status": "pendiente" if not announcement.is_processed else "recibido",
                "announced_at": announcement.announced_at.isoformat() if announcement.announced_at else None,
                "is_processed": announcement.is_processed
            })

        for package in packages:
            results.append({
                "type": "package",
                "id": str(package.id),
                "guide_number": package.tracking_number,
                "tracking_code": "N/A",
                "customer_name": package.customer.full_name if package.customer else None,
                "customer_phone": package.customer.phone if package.customer else None,
                "status": package.status.value if package.status else "desconocido",
                "announced_at": package.announced_at.isoformat() if package.announced_at else None,
                "is_processed": True
            })

        if len(results) == 0:
            return {
                "success": False,
                "message": "NOT_FOUND"
            }

        # Para el frontend, devolver solo el primer resultado como un anuncio individual
        # (el frontend está diseñado para mostrar un solo paquete a la vez)
        first_result = results[0]

        # Determinar el tipo de query y si mostrar formulario de consulta
        query_type_info = {
            "type": query_type.get("type"),
            "should_show_inquiry_form": query_type.get("type") == "tracking_code",
            "should_show_history": query_type.get("type") == "tracking_code"
        }

        # Obtener historial si es un tracking code (manejo robusto)
        history = []
        current_status = "ANUNCIADO"
        if query_type.get("type") == "tracking_code":
            try:
                package_obj = None
                if first_result.get("type") == "announcement":
                    # Resolver anuncio y paquete vinculado de forma robusta
                    ann = db.query(PackageAnnouncementNew).filter(
                        PackageAnnouncementNew.tracking_code == first_result.get("tracking_code")
                    ).first()
                    if ann and getattr(ann, "package_id", None):
                        package_obj = db.query(Package).filter(Package.id == ann.package_id).first()
                    if not package_obj and ann:
                        package_obj = db.query(Package).filter(Package.tracking_number == ann.guide_number).first()
                    if not package_obj and ann:
                        package_obj = db.query(Package).filter(Package.tracking_number == ann.tracking_code).first()
                elif first_result.get("type") == "package":
                    try:
                        package_obj = db.query(Package).filter(Package.id == int(first_result.get("id"))).first()
                    except Exception:
                        package_obj = None

                if package_obj:
                    # Usar el tracking_number real del paquete para obtener historial unificado
                    history_response = await get_package_history(package_obj.tracking_number, db)
                    if history_response.get("success"):
                        history = history_response.get("history", [])
                        current_status = history_response.get("current_status", "ANUNCIADO")
                else:
                    # Fallback: intentar con el código de 4 dígitos como antes
                    history_response = await get_package_history(first_result.get("tracking_code"), db)
                    if history_response.get("success"):
                        history = history_response.get("history", [])
                        current_status = history_response.get("current_status", "ANUNCIADO")
            except Exception:
                pass

        # Verificar si hay mensajes pendientes para este tracking code
        has_pending_messages = False
        if query_type.get("type") == "tracking_code":
            try:
                from sqlalchemy import text
                pending_count = db.execute(text("""
                    SELECT COUNT(*) FROM messages
                    WHERE tracking_code = :tracking_code
                    AND status = 'ABIERTO'
                """), {"tracking_code": first_result.get("tracking_code")}).scalar()
                has_pending_messages = pending_count > 0
            except:
                pass

        inquiry_info = {
            "has_existing_email": has_pending_messages,
            "has_pending_messages": has_pending_messages
        }

        # Return only the format expected by the frontend
        return {
            "success": True,
            "announcement": {
                "id": first_result["id"],
                "guide_number": first_result["guide_number"],
                "tracking_code": first_result["tracking_code"],
                "customer_name": first_result["customer_name"],
                "customer_phone": first_result["customer_phone"]
            },
            "current_status": current_status,
            "history": history,
            "query_type": query_type_info,
            "inquiry_info": inquiry_info
        }

    except Exception as e:
        logger.error(f"Error en búsqueda de paquete: {e}")
        return {
            "success": False,
            "message": "SEARCH_ERROR"
        }


def determine_query_type(query: str) -> dict:
    """
    Determinar el tipo de consulta basado en el formato del query
    Para guías y códigos de tracking, se requiere coincidencia exacta
    Solo permite búsquedas válidas, todo lo demás es inválido
    """
    import re

    print(f"DEBUG: determine_query_type called with query='{query}'")

    # Si es exactamente 4 caracteres alfanuméricos, es un tracking code
    if re.match(r'^[A-Z0-9]{4}$', query.upper()):
        print(f"DEBUG: '{query}' classified as tracking_code")
        return {"type": "tracking_code"}

    # Si parece un número de guía (5+ caracteres alfanuméricos)
    if re.match(r'^[A-Z0-9]{5,}$', query.upper()):
        print(f"DEBUG: '{query}' classified as guide_number")
        return {"type": "guide_number"}

    # Si parece un teléfono válido (mínimo 7 dígitos, con posibles espacios/guiones)
    if re.match(r'^[\d\s\-\+\(\)]{7,}$', query):
        print(f"DEBUG: '{query}' classified as phone")
        return {"type": "phone"}

    # Si parece un nombre válido (mínimo 3 caracteres alfabéticos)
    if re.match(r'^[A-Za-z\s]{3,}$', query):
        print(f"DEBUG: '{query}' classified as name")
        return {"type": "name"}

    # Para cualquier otra cosa (letras sueltas, números cortos, caracteres especiales, etc.)
    # no permitir búsqueda - devolver tipo inválido
    print(f"DEBUG: '{query}' classified as invalid")
    return {"type": "invalid"}

@router.get("/packages/{tracking_number}/history")
async def get_package_history(tracking_number: str, db: Session = Depends(get_db)):
    """Obtener historial formateado para frontend: incluye ANUNCIADO y eventos existentes.
    Si faltan eventos en package_history, se sintetizan a partir de timestamps del paquete.
    """
    try:
        # 1) Resolver anuncio y paquete por tracking_number (tracking_code)
        announcement = db.query(PackageAnnouncementNew).filter(
            PackageAnnouncementNew.tracking_code == tracking_number
        ).first()

        package = PackageStateService.get_package_by_tracking_number(db, tracking_number)
        if not package and announcement and announcement.package_id:
            package = db.query(Package).filter(Package.id == announcement.package_id).first()

        # 2) Construir eventos del historial en formato esperado por el frontend (incluir todos los estados)
        history_events = []

        # Evento ANUNCIADO (si existe anuncio)
        if announcement:
            history_events.append({
                "status": "ANUNCIADO",
                "timestamp": announcement.announced_at.isoformat() if announcement.announced_at else None,
                "description": "Paquete anunciado",
                "details": {
                    "customer_name": announcement.customer_name,
                    "customer_phone": announcement.customer_phone,
                    "guide_number": announcement.guide_number,
                    "tracking_code": announcement.tracking_code
                }
            })

        # Eventos desde la tabla package_history (RECIBIDO, ENTREGADO, CANCELADO)
        if package:
            entries = db.query(PackageHistory).filter(
                PackageHistory.package_id == package.id
            ).order_by(PackageHistory.changed_at.asc()).all()

            # Pre-cargar imágenes del paquete (para mostrar en evento RECIBIDO)
            images = db.query(FileUpload).filter(
                FileUpload.package_id == package.id,
                FileUpload.file_type == FileType.IMAGEN
            ).all()
            image_payload = [
                {
                    "s3_url": f"/api/images/{f.id}",  # Usar endpoint interno
                    "filename": f.filename
                }
                for f in images
                if f.s3_key  # Verificar s3_key en lugar de s3_url
            ]

            for entry in entries:
                status = entry.new_status
                description = {
                    "ANUNCIADO": "Paquete anunciado",
                    "RECIBIDO": "Paquete recibido",
                    "ENTREGADO": "Paquete entregado",
                    "CANCELADO": "Paquete cancelado"
                }.get(status, status.title())

                details = dict(entry.additional_data or {})

                # Enriquecer detalles para evento RECIBIDO
                if status == "RECIBIDO":
                    details.setdefault("received_by", entry.changed_by)
                    details.setdefault("package_type", getattr(package.package_type, "value", None))
                    details.setdefault("package_condition", getattr(package.package_condition, "value", None))
                    details.setdefault("images", image_payload)
                elif status == "ENTREGADO":
                    # Asegurarse de que delivered_to tenga el nombre del cliente
                    if "delivered_to" not in details or not details.get("delivered_to"):
                        customer_name = "Cliente"
                        if announcement and announcement.customer_name:
                            customer_name = announcement.customer_name
                        elif package.customer and package.customer.full_name:
                            customer_name = package.customer.full_name
                        
                        # Extraer solo el primer nombre
                        first_name = customer_name.split(' ')[0] if customer_name and customer_name != "Cliente" else customer_name
                        details["delivered_to"] = first_name

                history_events.append({
                    "status": status,
                    "timestamp": entry.changed_at.isoformat() if entry.changed_at else None,
                    "description": description,
                    "details": details
                })

        # 2.1) Síntesis de eventos faltantes basados en timestamps del paquete
        if package:
            existing_statuses = {e.get("status") for e in history_events}
            # ANUNCIADO
            if "ANUNCIADO" not in existing_statuses:
                announced_ts = None
                if package.announced_at:
                    announced_ts = package.announced_at.isoformat()
                elif announcement and announcement.announced_at:
                    announced_ts = announcement.announced_at.isoformat()
                if announced_ts:
                    history_events.insert(0, {
                        "status": "ANUNCIADO",
                        "timestamp": announced_ts,
                        "description": "Paquete anunciado",
                        "details": {
                            "customer_name": announcement.customer_name if announcement else (package.customer.full_name if package.customer else None),
                            "customer_phone": announcement.customer_phone if announcement else (package.customer.phone if package.customer else None),
                            "guide_number": announcement.guide_number if announcement else package.guide_number,
                            "tracking_code": tracking_number
                        }
                    })
            # RECIBIDO
            if package.received_at and "RECIBIDO" not in existing_statuses:
                history_events.append({
                    "status": "RECIBIDO",
                    "timestamp": package.received_at.isoformat(),
                    "description": "Paquete recibido",
                    "details": {
                        "received_by": None,
                        "package_type": getattr(package.package_type, "value", None),
                        "package_condition": getattr(package.package_condition, "value", None)
                    }
                })
            # ENTREGADO
            if package.delivered_at and "ENTREGADO" not in existing_statuses:
                # Obtener el nombre del cliente del anuncio o del paquete
                customer_name = "Cliente"
                if announcement and announcement.customer_name:
                    customer_name = announcement.customer_name
                elif package.customer and package.customer.full_name:
                    customer_name = package.customer.full_name
                
                # Extraer solo el primer nombre
                first_name = customer_name.split(' ')[0] if customer_name and customer_name != "Cliente" else customer_name
                
                history_events.append({
                    "status": "ENTREGADO",
                    "timestamp": package.delivered_at.isoformat(),
                    "description": "Paquete entregado",
                    "details": {"delivered_to": first_name}
                })
            # CANCELADO
            if package.cancelled_at and "CANCELADO" not in existing_statuses:
                history_events.append({
                    "status": "CANCELADO",
                    "timestamp": package.cancelled_at.isoformat(),
                    "description": "Paquete cancelado",
                    "details": {"reason": None}
                })

        # 3) Determinar estado actual
        current_status = package.status.value if package and hasattr(package.status, 'value') else (
            package.status if package else "ANUNCIADO"
        )

        return {
            "success": True,
            "package_id": str(package.id) if package else None,
            "tracking_number": tracking_number,
            "current_status": current_status,
            "history": history_events
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error al obtener el historial: {str(e)}",
            "history": []
        }

@router.get("/packages")
async def get_packages(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener paquetes de la base de datos con paginación"""
    try:
        # Obtener total de paquetes
        total_packages = db.query(Package).count()

        # Obtener paquetes con paginación e incluir información del cliente
        packages = db.query(Package).join(Package.customer, isouter=True).offset(skip).limit(limit).all()

        # Calcular información de paginación
        current_page = (skip // limit) + 1
        total_pages = (total_packages + limit - 1) // limit  # Ceiling division

        return {
            "success": True,
            "packages": [
                {
                    "id": str(pkg.id),
                    "tracking_number": pkg.tracking_number,
                    "customer_name": pkg.customer.full_name if pkg.customer else None,
                    "customer_phone": pkg.customer.phone if pkg.customer else None,
                    "status": pkg.status.value if pkg.status else None,
                    "package_type": pkg.package_type.value if pkg.package_type else None,
                    "package_condition": pkg.package_condition.value if pkg.package_condition else None,
                    "observations": pkg.observations,
                    "announced_at": pkg.announced_at.isoformat() if pkg.announced_at else None,
                    "received_at": pkg.received_at.isoformat() if pkg.received_at else None,
                    "delivered_at": pkg.delivered_at.isoformat() if pkg.delivered_at else None,
                    "guide_number": pkg.guide_number,
                    "baroti": pkg.posicion,
                    "access_code": pkg.access_code
                }
                for pkg in packages
            ],
            "pagination": {
                "total": total_packages,
                "page": current_page,
                "limit": limit,
                "pages": total_pages,
                "has_next": current_page < total_pages,
                "has_prev": current_page > 1
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "packages": [],
            "pagination": {
                "total": 0,
                "page": 1,
                "limit": limit,
                "pages": 0,
                "has_next": False,
                "has_prev": False
            }
        }

@router.get("/health")
async def api_health_check():
    """Health check para API"""
    from app.config import settings
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "environment": settings.environment
    }

@router.get("/test-profile-auth")
async def test_profile_auth(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies)
):
    """Endpoint de prueba para verificar autenticación"""
    return {
        "message": "Autenticación exitosa",
        "user_id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email
    }