# 🛡️ Prevención de Bloqueos del Servidor

**Fecha de implementación:** 2026-01-14  
**Versión:** 1.0.0  
**Estado:** ✅ Implementado

---

## 📋 Problema Identificado

El servidor de staging se bloqueó mostrando error **504 Gateway Timeout**, causado por:
- Operaciones que tardaron más del timeout configurado
- Posibles consultas lentas a la base de datos
- Operaciones de S3 sin timeout
- Configuración de Nginx con timeouts muy cortos (20s)

---

## ✅ Mejoras Implementadas

### 1. Timeouts en Operaciones de S3 🔧

**Archivo:** `src/app/services/s3_storage_service.py`

**Cambios:**
```python
from botocore.config import Config

boto_config = Config(
    region_name=self.region,
    connect_timeout=5,   # Timeout de conexión: 5 segundos
    read_timeout=30,     # Timeout de lectura: 30 segundos
    retries={
        'max_attempts': 3,
        'mode': 'adaptive'  # Reintentos adaptativos
    }
)

self.s3_client = boto3.client('s3', config=boto_config, ...)
```

**Beneficios:**
- ✅ Operaciones de S3 no se quedan colgadas indefinidamente
- ✅ Reintentos automáticos en caso de fallo temporal
- ✅ Timeout total máximo: 5s conexión + 30s lectura = 35s

---

### 2. Middleware de Timeout para Requests ⏱️

**Archivo:** `src/app/middleware/timeout_middleware.py` (NUEVO)

**Funcionalidad:**
- Aplica timeout de **60 segundos** a todas las requests
- Excluye health checks del timeout
- Retorna error 504 si se excede el tiempo

**Código:**
```python
class TimeoutMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        try:
            response = await asyncio.wait_for(
                call_next(request),
                timeout=60  # 60 segundos
            )
            return response
        except asyncio.TimeoutError:
            return JSONResponse(
                status_code=504,
                content={
                    "error": "Request Timeout",
                    "message": "La operación excedió el tiempo límite de 60 segundos"
                }
            )
```

**Beneficios:**
- ✅ Ninguna request puede colgar el servidor indefinidamente
- ✅ Respuesta clara al usuario cuando hay timeout
- ✅ Logs detallados de requests que exceden el tiempo

---

### 3. Timeouts en Base de Datos 🗄️

**Archivo:** `src/app/database.py`

**Cambios:**
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,          # Tamaño del pool
    max_overflow=20,       # Conexiones adicionales
    pool_timeout=30,       # Timeout para obtener conexión
    connect_args={
        "options": "-c statement_timeout=30000"  # 30s para queries
    }
)
```

**Beneficios:**
- ✅ Queries lentas se cancelan automáticamente después de 30s
- ✅ Pool de conexiones optimizado
- ✅ Previene bloqueos por queries mal optimizadas

---

### 4. Timeouts de Nginx Aumentados 🌐

**Archivo:** `/etc/nginx/sites-available/staging` (servidor remoto)

**Cambios:**
```nginx
location / {
    proxy_connect_timeout 30s;  # Antes: 10s
    proxy_send_timeout 60s;     # Antes: 20s
    proxy_read_timeout 60s;     # Antes: 20s
}
```

**Beneficios:**
- ✅ Nginx espera más tiempo antes de retornar 504
- ✅ Permite operaciones más largas (uploads, procesamiento)
- ✅ Alineado con timeout de la aplicación (60s)

---

### 5. Configuración de Uvicorn Mejorada ⚙️

**Archivo:** `src/uvicorn_config.py`

**Cambios:**
```python
TIMEOUT_KEEP_ALIVE = 30
TIMEOUT_GRACEFUL_SHUTDOWN = 30
```

**Beneficios:**
- ✅ Shutdown graceful de workers
- ✅ Conexiones keep-alive optimizadas

---

## 📊 Arquitectura de Timeouts

```
┌─────────────────────────────────────────────────────────┐
│  CLIENTE                                                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  NGINX                                                   │
│  - proxy_connect_timeout: 30s                           │
│  - proxy_send_timeout: 60s                              │
│  - proxy_read_timeout: 60s                              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  TIMEOUT MIDDLEWARE                                      │
│  - Request timeout: 60s                                 │
│  - Cancela operaciones que excedan el tiempo            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  APLICACIÓN FASTAPI                                      │
│  - Procesa request normalmente                          │
└─────────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────┴─────────────────┐
        ↓                                    ↓
┌──────────────────┐              ┌──────────────────┐
│  BASE DE DATOS   │              │  AWS S3          │
│  - Query: 30s    │              │  - Connect: 5s   │
│  - Pool: 30s     │              │  - Read: 30s     │
└──────────────────┘              └──────────────────┘
```

---

## 🔍 Monitoreo y Logs

### Logs de Timeout

**Middleware de Timeout:**
```
⏱️ Request timeout después de 60s: GET /invoices
```

**Base de Datos:**
```
ERROR: canceling statement due to statement timeout
```

**S3:**
```
botocore.exceptions.ReadTimeoutError: Read timeout on endpoint URL
```

### Verificar Logs

```bash
# Logs de aplicación
ssh staging "docker logs --tail=100 paqueteria_staging_app | grep -i timeout"

# Logs de Nginx
ssh staging "sudo tail -100 /var/log/nginx/error.log | grep timeout"
```

---

## 🧪 Pruebas

### Test de Timeout de Request

```python
import asyncio
from fastapi import FastAPI, Request

@app.get("/test-timeout")
async def test_timeout():
    # Simular operación lenta
    await asyncio.sleep(70)  # Más de 60s
    return {"status": "ok"}
```

**Resultado esperado:** Error 504 después de 60 segundos

### Test de Timeout de Base de Datos

```sql
-- Query que tarda más de 30s
SELECT pg_sleep(35);
```

**Resultado esperado:** Query cancelada con error de timeout

---

## 📈 Mejoras de Rendimiento

| Componente | Antes | Ahora | Mejora |
|------------|-------|-------|--------|
| **S3 Operations** | Sin timeout | 35s max | ✅ Previene bloqueos |
| **Requests** | Sin límite | 60s max | ✅ Protege servidor |
| **DB Queries** | Sin límite | 30s max | ✅ Cancela queries lentas |
| **Nginx Timeout** | 20s | 60s | ✅ Más flexible |

---

## ⚠️ Consideraciones

### Operaciones Largas

Si tienes operaciones que legítimamente tardan más de 60s:

**Opción 1: Procesamiento Asíncrono**
```python
from fastapi import BackgroundTasks

@app.post("/process-large-file")
async def process_file(background_tasks: BackgroundTasks):
    background_tasks.add_task(long_running_task)
    return {"status": "processing", "message": "Se procesará en segundo plano"}
```

**Opción 2: Aumentar Timeout Específico**
```python
@app.get("/long-operation")
async def long_operation(request: Request):
    # Marcar para excluir del timeout
    request.state.skip_timeout = True
    # ... operación larga
```

### Queries Lentas

Si tienes queries que tardan más de 30s:

1. **Optimizar la query** (recomendado)
   - Agregar índices
   - Reducir joins
   - Limitar resultados

2. **Aumentar timeout temporalmente**
   ```python
   db.execute("SET statement_timeout = '60000'")  # 60s
   # ... query larga
   db.execute("RESET statement_timeout")
   ```

---

## 🚀 Despliegue

### Staging (Ya Aplicado) ✅

```bash
# 1. Actualizar código
git pull origin main

# 2. Reconstruir imagen
ssh staging "cd ~/paqueteria-staging && docker compose -f docker-compose.staging.yml build"

# 3. Reiniciar contenedor
ssh staging "cd ~/paqueteria-staging && docker compose -f docker-compose.staging.yml up -d"

# 4. Verificar
ssh staging "docker logs --tail=50 paqueteria_staging_app"
```

### Producción (Pendiente)

```bash
# 1. Actualizar timeouts de Nginx
ssh production << 'EOF'
sudo sed -i 's/proxy_connect_timeout 10s;/proxy_connect_timeout 30s;/g' /etc/nginx/sites-available/production
sudo sed -i 's/proxy_send_timeout 20s;/proxy_send_timeout 60s;/g' /etc/nginx/sites-available/production
sudo sed -i 's/proxy_read_timeout 20s;/proxy_read_timeout 60s;/g' /etc/nginx/sites-available/production
sudo nginx -t && sudo systemctl reload nginx
EOF

# 2. Desplegar código actualizado
./deploy.sh production
```

---

## 📋 Checklist de Verificación

### Post-Despliegue

- [x] Timeouts de S3 configurados
- [x] Middleware de timeout agregado
- [x] Timeouts de BD configurados
- [x] Timeouts de Nginx actualizados
- [x] Logs verificados
- [ ] Monitoreo de timeouts activo
- [ ] Alertas configuradas

### Monitoreo Continuo

- [ ] Revisar logs diariamente
- [ ] Identificar queries lentas
- [ ] Optimizar operaciones que se acerquen al timeout
- [ ] Ajustar timeouts si es necesario

---

## 🔧 Troubleshooting

### Problema: Muchos timeouts de requests

**Causa:** Operaciones legítimamente lentas  
**Solución:** Mover a procesamiento asíncrono

### Problema: Timeouts de BD frecuentes

**Causa:** Queries no optimizadas  
**Solución:** 
1. Identificar queries lentas: `SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC`
2. Agregar índices necesarios
3. Optimizar queries

### Problema: Timeouts de S3

**Causa:** Archivos muy grandes o conexión lenta  
**Solución:**
1. Usar multipart upload para archivos grandes
2. Aumentar timeout de lectura si es necesario
3. Implementar retry con backoff exponencial

---

## 📚 Referencias

- **Boto3 Config:** https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html
- **FastAPI Middleware:** https://fastapi.tiangolo.com/tutorial/middleware/
- **PostgreSQL Timeouts:** https://www.postgresql.org/docs/current/runtime-config-client.html
- **Nginx Timeouts:** https://nginx.org/en/docs/http/ngx_http_proxy_module.html

---

## 📞 Soporte

**En caso de bloqueos:**
1. Revisar logs: `docker logs paqueteria_staging_app`
2. Verificar Nginx: `sudo tail /var/log/nginx/error.log`
3. Reiniciar si es necesario: `docker restart paqueteria_staging_app`

**Contacto:**
- Equipo de Desarrollo
- Logs en: `/app/logs/app.log`

---

**Última actualización:** 2026-01-14  
**Versión:** 1.0.0  
**Estado:** ✅ Implementado y Activo
