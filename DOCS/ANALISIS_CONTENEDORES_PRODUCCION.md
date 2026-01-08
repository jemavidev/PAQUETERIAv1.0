# 🔍 ANÁLISIS DE CONTENEDORES EN PRODUCCIÓN

**Fecha:** 2024-12-12  
**Servidor:** paquetex.papyrus.com.co (914MB RAM)

---

## 📊 CONTENEDORES ACTUALES (9 total)

| # | Contenedor | RAM | CPU | Estado | Necesario |
|---|------------|-----|-----|--------|-----------|
| 1 | **paqueteria_v1_prod_app** | 99.75MB | 0.27% | ✅ Healthy | ✅ **CRÍTICO** |
| 2 | **paqueteria_v1_prod_redis** | 10.59MB | 0.50% | ✅ Healthy | ✅ **CRÍTICO** |
| 3 | **paqueteria_v1_prod_celery** | 9.22MB | 0.15% | ✅ Healthy | ✅ **NECESARIO** |
| 4 | **paqueteria_v1_prod_celery_beat** | 8.26MB | 0.00% | ✅ Up | ✅ **NECESARIO** |
| 5 | **paqueteria_v1_prod_grafana** | 93.34MB | 0.35% | ✅ Healthy | ⚠️ **OPCIONAL** |
| 6 | **paqueteria_v1_prod_prometheus** | 41.74MB | 0.07% | ✅ Healthy | ⚠️ **OPCIONAL** |
| 7 | **paqueteria_v1_prod_node_exporter** | 15.34MB | 0.00% | ✅ Healthy | ⚠️ **OPCIONAL** |
| 8 | **paqueteria_staging_app** | 12.07MB | 0.12% | ✅ Healthy | ⚠️ **STAGING** |
| 9 | **paqueteria_staging_redis** | 1.44MB | 0.49% | ✅ Healthy | ⚠️ **STAGING** |

**Total RAM usado:** 291.75MB (32% del total)

---

## 🎯 ANÁLISIS DETALLADO

### ✅ CONTENEDORES CRÍTICOS (127.56MB)

#### 1. paqueteria_v1_prod_app (99.75MB)
- **Función:** Aplicación principal FastAPI
- **Puerto:** 8000 (producción)
- **Estado:** Healthy, funcionando correctamente
- **Necesario:** ✅ **SÍ - CRÍTICO**
- **Acción:** MANTENER

#### 2. paqueteria_v1_prod_redis (10.59MB)
- **Función:** Cache y broker para Celery
- **Puerto:** 6379
- **Estado:** Healthy
- **Necesario:** ✅ **SÍ - CRÍTICO**
- **Acción:** MANTENER

#### 3. paqueteria_v1_prod_celery (9.22MB)
- **Función:** Worker para tareas asíncronas
- **Tareas activas:**
  - Envío de SMS masivos
  - Envío de emails
  - Generación de reportes
  - Procesamiento de archivos
  - Limpieza de archivos temporales
- **Necesario:** ✅ **SÍ - NECESARIO**
- **Acción:** MANTENER

#### 4. paqueteria_v1_prod_celery_beat (8.26MB)
- **Función:** Scheduler para tareas programadas
- **Tareas programadas:**
  - `update-dashboard-metrics` (cada 5 min)
  - `cleanup-temp-files` (diario)
  - `cleanup-old-reports` (diario)
- **Necesario:** ✅ **SÍ - NECESARIO**
- **Acción:** MANTENER

---

### ⚠️ CONTENEDORES OPCIONALES - MONITORING (150.42MB)

#### 5. paqueteria_v1_prod_grafana (93.34MB) ⚠️
- **Función:** Dashboard de monitoreo visual
- **Puerto:** 3000 (solo localhost)
- **Uso:** Visualización de métricas
- **Estado:** Funcionando, 701MB de datos
- **Necesario:** ⚠️ **OPCIONAL**
- **Impacto si se detiene:** Sin impacto en aplicación
- **Recomendación:** 
  - **DETENER temporalmente** para liberar RAM
  - Iniciar solo cuando se necesite monitorear
  - Ahorro: **~93MB RAM**

#### 6. paqueteria_v1_prod_prometheus (41.74MB) ⚠️
- **Función:** Recolección de métricas
- **Puerto:** 9090 (solo localhost)
- **Uso:** Almacena métricas de la aplicación
- **Estado:** Funcionando, 701MB de datos en disco
- **Necesario:** ⚠️ **OPCIONAL**
- **Impacto si se detiene:** Sin impacto en aplicación
- **Recomendación:**
  - **DETENER temporalmente** para liberar RAM
  - Iniciar solo cuando se necesite monitorear
  - Ahorro: **~42MB RAM**

#### 7. paqueteria_v1_prod_node_exporter (15.34MB) ⚠️
- **Función:** Exporta métricas del sistema
- **Puerto:** 9100 (solo localhost)
- **Uso:** Métricas de CPU, RAM, disco para Prometheus
- **Necesario:** ⚠️ **OPCIONAL** (solo si Prometheus está activo)
- **Recomendación:**
  - **DETENER temporalmente** con Prometheus
  - Ahorro: **~15MB RAM**

**Total ahorro monitoring:** **~150MB RAM**

---

### ⚠️ CONTENEDORES DE STAGING (13.51MB)

#### 8. paqueteria_staging_app (12.07MB)
- **Función:** Aplicación de staging para pruebas
- **Puerto:** 8001
- **Estado:** Funcionando en mismo servidor que producción
- **Necesario:** ⚠️ **DEPENDE**
- **Recomendación:**
  - Si staging tiene su propio servidor: **MOVER**
  - Si se usa frecuentemente: **MANTENER**
  - Si no se usa: **DETENER**
  - Ahorro potencial: **~12MB RAM**

#### 9. paqueteria_staging_redis (1.44MB)
- **Función:** Redis para staging
- **Puerto:** 6380
- **Necesario:** ⚠️ **SOLO SI STAGING ESTÁ ACTIVO**
- **Recomendación:** Igual que staging_app
- **Ahorro potencial: **~1.5MB RAM**

**Total ahorro staging:** **~13.5MB RAM**

---

## 💡 RECOMENDACIONES

### 🔴 ACCIÓN INMEDIATA - Liberar RAM (163.5MB)

#### Opción 1: Detener Monitoring Temporalmente (RECOMENDADO)
```bash
# Detener stack de monitoring
ssh papyrus "docker stop paqueteria_v1_prod_grafana paqueteria_v1_prod_prometheus paqueteria_v1_prod_node_exporter"

# Ahorro: ~150MB RAM
# Impacto: NINGUNO en aplicación
# Reversible: Sí, con docker start
```

**Beneficios:**
- ✅ Libera 150MB RAM inmediatamente
- ✅ Reduce SWAP significativamente
- ✅ Sin impacto en aplicación
- ✅ Fácilmente reversible

**Cuándo iniciar monitoring:**
- Solo cuando necesites ver métricas
- Para debugging de problemas
- Para análisis de rendimiento

#### Opción 2: Mover Staging a Otro Servidor
```bash
# Si staging tiene su propio servidor (staging.jemavi.co)
# Detener staging en producción
ssh papyrus "docker stop paqueteria_staging_app paqueteria_staging_redis"

# Ahorro: ~13.5MB RAM
# Impacto: Staging no disponible en este servidor
```

---

### 🟢 CONFIGURACIÓN ÓPTIMA RECOMENDADA

#### Producción (Contenedores Esenciales)
```
✅ paqueteria_v1_prod_app         (99.75MB)
✅ paqueteria_v1_prod_redis        (10.59MB)
✅ paqueteria_v1_prod_celery       (9.22MB)
✅ paqueteria_v1_prod_celery_beat  (8.26MB)
-------------------------------------------
Total RAM esencial: 127.82MB (14% del total)
```

#### Monitoring (Iniciar solo cuando se necesite)
```
⏸️  paqueteria_v1_prod_grafana       (93.34MB) - DETENIDO
⏸️  paqueteria_v1_prod_prometheus    (41.74MB) - DETENIDO
⏸️  paqueteria_v1_prod_node_exporter (15.34MB) - DETENIDO
```

#### Staging (Mover a servidor dedicado)
```
⏸️  paqueteria_staging_app    (12.07MB) - MOVER
⏸️  paqueteria_staging_redis  (1.44MB)  - MOVER
```

---

## 📊 IMPACTO ESPERADO

### Escenario Actual
```
RAM Total:      914MB
RAM Usada:      670MB (73%)
SWAP Usado:     988MB (49%)
Contenedores:   9
RAM Apps:       291.75MB
```

### Escenario Optimizado (Solo detener monitoring)
```
RAM Total:      914MB
RAM Usada:      ~520MB (57%)  ⬇️ -150MB
SWAP Usado:     ~800MB (40%)  ⬇️ -188MB
Contenedores:   6 (3 detenidos)
RAM Apps:       141.33MB
```

### Escenario Óptimo (Detener monitoring + mover staging)
```
RAM Total:      914MB
RAM Usada:      ~507MB (55%)  ⬇️ -163MB
SWAP Usado:     ~780MB (39%)  ⬇️ -208MB
Contenedores:   4 (5 detenidos/movidos)
RAM Apps:       127.82MB
```

---

## 🚀 PLAN DE ACCIÓN RECOMENDADO

### Fase 1: INMEDIATA (Antes de deploy de optimizaciones)
```bash
# 1. Detener monitoring (libera 150MB)
ssh papyrus << 'EOF'
docker stop paqueteria_v1_prod_grafana
docker stop paqueteria_v1_prod_prometheus
docker stop paqueteria_v1_prod_node_exporter
echo "✅ Monitoring detenido - 150MB liberados"
free -h | grep -E "Mem:|Swap:"
EOF
```

### Fase 2: Deploy de Optimizaciones
```bash
# Con 150MB más de RAM libre, el deploy será más seguro
./deploy.sh --env papyrus --deploy
```

### Fase 3: OPCIONAL (Si staging no se usa en producción)
```bash
# Verificar si staging.jemavi.co es un servidor diferente
# Si sí, detener staging en producción
ssh papyrus << 'EOF'
docker stop paqueteria_staging_app
docker stop paqueteria_staging_redis
echo "✅ Staging detenido - 13.5MB adicionales liberados"
EOF
```

### Fase 4: Iniciar Monitoring Solo Cuando Se Necesite
```bash
# Cuando necesites ver métricas
ssh papyrus << 'EOF'
docker start paqueteria_v1_prod_node_exporter
docker start paqueteria_v1_prod_prometheus
docker start paqueteria_v1_prod_grafana
echo "✅ Monitoring iniciado"
EOF

# Acceder a Grafana
# http://paquetex.papyrus.com.co:3000 (si está expuesto)
# O crear túnel SSH: ssh -L 3000:localhost:3000 papyrus
```

---

## ⚠️ CONTENEDORES QUE NO SE DEBEN DETENER

### ❌ NO DETENER ESTOS:
1. **paqueteria_v1_prod_app** - Aplicación principal
2. **paqueteria_v1_prod_redis** - Cache y broker
3. **paqueteria_v1_prod_celery** - Tareas asíncronas (SMS, emails, reportes)
4. **paqueteria_v1_prod_celery_beat** - Tareas programadas (limpieza, métricas)

**Razón:** Son esenciales para el funcionamiento de la aplicación

---

## 📋 COMANDOS ÚTILES

### Ver estado actual
```bash
ssh papyrus "docker ps --format 'table {{.Names}}\t{{.Status}}' && echo '---' && free -h"
```

### Detener monitoring
```bash
ssh papyrus "docker stop paqueteria_v1_prod_grafana paqueteria_v1_prod_prometheus paqueteria_v1_prod_node_exporter"
```

### Iniciar monitoring
```bash
ssh papyrus "docker start paqueteria_v1_prod_node_exporter paqueteria_v1_prod_prometheus paqueteria_v1_prod_grafana"
```

### Ver logs de Celery (verificar que funciona)
```bash
ssh papyrus "docker logs --tail 50 paqueteria_v1_prod_celery"
ssh papyrus "docker logs --tail 50 paqueteria_v1_prod_celery_beat"
```

---

## ✅ RESUMEN EJECUTIVO

### Contenedores Necesarios (4)
- ✅ App principal
- ✅ Redis
- ✅ Celery worker
- ✅ Celery beat

### Contenedores Opcionales (3)
- ⏸️ Grafana (93MB) - Detener
- ⏸️ Prometheus (42MB) - Detener
- ⏸️ Node Exporter (15MB) - Detener

### Contenedores Staging (2)
- ⏸️ Staging app (12MB) - Evaluar mover
- ⏸️ Staging redis (1.5MB) - Evaluar mover

### Ahorro Total Posible
- **Inmediato:** 150MB (detener monitoring)
- **Adicional:** 13.5MB (mover staging)
- **Total:** 163.5MB (18% de RAM)

---

**Recomendación Final:** 
1. ✅ Detener monitoring AHORA (150MB libres)
2. ✅ Deploy de optimizaciones
3. ⏸️ Evaluar mover staging según uso

---

**Última actualización:** 2024-12-12  
**Estado:** ✅ ANÁLISIS COMPLETADO
