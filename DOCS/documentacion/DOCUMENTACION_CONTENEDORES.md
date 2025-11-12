# Documentación de Contenedores Docker

## 📦 Descripción General

Este documento describe todos los contenedores Docker que forman parte del stack de producción de **PAQUETERÍA v1.0**. El proyecto utiliza Docker Compose para orquestar múltiples servicios que trabajan juntos para proporcionar una aplicación completa de gestión de paquetería.

---

## 🐳 Contenedores del Stack

### 1. **redis** - Servidor Redis

**Imagen**: `redis:7-alpine`  
**Nombre del contenedor**: `paqueteria_v1_prod_redis`  
**Puerto**: 6379 (interno)

#### ¿Qué hace?
Redis actúa como **broker y backend** para Celery, proporcionando:
- **Cola de mensajes**: Gestiona las tareas asíncronas de Celery (worker y beat)
- **Cache**: Almacenamiento temporal de datos para mejorar el rendimiento
- **Sesiones**: Almacenamiento de sesiones de usuario (si se configura)

#### Características:
- Requiere contraseña para acceso (`REDIS_PASSWORD`)
- Límite de memoria: 256MB con política `allkeys-lru` (elimina claves menos usadas cuando se alcanza el límite)
- Health check configurado para verificar disponibilidad
- Volumen persistente: `redis_data` para mantener datos entre reinicios
- Zona horaria: `America/Bogota`

#### Dependencias:
- Ninguna (es el servicio base)

---

### 2. **app** - Aplicación Principal FastAPI

**Imagen**: `paqueteria_v1_app:prod` (construida desde `CODE/Dockerfile`)  
**Nombre del contenedor**: `paqueteria_v1_prod_app`  
**Puerto**: 8000 (expuesto en `127.0.0.1:8000`)

#### ¿Qué hace?
Es el **núcleo de la aplicación**, proporcionando:
- **API REST**: Endpoints para todas las funcionalidades del sistema
- **Interfaz Web**: Templates HTML con CSS y JavaScript para la interfaz de usuario
- **Autenticación**: Sistema de login y gestión de sesiones
- **Gestión de Paquetes**: CRUD completo de paquetes, clientes, tarifas, etc.
- **Métricas**: Endpoint `/metrics` para Prometheus

#### Características:
- Framework: **FastAPI** con **Uvicorn**
- **Hot Reload**: Activado para desarrollo (cambios en código se reflejan automáticamente)
- Health check en `/health`
- Volúmenes montados:
  - `./CODE/src` → `/app/src` (código fuente)
  - `./CODE/src/static` → `/app/static` (archivos estáticos)
  - `uploads_data` → `/app/uploads` (archivos subidos)
  - `logs_data` → `/app/logs` (logs de la aplicación)

#### Dependencias:
- `redis` (debe estar saludable antes de iniciar)

#### Comando de inicio:
```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir /app/src
```

---

### 3. **celery_worker** - Worker de Tareas Asíncronas

**Imagen**: `paqueteria_v1_app:prod` (misma imagen que `app`)  
**Nombre del contenedor**: `paqueteria_v1_prod_celery`  
**Puerto**: Ninguno (solo interno)

#### ¿Qué hace?
Ejecuta **tareas asíncronas** en segundo plano:
- **Envío de emails**: Procesa cola de emails SMTP
- **Envío de SMS**: Procesa cola de SMS vía Liwa.co
- **Generación de reportes**: Crea reportes PDF/Excel de forma asíncrona
- **Procesamiento de archivos**: Sube archivos a S3, procesa imágenes
- **Limpieza de datos**: Tareas de mantenimiento programadas

#### Características:
- Concurrencia: 4 workers simultáneos
- Colas configuradas: `reports`, `sms`, `files`, `maintenance`, `default`
- Health check básico
- Volúmenes:
  - `./CODE/src` → `/app/src:ro` (solo lectura)
  - `uploads_data` → `/app/uploads` (acceso a archivos)
  - `logs_data` → `/app/logs` (logs del worker)

#### Dependencias:
- `redis` (debe estar saludable)
- `app` (debe estar iniciado)

#### Comando de inicio:
```bash
celery -A src.app.celery_app worker --loglevel=info --concurrency=4 --hostname=worker@%h
```

---

### 4. **celery_beat** - Programador de Tareas

**Imagen**: `paqueteria_v1_app:prod` (misma imagen que `app`)  
**Nombre del contenedor**: `paqueteria_v1_prod_celery_beat`  
**Puerto**: Ninguno (solo interno)

#### ¿Qué hace?
**Programa y ejecuta tareas periódicas**:
- **Limpieza de reportes antiguos**: Cada 24 horas
- **Limpieza de archivos temporales**: Cada hora
- **Actualización de métricas del dashboard**: Cada 5 minutos
- **Recordatorios diarios**: Envío de notificaciones programadas

#### Características:
- Usa archivo de schedule persistente: `/app/celerybeat/celerybeat-schedule`
- Volumen persistente: `celery_beat_data` para mantener el schedule entre reinicios
- Health check básico
- Volúmenes:
  - `./CODE/src` → `/app/src:ro` (solo lectura)
  - `celery_beat_data` → `/app/celerybeat` (schedule persistente)
  - `logs_data` → `/app/logs` (logs del beat)

#### Dependencias:
- `redis` (debe estar saludable)
- `app` (debe estar iniciado)

#### Comando de inicio:
```bash
celery -A src.app.celery_app beat --loglevel=info --schedule=/app/celerybeat/celerybeat-schedule
```

---

### 5. **prometheus** - Servidor de Métricas

**Imagen**: `prom/prometheus:latest`  
**Nombre del contenedor**: `paqueteria_v1_prod_prometheus`  
**Puerto**: 9090 (expuesto en `127.0.0.1:9090`)

#### ¿Qué hace?
**Recopila y almacena métricas** del sistema:
- **Métricas de la aplicación**: Endpoint `/metrics` de FastAPI
- **Métricas del sistema**: Desde Node Exporter
- **Métricas de Celery**: Si está configurado
- **Almacenamiento**: Retención de 30 días de datos históricos

#### Características:
- Configuración: `./CODE/monitoring/prometheus.yml`
- Almacenamiento: Volumen `prometheus_data` (TSDB)
- Health check en `/-/healthy`
- Web UI disponible en `http://localhost:9090`

#### Dependencias:
- `app` (para métricas de la aplicación)
- `celery_worker` (para métricas de Celery)

---

### 6. **grafana** - Dashboards de Monitoreo

**Imagen**: `grafana/grafana:latest`  
**Nombre del contenedor**: `paqueteria_v1_prod_grafana`  
**Puerto**: 3000 (expuesto en `127.0.0.1:3000`)

#### ¿Qué hace?
**Visualiza métricas** recopiladas por Prometheus:
- **Dashboards pre-configurados**: Métricas de aplicación, sistema, Celery
- **Alertas**: Configuración de alertas basadas en métricas
- **Gráficos**: Visualización de rendimiento, uso de recursos, errores

#### Características:
- Usuario admin: `admin` (contraseña desde `GRAFANA_PASSWORD`)
- Sign-up deshabilitado (solo admin)
- Dashboards automáticos desde `./CODE/monitoring/grafana/dashboards`
- Provisioning desde `./CODE/monitoring/grafana/provisioning`
- Volumen persistente: `grafana_data` (mantiene dashboards y configuraciones)
- Health check en `/api/health`

#### Dependencias:
- `prometheus` (fuente de datos)

#### Acceso:
- URL: `http://localhost:3000`
- Usuario: `admin`
- Contraseña: Valor de `GRAFANA_PASSWORD` en `.env`

---

### 7. **node_exporter** - Exportador de Métricas del Sistema

**Imagen**: `prom/node-exporter:latest`  
**Nombre del contenedor**: `paqueteria_v1_prod_node_exporter`  
**Puerto**: 9100 (expuesto en `127.0.0.1:9100`)

#### ¿Qué hace?
**Exporta métricas del sistema operativo** del host:
- **CPU**: Uso, carga, tiempo
- **Memoria**: RAM, swap, buffers
- **Disco**: Espacio, I/O, uso
- **Red**: Tráfico, conexiones
- **Procesos**: Cantidad, estados

#### Características:
- Acceso de solo lectura a `/proc`, `/sys`, `/` del host
- Endpoint de métricas: `http://localhost:9100/metrics`
- Health check en `/metrics`
- Prometheus scrapea estas métricas automáticamente

#### Dependencias:
- Ninguna (independiente)

---

## 🔗 Red Docker

Todos los contenedores están conectados a la red `paqueteria_v1_prod_network` (bridge), lo que permite:
- Comunicación entre contenedores usando nombres de servicio como DNS
- Aislamiento del resto de la red del host
- Seguridad adicional

**Ejemplo de comunicación**:
- `app` se conecta a `redis` usando: `redis://:password@redis:6379/0`
- `celery_worker` se conecta a `redis` usando: `redis://:password@redis:6379/0`

---

## 💾 Volúmenes Persistentes

Los siguientes volúmenes mantienen datos entre reinicios:

1. **`redis_data`**: Datos de Redis (cache, colas)
2. **`uploads_data`**: Archivos subidos por usuarios
3. **`logs_data`**: Logs de la aplicación
4. **`celery_beat_data`**: Schedule de tareas programadas
5. **`prometheus_data`**: Base de datos de métricas (30 días)
6. **`grafana_data`**: Dashboards, usuarios, configuraciones de Grafana

---

## 🔄 Orden de Inicio

Docker Compose maneja las dependencias automáticamente:

1. **redis** → Inicia primero (sin dependencias)
2. **app** → Espera a que `redis` esté saludable
3. **celery_worker** → Espera a `redis` y `app`
4. **celery_beat** → Espera a `redis` y `app`
5. **prometheus** → Espera a `app` y `celery_worker`
6. **grafana** → Espera a `prometheus`
7. **node_exporter** → Inicia independientemente

---

## 🚀 Comandos Útiles

```bash
# Ver estado de todos los contenedores
docker compose -f docker-compose.prod.yml ps

# Ver logs de un contenedor específico
docker compose -f docker-compose.prod.yml logs -f app
docker compose -f docker-compose.prod.yml logs -f celery_worker

# Reiniciar un contenedor
docker compose -f docker-compose.prod.yml restart app

# Detener todos los servicios
docker compose -f docker-compose.prod.yml down

# Detener y eliminar volúmenes (¡CUIDADO! Elimina datos)
docker compose -f docker-compose.prod.yml down -v

# Ver uso de recursos
docker stats
```

---

## 📊 Puertos Expuestos

| Contenedor | Puerto Interno | Puerto Host | Acceso |
|------------|----------------|-------------|--------|
| `app` | 8000 | 127.0.0.1:8000 | Aplicación web |
| `prometheus` | 9090 | 127.0.0.1:9090 | Métricas |
| `grafana` | 3000 | 127.0.0.1:3000 | Dashboards |
| `node_exporter` | 9100 | 127.0.0.1:9100 | Métricas del sistema |

**Nota**: Todos los puertos están expuestos solo en `127.0.0.1` (localhost) por seguridad. Para acceso externo, configurar un reverse proxy (Nginx) en el host.

---

## 🔒 Seguridad

- **Redis**: Protegido con contraseña
- **Grafana**: Requiere autenticación
- **Puertos**: Solo expuestos en localhost
- **Variables de entorno**: Sensibles en `.env` (no versionado)
- **Volúmenes**: Datos persistentes aislados

---

**Última actualización**: 2025-01-24  
**Versión del documento**: 1.0.0

