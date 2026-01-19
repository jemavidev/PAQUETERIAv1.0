# 🚀 Guía: Desarrollo en Localhost

## Opción 1: Ejecutar Directamente con Python (Recomendado para desarrollo)

### 1. Requisitos Previos
```bash
# Python 3.9+
python3 --version

# PostgreSQL
psql --version

# Redis (opcional)
redis-cli --version
```

### 2. Configurar Base de Datos

```bash
# Crear base de datos PostgreSQL
sudo -u postgres psql
CREATE DATABASE paqueteria;
CREATE USER paquetex WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE paqueteria TO paquetex;
\q
```

### 3. Configurar Entorno

```bash
# Ir al directorio del código
cd CODE

# Copiar archivo de configuración
cp env.example .env

# Editar .env con tus credenciales locales
nano .env
```

**Configuración mínima en `.env`:**
```bash
# Base de datos
DATABASE_URL=postgresql://paquetex:tu_password@localhost:5432/paqueteria

# Redis (opcional - si no tienes Redis, comentar esta línea)
# REDIS_URL=redis://localhost:6379/0

# Secreto para JWT
SECRET_KEY=tu_clave_secreta_super_segura_aqui

# AWS S3 (opcional para desarrollo - puedes usar almacenamiento local)
# AWS_ACCESS_KEY_ID=tu_access_key
# AWS_SECRET_ACCESS_KEY=tu_secret_key
# AWS_S3_BUCKET_NAME=tu_bucket

# Modo desarrollo
DEBUG=True
ENVIRONMENT=development
```

### 4. Instalar Dependencias

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate  # En Linux/Mac
# o
venv\Scripts\activate  # En Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 5. Ejecutar Migraciones

```bash
# Ejecutar migraciones de base de datos
alembic upgrade head
```

### 6. Crear Usuario Admin (Opcional)

```bash
# Ejecutar script para crear usuario admin
python src/scripts/create_admin_user.py
```

O crear manualmente en la base de datos:
```sql
INSERT INTO users (username, email, password_hash, role, is_active) 
VALUES ('admin', 'admin@paquetex.com', '$2b$12$...', 'admin', true);
```

### 7. Levantar el Servidor

```bash
# Opción A: Con uvicorn directamente (más rápido)
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Opción B: Con el script de configuración
python src/main.py
```

### 8. Acceder a la Aplicación

```
🌐 Aplicación: http://localhost:8000
📚 API Docs: http://localhost:8000/docs
📊 ReDoc: http://localhost:8000/redoc
```

---

## Opción 2: Usar Docker Compose (Más completo)

### 1. Crear docker-compose.dev.yml

Crea el archivo `docker-compose.dev.yml` en la raíz del proyecto:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: paquetex_dev_postgres
    environment:
      POSTGRES_DB: paqueteria
      POSTGRES_USER: paquetex
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - paquetex_network

  redis:
    image: redis:7-alpine
    container_name: paquetex_dev_redis
    ports:
      - "6379:6379"
    networks:
      - paquetex_network

  app:
    build:
      context: ./CODE
      dockerfile: Dockerfile
    container_name: paquetex_dev_app
    command: uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    volumes:
      - ./CODE/src:/app/src:rw
      - ./CODE/alembic:/app/alembic:rw
      - ./CODE/uploads:/app/uploads:rw
    environment:
      - DATABASE_URL=postgresql://paquetex:dev_password@postgres:5432/paqueteria
      - REDIS_URL=redis://redis:6379/0
      - DEBUG=True
      - ENVIRONMENT=development
    depends_on:
      - postgres
      - redis
    networks:
      - paquetex_network

volumes:
  postgres_data:

networks:
  paquetex_network:
    driver: bridge
```

### 2. Levantar Servicios

```bash
# Levantar todos los servicios
docker compose -f docker-compose.dev.yml up -d

# Ver logs
docker compose -f docker-compose.dev.yml logs -f app

# Ejecutar migraciones
docker compose -f docker-compose.dev.yml exec app alembic upgrade head
```

### 3. Acceder

```
🌐 Aplicación: http://localhost:8000
```

### 4. Comandos Útiles

```bash
# Detener servicios
docker compose -f docker-compose.dev.yml down

# Reiniciar solo la app
docker compose -f docker-compose.dev.yml restart app

# Ver logs
docker compose -f docker-compose.dev.yml logs -f

# Entrar al contenedor
docker compose -f docker-compose.dev.yml exec app bash

# Ejecutar script de reprocesamiento
docker compose -f docker-compose.dev.yml exec app python /app/reprocesar_facturas_supplier.py
```

---

## Opción 3: Usar el Script de Deploy (Si existe docker-compose.dev.yml)

```bash
# Levantar servicios
./deploy.sh --env localhost --deploy

# Ver logs
./deploy.sh --env localhost --logs

# Reiniciar
./deploy.sh --env localhost --restart

# Estado
./deploy.sh --env localhost --status
```

---

## 🔧 Troubleshooting

### Error: Puerto 8000 ya en uso
```bash
# Encontrar proceso usando el puerto
lsof -i :8000

# Matar proceso
kill -9 <PID>
```

### Error: No se puede conectar a PostgreSQL
```bash
# Verificar que PostgreSQL esté corriendo
sudo systemctl status postgresql

# Iniciar PostgreSQL
sudo systemctl start postgresql
```

### Error: Módulo no encontrado
```bash
# Asegurarse de estar en el entorno virtual
source venv/bin/activate

# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: Migraciones fallan
```bash
# Verificar conexión a BD
psql -U paquetex -d paqueteria -h localhost

# Resetear migraciones (CUIDADO: borra datos)
alembic downgrade base
alembic upgrade head
```

---

## 📝 Desarrollo Diario

### Flujo de Trabajo Recomendado

1. **Activar entorno virtual**
   ```bash
   cd CODE
   source venv/bin/activate
   ```

2. **Actualizar código**
   ```bash
   git pull origin main
   ```

3. **Actualizar dependencias (si cambiaron)**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar migraciones (si hay nuevas)**
   ```bash
   alembic upgrade head
   ```

5. **Levantar servidor**
   ```bash
   cd src
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Desarrollar y probar**
   - Los cambios se recargan automáticamente con `--reload`
   - Acceder a http://localhost:8000

7. **Ejecutar script de reprocesamiento (si es necesario)**
   ```bash
   # Desde la raíz del proyecto
   cd CODE
   python ../reprocesar_facturas_supplier.py
   ```

---

## 🧪 Testing

### Ejecutar Tests
```bash
# Todos los tests
pytest

# Tests específicos
pytest tests/test_invoices.py

# Con cobertura
pytest --cov=app tests/
```

### Probar Endpoints Manualmente
```bash
# Health check
curl http://localhost:8000/health

# API docs interactiva
# Abrir en navegador: http://localhost:8000/docs
```

---

## 📊 Acceso a Base de Datos

### Con psql
```bash
psql -U paquetex -d paqueteria -h localhost
```

### Con pgAdmin
- Host: localhost
- Port: 5432
- Database: paqueteria
- Username: paquetex
- Password: (tu password)

---

## 🔑 Credenciales por Defecto

### Usuario Admin (si creaste uno)
- Username: `admin`
- Password: (el que configuraste)

### Base de Datos
- Database: `paqueteria`
- User: `paquetex`
- Password: (el que configuraste en .env)

---

## 📚 Recursos Adicionales

- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Documentación**: [DOCS/](DOCS/)
- **README Principal**: [README.md](README.md)

---

## ⚡ Tips de Desarrollo

1. **Hot Reload**: Usa `--reload` para que los cambios se apliquen automáticamente
2. **Debug**: Activa `DEBUG=True` en `.env` para ver errores detallados
3. **Logs**: Revisa los logs en consola para debugging
4. **DB Browser**: Usa pgAdmin o DBeaver para explorar la BD
5. **API Testing**: Usa la interfaz de Swagger en `/docs`

---

## 🚀 Siguiente Paso: Probar Cambios

Después de levantar el servidor en localhost:

1. Acceder a http://localhost:8000/invoices
2. Subir una factura de prueba
3. Verificar que los datos se extraen correctamente
4. Ejecutar el script de reprocesamiento si es necesario:
   ```bash
   python reprocesar_facturas_supplier.py
   ```
