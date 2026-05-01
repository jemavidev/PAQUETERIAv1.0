"""
╔════════════════════════════════════════════════════════════════════════════╗
║                    ADMIN: SINCRONIZACIÓN DE BD                             ║
║                  Endpoint para sincronizar BD en Staging                   ║
╚════════════════════════════════════════════════════════════════════════════╝

PROPÓSITO:
- Ejecutar script de sincronización BD producción → staging
- Solo disponible en entorno STAGING
- Solo para usuarios ADMIN
- Streaming de logs en tiempo real

SEGURIDAD:
- Verificar ENVIRONMENT=staging
- Verificar rol admin
- Rate limiting (1 ejecución cada 5 minutos)
- Logs de auditoría

USO:
POST /api/admin/sync-database
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import subprocess
import os
import asyncio
from datetime import datetime, timedelta
from typing import AsyncGenerator

from app.database import get_db
from app.models import User
from app.dependencies import get_current_user
from app.config import settings

router = APIRouter(prefix="/api/admin", tags=["admin-sync"])

# Rate limiting simple (en memoria)
last_sync_time = None
SYNC_COOLDOWN_MINUTES = 5

# ════════════════════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ════════════════════════════════════════════════════════════════════════════

def check_environment():
    """Verificar que estamos en staging"""
    if settings.environment != "staging":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta funcionalidad solo está disponible en el entorno de staging"
        )

def check_admin_role(current_user: User):
    """Verificar que el usuario es admin"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden ejecutar esta acción"
        )

def check_rate_limit():
    """Verificar rate limiting"""
    global last_sync_time
    
    if last_sync_time:
        time_since_last_sync = datetime.now() - last_sync_time
        if time_since_last_sync < timedelta(minutes=SYNC_COOLDOWN_MINUTES):
            remaining = SYNC_COOLDOWN_MINUTES - (time_since_last_sync.seconds // 60)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Debes esperar {remaining} minutos antes de ejecutar otra sincronización"
            )

async def stream_sync_logs() -> AsyncGenerator[str, None]:
    """
    Ejecutar script de sincronización y hacer streaming de logs
    """
    global last_sync_time
    
    # Actualizar timestamp
    last_sync_time = datetime.now()
    
    # Ruta al script
    script_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        "scripts",
        "database",
        "sync_production_to_staging.sh"
    )
    
    if not os.path.exists(script_path):
        yield f"data: {{\"type\": \"error\", \"message\": \"Script no encontrado: {script_path}\"}}\n\n"
        return
    
    try:
        # Iniciar proceso
        yield f"data: {{\"type\": \"info\", \"message\": \"Iniciando sincronización...\"}}\n\n"
        
        # Ejecutar script con --auto para evitar confirmación
        process = await asyncio.create_subprocess_exec(
            script_path,
            "--auto",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=os.path.dirname(script_path)
        )
        
        # Leer output línea por línea
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            
            line_text = line.decode('utf-8').strip()
            if line_text:
                # Detectar tipo de mensaje por el emoji/símbolo
                msg_type = "info"
                if "✓" in line_text or "success" in line_text.lower():
                    msg_type = "success"
                elif "✗" in line_text or "error" in line_text.lower():
                    msg_type = "error"
                elif "⚠" in line_text or "warning" in line_text.lower():
                    msg_type = "warning"
                
                # Enviar al cliente
                yield f"data: {{\"type\": \"{msg_type}\", \"message\": \"{line_text}\"}}\n\n"
        
        # Esperar a que termine
        await process.wait()
        
        if process.returncode == 0:
            yield f"data: {{\"type\": \"success\", \"message\": \"✅ Sincronización completada exitosamente\"}}\n\n"
            yield f"data: {{\"type\": \"complete\", \"message\": \"done\"}}\n\n"
        else:
            yield f"data: {{\"type\": \"error\", \"message\": \"❌ Error en la sincronización (código: {process.returncode})\"}}\n\n"
            yield f"data: {{\"type\": \"complete\", \"message\": \"error\"}}\n\n"
            
    except Exception as e:
        yield f"data: {{\"type\": \"error\", \"message\": \"Error: {str(e)}\"}}\n\n"
        yield f"data: {{\"type\": \"complete\", \"message\": \"error\"}}\n\n"

# ════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ════════════════════════════════════════════════════════════════════════════

@router.get("/sync-database/status")
async def get_sync_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener estado de sincronización
    """
    check_environment()
    check_admin_role(current_user)
    
    global last_sync_time
    
    can_sync = True
    cooldown_remaining = 0
    
    if last_sync_time:
        time_since_last_sync = datetime.now() - last_sync_time
        if time_since_last_sync < timedelta(minutes=SYNC_COOLDOWN_MINUTES):
            can_sync = False
            cooldown_remaining = SYNC_COOLDOWN_MINUTES - (time_since_last_sync.seconds // 60)
    
    return {
        "can_sync": can_sync,
        "last_sync": last_sync_time.isoformat() if last_sync_time else None,
        "cooldown_remaining_minutes": cooldown_remaining,
        "environment": settings.environment
    }

@router.post("/sync-database")
async def sync_database(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ejecutar sincronización de BD producción → staging
    
    Streaming de logs en tiempo real usando Server-Sent Events (SSE)
    """
    check_environment()
    check_admin_role(current_user)
    check_rate_limit()
    
    # Log de auditoría
    print(f"[AUDIT] Sincronización BD iniciada por {current_user.username} ({current_user.email})")
    
    return StreamingResponse(
        stream_sync_logs(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Deshabilitar buffering en nginx
        }
    )
