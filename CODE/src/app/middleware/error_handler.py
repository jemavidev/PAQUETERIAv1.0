# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Handler de Errores
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

async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handler para excepciones HTTP de Starlette
    
    Args:
        request: Request de FastAPI
        exc: Excepción HTTP de Starlette
        
    Returns:
        JSONResponse con error formateado
    """
    logger.warning(f"Error Starlette en {request.url}: {exc}")
    
    # Crear mensaje simple
    simple_message = "Algo salió mal. Intenta nuevamente."
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": simple_message
        }
    )

async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler para excepciones genéricas
    
    Args:
        request: Request de FastAPI
        exc: Excepción genérica
        
    Returns:
        JSONResponse con error formateado
    """
    logger.error(f"Error inesperado en {request.url}: {exc}", exc_info=True)
    
    # Crear mensaje simple
    simple_message = "Ocurrió un error inesperado. Intenta nuevamente."
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": simple_message
        }
    )

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
