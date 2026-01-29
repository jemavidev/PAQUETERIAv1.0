# 📝 ESTRUCTURA DE ARCHIVOS .ENV

**Fecha**: 2026-01-29  
**Proyecto**: PAQUETEX v1.0

---

## 📊 RESUMEN

El proyecto utiliza **archivos `.env` separados** para cada entorno, ubicados en **dos ubicaciones diferentes** según el propósito.

---

## 📁 UBICACIÓN DE ARCHIVOS .ENV

### 🗂️ Raíz del Proyecto (para Docker Compose)

```
PAQUETEX v1.0/
├── .env                    → LOCALHOST (desarrollo local)
├── .env.staging            → STAGING (servidor de pruebas)
├── .env.production         → PRODUCCIÓN (servidor de producción)
└── docker-compose.*.yml    → Usan estos archivos
```

**Uso**: Los archivos docker-compose leen estos archivos.

### 🗂️ CODE/ (para desarrollo sin Docker)

```
CODE/
├── .env                        → LOCALHOST (desarrollo local)
├── .env.staging                → STAGING (referencia)
├── .env.staging.example        → Template de staging
└── .env.production.example     → Template de producción
```

**Uso**: Para desarrollo directo con Python (sin Docker).

---

## 🎯 MAPEO: ENTORNO → ARCHIVO .ENV

| Entorno | Docker Compose | Archivo .env | Base de Datos |
|---------|----------------|--------------|---------------|
| **LOCALHOST** | `docker-compose.dev.yml` | `CODE/.env` | `paqueteria_staging` |
| **STAGING** | `docker-compose.staging.yml` | `.env.staging` | `paqueteria_staging` |
| **PRODUCCIÓN** | `docker-compose.prod.yml` | `.env.production` | `paqueteria_v4` |

---

## 📋 CONFIGURACIÓN POR ARCHIVO

### 1️⃣ `.env` (Raíz) - LOCALHOST

**Ubicación**: `./env`  
**Usado por**: Desarrollo local sin Docker  
**Base de datos**: `paqueteria_staging`

```bash
ENVIRONMENT=development
DATABASE_URL=postgresql://...paqueteria_staging
PORT=8000
DEBUG=True
```

### 2️⃣ `CODE/.env` - LOCALHOST (Docker)

**Ubicación**: `CODE/.env`  
**Usado por**: `docker-compose.dev.yml`  
**Base de datos**: `paqueteria_staging`

```bash
ENVIRONMENT=development
DATABASE_URL=postgresql://...paqueteria_staging
PORT=8000
DEBUG=True
```

### 3️⃣ `.env.staging` (Raíz) - STAGING

**Ubicación**: `./.env.staging`  
**Usado por**: `docker-compose.staging.yml`  
**Base de datos**: `paqueteria_staging`

```bash
ENVIRONMENT=staging
DATABASE_URL=postgresql://...paqueteria_staging
PORT=8001
REDIS_PORT=6380
S3_PREFIX=staging/
```

### 4️⃣ `CODE/.env.staging` - STAGING (Referencia)

**Ubicación**: `CODE/.env.staging`  
**Usado por**: Referencia (no usado por Docker)  
**Base de datos**: `paqueteria_staging`

### 5️⃣ `.env.production` (Raíz) - PRODUCCIÓN

**Ubicación**: `./.env.production`  
**Usado por**: `docker-compose.prod.yml`  
**Base de datos**: `paqueteria_v4`

```bash
ENVIRONMENT=production
DATABASE_URL=postgresql://...paqueteria_v4
PORT=8000
REDIS_PORT=6379
DEBUG=False
```

---

## 🔧 CONFIGURACIÓN EN DOCKER-COMPOSE

### `docker-compose.dev.yml` - LOCALHOST

```yaml
services:
  app:
    # NO usa env_file (usa variables de entorno directamente)
    environment:
      - DATABASE_URL=${DATABASE_URL}  # Lee de CODE/.env
      - ENVIRONMENT=development
```

**Nota**: Lee variables del sistema o de `CODE/.env` si está configurado.

### `docker-compose.staging.yml` - STAGING

```yaml
services:
  app:
    env_file:
      - ./.env.staging  # ✅ Archivo correcto
    environment:
      - ENVIRONMENT=staging
```

### `docker-compose.prod.yml` - PRODUCCIÓN

```yaml
services:
  app:
    env_file:
      - ./.env.production  # ✅ Archivo correcto
  
  celery_worker:
    env_file:
      - ./.env.production  # ✅ Archivo correcto
  
  celery_beat:
    env_file:
      - ./.env.production  # ✅ Archivo correcto
```

---

## ⚠️ ARCHIVOS QUE NO DEBEN ESTAR EN GIT

```gitignore
# Archivos con credenciales reales
.env
.env.staging
.env.production
CODE/.env
CODE/.env.staging
CODE/.env.production

# Solo los .example deben estar en git
CODE/.env.staging.example      ✅ En git
CODE/.env.production.example   ✅ En git
```

---

## 🔐 DIFERENCIAS CLAVE ENTRE ENTORNOS

| Variable | LOCALHOST | STAGING | PRODUCCIÓN |
|----------|-----------|---------|------------|
| `ENVIRONMENT` | `development` | `staging` | `production` |
| `DATABASE_URL` | `...paqueteria_staging` | `...paqueteria_staging` | `...paqueteria_v4` |
| `PORT` | `8000` | `8001` | `8000` |
| `REDIS_PORT` | `6379` | `6380` | `6379` |
| `DEBUG` | `True` | `False` | `False` |
| `S3_PREFIX` | `dev/` | `staging/` | `` (raíz) |

---

## 🚀 COMANDOS DE USO

### LOCALHOST (Desarrollo)

```bash
# Con Docker
docker compose -f docker-compose.dev.yml up -d
# Lee: CODE/.env (implícitamente)

# Sin Docker
cd CODE
python -m uvicorn src.main:app --reload
# Lee: CODE/.env
```

### STAGING

```bash
# Con Docker
docker compose -f docker-compose.staging.yml up -d
# Lee: ./.env.staging

# Verificar configuración
docker compose -f docker-compose.staging.yml config
```

### PRODUCCIÓN

```bash
# Con Docker
docker compose -f docker-compose.prod.yml up -d
# Lee: ./.env.production

# Verificar configuración
docker compose -f docker-compose.prod.yml config
```

---

## 📝 CREAR ARCHIVOS .ENV DESDE TEMPLATES

### Para Staging

```bash
# Copiar template
cp CODE/.env.staging.example .env.staging

# Editar con credenciales reales
nano .env.staging
```

### Para Producción

```bash
# Copiar template
cp CODE/.env.production.example .env.production

# Editar con credenciales reales
nano .env.production
```

---

## ✅ CHECKLIST DE VERIFICACIÓN

- [ ] `.env` existe en raíz (para desarrollo local)
- [ ] `.env.staging` existe en raíz (para staging)
- [ ] `.env.production` existe en raíz (para producción)
- [ ] `CODE/.env` existe (para desarrollo sin Docker)
- [ ] Todos los archivos `.env` tienen `DATABASE_URL` correcto
- [ ] Staging apunta a `paqueteria_staging`
- [ ] Producción apunta a `paqueteria_v4`
- [ ] Archivos `.env` NO están en git
- [ ] Solo archivos `.example` están en git

---

## 🔍 VERIFICAR CONFIGURACIÓN

```bash
# Ver qué archivo .env usa cada docker-compose
grep -A1 "env_file:" docker-compose.*.yml

# Verificar base de datos en cada archivo
echo "=== LOCALHOST ===" && grep DATABASE_URL CODE/.env | head -1
echo "=== STAGING ===" && grep DATABASE_URL .env.staging | head -1
echo "=== PRODUCCIÓN ===" && grep DATABASE_URL .env.production | head -1
```

---

## 📚 DOCUMENTACIÓN RELACIONADA

- [Arquitectura de Base de Datos](../01-arquitectura/ARQUITECTURA_BASE_DATOS.md)
- [Análisis Docker Compose](../01-arquitectura/ANALISIS_DOCKER_COMPOSE_FILES.md)
- [Resumen Final Configuración](./RESUMEN_FINAL_CONFIGURACION.md)

---

**Última actualización**: 2026-01-29  
**Commit**: Pendiente
