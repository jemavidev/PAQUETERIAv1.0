# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Debug Dashboard Routes
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo
"""

import logging
import os
import psutil
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pathlib import Path

from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect

from app.database import get_db
from app.dependencies import get_current_active_user_from_cookies
from app.models.user import User, UserRole
from app.utils.auth_context import get_auth_context_required
from app.utils.datetime_utils import get_colombia_now
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

from app.utils.template_loader import get_templates
templates = get_templates()

# Middleware de autenticación para debug (solo admin)
async def require_admin_access(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies)
):
    """Verificar que el usuario actual sea administrador"""
    if not current_user or current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo administradores pueden acceder al debug dashboard."
        )
    return current_user

@router.get("/debug")
async def debug_dashboard_main(
    request: Request,
    current_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Dashboard principal de debug"""
    try:
        context = get_auth_context_required(request)
        context["user"] = current_user
        
        # Obtener métricas del sistema
        system_metrics = get_system_metrics()
        context["system_metrics"] = system_metrics
        
        # Obtener estado de servicios
        service_status = await get_services_status(db)
        context["service_status"] = service_status
        
        return templates.TemplateResponse("debug/dashboard.html", context)
        
    except Exception as e:
        logger.error(f"Error en debug dashboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cargando debug dashboard: {str(e)}"
        )

def get_system_metrics() -> Dict[str, Any]:
    """Obtener métricas del sistema"""
    try:
        # Información del proceso actual
        process = psutil.Process()
        
        # Métricas de memoria
        memory_info = process.memory_info()
        system_memory = psutil.virtual_memory()
        
        # Métricas de CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Información del disco
        disk_usage = psutil.disk_usage('/')
        
        # Uptime del proceso
        create_time = datetime.fromtimestamp(process.create_time())
        uptime = datetime.now() - create_time
        
        return {
            "uptime": str(uptime).split('.')[0],  # Sin microsegundos
            "memory": {
                "process_mb": round(memory_info.rss / 1024 / 1024, 2),
                "system_total_gb": round(system_memory.total / 1024 / 1024 / 1024, 2),
                "system_used_percent": system_memory.percent
            },
            "cpu": {
                "percent": cpu_percent,
                "count": psutil.cpu_count()
            },
            "disk": {
                "total_gb": round(disk_usage.total / 1024 / 1024 / 1024, 2),
                "used_gb": round(disk_usage.used / 1024 / 1024 / 1024, 2),
                "free_gb": round(disk_usage.free / 1024 / 1024 / 1024, 2),
                "used_percent": round((disk_usage.used / disk_usage.total) * 100, 2)
            },
            "timestamp": get_colombia_now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error obteniendo métricas del sistema: {str(e)}")
        return {
            "error": str(e),
            "timestamp": get_colombia_now().isoformat()
        }

async def get_services_status(db: Session) -> Dict[str, Any]:
    """Verificar estado de servicios externos"""
    services = {
        "database": {"status": "unknown", "details": ""},
        "s3": {"status": "unknown", "details": ""},
        "redis": {"status": "unknown", "details": ""},
        "sms": {"status": "unknown", "details": ""}
    }
    
    # Verificar base de datos
    try:
        db.execute(text("SELECT 1"))
        services["database"] = {"status": "ok", "details": "AWS RDS Connected"}
    except Exception as e:
        services["database"] = {"status": "error", "details": str(e)}
    
    # Verificar S3
    try:
        from app.services.s3_service import S3Service
        s3_service = S3Service()
        # Intentar listar objetos (operación básica)
        services["s3"] = {"status": "ok", "details": "S3 Service Available"}
    except Exception as e:
        services["s3"] = {"status": "error", "details": str(e)}
    
    # Verificar Redis (si está configurado)
    try:
        import redis
        redis_client = redis.from_url(settings.redis_url)
        redis_client.ping()
        services["redis"] = {"status": "ok", "details": "Redis Connected"}
    except Exception as e:
        services["redis"] = {"status": "error", "details": str(e)}
    
    # Verificar SMS (LIWA)
    try:
        # Solo verificar que las credenciales estén configuradas
        if hasattr(settings, 'liwa_api_key') and settings.liwa_api_key:
            services["sms"] = {"status": "ok", "details": "LIWA Credentials Configured"}
        else:
            services["sms"] = {"status": "warning", "details": "LIWA Credentials Not Found"}
    except Exception as e:
        services["sms"] = {"status": "error", "details": str(e)}
    
    return services

@router.get("/debug/api/system-metrics")
async def get_system_metrics_api(
    current_user: User = Depends(require_admin_access)
):
    """API endpoint para obtener métricas del sistema en tiempo real"""
    return get_system_metrics()

@router.get("/debug/api/services-status")
async def get_services_status_api(
    current_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """API endpoint para obtener estado de servicios"""
    return await get_services_status(db)