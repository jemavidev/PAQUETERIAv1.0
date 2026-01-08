# 🚀 Deploy de Optimizaciones de Cache a Staging

**Fecha:** 2024-12-18  
**Servidor:** staging.jemavi.co  
**SSH:** `ssh staging`  
**Rama:** staging

---

## ✅ CAMBIOS IMPLEMENTADOS

- ✅ Cache implementado en `PackageService` (6 métodos)
- ✅ Cache implementado en `CustomerService` (3 métodos)
- ✅ Eager loading agregado para evitar N+1 queries
- ✅ Invalidación automática de cache
- ✅ Logging de cache hits/misses

**Commits:**
- `5e90e04` - feat: implementar cache en servicios principales
- `54b30b2` - test: agregar scripts de verificación de cache

---

## 🚀 DEPLOY AUTOMÁTICO

```bash
# Ejecutar script de deploy automático
./deploy_cache_to_staging.sh
```

El script hace:
1. ✅ Verifica rama staging
2. ✅ Pull en servidor staging
3. ✅ Rebuild de contenedores
4. ✅ Restart de servicios
5. ✅ Verifica Redis
6. ✅ Verifica logs
7. ✅ Test de rendimiento

---

## 🔧 DEPLOY MANUAL

Si prefieres hacerlo paso a paso:

### 1. Conectar a staging
```bash
ssh staging
cd /home/ubuntu/paqueteria-staging
```

### 2. Pull de cambios
```bash
git pull origin staging
```

### 3. Rebuild y restart
```bash
docker compose -f docker-compose.staging.yml build app
docker compose -f docker-compose.staging.yml up -d
```

### 4. Verificar
```bash
# Health check
curl https://staging.jemavi.co/health

# Verificar Redis
docker exec paqueteria_staging_app python -c '
from app.cache_manager import cache_manager
print("Redis Status:", cache_manager.redis_client.ping())
'

# Ver logs
docker logs --tail 50 paqueteria_staging_app | grep -E "Cache|ERROR"
```

---

## 🧪 VERIFICACIÓN

### Opción 1: Script automático
```bash
./test_cache.sh https://staging.jemavi.co
```

### Opción 2: Manual
```bash
# Test 1: Primera llamada (cache miss)
curl -w "\nTiempo: %{time_total}s\n" https://staging.jemavi.co/api/packages?limit=10

# Test 2: Segunda llamada (cache hit) - debe ser mucho más rápido
curl -w "\nTiempo: %{time_total}s\n" https://staging.jemavi.co/api/packages?limit=10
```

**Resultado esperado:**
- Primera llamada: ~200-300ms (cache miss)
- Segunda llamada: ~10-20ms (cache hit)
- Mejora: >80%

### Verificar estadísticas de cache
```bash
ssh staging "docker exec paqueteria_staging_app python -c '
from app.cache_manager import cache_manager
import json
print(json.dumps(cache_manager.get_cache_stats(), indent=2))
'"
```

**Métricas esperadas:**
- `hit_rate`: >80%
- `used_memory`: <100MB
- `total_keys`: >0

---

## 📊 MONITOREO

### Logs en tiempo real
```bash
ssh staging "docker logs -f paqueteria_staging_app | grep Cache"
```

**Logs esperados:**
```
DEBUG - Cache MISS: search_packages con filtros {...}
DEBUG - Cache HIT: search_packages con filtros {...}
DEBUG - Cache invalidado para customer_id=123
```

### Verificar memoria
```bash
ssh staging "free -h"
ssh staging "docker stats --no-stream paqueteria_staging_app"
```

### Verificar Redis
```bash
ssh staging "docker exec paqueteria_staging_redis redis-cli INFO memory"
```

---

## ⚠️ TROUBLESHOOTING

### Problema: Cache no funciona

**Síntoma:** No hay mejora en tiempos de respuesta

**Solución:**
```bash
# 1. Verificar que Redis está corriendo
ssh staging "docker ps | grep redis"

# 2. Verificar conexión a Redis
ssh staging "docker exec paqueteria_staging_app python -c '
from app.cache_manager import cache_manager
print(cache_manager.redis_client.ping())
'"

# 3. Verificar logs de error
ssh staging "docker logs paqueteria_staging_app | grep -i redis"

# 4. Restart de Redis si es necesario
ssh staging "docker compose -f docker-compose.staging.yml restart redis"
```

### Problema: Errores en logs

**Síntoma:** Errores relacionados con cache

**Solución:**
```bash
# Ver errores completos
ssh staging "docker logs --tail 100 paqueteria_staging_app | grep -A 5 ERROR"

# Si hay errores de import
ssh staging "docker compose -f docker-compose.staging.yml restart app"
```

### Problema: Datos desactualizados

**Síntoma:** Cache muestra datos viejos

**Solución:**
```bash
# Limpiar cache manualmente
ssh staging "docker exec paqueteria_staging_app python -c '
from app.cache_manager import cache_manager
cleared = cache_manager.clear_pattern(\"paqueteria:cache:*\")
print(f\"Cleared {cleared} keys\")
'"
```

---

## 📈 MÉTRICAS A MONITOREAR

### Primeras 24 horas (revisar cada hora)

| Métrica | Objetivo | Comando |
|---------|----------|---------|
| **Cache hit rate** | >80% | Ver estadísticas de cache |
| **Tiempo de respuesta** | <50ms (cache hit) | `curl -w "%{time_total}"` |
| **Uso de Redis** | <100MB | `docker stats` |
| **Errores** | 0 | `docker logs \| grep ERROR` |

### Después de 24 horas

| Métrica | Objetivo | Comando |
|---------|----------|---------|
| **Queries a BD** | -90% | Logs de PostgreSQL |
| **Uso de CPU** | -50% | `docker stats` |
| **Uso de RAM** | -30% | `free -h` |

---

## ✅ CRITERIOS DE ÉXITO

Para considerar el deploy exitoso:

- ✅ Cache hit rate >80%
- ✅ Tiempo de respuesta <50ms (cache hit)
- ✅ Sin errores en logs
- ✅ Redis usando <100MB
- ✅ Aplicación estable por 24 horas

Si se cumplen todos los criterios → **Deploy a producción**

---

## 🔄 ROLLBACK

Si algo sale mal:

```bash
# 1. Conectar a staging
ssh staging
cd /home/ubuntu/paqueteria-staging

# 2. Volver a commit anterior
git checkout 7f2cf09  # Commit antes de las optimizaciones

# 3. Rebuild y restart
docker compose -f docker-compose.staging.yml build app
docker compose -f docker-compose.staging.yml up -d

# 4. Verificar
curl https://staging.jemavi.co/health
```

---

## 📞 CONTACTO

Si tienes problemas:
1. Revisar logs: `docker logs paqueteria_staging_app`
2. Verificar Redis: `docker ps | grep redis`
3. Consultar documentación: `OPTIMIZACION_CACHE_IMPLEMENTADA.md`

---

**Última actualización:** 2024-12-18  
**Versión:** 1.0.0  
**Estado:** ✅ LISTO PARA DEPLOY
