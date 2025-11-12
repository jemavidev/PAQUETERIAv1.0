# ========================================
# PAQUETES EL CLUB v1.0 - Utilidades de Autenticación
# ========================================
# Archivo: CODE/LOCAL/src/app/utils/auth.py (siguiendo reglas de AGENTS.md)
# Versión: 1.0.0
# Fecha: 2025-01-24
# Autor: Equipo de Desarrollo
# ========================================

"""
Utilidades para autenticación JWT y manejo de tokens
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
import bcrypt
import logging
from app.config import settings

# Configurar logger
logger = logging.getLogger(__name__)

# Configuración JWT
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verificar contraseña plana contra hash

    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash de la contraseña

    Returns:
        bool: True si la contraseña es correcta
    """
    # Aplicar la misma truncación de 72 bytes que se usó para hashear
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

    try:
        return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """
    Generar hash de contraseña

    Args:
        password: Contraseña en texto plano

    Returns:
        str: Hash de la contraseña
    """
    # bcrypt tiene una limitación de 72 bytes para contraseñas
    # Truncamos la contraseña si es más larga
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

    # Generar salt y hashear con bcrypt directamente
    salt = bcrypt.gensalt(rounds=12)  # Usar 12 rounds como en la configuración anterior
    hashed = bcrypt.hashpw(password_bytes, salt)

    return hashed.decode('utf-8')


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Crear token de acceso JWT

    Args:
        data: Datos a incluir en el token
        expires_delta: Tiempo de expiración opcional

    Returns:
        str: Token JWT
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verificar y decodificar token JWT

    Args:
        token: Token JWT a verificar

    Returns:
        Optional[Dict]: Datos del token si es válido, None si no
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Logging para diagnóstico
        if "exp" in payload:
            exp_timestamp = payload["exp"]
            exp_datetime = datetime.fromtimestamp(exp_timestamp)
            now_utc = datetime.utcnow()
            time_remaining = exp_datetime - now_utc
            
            logger.debug(
                f"Token verificado - Exp: {exp_datetime}, "
                f"Ahora UTC: {now_utc}, "
                f"Tiempo restante: {time_remaining.total_seconds() / 60:.2f} minutos"
            )
            
            # Si el token está cerca de expirar (menos de 1 minuto), log warning
            if time_remaining.total_seconds() < 60:
                logger.warning(
                    f"Token cerca de expirar - Tiempo restante: {time_remaining.total_seconds():.2f} segundos"
                )
        
        return payload
    except ExpiredSignatureError as e:
        # Token expirado específicamente
        logger.warning(f"Token expirado: {str(e)}")
        
        # Intentar obtener información del token expirado para logging
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
            if "exp" in payload:
                exp_timestamp = payload["exp"]
                exp_datetime = datetime.fromtimestamp(exp_timestamp)
                now_utc = datetime.utcnow()
                time_past_expiration = now_utc - exp_datetime
                logger.warning(
                    f"Token expirado hace {time_past_expiration.total_seconds() / 60:.2f} minutos. "
                    f"Exp: {exp_datetime}, Ahora: {now_utc}"
                )
        except Exception:
            pass
        
        return None
    except JWTError as e:
        # Otro error de JWT (firma inválida, formato incorrecto, etc.)
        logger.error(f"Error verificando token JWT: {str(e)}")
        return None
    except Exception as e:
        # Error inesperado
        logger.error(f"Error inesperado al verificar token: {str(e)}", exc_info=True)
        return None


def get_token_expiration(token: str) -> Optional[datetime]:
    """
    Obtener fecha de expiración de un token

    Args:
        token: Token JWT

    Returns:
        Optional[datetime]: Fecha de expiración o None si token inválido
    """
    payload = verify_token(token)
    if payload and "exp" in payload:
        return datetime.fromtimestamp(payload["exp"])
    return None


def is_token_expired(token: str) -> bool:
    """
    Verificar si un token ha expirado

    Args:
        token: Token JWT

    Returns:
        bool: True si el token ha expirado
    """
    try:
        expiration = get_token_expiration(token)
        if expiration:
            now_utc = datetime.utcnow()
            is_expired = now_utc > expiration
            time_diff = (now_utc - expiration).total_seconds() / 60 if is_expired else (expiration - now_utc).total_seconds() / 60
            
            logger.debug(
                f"Verificando expiración - Exp: {expiration}, "
                f"Ahora: {now_utc}, "
                f"Expirado: {is_expired}, "
                f"Diferencia: {abs(time_diff):.2f} minutos"
            )
            
            return is_expired
        
        # Si no se puede obtener la expiración, asumir que está expirado por seguridad
        logger.warning("No se pudo obtener fecha de expiración del token, asumiendo expirado")
        return True
    except Exception as e:
        logger.error(f"Error verificando expiración de token: {str(e)}", exc_info=True)
        # Por seguridad, retornar True si hay error
        return True


def refresh_token(token: str) -> Optional[str]:
    """
    Refrescar un token JWT si no ha expirado

    Args:
        token: Token JWT a refrescar

    Returns:
        Optional[str]: Nuevo token o None si no se puede refrescar
    """
    payload = verify_token(token)
    if payload and not is_token_expired(token):
        # Remover campos de expiración para crear nuevo token
        payload.pop("exp", None)
        payload.pop("iat", None)
        return create_access_token(payload)
    return None


def get_token_data(token: str) -> Optional[Dict[str, Any]]:
    """
    Obtener datos del token sin verificar expiración

    Args:
        token: Token JWT

    Returns:
        Optional[Dict]: Datos del token o None si inválido
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        return payload
    except JWTError:
        return None


def create_user_token(user_id: str, username: str, role: str) -> str:
    """
    Crear token JWT para usuario

    Args:
        user_id: ID del usuario
        username: Nombre de usuario
        role: Rol del usuario

    Returns:
        str: Token JWT
    """
    token_data = {
        "sub": user_id,
        "username": username,
        "role": role,
        "type": "access"
    }
    return create_access_token(token_data)


def get_user_from_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Extraer información del usuario desde token

    Args:
        token: Token JWT

    Returns:
        Optional[Dict]: Información del usuario o None si inválido
    """
    # Special handling for development fake token
    if token == "fake_token_for_development":
        logger.debug("Usando token de desarrollo fake")
        return {
            "user_id": "1",
            "username": "jesus",
            "role": "ADMIN"
        }

    if not token:
        logger.warning("Token vacío o None en get_user_from_token")
        return None

    payload = verify_token(token)
    if not payload:
        logger.warning("verify_token retornó None para el token")
        return None
    
    if payload.get("type") != "access":
        logger.warning(f"Token no es de tipo 'access', tipo encontrado: {payload.get('type')}")
        return None
    
    user_info = {
        "user_id": payload.get("sub"),
        "username": payload.get("username"),
        "role": payload.get("role")
    }
    
    logger.debug(f"Usuario extraído del token: {user_info.get('username')} (ID: {user_info.get('user_id')})")
    return user_info


def validate_token_format(token: str) -> bool:
    """
    Validar formato básico de token JWT

    Args:
        token: Token a validar

    Returns:
        bool: True si el formato es válido
    """
    if not token or not isinstance(token, str):
        return False

    parts = token.split(".")
    return len(parts) == 3 and all(parts)


def hash_password_for_storage(password: str) -> str:
    """
    Función wrapper para hashear contraseñas (para compatibilidad)

    Args:
        password: Contraseña en texto plano

    Returns:
        str: Hash de la contraseña
    """
    return get_password_hash(password)


def check_password_strength(password: str) -> Dict[str, Any]:
    """
    Verificar fortaleza de contraseña

    Args:
        password: Contraseña a verificar

    Returns:
        Dict: Información sobre la fortaleza de la contraseña
    """
    if not password:
        return {"valid": False, "strength": 0, "message": "Contraseña requerida"}

    strength = 0
    messages = []

    if len(password) >= 8:
        strength += 1
    else:
        messages.append("Mínimo 8 caracteres")

    if any(c.isupper() for c in password):
        strength += 1
    else:
        messages.append("Al menos una mayúscula")

    if any(c.islower() for c in password):
        strength += 1
    else:
        messages.append("Al menos una minúscula")

    if any(c.isdigit() for c in password):
        strength += 1
    else:
        messages.append("Al menos un número")

    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        strength += 1
    else:
        messages.append("Al menos un carácter especial")

    return {
        "valid": strength >= 3,
        "strength": strength,
        "max_strength": 5,
        "message": "Contraseña aceptable" if strength >= 3 else "; ".join(messages)
    }


def generate_secure_token(length: int = 32) -> str:
    """
    Generar token seguro aleatorio

    Args:
        length: Longitud del token

    Returns:
        str: Token seguro
    """
    import secrets
    import string

    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def create_reset_token(user_id: str) -> str:
    """
    Crear token para reset de contraseña

    Args:
        user_id: ID del usuario

    Returns:
        str: Token de reset
    """
    token_data = {
        "sub": user_id,
        "type": "reset",
        "jti": generate_secure_token(16)
    }
    # Token de reset expira en 24 horas
    return create_access_token(token_data, timedelta(hours=24))


def verify_reset_token(token: str) -> Optional[str]:
    """
    Verificar token de reset de contraseña

    Args:
        token: Token de reset

    Returns:
        Optional[str]: User ID si válido, None si no
    """
    payload = verify_token(token)
    if payload and payload.get("type") == "reset":
        return payload.get("sub")
    return None