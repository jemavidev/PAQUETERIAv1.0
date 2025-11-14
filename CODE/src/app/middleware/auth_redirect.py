# ========================================
# PAQUETES EL CLUB v1.0 - Middleware de Redirección de Autenticación
# ========================================
# Archivo: CODE/LOCAL/src/app/middleware/auth_redirect.py
# Versión: 1.0.0
# Fecha: 2025-01-24
# Autor: Equipo de Desarrollo
# ========================================

"""
Middleware para redirección automática al login cuando el usuario no está autenticado
"""

from fastapi import Request, Response, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging
from typing import List, Optional
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

class AuthRedirectMiddleware(BaseHTTPMiddleware):
    """
    Middleware que intercepta respuestas 401 y redirige automáticamente al login
    """
    
    def __init__(self, app: ASGIApp, login_url: str = "/auth/login"):
        super().__init__(app)
        self.login_url = login_url
        
        # Rutas que no requieren redirección (públicas)
        self.public_paths = {
            "/",
            "/announce",
            "/search",
            "/help",
            "/cookies",
            "/policies",
            "/auth/login",
            "/auth/register", 
            "/auth/forgot-password",
            "/auth/reset-password",
            "/health",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/health",
            "/api/auth/login"  # Agregar endpoint de login API
        }
        
        # Rutas de API que requieren redirección JSON
        self.api_paths = {
            "/api/"
        }
        
        # Rutas estáticas que no requieren autenticación
        self.static_paths = {
            "/static/",
            "/uploads/"
        }

    async def dispatch(self, request: Request, call_next):
        """
        Intercepta la request y maneja la redirección de autenticación
        """
        try:
            # Verificar si es una ruta pública
            if self._is_public_path(request.url.path):
                response = await call_next(request)
                return response
            
            # Verificar si es una ruta estática
            if self._is_static_path(request.url.path):
                response = await call_next(request)
                return response
            
            # Procesar la request normalmente
            response = await call_next(request)
            
            # Si la respuesta es 401, manejar la redirección
            if response.status_code == 401:
                return await self._handle_unauthorized(request, response)
            
            return response
            
        except HTTPException as e:
            if e.status_code == 401:
                return await self._handle_unauthorized(request, None)
            raise e
        except Exception as e:
            logger.error(f"Error en AuthRedirectMiddleware: {e}")
            return await call_next(request)

    def _is_public_path(self, path: str) -> bool:
        """Verificar si la ruta es pública"""
        # Verificación exacta
        if path in self.public_paths:
            return True
        
        # Verificación de prefijos
        for public_path in self.public_paths:
            if path.startswith(public_path + "/") or path.startswith(public_path + "?"):
                return True
        
        return False

    def _is_static_path(self, path: str) -> bool:
        """Verificar si la ruta es estática"""
        for static_path in self.static_paths:
            if path.startswith(static_path):
                return True
        return False

    def _is_api_path(self, path: str) -> bool:
        """Verificar si la ruta es de API"""
        # Solo las rutas que empiecen con /api/ son APIs
        return path.startswith("/api/")

    async def _handle_unauthorized(self, request: Request, response: Optional[Response]):
        """
        Manejar respuesta 401 - redirigir al login
        """
        path = request.url.path
        query_params = dict(request.query_params)
        
        # Preservar la URL original para redirección después del login
        redirect_url = f"{path}"
        if query_params:
            redirect_url += f"?{urlencode(query_params)}"
        
        # Si es una ruta de API, devolver JSON SIN header Location para evitar redirects automáticos
        if self._is_api_path(path) or path.startswith("/api/"):
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
                    "X-Original-URL": redirect_url
                }
            )
        
        # Para páginas web, redirigir directamente al login
        login_url_with_redirect = f"{self.login_url}?redirect={redirect_url}"
        
        logger.info(f"Redirigiendo usuario no autenticado desde {path} a {login_url_with_redirect}")
        
        return RedirectResponse(
            url=login_url_with_redirect,
            status_code=302,
            headers={
                "X-Original-URL": redirect_url,
                "Cache-Control": "no-cache, no-store, must-revalidate"
            }
        )


def create_auth_redirect_middleware(login_url: str = "/auth/login") -> AuthRedirectMiddleware:
    """
    Factory function para crear el middleware de redirección de autenticación
    """
    return lambda app: AuthRedirectMiddleware(app, login_url)
