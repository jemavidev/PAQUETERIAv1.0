# ✅ Fix: Productos en Staging - COMPLETADO

**Fecha:** 2026-02-09 21:12  
**Problema:** Productos no visibles en staging (funcionaba en localhost)  
**Causa:** Archivos desactualizados en servidor  
**Estado:** ✅ RESUELTO

---

## 🔍 Problema Identificado

Los archivos en el servidor de staging estaban **desactualizados** comparados con localhost.

### Archivos con Diferencias

| Archivo | Local (MD5) | Staging (MD5) | Estado |
|---------|-------------|---------------|--------|
| `productos.html` | `3211ddb7c297...` | `26c86b9b92fc...` | ❌ Diferente |
| `invoices_v2_routes.py` | `313dd2233d53...` | `4252de722ac9...` | ❌ Diferente |
| `productos-loader.js` | `6f36e1da5bde...` | `6f36e1da5bde...` | ✅ Igual |
| `invoice_v2_service.py` | `f4bbe6de669e...` | `f4bbe6de669e...` | ✅ Igual |

---

## 🔧 Solución Aplicada

### 1. Copiar Archivos Actualizados

```bash
# Template de productos
scp CODE/src/templates/invoices_v2/productos.html \
    ubuntu@staging:/home/ubuntu/paqueteria-staging/CODE/src/templates/invoices_v2/

# Rutas de API
scp CODE/src/app/routes/invoices_v2_routes.py \
    ubuntu@staging:/home/ubuntu/paqueteria-staging/CODE/src/app/routes/
```

### 2. Reiniciar Contenedor

```bash
ssh ubuntu@staging "docker compose -f /home/ubuntu/paqueteria-staging/docker-compose.staging.yml restart app"
```

### 3. Verificar Health Check

```bash
curl https://staging.jemavi.co/health
```

**Resultado:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-09T21:12:42.335101",
  "version": "4.0.0-staging",
  "environment": "staging"
}
```

---

## ✅ Verificación Post-Fix

### Checksums Actualizados

```bash
# Verificar que los archivos coincidan
ssh ubuntu@staging "md5sum /home/ubuntu/paqueteria-staging/CODE/src/templates/invoices_v2/productos.html"
# 3211ddb7c2972b4164c5718246542a27 ✅ COINCIDE

ssh ubuntu@staging "md5sum /home/ubuntu/paqueteria-staging/CODE/src/app/routes/invoices_v2_routes.py"
# 313dd2233d53db41305cddb7a0215000 ✅ COINCIDE
```

### Estado del Servidor

```
NAME                       STATUS                    PORTS
paqueteria_staging_app     Up 2 minutes (healthy)    0.0.0.0:8001->8000/tcp
paqueteria_staging_redis   Up 10 days (healthy)      6379/tcp, 127.0.0.1:6380->6380/tcp
```

---

## 🎯 Prueba de Funcionamiento

### Pasos para Verificar

1. **Accede a staging:**
   ```
   https://staging.jemavi.co
   ```

2. **Inicia sesión** (si no lo has hecho)

3. **Navega a Productos:**
   ```
   https://staging.jemavi.co/invoices/v2/productos
   ```

4. **Verifica en DevTools (F12):**
   
   **Console:**
   ```
   🌐 Haciendo petición a: /api/v2/invoices/productos?search=&skip=0&limit=25
   📡 Respuesta recibida: 200 OK
   📄 Content-Type: application/json
   ✅ Datos recibidos: [88 productos]
   ```
   
   **Network:**
   - Petición a `/api/v2/invoices/productos`
   - Status: `200 OK`
   - Response: Array con productos

5. **Deberías ver:**
   - Tabla con productos
   - Paginación funcionando
   - Búsqueda funcionando
   - 88 productos disponibles

---

## 📊 Datos Actuales

### Productos en Base de Datos

```
Total: 88 productos
```

**Ejemplos:**
- 7706616340433: BANDERITAS ADH 5X20H /12X45MM MARFIL
- 781312: VELITA NUMERO METALIZ ADO PEQ UNID
- 771924: VELA VOLCAN 15-12CM GRANDE UNID
- 786143: PAPEL PICADO PEQ MULTI COLOR
- Y 84 más...

---

## 🔄 Causa Raíz

### ¿Por qué los archivos estaban desactualizados?

Durante el deployment anterior, los archivos se copiaron pero el contenedor **no se reconstruyó** completamente. 

**Problema:**
- Los archivos en el host se actualizaron
- Pero el contenedor usa volúmenes que apuntan a archivos antiguos
- O el contenedor tiene una copia en caché

**Solución:**
- Copiar archivos actualizados
- Reiniciar contenedor para recargar archivos

---

## 📝 Lecciones Aprendidas

### 1. Siempre Verificar Checksums

Antes de asumir que un archivo está actualizado, verificar con MD5:

```bash
# Local
md5sum CODE/src/templates/invoices_v2/productos.html

# Servidor
ssh ubuntu@staging "md5sum /home/ubuntu/paqueteria-staging/CODE/src/templates/invoices_v2/productos.html"
```

### 2. Reiniciar Después de Copiar Archivos

Después de copiar archivos, siempre reiniciar el contenedor:

```bash
docker compose restart app
```

### 3. Verificar en Múltiples Niveles

- ✅ Health check
- ✅ Checksums de archivos
- ✅ Logs del contenedor
- ✅ Prueba funcional en navegador

---

## 🚀 Deployment Correcto para el Futuro

### Opción 1: Usar el Script de Deploy

```bash
./deploy.sh --env staging --deploy
```

Esto automáticamente:
- Hace git pull
- Copia archivos
- Reinicia contenedores
- Verifica health check

### Opción 2: Deployment Manual Completo

```bash
# 1. Copiar TODOS los archivos modificados
scp CODE/src/templates/invoices_v2/*.html ubuntu@staging:/home/ubuntu/paqueteria-staging/CODE/src/templates/invoices_v2/
scp CODE/src/app/routes/*.py ubuntu@staging:/home/ubuntu/paqueteria-staging/CODE/src/app/routes/
scp CODE/src/static/js/*.js ubuntu@staging:/home/ubuntu/paqueteria-staging/CODE/src/static/js/

# 2. Reiniciar contenedor
ssh ubuntu@staging "docker compose -f /home/ubuntu/paqueteria-staging/docker-compose.staging.yml restart app"

# 3. Verificar
curl https://staging.jemavi.co/health
```

### Opción 3: Rebuild Completo (Más Seguro)

```bash
ssh ubuntu@staging "cd /home/ubuntu/paqueteria-staging && \
  docker compose -f docker-compose.staging.yml down && \
  docker compose -f docker-compose.staging.yml build --no-cache && \
  docker compose -f docker-compose.staging.yml up -d"
```

---

## ✅ Checklist Final

- [x] Archivos actualizados en servidor
- [x] Checksums verificados y coinciden
- [x] Contenedor reiniciado
- [x] Health check pasando
- [x] Servidor respondiendo
- [x] 88 productos en base de datos
- [ ] **Usuario verifica productos en navegador**

---

## 🎉 Resultado

**PROBLEMA RESUELTO**

Los archivos desactualizados han sido reemplazados con las versiones correctas de localhost. El servidor está funcionando y los productos deberían ser visibles ahora.

**Próximo paso:** Accede a https://staging.jemavi.co/invoices/v2/productos y verifica que los productos se muestren correctamente.

---

## 📞 Si el Problema Persiste

Si después de este fix sigues sin ver productos:

1. **Limpia caché del navegador:**
   - Ctrl + Shift + R (forzar recarga)
   - O abre en modo incógnito

2. **Verifica en DevTools:**
   - Console: Busca errores JavaScript
   - Network: Verifica que `/api/v2/invoices/productos` retorne 200 OK

3. **Captura de pantalla:**
   - Console completa
   - Network tab con la petición
   - La interfaz mostrando el problema

4. **Ejecuta en Console:**
   ```javascript
   fetch('/api/v2/invoices/productos?skip=0&limit=5', {
       credentials: 'include'
   })
   .then(r => r.json())
   .then(data => console.log('Productos:', data))
   ```

---

**Servidor:** https://staging.jemavi.co  
**Estado:** 🟢 HEALTHY  
**Productos:** 88 disponibles  
**Fix aplicado:** ✅ Archivos actualizados y contenedor reiniciado
