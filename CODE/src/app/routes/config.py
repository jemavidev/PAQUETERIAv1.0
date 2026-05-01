# ========================================
# PAQUETES EL CLUB v2.0 - Rutas de Configuración
# ========================================
# Archivo: CODE/src/app/routes/config.py
# Versión: 2.0.0
# Fecha: 2025-01-27
# Descripción: Endpoints de configuración para el frontend
# ========================================

"""
Endpoints de configuración para el frontend.

Proporciona información de configuración que el frontend necesita,
como rutas públicas, configuración de la aplicación, etc.
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.config_routes import get_all_public_routes
from app.config import settings

router = APIRouter()


@router.get("/api/config/public-routes")
async def get_public_routes_endpoint():
    """
    Obtener lista de rutas públicas para el frontend.
    
    Este endpoint permite que el frontend conozca qué rutas son públicas
    sin necesidad de mantener una lista hardcodeada en JavaScript.
    
    Returns:
        JSON con rutas públicas, APIs públicas y prefijos estáticos
    
    Example Response:
        {
            "public_routes": ["/", "/announce", "/auth/login", ...],
            "api_public_routes": ["/api/auth/login", ...],
            "static_prefixes": ["/static/", "/uploads/"],
            "protected_routes": ["/admin", "/packages", ...]
        }
    """
    return get_all_public_routes()


@router.get("/api/config/app")
async def get_app_config():
    """
    Obtener configuración general de la aplicación.
    
    Returns:
        JSON con configuración pública de la aplicación
    
    Example Response:
        {
            "app_name": "PAQUETES EL CLUB",
            "app_version": "2.0.0",
            "environment": "production",
            "features": {
                "sms_enabled": true,
                "email_enabled": true
            }
        }
    """
    try:
        return {
            "app_name": getattr(settings, "app_name", "PAQUETES EL CLUB"),
            "app_version": getattr(settings, "app_version", "2.0.0"),
            "environment": getattr(settings, "environment", "development"),
            "features": {
                "sms_enabled": bool(getattr(settings, "liwa_api_key", "")),
                "email_enabled": bool(getattr(settings, "smtp_server", "")),
            }
        }
    except Exception as e:
        # Retornar configuración por defecto si hay error
        return {
            "app_name": "PAQUETES EL CLUB",
            "app_version": "2.0.0",
            "environment": "development",
            "features": {
                "sms_enabled": False,
                "email_enabled": False,
            }
        }


@router.get("/api/config/auth")
async def get_auth_config():
    """
    Obtener configuración de autenticación.
    
    Returns:
        JSON con configuración de autenticación
    
    Example Response:
        {
            "login_url": "/auth/login",
            "token_expiry_hours": 24,
            "remember_me_days": 30
        }
    """
    return {
        "login_url": "/auth/login",
        "token_expiry_hours": 24,
        "remember_me_days": 30,
    }


@router.get("/api/config/environment")
async def get_environment():
    """
    Obtener el entorno actual (production, staging, development).
    
    Returns:
        JSON con el entorno actual
    
    Example Response:
        {
            "environment": "staging"
        }
    """
    return {
        "environment": getattr(settings, "environment", "development")
    }
