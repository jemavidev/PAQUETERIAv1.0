# ========================================
# PAQUETES EL CLUB v4.0 - Rutas Protegidas
# ========================================

from fastapi import APIRouter, Request, HTTPException, Depends, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, or_, cast, String
from datetime import datetime
import uuid
import secrets
import string

from app.utils.auth_context import get_auth_context_from_request, get_auth_context_required
from app.database import get_db
from app.models.user import User, UserRole
from app.models.package import Package
from app.models.user_preferences import UserPreferences
# from app.models.announcement_new import Package  # Archivo eliminado
from app.dependencies import get_current_active_user, get_current_active_user_from_cookies
from app.utils.auth import get_password_hash, verify_password
from app.utils.datetime_utils import get_colombia_now
from app.services.package_state_service import PackageStateService
from app.models.customer import Customer
from app.services.customer_service import CustomerService
from app.schemas.customer import CustomerCreate, CustomerUpdate

router = APIRouter()
templates = Jinja2Templates(directory="/app/src/templates", auto_reload=True)

# ========================================
# RUTAS PROTEGIDAS - REQUIEREN AUTENTICACIÓN
# ========================================

@router.get("/settings")
async def settings_page(request: Request, current_user: User = Depends(get_current_active_user_from_cookies), db: Session = Depends(get_db)):
    """Página de configuración del usuario"""
    context = get_auth_context_from_request(request)
    context["user"] = current_user
    
    # Obtener o crear preferencias del usuario
    preferences = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()
    if not preferences:
        # Crear preferencias por defecto
        preferences = UserPreferences(
            user_id=current_user.id,
            email_notifications_enabled=True,
            push_notifications_enabled=False,
            sms_notifications_enabled=False,
            notify_package_received=True,
            notify_package_delivered=True,
            notify_messages=True,
            profile_public=True,
            share_activity_data=False,
            theme="light",
            language="es",
            items_per_page="20",
            show_statistics=True,
            show_recent_activity=True,
            show_charts=True
        )
        db.add(preferences)
        db.commit()
        db.refresh(preferences)
    
    context["preferences"] = preferences
    
    return templates.TemplateResponse("users/settings.html", context)

@router.post("/settings")
async def save_settings(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Guardar configuración del usuario"""
    try:
        form_data = await request.form()
        
        # Obtener o crear preferencias
        preferences = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()
        if not preferences:
            preferences = UserPreferences(user_id=current_user.id)
            db.add(preferences)
        
        # Actualizar preferencias de notificaciones
        preferences.email_notifications_enabled = form_data.get("email_notifications") == "on"
        preferences.push_notifications_enabled = form_data.get("push_notifications") == "on"
        preferences.sms_notifications_enabled = form_data.get("sms_notifications") == "on"
        preferences.notify_package_received = form_data.get("notify_package_received") == "on"
        preferences.notify_package_delivered = form_data.get("notify_package_delivered") == "on"
        preferences.notify_messages = form_data.get("notify_messages") == "on"
        
        # Actualizar preferencias de privacidad
        preferences.profile_public = form_data.get("profile_public") == "on"
        preferences.share_activity_data = form_data.get("share_activity_data") == "on"
        
        # Actualizar preferencias de interfaz
        preferences.theme = form_data.get("theme", "light")
        preferences.language = form_data.get("language", "es")
        preferences.items_per_page = form_data.get("items_per_page", "20")
        
        # Actualizar preferencias de dashboard
        preferences.show_statistics = form_data.get("show_statistics") == "on"
        preferences.show_recent_activity = form_data.get("show_recent_activity") == "on"
        preferences.show_charts = form_data.get("show_charts") == "on"
        
        preferences.updated_at = get_colombia_now()
        
        db.commit()
        db.refresh(preferences)
        
        # Redirigir con mensaje de éxito
        return RedirectResponse(url="/settings?success=Configuración guardada exitosamente", status_code=302)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error al guardar configuración: {e}", exc_info=True)
        
        context = get_auth_context_from_request(request)
        context["user"] = current_user
        
        # Intentar obtener preferencias actuales o usar valores por defecto
        try:
            preferences = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()
            if not preferences:
                from types import SimpleNamespace
                preferences = SimpleNamespace(
                    email_notifications_enabled=True,
                    push_notifications_enabled=False,
                    sms_notifications_enabled=False,
                    notify_package_received=True,
                    notify_package_delivered=True,
                    notify_messages=True,
                    profile_public=True,
                    share_activity_data=False,
                    theme="light",
                    language="es",
                    items_per_page="20",
                    show_statistics=True,
                    show_recent_activity=True,
                    show_charts=True
                )
        except:
            from types import SimpleNamespace
            preferences = SimpleNamespace(
                email_notifications_enabled=True,
                push_notifications_enabled=False,
                sms_notifications_enabled=False,
                notify_package_received=True,
                notify_package_delivered=True,
                notify_messages=True,
                profile_public=True,
                share_activity_data=False,
                theme="light",
                language="es",
                items_per_page="20",
                show_statistics=True,
                show_recent_activity=True,
                show_charts=True
            )
        
        context["preferences"] = preferences
        context["error"] = f"Error al guardar configuración: {str(e)}"
        return templates.TemplateResponse("users/settings.html", context)

@router.get("/admin")
async def admin_page(request: Request):
    """Página de administración - Solo para administradores"""
    context = get_auth_context_required(request)

    if not context["is_authenticated"]:
        return RedirectResponse(url="/auth/login?redirect=/admin", status_code=302)

    return templates.TemplateResponse("admin/admin.html", context)

@router.get("/test-simple")
async def test_simple():
    """Ruta de prueba simple"""
    return {"message": "Test simple funcionando"}

@router.get("/dashboard")
async def dashboard_redirect(request: Request):
    """Redirección de dashboard a administración"""
    return RedirectResponse(url="/admin", status_code=302)

@router.get("/packages")
async def packages_page(request: Request):
    """Página de gestión de paquetes - Solo para usuarios autenticados"""
    context = get_auth_context_required(request)

    if not context["is_authenticated"]:
        return RedirectResponse(url="/auth/login?redirect=/packages", status_code=302)

    return templates.TemplateResponse("packages/list.html", context)

@router.get("/packages/{package_id}")
async def package_detail_page(package_id: str, request: Request, db: Session = Depends(get_db)):
    """Página de detalle del paquete - Solo para usuarios autenticados"""
    context = get_auth_context_required(request)

    if not context["is_authenticated"]:
        return RedirectResponse(url="/auth/login?redirect=/packages/" + package_id, status_code=302)

    try:
        # Obtener el paquete de la base de datos
        package = db.query(Package).filter(Package.id == package_id).first()

        if not package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paquete no encontrado"
            )

        context["package"] = package
        return templates.TemplateResponse("packages/package_detail.html", context)

    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error al cargar paquete {package_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al cargar el paquete"
        )

@router.get("/announcements/{announcement_id}")
async def announcement_detail_page(announcement_id: str, request: Request, db: Session = Depends(get_db)):
    """Página de detalle del anuncio - Solo para usuarios autenticados"""
    context = get_auth_context_required(request)

    if not context["is_authenticated"]:
        return RedirectResponse(url="/auth/login?redirect=/announcements/" + announcement_id, status_code=302)

    try:
        # Obtener el anuncio de la base de datos
        announcement = db.query(Package).filter(Package.id == announcement_id).first()

        if not announcement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Anuncio no encontrado"
            )

        context["announcement"] = announcement
        return templates.TemplateResponse("announce/announcement_detail.html", context)

    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error al cargar anuncio {announcement_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al cargar el anuncio"
        )

@router.get("/announcements/guide/{guide_number}")
async def announcement_detail_by_guide_page(guide_number: str, request: Request, db: Session = Depends(get_db)):
    """Página de detalle del anuncio por número de guía - Con datos reales de la base de datos"""
    # Obtener contexto de autenticación
    context = get_auth_context_required(request)

    if not context["is_authenticated"]:
        return RedirectResponse(url="/auth/login?redirect=" + request.url.path, status_code=302)

    try:
        # Buscar el anuncio en la base de datos
        announcement = PackageStateService.get_announcement_by_guide_number(db, guide_number)

        if announcement:
            # Anuncio encontrado - usar datos reales
            announcement_data = {
                "id": str(announcement.id),
                "customer_name": announcement.customer_name,
                "customer_phone": announcement.customer_phone,
                "guide_number": announcement.guide_number,
                "tracking_code": announcement.tracking_code,
                "is_processed": announcement.is_processed,
                "announced_at": announcement.announced_at,
                "status": announcement.status,
                "package_type": "normal",  # Por defecto
                "package_condition": "ok",  # Por defecto
                "observations": ""
            }

            # Si el anuncio está procesado, buscar el paquete para obtener más detalles
            if announcement.is_processed:
                # Primero intentar buscar por package_id si existe
                package = None
                if announcement.package_id:
                    package = db.query(Package).filter(Package.id == announcement.package_id).first()

                # Si no se encontró por package_id, buscar por tracking_number
                if not package:
                    package = PackageStateService.get_package_by_tracking_number(db, guide_number)

                if package:
                    announcement_data.update({
                        "package_type": package.package_type.value if package.package_type else "normal",
                        "package_condition": package.package_condition.value if package.package_condition else "ok",
                        # "observations": package.observations or "",  # Campo eliminado del modelo Package
                        "package_id": str(package.id)  # Agregar el ID del paquete para cambios de estado
                    })
        else:
            # Anuncio no encontrado - crear anuncio en la base de datos
            try:
                # Generar código de tracking único
                import secrets
                import string
                tracking_code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))

                # Crear anuncio en la base de datos
                new_announcement = PackageStateService.create_announcement(
                    db=db,
                    customer_name="CLIENTE PRUEBA",
                    customer_phone=settings.test_phone_number_1,
                    guide_number=guide_number,
                    tracking_code=tracking_code,
                    created_by="system"
                )

                announcement_data = {
                    "id": str(new_announcement.id),
                    "customer_name": new_announcement.customer_name,
                    "customer_phone": new_announcement.customer_phone,
                    "guide_number": new_announcement.guide_number,
                    "tracking_code": new_announcement.tracking_code,
                    "is_processed": new_announcement.is_processed,
                    "announced_at": new_announcement.announced_at,
                    "status": "pendiente",
                    "package_type": "normal",
                    "package_condition": "ok",
                    "observations": ""
                }
            except Exception as create_error:
                # Si falla la creación, usar datos por defecto sin guardar en BD
                print(f"Error creando anuncio: {create_error}")
                announcement_data = {
                    "id": f"test-{guide_number}",
                    "customer_name": "CLIENTE PRUEBA",
                    "customer_phone": settings.test_phone_number_1,
                    "guide_number": guide_number,
                    "tracking_code": "TEST123",
                    "is_processed": False,
                    "announced_at": datetime.now(),
                    "status": "pendiente",
                    "package_type": "normal",
                    "package_condition": "ok",
                    "observations": ""
                }

        # Agregar el anuncio al contexto
        context["announcement"] = announcement_data

        return templates.TemplateResponse("announce/announcement_detail.html", context)

    except Exception as e:
        # En caso de error, usar datos por defecto
        announcement_data = {
            "id": f"test-{guide_number}",
            "customer_name": "CLIENTE PRUEBA",
            "customer_phone": settings.test_phone_number_1,
            "guide_number": guide_number,
            "tracking_code": "TEST123",
            "is_processed": False,
            "announced_at": datetime.now(),
            "status": "pendiente",
            "package_type": "normal",
            "package_condition": "ok",
            "observations": ""
        }
        context["announcement"] = announcement_data

        return templates.TemplateResponse("announce/announcement_detail.html", context)
@router.get("/customers-management")
async def customers_management_redirect(request: Request):
    """Redirección de gestión de clientes a administración"""
    return RedirectResponse(url="/admin", status_code=302)

# ========================================
# RUTAS DE GESTIÓN DE CLIENTES
# ========================================

@router.get("/customers/manage")
async def customers_manage_page(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 10
):
    """Vista de gestión de clientes con paginación (10 clientes por página)"""
    context = get_auth_context_required(request)
    context["user"] = current_user
    
    if not context["is_authenticated"]:
        return RedirectResponse(url="/auth/login?redirect=/customers/manage", status_code=302)
    
    try:
        # Obtener clientes con paginación
        skip = (page - 1) * limit
        customer_service = CustomerService()
        customers, total = customer_service.search_customers_advanced(
            db=db,
            query="",
            skip=skip,
            limit=limit
        )
        
        # Calcular metadata de paginación
        total_pages = (total + limit - 1) // limit if total > 0 else 1
        has_next = skip + limit < total
        has_prev = page > 1
        
        context["customers"] = customers
        context["pagination"] = {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev
        }
    except Exception as e:
        context["customers"] = []
        context["pagination"] = {
            "page": 1,
            "limit": limit,
            "total": 0,
            "total_pages": 1,
            "has_next": False,
            "has_prev": False
        }
    
    return templates.TemplateResponse("customers/manage.html", context)

@router.get("/customers/create")
async def customers_create_page(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Vista de formulario para crear cliente"""
    context = get_auth_context_required(request)
    context["user"] = current_user
    
    if not context["is_authenticated"]:
        return RedirectResponse(url="/auth/login?redirect=/customers/create", status_code=302)
    
    return templates.TemplateResponse("customers/create.html", context)

@router.get("/customers/edit/{customer_id}")
async def customers_edit_page(
    customer_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Vista de formulario para editar cliente"""
    context = get_auth_context_required(request)
    context["user"] = current_user
    
    if not context["is_authenticated"]:
        return RedirectResponse(url=f"/auth/login?redirect=/customers/edit/{customer_id}", status_code=302)
    
    try:
        customer_service = CustomerService()
        customer = customer_service.get_by_id(db, uuid.UUID(customer_id))
        
        if not customer:
            return RedirectResponse(url="/customers/manage?error=Cliente no encontrado", status_code=302)
        
        context["customer"] = customer
    except Exception as e:
        return RedirectResponse(url="/customers/manage?error=Error al cargar cliente", status_code=302)
    
    return templates.TemplateResponse("customers/edit.html", context)

# ========================================
# ENDPOINTS DE GESTIÓN DE USUARIOS (ADMIN)
# ========================================

@router.get("/admin/users")
async def admin_users_page(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Página de gestión de usuarios - Solo para administradores"""
    # Verificar que el usuario sea administrador
    if current_user.role.value != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo administradores pueden acceder a esta página."
        )

    context = get_auth_context_required(request)
    context["user"] = current_user

    # Validar parámetros de paginación
    page = max(1, page)
    limit = max(1, min(100, limit))  # Limitar entre 1 y 100
    skip = (page - 1) * limit

    # Obtener usuarios con paginación
    try:
        total_users = db.query(User).count()
        users = db.query(User).order_by(User.created_at.desc()).offset(skip).limit(limit).all()
        
        total_pages = (total_users + limit - 1) // limit  # Ceiling division
        
        context["users"] = users
        context["pagination"] = {
            "page": page,
            "limit": limit,
            "total": total_users,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    finally:
        pass  # No cerrar db aquí, se maneja con Depends

    return templates.TemplateResponse("admin/users.html", context)

@router.get("/admin/users/search")
async def search_users(
    request: Request,
    q: str = None,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """API endpoint para búsqueda de usuarios - Solo para administradores"""
    # Verificar que el usuario sea administrador
    if current_user.role.value != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo los administradores pueden acceder a esta función."
        )

    if not q or q.strip() == "":
        # Si no hay término de búsqueda, devolver todos los usuarios
        users = db.query(User).order_by(User.created_at.desc()).all()
    else:
        search_term = f"%{q.strip()}%"
        # Buscar en todos los campos: username, full_name, email, phone, role, is_active
        users = db.query(User).filter(
            or_(
                User.email.ilike(search_term),
                User.phone.ilike(search_term),
                cast(User.role, String).ilike(search_term),
                User.full_name.ilike(search_term),
                User.username.ilike(search_term),
                # Búsqueda por estado activo/inactivo
                User.is_active == (q.strip().lower() in ['activo', 'active', 'true', '1']),
                User.is_active == (q.strip().lower() in ['inactivo', 'inactive', 'false', '0'])
            )
        ).order_by(User.created_at.desc()).all()

    # Convertir usuarios a formato JSON
    users_data = []
    for user in users:
        users_data.append({
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
            "role": user.role.value if user.role else None,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None
        })

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
    """Crear un nuevo usuario - Solo para administradores"""
    # Verificar que el usuario sea administrador
    if current_user.role.value != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo administradores pueden crear usuarios."
        )

    try:
        # Obtener datos del JSON
        data = await request.json()

        username = data.get("username")
        email = data.get("email")
        full_name = data.get("full_name")
        phone = data.get("phone", "")
        role = data.get("role", "operator")  # Permitir "operator" o "user"
        password = data.get("password")

        # Validar que el rol sea válido
        if role not in ["OPERADOR", "USUARIO", "ADMIN"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rol inválido. Solo se permiten roles 'operator', 'user' o 'admin'"
            )

        # Validaciones básicas
        required_fields = [username, email, full_name]
        if role in ["OPERADOR", "ADMIN"]:
            required_fields.append(password)

        if not all(required_fields):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Todos los campos obligatorios deben ser completados"
            )

        # Verificar si el usuario ya existe
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario o email ya existe"
            )

        # Crear nuevo usuario
        # Hashear la contraseña solo si se proporciona (roles operator y admin)
        hashed_password = None
        if role in ["OPERADOR", "ADMIN"] and password:
            hashed_password = get_password_hash(password)

        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            phone=phone if phone else None,
            role=UserRole(role),
            password_hash=hashed_password,
            is_active=True
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "Usuario creado exitosamente",
                "user_id": str(new_user.id)
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
    """Actualizar un usuario existente - Solo para administradores"""
    # Verificar que el usuario sea administrador
    if current_user.role.value != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo administradores pueden actualizar usuarios."
        )

    try:
        # Obtener datos del JSON
        data = await request.json()

        user_id_str = data.get("user_id")
        username = data.get("username")
        email = data.get("email")
        full_name = data.get("full_name")
        phone = data.get("phone", "")
        role = data.get("role")
        is_active = data.get("is_active", True)  # Default true

        # Validaciones básicas
        if not all([user_id_str, username, email, full_name, role]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Todos los campos obligatorios deben ser completados"
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

        # Verificar que el rol sea válido
        if role not in ["OPERADOR", "USUARIO", "ADMIN"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rol inválido. Solo se permiten roles 'operator', 'user' o 'admin'"
            )

        # Buscar el usuario a actualizar
        user_to_update = db.query(User).filter(User.id == user_id).first()

        if not user_to_update:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        # Permitir cambios de rol, pero con validaciones de seguridad
        # No permitir que un admin se degrade a sí mismo si es el único admin
        from app.models.user import UserRole
        if user_to_update.role.value == "ADMIN" and role != "ADMIN" and user_to_update.id == current_user.id:
            admin_count = db.query(User).filter(User.role == UserRole.ADMIN).count()
            if admin_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No puedes cambiar tu propio rol de administrador si eres el único admin del sistema"
                )

        # Verificar si el username o email ya existen en otros usuarios
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email),
            User.id != user_id
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario o email ya existe en otro usuario"
            )

        # Actualizar el usuario
        user_to_update.username = username
        user_to_update.email = email
        user_to_update.full_name = full_name
        user_to_update.phone = phone if phone else None
        user_to_update.role = UserRole(role)
        user_to_update.is_active = is_active

        db.commit()
        db.refresh(user_to_update)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": "Usuario actualizado exitosamente",
                "user_id": str(user_to_update.id)
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar usuario: {str(e)}"
        )

@router.post("/admin/users/delete")
async def delete_user(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Eliminar un usuario - Solo para administradores"""
    # Verificar que el usuario sea administrador
    if current_user.role.value != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo administradores pueden eliminar usuarios."
        )

    try:
        # Obtener datos del JSON
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
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "success": False,
                    "detail": f"ID de usuario inválido: {user_id_str}",
                    "message": f"ID de usuario inválido: {user_id_str}"
                }
            )

        # Buscar el usuario a eliminar
        user_to_delete = db.query(User).filter(User.id == user_id).first()

        if not user_to_delete:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "success": False,
                    "detail": "Usuario no encontrado",
                    "message": "Usuario no encontrado"
                }
            )

        # No permitir eliminar el propio usuario
        if user_to_delete.id == current_user.id:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "success": False,
                    "detail": "No puedes eliminar tu propio usuario",
                    "message": "No puedes eliminar tu propio usuario"
                }
            )

        # Usar AdminService para eliminar el usuario (tiene validaciones adicionales)
        from app.services.admin_service import AdminService
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
            status_code=status.HTTP_400_BAD_REQUEST,
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
    """Activar/Desactivar un usuario - Solo para administradores"""
    # Verificar que el usuario sea administrador
    if current_user.role.value != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo administradores pueden cambiar el estado de usuarios."
        )

    try:
        # Obtener datos del JSON
        data = await request.json()
        user_id_str = data.get("user_id")
        is_active = data.get("is_active")

        if not user_id_str or is_active is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de usuario y estado requeridos"
            )

        # Convertir string a UUID
        try:
            user_id = uuid.UUID(user_id_str)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de usuario inválido"
            )

        # Buscar el usuario
        user_to_update = db.query(User).filter(User.id == user_id).first()

        if not user_to_update:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        # No permitir desactivar el propio usuario
        if user_to_update.id == current_user.id and not is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes desactivar tu propio usuario"
            )

        # Actualizar el estado
        user_to_update.is_active = is_active
        db.commit()
        db.refresh(user_to_update)

        status_text = "activado" if is_active else "desactivado"
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": f"Usuario {status_text} exitosamente",
                "is_active": is_active
            }
        )

    except HTTPException:
        raise
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
    """Restablecer contraseña de un usuario - Solo para administradores"""
    # Verificar que el usuario sea administrador
    if current_user.role.value != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo administradores pueden restablecer contraseñas."
        )

    try:
        # Obtener datos del JSON
        data = await request.json()
        user_id_str = data.get("user_id")

        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de usuario requerido"
            )

        # Convertir string a UUID
        try:
            user_id = uuid.UUID(user_id_str)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de usuario inválido"
            )

        # Buscar el usuario
        user_to_reset = db.query(User).filter(User.id == user_id).first()

        if not user_to_reset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        # Solo restablecer contraseña para usuarios con rol operator o admin
        if user_to_reset.role.value not in ["ADMIN", "OPERADOR"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden restablecer contraseñas de usuarios con rol Administrador u Operador"
            )

        # Generar nueva contraseña temporal
        new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))

        # Actualizar la contraseña
        user_to_reset.password_hash = get_password_hash(new_password)
        db.commit()

        # Aquí se podría enviar un email con la nueva contraseña
        # Por ahora, solo retornamos un mensaje de éxito

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": "Contraseña restablecida exitosamente",
                "new_password": new_password  # En producción, esto debería enviarse por email
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al restablecer contraseña: {str(e)}"
        )

# ========================================
# GESTIÓN DE PERFIL DE USUARIO
# ========================================

@router.post("/profile/edit")
async def edit_profile_submit(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Procesar formulario de edición de perfil"""
    try:
        # Obtener datos del formulario
        form_data = await request.form()
        
        username = form_data.get("username", "").strip()
        email = form_data.get("email", "").strip()
        full_name = form_data.get("full_name", "").strip()
        phone = form_data.get("phone", "").strip() or None
        
        # Validaciones básicas
        if not all([username, email, full_name]):
            context = get_auth_context_from_request(request)
            context["user"] = current_user
            context["error"] = "Los campos username, email y full_name son obligatorios"
            return templates.TemplateResponse("users/edit_profile_page.html", context)
        
        # Verificar username único si se está cambiando
        if username.lower() != current_user.username:
            existing = db.query(User).filter(
                and_(
                    User.username == username.lower(),
                    User.id != current_user.id
                )
            ).first()
            if existing:
                context = get_auth_context_from_request(request)
                context["user"] = current_user
                context["error"] = f"El nombre de usuario '{username}' ya existe"
                return templates.TemplateResponse("users/edit_profile_page.html", context)
        
        # Verificar email único si se está cambiando
        if email.lower() != current_user.email:
            existing = db.query(User).filter(
                and_(
                    User.email == email.lower(),
                    User.id != current_user.id
                )
            ).first()
            if existing:
                context = get_auth_context_from_request(request)
                context["user"] = current_user
                context["error"] = f"El email '{email}' ya está registrado"
                return templates.TemplateResponse("users/edit_profile_page.html", context)
        
        # Validar formato de teléfono si se proporciona
        if phone:
            # Limpiar teléfono (remover espacios, guiones, etc.)
            phone = ''.join(filter(str.isdigit, phone))
            if len(phone) != 10:
                context = get_auth_context_from_request(request)
                context["user"] = current_user
                context["error"] = "El teléfono debe tener 10 dígitos"
                return templates.TemplateResponse("users/edit_profile_page.html", context)
        
        # Actualizar usuario en la base de datos
        current_user.username = username.lower()
        current_user.email = email.lower()
        current_user.full_name = full_name
        current_user.phone = phone
        current_user.updated_at = get_colombia_now()
        
        db.commit()
        db.refresh(current_user)
        
        # Redirigir al perfil con mensaje de éxito
        return RedirectResponse(url="/profile?success=Perfil actualizado exitosamente", status_code=302)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        context = get_auth_context_from_request(request)
        context["user"] = current_user
        context["error"] = f"Error al actualizar perfil: {str(e)}"
        return templates.TemplateResponse("users/edit_profile_page.html", context)

@router.post("/profile/update")
async def update_current_user_profile(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Actualizar perfil del usuario actual (API JSON)"""
    try:
        # Obtener datos del request JSON
        data = await request.json()

        username = data.get("username", "").strip()
        email = data.get("email", "").strip()
        full_name = data.get("full_name", "").strip()
        phone = data.get("phone", "").strip() or None

        # Validaciones básicas
        if not all([username, email, full_name]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Los campos username, email y full_name son obligatorios"
            )

        # Verificar username único si se está cambiando
        if username.lower() != current_user.username:
            existing = db.query(User).filter(
                and_(
                    User.username == username.lower(),
                    User.id != current_user.id
                )
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El nombre de usuario '{username}' ya existe"
                )

        # Verificar email único si se está cambiando
        if email.lower() != current_user.email:
            existing = db.query(User).filter(
                and_(
                    User.email == email.lower(),
                    User.id != current_user.id
                )
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El email '{email}' ya está registrado"
                )

        # Actualizar usuario
        current_user.username = username.lower()
        current_user.email = email.lower()
        current_user.full_name = full_name
        current_user.phone = phone

        # Separar nombre completo en first_name y last_name
        # Nota: first_name y last_name son propiedades calculadas del full_name
        # No necesitamos asignarlas ya que se calculan automáticamente

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

@router.post("/profile/api/change-password")
async def change_current_user_password(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Cambiar contraseña del usuario actual"""
    try:
        # Obtener datos del request JSON
        data = await request.json()

        current_password = data.get("current_password", "").strip()
        new_password = data.get("new_password", "").strip()

        # Validaciones básicas
        if not all([current_password, new_password]):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "success": False,
                    "detail": "La contraseña actual y la nueva contraseña son obligatorias"
                }
            )

        if len(new_password) < 8:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "success": False,
                    "detail": "La nueva contraseña debe tener al menos 8 caracteres"
                }
            )

        # Verificar que la contraseña actual sea correcta
        if not verify_password(current_password, current_user.password_hash):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "success": False,
                    "detail": "La contraseña actual es incorrecta"
                }
            )

        # Verificar que la nueva contraseña sea diferente a la actual
        if verify_password(new_password, current_user.password_hash):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "success": False,
                    "detail": "La nueva contraseña debe ser diferente a la contraseña actual"
                }
            )

        # Actualizar la contraseña en la base de datos
        current_user.password_hash = get_password_hash(new_password)
        current_user.updated_at = get_colombia_now()

        db.commit()
        db.refresh(current_user)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": "Contraseña cambiada exitosamente"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error al cambiar contraseña: {e}", exc_info=True)
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "detail": f"Error al cambiar contraseña: {str(e)}"
            }
        )

# ========================================
# ENDPOINTS DE GESTIÓN DE PAQUETES
# ========================================

@router.post("/api/announcements/{announcement_id}/create-package")
async def create_package_from_announcement_simple(announcement_id: str, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user_from_cookies)):
    """Actualizar estado de paquete desde ANUNCIADO a RECIBIDO - Con historial completo"""
    try:
        # Obtener datos del request
        body = await request.json()
        package_type = body.get("package_type", "normal")
        package_condition = body.get("package_condition", "ok")
        observations = body.get("observations", "")

        print(f"🔧 DEBUG: Endpoint called with announcement_id={announcement_id}")
        print(f"🔧 DEBUG: Request body: {body}")

        from app.models.package import PackageType, PackageCondition

        # Intentar convertir announcement_id a UUID para ver si es un ID real
        try:
            announcement_uuid = uuid.UUID(announcement_id)
            # Si es un UUID válido, buscar el anuncio por ID
            announcement = db.query(Package).filter(Package.id == announcement_uuid).first()
            if announcement:
                guide_number = announcement.guide_number
                print(f"🔧 DEBUG: Found announcement by UUID: {guide_number}")
            else:
                raise ValueError(f"No se encontró anuncio con ID: {announcement_id}")
        except (ValueError, TypeError):
            # Si no es un UUID válido, tratarlo como guide_number
            guide_number = announcement_id
            print(f"🔧 DEBUG: Treating as guide_number: {guide_number}")

        try:
            package_type_enum = PackageType(package_type)
            package_condition_enum = PackageCondition(package_condition)
            print(f"🔧 DEBUG: Enums converted successfully: {package_type_enum}, {package_condition_enum}")
        except Exception as enum_error:
            raise ValueError(f"Valor inválido para enum: {enum_error}")

        # Obtener nombre real del usuario actual
        operator_name = "Sistema"
        if current_user:
            operator_name = current_user.username or current_user.first_name or f"Usuario {current_user.id}"

        # Usar el servicio de estados para procesar el cambio
        print(f"🔧 DEBUG: Calling PackageStateService.process_announcement_to_received")
        result = PackageStateService.process_announcement_to_received(
            db=db,
            guide_number=guide_number,
            package_type=package_type_enum,
            package_condition=package_condition_enum,
            observations=observations,
            changed_by=operator_name  # Usar nombre real del usuario
        )

        print(f"🔧 DEBUG: Service returned: {result}")
        return result

    except ValueError as e:
        # Error de validación (paquete no encontrado, transición no permitida, etc.)
        print(f"❌ DEBUG: ValueError: {str(e)}")
        return {
            "success": False,
            "message": str(e),
            "package_id": None,
            "status": "ERROR_VALIDACION"
        }
    except Exception as e:
        db.rollback()
        print(f"❌ DEBUG: Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Error al procesar el anuncio: {str(e)}",
            "package_id": None,
            "status": "ERROR"
        }

@router.get("/api/packages/{tracking_number}/history")
async def get_package_history(tracking_number: str, db: Session = Depends(get_db)):
    """Obtener el historial completo de un paquete"""
    try:
        # Buscar el paquete
        package = PackageStateService.get_package_by_tracking_number(db, tracking_number)
        if not package:
            return {
                "success": False,
                "message": f"No se encontró un paquete con el número de guía: {tracking_number}",
                "history": []
            }

        # Obtener el historial del anuncio
        history = PackageStateService.get_announcement_history(db, tracking_number)

        return {
            "success": True,
            "package_id": str(package.id),
            "tracking_number": package.tracking_number,
            "current_status": package.status.value,
            "history": [entry.to_dict() for entry in history]
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error al obtener el historial: {str(e)}",
            "history": []
        }

# TEMPORARILY DISABLED - CONFLICT WITH packages.py
# @router.put("/api/packages/{package_id}/status")
async def update_package_status_disabled(package_id: str, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user_from_cookies)):
    """Actualizar el estado de un paquete"""
    try:
        print(f"🔄 DEBUG: update_package_status called with package_id={package_id}")

        # Obtener datos del request
        body = await request.json()
        new_status = body.get("status")

        print(f"🔄 DEBUG: Request body: {body}")
        print(f"🔄 DEBUG: New status: {new_status}")

        if not new_status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El campo 'status' es requerido"
            )

        # Convertir string a entero (Package.id es Integer, no UUID)
        try:
            package_id_int = int(package_id)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de paquete inválido"
            )

        # Buscar el paquete
        package = db.query(Package).filter(Package.id == package_id_int).first()
        if not package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paquete no encontrado"
            )

        # Convertir string de status a enum
        from app.models.package import PackageStatus
        try:
            status_enum = PackageStatus(new_status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estado inválido: {new_status}. Estados válidos: {[s.value for s in PackageStatus]}"
            )

        print(f"🔄 DEBUG: Current package status: {package.status}")
        print(f"🔄 DEBUG: New status enum: {status_enum}")
        print(f"🔄 DEBUG: Transition: {package.status.value} -> {status_enum.value}")

        # Actualizar el estado usando el servicio
        history_entry = PackageStateService.update_package_status(
            db=db,
            package=package,
            new_status=status_enum,
            changed_by="user"  # TODO: Obtener del usuario autenticado
        )

        return {
            "success": True,
            "message": f"Estado del paquete actualizado a {status_enum.value}",
            "package_id": str(package.id),
            "new_status": status_enum.value,
            "history_entry_id": str(history_entry.id)
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el estado del paquete: {str(e)}"
        )

@router.get("/api/packages")
async def get_packages(db: Session = Depends(get_db)):
    """Obtener todos los paquetes de la base de datos"""
    try:
        from sqlalchemy.orm import joinedload
        
        packages = db.query(Package).options(joinedload(Package.customer)).all()
        return {
            "success": True,
            "count": len(packages),
            "packages": [
                {
                    "id": str(pkg.id),
                    "tracking_number": pkg.tracking_number,
                    "customer_name": pkg.customer.full_name if pkg.customer else "Sin cliente",
                    "customer_phone": pkg.customer.phone if pkg.customer else "Sin teléfono",
                    "status": pkg.status.value if pkg.status else None,
                    "package_type": pkg.package_type.value if pkg.package_type else None,
                    "package_condition": pkg.package_condition.value if pkg.package_condition else None,
                    "observations": None,  # Campo no disponible en el modelo actual
                    "baroti": pkg.posicion,
                    "guide_number": pkg.guide_number,
                    "access_code": pkg.access_code,
                    "announced_at": pkg.announced_at.isoformat() if pkg.announced_at else None,
                    "received_at": pkg.received_at.isoformat() if pkg.received_at else None,
                    "delivered_at": pkg.delivered_at.isoformat() if pkg.delivered_at else None,
                    "cancelled_at": pkg.cancelled_at.isoformat() if pkg.cancelled_at else None,
                    "created_at": pkg.created_at.isoformat() if pkg.created_at else None
                }
                for pkg in packages
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "count": 0,
            "packages": []
        }

@router.get("/api/dashboard/packages")
async def get_dashboard_packages(
    page: int = 1,
    limit: int = 8,
    search: str = None,
    db: Session = Depends(get_db)
):
    """Obtener paquetes para el dashboard con paginación y búsqueda"""
    try:
        # Construir query base
        packages_query = db.query(Package)

        # Aplicar filtros de búsqueda si se proporciona
        if search and search.strip():
            search_term = f"%{search.strip()}%"
            packages_query = packages_query.filter(
                or_(
                    Package.customer_name.ilike(search_term),
                    Package.customer_phone.ilike(search_term),
                    Package.guide_number.ilike(search_term),
                    Package.tracking_number.ilike(search_term)
                )
            )

        # Ordenar por fecha de anuncio descendente
        packages_query = packages_query.order_by(Package.announced_at.desc())

        # Calcular offset
        offset = (page - 1) * limit

        # Obtener total de paquetes (con filtros aplicados)
        total_packages = packages_query.count()

        # Obtener paquetes con paginación
        packages = packages_query.offset(offset).limit(limit).all()

        # Calcular información de paginación
        total_pages = (total_packages + limit - 1) // limit  # Ceiling division

        # Convertir a formato para el frontend
        packages_data = []
        for announcement in packages:
            packages_data.append({
                "id": str(announcement.id),
                "customer_name": announcement.customer_name,
                "customer_phone": announcement.customer_phone,
                "guide_number": announcement.guide_number,
                "tracking_code": announcement.tracking_code,
                "is_processed": announcement.is_processed,
                "announced_at": announcement.announced_at.isoformat() if announcement.announced_at else None,
                "package_type": getattr(announcement, 'package_type', None),
                "package_condition": getattr(announcement, 'package_condition', None),
                "observations": getattr(announcement, 'observations', None),
                "estimated_cost": getattr(announcement, 'estimated_cost', None)
            })

        return {
            "success": True,
            "packages": packages_data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_packages,
                "total_pages": total_pages,
                "has_prev": page > 1,
                "has_next": page < total_pages
            },
            "search": search
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "packages": [],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": 0,
                "total_pages": 0,
                "has_prev": False,
                "has_next": False
            },
            "search": search
        }


@router.get("/logout")
async def logout_page(request: Request):
    """Página de logout - Redirige a la página de login"""
    # Limpiar cookies de autenticación
    response = RedirectResponse(url="/auth/login", status_code=302)
    response.delete_cookie("access_token")
    response.delete_cookie("user_id")
    response.delete_cookie("user_name")
    response.delete_cookie("user_role")
    return response

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

@router.post("/admin/cleanup-database")
async def cleanup_database(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Endpoint temporal para limpiar la base de datos - Solo para administradores"""
    
    # Verificar que el usuario sea administrador
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden ejecutar esta operación"
        )
    
    try:
        # Tablas a limpiar en orden correcto
        tables = [
            'file_uploads',
            'messages', 
            'package_history',
            'package_announcements_new',
            'packages',
            'customers'
        ]
        
        total_deleted = 0
        results = {}
        
        # Obtener conteo actual
        for table in tables:
            try:
                result = db.execute(f"SELECT COUNT(*) FROM {table}")
                count = result.scalar()
                results[table] = {"before": count}
            except Exception as e:
                results[table] = {"error": str(e)}
        
        # Ejecutar limpieza
        for table in tables:
            try:
                result = db.execute(f"DELETE FROM {table}")
                deleted = result.rowcount
                total_deleted += deleted
                results[table]["deleted"] = deleted
            except Exception as e:
                results[table]["error"] = str(e)
        
        # Commit cambios
        db.commit()
        
        # Verificar limpieza
        for table in tables:
            try:
                result = db.execute(f"SELECT COUNT(*) FROM {table}")
                count = result.scalar()
                results[table]["after"] = count
            except Exception as e:
                results[table]["verify_error"] = str(e)
        
        return {
            "message": "Limpieza completada exitosamente",
            "total_deleted": total_deleted,
            "results": results,
            "timestamp": get_colombia_now().isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante la limpieza: {str(e)}"
        )