# 🔍 Análisis de Estructura: Producción vs Staging

## 📊 ESTADO ACTUAL DEL SISTEMA

### 🎯 Resumen Ejecutivo

**Situación Actual:**
- ✅ **Producción:** Funcionando en AWS RDS con `paqueteria_v4`
- ⚠️ **Staging:** Usa la MISMA base de datos que producción
- ❌ **Problema:** No hay separación real de ambientes

---

## 🗄️ BASES DE DATOS ACTUALES

### Producción (MAIN)
```yaml
Base de datos: paqueteria_v4
Host: ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com
Puerto: 5432
Usuario: jveyes
Ambiente: production
Rama Git: main
```

### Staging (STAGING)
```yaml
Base de datos: paqueteria_v4  ⚠️ MISMA QUE PRODUCCIÓN
Host: ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com
Puerto: 5432
Usuario: jveyes
Ambiente: staging
Rama Git: staging
```

**⚠️ RIESGO CRÍTICO:** Staging y Producción comparten la misma base de datos

---

## 🐳 CONTENEDORES DOCKER

### Producción
```yaml
Compose: docker-compose.prod.yml
Stack: "PAQUETERIA v1.0 PROD"
Contenedores:
  - paqueteria_v1_prod_app (Puerto: 8000)
  - paqueteria_v1_prod_redis (Puerto: 6379)
  - paqueteria_v1_prod_celery
  - paqueteria_v1_prod_celery_beat
  - paqueteria_v1_prod_prometheus (Puerto: 9090)
  - paqueteria_v1_prod_grafana (Puerto: 3000)
  - paqueteria_v1_prod_node_exporter (Puerto: 9100)

Red: paqueteria_v1_prod_network
Volúmenes:
  - redis_data
  - uploads_data
  - logs_data
  - backups_data
  - celery_beat_data
  - prometheus_data
  - grafana_data
```

### Staging
```yaml
Compose: docker-compose.staging.yml
Stack: "PAQUETERIA_STAGING"
Contenedores:
  - paqueteria_staging_app (Puerto: 8001)
  - paqueteria_staging_redis (Puerto: 6380)

Red: paqueteria_staging_network
Volúmenes:
  - redis_staging_data
  - uploads_staging_data
  - logs_staging_data
```

**✅ BIEN:** Contenedores y puertos separados
**❌ MAL:** Base de datos compartida

---

## 📁 ESTRUCTURA DE ARCHIVOS

### Archivos de Configuración

```
Raíz del proyecto:
├── .env                              # ⚠️ Producción (paqueteria_v4)
├── docker-compose.prod.yml           # ✅ Producción
├── docker-compose.staging.yml        # ✅ Staging
├── docker-compose.dev.yml            # ✅ Desarrollo local
├── docker-compose.staging-minimal.yml # ✅ Staging mínimo
└── docker-compose.lightsail.yml      # ✅ Lightsail

CODE/:
├── .env                              # ⚠️ Desarrollo (placeholder)
├── .env.production.example           # ✅ Ejemplo producción
└── Dockerfile                        # ✅ Compartido
```

### Scripts de Deployment

```
Raíz:
├── deploy.sh                         # ⚠️ ¿Producción o Staging?
├── check_staging.sh                  # ✅ Staging
├── fix_staging.sh                    # ✅ Staging
├── restart_staging_correct.sh        # ✅ Staging
├── staging_health_check.sh           # ✅ Staging
└── start-dev.sh                      # ✅ Desarrollo

scripts/:
├── database/
│   ├── sync_prod_to_staging_initial.sh    # 🆕 Creado
│   └── sync_prod_to_staging_daily.sh      # 🆕 Creado
├── deploy/
├── deployment/
└── testing/
```

---

## 🔍 IDENTIFICACIÓN: ¿QUÉ ES DE STAGING Y QUÉ ES DE PRODUCCIÓN?

### ✅ PRODUCCIÓN (MAIN)

**Código:**
- Rama: `main`
- Funcionalidades: Estables y probadas
- Tablas DB:
  - users
  - accounts
  - packages
  - customers
  - rates
  - messages
  - announcements
  - package_events
  - customer_preferences
  - files
  - notifications
  - products (DynamiaERP)
  - product_column_config
  - product_sync_log

**Infraestructura:**
- Base de datos: `paqueteria_v4` (AWS RDS)
- Contenedores: `paqueteria_v1_prod_*`
- Puerto: 8000
- Redis: 6379
- Monitoreo: Prometheus + Grafana

### ⚠️ STAGING (STAGING)

**Código:**
- Rama: `staging`
- Funcionalidades: En desarrollo/prueba
- Tablas DB adicionales (que NO están en producción):
  - invoice_items ✨
  - cufe_records ✨
  - supplier_invoices ✨
  - dian_pdfs ✨
  - (otras tablas de facturas/CUFE)

**Infraestructura:**
- Base de datos: `paqueteria_v4` ⚠️ MISMA QUE PRODUCCIÓN
- Contenedores: `paqueteria_staging_*`
- Puerto: 8001
- Redis: 6380

---

## 🚨 PROBLEMAS IDENTIFICADOS

### 1. Base de Datos Compartida ⚠️⚠️⚠️

**Problema:**
```
Producción → paqueteria_v4 ←─┐
                              ├─ MISMA DB
Staging    → paqueteria_v4 ←─┘
```

**Riesgos:**
- ❌ Staging puede modificar datos de producción
- ❌ Migraciones de staging afectan producción
- ❌ Pruebas en staging pueden romper producción
- ❌ No se pueden probar cambios destructivos
- ❌ Datos de prueba mezclados con datos reales

### 2. Configuración .env Ambigua

**Problema:**
- `.env` en raíz apunta a producción
- Staging usa el mismo `.env`
- No hay `.env.staging` separado

### 3. Migraciones Sin Control

**Problema:**
- Alembic apunta a la misma DB
- No hay control de qué migraciones van a cada ambiente
- Riesgo de aplicar migraciones de staging en producción

---

## ✅ SOLUCIÓN PROPUESTA

### Arquitectura Objetivo

```
┌─────────────────────────────────────────────────────────────────┐
│                        AWS RDS                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────┐         ┌──────────────────────┐     │
│  │   PRODUCCIÓN         │         │     STAGING          │     │
│  │  paqueteria_v4       │    X    │  paqueteria_staging  │     │
│  │                      │  (NO)   │                      │     │
│  │  Rama: main          │  SYNC   │  Rama: staging       │     │
│  │  Puerto: 8000        │         │  Puerto: 8001        │     │
│  │  Redis: 6379         │         │  Redis: 6380         │     │
│  │                      │         │                      │     │
│  │  Datos: REALES       │────────▶│  Datos: COPIA        │     │
│  │  Solo lectura        │  Sync   │  + Tablas nuevas     │     │
│  │  desde staging       │  Diaria │  + Datos de prueba   │     │
│  └──────────────────────┘         └──────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 PLAN DE SEPARACIÓN

### Fase 1: Crear Base de Datos Staging

```bash
# 1. Crear nueva instancia RDS o nueva base de datos
aws rds create-db-instance \
  --db-instance-identifier paqueteria-staging \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username jveyes \
  --master-user-password "STAGING_PASSWORD" \
  --allocated-storage 20

# O crear nueva base de datos en la misma instancia
psql -h $PROD_HOST -U jveyes -d postgres -c "CREATE DATABASE paqueteria_staging;"
```

### Fase 2: Configurar Variables de Entorno

**Crear `.env.production` (renombrar `.env` actual):**
```bash
# Producción
DATABASE_URL=postgresql://jveyes:password@prod-host:5432/paqueteria_v4
ENVIRONMENT=production
DEBUG=False
```

**Crear `.env.staging` (nuevo):**
```bash
# Staging
DATABASE_URL=postgresql://jveyes:password@staging-host:5432/paqueteria_staging
ENVIRONMENT=staging
DEBUG=True

# Conexión a producción (solo lectura para sincronización)
PROD_DATABASE_URL=postgresql://jveyes:password@prod-host:5432/paqueteria_v4
```

### Fase 3: Actualizar Docker Compose

**docker-compose.prod.yml:**
```yaml
services:
  app:
    env_file:
      - .env.production  # ← Cambiar
```

**docker-compose.staging.yml:**
```yaml
services:
  app:
    env_file:
      - .env.staging  # ← Cambiar
```

### Fase 4: Sincronización Inicial

```bash
# Copiar estructura y datos de producción a staging
./scripts/database/sync_prod_to_staging_initial.sh
```

### Fase 5: Aplicar Migraciones de Staging

```bash
# En staging, aplicar migraciones adicionales
cd CODE
DATABASE_URL=postgresql://staging-url alembic upgrade head
```

### Fase 6: Configurar Sincronización Automática

```bash
# Cron job para sincronización diaria
crontab -e

# Agregar:
0 2 * * * /path/to/scripts/database/sync_prod_to_staging_daily.sh
```

---

## 📊 COMPARACIÓN: ANTES vs DESPUÉS

### ANTES (Actual)

```
Producción:
  DB: paqueteria_v4
  Contenedor: paqueteria_v1_prod_app
  Puerto: 8000
  ↓
  ↓ MISMA BASE DE DATOS ⚠️
  ↓
Staging:
  DB: paqueteria_v4 (MISMA)
  Contenedor: paqueteria_staging_app
  Puerto: 8001
```

**Problemas:**
- ❌ Riesgo de corrupción de datos
- ❌ No se pueden probar cambios destructivos
- ❌ Migraciones afectan ambos ambientes

### DESPUÉS (Propuesto)

```
Producción:
  DB: paqueteria_v4
  Contenedor: paqueteria_v1_prod_app
  Puerto: 8000
  Datos: REALES
  ↓
  ↓ Sincronización Diaria (Solo lectura)
  ↓
Staging:
  DB: paqueteria_staging (SEPARADA)
  Contenedor: paqueteria_staging_app
  Puerto: 8001
  Datos: COPIA + Nuevas tablas
```

**Beneficios:**
- ✅ Ambientes completamente separados
- ✅ Pruebas seguras en staging
- ✅ Migraciones independientes
- ✅ Datos reales para pruebas realistas

---

## 🔧 ARCHIVOS A MODIFICAR

### 1. Crear Nuevos Archivos

```bash
# Variables de entorno
.env.production          # Renombrar .env actual
.env.staging             # Crear nuevo

# Scripts de sincronización
scripts/database/sync_prod_to_staging_initial.sh    # ✅ Ya creado
scripts/database/sync_prod_to_staging_daily.sh      # ✅ Ya creado
scripts/database/verify_db_sync.py                  # Crear
```

### 2. Modificar Archivos Existentes

```bash
# Docker Compose
docker-compose.prod.yml      # Cambiar env_file a .env.production
docker-compose.staging.yml   # Cambiar env_file a .env.staging

# Scripts de deployment
deploy.sh                    # Especificar ambiente
scripts/deploy/*.sh          # Agregar validación de ambiente
```

### 3. Actualizar Documentación

```bash
README.md                    # Agregar sección de ambientes
CODE/README.md               # Actualizar instrucciones
DOCS/deployment/*.md         # Actualizar guías de deployment
```

---

## 📝 CHECKLIST DE IMPLEMENTACIÓN

### Preparación
- [ ] Backup completo de `paqueteria_v4`
- [ ] Crear base de datos `paqueteria_staging`
- [ ] Configurar credenciales de staging
- [ ] Probar conectividad a ambas bases de datos

### Configuración
- [ ] Crear `.env.production` (renombrar `.env`)
- [ ] Crear `.env.staging`
- [ ] Actualizar `docker-compose.prod.yml`
- [ ] Actualizar `docker-compose.staging.yml`
- [ ] Configurar scripts de sincronización

### Migración
- [ ] Ejecutar sincronización inicial
- [ ] Aplicar migraciones de staging
- [ ] Verificar datos en staging
- [ ] Probar aplicación en staging

### Automatización
- [ ] Configurar cron job de sincronización
- [ ] Configurar alertas de sincronización
- [ ] Documentar proceso

### Validación
- [ ] Probar deployment en staging
- [ ] Verificar que producción no se afecta
- [ ] Probar merge de staging a main
- [ ] Validar proceso de migraciones

---

## ⏱️ TIMELINE ESTIMADO

```
Día 1: Preparación y Backup
  - Backup de producción
  - Crear base de datos staging
  - Configurar credenciales

Día 2: Configuración
  - Crear archivos .env
  - Actualizar docker-compose
  - Configurar scripts

Día 3: Migración Inicial
  - Sincronización inicial
  - Aplicar migraciones
  - Pruebas básicas

Día 4: Automatización
  - Configurar cron jobs
  - Configurar alertas
  - Documentación

Día 5: Validación
  - Pruebas completas
  - Ajustes finales
  - Go-live
```

---

## 💰 COSTOS ESTIMADOS

### Opción A: Nueva Instancia RDS
```
Staging (db.t3.micro):
- Instancia: ~$15/mes
- Almacenamiento (20GB): ~$2.30/mes
- Backup: ~$1/mes
Total: ~$18/mes adicionales
```

### Opción B: Misma Instancia, Nueva Base de Datos
```
Almacenamiento adicional (20GB): ~$2.30/mes
Total: ~$2.30/mes adicionales
```

**Recomendación:** Opción B (misma instancia, nueva base de datos)

---

## 🎯 RECOMENDACIÓN FINAL

### Estrategia Recomendada:

1. **Crear `paqueteria_staging` en la misma instancia RDS**
   - Más económico
   - Misma región y configuración
   - Fácil de gestionar

2. **Sincronización diaria automática**
   - Mantiene datos actualizados
   - No afecta performance de producción
   - Permite pruebas realistas

3. **Migraciones independientes**
   - Staging puede tener tablas adicionales
   - Producción solo recibe migraciones aprobadas
   - Control total del proceso

4. **Flujo de trabajo claro**
   - Desarrollo → Staging → Pruebas → Main → Producción
   - Cada ambiente con su propósito
   - Sin riesgos de corrupción

---

## 📚 PRÓXIMOS PASOS

1. ✅ **Revisar y aprobar este análisis**
2. ⏳ **Crear base de datos staging**
3. ⏳ **Configurar variables de entorno**
4. ⏳ **Ejecutar sincronización inicial**
5. ⏳ **Configurar automatización**
6. ⏳ **Validar y documentar**

---

**Generado:** 27 de enero de 2026  
**Rama Actual:** mainv2.1  
**Estado:** Análisis completado - Pendiente implementación
