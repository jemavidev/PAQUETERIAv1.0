FROM python:3.11-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app:/app/src

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY src/ /app/src/
COPY alembic/ /app/alembic/
COPY alembic.ini /app/

# Crear directorios necesarios
RUN mkdir -p /app/uploads /app/logs /app/backups/database

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["sh", "-c", "cd /app && PYTHONPATH=/app:/app/src python -m uvicorn src.main:app --host 0.0.0.0 --port 8000"]