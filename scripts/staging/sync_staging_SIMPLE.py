"""
Endpoint para sincronizar datos de producción a staging
VERSIÓN SIMPLE - Ejecuta directamente en el contenedor
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
    Ejecuta la sincronización directamente usando pg_dump y pg_restore
    """
    global sync_status
    
    try:
        sync_status["is_running"] = True
        sync_status["progress"] = 10
        sync_status["message"] = "Iniciando sincronización..."
        
        logger.info("🔄 Iniciando sincronización de datos...")
        
        # Obtener credenciales
        host = os.getenv("POSTGRES_HOST", "ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com")
        user = os.getenv("POSTGRES_USER", "jveyes")
        password = os.getenv("POSTGRES_PASSWORD", "a?HC!2.*1#?[==:|289qAI=)#V4kDzl$")
        
        # Configurar PGPASSWORD para los comandos
        env = os.environ.copy()
        env["PGPASSWORD"] = password
        
        # Paso 1: Exportar producción
        sync_status["progress"] = 30
        sync_status["message"] = "Exportando base de datos de producción..."
        logger.info("📦 Exportando producción...")
        
        dump_cmd = [
            "pg_dump",
            "-h", host,
            "-U", user,
            "-d", "paqueteria_v4",
            "-F", "c",
            "-f", "/tmp/backup.dump",
            "--no-owner",
            "--no-acl"
        ]
        
        result = subprocess.run(
            dump_cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos máximo
        )
        
        if result.returncode != 0:
            raise Exception(f"Error en pg_dump: {result.stderr}")
        
        logger.info("✅ Exportación completada")
        
        # Paso 2: Restaurar en staging
        sync_status["progress"] = 70
        sync_status["message"] = "Restaurando en staging..."
        logger.info("📥 Restaurando en staging...")
        
        restore_cmd = [
            "pg_restore",
            "-h", host,
            "-U", user,
            "-d", "paqueteria_staging",
            "/tmp/backup.dump",
            "--clean",
            "--if-exists",
            "--no-owner",
            "--no-acl"
        ]
        
        result = subprocess.run(
            restore_cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos máximo
        )
        
        # pg_restore puede retornar warnings, ignorarlos
        if result.returncode not in [0, 1]:
            raise Exception(f"Error en pg_restore: {result.stderr}")
        
        logger.info("✅ Restauración completada")
        
        # Paso 3: Limpiar archivo temporal
        try:
            os.remove("/tmp/backup.dump")
        except:
            pass
        
        # Completado
        sync_status["progress"] = 100
        sync_status["last_result"] = "success"
        sync_status["message"] = "Sincronización completada exitosamente"
        sync_status["last_sync"] = __import__('datetime').datetime.now().isoformat()
        
        logger.info("✅ Sincronización completada exitosamente")
        
    except subprocess.TimeoutExpired:
        logger.error("❌ Timeout: La sincronización tardó demasiado")
        sync_status["last_result"] = "error: Timeout - La sincronización tardó más de 5 minutos"
        sync_status["progress"] = 0
        sync_status["message"] = "Timeout: La sincronización tardó demasiado"
        
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
