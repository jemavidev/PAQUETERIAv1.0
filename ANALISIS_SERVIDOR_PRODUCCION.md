# 📊 ANÁLISIS SERVIDOR DE PRODUCCIÓN (PAPYRUS)

**Fecha:** 2024-12-12  
**Servidor:** paquetex.papyrus.com.co

---

## 🖥️ ESPECIFICACIONES DEL SERVIDOR

### Hardware
- **RAM Total:** 914MB (2.2x más que staging)
- **RAM Usada:** 670MB (73%)
- **RAM Libre:** 77MB
- **SWAP Total:** 2GB
- **SWAP Usado:** 988MB (49%) ⚠️
- **CPU:** 2 cores
- **Disco:** 38GB (76% usado)
- **Uptime:** 5 días, 23 horas

### Estado Actual
- **Load Average:** 0.16, 0.11, 0.03 (excelente)
- **Tiempo de respuesta:** 0.0046s (muy rápido)
- **Contenedores activos:** 9 (prod + staging + monitoring)

---

## 📦 CONTENEDORES EN EJECUCIÓN

### Producción
1. **paqueteria_v1_prod_app** - 93.52MB RAM (10.23%)
2. **paqueteria_v1_prod_celery** - 9.25MB RAM (1.01%)
3. **paqueteria_v1_prod_celery_beat** - 8.55MB RAM (0.94%)
4. **paqueteria_v1_prod_redis** - 4.43MB RAM (0.48%)
5. **paqueteria_v1_prod_grafana** - 85.75MB RAM (9.38%)
6. **paqueteria_v1_prod_prometheus** - 33.06MB RAM (3.62%)
7. **paqueteria_v1_prod_node_exporter** - 14.2MB RAM (1.55%)

### Staging (en mismo servidor)
8. **paqueteria_staging_app** - 24.97MB RAM (2.73%)
9. **paqueteria_staging_redis** - 1.22MB RAM (0.13%)

**Total RAM contenedores:** ~275MB (30% del total)

---

## ⚙️ CONFIGURACIÓN ACTUAL

### Uvicorn
- **Workers:** 2 (correcto para 2 cores)
- **Comando:** `python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 2 --access-log --log-level info`
- **Procesos Python:** 5 (1 master + 2 workers + 2 resource trackers)

### Base de Datos
- **Pool size:** 20 conexiones
- **Max overflow:** 10 conexiones
- **Total máximo:** 30 conexiones
- **Conexiones activas:** 0 (idle actualmente)
- **Environment:** production ✅

### Docker
- **Memory limit:** Sin límite (0)
- **Network:** Bridge
- **Restart policy:** unless-stopped

---

## 🔍 ANÁLISIS DE PROBLEMAS

### ⚠️ PROBLEMA 1: USO DE SWAP (CRÍTICO)
**Estado:** 988MB de SWAP en uso (49% del total)

**Causa:**
- Servidor con solo 914MB RAM
- 9 contenedores corriendo simultáneamente
- Monitoring stack (Grafana + Prometheus) consume ~119MB
- Sin límites de memoria en contenedores

**Impacto:**
- Lentitud general del sistema
- Disco es 1000x más lento que RAM
- Afecta a TODOS los contenedores

### ⚠️ PROBLEMA 2: POOL DE CONEXIONES EXCESIVO
**Estado:** 30 conexiones máximas configuradas

**Causa:**
- Configuración heredada de servidor con más recursos
- 2 workers × 30 conexiones = 60 conexiones potenciales
- Cada conexión consume ~5-10MB RAM

**Impacto:**
- Presión innecesaria en memoria
- Contribuye al uso de SWAP

### ✅ PROBLEMA 3: WORKERS (CORRECTO)
**Estado:** 2 workers activos

**Análisis:**
- Correcto para 2 cores CPU
- No necesita cambios inmediatos
- Nuestra optimización lo aumentaría a 4 (puede ser excesivo)

---

## 🎯 IMPACTO DE LAS OPTIMIZACIONES

### Optimización 1: Pool de Conexiones
```
Antes:  pool_size=20, max_overflow=10 (30 total)
Después: pool_size=15, max_overflow=8 (23 total)
Ahorro: ~35-70MB RAM
```

### Optimización 2: Workers
```
Antes:  2 workers
Después: 4 workers (según nuestra config)
Impacto: +50-100MB RAM ⚠️
```

### Optimización 3: Memoria PostgreSQL
```
Antes:  work_mem=32MB, cache=1GB
Después: work_mem=32MB, cache=1GB (sin cambio en prod)
Impacto: 0MB
```

### Optimización 4: Índices
```
Impacto: Mejora velocidad de queries
Sin impacto en RAM
```

---

## ⚠️ RECOMENDACIONES CRÍTICAS

### 🔴 AJUSTE NECESARIO: Workers en Producción

**Problema:** Nuestra configuración aumentaría workers de 2 a 4, lo cual:
- Aumentaría consumo de RAM en ~50-100MB
- Empeoraría el uso de SWAP
- No es óptimo para servidor con 914MB RAM

**Solución:** Ajustar la configuración para producción

```python
# uvicorn_config.py - AJUSTE NECESARIO
WORKERS = 2 if IS_STAGING else 3  # Cambiar de 4 a 3
```

**Justificación:**
- 3 workers es un buen balance para 2 cores
- Ahorra ~25-50MB RAM vs 4 workers
- Mantiene buen throughput

### 🟡 RECOMENDACIÓN: Límites de Memoria en Docker

Agregar límites a contenedores no críticos:

```yaml
# docker-compose.prod.yml
grafana:
  mem_limit: 128m
  mem_reservation: 64m

prometheus:
  mem_limit: 64m
  mem_reservation: 32m
```

### 🟢 OPTIMIZACIÓN: Pool de Conexiones

La reducción de 30 → 23 conexiones es beneficiosa:
- Ahorra 35-70MB RAM
- Suficiente para 3 workers
- Reduce presión de SWAP

---

## ✅ CONCLUSIÓN Y PLAN DE ACCIÓN

### Estado Actual
- ✅ Producción funciona bien (0.0046s respuesta)
- ⚠️ Usando SWAP (988MB) - causa lentitud potencial
- ✅ Workers correctos (2)
- ⚠️ Pool conexiones excesivo (30)

### Optimizaciones Seguras para Aplicar
1. ✅ **Pool de conexiones:** 30 → 23 (SEGURO)
2. ⚠️ **Workers:** 2 → 3 (AJUSTAR, no 4)
3. ✅ **Índices BD:** Crear (SEGURO, mejora performance)
4. ✅ **Memoria PostgreSQL:** Sin cambio en prod (SEGURO)

### Optimizaciones que NO Aplicar
1. ❌ **Workers a 4:** Consumiría demasiada RAM
2. ❌ **Reducir pool a 8:** Muy poco para producción

### Ajuste Requerido en Código

**ANTES de hacer commit, cambiar:**

```python
# CODE/uvicorn_config.py - LÍNEA 13
# Cambiar esto:
WORKERS = 2 if IS_STAGING else 4

# Por esto:
WORKERS = 2 if IS_STAGING else 3
```

---

## 📈 RESULTADOS ESPERADOS POST-OPTIMIZACIÓN

### Producción
- **Uso RAM:** -35-70MB (por pool reducido)
- **Uso SWAP:** Reducción moderada (~50-100MB)
- **Queries:** -50-80% tiempo (por índices)
- **Workers:** 2 → 3 (+50% throughput con +25MB RAM)
- **Tiempo respuesta:** Mantener <0.01s

### Staging
- **Uso RAM:** -150-200MB (pool + config PostgreSQL)
- **Uso SWAP:** -180MB (reducción 65%)
- **Queries:** -50-80% tiempo (por índices)
- **Workers:** 1 → 2 (+100% throughput)
- **Tiempo respuesta:** Mejora significativa

---

## 🚦 SEMÁFORO DE RIESGO

| Optimización | Staging | Producción | Riesgo |
|--------------|---------|------------|--------|
| Pool conexiones | 🟢 Seguro | 🟢 Seguro | Bajo |
| Workers 2→3 | 🟢 Seguro | 🟡 Moderado | Medio |
| Workers 2→4 | 🟢 Seguro | 🔴 Riesgoso | Alto |
| Índices BD | 🟢 Seguro | 🟢 Seguro | Bajo |
| Config PostgreSQL | 🟢 Seguro | 🟢 Seguro | Bajo |

---

## ✅ APROBACIÓN PARA CONTINUAR

**Recomendación:** PROCEDER con ajuste de workers a 3 (no 4)

**Pasos:**
1. Ajustar `uvicorn_config.py` (workers: 4 → 3)
2. Commit y push
3. Deploy a staging primero
4. Verificar staging 24h
5. Deploy a producción

**Tiempo estimado:** 30 minutos

---

**Última actualización:** 2024-12-12  
**Analista:** Sistema de Diagnóstico Automático  
**Estado:** ✅ LISTO PARA OPTIMIZAR (con ajuste)
