# ✅ VERIFICACIÓN PRE-DEPLOY A STAGING

## 📋 RESUMEN

Todos los archivos están correctamente configurados para el despliegue a staging con la nueva base de datos `paqueteria_staging` en AWS RDS.

---

## ✅ ARCHIVOS VERIFICADOS

### 1. **CODE/.env.staging** ✅
- **Base de datos**: `paqueteria_staging` (AWS RDS)
- **Puerto**: 8001 (sin conflicto con producción)
- **Redis**: Puerto 6380 (sin conflicto con producción)
- **S3 Prefix**: `staging/` (separado de producción)
- **Conexión a producción**: Configurada para sincronización (solo lectura)

```bash
DATABASE_URL=postgresql://jveyes:...@ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com:5432/paqueteria_staging
```

### 2. **docker-compose.staging.yml** ✅
- **env_file**: `./CODE/.env.staging` ✅
- **Puerto app**: 8001:8000 (sin conflicto)
- **Puerto redis**: 6380:6380 (sin conflicto)
- **Volúmenes**: Separados de producción
- **Red**: `paqueteria_staging_network` (separada)

### 3. **.deploy/config/staging.conf** ✅
- **DOCKER_COMPOSE_FILE**: `docker-compose.staging.yml` ✅
- **SSH_HOST**: staging ✅
- **GIT_BRANCH**: staging ✅
- **DOCKER_REBUILD_ON_DEPLOY**: true ✅
- **HEALTH_CHECK_URL**: http://localhost:8001/health ✅

### 4. **deploy.sh** ✅
- Script completo con soporte para múltiples entornos
- Maneja correctamente SSH, Git, Docker, Health Checks
- Soporta modo interactivo y CLI

---

## 🎯 ARQUITECTURA DE BASES DE DATOS

```
┌─────────────────────────────────────────────────────────────┐
│           AWS RDS PostgreSQL (us-east-1)                    │
│  ls-abe25e9bea57818f0ee32555c0e7b4a10e361535...            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📦 paqueteria_v4 (PRODUCCIÓN)                             │
│     └─── Servidor Producción (papyrus.com.co)             │
│                                                             │
│  📦 paqueteria_staging (STAGING)                           │
│     ├─── Servidor Staging (staging.jemavi.co)             │
│     └─── Localhost (desarrollo)                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### ✅ PRINCIPIO CRÍTICO CUMPLIDO
**NO HAY BASES DE DATOS LOCALES** - Todos los entornos apuntan a AWS RDS

---

## 🚀 COMANDOS DE DESPLIEGUE

### Opción 1: Modo Interactivo
```bash
./deploy.sh
# Seleccionar: staging
# Seleccionar: 1) Deploy Completo
```

### Opción 2: Modo CLI (Recomendado)
```bash
./deploy.sh --env staging --deploy
```

### Verificar Estado
```bash
./deploy.sh --env staging --status
```

### Ver Logs
```bash
./deploy.sh --env staging --logs
```

### Health Check
```bash
./deploy.sh --env staging --health
```

---

## 📝 QUÉ HARÁ EL DEPLOY

1. **Git Operations**:
   - Checkout a rama `staging`
   - Pull últimos cambios
   - Commit automático si hay cambios

2. **Docker Operations**:
   - Build imagen con `docker-compose.staging.yml`
   - Usa `CODE/.env.staging` como configuración
   - Levanta servicios: app + redis
   - Mapea puerto 8001 (sin conflicto con producción)

3. **Health Check**:
   - Verifica que la app responda en `http://localhost:8001/health`
   - 30 reintentos cada 2 segundos (60s timeout total)

4. **Conexión a Base de Datos**:
   - App se conecta a `paqueteria_staging` en AWS RDS
   - Todos los endpoints usan `Depends(get_db)` → `DATABASE_URL`
   - No hay cambios de código necesarios

---

## 🔍 VERIFICACIONES POST-DEPLOY

### 1. Verificar que el contenedor está corriendo
```bash
ssh ubuntu@staging "docker ps | grep paqueteria_staging"
```

### 2. Verificar conexión a base de datos
```bash
ssh ubuntu@staging "docker logs paqueteria_staging_app | grep -i database"
```

### 3. Verificar health endpoint
```bash
curl http://staging.jemavi.co/health
```

### 4. Verificar que usa paqueteria_staging
```bash
ssh ubuntu@staging "docker exec paqueteria_staging_app env | grep DATABASE_URL"
```

---

## ⚠️ NOTAS IMPORTANTES

### Servidor Staging
- **IP**: 3.81.183.102
- **Dominio**: staging.jemavi.co
- **RAM**: 416MB + 1GB SWAP (recursos limitados)
- **Configuración**: Ultra minimal (solo app + redis)

### Base de Datos
- **Nombre**: `paqueteria_staging`
- **Ubicación**: AWS RDS (mismo servidor que producción)
- **Estado**: Ya existe y está lista para usar
- **Separación**: Completamente separada de `paqueteria_v4`

### Sincronización
- Staging puede leer de producción vía `PROD_DATABASE_URL`
- Producción NUNCA lee de staging
- Datos de staging son independientes

---

## ✅ CHECKLIST PRE-DEPLOY

- [x] `CODE/.env.staging` apunta a `paqueteria_staging`
- [x] `docker-compose.staging.yml` usa `CODE/.env.staging`
- [x] `.deploy/config/staging.conf` usa `docker-compose.staging.yml`
- [x] `deploy.sh` tiene soporte completo para staging
- [x] Base de datos `paqueteria_staging` existe en AWS RDS
- [x] Puertos no conflictúan (8001 staging, 8000 producción)
- [x] Redis no conflictúa (6380 staging, 6379 producción)
- [x] Volúmenes separados
- [x] Red separada

---

## 🎯 PRÓXIMOS PASOS

1. **Ejecutar deploy**:
   ```bash
   ./deploy.sh --env staging --deploy
   ```

2. **Verificar que funciona**:
   ```bash
   curl http://staging.jemavi.co/health
   ```

3. **Verificar base de datos**:
   - Acceder a https://staging.jemavi.co/invoices
   - Verificar que la lista está vacía (base de datos nueva)
   - Probar crear/editar registros

4. **Sincronizar datos si es necesario**:
   - Usar scripts de sincronización para copiar datos de producción a staging
   - O trabajar con datos de prueba

---

## 📚 DOCUMENTACIÓN RELACIONADA

- `ARQUITECTURA_BASE_DATOS.md` - Arquitectura completa de bases de datos
- `RESUMEN_FINAL_CONFIGURACION.md` - Resumen de configuración
- `DEPLOY_STAGING_CHECKLIST.md` - Checklist de despliegue
- `.deploy/docs/README.md` - Documentación del sistema de deploy
- `.deploy/docs/QUICKSTART.md` - Guía rápida de deploy

---

**TODO ESTÁ LISTO PARA EL DEPLOY** ✅
