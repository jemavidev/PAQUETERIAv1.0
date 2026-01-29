"""
Endpoint para sincronizar datos de producción a staging
Solo disponible en entorno staging
VERSIÓN SIMPLE: Llama al script sync_manual.sh en el host
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
    Ejecuta el script de sincronización directamente en el host
    """
    global sync_status
    
    try:
        sync_status["is_running"] = True
        sync_status["progress"] = 10
        sync_status["message"] = "Iniciando sincronización..."
        
        logger.info("🔄 Iniciando sincronización de datos...")
        
        # Verificar que el script existe en /tmp (compartido con el host)
        script_path = "/tmp/sync_manual.sh"
        
        if not os.path.exists(script_path):
            raise Exception(f"Script no encontrado: {script_path}. Copia ~/sync_manual.sh a /tmp/ en el host.")
        
        sync_status["progress"] = 20
        sync_status["message"] = "Ejecutando sincronización..."
        logger.info("📦 Ejecutando script de sincronización...")
        
        # Obtener credenciales de la base de datos
        db_host = os.getenv("POSTGRES_HOST")
        db_user = os.getenv("POSTGRES_USER")
        db_pass = os.getenv("POSTGRES_PASSWORD")
        
        if not all([db_host, db_user, db_pass]):
            raise Exception("Credenciales de base de datos no configuradas")
        
        # Ejecutar pg_dump y pg_restore directamente usando Docker con postgres:17-alpine
        # que ya tiene las herramientas instaladas
        
        sync_status["progress"] = 30
        sync_status["message"] = "Exportando producción..."
        logger.info("📦 Exportando producción...")
        
        # Paso 1: Exportar producción
        dump_process = await asyncio.create_subprocess_exec(
            "docker", "run", "--rm",
            "-e", f"PGPASSWORD={db_pass}",
            "-v", "/tmp:/backup",
            "postgres:17-alpine",
            "pg_dump",
            "-h", db_host,
            "-U", db_user,
            "-d", "paqueteria_v4",
            "-F", "c",
            "-f", "/backup/staging_backup.dump",
            "--no-owner",
            "--no-acl",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(dump_process.communicate(), timeout=300)
        
        if dump_process.returncode != 0:
            error_msg = stderr.decode() if stderr else "Error desconocido"
            raise Exception(f"Error exportando: {error_msg}")
        
        logger.info("✅ Exportación completada")
        
        sync_status["progress"] = 70
        sync_status["message"] = "Restaurando en staging..."
        logger.info("📥 Restaurando en staging...")
        
        # Paso 2: Restaurar en staging
        restore_process = await asyncio.create_subprocess_exec(
            "docker", "run", "--rm",
            "-e", f"PGPASSWORD={db_pass}",
            "-v", "/tmp:/backup",
            "postgres:17-alpine",
            "pg_restore",
            "-h", db_host,
            "-U", db_user,
            "-d", "paqueteria_staging",
            "/backup/staging_backup.dump",
            "--clean",
            "--if-exists",
            "--no-owner",
            "--no-acl",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(restore_process.communicate(), timeout=300)
        
        # pg_restore puede retornar 1 con warnings, eso es OK
        if restore_process.returncode > 1:
            error_msg = stderr.decode() if stderr else "Error desconocido"
            raise Exception(f"Error restaurando: {error_msg}")
        
        logger.info("✅ Restauración completada")
        
        # Limpiar archivo temporal
        try:
            if os.path.exists("/tmp/staging_backup.dump"):
                os.remove("/tmp/staging_backup.dump")
        except:
            pass
        
        sync_status["progress"] = 100
        sync_status["last_result"] = "success"
        sync_status["message"] = "Sincronización completada exitosamente"
        sync_status["last_sync"] = __import__('datetime').datetime.now().isoformat()
        logger.info("✅ Sincronización completada exitosamente")
        
    except asyncio.TimeoutError:
        logger.error("❌ Timeout: La sincronización tardó más de 10 minutos")
        sync_status["last_result"] = "error: Timeout - La sincronización tardó demasiado"
        sync_status["progress"] = 0
        sync_status["message"] = "Timeout - La sincronización tardó demasiado"
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
    
    NOTA: Requiere que el script sync_staging_cron.sh esté corriendo en el host
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
