# 📊 ANÁLISIS DE ARCHIVOS DOCKER-COMPOSE

**Fecha**: 2026-01-29  
**Proyecto**: PAQUETEX v1.0  
**Entornos**: LOCALHOST, STAGING, PRODUCCIÓN

---

## 🎯 RESUMEN EJECUTIVO

**Archivos encontrados**: 5 archivos `.yml`  
**Archivos necesarios**: 3 archivos  
**Archivos redundantes**: 2 archivos

### ✅ Archivos NECESARIOS

| Archivo | Entorno | Puerto App | Puerto Redis | Base de Datos | Estado |
|---------|---------|------------|--------------|---------------|--------|
| `docker-compose.dev.yml` | **LOCALHOST** | 8000 | 6379 | `paqueteria_staging` | ✅ Necesario |
| `docker-compose.staging.yml` | **STAGING** | 8001 | 6380 | `paqueteria_staging` | ✅ Necesario |
| `docker-compose.prod.yml` | **PRODUCCIÓN** | 8000 | 6379 | `paqueteria_v4` | ✅ Necesario |

### ❌ Archivos REDUNDANTES

| Archivo | Razón | Acción Recomendada |
|---------|-------|-------------------|
| `docker-compose.lightsail.yml` | Duplicado de producción con optimizaciones específicas de AWS Lightsail | ⚠️ Mover a `ARCHIVE/` o eliminar |
| `docker-compose.staging-minimal.yml` | Versión ultra-minimal de staging sin Redis | ⚠️ Mover a `ARCHIVE/` o eliminar |

---

## 📋 ANÁLISIS DETALLADO POR ARCHIVO

### 1️⃣ `docker-compose.dev.yml` - LOCALHOST ✅

**Propósito**: Desarrollo local  
**Uso**: `docker compose -f docker-compose.dev.yml up -d`

#### Características
- **Puerto App**: 8000
- **Puerto Redis**: 6379
- **Base de Datos**: AWS RDS `paqueteria_staging` (remota)
- **Archivo .env**: `CODE/.env`
- **Hot Reload**: ✅ Sí (volúmenes montados con `:rw`)
- **Servicios**: 
  - `app` (FastAPI)
  - `redis` (Cache)

#### Configuración
```yaml
services:
  redis:
    ports: "6379:6379"
  app:
    ports: "8000:8000"
    command: uvicorn main:app --reload --host 0.0.0.0 --port 8000
    volumes:
      - ./CODE/src:/app/src:rw  # Hot reload
```

#### Variables de Entorno
```bash
DATABASE_URL=${DATABASE_URL}  # paqueteria_staging en AWS RDS
REDIS_URL=redis://redis:6379/0
DEBUG=True
ENVIRONMENT=development
```

#### ✅ Ventajas
- Hot reload para desarrollo rápido
- Usa base de datos staging (no local)
- Configuración simple y clara

#### 📝 Recomendación
**MANTENER** - Es el archivo correcto para desarrollo local.

---

### 2️⃣ `docker-compose.staging.yml` - STAGING ✅

**Propósito**: Servidor de staging para pruebas  
**Uso**: `docker compose -f docker-compose.staging.yml up -d`

#### Características
- **Puerto App**: 8001 (evita conflicto con producción)
- **Puerto Redis**: 6380 (evita conflicto con producción)
- **Base de Datos**: AWS RDS `paqueteria_staging` (remota)
- **Archivo .env**: `CODE/.env.staging`
- **Hot Reload**: ❌ No (código read-only)
- **Servicios**: 
  - `app` (FastAPI)
  - `redis` (Cache)

#### Configuración
```yaml
services:
  redis:
    ports: "127.0.0.1:6380:6380"
    command: redis-server --port 6380
  app:
    ports: "0.0.0.0:8001:8000"
    env_file: ./CODE/.env.staging
    volumes:
      - ./CODE/src/app:/app/src/app:ro  # Read-only
      - ./CODE/src/static:/app/src/static  # Editable
      - ./CODE/src/templates:/app/src/templates  # Editable
```

#### Variables de Entorno
```bash
DATABASE_URL=${DATABASE_URL}  # paqueteria_staging en AWS RDS
REDIS_URL=redis://:password@redis:6380/0
ENVIRONMENT=staging
```

#### ✅ Ventajas
- Puertos diferentes evitan conflicto con producción
- Permite editar CSS/HTML sin rebuild
- Red y volúmenes separados de producción

#### 📝 Recomendación
**MANTENER** - Es el archivo correcto para staging.

---

### 3️⃣ `docker-compose.prod.yml` - PRODUCCIÓN ✅

**Propósito**: Servidor de producción  
**Uso**: `docker compose -f docker-compose.prod.yml up -d`

#### Características
- **Puerto App**: 8000 (solo localhost)
- **Puerto Redis**: 6379
- **Base de Datos**: AWS RDS `paqueteria_v4` (remota)
- **Archivo .env**: `CODE/.env.production`
- **Hot Reload**: ❌ No (código read-only)
- **Servicios**: 
  - `app` (FastAPI con uvicorn config)
  - `redis` (Cache)
  - `celery_worker` (Tareas asíncronas)
  - `celery_beat` (Tareas programadas)
  - `prometheus` (Métricas)
  - `grafana` (Dashboards)
  - `node_exporter` (Métricas del sistema)

#### Configuración
```yaml
services:
  redis:
    command: redis-server --maxmemory 256mb
  app:
    ports: "127.0.0.1:8000:8000"  # Solo localhost
    env_file: ./CODE/.env.production
    command: python -c 'from src.uvicorn_config import *; ...'
  celery_worker:
    command: celery -A src.app.celery_app worker --concurrency=4
  celery_beat:
    command: celery -A src.app.celery_app beat
```

#### Variables de Entorno
```bash
DATABASE_URL=${DATABASE_URL}  # paqueteria_v4 en AWS RDS
REDIS_URL=redis://:password@redis:6379/0
ENVIRONMENT=production
```

#### ✅ Ventajas
- Stack completo con monitoreo
- Celery para tareas asíncronas
- Prometheus + Grafana para métricas
- Seguridad: app solo en localhost (Nginx del host hace proxy)

#### 📝 Recomendación
**MANTENER** - Es el archivo correcto para producción.

---

### 4️⃣ `docker-compose.lightsail.yml` - REDUNDANTE ❌

**Propósito**: Optimizado para AWS Lightsail (1GB RAM)  
**Problema**: Es una versión optimizada de producción para hardware limitado

#### Diferencias con `docker-compose.prod.yml`
- Límites de memoria estrictos (`mem_limit`, `mem_reservation`)
- Límites de CPU (`cpus`)
- Workers reducidos (2 en lugar de 4)
- Solo 1 celery worker (en lugar de 4)
- Sin Prometheus/Grafana/Node Exporter
- Logging reducido

#### ¿Por qué es redundante?
1. **No corresponde a ninguno de los 3 entornos** (LOCALHOST, STAGING, PRODUCCIÓN)
2. **Es una optimización específica** de hardware que debería ser parte de `docker-compose.prod.yml` con variables
3. **Duplica configuración** que ya existe en prod

#### 📝 Recomendación
**ELIMINAR o ARCHIVAR** - Si el servidor de producción es AWS Lightsail, entonces:
- **Opción A**: Renombrar `docker-compose.prod.yml` → `docker-compose.prod-full.yml`
- **Opción B**: Renombrar `docker-compose.lightsail.yml` → `docker-compose.prod.yml`
- **Opción C**: Mover a `ARCHIVE/docker-compose.lightsail.yml` como referencia

---

### 5️⃣ `docker-compose.staging-minimal.yml` - REDUNDANTE ❌

**Propósito**: Versión ultra-minimal de staging sin Redis  
**Problema**: Es una versión reducida de staging

#### Diferencias con `docker-compose.staging.yml`
- **Sin Redis** (usa cache en memoria)
- Solo servicio `app`
- Límites de memoria más estrictos (300MB)
- `network_mode: host` (no usa red Docker)
- Logging más reducido

#### ¿Por qué es redundante?
1. **No es necesario** - Staging ya es ligero
2. **Sin Redis** - Pierde funcionalidad importante
3. **Duplica configuración** de staging

#### 📝 Recomendación
**ELIMINAR o ARCHIVAR** - No es necesario tener dos versiones de staging.

---

## 🎯 RECOMENDACIONES FINALES

### ✅ Mantener (3 archivos)

```
docker-compose.dev.yml       → LOCALHOST (desarrollo)
docker-compose.staging.yml   → STAGING (pruebas)
docker-compose.prod.yml      → PRODUCCIÓN (producción)
```

### ❌ Eliminar o Archivar (2 archivos)

```
docker-compose.lightsail.yml        → Mover a ARCHIVE/
docker-compose.staging-minimal.yml  → Mover a ARCHIVE/
```

---

## 📊 TABLA COMPARATIVA FINAL

| Característica | LOCALHOST | STAGING | PRODUCCIÓN |
|----------------|-----------|---------|------------|
| **Archivo** | `dev.yml` | `staging.yml` | `prod.yml` |
| **Puerto App** | 8000 | 8001 | 8000 |
| **Puerto Redis** | 6379 | 6380 | 6379 |
| **Base de Datos** | `paqueteria_staging` | `paqueteria_staging` | `paqueteria_v4` |
| **Archivo .env** | `CODE/.env` | `CODE/.env.staging` | `CODE/.env.production` |
| **Hot Reload** | ✅ Sí | ❌ No | ❌ No |
| **Redis** | ✅ Sí | ✅ Sí | ✅ Sí |
| **Celery Worker** | ❌ No | ❌ No | ✅ Sí |
| **Celery Beat** | ❌ No | ❌ No | ✅ Sí |
| **Prometheus** | ❌ No | ❌ No | ✅ Sí |
| **Grafana** | ❌ No | ❌ No | ✅ Sí |
| **Node Exporter** | ❌ No | ❌ No | ✅ Sí |
| **Código** | Read-Write | Read-Only | Read-Only |
| **Static/Templates** | Read-Write | Read-Write | Read-Write |

---

## 🚀 COMANDOS DE USO

### LOCALHOST (Desarrollo)
```bash
# Levantar
docker compose -f docker-compose.dev.yml up -d

# Ver logs
docker compose -f docker-compose.dev.yml logs -f app

# Detener
docker compose -f docker-compose.dev.yml down
```

### STAGING (Pruebas)
```bash
# Levantar
docker compose -f docker-compose.staging.yml up -d

# Ver logs
docker compose -f docker-compose.staging.yml logs -f app

# Detener
docker compose -f docker-compose.staging.yml down
```

### PRODUCCIÓN
```bash
# Levantar
docker compose -f docker-compose.prod.yml up -d

# Ver logs
docker compose -f docker-compose.prod.yml logs -f app

# Detener
docker compose -f docker-compose.prod.yml down
```

---

## 📝 ACCIONES RECOMENDADAS

1. **Crear carpeta ARCHIVE**:
   ```bash
   mkdir -p ARCHIVE/docker-compose
   ```

2. **Mover archivos redundantes**:
   ```bash
   mv docker-compose.lightsail.yml ARCHIVE/docker-compose/
   mv docker-compose.staging-minimal.yml ARCHIVE/docker-compose/
   ```

3. **Actualizar README.md** con los 3 archivos principales

4. **Documentar** en `.deploy/config/` qué archivo usa cada entorno

---

## ✅ CONCLUSIÓN

El proyecto necesita **solo 3 archivos** docker-compose:
- ✅ `docker-compose.dev.yml` - LOCALHOST
- ✅ `docker-compose.staging.yml` - STAGING  
- ✅ `docker-compose.prod.yml` - PRODUCCIÓN

Los otros 2 archivos son redundantes y deben archivarse o eliminarse para mantener el proyecto limpio y evitar confusión.
