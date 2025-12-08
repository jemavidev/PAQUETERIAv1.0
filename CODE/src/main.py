# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Aplicación Principal FastAPI
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Importaciones locales
from src.app.config import settings
from src.app.utils.exceptions import PaqueteriaException
from src.app.database import init_db
from src.app.routes.api import router as api_router
from src.app.routes.views import router as views_router
from src.app.routes.public import router as public_router
from src.app.routes import auth, protected, customers, rates, notifications, messages, files, admin, announcements, profile, packages, settings_api
from src.app.routes.header_notifications import router as header_notifications
from src.app.routes.customer_preferences import router as customer_preferences_router
from src.app.routes.customer_preferences_otp import router as customer_preferences_otp_router
from src.app.routes.upload import router as upload_router
from src.app.routes.images import router as images_router
from src.app.routes.debug_standalone import router as debug_standalone_router
from src.app.routes.package_events import router as package_events_router
from src.app.routes.config import router as config_router  # ✨ Nuevo: Endpoints de configuración
from src.app.routes.customer_portal import router as customer_portal_api_router  # ✨ Portal de Clientes API
from src.app.routes.customer_portal_views import router as customer_portal_views_router  # ✨ Portal de Clientes Vistas
from src.app.routes.debug_portal import router as debug_portal_router  # ✨ Debug Portal
from src.app.middleware.rate_limiting import limiter, rate_limit_exceeded_handler
from src.app.middleware.error_handler import setup_error_handlers
from src.app.middleware.auth_middleware import AuthMiddleware  # Middleware refactorizado v2
from slowapi import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando PAQUETES EL CLUB v1.0...")
    try:
        init_db()
        logger.info("✅ Base de datos inicializada correctamente")
        logger.info(f"📊 Motor: {settings.database_url.split('@')[0]}***@{settings.database_url.split('@')[1].split('/')[0]}")
        logger.info(f"🗄️  Base de datos: {settings.database_url.split('/')[-1]}")
    except Exception as e:
        logger.error(f"❌ Error al inicializar la base de datos: {e}")
    
    # Validar configuración SMTP al iniciar (solo si está configurada)
    try:
        from app.services.email_service import EmailService
        email_service = EmailService()
        smtp_test = await email_service.test_smtp_connection()
        if smtp_test.get("success"):
            logger.info(f"✅ Conexión SMTP validada: {smtp_test.get('server')}:{smtp_test.get('port')}")
        else:
            logger.warning(f"⚠️ Configuración SMTP no disponible o inválida: {smtp_test.get('message')}")
            logger.warning("   Los emails no funcionarán hasta que se configure SMTP correctamente")
    except Exception as e:
        logger.warning(f"⚠️ No se pudo validar configuración SMTP: {str(e)}")
    
    yield
    logger.info("Cerrando PAQUETES EL CLUB v1.0...")

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Sistema de gestión de paquetería optimizado para producción",
    lifespan=lifespan
)

# Configurar métricas de Prometheus
Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de autenticación (refactorizado v2)
app.add_middleware(AuthMiddleware, login_url="/auth/login")

# Configuración de Rate Limiting
app.add_middleware(SlowAPIMiddleware)
app.state.limiter = limiter  # Set the limiter in app state for middleware
app.add_exception_handler(429, rate_limit_exceeded_handler)

# Montar archivos estáticos (sin cache para desarrollo, permite cambios en tiempo real)
app.mount("/static", StaticFiles(directory="/app/src/static"), name="static")

# Montar uploads desde /app/uploads (volumen dedicado)
# Crear directorio si no existe
from pathlib import Path
uploads_dir = Path("/app/uploads")
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# Configuración de templates
from src.app.utils.template_loader import get_templates
templates = get_templates()

# Manejadores de excepciones
def handle_paqueteria_exception(request: Request, exc: PaqueteriaException):
    logger.error(f"PaqueteriaException: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"}
    )

def handle_http_exception(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        if "/api/auth/login" not in str(request.url):
            headers = dict(exc.headers) if exc.headers else {}
            headers["Location"] = "/auth/login"
            headers["Content-Type"] = "application/json"

            return JSONResponse(
                status_code=401,
                content={"detail": "No autenticado"},
                headers=headers
            )

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# Configurar handlers de error personalizados
setup_error_handlers(app)

# Mantener handlers específicos existentes
app.add_exception_handler(PaqueteriaException, handle_paqueteria_exception)

# Handler para 404
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Manejador personalizado para errores 404"""
    # Si es una petición API, devolver JSON
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=404,
            content={"detail": "Recurso no encontrado"}
        )
    # Si es una petición web, mostrar página 404
    return templates.TemplateResponse(
        "errors/404.html",
        {"request": request},
        status_code=404
    )

# Incluir routers
app.include_router(api_router, prefix="/api")
app.include_router(public_router, tags=["Público"])  # Rutas públicas (debe ir primero)
app.include_router(views_router)
app.include_router(protected.router, tags=["Protegido"])
app.include_router(auth, prefix="/api/auth", tags=["Autenticación"])
app.include_router(packages, prefix="/api/packages", tags=["Paquetes"])
app.include_router(announcements, prefix="/api/announcements", tags=["Anuncios"])
app.include_router(customers, prefix="/api/customers", tags=["Clientes"])
app.include_router(rates, prefix="/api/rates", tags=["Tarifas"])
app.include_router(notifications, prefix="/api/notifications", tags=["Notificaciones"])
app.include_router(messages, prefix="/api/messages", tags=["Mensajes"])
app.include_router(header_notifications, prefix="/api/header", tags=["Notificaciones del Header"])
app.include_router(files, prefix="/api/files", tags=["Archivos"])
app.include_router(admin, prefix="/api/admin", tags=["Administración"])
app.include_router(profile, prefix="/profile", tags=["Perfil"])
app.include_router(settings_api, tags=["Configuración"])
app.include_router(config_router, tags=["Configuración"])  # ✨ Nuevo: Endpoints de configuración
app.include_router(customer_preferences_router, tags=["Preferencias de Cliente"])
app.include_router(customer_preferences_otp_router, tags=["Preferencias de Cliente - OTP"])
app.include_router(upload_router, tags=["Upload"])
app.include_router(images_router, tags=["Imágenes"])
app.include_router(debug_standalone_router, tags=["Debug Standalone"])
app.include_router(package_events_router, tags=["Eventos de Paquetes"])
app.include_router(customer_portal_api_router, tags=["Portal de Clientes - API"])  # ✨ Portal de Clientes API
app.include_router(customer_portal_views_router, tags=["Portal de Clientes - Vistas"])  # ✨ Portal de Clientes Vistas
app.include_router(debug_portal_router, tags=["Debug Portal"])  # ✨ Debug Portal

# Endpoint de health check
@app.get("/health")
async def health_check():
    """Health check para la aplicación"""
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "environment": os.getenv("ENVIRONMENT", "development")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
