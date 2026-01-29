"""
Endpoint para obtener información del entorno (producción/staging/desarrollo)
"""
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import os

router = APIRouter()

@router.get("/api/environment")
async def get_environment(request: Request):
    """
    Devuelve información sobre el entorno actual
    Endpoint público - no requiere autenticación
    """
    # Marcar como ruta pública
    request.state.is_public = True
    
    db_name = os.getenv("POSTGRES_DB", "unknown")
    environment = os.getenv("ENVIRONMENT", "unknown")
    app_name = os.getenv("APP_NAME", "PAQUETEX EL CLUB")
    
    # Determinar el tipo de entorno basado en la base de datos
    if db_name == "paqueteria_v4":
        env_type = "production"
        env_label = "Producción"
        env_color = "green"
    elif db_name == "paqueteria_staging":
        env_type = "staging"
        env_label = "Staging"
        env_color = "yellow"
    else:
        env_type = "development"
        env_label = "Desarrollo"
        env_color = "red"
    
    return JSONResponse({
        "environment": env_type,
        "label": env_label,
        "color": env_color,
        "database": db_name,
        "app_name": app_name,
        "env_var": environment
    })
