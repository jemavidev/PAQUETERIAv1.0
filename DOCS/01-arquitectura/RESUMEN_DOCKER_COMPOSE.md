# 🎯 RESUMEN: Archivos Docker-Compose

**Fecha**: 2026-01-29  
**Acción**: Análisis y limpieza de archivos docker-compose

---

## ✅ RESULTADO FINAL

### Archivos Activos (3)

```
📁 Raíz del proyecto/
├── docker-compose.dev.yml      → LOCALHOST
├── docker-compose.staging.yml  → STAGING
└── docker-compose.prod.yml     → PRODUCCIÓN
```

### Archivos Archivados (2)

```
📁 ARCHIVE/docker-compose/
├── docker-compose.lightsail.yml
├── docker-compose.staging-minimal.yml
└── README.md
```

---

## 📊 CONFIGURACIÓN POR ENTORNO

### 🖥️ LOCALHOST (Desarrollo)
- **Archivo**: `docker-compose.dev.yml`
- **Puerto App**: 8000
- **Puerto Redis**: 6379
- **Base de Datos**: `paqueteria_staging` (AWS RDS)
- **Archivo .env**: `CODE/.env`
- **Hot Reload**: ✅ Sí
- **Comando**: `docker compose -f docker-compose.dev.yml up -d`

### 🧪 STAGING (Pruebas)
- **Archivo**: `docker-compose.staging.yml`
- **Puerto App**: 8001
- **Puerto Redis**: 6380
- **Base de Datos**: `paqueteria_staging` (AWS RDS)
- **Archivo .env**: `CODE/.env.staging`
- **Hot Reload**: ❌ No
- **Comando**: `docker compose -f docker-compose.staging.yml up -d`

### 🚀 PRODUCCIÓN
- **Archivo**: `docker-compose.prod.yml`
- **Puerto App**: 8000 (solo localhost)
- **Puerto Redis**: 6379
- **Base de Datos**: `paqueteria_v4` (AWS RDS)
- **Archivo .env**: `CODE/.env.production`
- **Hot Reload**: ❌ No
- **Stack Completo**: App, Redis, Celery Worker, Celery Beat, Prometheus, Grafana, Node Exporter
- **Comando**: `docker compose -f docker-compose.prod.yml up -d`

---

## 🔍 DIFERENCIAS CLAVE

| Característica | LOCALHOST | STAGING | PRODUCCIÓN |
|----------------|-----------|---------|------------|
| Puerto App | 8000 | 8001 | 8000 |
| Puerto Redis | 6379 | 6380 | 6379 |
| Base de Datos | staging | staging | v4 |
| Hot Reload | ✅ | ❌ | ❌ |
| Celery | ❌ | ❌ | ✅ |
| Monitoring | ❌ | ❌ | ✅ |

---

## 📝 NOTAS IMPORTANTES

1. **LOCALHOST y STAGING** comparten la misma base de datos (`paqueteria_staging`)
2. **STAGING** usa puertos diferentes (8001, 6380) para evitar conflictos con producción
3. **PRODUCCIÓN** tiene stack completo con monitoreo y tareas asíncronas
4. **Todos los entornos** usan AWS RDS (sin bases de datos locales)

---

## 📚 Documentación Completa

Ver análisis detallado en: [`ANALISIS_DOCKER_COMPOSE_FILES.md`](./ANALISIS_DOCKER_COMPOSE_FILES.md)

---

**Commit**: 9a92c84
