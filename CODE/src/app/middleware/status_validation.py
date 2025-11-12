# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Middleware de Validación de Estados
Versión: 4.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo

Middleware para validar y corregir inconsistencias de estado
en las respuestas de la API.
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.package_status_service import PackageStatusService
from sqlalchemy.orm import Session
from app.database import get_db
import json
import logging

logger = logging.getLogger(__name__)


class StatusValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware que valida y corrige inconsistencias de estado
    en las respuestas de la API.
    """
    
    def __init__(self, app, validate_endpoints: list = None):
        super().__init__(app)
        # Endpoints que requieren validación de estado
        self.validate_endpoints = validate_endpoints or [
            "/api/announcements/search/package",
            "/api/packages/",
            "/api/dashboard/packages"
        ]
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Solo validar endpoints específicos
        if not any(endpoint in str(request.url.path) for endpoint in self.validate_endpoints):
            return response
        
        # Solo validar respuestas JSON exitosas
        if response.status_code != 200:
            return response
        
        try:
            # Obtener el cuerpo de la respuesta
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            # Parsear JSON
            try:
                data = json.loads(body.decode())
            except json.JSONDecodeError:
                return response
            
            # Validar y corregir si es necesario
            corrected_data = await self._validate_and_correct_status(data, request)
            
            if corrected_data != data:
                logger.warning(f"Status validation corrected data for {request.url.path}")
                # Crear nueva respuesta con datos corregidos
                corrected_body = json.dumps(corrected_data, ensure_ascii=False).encode()
                return Response(
                    content=corrected_body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type="application/json"
                )
            
        except Exception as e:
            logger.error(f"Error in status validation middleware: {e}")
        
        return response
    
    async def _validate_and_correct_status(self, data: dict, request: Request) -> dict:
        """
        Validar y corregir inconsistencias de estado en los datos.
        """
        try:
            # Obtener sesión de base de datos
            db = next(get_db())
            
            # Buscar tracking_code en los datos
            tracking_code = None
            if "announcement" in data and data["announcement"]:
                tracking_code = data["announcement"].get("tracking_code")
            elif "current_status" in data and "announcement" in data:
                tracking_code = data.get("announcement", {}).get("tracking_code")
            
            if not tracking_code:
                return data
            
            # Obtener estado correcto usando el servicio centralizado
            effective_status = PackageStatusService.get_effective_status(db, tracking_code)
            
            # Corregir current_status si es necesario
            if "current_status" in data:
                correct_status = effective_status["status"]
                if data["current_status"] != correct_status:
                    logger.warning(f"Correcting status for {tracking_code}: {data['current_status']} -> {correct_status}")
                    data["current_status"] = correct_status
            
            # Corregir allows_inquiries si está presente
            if "inquiry_info" in data:
                data["inquiry_info"]["allows_inquiries"] = effective_status["allows_inquiries"]
            
            # Corregir query_type si está presente
            if "query_type" in data:
                data["query_type"]["should_show_inquiry_form"] = effective_status["allows_inquiries"]
                data["query_type"]["should_show_history"] = effective_status["allows_inquiries"]
            
            db.close()
            return data
            
        except Exception as e:
            logger.error(f"Error validating status: {e}")
            return data


def setup_status_validation_middleware(app, validate_endpoints: list = None):
    """
    Configurar el middleware de validación de estados.
    
    Args:
        app: Aplicación FastAPI
        validate_endpoints: Lista de endpoints a validar
    """
    app.add_middleware(
        StatusValidationMiddleware,
        validate_endpoints=validate_endpoints
    )
    logger.info("Status validation middleware configured")
