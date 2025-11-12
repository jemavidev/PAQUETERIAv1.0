# ========================================
# PAQUETES EL CLUB v4.0 - Router de Autenticación
# ========================================
# Archivo: CODE/LOCAL/src/app/routes/auth.py (siguiendo reglas de AGENTS.md)
# Versión: 1.0.0
# Fecha: 2025-01-24
# Autor: Equipo de Desarrollo
# ========================================

"""
Router de autenticación para PAQUETES EL CLUB
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional

from src.app.database import get_db
from src.app.dependencies import get_current_active_user
from src.app.models.user import User
from src.app.schemas.user import UserCreate, UserResponse
from src.app.services.user_service import UserService

# Crear router
router = APIRouter()

# Esquema OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/test")
async def test_endpoint():
    """Endpoint de prueba para verificar que el frontend puede hacer peticiones"""
    return {"success": True, "message": "Endpoint de prueba funcionando"}

@router.post("/test-login")
async def test_login_endpoint(request: Request):
    """Endpoint de prueba para simular el login del frontend"""
    try:
        print(f"DEBUG: Petición de prueba recibida en /api/auth/test-login")
        print(f"DEBUG: Headers: {dict(request.headers)}")
        
        # Obtener datos del formulario
        form_data = await request.form()
        print(f"DEBUG: Form data keys: {list(form_data.keys())}")
        
        username = form_data.get("username", "").strip()
        password = form_data.get("password", "").strip()
        
        print(f"DEBUG: Datos recibidos - username: {username}, password: {'*' * len(password)}")
        
        return {
            "success": True,
            "message": "✅ Prueba de login exitosa",
            "data": {
                "username": username,
                "password_length": len(password)
            }
        }
        
    except Exception as e:
        print(f"Error en test-login: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"❌ Error en prueba: {str(e)}"
        }


@router.post("/login")
async def login_frontend(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint de login específico para el frontend
    """
    try:
        print(f"DEBUG: Petición recibida en /api/auth/login")
        print(f"DEBUG: Headers: {dict(request.headers)}")
        
        # Obtener datos del formulario
        form_data = await request.form()
        print(f"DEBUG: Form data keys: {list(form_data.keys())}")
        
        username_or_email = form_data.get("username", "").strip()
        password = form_data.get("password", "").strip()
        
        # Debug: imprimir datos recibidos
        print(f"DEBUG: Datos recibidos - username: {username_or_email}, password: {'*' * len(password)}")
        
        if not username_or_email or not password:
            return JSONResponse({
                "success": False,
                "message": "❌ Usuario y contraseña son requeridos"
            }, status_code=400)
        
        # Buscar usuario por username o email
        from sqlalchemy import or_
        user = db.query(User).filter(
            or_(
                User.username == username_or_email.lower(),
                User.email == username_or_email.lower()
            )
        ).first()
        
        if not user:
            return JSONResponse({
                "success": False,
                "message": "❌ Credenciales incorrectas"
            }, status_code=401)
        
        if not user.is_active:
            return JSONResponse({
                "success": False,
                "message": "❌ Usuario inactivo. Contacta al administrador"
            }, status_code=400)
        
        # Verificar contraseña
        from app.utils.auth import verify_password
        if not verify_password(password, user.password_hash):
            return JSONResponse({
                "success": False,
                "message": "❌ Credenciales incorrectas"
            }, status_code=401)
        
        # Generar token JWT
        from app.utils.auth import create_user_token
        access_token = create_user_token(
            user_id=str(user.id),
            username=user.username,
            role=user.role.value if user.role else "user"
        )
        
        # Crear respuesta exitosa
        response = JSONResponse({
            "success": True,
            "message": "✅ Login exitoso",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "first_name": user.full_name.split()[0] if user.full_name else user.username,
                "last_name": " ".join(user.full_name.split()[1:]) if user.full_name and len(user.full_name.split()) > 1 else "",
                "role": user.role.value if user.role else "user"
            }
        })
        
        # Debug: imprimir respuesta
        print(f"DEBUG: Respuesta exitosa para usuario {user.username}")
        
        # Establecer cookies (24h) con flags de seguridad
        from app.config import settings
        secure_cookie = settings.environment != "development"
        response.set_cookie(
            "access_token",
            access_token,
            max_age=86400,  # 24 horas = 86400 segundos
            httponly=True,
            secure=secure_cookie,
            samesite="Lax"
        )
        response.set_cookie(
            "user_id",
            str(user.id),
            max_age=86400,  # 24 horas = 86400 segundos
            httponly=True,
            secure=secure_cookie,
            samesite="Lax"
        )
        response.set_cookie(
            "user_name",
            user.username,
            max_age=86400,  # 24 horas = 86400 segundos
            httponly=True,
            secure=secure_cookie,
            samesite="Lax"
        )
        response.set_cookie(
            "user_role",
            user.role.value if user.role else "user",
            max_age=86400,  # 24 horas = 86400 segundos
            httponly=True,
            secure=secure_cookie,
            samesite="Lax"
        )
        
        return response
        
    except Exception as e:
        # Fallback de desarrollo: permitir login sin BD si el entorno es development
        try:
            from app.config import settings as app_settings
        except Exception:
            app_settings = None

        if app_settings and app_settings.environment == "development":
            try:
                from app.utils.auth import create_user_token

                # Usar el username del formulario como identidad de desarrollo
                form = await request.form()
                dev_username = form.get("username", "devuser").strip() or "devuser"

                access_token = create_user_token(
                    user_id="1",
                    username=dev_username,
                    role="admin"
                )

                response = JSONResponse({
                    "success": True,
                    "message": "✅ Login de desarrollo (sin BD) exitoso",
                    "access_token": access_token,
                    "token_type": "bearer",
                    "user": {
                        "id": "1",
                        "username": dev_username,
                        "email": f"{dev_username}@local.dev",
                        "first_name": dev_username,
                        "last_name": "",
                        "role": "admin"
                    }
                })

                secure_cookie = app_settings.environment != "development"
                response.set_cookie(
                    "access_token",
                    access_token,
                    max_age=86400,  # 24 horas = 86400 segundos
                    httponly=True,
                    secure=secure_cookie,
                    samesite="Lax"
                )
                response.set_cookie(
                    "user_id",
                    "1",
                    max_age=86400,  # 24 horas = 86400 segundos
                    httponly=True,
                    secure=secure_cookie,
                    samesite="Lax"
                )
                response.set_cookie(
                    "user_name",
                    dev_username,
                    max_age=86400,  # 24 horas = 86400 segundos
                    httponly=True,
                    secure=secure_cookie,
                    samesite="Lax"
                )
                response.set_cookie(
                    "user_role",
                    "admin",
                    max_age=86400,  # 24 horas = 86400 segundos
                    httponly=True,
                    secure=secure_cookie,
                    samesite="Lax"
                )

                return response
            except Exception as fallback_error:
                print(f"Error en fallback de desarrollo: {fallback_error}")

        print(f"Error en login: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse({
            "success": False,
            "message": "❌ No pudimos procesar tu solicitud. Intenta nuevamente."
        }, status_code=500)


@router.post("/login-oauth")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Autenticar usuario y retornar token JWT
    """
    try:
        user_service = UserService()
        user = user_service.authenticate_user(db, form_data.username, form_data.password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario inactivo"
            )

        # Crear token de acceso
        from app.utils.auth import create_user_token
        access_token = create_user_token(str(user.id), user.username, user.role.value)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value if user.role else None
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.post("/reset-password")
async def reset_password(
    request_data: dict,
    db: Session = Depends(get_db)
):
    """
    Restablecer contraseña usando token
    """
    try:
        token = request_data.get("token", "").strip()
        new_password = request_data.get("new_password", "").strip()

        if not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token es requerido"
            )

        if not new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nueva contraseña es requerida"
            )

        if len(new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña debe tener al menos 8 caracteres"
            )

        # Verificar token
        from app.utils.auth import verify_reset_token
        user_id = verify_reset_token(token)

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido o expirado"
            )

        # Buscar usuario
        user_service = UserService()
        user = user_service.get_by_id(db, user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario inactivo"
            )

        # Actualizar contraseña
        from app.utils.auth import get_password_hash
        user.password_hash = get_password_hash(new_password)

        from app.utils.datetime_utils import get_colombia_now
        user.updated_at = get_colombia_now()

        db.commit()

        return {
            "message": "Contraseña restablecida exitosamente",
            "user_id": str(user.id)
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Registrar nuevo usuario
    """
    try:
        user_service = UserService()

        # Verificar que el username no existe
        existing = user_service.get_user_by_username(db, user_data.username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya existe"
            )

        # Verificar que el email no existe
        existing = user_service.get_user_by_email(db, user_data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )

        # Crear usuario
        user = user_service.create_user(db, user_data)

        return UserResponse.model_validate(user)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar usuario: {str(e)}"
        )


@router.post("/logout")
async def logout():
    """
    Endpoint de logout - Implementación básica
    """
    return {"message": "Logout endpoint - Implementación pendiente"}


@router.get("/me")
async def get_current_user_info(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Obtener información del usuario actual desde cookies o Authorization header
    """
    from src.app.dependencies import get_current_active_user_from_cookies
    
    try:
        current_user = get_current_active_user_from_cookies(request, db)
        return {
            "id": str(current_user.id),
            "username": current_user.username,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "role": current_user.role.value if current_user.role else None,
            "is_active": current_user.is_active
        }
    except HTTPException as e:
        # Return 401 instead of 403 for better client handling
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado"
        )


@router.post("/refresh-token")
async def refresh_token():
    """
    Refrescar token de acceso - Implementación básica
    """
    return {"message": "Refresh token endpoint - Implementación pendiente"}


@router.post("/request-reset")
async def request_password_reset(
    request_data: dict,
    db: Session = Depends(get_db)
):
    """
    Solicitar restablecimiento de contraseña
    """
    try:
        email = request_data.get("email", "").strip().lower()

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email es requerido"
            )

        # Validar formato de email
        import re
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de email inválido"
            )

        # Buscar usuario por email
        user_service = UserService()
        user = user_service.get_user_by_email(db, email)

        if not user:
            # Por seguridad, no revelamos si el email existe o no
            # Simplemente retornamos éxito
            return {
                "message": "Si el email existe, se ha enviado un enlace de recuperación",
                "email": email
            }

        if not user.is_active:
            # Usuario inactivo, no enviamos email
            return {
                "message": "Si el email existe, se ha enviado un enlace de recuperación",
                "email": email
            }

        # Generar token de reset
        from app.utils.auth import create_reset_token
        reset_token = create_reset_token(str(user.id))

        # Enviar email usando NotificationService (que usa EmailService internamente)
        try:
            from app.services.notification_service import NotificationService
            import logging
            
            email_logger = logging.getLogger("auth")
            notification_service = NotificationService()

            # Enviar email de reset de contraseña (usa EmailService con templates)
            email_sent = await notification_service.send_password_reset_email(db, user, reset_token)

            if email_sent:
                email_logger.info(f"✅ Email de reset enviado a: {user.email}")
            else:
                email_logger.warning(f"⚠️ No se pudo enviar email de reset a: {user.email}")
                # Continuamos como si se hubiera enviado (por seguridad - no revelar si el email existe)

        except Exception as email_error:
            import logging
            email_logger = logging.getLogger("auth")
            email_logger.error(f"❌ Error enviando email de reset: {str(email_error)}")
            # Continuamos como si se hubiera enviado (por seguridad)

        return {
            "message": "Si el email existe, se ha enviado un enlace de recuperación",
            "email": email
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )