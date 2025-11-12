# ========================================
# PAQUETES EL CLUB v1.0 - Excepciones Personalizadas
# ========================================
# Archivo: CODE/LOCAL/src/app/utils/exceptions.py (siguiendo reglas de AGENTS.md)
# Versión: 1.0.0
# Fecha: 2025-01-24
# Autor: Equipo de Desarrollo
# ========================================

"""
Excepciones personalizadas para la aplicación PAQUETES EL CLUB
"""

from fastapi import HTTPException
from typing import Optional, Dict, Any


class PaqueteriaException(Exception):
    """
    Excepción base para errores de la aplicación Paqueteria
    """

    def __init__(
        self,
        message: str = "Error interno del servidor",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class UserException(PaqueteriaException):
    """
    Excepciones relacionadas con usuarios
    """

    def __init__(
        self,
        message: str = "Error relacionado con usuario",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code, details)


class PackageException(PaqueteriaException):
    """
    Excepciones relacionadas con paquetes
    """

    def __init__(
        self,
        message: str = "Error relacionado con paquete",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code, details)


class NotificationException(PaqueteriaException):
    """
    Excepciones relacionadas con notificaciones
    """

    def __init__(
        self,
        message: str = "Error en notificación",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code, details)


class DatabaseException(PaqueteriaException):
    """
    Excepciones relacionadas con la base de datos
    """

    def __init__(
        self,
        message: str = "Error en base de datos",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code, details)


class ValidationException(PaqueteriaException):
    """
    Excepciones de validación de datos
    """

    def __init__(
        self,
        message: str = "Error de validación",
        status_code: int = 422,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code, details)


class AuthenticationException(PaqueteriaException):
    """
    Excepciones de autenticación
    """

    def __init__(
        self,
        message: str = "Error de autenticación",
        status_code: int = 401,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code, details)


class AuthorizationException(PaqueteriaException):
    """
    Excepciones de autorización
    """

    def __init__(
        self,
        message: str = "Acceso denegado",
        status_code: int = 403,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code, details)


class SMSException(PaqueteriaException):
    """
    Excepciones relacionadas con envío de SMS
    """

    def __init__(
        self,
        message: str = "Error en envío de SMS",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code, details)


class ExternalServiceException(PaqueteriaException):
    """
    Excepciones relacionadas con servicios externos (APIs, etc.)
    """

    def __init__(
        self,
        message: str = "Error en servicio externo",
        status_code: int = 502,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code, details)


class EmailException(PaqueteriaException):
    """
    Excepciones relacionadas con envío de emails
    """

    def __init__(
        self,
        message: str = "Error en envío de email",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code, details)


# Funciones helper para crear excepciones comunes
def create_user_not_found_exception(user_id: str) -> UserException:
    """Crear excepción para usuario no encontrado"""
    return UserException(
        message=f"Usuario con ID {user_id} no encontrado",
        status_code=404,
        details={"user_id": user_id}
    )


def create_package_not_found_exception(package_id: str) -> PackageException:
    """Crear excepción para paquete no encontrado"""
    return PackageException(
        message=f"Paquete con ID {package_id} no encontrado",
        status_code=404,
        details={"package_id": package_id}
    )


def create_invalid_credentials_exception() -> AuthenticationException:
    """Crear excepción para credenciales inválidas"""
    return AuthenticationException(
        message="Credenciales inválidas",
        status_code=401,
        details={"error": "invalid_credentials"}
    )


def create_insufficient_permissions_exception(resource: str) -> AuthorizationException:
    """Crear excepción para permisos insuficientes"""
    return AuthorizationException(
        message=f"No tienes permisos para acceder a {resource}",
        status_code=403,
        details={"resource": resource}
    )


def create_validation_error_exception(field: str, value: Any, reason: str) -> ValidationException:
    """Crear excepción para error de validación"""
    return ValidationException(
        message=f"Error de validación en campo '{field}': {reason}",
        status_code=422,
        details={
            "field": field,
            "value": str(value),
            "reason": reason
        }
    )


class RateException(PaqueteriaException):
    """
    Excepciones relacionadas con tarifas
    """

    def __init__(
        self,
        message: str = "Error relacionado con tarifas",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code, details)


class RateCalculationException(RateException):
    """
    Excepciones para errores de cálculo de tarifas
    """

    def __init__(
        self,
        message: str = "Error en cálculo de tarifa",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code, details)