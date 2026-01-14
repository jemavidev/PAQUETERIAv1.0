# Configuración de Uvicorn para forzar host 0.0.0.0
import os

# Configuración de host y puerto
HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", 8000))

# Detectar entorno
ENVIRONMENT = os.getenv("ENVIRONMENT", "production").lower()
IS_STAGING = ENVIRONMENT in ["staging", "development", "dev"]

# Configuración de workers adaptativa
# STAGING: 2 workers (servidor con 416MB RAM)
# PRODUCCIÓN: 3 workers (servidor con 914MB RAM, balance óptimo)
WORKERS = 2 if IS_STAGING else 3

# Configuración de timeouts para evitar bloqueos
TIMEOUT_KEEP_ALIVE = 30  # Mantener conexión viva por 30 segundos
TIMEOUT_GRACEFUL_SHUTDOWN = 30  # Tiempo para apagar gracefully
LIMIT_CONCURRENCY = 100 if IS_STAGING else 200

# Configuración de logging
LOG_LEVEL = "info"

print(f"🚀 Uvicorn Config: {ENVIRONMENT.upper()} | Workers: {WORKERS} | Concurrency: {LIMIT_CONCURRENCY} | Timeouts: {TIMEOUT_KEEP_ALIVE}s")

