# ========================================
# PAQUETES EL CLUB v2.0 - Configuración de Rutas
# ========================================
# Archivo: CODE/src/app/config/routes.py
# Versión: 2.0.0
# Fecha: 2025-01-27
# Descripción: Fuente única de verdad para rutas públicas y protegidas
# ========================================

"""
Configuración centralizada de rutas públicas y protegidas.

Este módulo es la ÚNICA fuente de verdad para determinar qué rutas
son públicas y cuáles requieren autenticación.

Ventajas:
- Un solo lugar para agregar/quitar rutas públicas
- Compartido entre backend y frontend (vía API)
- Fácil de mantener y auditar
"""

from typing import Set

# ========================================
# RUTAS PÚBLICAS (HTML)
# ========================================

PUBLIC_ROUTES: Set[str] = {
    # Página principal
    "/",
    
    # Páginas públicas de funcionalidad
    "/announce",          # Anunciar paquetes
    "/search",            # Buscar paquetes
    
    # Autenticación
    "/auth/login",
    "/auth/register",
    "/auth/forgot-password",
    "/auth/reset-password",
    "/login",             # Alias de /auth/login
    
    # Portal de Clientes (público con OTP)
    "/customer-portal",
    "/customer-portal/verify",
    "/customer-portal/dashboard",
    
    # Páginas informativas
    "/help",
    "/cookies",
    "/terms",
    "/privacy",
    "/policies",
    
    # Páginas de demostración/testing
    "/error-demo",
    "/test-search",
    "/demo-error-system",
    
    # Health checks y métricas
    "/health",
    "/metrics",
    
    # Documentación API
    "/docs",
    "/redoc",
    "/openapi.json",
}

# ========================================
# RUTAS ESTÁTICAS
# ========================================

STATIC_PREFIXES: Set[str] = {
    "/static/",
    "/uploads/",
}

# ========================================
# RUTAS API PÚBLICAS
# ========================================

API_PUBLIC_ROUTES: Set[str] = {
    # Autenticación
    "/api/auth/login",
    "/api/auth/register",
    "/api/auth/forgot-password",
    "/api/auth/reset-password",
    
    # Portal de Clientes (APIs públicas con OTP)
    "/api/customer-portal/request-otp",
    "/api/customer-portal/verify-otp",
    "/api/customer-portal/me",
    "/api/customer-portal/packages",
    "/api/customer-portal/logout",
    
    # Anuncios y búsqueda (públicos)
    "/api/announcements/direct",
    "/api/announcements/search/package",
    "/api/search",
    
    # Configuración (públicos)
    "/api/config/public-routes",
    "/api/config/app",
    "/api/config/auth",
    
    # Health y métricas
    "/api/health",
    "/health",
    "/metrics",
    
    # Debug (público)
    "/api/debug/portal-routes",
    
    # Desarrollo (solo en dev)
    "/api/auth/dev/set-cookies",
    "/api/auth/dev/check",
}

# ========================================
# RUTAS PROTEGIDAS (Ejemplos)
# ========================================

PROTECTED_ROUTES: Set[str] = {
    "/admin",
    "/packages",
    "/profile",
    "/settings",
    "/messages",
    "/receive",
    "/dashboard",
}

# ========================================
# FUNCIONES HELPER
# ========================================

def is_public_route(path: str) -> bool:
    """
    Verificar si una ruta es pública.
    
    Args:
        path: Ruta a verificar (ej: "/auth/login")
    
    Returns:
        True si la ruta es pública, False si requiere autenticación
    
    Examples:
        >>> is_public_route("/auth/login")
        True
        >>> is_public_route("/admin")
        False
        >>> is_public_route("/static/css/style.css")
        True
    """
    # Verificación exacta
    if path in PUBLIC_ROUTES:
        return True
    
    # Verificación de prefijos estáticos
    for prefix in STATIC_PREFIXES:
        if path.startswith(prefix):
            return True
    
    # Verificación de rutas con query params
    path_without_query = path.split("?")[0]
    if path_without_query in PUBLIC_ROUTES:
        return True
    
    return False


def is_api_public_route(path: str) -> bool:
    """
    Verificar si una ruta API es pública.
    
    Args:
        path: Ruta API a verificar (ej: "/api/auth/login")
    
    Returns:
        True si la ruta API es pública, False si requiere autenticación
    
    Examples:
        >>> is_api_public_route("/api/auth/login")
        True
        >>> is_api_public_route("/api/packages")
        False
    """
    # Verificación exacta
    if path in API_PUBLIC_ROUTES:
        return True
    
    # Verificación de rutas con query params
    path_without_query = path.split("?")[0]
    if path_without_query in API_PUBLIC_ROUTES:
        return True
    
    return False


def is_static_route(path: str) -> bool:
    """
    Verificar si una ruta es estática.
    
    Args:
        path: Ruta a verificar
    
    Returns:
        True si la ruta es estática
    
    Examples:
        >>> is_static_route("/static/css/style.css")
        True
        >>> is_static_route("/uploads/image.jpg")
        True
        >>> is_static_route("/admin")
        False
    """
    for prefix in STATIC_PREFIXES:
        if path.startswith(prefix):
            return True
    return False


def get_all_public_routes() -> dict:
    """
    Obtener todas las rutas públicas para el frontend.
    
    Returns:
        Diccionario con rutas públicas, APIs públicas y prefijos estáticos
    
    Examples:
        >>> routes = get_all_public_routes()
        >>> "/auth/login" in routes["public_routes"]
        True
    """
    return {
        "public_routes": sorted(list(PUBLIC_ROUTES)),
        "api_public_routes": sorted(list(API_PUBLIC_ROUTES)),
        "static_prefixes": sorted(list(STATIC_PREFIXES)),
        "protected_routes": sorted(list(PROTECTED_ROUTES)),
    }


# ========================================
# VALIDACIÓN AL IMPORTAR
# ========================================

def _validate_routes():
    """Validar que no haya conflictos en la configuración"""
    # Verificar que no haya rutas duplicadas entre públicas y protegidas
    conflicts = PUBLIC_ROUTES & PROTECTED_ROUTES
    if conflicts:
        raise ValueError(f"Rutas en conflicto (públicas y protegidas): {conflicts}")
    
    # Verificar que todas las rutas empiecen con /
    for route in PUBLIC_ROUTES | API_PUBLIC_ROUTES | PROTECTED_ROUTES:
        if not route.startswith("/"):
            raise ValueError(f"Ruta inválida (debe empezar con /): {route}")

# Ejecutar validación al importar
_validate_routes()
