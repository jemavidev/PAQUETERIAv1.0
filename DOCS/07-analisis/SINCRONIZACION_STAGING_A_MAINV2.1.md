# 📋 SINCRONIZACIÓN DE STAGING A MAINV2.1

## 🎯 OBJETIVO
Aplicar los cambios de configuración de staging (base de datos `paqueteria_staging`) a la rama `mainv2.1`.

---

## 📝 ARCHIVOS A SINCRONIZAR

### 1. **Archivos de Configuración de Staging** (Trackeados en Git)

#### Docker Compose
- ✅ `docker-compose.staging.yml` - Configuración de contenedores para staging
  - Usa `CODE/.env.staging`
  - Puerto 8001 (app)
  - Puerto 6380 (redis)
  - Volúmenes separados

#### Sistema de Deploy
- ✅ `.deploy/config/staging.conf` - Configuración del deploy para staging
  - Ya existe en ambas ramas
  - Usa `docker-compose.staging.yml`
  - Configuración SSH para servidor staging

### 2. **Archivos NO Trackeados** (Necesitan crearse manualmente)

#### Variables de Entorno
- ⚠️ `CODE/.env.staging` - **NO está en git** (en .gitignore)
  - Contiene credenciales sensibles
  - Apunta a `paqueteria_staging`
  - Puerto 8001, Redis 6380
  - S3 prefix: `staging/`

- ⚠️ `CODE/.env` - **NO está en git** (en .gitignore)
  - Para desarrollo local
  - Debe apuntar a `paqueteria_staging`

### 3. **Documentación Creada**

Archivos de documentación que explican la configuración:
- ✅ `ARQUITECTURA_BASE_DATOS.md`
- ✅ `RESUMEN_FINAL_CONFIGURACION.md`
- ✅ `DEPLOY_STAGING_CHECKLIST.md`
- ✅ `VERIFICACION_DEPLOY_STAGING.md`
- ✅ `DESPLIEGUE_STAGING_COMPLETADO.md`
- ✅ `ANALISIS_CONEXIONES_DB_COMPLETO.md`
- ✅ `ANALISIS_STAGING_ACTUAL.md`

---

## 🔄 PLAN DE SINCRONIZACIÓN

### PASO 1: Archivos Trackeados en Git
```bash
# Copiar docker-compose.staging.yml desde staging
git checkout staging -- docker-compose.staging.yml

# Verificar que .deploy/config/staging.conf esté actualizado
git diff staging mainv2.1 -- .deploy/config/staging.conf
```

### PASO 2: Archivos de Documentación
```bash
# Copiar documentación importante
git checkout staging -- ARQUITECTURA_BASE_DATOS.md
git checkout staging -- RESUMEN_FINAL_CONFIGURACION.md
git checkout staging -- DEPLOY_STAGING_CHECKLIST.md
git checkout staging -- VERIFICACION_DEPLOY_STAGING.md
git checkout staging -- DESPLIEGUE_STAGING_COMPLETADO.md
```

### PASO 3: Crear CODE/.env.staging (Manual)
Este archivo NO está en git, necesita crearse con el siguiente contenido:

```bash
# Ver contenido actual
cat CODE/.env.staging
```

**Contenido clave:**
- `DATABASE_URL=postgresql://...@...amazonaws.com:5432/paqueteria_staging`
- `POSTGRES_DB=paqueteria_staging`
- `REDIS_URL=redis://:Redis2025!Secure@redis:6380/0`
- `REDIS_PORT=6380`
- `S3_PREFIX=staging/`
- `ENVIRONMENT=staging`
- `APP_PORT=8000` (interno, mapeado a 8001 externamente)

### PASO 4: Actualizar CODE/.env (Manual)
Para desarrollo local, debe apuntar a staging:
- `DATABASE_URL` → `paqueteria_staging`
- `REDIS_PORT=6380`

---

## ⚠️ ARCHIVOS QUE NO SE DEBEN SINCRONIZAR

Archivos que son específicos de staging y NO deben ir a mainv2.1:
- ❌ Archivos de sincronización temporal (sync_*.py)
- ❌ Scripts de debug específicos de staging
- ❌ Archivos de prueba temporales

---

## ✅ VERIFICACIÓN POST-SINCRONIZACIÓN

Después de sincronizar, verificar:

1. **docker-compose.staging.yml**
   - ✅ `env_file: ./CODE/.env.staging`
   - ✅ Puerto 8001:8000
   - ✅ Redis puerto 6380

2. **CODE/.env.staging** (crear si no existe)
   - ✅ `DATABASE_URL` apunta a `paqueteria_staging`
   - ✅ `REDIS_PORT=6380`
   - ✅ `S3_PREFIX=staging/`

3. **CODE/.env** (actualizar)
   - ✅ Apunta a `paqueteria_staging` para desarrollo local

4. **.deploy/config/staging.conf**
   - ✅ `DOCKER_COMPOSE_FILE="docker-compose.staging.yml"`

---

## 🎯 RESUMEN DE CAMBIOS

### Archivos a Copiar desde Staging:
1. ✅ `docker-compose.staging.yml`
2. ✅ Documentación (5 archivos .md)

### Archivos a Crear/Actualizar Manualmente:
1. ⚠️ `CODE/.env.staging` (copiar contenido actual)
2. ⚠️ `CODE/.env` (actualizar para apuntar a staging)

### Archivos que Ya Existen (Verificar):
1. ✅ `.deploy/config/staging.conf`

---

## 📊 IMPACTO

### En Desarrollo Local:
- Apuntará a `paqueteria_staging` en AWS RDS
- Puerto 8001 (para no conflictuar con producción si corre localmente)

### En Servidor Staging:
- Usará `CODE/.env.staging`
- Conectará a `paqueteria_staging`
- Puerto 8001, Redis 6380

### En Producción:
- **SIN CAMBIOS** - Sigue usando `paqueteria_v4`
- Puerto 8000, Redis 6379

---

## 🚀 COMANDOS PARA EJECUTAR

```bash
# 1. Copiar docker-compose.staging.yml
git checkout staging -- docker-compose.staging.yml

# 2. Copiar documentación
git checkout staging -- ARQUITECTURA_BASE_DATOS.md \
                        RESUMEN_FINAL_CONFIGURACION.md \
                        DEPLOY_STAGING_CHECKLIST.md \
                        VERIFICACION_DEPLOY_STAGING.md \
                        DESPLIEGUE_STAGING_COMPLETADO.md

# 3. Verificar cambios
git status

# 4. Commit
git add docker-compose.staging.yml *.md
git commit -m "feat: Agregar configuración de staging con base de datos separada

- Agregar docker-compose.staging.yml con configuración para paqueteria_staging
- Documentar arquitectura de bases de datos
- Separar completamente staging de producción
- Puerto 8001 para staging, 8000 para producción
- Redis 6380 para staging, 6379 para producción"

# 5. IMPORTANTE: Crear CODE/.env.staging manualmente
# (No está en git por seguridad)
```

---

## 📝 NOTAS IMPORTANTES

1. **CODE/.env.staging NO está en git** por seguridad (contiene credenciales)
   - Debe crearse manualmente en cada entorno
   - Usar como referencia el archivo actual en staging

2. **Separación completa**
   - Staging: `paqueteria_staging`, puerto 8001, redis 6380
   - Producción: `paqueteria_v4`, puerto 8000, redis 6379

3. **Sin bases de datos locales**
   - Todos los entornos apuntan a AWS RDS
   - No hay contenedores de PostgreSQL

---

**¿Proceder con la sincronización?**
