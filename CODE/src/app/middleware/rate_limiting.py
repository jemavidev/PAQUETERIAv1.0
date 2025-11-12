# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Rate Limiting Middleware
Versión: 1.0.0
Fecha: 2025-09-21
Autor: Equipo de Desarrollo
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import redis
from app.config import settings

# Crear cliente Redis para rate limiting
redis_client = redis.from_url(settings.redis_url)

# Configurar Limiter con Redis como backend
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.redis_url,
    strategy="fixed-window",  # Ventana fija para consistencia
)

# ========================================
# CONFIGURACIÓN DE LIMITS POR ENDPOINT
# ========================================

# Límites generales
GENERAL_LIMITS = {
    "default": "100/minute",  # Límite general por IP
    "strict": "10/minute",    # Límite estricto para endpoints sensibles
    "api": "200/minute",      # Límite para endpoints de API
}

# Límites específicos por endpoint/ruta
ENDPOINT_LIMITS = {
    # Autenticación - más restrictivo
    "/api/auth/login": "5/minute",
    "/api/auth/register": "3/minute",
    "/api/auth/forgot-password": "2/minute",

    # API de administración - restrictivo
    "/api/admin": "50/minute",
    "/api/admin/users": "20/minute",

    # API de archivos - moderado
    "/api/files/upload": "10/minute",

    # API de SMS - restrictivo por costos
    "/api/notifications/send": "20/minute",
    "/api/notifications/send/bulk": "5/minute",

    # API de reportes - moderado
    "/api/reports/generate": "10/minute",

    # API de búsqueda - permisivo
    "/api/search": "500/minute",

    # Endpoints públicos - permisivos
    "/api/announcements": "1000/minute",
    "/api/packages": "500/minute",
}

# ========================================
# FUNCIONES DE RATE LIMITING
# ========================================

def get_rate_limit_for_path(path: str) -> str:
    """
    Obtener el límite de rate para una ruta específica
    """
    # Buscar coincidencias exactas primero
    if path in ENDPOINT_LIMITS:
        return ENDPOINT_LIMITS[path]

    # Buscar coincidencias por prefijo
    for endpoint, limit in ENDPOINT_LIMITS.items():
        if path.startswith(endpoint):
            return limit

    # Categorizar por tipo de endpoint
    if path.startswith("/api/admin"):
        return GENERAL_LIMITS["strict"]
    elif path.startswith("/api/"):
        return GENERAL_LIMITS["api"]
    else:
        return GENERAL_LIMITS["default"]

# ========================================
# HANDLERS DE ERRORES
# ========================================

async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    Handler personalizado para errores de rate limiting
    """
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Demasiadas solicitudes. Por favor, espere antes de intentar nuevamente.",
            "error": "rate_limit_exceeded",
            "retry_after": exc.retry_after,
            "limit": exc.limit,
            "remaining": exc.remaining,
        },
        headers={
            "Retry-After": str(exc.retry_after),
            "X-RateLimit-Limit": str(exc.limit),
            "X-RateLimit-Remaining": str(exc.remaining),
            "X-RateLimit-Reset": str(exc.reset_time),
        }
    )

# ========================================
# MIDDLEWARE CONFIGURATION
# ========================================

def create_rate_limiter():
    """
    Crear y configurar el limiter con todas las reglas
    """
    # Configurar el handler de errores
    limiter._rate_limit_exceeded_handler = rate_limit_exceeded_handler

    return limiter

# ========================================
# DECORADORES PARA ENDPOINTS ESPECÍFICOS
# ========================================

def auth_rate_limit():
    """Decorador para endpoints de autenticación"""
    return limiter.limit(GENERAL_LIMITS["strict"])

def admin_rate_limit():
    """Decorador para endpoints de administración"""
    return limiter.limit("20/minute")

def api_rate_limit():
    """Decorador para endpoints generales de API"""
    return limiter.limit(GENERAL_LIMITS["api"])

def public_rate_limit():
    """Decorador para endpoints públicos"""
    return limiter.limit("500/minute")

# ========================================
# FUNCIONES DE MONITOREO
# ========================================

def get_rate_limit_stats():
    """
    Obtener estadísticas de rate limiting
    """
    try:
        # Obtener keys de rate limiting desde Redis
        keys = redis_client.keys("limiter:*")
        stats = {}

        for key in keys[:50]:  # Limitar a 50 keys para performance
            key_str = key.decode('utf-8')
            value = redis_client.get(key)
            if value:
                stats[key_str] = int(value)

        return {
            "total_keys": len(keys),
            "sample_stats": stats,
            "limits": GENERAL_LIMITS,
            "endpoint_limits": ENDPOINT_LIMITS,
        }
    except Exception as e:
        return {"error": f"Error obteniendo estadísticas: {str(e)}"}

def clear_rate_limits():
    """
    Limpiar todos los límites de rate (solo para desarrollo/testing)
    """
    try:
        keys = redis_client.keys("limiter:*")
        if keys:
            redis_client.delete(*keys)
        return {"cleared_keys": len(keys)}
    except Exception as e:
        return {"error": f"Error limpiando límites: {str(e)}"}