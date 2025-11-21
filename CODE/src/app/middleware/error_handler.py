# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Handler de Errores
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from typing import Union

from app.utils.error_formatter import ErrorFormatter

logger = logging.getLogger(__name__)

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handler para errores de validación de Pydantic
    
    Args:
        request: Request de FastAPI
        exc: Excepción de validación
        
    Returns:
        JSONResponse con error formateado
    """
    logger.warning(f"Error de validación en {request.url}: {exc}")
    
    # Crear mensaje simple
    simple_message = ErrorFormatter.create_user_friendly_message(exc)
    
    # Debug: imprimir el mensaje
    logger.info(f"Mensaje generado: {simple_message}")
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": simple_message
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handler para excepciones HTTP
    
    Args:
        request: Request de FastAPI
        exc: Excepción HTTP
        
    Returns:
        JSONResponse con error formateado
    """
    logger.warning(f"Error HTTP en {request.url}: {exc.detail if hasattr(exc, 'detail') else exc}")
    
    # Si el endpoint ya proporcionó un mensaje detallado, usarlo
    if hasattr(exc, 'detail') and exc.detail and isinstance(exc.detail, str):
        message = exc.detail
    else:
        # Crear mensaje simple solo si no hay detail
        message = ErrorFormatter.create_user_friendly_message(exc)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": message,
            "detail": exc.detail if hasattr(exc, 'detail') else None
        }
    )

async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handler para excepciones HTTP de Starlette
    
    Args:
        request: Request de FastAPI
        exc: Excepción HTTP de Starlette
        
    Returns:
        JSONResponse o HTMLResponse según el tipo de petición
    """
    logger.warning(f"Error Starlette en {request.url}: {exc}")
    
    # Detectar si la petición espera HTML (navegador) o JSON (API)
    accept_header = request.headers.get("accept", "")
    is_api_request = (
        request.url.path.startswith("/api/") or
        "application/json" in accept_header
    )
    
    # Si es una petición de API, devolver JSON
    if is_api_request:
        simple_message = "Algo salió mal. Intenta nuevamente."
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": simple_message
            }
        )
    
    # Si es una petición de navegador, devolver HTML
    from fastapi.responses import HTMLResponse
    from app.utils.template_loader import get_templates
    
    templates = get_templates()
    
    # Intentar renderizar página de error personalizada
    try:
        context = {
            "request": request,
            "status_code": exc.status_code,
            "detail": exc.detail if hasattr(exc, 'detail') else "Algo salió mal",
            "is_authenticated": False,
            "user": None
        }
        
        # Si existe un template de error, usarlo
        return templates.TemplateResponse(
            "errors/error.html",
            context,
            status_code=exc.status_code
        )
    except Exception as template_error:
        # Si falla el template, devolver HTML simple
        logger.error(f"Error al renderizar template de error: {template_error}")
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error {exc.status_code}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; text-align: center; }}
                h1 {{ color: #e74c3c; }}
                p {{ color: #555; }}
                a {{ color: #3498db; text-decoration: none; }}
            </style>
        </head>
        <body>
            <h1>Error {exc.status_code}</h1>
            <p>{exc.detail if hasattr(exc, 'detail') else 'Algo salió mal'}</p>
            <p><a href="/">Volver al inicio</a></p>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=exc.status_code)

async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handler para excepciones genéricas
    
    Args:
        request: Request de FastAPI
        exc: Excepción genérica
        
    Returns:
        JSONResponse o HTMLResponse según el tipo de petición
    """
    logger.error(f"Error inesperado en {request.url}: {exc}", exc_info=True)
    
    # Detectar si la petición espera HTML (navegador) o JSON (API)
    accept_header = request.headers.get("accept", "")
    is_api_request = (
        request.url.path.startswith("/api/") or
        "application/json" in accept_header
    )
    
    # Si es una petición de API, devolver JSON
    if is_api_request:
        simple_message = "Ocurrió un error inesperado. Intenta nuevamente."
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": simple_message
            }
        )
    
    # Si es una petición de navegador, devolver HTML
    from fastapi.responses import HTMLResponse
    from app.utils.template_loader import get_templates
    
    templates = get_templates()
    
    # Intentar renderizar página de error personalizada
    try:
        context = {
            "request": request,
            "status_code": 500,
            "detail": "Ocurrió un error inesperado",
            "is_authenticated": False,
            "user": None
        }
        
        return templates.TemplateResponse(
            "errors/error.html",
            context,
            status_code=500
        )
    except Exception as template_error:
        # Si falla el template, devolver HTML simple
        logger.error(f"Error al renderizar template de error: {template_error}")
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error 500</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; text-align: center; }}
                h1 {{ color: #e74c3c; }}
                p {{ color: #555; }}
                a {{ color: #3498db; text-decoration: none; }}
                .error-details {{ 
                    background: #f8f9fa; 
                    padding: 20px; 
                    border-radius: 8px; 
                    margin: 20px auto;
                    max-width: 600px;
                    text-align: left;
                }}
            </style>
        </head>
        <body>
            <h1>Error 500</h1>
            <p>Ocurrió un error inesperado en el servidor</p>
            <div class="error-details">
                <strong>Detalles técnicos:</strong><br>
                {str(exc)[:200]}
            </div>
            <p><a href="/">Volver al inicio</a></p>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=500)

def setup_error_handlers(app):
    """
    Configurar handlers de error en la aplicación FastAPI
    
    Args:
        app: Instancia de FastAPI
    """
    # Handler para errores de validación de Pydantic
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # Handler para excepciones HTTP de FastAPI
    app.add_exception_handler(HTTPException, http_exception_handler)
    
    # Handler para excepciones HTTP de Starlette
    app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
    
    # Handler para excepciones genéricas
    app.add_exception_handler(Exception, generic_exception_handler)
    
    logger.info("✅ Handlers de error configurados correctamente")
