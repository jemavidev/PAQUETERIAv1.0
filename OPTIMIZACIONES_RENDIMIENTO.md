# 🚀 OPTIMIZACIONES DE RENDIMIENTO - PAQUETEX EL CLUB

**Fecha:** 2024-12-12  
**Objetivo:** Mejorar rendimiento de operaciones CRUD en staging y producción

---

## 📊 DIAGNÓSTICO REALIZADO

### Servidor Staging
- **RAM:** 416MB (usando 283MB de SWAP ⚠️)
- **CPU:** 2 cores, carga baja (0.05)
- **Base de datos:** AWS RDS us-east-1
- **Problema principal:** Memoria insuficiente causando uso de SWAP

### Métricas Antes de Optimización
- **Import time:** 1.369s (muy lento)
- **Query simple:** 0.078s (aceptable)
- **Workers:** 1 (subóptimo)
- **Pool conexiones:** 20+10 (excesivo para staging)

---

## ✅ OPTIMIZACIONES IMPLEMENTADAS

### 1. **Pool de Conexiones Adaptativo** (`database_optimized.py`)

**Cambio:** Configuración dinámica según entorno

```python
# STAGING (recursos limitados)
- pool_size: 20 → 5
- max_overflow: 10 → 3
- pool_timeout: 30s → 20s
- Total conexiones: 30 → 8

# PRODUCCIÓN (recursos normales)
- pool_size: 15
- max_overflow: 8
- pool_timeout: 30s
- Total conexiones: 23
```

**Impacto esperado:** Reducción de 70% en uso de memoria por conexiones DB

---

### 2. **Workers de Uvicorn Optimizados** (`uvicorn_config.py`)

**Cambio:** Workers adaptativos según entorno

```python
# STAGING
- Workers: 1 → 2
- Concurrency: 100

# PRODUCCIÓN
- Workers: 4
- Concurrency: 200
```

**Impacto esperado:** Mejor aprovechamiento de CPU, respuesta más rápida

---

### 3. **Configuración PostgreSQL Adaptativa** (`database_optimized.py`)

**Cambio:** Parámetros de memoria según entorno

```python
# STAGING
- work_mem: 32MB → 8MB
- maintenance_work_mem: 128MB → 32MB
- effective_cache_size: 1GB → 256MB

# PRODUCCIÓN
- work_mem: 32MB
- maintenance_work_mem: 128MB
- effective_cache_size: 1GB
```

**Impacto esperado:** Reducción de presión de memoria en staging

---

### 4. **Script de Creación de Índices** (`scripts/create_database_indexes.py`)

**Nuevos índices creados:**

#### Tabla `packages` (más crítica)
- `idx_packages_customer_id` - Búsquedas por cliente
- `idx_packages_status` - Filtros por estado
- `idx_packages_created_at` - Ordenamiento por fecha
- `idx_packages_tracking_number` - Búsqueda por tracking
- `idx_packages_guide_number` - Búsqueda por guía
- `idx_packages_status_created` - Compuesto para dashboard
- `idx_packages_customer_status` - Compuesto para filtros

#### Tabla `customers`
- `idx_customers_phone` - Búsqueda por teléfono
- `idx_customers_full_name` - Búsqueda por nombre
- `idx_customers_created_at` - Ordenamiento

#### Tabla `messages`
- `idx_messages_package_id` - Mensajes por paquete
- `idx_messages_customer_id` - Mensajes por cliente
- `idx_messages_status` - Filtros por estado
- `idx_messages_package_status` - Compuesto

#### Otras tablas
- Índices en `notifications`, `users`, `file_uploads`

**Impacto esperado:** Reducción de 50-80% en tiempo de queries complejas

---

### 5. **Docker Compose Optimizado**

**Cambio:** Uso de configuración dinámica en ambos entornos

```yaml
# Antes
command: python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 2

# Después
command: python -c 'from uvicorn_config import *; import uvicorn; uvicorn.run(...)'
```

**Beneficio:** Configuración centralizada y adaptativa

---

## 📋 INSTRUCCIONES DE DESPLIEGUE

### Paso 1: Commit y Push
```bash
git add .
git commit -m "feat: optimizaciones de rendimiento para staging y producción"
git push origin main
```

### Paso 2: Deploy a Staging
```bash
./deploy.sh --env staging --deploy
```

### Paso 3: Crear Índices en Base de Datos
```bash
# Conectar a staging
ssh staging

# Ir al directorio
cd /home/ubuntu/paqueteria-staging

# Ejecutar script de índices
docker exec paqueteria_staging_app python scripts/create_database_indexes.py --create

# Verificar índices creados
docker exec paqueteria_staging_app python scripts/create_database_indexes.py --check
```

### Paso 4: Verificar Mejoras
```bash
# Ver logs
docker logs -f paqueteria_staging_app | head -20

# Verificar configuración
docker exec paqueteria_staging_app python -c "
from uvicorn_config import *
print(f'Workers: {WORKERS}')
print(f'Concurrency: {LIMIT_CONCURRENCY}')
"

# Verificar pool de conexiones
docker exec paqueteria_staging_app python -c "
from app.database_optimized import get_db_pool_status
import json
print(json.dumps(get_db_pool_status(), indent=2))
"
```

### Paso 5: Monitorear Rendimiento
```bash
# Ver uso de memoria
ssh staging "free -h"

# Ver uso de SWAP (debe reducirse)
ssh staging "free -h | grep Swap"

# Ver stats de Docker
ssh staging "docker stats --no-stream"

# Probar tiempo de respuesta
curl -w "\nTiempo: %{time_total}s\n" http://staging.jemavi.co/health
```

---

## 📈 RESULTADOS ESPERADOS

### Mejoras en Staging
- ✅ **Uso de SWAP:** 283MB → <100MB (reducción 65%)
- ✅ **Tiempo de respuesta:** Reducción 30-50%
- ✅ **Queries complejas:** Reducción 50-80%
- ✅ **Concurrencia:** Mejor manejo de usuarios simultáneos

### Mejoras en Producción
- ✅ **Throughput:** Aumento 100% (2→4 workers)
- ✅ **Queries:** Reducción 50-80% con índices
- ✅ **Escalabilidad:** Mejor manejo de carga

---

## 🔍 MONITOREO POST-DESPLIEGUE

### Métricas a Vigilar

#### 1. Memoria
```bash
# Cada 5 minutos durante 1 hora
watch -n 300 'ssh staging "free -h"'
```

#### 2. Tiempo de Respuesta
```bash
# Probar endpoints críticos
curl -w "\nTiempo: %{time_total}s\n" http://staging.jemavi.co/api/packages
curl -w "\nTiempo: %{time_total}s\n" http://staging.jemavi.co/api/customers
```

#### 3. Logs de Aplicación
```bash
# Buscar errores o warnings
ssh staging "docker logs --tail 100 paqueteria_staging_app | grep -E 'ERROR|WARNING'"
```

#### 4. Pool de Conexiones
```bash
# Verificar que no se agoten las conexiones
ssh staging "docker exec paqueteria_staging_app python -c '
from app.database_optimized import get_db_pool_status
import json
print(json.dumps(get_db_pool_status(), indent=2))
'"
```

---

## ⚠️ ROLLBACK (Si es necesario)

Si algo sale mal, revertir cambios:

```bash
# 1. Volver a commit anterior
git revert HEAD
git push origin main

# 2. Deploy de versión anterior
./deploy.sh --env staging --rollback

# 3. Verificar que funciona
curl http://staging.jemavi.co/health
```

---

## 📝 NOTAS ADICIONALES

### Variables de Entorno Importantes

Asegurar que estén configuradas correctamente:

```bash
# Staging
ENVIRONMENT=staging

# Producción
ENVIRONMENT=production
```

### Índices en Base de Datos

Los índices se crean con `CONCURRENTLY` para no bloquear la tabla durante la creación. Esto es seguro en producción.

### Futuras Optimizaciones

Si el problema persiste después de estas optimizaciones:

1. **Upgrade de servidor:** Aumentar RAM a 1GB mínimo
2. **Cache Redis:** Implementar cache de queries frecuentes
3. **CDN:** Para archivos estáticos
4. **Query optimization:** Revisar queries N+1
5. **Lazy loading:** Optimizar imports de Python

---

## 📞 SOPORTE

Si encuentras problemas:

1. Revisar logs: `docker logs paqueteria_staging_app`
2. Verificar memoria: `free -h`
3. Verificar pool: Script de diagnóstico incluido
4. Contactar al equipo de desarrollo

---

**Última actualización:** 2024-12-12  
**Autor:** Sistema de Optimización Automática  
**Versión:** 1.0.0
