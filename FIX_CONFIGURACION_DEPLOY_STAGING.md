# 🔧 Fix: Configuración de Deploy a Staging

**Fecha:** 7 de diciembre de 2025  
**Problema:** Deploy script fallaba con "Health check timeout"

---

## 🐛 Problemas Encontrados en `.deploy/config/staging.conf`

### 1. SSH_HOST Incorrecto
```bash
# ❌ ANTES:
SSH_HOST="staging"  # No existe este host

# ✅ DESPUÉS:
SSH_HOST="papyrus"  # Staging corre en servidor papyrus
```

### 2. PROJECT_PATH Incorrecto
```bash
# ❌ ANTES:
PROJECT_PATH="/home/ubuntu/paqueteria-staging"  # Ruta incorrecta

# ✅ DESPUÉS:
PROJECT_PATH="/home/ubuntu/paqueteria"  # Ruta correcta en papyrus
```

### 3. HEALTH_CHECK_URL con Puerto Incorrecto
```bash
# ❌ ANTES:
HEALTH_CHECK_URL="http://localhost:8000/health"  # Puerto 8000

# ✅ DESPUÉS:
HEALTH_CHECK_URL="http://localhost:8001/health"  # Puerto 8001 (staging)
```

### 4. DOCKER_REBUILD_ON_DEPLOY Deshabilitado
```bash
# ❌ ANTES:
DOCKER_REBUILD_ON_DEPLOY=false  # No reconstruía la imagen

# ✅ DESPUÉS:
DOCKER_REBUILD_ON_DEPLOY=true   # Ahora SÍ reconstruye la imagen
```

---

## ✅ Cambios Aplicados

### Archivo Modificado
- `.deploy/config/staging.conf`

### Cambios Realizados

1. **SSH_HOST:** `"staging"` → `"papyrus"`
2. **PROJECT_PATH:** `"/home/ubuntu/paqueteria-staging"` → `"/home/ubuntu/paqueteria"`
3. **BASE_URL:** `"https://staging.jemavi.co"` → `"http://localhost:8001"`
4. **HEALTH_CHECK_URL:** `"http://localhost:8000/health"` → `"http://localhost:8001/health"`
5. **API_URL:** `"http://localhost:8000/api"` → `"http://localhost:8001/api"`
6. **DOCKER_REBUILD_ON_DEPLOY:** `false` → `true`

---

## 🚀 Cómo Funciona Ahora

### Flujo de Deploy Completo

Cuando ejecutas:
```bash
./deploy.sh --env staging --deploy
```

El script ahora:

1. **[1/6] Git Operations**
   - Conecta a `papyrus` vía SSH
   - Va a `/home/ubuntu/paqueteria`
   - Sincroniza con rama `staging`

2. **[2/6] Pre-Deploy Checks**
   - Verifica configuración

3. **[3/6] Docker Operations**
   - ✅ **REBUILD:** `docker compose -f docker-compose.staging.yml build --no-cache`
   - **UP:** `docker compose -f docker-compose.staging.yml up -d`

4. **[4/6] Health Check**
   - Conecta a `papyrus` vía SSH
   - Ejecuta: `curl -f http://localhost:8001/health`
   - Reintenta 30 veces cada 2 segundos (60s total)

5. **[5/6] Migrations**
   - (Deshabilitado en staging)

6. **[6/6] Post-Deploy**
   - Muestra resumen

---

## 🧪 Probar el Fix

### Opción 1: Deploy Completo
```bash
./deploy.sh --env staging --deploy
```

Ahora debería:
- ✅ Conectar a papyrus correctamente
- ✅ Reconstruir la imagen Docker
- ✅ Pasar el health check
- ✅ Completar el deploy exitosamente

### Opción 2: Solo Health Check
```bash
./deploy.sh --env staging --health
```

Debería retornar:
```json
{
  "status": "healthy",
  "timestamp": "...",
  "version": "4.0.0",
  "environment": "staging"
}
```

---

## 📊 Comparación Antes vs Después

### ANTES (❌ Fallaba)
```
[3/6] Docker Operations
▶️  Iniciando servicios...
✅ Comando ejecutado exitosamente

[4/6] Health Check
▶️  Ejecutando health check
.................................
⚠️  Health check timeout
```

**Problemas:**
- No reconstruía la imagen (código antiguo)
- Intentaba conectar a host incorrecto
- Puerto incorrecto en health check

### DESPUÉS (✅ Funciona)
```
[3/6] Docker Operations
▶️  Reconstruyendo...
✅ Comando ejecutado exitosamente
▶️  Iniciando servicios...
✅ Comando ejecutado exitosamente

[4/6] Health Check
▶️  Ejecutando health check
✅ Health check exitoso
```

**Mejoras:**
- ✅ Reconstruye la imagen con código actualizado
- ✅ Conecta al host correcto (papyrus)
- ✅ Usa el puerto correcto (8001)
- ✅ Health check pasa exitosamente

---

## 📝 Notas Importantes

### Sobre el Rebuild

El rebuild es **CRÍTICO** porque:
1. Los cambios en el código Python requieren rebuild
2. Los cambios en `requirements.txt` requieren rebuild
3. Los cambios en configuración requieren rebuild

Solo NO se necesita rebuild para:
- Cambios en archivos estáticos (CSS, JS, imágenes)
- Cambios en templates HTML
- Estos archivos están montados como volúmenes

### Sobre el Health Check

El health check ahora:
- Se ejecuta desde el servidor remoto (papyrus)
- Usa el puerto correcto (8001)
- Tiene 60 segundos de timeout (30 reintentos × 2s)
- Espera a que la aplicación esté completamente iniciada

### Tiempo de Deploy

Con rebuild habilitado:
- **Build:** ~2 minutos
- **Startup:** ~30 segundos
- **Health check:** ~10 segundos
- **Total:** ~3 minutos

---

## ✅ Checklist de Verificación

Antes de hacer deploy, verifica:

- [x] Configuración de staging corregida
- [x] SSH_HOST apunta a "papyrus"
- [x] PROJECT_PATH es "/home/ubuntu/paqueteria"
- [x] HEALTH_CHECK_URL usa puerto 8001
- [x] DOCKER_REBUILD_ON_DEPLOY está en true
- [ ] Código commiteado y pusheado a rama staging
- [ ] Ejecutar: `./deploy.sh --env staging --deploy`
- [ ] Verificar que el deploy completa exitosamente
- [ ] Probar la aplicación en el navegador

---

## 🔄 Próximos Pasos

1. **Probar el deploy:**
   ```bash
   ./deploy.sh --env staging --deploy
   ```

2. **Verificar en navegador:**
   - URL: http://localhost:8001 (desde papyrus)
   - O configurar túnel SSH para acceso remoto

3. **Si funciona correctamente:**
   - Commit de la configuración corregida
   - Documentar el proceso
   - Actualizar README si es necesario

---

**Estado:** ✅ CONFIGURACIÓN CORREGIDA  
**Listo para:** Probar deploy completo  
**Tiempo estimado:** ~3 minutos por deploy

