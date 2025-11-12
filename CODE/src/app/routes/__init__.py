# ========================================
# PAQUETES EL CLUB v1.0 - Rutas FastAPI
# ========================================
# Archivo: CODE/LOCAL/src/app/routes/__init__.py (siguiendo reglas de AGENTS.md)
# Versión: 1.0.0
# Fecha: 2025-01-24
# Autor: Equipo de Desarrollo
# ========================================

"""
Módulo de rutas FastAPI para PAQUETES EL CLUB
"""

# Importar routers principales
from .auth import router as auth
from .packages import router as packages
from .customers import router as customers
from .rates import router as rates
from .notifications import router as notifications
from .messages import router as messages
from .files import router as files
from .admin import router as admin
from .announcements import router as announcements
from .profile import router as profile
# from .public import router as public  # Archivo no existe
# from .protected import router as protected  # Archivo no existe

__all__ = [
    "auth",
    "packages",
    "customers",
    "rates",
    "notifications",
    "messages",
    "files",
    "admin",
    "announcements",
    "profile",
    # "public",  # Archivo no existe
    # "protected"  # Archivo no existe
]
