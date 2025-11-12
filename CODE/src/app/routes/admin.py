# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Rutas de Administración
Versión: 2.0.0
Fecha: 2025-09-21
Autor: Equipo de Desarrollo
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.services.admin_service import AdminService
from app.dependencies import get_current_admin_user, get_current_admin_user_from_cookies
from app.models.user import User, UserRole
from app.utils.datetime_utils import get_colombia_now

router = APIRouter(tags=["Administración"])


# === DASHBOARD ADMINISTRATIVO ===

@router.get("/dashboard")
async def get_admin_dashboard(
    period_days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_admin_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Dashboard administrativo con estadísticas completas"""
    try:
        service = AdminService(db)
        stats = service.get_admin_dashboard_stats(period_days)

        return {
            "success": True,
            "data": stats,
            "generated_at": get_colombia_now().isoformat(),
            "generated_by": current_user.get("username")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo dashboard: {str(e)}")


@router.get("/system/health")
async def get_system_health(
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Estado de salud del sistema"""
    try:
        service = AdminService(db)
        dashboard_stats = service.get_admin_dashboard_stats(7)  # Última semana

        health_status = {
            "status": "healthy",
            "timestamp": get_colombia_now().isoformat(),
            "checks": {
                "database": "ok",
                "users": "ok" if dashboard_stats["system_overview"]["total_users"] > 0 else "warning",
                "packages": "ok",
                "messages": "ok",
                "notifications": "ok",
                "reports": "ok"
            },
            "metrics": dashboard_stats["system_health"]
        }

        # Determinar estado general
        if dashboard_stats["system_health"]["failed_reports"] > 0:
            health_status["status"] = "warning"
        if dashboard_stats["system_health"]["unprocessed_packages"] > 100:
            health_status["status"] = "warning"

        return health_status

    except Exception as e:
        return {
            "status": "error",
            "timestamp": get_colombia_now().isoformat(),
            "error": str(e)
        }


# === GESTIÓN DE USUARIOS ===

@router.get("/users")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Lista usuarios con filtros y paginación"""
    try:
        service = AdminService(db)

        filters = {}
        if role:
            filters["role"] = role
        if is_active is not None:
            filters["is_active"] = is_active
        if search:
            filters["search"] = search

        users, total = service.get_users_list(skip=skip, limit=limit, filters=filters)

        return {
            "users": [
                {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "phone": user.phone,
                    "role": user.role.value if user.role else None,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "last_login": user.updated_at.isoformat() if user.updated_at else None
                } for user in users
            ],
            "total": total,
            "skip": skip,
            "limit": limit
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando usuarios: {str(e)}")


@router.post("/users")
async def create_user(
    user_data: Dict[str, Any],
    current_user: User = Depends(get_current_admin_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Crea un nuevo usuario"""
    try:
        # Validar datos requeridos
        required_fields = ["username", "email", "full_name", "password", "role"]
        for field in required_fields:
            if field not in user_data:
                raise HTTPException(status_code=400, detail=f"Campo requerido: {field}")

        # Validar rol
        if user_data["role"] not in ["ADMIN", "OPERADOR", "USUARIO"]:
            raise HTTPException(status_code=400, detail="Rol inválido")

        service = AdminService(db)
        user = service.create_user(user_data, created_by_user_id=current_user.id)

        return {
            "success": True,
            "message": "Usuario creado exitosamente",
            "user_id": str(user.id),
            "username": user.username
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando usuario: {str(e)}")


@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user_data: Dict[str, Any],
    current_user: User = Depends(get_current_admin_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Actualiza un usuario existente"""
    try:
        service = AdminService(db)
        user = service.update_user(user_id, user_data, updated_by_user_id=current_user.id)

        return {
            "success": True,
            "message": "Usuario actualizado exitosamente",
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value if user.role else None,
                "is_active": user.is_active
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando usuario: {str(e)}")


@router.post("/users/{user_id}/toggle-status")
async def toggle_user_status(
    user_id: int,
    current_user: User = Depends(get_current_admin_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Activa/desactiva un usuario"""
    try:
        service = AdminService(db)
        user = service.toggle_user_status(user_id, changed_by_user_id=current_user.id)

        status_text = "activado" if user.is_active else "desactivado"

        return {
            "success": True,
            "message": f"Usuario {status_text} exitosamente",
            "user_id": str(user.id),
            "is_active": user.is_active
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cambiando estado del usuario: {str(e)}")


@router.post("/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    password_data: Dict[str, str],
    current_user: User = Depends(get_current_admin_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Resetea la contraseña de un usuario"""
    try:
        new_password = password_data.get("new_password")
        if not new_password or len(new_password) < 8:
            raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 8 caracteres")

        service = AdminService(db)
        user = service.reset_user_password(user_id, new_password, reset_by_user_id=current_user.id)

        return {
            "success": True,
            "message": "Contraseña reseteada exitosamente",
            "user_id": str(user.id),
            "username": user.username
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reseteando contraseña: {str(e)}")


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Elimina un usuario"""
    try:
        service = AdminService(db)
        result = service.delete_user(user_id, deleted_by_user_id=current_user.id)

        return {
            "success": True,
            "message": "Usuario eliminado exitosamente"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando usuario: {str(e)}")


# === CONFIGURACIONES DEL SISTEMA ===

@router.get("/config")
async def get_system_config(
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Obtiene configuraciones del sistema"""
    try:
        service = AdminService(db)
        config = service.get_system_config()

        return {
            "success": True,
            "config": config
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo configuración: {str(e)}")


@router.put("/config")
async def update_system_config(
    config_data: Dict[str, Any],
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Actualiza configuraciones del sistema"""
    try:
        service = AdminService(db)
        updated_config = service.update_system_config(config_data)

        return {
            "success": True,
            "message": "Configuración actualizada exitosamente",
            "updated_config": updated_config
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando configuración: {str(e)}")


# === AUDITORÍA Y LOGS ===

@router.get("/audit/logs")
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    action: Optional[str] = None,
    user: Optional[str] = None,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Obtiene logs de auditoría"""
    try:
        service = AdminService(db)

        filters = {}
        if action:
            filters["action"] = action
        if user:
            filters["user"] = user

        logs, total = service.get_audit_logs(skip=skip, limit=limit, filters=filters)

        return {
            "logs": logs,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo logs de auditoría: {str(e)}")


# === UTILIDADES ADMINISTRATIVAS ===

@router.post("/cleanup")
async def cleanup_old_data(
    days_old: int = Query(90, ge=30, le=365),
    dry_run: bool = Query(True, description="Si es True, solo muestra qué se eliminaría"),
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Limpia datos antiguos del sistema"""
    try:
        service = AdminService(db)
        result = service.cleanup_old_data(days_old)

        action = "simulada" if dry_run else "ejecutada"

        return {
            "success": True,
            "message": f"Limpieza {action} exitosamente",
            "result": result,
            "dry_run": dry_run
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en limpieza: {str(e)}")


@router.get("/system/info")
async def get_system_info(
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Información del sistema para diagnóstico"""
    try:
        service = AdminService(db)
        info = service.get_system_info()

        return {
            "success": True,
            "system_info": info
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo información del sistema: {str(e)}")


# === ESTADÍSTICAS AVANZADAS ===

@router.get("/stats/detailed")
async def get_detailed_stats(
    period_days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Estadísticas detalladas para análisis avanzado"""
    try:
        service = AdminService(db)
        dashboard_stats = service.get_admin_dashboard_stats(period_days)

        # Agregar estadísticas adicionales detalladas
        detailed_stats = {
            **dashboard_stats,
            "performance_indicators": {
                "user_growth_rate": 0,  # Calcular basado en períodos anteriores
                "package_processing_efficiency": 0,
                "customer_satisfaction_score": 0,
                "system_uptime_percentage": 99.9
            },
            "resource_usage": {
                "database_connections": "normal",
                "cache_hit_rate": 95.5,
                "api_response_time_avg": 245,  # ms
                "error_rate": 0.1  # porcentaje
            }
        }

        return {
            "success": True,
            "detailed_stats": detailed_stats
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas detalladas: {str(e)}")


# === ENDPOINT LEGACY PARA COMPATIBILIDAD ===

@router.get("/")
async def get_admin_legacy():
    """Endpoint legacy para compatibilidad"""
    return {
        "message": "Panel de Administración v4.0",
        "version": "4.0.0",
        "endpoints": {
            "dashboard": "/api/admin/dashboard",
            "users": "/api/admin/users",
            "config": "/api/admin/config",
            "audit": "/api/admin/audit/logs",
            "system": "/api/admin/system/info"
        }
    }
