# ========================================
# PAQUETES EL CLUB v2.0 - Middleware de Autenticación (Refactorizado)
# ========================================
# Archivo: CODE/src/app/middleware/auth_middleware_v2.py
# Versión: 2.0.0
# Fecha: 2025-01-27
# Descripción: Middleware simplificado con responsabilidades claras
# ========================================

"""
Middleware de autenticación refactorizado.

Responsabilidades:
1. Verificar autenticación en rutas protegidas
2. Redirigir páginas HTML a /auth/login
3. Retornar 401 JSON para APIs
4. Usar configuración centralizada de rutas

NO hace:
- Limpiar cookies (eso es del endpoint /auth/login)
- Verificar tokens expirados (eso es del servicio de auth)
- Mantener lista hardcodeada de rutas públicas
"""

from fastapi import Request, Response
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging
from typing import Optional
from urllib.parse import urlencode

from app.config_routes import is_public_route, is_api_public_route, is_static_route
from app.utils.auth import verify_token

logger = logging.getLogger(__name__)

from app.config_routes import is_public_route, is_api_public_route, is_static_route


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware de autenticación simplificado.
    
    Flujo:
    1. Request llega
    2. ¿Es ruta pública? → Continuar
    3. ¿Es ruta estática? → Continuar
    4. ¿Está autenticado? → Continuar
    5. ¿Es API? → Retornar 401 JSON
    6. ¿Es HTML? → Redirigir a /auth/login
    """
    
    def __init__(self, app: ASGIApp, login_url: str = "/auth/login"):
        super().__init__(app)
        self.login_url = login_url

    async def dispatch(self, request: Request, call_next):
        """Interceptar request y verificar autenticación"""
        path = request.url.path
        
        # 1. Rutas públicas → Continuar sin verificar
        if is_public_route(path):
            return await call_next(request)
        
        # 2. Rutas API públicas → Continuar sin verificar
        if is_api_public_route(path):
            return await call_next(request)
        
        # 3. Rutas estáticas → Continuar sin verificar
        if is_static_route(path):
            return await call_next(request)
        
        # 4. Verificar autenticación
        is_authenticated = await self._check_authentication(request)
        
        if is_authenticated:
            # Usuario autenticado → Continuar
            return await call_next(request)
        
        # 4. Usuario NO autenticado
        # ¿Es API? → 401 JSON
        if path.startswith("/api/"):
            return self._return_401_json(request, path)
        
        # ¿Es HTML? → Redirigir a login
        return self._redirect_to_login(request, path)

    async def _check_authentication(self, request: Request) -> bool:
        """
        Verificar si el usuario está autenticado.
        
        Returns:
            True si está autenticado, False si no
        """
        try:
            # Obtener token de cookies
            access_token = request.cookies.get("access_token")
            
            if not access_token:
                return False
            
            # Verificar token (delegar a servicio de auth)
            payload = verify_token(access_token)
            
            if not payload:
                return False
            
            # Token válido
            return True
            
        except Exception as e:
            logger.debug(f"Error verificando autenticación: {e}")
            return False

    def _return_401_json(self, request: Request, path: str) -> JSONResponse:
        """
        Retornar 401 JSON para APIs.
        
        NO incluye header Location para evitar redirects automáticos del navegador.
        """
        query_params = dict(request.query_params)
        redirect_url = f"{path}"
        if query_params:
            redirect_url += f"?{urlencode(query_params)}"
        
        logger.info(f"API no autenticada: {path}")
        
        return JSONResponse(
            status_code=401,
            content={
                "detail": "No autenticado",
                "redirect_url": self.login_url,
                "original_url": redirect_url,
                "requires_auth": True
            },
            headers={
                "X-Login-URL": self.login_url,
                "X-Original-URL": redirect_url,
                "Cache-Control": "no-cache, no-store, must-revalidate"
            }
        )

    def _redirect_to_login(self, request: Request, path: str) -> RedirectResponse:
        """
        Redirigir a página de login.
        
        Preserva la URL original para redirección después del login.
        """
        query_params = dict(request.query_params)
        redirect_url = f"{path}"
        if query_params:
            redirect_url += f"?{urlencode(query_params)}"
        
        login_url_with_redirect = f"{self.login_url}?redirect={redirect_url}"
        
        logger.info(f"Redirigiendo a login desde: {path}")
        
        return RedirectResponse(
            url=login_url_with_redirect,
            status_code=302,
            headers={
                "X-Original-URL": redirect_url,
                "Cache-Control": "no-cache, no-store, must-revalidate"
            }
        )


def create_auth_middleware(login_url: str = "/auth/login"):
    """
    Factory function para crear el middleware.
    
    Args:
        login_url: URL de la página de login
    
    Returns:
        Función que crea el middleware
    
    Example:
        app.add_middleware(AuthMiddleware, login_url="/auth/login")
    """
    return lambda app: AuthMiddleware(app, login_url)
