# ========================================
# PAQUETES EL CLUB v1.0 - Contexto de Autenticación
# ========================================
# Archivo: CODE/LOCAL/src/app/utils/auth_context.py (siguiendo reglas de AGENTS.md)
# Versión: 1.0.0
# Fecha: 2025-01-24
# Autor: Equipo de Desarrollo
# ========================================

"""
Utilidades para manejar el contexto de autenticación en las plantillas
"""

from fastapi import Request, Depends
from fastapi.templating import Jinja2Templates
from typing import Dict, Any, Optional
from .auth import verify_token
from app.models.user import User
from app.dependencies import get_current_active_user_from_cookies


def get_auth_context(request: Request) -> Dict[str, Any]:
    """
    Obtener contexto de autenticación básico para plantillas

    Args:
        request: Objeto Request de FastAPI

    Returns:
        Dict con información de autenticación
    """
    try:
        # Verificar si hay token de acceso en las cookies
        access_token = request.cookies.get("access_token")
        user_name = request.cookies.get("user_name")
        user_role = request.cookies.get("user_role")

        # Verificar si el token es válido
        is_authenticated = False
        if access_token and user_name:
            try:
                # Intentar verificar el token JWT
                from .auth import verify_token
                payload = verify_token(access_token)
                if payload:
                    is_authenticated = True
                    # Actualizar información del usuario desde el token si es necesario
                    user_name = payload.get("username", user_name)
                    user_role = payload.get("role", user_role)
            except Exception as e:
                # Token inválido o expirado
                print(f"Token inválido en get_auth_context: {e}")
                is_authenticated = False

        context = {
            "request": request,
            "is_authenticated": is_authenticated,
            "user_name": user_name if is_authenticated else None,
            "user_role": user_role if is_authenticated else None,
            "user": {
                "username": user_name,
                "role": user_role,
                "full_name": user_name.title() if user_name else None
            } if is_authenticated else None
        }

        return context
    except Exception as e:
        print(f"Error en get_auth_context: {e}")
        # Retornar contexto básico en caso de error
        return {
            "request": request,
            "is_authenticated": False,
            "user_name": None,
            "user_role": None,
            "user": None
        }


def get_auth_context_from_request(request: Request) -> Dict[str, Any]:
    """
    Obtener contexto de autenticación completo desde request

    Args:
        request: Objeto Request de FastAPI

    Returns:
        Dict con información completa de autenticación
    """
    try:
        # Obtener contexto básico
        context = get_auth_context(request)

        # Agregar información adicional para las plantillas
        context.update({
            "current_path": str(request.url.path),
            "query_params": dict(request.query_params),
            "method": request.method,
            "headers": dict(request.headers),
            "client_host": getattr(request.client, 'host', None) if request.client else None,
        })

        return context
    except Exception as e:
        print(f"Error en get_auth_context_from_request: {e}")
        # Retornar contexto básico en caso de error
        return {
            "is_authenticated": False,
            "user": None,
            "user_name": None,
            "user_role": None,
            "current_path": str(request.url.path),
            "query_params": dict(request.query_params),
            "method": request.method,
            "headers": dict(request.headers),
            "client_host": getattr(request.client, 'host', None) if request.client else None,
        }


def get_auth_context_with_user(request: Request, user: Optional[User] = None) -> Dict[str, Any]:
    """
    Obtener contexto de autenticación con información detallada del usuario

    Args:
        request: Objeto Request de FastAPI
        user: Objeto User opcional

    Returns:
        Dict con información completa de autenticación y usuario
    """
    context = get_auth_context_from_request(request)

    if user:
        context.update({
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "phone": user.phone,
                "role": user.role.value if user.role else None,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            },
            "is_admin": user.role.value == "ADMIN" if user.role else False,
            "is_operator": user.role.value == "OPERADOR" if user.role else False,
            "is_user": user.role.value == "USUARIO" if user.role else False,
        })

    return context


def create_template_context(
    request: Request,
    title: str = "PAQUETES EL CLUB",
    user: Optional[User] = None,
    **extra_context
) -> Dict[str, Any]:
    """
    Crear contexto completo para plantillas

    Args:
        request: Objeto Request de FastAPI
        title: Título de la página
        user: Objeto User opcional
        **extra_context: Contexto adicional

    Returns:
        Dict con contexto completo para plantillas
    """
    context = get_auth_context_with_user(request, user)

    # Agregar información básica de la aplicación
    context.update({
        "title": title,
        "app_name": "PAQUETES EL CLUB",
        "app_version": "1.0.0",
        "company_name": "PAQUETES EL CLUB",
        "company_phone": "3334004007",
        "company_email": "guia@papyrus.com.co",
        "current_year": 2025,
    })

    # Agregar contexto adicional
    context.update(extra_context)

    return context


# Funciones de conveniencia para dependencias
async def get_template_context(
    request: Request,
    user: Optional[User] = Depends(get_current_active_user_from_cookies)
) -> Dict[str, Any]:
    """
    Dependencia para obtener contexto de plantilla con usuario autenticado

    Args:
        request: Objeto Request de FastAPI
        user: Usuario autenticado (opcional)

    Returns:
        Dict con contexto completo
    """
    return get_auth_context_with_user(request, user)


async def require_auth_context(request: Request) -> Dict[str, Any]:
    """
    Dependencia que requiere autenticación y devuelve contexto

    Args:
        request: Objeto Request de FastAPI

    Returns:
        Dict con contexto de autenticación

    Raises:
        HTTPException: Si el usuario no está autenticado
    """
    context = get_auth_context(request)

    if not context["is_authenticated"]:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticación requerida"
        )

    return context


def get_auth_context_required(request: Request) -> Dict[str, Any]:
    """
    Obtener contexto de autenticación y lanzar 401 si no está autenticado
    Esta función debe usarse en rutas que requieren autenticación

    Args:
        request: Objeto Request de FastAPI

    Returns:
        Dict con contexto de autenticación

    Raises:
        HTTPException: Si el usuario no está autenticado
    """
    context = get_auth_context_from_request(request)

    if not context["is_authenticated"]:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticación requerida"
        )

    return context


async def require_admin_context(
    request: Request,
    user: User = Depends(get_current_active_user_from_cookies)
) -> Dict[str, Any]:
    """
    Dependencia que requiere rol de administrador

    Args:
        request: Objeto Request de FastAPI
        user: Usuario autenticado

    Returns:
        Dict con contexto de administrador

    Raises:
        HTTPException: Si el usuario no es administrador
    """
    if user.role.value != "ADMIN":
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )

    return get_auth_context_with_user(request, user)