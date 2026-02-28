# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Rutas de Sincronización de Base de Datos
Versión: 1.0.0
Fecha: 2026-02-28
Autor: Equipo de Desarrollo
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any
import subprocess
import os
import logging
from datetime import datetime

from app.database import get_db
from app.dependencies import get_current_admin_user_from_cookies
from app.models.user import User
from app.utils.datetime_utils import get_colombia_now

router = APIRouter(tags=["Sincronización"])
logger = logging.getLogger(__name__)

# Estado de sincronización en memoria
sync_status = {
    "is_running": False,
    "last_sync": None,
    "last_result": None,
    "progress": None
}


def run_sync_script():
    """Ejecuta el script de sincronización en background"""
    global sync_status
    
    try:
        sync_status["is_running"] = True
        sync_status["progress"] = "Iniciando sincronización..."
        
        # Ruta al script de sincronización
        script_path = os.path.join(
            os.path.dirname(__file__),
            "../../../..",
            "scripts/database/sync_rds_prod_to_staging.sh"
        )
        
        # Verificar que el script existe
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script no encontrado: {script_path}")
        
        # Hacer el script ejecutable
        os.chmod(script_path, 0o755)
        
        logger.info(f"🔄 Ejecutando script de sincronización: {script_path}")
        sync_status["progress"] = "Ejecutando script de sincronización..."
        
        # Ejecutar el script en modo automático
        result = subprocess.run(
            [script_path, "--auto"],
            capture_output=True,
            text=True,
            timeout=1800  # 30 minutos máximo
        )
        
        if result.returncode == 0:
            sync_status["last_result"] = {
                "success": True,
                "message": "Sincronización completada exitosamente",
                "output": result.stdout,
                "timestamp": get_colombia_now().isoformat()
            }
            logger.info("✅ Sincronización completada exitosamente")
        else:
            sync_status["last_result"] = {
                "success": False,
                "message": "Error en la sincronización",
                "error": result.stderr,
                "output": result.stdout,
                "timestamp": get_colombia_now().isoformat()
            }
            logger.error(f"❌ Error en sincronización: {result.stderr}")
        
    except subprocess.TimeoutExpired:
        sync_status["last_result"] = {
            "success": False,
            "message": "Timeout: La sincronización tardó más de 30 minutos",
            "timestamp": get_colombia_now().isoformat()
        }
        logger.error("❌ Timeout en sincronización")
        
    except Exception as e:
        sync_status["last_result"] = {
            "success": False,
            "message": f"Error ejecutando sincronización: {str(e)}",
            "timestamp": get_colombia_now().isoformat()
        }
        logger.error(f"❌ Error en sincronización: {str(e)}", exc_info=True)
        
    finally:
        sync_status["is_running"] = False
        sync_status["last_sync"] = get_colombia_now().isoformat()
        sync_status["progress"] = None


@router.post("/sync/database")
async def sync_database(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_admin_user_from_cookies),
    db: Session = Depends(get_db)
):
    """
    Sincroniza la base de datos de producción a staging
    Solo disponible para administradores en entorno staging
    """
    try:
        # Verificar que es un administrador
        if current_user.role.value != "ADMIN":
            raise HTTPException(
                status_code=403,
                detail="Acceso denegado. Solo administradores pueden sincronizar la base de datos."
            )
        
        # Verificar que estamos en staging
        environment = os.getenv("ENVIRONMENT", "production")
        if environment != "staging":
            raise HTTPException(
                status_code=403,
                detail="Esta operación solo está disponible en el entorno de staging."
            )
        
        # Verificar que no hay una sincronización en curso
        if sync_status["is_running"]:
            return JSONResponse(
                status_code=409,
                content={
                    "success": False,
                    "message": "Ya hay una sincronización en curso",
                    "progress": sync_status["progress"]
                }
            )
        
        # Iniciar sincronización en background
        background_tasks.add_task(run_sync_script)
        
        logger.info(f"🔄 Sincronización iniciada por usuario: {current_user.username}")
        
        return {
            "success": True,
            "message": "Sincronización iniciada en segundo plano",
            "started_by": current_user.username,
            "started_at": get_colombia_now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error iniciando sincronización: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error iniciando sincronización: {str(e)}"
        )


@router.get("/sync/status")
async def get_sync_status(
    current_user: User = Depends(get_current_admin_user_from_cookies)
):
    """
    Obtiene el estado actual de la sincronización
    """
    try:
        # Verificar que es un administrador
        if current_user.role.value != "ADMIN":
            raise HTTPException(
                status_code=403,
                detail="Acceso denegado. Solo administradores pueden ver el estado de sincronización."
            )
        
        return {
            "success": True,
            "status": {
                "is_running": sync_status["is_running"],
                "progress": sync_status["progress"],
                "last_sync": sync_status["last_sync"],
                "last_result": sync_status["last_result"]
            },
            "environment": os.getenv("ENVIRONMENT", "production")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error obteniendo estado de sincronización: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estado: {str(e)}"
        )


@router.get("/sync/history")
async def get_sync_history(
    current_user: User = Depends(get_current_admin_user_from_cookies)
):
    """
    Obtiene el historial de sincronizaciones
    """
    try:
        # Verificar que es un administrador
        if current_user.role.value != "ADMIN":
            raise HTTPException(
                status_code=403,
                detail="Acceso denegado."
            )
        
        # Por ahora solo retornamos la última sincronización
        # En el futuro se puede guardar en BD
        history = []
        if sync_status["last_result"]:
            history.append(sync_status["last_result"])
        
        return {
            "success": True,
            "history": history,
            "total": len(history)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error obteniendo historial: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo historial: {str(e)}"
        )
