# ========================================
# PAQUETES EL CLUB v3.1 - Dependencias de Autenticación
# ========================================

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import uuid
import logging

from .database import get_db
from .models.user import User, UserRole
from .services.user_service import UserService
from .utils.auth import get_user_from_token

# Configurar logger
logger = logging.getLogger(__name__)

# Configuración del esquema de autenticación
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Obtener usuario actual desde token JWT"""
    token = credentials.credentials
    
    # Verificar token
    user_data = get_user_from_token(token)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acceso inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Obtener usuario de la base de datos
    user_service = UserService()
    user = user_service.get_by_id(db, int(user_data["user_id"]))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Obtener usuario activo actual"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    return current_user

def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Obtener usuario administrador actual"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requieren permisos de administrador"
        )
    return current_user

def get_current_admin_user_from_cookies(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """Obtener usuario administrador actual desde cookies (para páginas web)"""
    user = get_current_user_from_cookies(request, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
            headers={
                "Location": "/auth/login",
                "Content-Type": "application/json"
            },
        )
    
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requieren permisos de administrador"
        )
    return user

def get_current_operator_user(current_user: User = Depends(get_current_user)) -> User:
    """Obtener usuario operador actual"""
    if not current_user.is_operator and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requieren permisos de operador"
        )
    return current_user

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Obtener servicio de usuarios"""
    return UserService(db)

def get_current_user_from_cookies(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Obtener usuario actual desde cookies (para páginas web)"""
    try:
        # Verificar si hay token en cookies
        token = request.cookies.get("access_token")
        if not token:
            logger.debug("No se encontró token access_token en cookies")
            return None

        logger.debug(f"Token encontrado en cookies, longitud: {len(token) if token else 0}")

        # Verificar token
        user_data = get_user_from_token(token)
        if not user_data:
            logger.warning("get_user_from_token retornó None, token inválido o expirado")
            return None
        
        logger.debug(f"Usuario extraído del token: {user_data.get('username')}")

        # Special handling for fake development token
        if token == "fake_token_for_development":
            # Create a fake user object for development
            from .models.user import User, UserRole
            fake_user = User()
            fake_user.id = 1
            fake_user.username = user_data["username"]
            fake_user.email = f"{user_data['username']}@example.com"
            fake_user.full_name = user_data["username"].title()
            # Convert role to lowercase for enum compatibility
            role_value = user_data["role"].lower() if user_data["role"] else "operator"
            fake_user.role = UserRole(role_value)
            fake_user.is_active = True
            return fake_user

        # Obtener usuario de la base de datos
        user_service = UserService()
        user_id = int(user_data["user_id"])
        logger.debug(f"Buscando usuario en BD con ID: {user_id}")
        
        user = user_service.get_by_id(db, user_id)

        if not user:
            logger.warning(f"Usuario no encontrado en BD con ID: {user_id}")
            return None
        
        if not user.is_active:
            logger.warning(f"Usuario {user.username} (ID: {user_id}) está inactivo")
            return None

        logger.debug(f"Usuario autenticado exitosamente: {user.username} (ID: {user.id})")
        return user
    except ValueError as e:
        logger.error(f"Error al convertir user_id a int: {str(e)}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Error inesperado en get_current_user_from_cookies: {str(e)}", exc_info=True)
        return None

def get_current_active_user_from_cookies(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """Obtener usuario activo actual desde cookies o Authorization header (para páginas web)"""
    user = get_current_user_from_cookies(request, db)
    if not user:
        # Try to get from Authorization header as fallback
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            user_data = get_user_from_token(token)
            if user_data:
                # For development token
                if token == "fake_token_for_development":
                    from .models.user import User, UserRole
                    fake_user = User()
                    fake_user.id = 1
                    fake_user.username = user_data["username"]
                    fake_user.email = f"{user_data['username']}@example.com"
                    fake_user.full_name = user_data["username"].title()
                    # Convert role to lowercase for enum compatibility
                    role_value = user_data["role"].lower() if user_data["role"] else "operator"
                    fake_user.role = UserRole(role_value)
                    fake_user.is_active = True
                    return fake_user
                else:
                    # Get from database
                    from .services.user_service import UserService
                    user_service = UserService()
                    user = user_service.get_by_id(db, int(user_data["user_id"]))
                    if user and user.is_active:
                        return user

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
            headers={
                "Location": "/auth/login",
                "Content-Type": "application/json"
            },
        )
    return user

def verify_token_optional(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Verificar token opcionalmente (para rutas que pueden ser públicas o privadas)"""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.split(" ")[1]
    user_data = get_user_from_token(token)
    
    if not user_data:
        return None
    
    user_service = UserService()
    user = user_service.get_by_id(db, int(user_data["user_id"]))
    
    if not user or not user.is_active:
        return None
    
    return user

def require_admin_or_self(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user)
) -> User:
    """Verificar que el usuario sea admin o el propietario del recurso"""
    if current_user.is_admin:
        return current_user
    
    if current_user.id == user_id:
        return current_user
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Acceso denegado. Solo puedes acceder a tus propios recursos"
    )
