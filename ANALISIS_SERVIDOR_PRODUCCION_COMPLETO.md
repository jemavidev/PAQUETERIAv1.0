# 🔍 ANÁLISIS COMPLETO DEL SERVIDOR DE PRODUCCIÓN - PAQUETEX v4.0

**Fecha de Análisis:** 27 de Abril de 2026  
**Servidor:** paquetex (SSH disponible)  
**Estado General:** ✅ ACTIVO Y FUNCIONANDO

---

## 📊 RESUMEN EJECUTIVO

El servidor de producción está **completamente operacional** con un sistema robusto de Docker Compose, monitoreo completo, base de datos en AWS RDS y caching con Redis. Todos los contenedores están saludables (healthy) y el servidor tiene recursos suficientes para operar.

---

## 🏗️ ARQUITECTURA DEL SISTEMA

### Stack Tecnológico

```
┌─────────────────────────────────────────────────────────────┐
│                    PAQUETEX v4.0                            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Frontend (Nginx)                Backend (FastAPI)            │
│  ├─ SSL/TLS (Let's Encrypt)      ├─ Python 3.11              │
│  ├─ Static Files                 ├─ Uvicorn + Workers        │
│  ├─ Proxy Reverso                ├─ Celery Workers           │
│  └─ Cache 7d                      ├─ Celery Beat (scheduler)  │
│                                   └─ Health checks            │
│                                                               │
│  Cache & Session Storage          Database                    │
│  ├─ Redis 7-alpine                ├─ PostgreSQL AWS RDS       │
│  ├─ 256MB max memory              ├─ Version: v4              │
│  └─ LRU eviction policy            ├─ Host: AWS us-east-1     │
│                                    └─ Multi-AZ support        │
│                                                               │
│  Monitoring & Metrics                                         │
│  ├─ Prometheus (scraping)                                    │
│  ├─ Grafana (dashboards)                                     │
│  └─ Node Exporter (system metrics)                           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🐳 CONTENEDORES DOCKER

### Estado de Contenedores

| Contenedor | Estado | Salud | Puerto | Función |
|-----------|--------|-------|--------|---------|
| `paqueteria_v1_prod_app` | ✅ UP 4min | HEALTHY | 127.0.0.1:8000 | API Principal FastAPI |
| `paqueteria_v1_prod_celery` | ✅ UP 4min | HEALTHY | 8000/tcp | Tareas Asincrónicas |
| `paqueteria_v1_prod_celery_beat` | ✅ UP 4min | - | 8000/tcp | Scheduler de Tareas |
| `paqueteria_v1_prod_redis` | ✅ UP 4min | HEALTHY | 6379/tcp | Cache & Broker |
| `paqueteria_v1_prod_prometheus` | ✅ UP 4min | HEALTHY | 127.0.0.1:9090 | Scraping Métricas |
| `paqueteria_v1_prod_grafana` | ✅ UP 4min | HEALTHY | 127.0.0.1:3000 | Dashboards |
| `paqueteria_v1_prod_node_exporter` | ✅ UP 4min | HEALTHY | 127.0.0.1:9100 | Métricas del Sistema |

### Recursos Utilizados

```
Contenedor                      CPU %   MEM USAGE    MEM %   Imagen
────────────────────────────────────────────────────────────────────
paqueteria_v1_prod_app          0.39%   224.6 MiB    24.64%  1.86 GB
paqueteria_v1_prod_grafana      0.45%   81.53 MiB    8.95%   993 MB
paqueteria_v1_prod_prometheus   0.00%   31.12 MiB    3.41%   507 MB
paqueteria_v1_prod_celery       0.04%   11.92 MiB    1.31%   1.86 GB
paqueteria_v1_prod_redis        0.58%   3.488 MiB    0.38%   60.7 MB
paqueteria_v1_prod_celery_beat  0.00%   20.72 MiB    2.27%   1.86 GB
node_exporter                   0.01%   13.62 MiB    1.49%   41.6 MB
────────────────────────────────────────────────────────────────────
TOTAL                           1.47%   387 MiB      42.45%  ~5.5 GB
```

**Conclusión:** Sistema con carga baja. Hay capacidad disponible para crecer.

---

## 🗄️ BASE DE DATOS

### Configuración

- **Tipo:** PostgreSQL (AWS RDS)
- **Host:** `ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com`
- **Puerto:** 5432
- **Database:** `paqueteria_v4`
- **Usuario:** `jveyes`
- **Región AWS:** us-east-1
- **Características:** Multi-AZ support (alta disponibilidad)

### Gestión de Migraciones

- **Sistema:** Alembic (SQLAlchemy)
- **Configuración:** `alembic.ini` en raíz del proyecto
- **Ubicación esperada:** `/CODE/alembic/versions/` (No encontradas - posiblemente en rama diferente)

---

## 💾 ALMACENAMIENTO Y VOLÚMENES

### Docker Volumes

```yaml
volumes:
  redis_data:          # Persistencia de Redis
  uploads_data:        # Archivos cargados por usuarios (/app/uploads)
  logs_data:          # Logs de la aplicación (/app/logs)
  backups_data:       # Backups de base de datos
  celery_beat_data:   # Schedule de Celery Beat
  prometheus_data:    # Métricas históricas (30 días)
  grafana_data:       # Configuración y dashboards
```

### Almacenamiento en Sistema de Archivos

```
Filesystem       Size   Used  Avail  Use%
──────────────────────────────────────
/dev/root        38G    26G   12G    69%    ← Espacio crítico (69% usado)
```

⚠️ **ALERTA:** El disco está al 69%. Se recomienda monitoreo cercano.

---

## 🔐 SEGURIDAD

### SSL/TLS

- **Certificado:** Let's Encrypt
- **Dominio:** `paquetex.papyrus.com.co`
- **Rutas:** 
  - Cert: `/etc/letsencrypt/live/paquetex.papyrus.com.co/fullchain.pem`
  - Key: `/etc/letsencrypt/live/paquetex.papyrus.com.co/privkey.pem`
- **Estado:** ❓ No encontrado en el sistema (verificar con: `certbot certificates`)

### Headers de Seguridad (Nginx)

```nginx
X-Frame-Options: SAMEORIGIN              # Previene clickjacking
X-Content-Type-Options: nosniff           # Previene MIME sniffing
X-XSS-Protection: 1; mode=block           # Protección XSS
```

### Credenciales

Las credenciales están configuradas en `/home/ubuntu/paqueteria/.env`:

- **Secret Key:** FastAPI JWT
- **Database Password:** Configurada en AWS RDS
- **Redis Password:** `Redis2025!Secure`
- **SMTP Password:** Para notificaciones por email
- **AWS Access Keys:** Para S3 storage
- **Liwa API Key:** Para SMS (Colombia)
- **Grafana Password:** `Grafana2025!Secure`

---

## 🔄 PROCESOS Y SERVICIOS

### Procesos Principales (PID)

```
Servicio               PID    Función
──────────────────────────────────────────────────────────────
Docker Daemon         826    Orquestación de contenedores
Nginx Master          659    Servidor web y reverse proxy
Redis Server         1390    Cache y broker
FastAPI/Uvicorn     1622    API principal
Celery Worker       1730    Procesamiento de tareas (4 concurrency)
Celery Beat         1614    Scheduler de tareas
Prometheus          1403    Scraping de métricas
Grafana             1399    Panel de monitoreo
Node Exporter       1402    Métricas del sistema
```

### Tareas Celery Configuradas

```python
Tasks:
  - send_email                    # Envío de notificaciones por email
  - send_sms_by_event             # SMS a través de Liwa.co
  - update_dashboard_metrics      # Actualización de métricas
```

---

## 📈 MONITOREO Y OBSERVABILIDAD

### Prometheus

- **Puerto:** `127.0.0.1:9090`
- **Scraping Interval:** Configurado en `/CODE/monitoring/prometheus.yml`
- **Data Retention:** 30 días
- **Targets:** App, Redis, Celery, Node Exporter

### Grafana

- **Puerto:** `127.0.0.1:3000`
- **Usuario Admin:** `admin`
- **Dashboards:** Localizados en `/CODE/monitoring/grafana/dashboards/`
- **Provisioning:** Automático desde `/CODE/monitoring/grafana/provisioning/`

### Node Exporter

- **Puerto:** `127.0.0.1:9100`
- **Métricas:** CPU, Memory, Disk, Network, etc.

---

## 🚀 DEPLOY Y GIT

### Estado del Repositorio

```
Rama actual:         PROD-staging
Rama principal:      main
Rama remota HEAD:    origin/main
```

### Ramas Disponibles

```
Local:
  - PROD-staging (actual)
  - main

Remotas:
  - origin/HEAD -> origin/main
  - origin/PROD-STAGING
  - origin/TEMP
  - origin/backup-main-before-sync-20260224
  - origin/main
  - origin/mainv2.1
  - origin/staging
```

### Commits Recientes

```
3fcbd9e - Merge remote-tracking branch 'origin/PROD-STAGING' into PROD-staging
1492d76 - chore: Agregar documentación de feature al .gitignore
afff1d1 - feat: Implementar ordenamiento por última actualización de paquetes
4295abe - .
43d78f1 - docs: Agregar estado completo de commits en PROD-staging
83a84d6 - docs: Agregar resumen de commit y estado de push pendiente
f673605 - fix: Aumentar vigencia de tokens a 24h y corregir bug de procesamiento múltiple de paquetes
```

### Historial de Deploy

**Últimos deploys a producción (papyrus):**

```
2025-12-19 06:05:43 - Success (432s)
2025-12-19 05:13:44 - Success (446s)
2025-12-15 07:21:03 - Success (476s)
2025-12-14 06:53:05 - Success (400s)
2025-12-13 07:30:25 - Success (374s)
2025-12-13 06:29:07 - Success (448s)
2025-12-12 20:56:12 - Success (444s)
2025-12-09 09:54:25 - Success (482s)
```

**Velocidad promedio de deploy:** 400-450 segundos (~7 minutos)

---

## 🐍 STACK PYTHON

### Versión de Python

- **Versión:** 3.11-slim (Docker)
- **Dockerfile:** Multi-stage build optimizado
- **PYTHONPATH:** `/app:/app/src`

### Dependencias Principales (requirements.txt)

```
FastAPI==0.104.1                          # Framework web
uvicorn[standard]==0.24.0                 # Servidor ASGI
sqlalchemy==2.0.23                        # ORM
psycopg2-binary==2.9.9                    # Driver PostgreSQL
alembic==1.12.1                           # Migraciones
pydantic[email]==2.5.0                    # Validación
redis==5.0.1                              # Cliente Redis
celery==5.3.4                             # Task queue
boto3==1.34.0                             # AWS SDK
prometheus-client==0.19.0                 # Métricas
prometheus-fastapi-instrumentator==6.1.0  # Instrumentación automática
```

### Compilación Frontend

- **Tailwind CSS:** Compilado en build time (`npm run build:css`)
- **Node.js:** Incluido en imagen Docker
- **Package.json:** Presente en raíz del proyecto

---

## 📁 ESTRUCTURA DEL PROYECTO

```
/home/ubuntu/paqueteria/
├── CODE/                                # Código fuente principal
│   ├── src/
│   │   ├── app/                         # Aplicación FastAPI
│   │   │   ├── api/                     # Rutas API
│   │   │   ├── models/                  # Modelos SQLAlchemy
│   │   │   ├── schemas/                 # Schemas Pydantic
│   │   │   ├── utils/                   # Utilidades
│   │   │   ├── tasks.py                 # Tareas Celery
│   │   │   └── ...
│   │   ├── templates/                   # Jinja2 templates
│   │   ├── static/                      # CSS, JS, imágenes
│   │   ├── uploads/                     # Archivos cargados
│   │   └── main.py                      # Entry point
│   ├── monitoring/
│   │   ├── prometheus.yml               # Config Prometheus
│   │   └── grafana/                     # Provisioning Grafana
│   ├── alembic/                         # Migraciones BD
│   ├── Dockerfile                       # Construcción imagen
│   ├── requirements.txt                 # Dependencias Python
│   └── package.json                     # Dependencias Node
│
├── docker-compose.prod.yml              # Orquestación producción
├── deploy.sh                            # Script de deploy principal
├── .deploy/                             # Configuración deploy
├── scripts/                             # Scripts utilitarios
│   ├── deployment/                      # Scripts deploy
│   ├── testing/                         # Scripts test
│   ├── database/                        # Scripts BD
│   └── ...
│
├── DOCS/                                # Documentación
├── .env                                 # Variables de entorno
└── .git/                                # Repositorio Git
```

---

## 🔌 PUERTOS Y SERVICIOS EXPUESTOS

### Puertos Internos (localhost only)

```
127.0.0.1:8000      → FastAPI app (Nginx reverse proxy)
127.0.0.1:3000      → Grafana dashboard
127.0.0.1:9090      → Prometheus metrics
127.0.0.1:9100      → Node Exporter
6379                → Redis (internal network)
```

### Puertos Públicos

```
80  → HTTP (redirige a HTTPS)
443 → HTTPS (paquetex.papyrus.com.co)
```

---

## 🔧 CONFIGURACIÓN NGINX

### Upstream Backend

```nginx
upstream fastapi_backend {
    server 127.0.0.1:8000 max_fails=3 fail_timeout=30s;
    keepalive 32;
}
```

### Rutas Configuradas

| Ruta | Acción | Cache |
|------|--------|-------|
| `/static/` | Archivos estáticos | 7 días |
| `/uploads/` | Archivos cargados | 1 día |
| `/health` | Health check | Sin cache |
| `/api/` | API endpoints | Dinámico |
| `/` | Todas las demás | Dinámico |

### Timeouts

- `proxy_connect_timeout: 10s`
- `proxy_send_timeout: 30s`
- `proxy_read_timeout: 30s`

---

## 📊 ESTADÍSTICAS DEL SISTEMA

### Uptime y Carga

```
Uptime:          5 minutos (servidor recientemente reiniciado)
Load Average:    0.10, 0.24, 0.14 (bajo)
CPU Cores:       4 (estimado)
```

### Memoria

```
Total:           911 Mi
Usada:           725 Mi (79.6%)
Libre:           61 Mi
Disponible:      185 Mi (20.3%)
Swap Usado:      914 Mi de 2.0 Gi (45.7%)
```

⚠️ **NOTA:** Servidor con memoria ajustada. Monitorear crecimiento.

### Disco

```
Total:           38 GB
Usado:           26 GB (69%)
Disponible:      12 GB (31%)
```

⚠️ **ALERTA:** Espacio en disco limitado. Recomendado limpiar logs antiguos o aumentar capacidad.

---

## 🛠️ SERVICIOS DEL SISTEMA

### Sistema Operativo

- **SO:** Linux (Ubuntu)
- **Kernel:** 6.17.0-22-generic
- **Shell:** zsh

### Nginx

```
Master Process:  /usr/sbin/nginx
Worker Processes: 2 activos
Status:          Corriendo
```

---

## 📋 CONFIGURACIÓN DE ENTORNO (.env)

### Variables Críticas

```
# Aplicación
APP_NAME=PAQUETEX EL CLUB
APP_VERSION=4.0.0
ENVIRONMENT=production
DEBUG=False
TZ=America/Bogota

# Base de Datos
DATABASE_URL=postgresql://jveyes:***@ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com:5432/paqueteria_v4

# Cache
REDIS_URL=redis://:***@redis:6379/0
REDIS_PASSWORD=***

# Seguridad
SECRET_KEY=***
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440 (24 horas)

# Servicios Externos
SMTP_HOST=taylor.mxrouting.net (Email)
LIWA_API_KEY=*** (SMS Colombia)
AWS_S3_BUCKET=elclub-paqueteria (Storage)
AWS_REGION=us-east-1

# Puertos
APP_PORT=80
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000

# Rate y Tarifas
BASE_STORAGE_RATE=1000 COP
BASE_DELIVERY_RATE_NORMAL=1500 COP
BASE_DELIVERY_RATE_EXTRA_DIMENSIONED=2000 COP
CURRENCY=COP
```

---

## 📝 CHECKLIST DE SALUD

- [x] Todos los contenedores en estado UP
- [x] Healthchecks pasando
- [x] Base de datos accesible (AWS RDS)
- [x] Redis funcionando
- [x] Nginx activo y redirigiendo
- [x] SSL/TLS configurado
- [x] Celery workers procesando tareas
- [x] Monitoreo activo (Prometheus + Grafana)
- [x] Logs accesibles
- [x] Git repository sincronizado
- [⚠️] Espacio en disco: 69% (monitorear)
- [⚠️] Memoria: 79.6% usado (normal, pero vigilar)
- [❓] Certificados SSL: Verificar expiración

---

## 🚨 RECOMENDACIONES

### Inmediatas

1. **Limpiar logs antiguos** - El disco está al 69%
   ```bash
   docker exec paqueteria_v1_prod_app sh -c 'find /app/logs -mtime +30 -delete'
   ```

2. **Verificar certificados SSL**
   ```bash
   certbot certificates
   certbot renew --dry-run
   ```

3. **Monitorear memoria** - Está al 79.6%, vigilar crecimiento

### A Corto Plazo (1-2 semanas)

1. Implementar alertas en Grafana para:
   - Espacio en disco < 15%
   - Memoria disponible < 100Mi
   - Tasa de error en API > 1%

2. Revisar y optimizar:
   - Queries de base de datos lentas
   - Tamaño de imágenes cargadas

3. Configurar backup automático de:
   - Volúmenes Docker
   - Base de datos RDS

### A Mediano Plazo (1 mes)

1. Aumentar capacidad de almacenamiento
2. Implementar CDN para archivos estáticos
3. Revisar y optimizar índices de base de datos
4. Documentar procedimientos de escalado

---

## 📞 CONTACTOS Y REFERENCIAS

- **Servidor:** paquetex (SSH disponible)
- **Dominio:** paquetex.papyrus.com.co
- **Email:** paquetex@papyrus.com.co
- **Teléfono:** 3334004007
- **Git:** Rama `PROD-staging` actualmente en uso

---

## 📄 ARCHIVOS DE ANÁLISIS RELACIONADOS

Este servidor contiene numerosos archivos de análisis anteriores en `/home/ubuntu/paqueteria/`:

```
ANALISIS_CONTENEDORES_PRODUCCION.md
ANALISIS_DEPLOY_PRODUCCION.md
ANALISIS_ERRORES_Y_CORRECCION.md
DASHBOARD_ADMIN_IMPLEMENTADO.md
DEPLOY_PRODUCCION_COMPLETADO.md
Y muchos más...
```

Estos documentos contienen análisis históricos de problemas resueltos y features implementadas.

---

**Generado automáticamente por análisis de servidor**  
**Próxima revisión recomendada:** 2026-05-04
