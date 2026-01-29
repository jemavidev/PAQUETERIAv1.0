"""
Endpoint para sincronizar datos de producción a staging
VERSIÓN ULTRA SIMPLE - Llama a un script externo
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import os
import logging
import asyncio
import subprocess

router = APIRouter()
logger = logging.getLogger(__name__)

# Estado de la sincronización
sync_status = {
    "is_running": False,
    "last_sync": None,
    "last_result": None,
    "progress": 0,
    "message": ""
}

async def run_sync():
    """
    Ejecuta el script de sincronización en el host
    """
    global sync_status
    
    try:
        sync_status["is_running"] = True
        sync_status["progress"] = 10
        sync_status["message"] = "Iniciando sincronización..."
        
        logger.info("🔄 Iniciando sincronización de datos...")
        
        # Ejecutar script en el host
        # El script debe estar en ~/sync_simple_directo.py en el servidor
        script_path = "/home/rocky/sync_simple_directo.py"
        
        sync_status["progress"] = 20
        sync_status["message"] = "Ejecutando sincronización..."
        
        # Ejecutar el script
        result = await asyncio.create_subprocess_exec(
            "python3", script_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await result.communicate()
        
        if result.returncode == 0:
            sync_status["progress"] = 100
            sync_status["last_result"] = "success"
            sync_status["message"] = "Sincronización completada exitosamente"
            sync_status["last_sync"] = __import__('datetime').datetime.now().isoformat()
            logger.info("✅ Sincronización completada exitosamente")
        else:
            error_msg = stderr.decode() if stderr else "Error desconocido"
            raise Exception(f"Error en sincronización: {error_msg}")
        
    except Exception as e:
        logger.error(f"❌ Error en sincronización: {e}")
        sync_status["last_result"] = f"error: {str(e)}"
        sync_status["progress"] = 0
        sync_status["message"] = str(e)
        
    finally:
        sync_status["is_running"] = False


@router.post("/api/staging/sync")
async def sync_from_production(background_tasks: BackgroundTasks):
    """
    Sincroniza datos de producción a staging
    Solo disponible en entorno staging
    """
    # Verificar que estamos en staging
    environment = os.getenv("ENVIRONMENT", "production")
    db_name = os.getenv("POSTGRES_DB", "")
    
    if environment != "staging" or db_name != "paqueteria_staging":
        raise HTTPException(
            status_code=403,
            detail="Esta operación solo está disponible en el entorno staging"
        )
    
    # Verificar si ya hay una sincronización en curso
    if sync_status["is_running"]:
        return JSONResponse({
            "status": "running",
            "message": sync_status["message"],
            "progress": sync_status["progress"]
        })
    
    # Iniciar sincronización en segundo plano
    background_tasks.add_task(run_sync)
    
    return JSONResponse({
        "status": "started",
        "message": "Sincronización iniciada. Esto puede tardar varios minutos.",
        "progress": 0
    })


@router.get("/api/staging/sync/status")
async def get_sync_status():
    """
    Obtiene el estado de la sincronización
    """
    # Verificar que estamos en staging
    environment = os.getenv("ENVIRONMENT", "production")
    db_name = os.getenv("POSTGRES_DB", "")
    
    if environment != "staging" or db_name != "paqueteria_staging":
        raise HTTPException(
            status_code=403,
            detail="Esta operación solo está disponible en el entorno staging"
        )
    
    return JSONResponse({
        "is_running": sync_status["is_running"],
        "progress": sync_status["progress"],
        "message": sync_status["message"],
        "last_sync": sync_status["last_sync"],
        "last_result": sync_status["last_result"]
    })
