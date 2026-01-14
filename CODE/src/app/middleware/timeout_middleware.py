"""
Middleware de timeout para prevenir requests que se cuelgan
"""
import asyncio
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from typing import Callable

logger = logging.getLogger(__name__)


class TimeoutMiddleware(BaseHTTPMiddleware):
    """
    Middleware que aplica timeout a todas las requests
    para prevenir que se cuelguen indefinidamente
    """
    
    def __init__(self, app, timeout: int = 60):
        """
        Args:
            app: Aplicación FastAPI
            timeout: Timeout en segundos (default: 60)
        """
        super().__init__(app)
        self.timeout = timeout
    
    async def dispatch(self, request: Request, call_next: Callable):
        """
        Procesa la request con timeout
        """
        # Excluir health check del timeout
        if request.url.path == "/health":
            return await call_next(request)
        
        try:
            # Aplicar timeout a la request
            response = await asyncio.wait_for(
                call_next(request),
                timeout=self.timeout
            )
            return response
            
        except asyncio.TimeoutError:
            # Request excedió el timeout
            logger.error(
                f"⏱️ Request timeout después de {self.timeout}s: "
                f"{request.method} {request.url.path}"
            )
            
            return JSONResponse(
                status_code=504,
                content={
                    "error": "Request Timeout",
                    "message": f"La operación excedió el tiempo límite de {self.timeout} segundos",
                    "path": request.url.path
                }
            )
        
        except Exception as e:
            logger.error(f"Error en TimeoutMiddleware: {e}")
            raise
