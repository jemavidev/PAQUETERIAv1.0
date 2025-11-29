# Configuración de Uvicorn para forzar host 0.0.0.0
import os

# Configuración de host y puerto
HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", 8000))

# Configuración de workers
WORKERS = 1

# Configuración de timeouts
TIMEOUT_KEEP_ALIVE = 30
LIMIT_CONCURRENCY = 100

# Configuración de logging
LOG_LEVEL = "info"
