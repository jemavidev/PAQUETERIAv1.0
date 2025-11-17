 # ========================================
# PAQUETES EL CLUB v1.0 - Rutas Públicas
# ========================================

import logging
from fastapi import APIRouter, Request, HTTPException, Depends, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
import uuid
from typing import List, Dict

from app.utils.auth_context import get_auth_context_from_request
from app.database import get_db
from app.models.announcement_new import PackageAnnouncementNew
from app.models.package import Package, PackageStatus
from app.models.customer import Customer
from app.models.package_history import PackageHistory
from app.models.message import Message, MessageType, MessageStatus, MessagePriority
from app.services.package_state_service import PackageStateService
from app.utils.normalization import normalize_history_event, normalize_package_item, normalize_status
from app.services.s3_service import S3Service
from app.utils.datetime_utils import get_colombia_now
from app.schemas.message import CustomerInquiryCreate
from sqlalchemy.orm import joinedload
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()
from app.utils.template_loader import get_templates
templates = get_templates()

# ==========================================
# RUTAS PÚBLICAS - ACCESO SIN AUTENTICACIÓN
# ==========================================

@router.get("/")
async def root(request: Request):
    """
    Redirigir la raíz a la página pública de anuncio.
    """
    return RedirectResponse(url="/announce", status_code=302)

@router.get("/error-demo")
async def error_demo(request: Request):
    """
    Página de demostración del sistema de manejo de errores
    
    Args:
        request (Request): Objeto request de FastAPI
        
    Returns:
        TemplateResponse: Página HTML con demo de errores
    """
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("error-demo.html", context)

@router.post("/test-validation")
async def test_validation(data: dict):
    """
    Endpoint de prueba para validación de errores
    
    Args:
        data: Datos del formulario
        
    Returns:
        JSONResponse: Respuesta con error formateado
    """
    from pydantic import BaseModel, Field, ValidationError
    from fastapi.exceptions import RequestValidationError
    
    class TestModel(BaseModel):
        content: str = Field(..., min_length=10, max_length=2000)
        email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    
    try:
        validated_data = TestModel(**data)
        return {"success": True, "message": "Validación exitosa", "data": validated_data.dict()}
    except ValidationError as e:
        # Convertir ValidationError a RequestValidationError para que sea capturado por el handler
        raise RequestValidationError(e.errors())

@router.get("/customers")
async def customers_page(request: Request):
    """Página de anunciar paquetes - Redirige a la página principal"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/", status_code=302)

@router.get("/announce")
async def announce_page(request: Request):
    """Página de anunciar paquetes - Pública"""
    try:
        context = get_auth_context_from_request(request)
    except Exception as auth_error:
        logger.debug(f"Usuario no autenticado en /announce: {auth_error}")
        # Contexto por defecto para usuarios no autenticados
        context = {
            "is_authenticated": False,
            "user": None,
            "user_name": None,
            "user_role": None,
            "request": request
        }
    
    context["package_announcements"] = []
    context["current_path"] = str(request.url.path)
    
    return templates.TemplateResponse("announce/announce.html", context)

@router.get("/search")
async def search_page(request: Request):
    """Página de consulta de paquetes - Pública"""
    try:
        context = get_auth_context_from_request(request)
    except Exception as auth_error:
        logger.debug(f"Usuario no autenticado en /search: {auth_error}")
        # Contexto por defecto para usuarios no autenticados
        context = {
            "is_authenticated": False,
            "user": None,
            "user_name": None,
            "user_role": None,
            "request": request
        }
    
    context["current_path"] = str(request.url.path)
    return templates.TemplateResponse("packages/search.html", context)

@router.get("/messages")
async def messages_page(
    request: Request, 
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 9
):
    """Página de mensajes - Con autenticación real y paginación"""
    # Obtener contexto de autenticación
    context = get_auth_context_from_request(request)

    try:
        # Consultar el total de mensajes para estadísticas
        total_query = db.query(Message)
        total_messages = total_query.count()
        
        # Calcular offset para la paginación
        offset = (page - 1) * limit
        
        # Consultar mensajes con paginación
        messages = total_query.order_by(Message.created_at.desc()).offset(offset).limit(limit).all()

        # Convertir mensajes a formato compatible con el template
        messages_data = []
        for msg in messages:
            messages_data.append({
                "id": str(msg.id),
                "subject": msg.subject,
                "content": msg.content,
                "answer": msg.answer or "",
                "customer_name": msg.sender_name or "Cliente",
                "customer_phone": msg.sender_phone or "",
                "customer_email": msg.sender_email or "",
                "package_guide_number": "",  # No tenemos este campo directamente
                "package_tracking_code": msg.tracking_code or "",
                "is_read": msg.is_read,
                "status": msg.status.value if hasattr(msg.status, 'value') else str(msg.status),
                "message_type": msg.message_type.value if hasattr(msg.message_type, 'value') else str(msg.message_type),
                "priority": msg.priority.value if hasattr(msg.priority, 'value') else str(msg.priority),
                "created_at": msg.created_at.isoformat() if msg.created_at else None,
                "updated_at": msg.updated_at.isoformat() if msg.updated_at else None
            })

        # Calcular estadísticas (sobre todos los mensajes, no solo la página actual)
        all_messages = total_query.all()
        unread_count = sum(1 for m in all_messages if not m.is_read)
        pending_count = sum(1 for m in all_messages if (m.status.value if hasattr(m.status, 'value') else str(m.status)) == "ABIERTO")
        closed_count = sum(1 for m in all_messages if (m.status.value if hasattr(m.status, 'value') else str(m.status)) in ["CERRADO", "CLOSED"])

        # Calcular metadata de paginación
        import math
        total_pages = math.ceil(total_messages / limit) if total_messages > 0 else 1
        has_prev = page > 1
        has_next = page < total_pages

        context["messages"] = messages_data
        context["total_messages"] = total_messages
        context["message_stats"] = {
            "total": total_messages,
            "unread": unread_count,
            "pending": pending_count,
            "closed": closed_count
        }
        context["pagination"] = {
            "page": page,
            "limit": limit,
            "total": total_messages,
            "total_pages": total_pages,
            "has_prev": has_prev,
            "has_next": has_next
        }

    except Exception as e:
        # En caso de error, mostrar datos vacíos
        print(f"Error al cargar mensajes: {str(e)}")
        context["messages"] = []
        context["total_messages"] = 0
        context["message_stats"] = {
            "total": 0,
            "unread": 0,
            "pending": 0,
            "closed": 0
        }
        context["pagination"] = {
            "page": 1,
            "limit": 9,
            "total": 0,
            "total_pages": 1,
            "has_prev": False,
            "has_next": False
        }

    return templates.TemplateResponse("messages/messages.html", context)

@router.get("/test-messages")
async def test_messages_page():
    """Página de prueba de mensajes - Sin autenticación"""
    return {"message": "Test endpoint funcionando"}

@router.get("/demo-error-system")
async def demo_error_system_page(request: Request):
    """Página de demostración del sistema de alertas unificado"""
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("demo_error_system.html", context)

@router.get("/login")
async def login_page(request: Request):
    """Página de login - Pública"""
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("auth/login.html", context)

@router.get("/auth/login")
async def auth_login_page(request: Request):
    """Página de login - Pública (ruta alternativa)"""
    # Obtener parámetro de redirección
    redirect_url = request.query_params.get("redirect", "/dashboard")
    context = get_auth_context_from_request(request)
    context["redirect_url"] = redirect_url
    return templates.TemplateResponse("auth/login.html", context)

@router.get("/auth/register")
async def auth_register_page(request: Request):
    """Página de registro - Pública"""
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("auth/register.html", context)

@router.get("/auth/forgot-password")
async def auth_forgot_password_page(request: Request):
    """Página de recuperación de contraseña - Pública"""
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("auth/forgot-password.html", context)

@router.get("/auth/reset-password")
async def auth_reset_password_page(request: Request):
    """Página de restablecimiento de contraseña - Pública"""
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("auth/reset-password.html", context)

@router.get("/help")
async def help_page(request: Request):
    """Página de ayuda - Pública"""
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("general/help.html", context)

@router.get("/test-search")
async def test_search_page(request: Request):
    """Página de prueba de búsqueda - Pública"""
    return templates.TemplateResponse("testing/test_search.html", context={"request": request})

@router.get("/cookies")
async def cookies_page(request: Request):
    """Página de política de cookies - Pública"""
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("general/cookies.html", context)

@router.get("/policies")
async def policies_page(request: Request):
    """Página de políticas - Pública"""
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("general/policies.html", context)

# ========================================
# ENDPOINTS ADICIONALES PARA AUTENTICACIÓN
# ========================================

@router.post("/api/auth/dev/set-cookies")
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

        # Establecer cookies (24 horas)
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

@router.get("/api/auth/dev/check")
async def check_auth(request: Request):
    """Verificar estado de autenticación desde frontend"""
    # Verificar si existe el token de acceso en las cookies
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

# ========================================
# ENDPOINTS DE BÚSQUEDA Y ANUNCIOS
# ========================================

@router.post("/api/announcements/direct")
async def create_announcement_direct(request: Request, db: Session = Depends(get_db)):
    """Crear un nuevo anuncio de paquete - Endpoint directo"""
    try:
        # Obtener datos del request
        body = await request.json()
        customer_name = body.get("customer_name", "").strip().upper()
        customer_phone = body.get("customer_phone", "").strip()
        guide_number = body.get("guide_number", "").strip().upper()

        # Validaciones básicas
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

        # Verificar si ya existe un anuncio con este número de guía
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

        # Enviar SMS de confirmación automáticamente
        try:
            from app.services.sms_service import SMSService
            from app.models.notification import NotificationEvent
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
                priority="normal",
                is_test=False
            )
            await sms_service.send_sms_by_event(db=db, event_request=event_request)
        except Exception as sms_error:
            # Log error but don't fail the announcement creation
            print(f"Error sending SMS confirmation for announcement {announcement.id}: {str(sms_error)}")
            # Continue with success response

        # Enviar EMAIL de confirmación automáticamente
        # Solo si el anuncio está vinculado a un cliente con email registrado
        try:
            if announcement.customer_id:
                customer = db.query(Customer).filter(Customer.id == announcement.customer_id).first()
            else:
                customer = None

            if customer and getattr(customer, "email", None):
                from app.services.email_service import EmailService
                from app.models.notification import NotificationEvent

                email_service = EmailService()

                full_name = customer.full_name or announcement.customer_name
                first_name = full_name.split(" ")[0]

                consult_code = announcement.tracking_code
                tracking_base = settings.tracking_base_url.rstrip("/")
                tracking_url = f"{tracking_base}?auto_search={consult_code}"

                await email_service.send_email_by_event(
                    db=db,
                    event_type=NotificationEvent.PACKAGE_ANNOUNCED,
                    recipient=customer.email,
                    variables={
                        "first_name": first_name,
                        "current_status": PackageStatus.ANUNCIADO.value,
                        "guide_number": announcement.guide_number,
                        "consult_code": consult_code,
                        "tracking_url": tracking_url,
                    },
                    package_id=None,
                    customer_id=str(customer.id),
                    announcement_id=str(announcement.id),
                    is_test=False,
                )
        except Exception as email_error:
            # Log error but don't bloquear el flujo de anuncio
            print(f"Error sending EMAIL confirmation for announcement {announcement.id}: {str(email_error)}")

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

@router.get("/api/search")
async def search_packages_and_announcements(
    q: str = None,
    db: Session = Depends(get_db)
):
    """Buscar paquetes y anuncios por número de guía, código de tracking, nombre o teléfono"""
    try:
        from sqlalchemy import or_

        if not q or q.strip() == "":
            return {
                "success": False,
                "message": "Término de búsqueda requerido",
                "results": []
            }

        search_term = f"%{q.strip()}%"
        results = []

        # Buscar en anuncios
        announcements = db.query(PackageAnnouncementNew).filter(
            or_(
                PackageAnnouncementNew.guide_number.ilike(search_term),
                PackageAnnouncementNew.tracking_code.ilike(search_term),
                PackageAnnouncementNew.customer_name.ilike(search_term),
                PackageAnnouncementNew.customer_phone.ilike(search_term)
            )
        ).all()

        for announcement in announcements:
            results.append({
                "type": "announcement",
                "id": str(announcement.id),
                "guide_number": announcement.guide_number,
                "tracking_code": announcement.tracking_code,
                "customer_name": announcement.customer_name,
                "customer_phone": announcement.customer_phone,
                "status": "ANUNCIADO" if not announcement.is_processed else "RECIBIDO",
                "announced_at": announcement.announced_at.isoformat() if announcement.announced_at else None,
                "is_processed": announcement.is_processed
            })

        # Buscar en paquetes (comentado temporalmente para evitar errores)
        # packages = db.query(Package).filter(
        #     Package.tracking_number.ilike(search_term)
        # ).all()

        # for package in packages:
        #     results.append({
        #         "type": "package",
        #         "id": str(package.id),
        #         "guide_number": package.tracking_number,
        #         "tracking_code": "N/A",  # Los paquetes no tienen tracking_code
        #         "customer_name": "No disponible",  # Simplificado
        #         "customer_phone": "No disponible",  # Simplificado
        #         "status": package.status.value if package.status else "desconocido",
        #         "announced_at": package.announced_at.isoformat() if package.announced_at else None,
        #         "is_processed": True
        #     })

        return {
            "success": True,
            "message": f"Se encontraron {len(results)} resultados",
            "results": results,
            "search_term": q
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error al buscar: {str(e)}",
            "results": []
        }

@router.get("/api/announcements/search/package")
async def search_package_endpoint(
    query: str = None,
    db: Session = Depends(get_db)
):
    """Endpoint de búsqueda específico para el frontend - Busca paquetes y anuncios"""
    try:
        from sqlalchemy import or_

        if not query or query.strip() == "":
            return {
                "success": False,
                "message": "NOT_FOUND",
                "results": []
            }

        search_term = f"%{query.strip()}%"
        results = []

        # Determinar el tipo de búsqueda
        query_type = determine_query_type(query.strip())

        # Buscar en anuncios - solo coincidencias exactas por guía o tracking
        announcements = db.query(PackageAnnouncementNew).filter(
            or_(
                PackageAnnouncementNew.guide_number == query.strip(),
                PackageAnnouncementNew.tracking_code == query.strip()
            )
        ).all()

        for announcement in announcements:
            results.append({
                "type": "announcement",
                "id": str(announcement.id),
                "guide_number": announcement.guide_number,
                "tracking_code": announcement.tracking_code,
                "customer_name": announcement.customer_name,
                "customer_phone": announcement.customer_phone,
                "status": "ANUNCIADO" if not announcement.is_processed else "RECIBIDO",
                "announced_at": announcement.announced_at.isoformat() if announcement.announced_at else None,
                "is_processed": announcement.is_processed
            })

        # Buscar en paquetes (incluyendo access_code para códigos cortos de 4 caracteres)
        packages = db.query(Package).filter(
            or_(
                Package.tracking_number == query.strip(),
                Package.guide_number == query.strip(),
                Package.access_code == query.strip()  # Agregar búsqueda por access_code
            )
        ).all()

        for package in packages:
            try:
                # Obtener información del cliente
                customer_name = package.customer.full_name if package.customer else "Sin cliente"
                customer_phone = package.customer.phone if package.customer else "Sin teléfono"

                # Determinar qué mostrar como tracking_code:
                # Si fue encontrado por access_code, mostrar el access_code
                # Si no, mostrar el tracking_number
                tracking_code_display = package.access_code if package.access_code == query.strip() else package.tracking_number

                print(f"✅ Paquete encontrado: ID={package.id}, access_code={package.access_code}, tracking_number={package.tracking_number}, guide_number={package.guide_number}")

                results.append({
                    "type": "package",
                    "id": str(package.id),
                    "guide_number": package.guide_number or package.tracking_number,  # Mostrar guide_number si existe
                    "tracking_code": tracking_code_display,  # Mostrar el código que se usó para buscar
                    "customer_name": customer_name,
                    "customer_phone": customer_phone,
                    "status": package.status.value if hasattr(package.status, 'value') else str(package.status),
                    "announced_at": package.announced_at.isoformat() if package.announced_at else None,
                    "is_processed": True
                })
            except Exception as pkg_error:
                print(f"❌ Error procesando paquete {package.id}: {str(pkg_error)}")
                import traceback
                traceback.print_exc()
                continue  # Saltar este paquete y continuar con el siguiente

        if len(results) == 0:
            return {
                "success": False,
                "message": "NOT_FOUND",
                "results": []
            }

        # Para compatibilidad con el frontend, devolver el primer resultado directamente
        # Regla: si la query es tracking_code y existe un resultado de tipo 'package', priorizarlo
        first_result = results[0]
        try:
            if query_type.get("type") == "tracking_code":
                pkg_result = next((r for r in results if r.get("type") == "package"), None)
                if pkg_result:
                    first_result = pkg_result
        except Exception:
            pass
        
        print(f"🔍 Resultado encontrado: {first_result['type']} - {first_result.get('guide_number', 'N/A')}")
        print(f"📦 ID del resultado: {first_result.get('id', 'N/A')}")

        # Determinar si mostrar formulario de consulta (valores por defecto seguros)
        should_show_inquiry_form = query_type.get("type") == "tracking_code"
        has_pending_messages = False
        history = []

        # Bloque robusto para que NUNCA se rompa la respuesta
        try:
            # Verificar si hay mensajes pendientes para este tracking code
            if first_result.get("tracking_code"):
                pending_messages = db.query(Message).filter(
                    Message.tracking_code == first_result["tracking_code"],
                    Message.message_type == MessageType.CONSULTA,
                    Message.status == MessageStatus.ABIERTO
                ).count()
                has_pending_messages = pending_messages > 0

            # El formulario de consulta solo se muestra si NO hay mensajes pendientes
            should_show_inquiry_form = should_show_inquiry_form and not has_pending_messages

            # Crear línea de tiempo
            if first_result["type"] == "announcement":
                announcement = db.query(PackageAnnouncementNew).filter(
                    PackageAnnouncementNew.id == first_result["id"]
                ).first()

            # Siempre mostrar el evento de anuncio
            history.append(normalize_history_event({
                "status": "ANUNCIADO",
                "description": "Paquete anunciado",
                "timestamp": first_result["announced_at"],
                "details": {
                    "customer_name": first_result["customer_name"],
                    "customer_phone": first_result["customer_phone"],
                    "guide_number": first_result["guide_number"],
                    "tracking_code": first_result["tracking_code"]
                }
            }))

            # Si el anuncio está procesado, obtener el paquete real de la forma más confiable
            if announcement and announcement.is_processed:
                package = None
                # 1) Vía enlace directo package_id si existe (preferida)
                try:
                    if getattr(announcement, 'package_id', None):
                        package = db.query(Package).filter(Package.id == announcement.package_id).first()
                except Exception:
                    package = None

                # 2) Fallback por guide_number
                if not package:
                    package = db.query(Package).filter(Package.tracking_number == announcement.guide_number).first()

                # 3) Fallback por tracking_code exacto
                if not package:
                    package = db.query(Package).filter(Package.tracking_number == announcement.tracking_code).first()

                if package:
                    # Obtener el historial del paquete
                    # Obtener historial del paquete usando Integer directamente
                    package_history = db.query(PackageHistory).filter(
                        PackageHistory.package_id == package.id
                    ).order_by(PackageHistory.changed_at.asc()).all()

                    # Convertir el historial del paquete al formato esperado por el frontend
                    for hist_entry in package_history:
                        # Saltar el estado ANNOUNCED ya que ya lo mostramos arriba
                        if hist_entry.new_status == "ANUNCIADO":
                            continue

                        # Determinar la descripción según el estado
                        if hist_entry.new_status == "RECIBIDO":
                            description = "Paquete recibido"

                            # Obtener el nombre del usuario que recibió el paquete
                            received_by = "Sistema"
                            if hist_entry.changed_by:
                                if hist_entry.changed_by.startswith("user_"):
                                    try:
                                        from app.models.user import User
                                        user_id = int(hist_entry.changed_by.replace("user_", ""))
                                        user = db.query(User).filter(User.id == user_id).first()
                                        if user:
                                            received_by = user.username or user.first_name or "Usuario"
                                    except (ValueError, AttributeError):
                                        received_by = hist_entry.changed_by
                                else:
                                    received_by = hist_entry.changed_by

                            details = {
                                "received_by": received_by,
                                "location": "PAPYRUS"
                            }
                            if hist_entry.additional_data:
                                details.update(hist_entry.additional_data)

                            # Agregar información de imágenes si existen
                            if package:
                                from app.models.file_upload import FileUpload
                                from app.services.s3_service import S3Service
                                from app.models.file_upload import FileType
                                from sqlalchemy import or_
                                
                                # Buscar imágenes de recepción específicamente
                                # Buscar por múltiples criterios para mayor compatibilidad
                                images = db.query(FileUpload).filter(
                                    or_(
                                        # Búsqueda principal: por package_id
                                        FileUpload.package_id == package.id,
                                        # Búsqueda alternativa: por tracking_code en s3_key (para imágenes existentes)
                                        FileUpload.s3_key.like(f"%{announcement.tracking_code}%"),
                                        # Búsqueda adicional: por guide_number en s3_key
                                        FileUpload.s3_key.like(f"%{announcement.guide_number}%")
                                    ),
                                    FileUpload.file_type == FileType.IMAGEN,  # Usar IMAGEN en lugar de RECEPTION_IMAGE
                                    # Filtrar solo archivos de imagen (no metadata.json)
                                    or_(
                                        FileUpload.filename.like('%.jpg'),
                                        FileUpload.filename.like('%.jpeg'),
                                        FileUpload.filename.like('%.png'),
                                        FileUpload.filename.like('%.webp')
                                    )
                                ).all()

                                print(f"🔍 Buscando imágenes para paquete {package.id}: {len(images)} encontradas")
                                print(f"🔍 Criterios de búsqueda:")
                                print(f"   - package_id: {package.id}")
                                print(f"   - tracking_code: {announcement.tracking_code}")
                                print(f"   - guide_number: {announcement.guide_number}")
                                
                                # Debug: mostrar todas las imágenes encontradas
                                for img in images:
                                    print(f"   📷 Imagen encontrada: {img.filename} | s3_key: {img.s3_key}")

                                if images:
                                    details["has_images"] = True
                                    details["images_count"] = len(images)
                                    details["images"] = []
                                    try:
                                        s3_service = S3Service()
                                        for img in images:
                                            if img.s3_key:
                                                try:
                                                    print(f"🖼️ Procesando imagen: {img.filename}")
                                                    print(f"🔑 S3 Key: {img.s3_key}")
                                                    
                                                    # OPCIÓN 1 SIMPLIFICADA: Usar endpoint de fallback directo
                                                    filename = img.filename
                                                    print(f"🔍 Procesando imagen: {filename}")
                                                    
                                                    # Construir s3_key basado en el filename
                                                    if filename and '_' in filename:
                                                        parts = filename.split('_')
                                                        if len(parts) >= 2:
                                                            date_part = parts[1]  # YYYYMMDD
                                                            if len(date_part) == 8:
                                                                year = date_part[:4]
                                                                month = date_part[4:6]
                                                                day = date_part[6:8]
                                                                s3_key = f"{year}/{month}/{day}/packages/announcement_{announcement.tracking_code}/receive/{filename}"
                                                            else:
                                                                s3_key = f"packages/announcement_{announcement.tracking_code}/receive/{filename}"
                                                        else:
                                                            s3_key = f"packages/announcement_{announcement.tracking_code}/receive/{filename}"
                                                    else:
                                                        s3_key = f"packages/announcement_{announcement.tracking_code}/receive/{filename}"
                                                    
                                                    # OPCIÓN 1: Usar endpoint de imágenes mejorado con retry logic
                                                    secure_url = f"/api/images/{img.id}"
                                                    print(f"✅ URL segura generada (Opción 1): {secure_url}")
                                                    print(f"🔍 Imagen ID: {img.id}, Filename: {img.filename}")
                                                    
                                                    details["images"].append({
                                                        "id": str(img.id),
                                                        "filename": img.filename,
                                                        "s3_key": img.s3_key,
                                                        "s3_url": secure_url,  # URL del endpoint mejorado con retry logic
                                                        "uploaded_at": img.created_at.isoformat() if img.created_at else None
                                                    })
                                                    
                                                except Exception as url_error:
                                                    print(f"❌ Error generando URL presignada para {img.filename}: {str(url_error)}")
                                                    # Incluir imagen sin URL para debugging
                                                    details["images"].append({
                                                        "id": str(img.id),
                                                        "filename": img.filename,
                                                        "s3_key": img.s3_key,
                                                        "s3_url": None,
                                                        "error": str(url_error),
                                                        "uploaded_at": img.created_at.isoformat() if img.created_at else None
                                                    })
                                            else:
                                                print(f"⚠️ Imagen sin s3_key: {img.filename}")
                                                details["images"].append({
                                                    "id": str(img.id),
                                                    "filename": img.filename,
                                                    "s3_key": None,
                                                    "s3_url": None,
                                                    "error": "No S3 key found",
                                                    "uploaded_at": img.created_at.isoformat() if img.created_at else None
                                                })
                                    except Exception as s3_error:
                                        print(f"❌ Error general procesando imágenes: {str(s3_error)}")
                                        # Fallback: include images without URLs
                                        details["images"] = [
                                            {
                                                "id": str(img.id),
                                                "filename": img.filename,
                                                "s3_key": img.s3_key,
                                                "s3_url": None,
                                                "uploaded_at": img.created_at.isoformat() if img.created_at else None
                                            }
                                            for img in images
                                        ]
                                else:
                                    print(f"ℹ️ No se encontraron imágenes para el paquete {package.id}")
                                    details["has_images"] = False
                                    details["images_count"] = 0
                        elif hist_entry.new_status == "ENTREGADO":
                            description = "Paquete entregado"
                            details = {
                                "delivered_to": "Cliente"
                            }
                            if hist_entry.additional_data:
                                details.update(hist_entry.additional_data)
                        elif hist_entry.new_status == "CANCELADO":
                            description = "Paquete cancelado"
                            details = {
                                "reason": hist_entry.observations or "Cancelado por administrador"
                            }
                        else:
                            description = f"Estado: {hist_entry.new_status}"
                            details = {}

                        history.append(normalize_history_event({
                            "status": hist_entry.new_status,
                            "description": description,
                            "timestamp": hist_entry.changed_at.isoformat() if hist_entry.changed_at else None,
                            "details": details
                        }))
    
                    # Agregar eventos 'RECIBIDO' si el estado actual del paquete lo indica
                    try:
                        history = add_missing_history_events(package, history)
                    except Exception:
                        pass

                    # Intento adicional de consistencia
                    try:
                        history = add_missing_history_events(package, history)
                    except Exception:
                        pass

        except Exception as processing_error:
            # Loguear y continuar con respuesta mínima para no romper UX
            print(f"❌ Error procesando detalles/historial en búsqueda pública: {str(processing_error)}")
            import traceback
            traceback.print_exc()
            # Mantener defaults: history=[], has_pending_messages=False, should_show_inquiry_form según tipo

            # Fallback: si tenemos un anuncio procesado, intentar enriquecer el historial
            try:
                if first_result.get("type") == "announcement" and first_result.get("is_processed"):
                    from sqlalchemy import or_
                    fallback_guide = first_result.get("guide_number")
                    fallback_track = first_result.get("tracking_code")
                    pkg_fallback = db.query(Package).filter(
                        or_(
                            Package.tracking_number == fallback_guide,
                            Package.tracking_number == fallback_track,
                            Package.guide_number == fallback_guide,
                            Package.guide_number == fallback_track
                        )
                    ).first()
                    if pkg_fallback:
                        # Asegurar al menos los eventos que faltan según el estado actual
                        history[:] = add_missing_history_events(pkg_fallback, history)
            except Exception as fb_err:
                print(f"ℹ️ Fallback de historial no aplicado: {str(fb_err)}")

        if first_result["type"] == "package":
            # Handle package history directly
            package = None
            try:
                package = db.query(Package).filter(Package.id == int(first_result["id"])).first()
            except Exception:
                package = db.query(Package).filter(Package.tracking_number == first_result.get("tracking_number") ).first()

            if package:
                # Mostrar el evento de anuncio primero
                history.append(normalize_history_event({
                    "status": "ANUNCIADO",
                    "description": "Paquete anunciado",
                    "timestamp": package.announced_at.isoformat() if package.announced_at else None,
                    "details": {
                        "customer_name": first_result["customer_name"],
                        "customer_phone": first_result["customer_phone"],
                        "guide_number": package.tracking_number,
                        "tracking_code": package.tracking_number
                    }
                }))

                # Obtener el historial del paquete
                package_history = db.query(PackageHistory).filter(
                    PackageHistory.package_id == package.id
                ).order_by(PackageHistory.changed_at.asc()).all()

                # Convertir el historial del paquete al formato esperado por el frontend
                for hist_entry in package_history:
                    # Determinar la descripción según el estado
                    if hist_entry.new_status == "RECIBIDO":
                        description = "Paquete recibido"

                        # Obtener el nombre del usuario que recibió el paquete
                        received_by = "Sistema"
                        if hist_entry.changed_by:
                            if hist_entry.changed_by.startswith("user_"):
                                try:
                                    from app.models.user import User
                                    user_id = int(hist_entry.changed_by.replace("user_", ""))
                                    user = db.query(User).filter(User.id == user_id).first()
                                    if user:
                                        received_by = user.username or user.first_name or "Usuario"
                                except (ValueError, AttributeError):
                                    received_by = hist_entry.changed_by
                            else:
                                received_by = hist_entry.changed_by

                        details = {
                            "received_by": received_by,
                            "location": "PAPYRUS"
                        }
                        if hist_entry.additional_data:
                            details.update(hist_entry.additional_data)

                        # Agregar información de imágenes si existen
                        from app.models.file_upload import FileUpload
                        from app.services.s3_service import S3Service
                        from sqlalchemy import or_
                        from app.models.file_upload import FileType
                        
                        # Buscar imágenes por múltiples criterios para mayor compatibilidad
                        images = db.query(FileUpload).filter(
                            or_(
                                # Búsqueda principal: por package_id
                                FileUpload.package_id == package.id,
                                # Búsqueda alternativa: por tracking_number en s3_key
                                FileUpload.s3_key.like(f"%{package.tracking_number}%")
                            ),
                            FileUpload.file_type == FileType.IMAGEN,  # Usar IMAGEN en lugar de RECEPTION_IMAGE
                            # Filtrar solo archivos de imagen (no metadata.json)
                            or_(
                                FileUpload.filename.like('%.jpg'),
                                FileUpload.filename.like('%.jpeg'),
                                FileUpload.filename.like('%.png'),
                                FileUpload.filename.like('%.webp')
                            )
                        ).all()

                        if images:
                            details["has_images"] = True
                            details["images_count"] = len(images)
                            details["images"] = []
                            try:
                                s3_service = S3Service()
                                for img in images:
                                    # OPCIÓN 1: Usar endpoint interno en lugar de URL directa de S3
                                    secure_url = f"/api/images/{img.id}"
                                    print(f"✅ URL segura generada (Opción 1): {secure_url}")
                                    print(f"🔍 Imagen ID: {img.id}, Filename: {img.filename}")

                                    details["images"].append({
                                        "id": str(img.id),
                                        "filename": img.filename,
                                        "s3_url": secure_url,  # URL del endpoint mejorado con retry logic
                                        "uploaded_at": img.created_at.isoformat() if img.created_at else None
                                    })
                            except Exception as s3_error:
                                # Fallback: usar endpoints internos
                                details["images"] = [
                                    {
                                        "id": str(img.id),
                                        "filename": img.filename,
                                        "s3_url": f"/api/images/{img.id}",  # Endpoint interno como fallback
                                        "uploaded_at": img.created_at.isoformat() if img.created_at else None
                                    }
                                    for img in images
                                ]
                        else:
                            details["has_images"] = False
                            details["images_count"] = 0
                    elif hist_entry.new_status == "ENTREGADO":
                        description = "Paquete entregado"
                        details = {
                            "delivered_to": "Cliente"
                        }
                        if hist_entry.additional_data:
                            details.update(hist_entry.additional_data)
                    elif hist_entry.new_status == "CANCELADO":
                        description = "Paquete cancelado"
                        details = {
                            "reason": hist_entry.observations or "Cancelado por administrador"
                        }
                    else:
                        description = f"Estado: {hist_entry.new_status}"
                        details = {}

                    history.append(normalize_history_event({
                        "status": hist_entry.new_status,
                        "description": description,
                        "timestamp": hist_entry.changed_at.isoformat() if hist_entry.changed_at else None,
                        "details": details
                    }))

        # Asegurar consistencia mínima del historial según estado actual reportado
        try:
            reported_status = str(first_result.get("status") or "").upper()
            statuses_in_history = {entry.get("status") for entry in history}
            if reported_status == "RECIBIDO" and "RECIBIDO" not in statuses_in_history:
                # Agregar evento recibido con timestamp razonable
                received_ts = None
                try:
                    if 'package' in locals() and package and getattr(package, 'received_at', None):
                        received_ts = package.received_at.isoformat()
                except Exception:
                    received_ts = None
                if not received_ts:
                    received_ts = get_colombia_now().isoformat()
                history.append({
                    "status": "RECIBIDO",
                    "description": "Paquete recibido",
                    "timestamp": received_ts,
                    "details": {
                        "received_by": "Sistema",
                        "location": "PAPYRUS"
                    }
                })
        except Exception:
            pass

        # Determinar estado actual preferentemente desde el paquete real si existe
        try:
            final_status = first_result.get("status", "ANUNCIADO")
            # Priorizar estado del package real si existe
            if 'package' in locals() and package:
                if hasattr(package, 'status'):
                    final_status = package.status.value if hasattr(package.status, 'value') else str(package.status)
            # Si no hay package pero el anuncio está procesado, elevar al menos RECIBIDO
            elif 'announcement' in locals() and announcement and getattr(announcement, 'is_processed', False):
                final_status = 'RECIBIDO'
        except Exception:
            final_status = first_result.get("status", "ANUNCIADO")

        # Determinar si debemos mostrar el historial en frontend
        try:
            has_received_event = any((h.get("status") == "RECIBIDO") for h in history)
        except Exception:
            has_received_event = False
        final_should_show_history = (query_type.get("type") == "tracking_code") or has_received_event

        return {
            "success": True,
            "message": f"Se encontraron {len(results)} resultados",
            "results": [normalize_package_item(r) for r in results],
            "announcement": normalize_package_item(first_result) if first_result["type"] == "announcement" else None,
            "package": normalize_package_item(first_result) if first_result["type"] == "package" else None,
            "query_type": {
                "type": query_type.get("type"),
                "should_show_history": final_should_show_history,
                "should_show_inquiry_form": should_show_inquiry_form
            },
            "inquiry_info": {
                "has_existing_email": False,
                "registered_email": None,
                "has_pending_messages": has_pending_messages
            },
            "current_status": normalize_status(final_status),
            "history": [normalize_history_event(h) for h in history]
        }

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ ERROR EN BÚSQUEDA DE PAQUETE:")
        print(f"   Query: {query}")
        print(f"   Error: {str(e)}")
        print(f"   Traceback completo:")
        print(error_trace)
        
        return {
            "success": False,
            "message": f"Error en la búsqueda: {str(e)}",
            "error_details": str(e),
            "results": []
        }


def add_missing_history_events(package: Package, history: List[Dict]) -> List[Dict]:
    """Agregar eventos de historial faltantes basados en el estado actual del paquete"""

    # Verificar si falta el evento RECEIVED
    has_received = any(h['status'] == 'RECIBIDO' for h in history)
    if package.status == PackageStatus.RECIBIDO and not has_received:
        # Usar received_at si existe, sino usar la hora actual como fallback
        timestamp = package.received_at if package.received_at else get_colombia_now()
        history.append({
            "status": "RECIBIDO",
            "description": "Paquete recibido",
            "timestamp": timestamp.isoformat(),
            "details": {
                "received_by": "Sistema",
                "location": "PAPYRUS"
            }
        })

    # Verificar si falta el evento DELIVERED
    has_delivered = any(h['status'] == 'ENTREGADO' for h in history)
    if package.status == PackageStatus.ENTREGADO and not has_delivered:
        # Usar delivered_at si existe, sino usar la hora actual como fallback
        timestamp = package.delivered_at if package.delivered_at else get_colombia_now()
        history.append({
            "status": "ENTREGADO",
            "description": "Paquete entregado",
            "timestamp": timestamp.isoformat(),
            "details": {
                "delivered_to": "Cliente"
            }
        })

    # Ordenar por timestamp
    history.sort(key=lambda x: x['timestamp'] or '')

    return history


def determine_query_type(query: str) -> dict:
    """
    Determinar el tipo de consulta basado en el formato del query
    """
    import re

    # Si es exactamente 4 caracteres alfanuméricos, es un tracking code
    if re.match(r'^[A-Z0-9]{4}$', query.upper()):
        return {"type": "tracking_code"}

    # Si parece un número de guía (más largo, con letras y números)
    if re.match(r'^[A-Z0-9]{5,}$', query.upper()):
        return {"type": "guide_number"}

    # Si parece un teléfono (solo números, con posibles espacios/guiones)
    if re.match(r'^[\d\s\-\+\(\)]+$', query):
        return {"type": "phone"}

    # Si contiene letras y espacios, probablemente es un nombre
    if re.match(r'^[A-Za-z\s]+$', query):
        return {"type": "name"}

    # Default: tratar como guía
    return {"type": "guide_number"}

# ========================================
# ENDPOINTS DE CONSULTAS DE CLIENTES
# ========================================

@router.post("/api/messages/customer-inquiry", status_code=status.HTTP_201_CREATED)
async def create_customer_inquiry(
    inquiry: CustomerInquiryCreate,
    db: Session = Depends(get_db)
):
    """Crear consulta de cliente (pública) - Endpoint para el formulario de búsqueda"""
    try:
        # Crear nuevo mensaje
        message = Message(
            sender_name=inquiry.customer_name,
            sender_phone=inquiry.customer_phone,
            sender_email=inquiry.customer_email,
            tracking_code=inquiry.package_tracking_code,
            subject=inquiry.subject,
            content=inquiry.content,
            message_type=MessageType.CONSULTA,
            status=MessageStatus.ABIERTO,
            priority=MessagePriority.MEDIA
        )

        db.add(message)
        db.commit()
        db.refresh(message)

        # ========================================
        # ACTUALIZAR EMAIL DEL CLIENTE SI NO LO TIENE
        # ========================================
        if inquiry.customer_email and inquiry.package_tracking_code:
            try:
                # Buscar el paquete por tracking_code
                package = db.query(Package).filter(
                    or_(
                        Package.tracking_number == inquiry.package_tracking_code,
                        Package.access_code == inquiry.package_tracking_code
                    )
                ).first()
                
                # Si no se encuentra paquete, buscar en anuncios
                if not package:
                    announcement = db.query(PackageAnnouncementNew).filter(
                        or_(
                            PackageAnnouncementNew.tracking_code == inquiry.package_tracking_code,
                            PackageAnnouncementNew.guide_number == inquiry.package_tracking_code
                        )
                    ).first()
                    
                    if announcement and announcement.customer_id:
                        # Actualizar email del cliente del anuncio
                        customer = db.query(Customer).filter(
                            Customer.id == announcement.customer_id
                        ).first()
                        
                        if customer and not customer.email:
                            customer.email = inquiry.customer_email
                            customer.updated_at = get_colombia_now()
                            db.commit()
                            print(f"✅ Email actualizado para cliente {customer.id} desde anuncio: {inquiry.customer_email}")
                
                # Si existe paquete y tiene cliente asociado
                elif package and package.customer_id:
                    customer = db.query(Customer).filter(
                        Customer.id == package.customer_id
                    ).first()
                    
                    if customer and not customer.email:
                        customer.email = inquiry.customer_email
                        customer.updated_at = get_colombia_now()
                        db.commit()
                        print(f"✅ Email actualizado para cliente {customer.id} desde paquete: {inquiry.customer_email}")
                        
            except Exception as email_error:
                # No fallar la consulta por esto, solo registrar el error
                print(f"⚠️ Error actualizando email del cliente: {email_error}")
                import traceback
                traceback.print_exc()
                # Continuar normalmente

        return {
            "message": "Consulta enviada exitosamente",
            "id": str(message.id),
            "status": "pending"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear consulta: {str(e)}"
        )

@router.get("/api/messages/check-inquiry-exists")
async def check_inquiry_exists(
    customer_email: str = None,
    package_tracking_code: str = None,
    db: Session = Depends(get_db)
):
    """Verificar si ya existe una consulta previa para este email y paquete"""
    try:
        if not customer_email or not package_tracking_code:
            return {"exists": False}

        # Buscar consultas existentes con el mismo email y código de tracking
        existing_inquiry = db.query(Message).filter(
            Message.sender_email == customer_email,
            Message.tracking_code == package_tracking_code,
            Message.message_type == MessageType.CONSULTA
        ).first()

        return {
            "exists": existing_inquiry is not None,
            "inquiry_id": str(existing_inquiry.id) if existing_inquiry else None,
            "created_at": existing_inquiry.created_at.isoformat() if existing_inquiry else None,
            "has_pending": existing_inquiry.status == MessageStatus.ABIERTO if existing_inquiry else False
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al verificar consulta existente: {str(e)}"
        )

@router.get("/api/messages/tracking/{tracking_code}")
async def get_messages_by_tracking_code(
    tracking_code: str,
    db: Session = Depends(get_db)
):
    """Obtener mensajes por código de tracking (público - información básica)"""
    try:
        # Buscar mensajes para este código de tracking
        messages = db.query(Message).filter(
            Message.tracking_code == tracking_code,
            Message.message_type == MessageType.CONSULTA
        ).order_by(Message.created_at.desc()).all()

        # Convertir a formato público (sin información sensible)
        public_messages = []
        for msg in messages:
            # Determinar el estado para mostrar
            if msg.status == MessageStatus.ABIERTO:
                status_text = "PENDIENTE"
                status_class = "bg-yellow-100 text-yellow-800"
            elif msg.status == MessageStatus.RESPONDIDO:
                status_text = "RESUELTO"
                status_class = "bg-green-100 text-green-800"
            elif msg.status == MessageStatus.CERRADO:
                status_text = "CERRADO"
                status_class = "bg-gray-100 text-gray-800"
            else:
                status_text = "PENDIENTE"
                status_class = "bg-yellow-100 text-yellow-800"

            public_messages.append({
                "id": str(msg.id),
                "customer_name": msg.sender_name or "Cliente",
                "content": msg.content,
                "status": msg.status.value if hasattr(msg.status, 'value') else str(msg.status),
                "status_text": status_text,
                "status_class": status_class,
                "created_at": msg.created_at.isoformat() if msg.created_at else None,
                "answered_at": msg.answered_at.isoformat() if msg.answered_at else None,
                "admin_response": msg.answer if msg.answer else None,
                "admin_username": msg.answered_by_user.username if msg.answered_by_user and hasattr(msg.answered_by_user, 'username') else None
            })

        return public_messages

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener mensajes del tracking: {str(e)}"
        )

@router.get("/api/messages/check-tracking-inquiries")
async def check_tracking_inquiries(
    package_tracking_code: str = None,
    db: Session = Depends(get_db)
):
    """Verificar si ya existen consultas para este código de tracking"""
    try:
        if not package_tracking_code:
            return {"exists": False, "count": 0}

        # Buscar todas las consultas existentes para este código de tracking
        existing_inquiries = db.query(Message).filter(
            Message.tracking_code == package_tracking_code,
            Message.message_type == MessageType.CONSULTA
        ).all()

        # Si hay consultas, devolver la más reciente y información de estados
        if existing_inquiries:
            latest_inquiry = max(existing_inquiries, key=lambda x: x.created_at)

            # Verificar si hay mensajes pendientes y no leídos
            has_pending = any(inquiry.status == MessageStatus.ABIERTO for inquiry in existing_inquiries)
            has_unread = any((not inquiry.is_read) for inquiry in existing_inquiries)

            return {
                "exists": True,
                "count": len(existing_inquiries),
                "has_pending": has_pending,
                "has_unread": has_unread,
                "latest_inquiry": {
                    "id": str(latest_inquiry.id),
                    "customer_email": latest_inquiry.sender_email,
                    "status": latest_inquiry.status.value if hasattr(latest_inquiry.status, 'value') else str(latest_inquiry.status),
                    "created_at": latest_inquiry.created_at.isoformat()
                }
            }

        return {
            "exists": False,
            "count": 0,
            "latest_inquiry": None
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al verificar consultas del tracking: {str(e)}"
        )

# ========================================
# HEALTH CHECKS Y UTILIDADES
# ========================================

# Health check movido a main.py para evitar duplicados

# Eliminado health duplicado: /api/health se gestiona en api.py

@router.get("/api/test-s3")
async def test_s3_endpoint():
    """Test S3 service endpoint"""
    try:
        s3_service = S3Service()
        test_key = "paquetes-recibidos-imagenes/packages/27/reception_images/27_reception_image_1.jpg"
        presigned_url = s3_service.generate_presigned_url(test_key)
        return {
            "success": True,
            "presigned_url": presigned_url,
            "test_key": test_key
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

