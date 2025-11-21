from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Package, Message
from app.dependencies import get_current_active_user_from_cookies
from app.utils.auth_context import get_auth_context_from_request, get_auth_context_required
from datetime import datetime

router = APIRouter()
from app.utils.template_loader import get_templates
templates = get_templates()

@router.get("/")
async def root(request: Request):
    return RedirectResponse(url="/announce", status_code=302)

@router.get("/test")
async def test_endpoint():
    """Endpoint de prueba para verificar que el servidor esté funcionando"""
    return {"status": "ok", "message": "Servidor funcionando correctamente"}

@router.get("/announce-test")
async def announce_test():
    """Endpoint de prueba para la página de announce"""
    return {"status": "ok", "message": "Endpoint announce funcionando", "path": "/announce"}

# NOTA: Ruta /announce movida a public.py (ruta pública)

@router.get("/announce-simple")
async def announce_simple_page(request: Request):
    """Página de announce simplificada para pruebas"""
    try:
        context = {
            "is_authenticated": False,
            "user": None,
            "user_name": None,
            "user_role": None,
            "package_announcements": [],
            "current_path": str(request.url.path),
            "query_params": dict(request.query_params),
            "method": request.method,
            "request": request,
        }
        return templates.TemplateResponse("announce/announce_simple.html", context)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Error cargando template simplificado: {str(e)}",
                "error_type": "template_error"
            }
        )

@router.get("/test-base")
async def test_base_template(request: Request):
    """Prueba del template base con comentarios corregidos"""
    try:
        context = {
            "is_authenticated": False,
            "user": None,
            "user_name": None,
            "user_role": None,
            "current_path": str(request.url.path),
            "query_params": dict(request.query_params),
            "method": request.method,
            "request": request,
        }
        return templates.TemplateResponse("announce/announce.html", context)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Error cargando template base: {str(e)}",
                "error_type": "template_error"
            }
        )

@router.get("/test-static")
async def test_static_files():
    """Prueba de archivos estáticos"""
    return {
        "status": "ok",
        "message": "Archivos estáticos disponibles",
        "files": {
            "config_js": "/static/js/config.js",
            "form_validation_js": "/static/js/form-validation.js",
            "main_js": "/static/js/main.js",
            "favicon": "/static/images/favicon.png",
            "logo": "/static/images/logo.png"
        }
    }

@router.get("/demo/error-components")
async def demo_error_components(request: Request):
    """Página de demostración de componentes de error"""
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("demo_error_components.html", context)

@router.get("/demo/error-simple")
async def demo_error_simple(request: Request):
    """Página de demostración simplificada de componentes de error"""
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("demo_error_simple.html", context)

@router.get("/demo/javascript-errors")
async def demo_javascript_errors(request: Request):
    """Página de demostración del manejador de errores de JavaScript"""
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("demo_javascript_errors.html", context)

@router.get("/demo/native-validation")
async def demo_native_validation(request: Request):
    """Página de demostración del manejador de validación nativa del navegador"""
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("demo_native_validation.html", context)

@router.get("/demo/package-announcement")
async def demo_package_announcement(request: Request):
    """Página de demostración del formulario de anuncio de paquetes con interceptor de validación"""
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("demo_package_announcement.html", context)

@router.get("/test/validation-simple")
async def test_validation_simple(request: Request):
    """Página de prueba simple para validación de formularios"""
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("test_validation_simple.html", context)

@router.get("/test/announce-validation")
async def test_announce_validation(request: Request):
    """Página de prueba para validación de formularios de anuncios"""
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("test_announce_validation.html", context)

@router.get("/test/aggressive-validation")
async def test_aggressive_validation(request: Request):
    """Página de prueba para validación AGRESIVA de formularios"""
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("test_aggressive_validation.html", context)

@router.get("/demo/tooltip-error")
async def demo_tooltip_error(request: Request):
    """Página de demostración del sistema de tooltip de error"""
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("demo_tooltip_error.html", context)

@router.get("/demo/terminos-condiciones")
async def demo_terminos_condiciones(request: Request):
    """Página de demostración de validación de términos y condiciones"""
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("test_terminos_condiciones.html", context)

@router.get("/debug/terminos")
async def debug_terminos(request: Request):
    """Página de debug para validación de términos y condiciones"""
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("debug_terminos.html", context)

@router.get("/test/terms-validation")
async def test_terms_validation(request: Request):
    """Página de prueba específica para validación de términos y condiciones"""
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("test_terms_validation.html", context)

@router.get("/test/form-submission")
async def test_form_submission(request: Request):
    """Página de prueba para validación + envío de formulario"""
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("test_form_submission.html", context)

@router.get("/customers")
async def customers_page(request: Request):
    return RedirectResponse(url="/", status_code=302)

# NOTA: Ruta /search movida a public.py (ruta pública)
# @router.get("/search") - ELIMINADA (duplicada)

# Ruta duplicada de /messages removida. La definición oficial está en app/routes/public.py


# NOTA: Rutas /login y /auth/login movidas a public.py (rutas públicas)
# @router.get("/login") - ELIMINADA (duplicada)
# @router.get("/auth/login") - ELIMINADA (duplicada)

@router.get("/auth/register")
async def auth_register_page(request: Request):
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("auth/register.html", context)

@router.get("/auth/forgot-password")
async def auth_forgot_password_page(request: Request):
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("auth/forgot-password.html", context)

@router.get("/auth/reset-password")
async def auth_reset_password_page(request: Request):
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("auth/reset-password.html", context)


@router.get("/admin/users")
async def admin_users_page(request: Request, current_user: User = Depends(get_current_active_user_from_cookies), db: Session = Depends(get_db)):
    if current_user.role.value != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo administradores pueden acceder a esta página."
        )
    
    context = get_auth_context_required(request)
    context["user"] = current_user
    
    try:
        users = db.query(User).order_by(User.created_at.desc()).all()
        context["users"] = users
    finally:
        db.close()
    
    return templates.TemplateResponse("admin/users.html", context)

@router.get("/logout")
async def logout_page(request: Request):
    response = RedirectResponse(url="/auth/login", status_code=302)
    response.delete_cookie("access_token")
    response.delete_cookie("user_id")
    response.delete_cookie("user_name")
    response.delete_cookie("user_role")
    return response

@router.get("/help")
async def help_page(request: Request):
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("general/help.html", context)


@router.get("/cookies")
async def cookies_page(request: Request):
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("announce/announce.html", context)

@router.get("/policies")
async def policies_page(request: Request):
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("announce/announce.html", context)


@router.get("/admin")
async def admin_page(request: Request, current_user: User = Depends(get_current_active_user_from_cookies)):
    """Dashboard administrativo mejorado con estadísticas completas"""
    context = get_auth_context_required(request)
    context["user"] = current_user
    
    # Verificar que sea admin o operador
    if current_user.role.value not in ["ADMIN", "OPERADOR"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo administradores y operadores pueden acceder."
        )
    
    return templates.TemplateResponse("admin/dashboard_enhanced.html", context)








@router.get("/packages")
async def packages_page(request: Request, current_user: User = Depends(get_current_active_user_from_cookies)):
    context = get_auth_context_from_request(request)
    context["user"] = current_user

    if not context["is_authenticated"]:
        return RedirectResponse(url="/auth/login?redirect=/packages", status_code=302)

    # Agregar configuración de tarifas desde .env
    from app.config import settings
    context["app_config"] = {
        "rates": {
            "normal": settings.base_delivery_rate_normal,
            "extra_dimensioned": settings.base_delivery_rate_extra_dimensioned,
            "storage_per_day": settings.base_storage_rate
        },
        "development_url": settings.development_url,
        "production_url": settings.production_url
    }

    return templates.TemplateResponse("packages/packages.html", context)

@router.get("/receive")
async def receive_package_page(request: Request):
    # Verificar autenticación manualmente para vistas web
    try:
        # Intentar obtener usuario de cookies
        from app.dependencies import get_current_user_from_cookies
        from app.database import get_db
        from sqlalchemy.orm import Session

        db = next(get_db())
        user = get_current_user_from_cookies(request, db)

        if not user:
            return RedirectResponse(url="/auth/login?redirect=/receive", status_code=302)

        context = get_auth_context_from_request(request)
        context["user"] = user
        return templates.TemplateResponse("receive/receive.html", context)

    except Exception as e:
        print(f"Error en autenticación de /receive: {e}")
        return RedirectResponse(url="/auth/login?redirect=/receive", status_code=302)

@router.get("/packages/{package_id}")
async def package_detail_page(package_id: str, request: Request, db: Session = Depends(get_db)):
    context = get_auth_context_from_request(request)

    if not context["is_authenticated"]:
        return RedirectResponse(url="/auth/login?redirect=/packages/" + package_id, status_code=302)

    try:
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al cargar el paquete"
        )

@router.get("/announcements/{announcement_id}")
async def announcement_detail_page(announcement_id: str, request: Request, db: Session = Depends(get_db)):
    context = get_auth_context_from_request(request)

    if not context["is_authenticated"]:
        return RedirectResponse(url="/auth/login?redirect=/announcements/" + announcement_id, status_code=302)

    try:
        from app.models.announcement import PackageAnnouncement

        announcement = db.query(PackageAnnouncement).filter(PackageAnnouncement.id == announcement_id).first()

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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al cargar el anuncio"
        )

@router.get("/announcements/guide/{guide_number}")
async def announcement_detail_by_guide_page(guide_number: str, request: Request, db: Session = Depends(get_db)):
    context = {
        "request": request,
        "is_authenticated": True,
        "user": {"username": "jesus", "full_name": "Jesus Villalobos"}
    }

    try:
        from app.services.package_state_service import PackageStateService
        announcement = PackageStateService.get_announcement_by_guide_number(db, guide_number)

        if announcement:
            announcement_data = {
                "id": str(announcement.id),
                "customer_name": announcement.customer_name,
                "customer_phone": announcement.customer_phone,
                "guide_number": announcement.guide_number,
                "tracking_code": announcement.tracking_code,
                "is_processed": announcement.is_processed,
                "announced_at": announcement.announced_at,
                "status": announcement.status,
                "package_type": "normal",
                "package_condition": "ok",
                "observations": ""
            }

            if announcement.is_processed and announcement.package_id:
                package = PackageStateService.get_package_by_tracking_number(db, guide_number)
                if package:
                    announcement_data.update({
                        "package_type": package.package_type.value if package.package_type else "normal",
                        "package_condition": package.package_condition.value if package.package_condition else "ok",
                        # "observations": package.observations or ""  # Campo eliminado del modelo Package
                    })
        else:
            announcement_data = {
                "id": f"test-{guide_number}",
                "customer_name": "CLIENTE PRUEBA",
                "customer_phone": "3000000000",
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

    except Exception as e:
        # Return empty context for error cases
        context["announcement"] = None
        return templates.TemplateResponse("announce/announcement_detail.html", context)


@router.get("/profile")
async def profile_page(request: Request, current_user: User = Depends(get_current_active_user_from_cookies)):
    """Página de perfil del usuario actual"""
    context = get_auth_context_required(request)
    context["user"] = current_user

    return templates.TemplateResponse("users/profile.html", context)

@router.get("/profile/edit")
async def edit_profile_page(request: Request, current_user: User = Depends(get_current_active_user_from_cookies)):
    """Página de edición de perfil del usuario actual"""
    context = get_auth_context_required(request)
    context["user"] = current_user

    return templates.TemplateResponse("users/edit_profile_page.html", context)

@router.get("/profile/change-password")
async def change_password_page(request: Request, current_user: User = Depends(get_current_active_user_from_cookies)):
    """Página de cambio de contraseña"""
    context = get_auth_context_required(request)
    context["user"] = current_user

    return templates.TemplateResponse("users/change-password.html", context)


# Health check movido a main.py para evitar duplicados
@router.get("/debug/test-images")
async def test_images_page(request: Request):
    """Página de test para verificar imágenes de S3"""
    return templates.TemplateResponse("debug/test_images.html", {"request": request})