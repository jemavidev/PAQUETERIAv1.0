# 📦 ARCHIVE - Docker Compose Files

Esta carpeta contiene archivos `docker-compose.yml` que fueron archivados por ser redundantes o no corresponder a los 3 entornos principales del proyecto.

---

## 📋 Archivos Archivados

### `docker-compose.lightsail.yml`
**Fecha de archivo**: 2026-01-29  
**Razón**: Redundante - Es una versión optimizada de producción para AWS Lightsail

**Características**:
- Optimizado para 1GB RAM
- Límites de memoria y CPU estrictos
- Workers reducidos (2 en lugar de 4)
- Sin Prometheus/Grafana

**¿Por qué se archivó?**
- No corresponde a ninguno de los 3 entornos (LOCALHOST, STAGING, PRODUCCIÓN)
- Es una optimización específica de hardware
- Duplica configuración que ya existe en `docker-compose.prod.yml`

**Si necesitas usarlo**:
- Copia de vuelta a la raíz: `cp ARCHIVE/docker-compose/docker-compose.lightsail.yml .`
- O renombra como producción: `mv docker-compose.prod.yml docker-compose.prod-full.yml && cp ARCHIVE/docker-compose/docker-compose.lightsail.yml docker-compose.prod.yml`

---

### `docker-compose.staging-minimal.yml`
**Fecha de archivo**: 2026-01-29  
**Razón**: Redundante - Es una versión ultra-minimal de staging sin Redis

**Características**:
- Sin Redis (usa cache en memoria)
- Solo servicio `app`
- Límites de memoria más estrictos (300MB)
- `network_mode: host`

**¿Por qué se archivó?**
- No es necesario tener dos versiones de staging
- Sin Redis pierde funcionalidad importante
- Duplica configuración de `docker-compose.staging.yml`

**Si necesitas usarlo**:
- Copia de vuelta a la raíz: `cp ARCHIVE/docker-compose/docker-compose.staging-minimal.yml .`

---

## ✅ Archivos Activos (en raíz)

Los 3 archivos principales que corresponden a los 3 entornos:

1. **`docker-compose.dev.yml`** - LOCALHOST (desarrollo)
   - Puerto: 8000
   - Redis: 6379
   - Base de datos: `paqueteria_staging`
   - Hot reload: ✅

2. **`docker-compose.staging.yml`** - STAGING (pruebas)
   - Puerto: 8001
   - Redis: 6380
   - Base de datos: `paqueteria_staging`
   - Hot reload: ❌

3. **`docker-compose.prod.yml`** - PRODUCCIÓN
   - Puerto: 8000
   - Redis: 6379
   - Base de datos: `paqueteria_v4`
   - Stack completo: Celery, Prometheus, Grafana

---

## 📚 Documentación

Ver análisis completo en: `DOCS/01-arquitectura/ANALISIS_DOCKER_COMPOSE_FILES.md`

---

**Última actualización**: 2026-01-29
