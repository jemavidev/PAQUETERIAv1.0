# 🚀 CÓMO FUNCIONA EL SISTEMA DE DEPLOY Y ARCHIVOS .ENV

**Fecha**: 2026-01-29  
**Proyecto**: PAQUETEX v1.0

---

## 📊 RESUMEN

El proyecto usa un **sistema de deploy unificado** (`deploy.sh`) que maneja 3 entornos diferentes, cada uno con su propio archivo `.env` y `docker-compose.yml`.

---

## 🎯 ARQUITECTURA DEL SISTEMA

```
┌─────────────────────────────────────────────────────────────┐
│                      deploy.sh                              │
│                  (Script Principal)                         │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┴──────────┬──────────────────┐
        │                     │                  │
   ┌────▼────┐          ┌─────▼─────┐     ┌─────▼──────┐
   │LOCALHOST│          │  STAGING  │     │ PRODUCCIÓN │
   └────┬────┘          └─────┬─────┘     └─────┬──────┘
        │                     │                  │
   ┌────▼────────┐      ┌─────▼──────────┐ ┌────▼────────────┐
   │localhost.conf│      │staging.conf    │ │papyrus.conf     │
   └────┬────────┘      └─────┬──────────┘ └────┬────────────┘
        │                     │                  │
   ┌────▼──────────────┐ ┌───▼────────────────┐ ┌▼───────────────────┐
   │docker-compose.    │ │docker-compose.     │ │docker-compose.     │
   │dev.yml            │ │staging.yml         │ │prod.yml            │
   └────┬──────────────┘ └───┬────────────────┘ └┬───────────────────┘
        │                     │                   │
   ┌────▼──────┐        ┌────▼──────┐       ┌───▼──────────┐
   │CODE/.env  │        │.env.staging│       │.env.production│
   └───────────┘        └───────────┘       └──────────────┘
```

---

## 📁 ESTRUCTURA DE ARCHIVOS

### Sistema de Deploy

```
.deploy/
├── config/
│   ├── deploy.conf          # Configuración global
│   ├── localhost.conf       # Config LOCALHOST ✅
│   ├── staging.conf         # Config STAGING ✅
│   └── papyrus.conf         # Config PRODUCCIÓN ✅
├── lib/
│   ├── colors.sh            # Colores para terminal
│   └── git.sh               # Funciones de Git
├── hooks/
│   ├── pre-deploy-papyrus.sh
│   └── post-deploy-papyrus.sh
└── docs/
    └── ...

deploy.sh                     # Script principal ✅
```

### Docker Compose Files

```
Raíz/
├── docker-compose.dev.yml       # LOCALHOST ✅
├── docker-compose.staging.yml   # STAGING ✅
└── docker-compose.prod.yml      # PRODUCCIÓN ✅
```

### Archivos .env

```
Raíz/
├── .env                    # LOCALHOST (desarrollo)
├── .env.staging            # STAGING ✅
└── .env.production         # PRODUCCIÓN ✅

CODE/
├── .env                        # LOCALHOST (sin Docker)
├── .env.staging.example        # Template ✅ En git
└── .env.production.example     # Template ✅ En git
```

---

## 🔧 CONFIGURACIÓN POR ENTORNO

### 1️⃣ LOCALHOST (Desarrollo Local)

#### Archivo de Configuración
**Ubicación**: `.deploy/config/localhost.conf`

```bash
ENV_NAME="localhost"
ENV_TYPE="local"
DOCKER_COMPOSE_FILE="docker-compose.dev.yml"  # ✅
GIT_BRANCH="main"
```

#### Docker Compose
**Archivo**: `docker-compose.dev.yml`

```yaml
services:
  app:
    # NO especifica env_file (usa variables del sistema)
    environment:
      - DATABASE_URL=${DATABASE_URL}  # Lee de CODE/.env
```

#### Archivo .env
**Ubicación**: `CODE/.env` (implícito)

```bash
DATABASE_URL=postgresql://...paqueteria_staging
ENVIRONMENT=development
PORT=8000
```

#### Comando de Deploy
```bash
./deploy.sh --env localhost --deploy
```

---

### 2️⃣ STAGING (Servidor de Pruebas)

#### Archivo de Configuración
**Ubicación**: `.deploy/config/staging.conf`

```bash
ENV_NAME="staging"
ENV_TYPE="remote"
SSH_HOST="staging"
DOCKER_COMPOSE_FILE="docker-compose.staging.yml"  # ✅
GIT_BRANCH="staging"
PROJECT_PATH="/home/ubuntu/paqueteria-staging"
```

#### Docker Compose
**Archivo**: `docker-compose.staging.yml`

```yaml
services:
  app:
    env_file:
      - ./.env.staging  # ✅ CORRECTO
    environment:
      - ENVIRONMENT=staging
```

#### Archivo .env
**Ubicación**: `.env.staging` (raíz del proyecto)

```bash
DATABASE_URL=postgresql://...paqueteria_staging
ENVIRONMENT=staging
PORT=8001
REDIS_PORT=6380
```

#### Comando de Deploy
```bash
./deploy.sh --env staging --deploy
```

---

### 3️⃣ PRODUCCIÓN (Servidor AWS)

#### Archivo de Configuración
**Ubicación**: `.deploy/config/papyrus.conf`

```bash
ENV_NAME="papyrus"
ENV_TYPE="remote"
SSH_HOST="papyrus"
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"  # ✅
GIT_BRANCH="main"
PROJECT_PATH="/home/ubuntu/paqueteria"
```

#### Docker Compose
**Archivo**: `docker-compose.prod.yml`

```yaml
services:
  app:
    env_file:
      - ./.env.production  # ✅ CORRECTO
  
  celery_worker:
    env_file:
      - ./.env.production  # ✅ CORRECTO
  
  celery_beat:
    env_file:
      - ./.env.production  # ✅ CORRECTO
```

#### Archivo .env
**Ubicación**: `.env.production` (raíz del proyecto)

```bash
DATABASE_URL=postgresql://...paqueteria_v4
ENVIRONMENT=production
PORT=8000
REDIS_PORT=6379
DEBUG=False
```

#### Comando de Deploy
```bash
./deploy.sh --env papyrus --deploy
```

---

## 🔄 FLUJO DE DEPLOY

### Paso 1: Seleccionar Entorno

```bash
./deploy.sh
# O directamente:
./deploy.sh --env staging --deploy
```

### Paso 2: Deploy.sh Carga Configuración

```bash
# deploy.sh lee:
source .deploy/config/staging.conf

# Obtiene:
DOCKER_COMPOSE_FILE="docker-compose.staging.yml"
ENV_TYPE="remote"
SSH_HOST="staging"
```

### Paso 3: Docker Compose Lee .env

```bash
# docker-compose.staging.yml especifica:
env_file:
  - ./.env.staging

# Docker Compose carga variables de .env.staging
```

### Paso 4: Aplicación Usa Variables

```python
# CODE/src/app/config.py
DATABASE_URL = os.getenv("DATABASE_URL")
ENVIRONMENT = os.getenv("ENVIRONMENT")
```

---

## 📊 TABLA COMPARATIVA

| Componente | LOCALHOST | STAGING | PRODUCCIÓN |
|------------|-----------|---------|------------|
| **Config Deploy** | `localhost.conf` | `staging.conf` | `papyrus.conf` |
| **Docker Compose** | `dev.yml` | `staging.yml` | `prod.yml` |
| **Archivo .env** | `CODE/.env` | `.env.staging` | `.env.production` |
| **Base de Datos** | `paqueteria_staging` | `paqueteria_staging` | `paqueteria_v4` |
| **Puerto App** | 8000 | 8001 | 8000 |
| **Puerto Redis** | 6379 | 6380 | 6379 |
| **Tipo** | Local | Remote (SSH) | Remote (SSH) |
| **Rama Git** | `main` | `staging` | `main` |

---

## ✅ VERIFICACIÓN

### Verificar Configuración de Deploy

```bash
# Ver qué docker-compose usa cada entorno
grep "DOCKER_COMPOSE_FILE" .deploy/config/*.conf

# Resultado esperado:
# localhost.conf:DOCKER_COMPOSE_FILE="docker-compose.dev.yml"
# staging.conf:DOCKER_COMPOSE_FILE="docker-compose.staging.yml"
# papyrus.conf:DOCKER_COMPOSE_FILE="docker-compose.prod.yml"
```

### Verificar Archivos .env en Docker Compose

```bash
# Ver qué .env usa cada docker-compose
grep -A1 "env_file:" docker-compose.*.yml

# Resultado esperado:
# docker-compose.staging.yml:    env_file:
# docker-compose.staging.yml-      - ./.env.staging
# docker-compose.prod.yml:    env_file:
# docker-compose.prod.yml-      - ./.env.production
```

### Verificar Base de Datos

```bash
# Ver qué BD usa cada .env
echo "LOCALHOST:" && grep DATABASE_URL CODE/.env | head -1
echo "STAGING:" && grep DATABASE_URL .env.staging | head -1
echo "PRODUCCIÓN:" && grep DATABASE_URL .env.production | head -1
```

---

## 🚀 COMANDOS ÚTILES

### Deploy Completo

```bash
# LOCALHOST
./deploy.sh --env localhost --deploy

# STAGING
./deploy.sh --env staging --deploy

# PRODUCCIÓN
./deploy.sh --env papyrus --deploy
```

### Ver Configuración

```bash
# Modo interactivo
./deploy.sh
# Seleccionar entorno
# Opción [C] - Ver Configuración Actual
```

### Ver Estado

```bash
./deploy.sh --env staging --status
./deploy.sh --env papyrus --status
```

### Ver Logs

```bash
./deploy.sh --env staging --logs
./deploy.sh --env papyrus --logs
```

---

## 🔐 SEGURIDAD

### Archivos que NO deben estar en Git

```gitignore
# Archivos con credenciales
.env
.env.staging
.env.production
CODE/.env
CODE/.env.staging
CODE/.env.production

# Solo templates en git
CODE/.env.staging.example      ✅
CODE/.env.production.example   ✅
```

### Crear Archivos .env desde Templates

```bash
# Staging
cp CODE/.env.staging.example .env.staging
nano .env.staging  # Editar con credenciales reales

# Producción
cp CODE/.env.production.example .env.production
nano .env.production  # Editar con credenciales reales
```

---

## 📝 NOTAS IMPORTANTES

1. **deploy.sh NO modifica archivos .env**
   - Solo lee la configuración de `.deploy/config/*.conf`
   - Docker Compose es quien carga los archivos `.env`

2. **Cada entorno tiene su propio docker-compose**
   - `localhost.conf` → `docker-compose.dev.yml`
   - `staging.conf` → `docker-compose.staging.yml`
   - `papyrus.conf` → `docker-compose.prod.yml`

3. **Cada docker-compose especifica su .env**
   - `docker-compose.staging.yml` → `.env.staging`
   - `docker-compose.prod.yml` → `.env.production`

4. **Sistema completamente desacoplado**
   - Cambiar configuración: Editar `.deploy/config/*.conf`
   - Cambiar variables: Editar `.env.*`
   - Cambiar servicios: Editar `docker-compose.*.yml`

---

## 📚 DOCUMENTACIÓN RELACIONADA

- [Estructura de Archivos .env](../02-configuracion/ESTRUCTURA_ARCHIVOS_ENV.md)
- [Análisis Docker Compose](../01-arquitectura/ANALISIS_DOCKER_COMPOSE_FILES.md)
- [Arquitectura de Base de Datos](../01-arquitectura/ARQUITECTURA_BASE_DATOS.md)
- [Deploy Staging Checklist](./DEPLOY_STAGING_CHECKLIST.md)

---

**Última actualización**: 2026-01-29  
**Sistema**: deploy.sh v2.2.0
