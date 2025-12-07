# 🚨 Diagnóstico Rápido: Problema de Imágenes

## ✅ CONCLUSIÓN PRINCIPAL

**Ambas ramas (main y staging) tienen el código CORRECTO.**

El commit `b8fcaab` que rompió las imágenes YA FUE REVERTIDO en staging (`d095700`), y main NUNCA tuvo ese bug.

**Si las imágenes NO funcionan, el problema es OTRO, no el orden de montaje.**

---

## 🔍 Commit Sospechoso (YA REVERTIDO)

**Commit:** `b8fcaab` (6 dic 2025, 07:28)  
**Título:** "fix: Montar archivos estáticos ANTES de middlewares"  
**Estado:** ❌ Rompió las imágenes  
**Revertido:** `d095700` (6 dic 2025, 07:43) - 15 minutos después

**¿Qué hizo?**
Cambió el orden de montaje de archivos estáticos, poniéndolos ANTES de los middlewares.

**¿Por qué rompió las imágenes?**
En FastAPI, montar rutas ANTES de agregar middlewares causa que el registro interno de rutas no funcione correctamente.

---

## 📊 Estado Actual del Código

### Main (Producción) ✅
```python
# Orden CORRECTO
app.add_middleware(CORSMiddleware, ...)
app.add_middleware(AuthMiddleware, ...)
app.add_middleware(SlowAPIMiddleware)

# Archivos estáticos DESPUÉS de middlewares
app.mount("/static", StaticFiles(...))
app.mount("/uploads", StaticFiles(...))
```

### Staging ✅
```python
# Orden CORRECTO (después de revertir)
app.add_middleware(CORSMiddleware, ...)
app.add_middleware(AuthMiddleware, ...)
app.add_middleware(SlowAPIMiddleware)

# Archivos estáticos DESPUÉS de middlewares
app.mount("/static", StaticFiles(...))
app.mount("/uploads", StaticFiles(...))
```

**Ambas ramas tienen el mismo código correcto.**

---

## 🧪 Pruebas de Diagnóstico

### Prueba 1: Verificar que el directorio existe

```bash
# En el servidor
docker exec -it paquetex_web bash
ls -la /app/uploads/

# Debería mostrar archivos de imágenes
# Si está vacío o no existe, ese es el problema
```

### Prueba 2: Verificar permisos

```bash
docker exec -it paquetex_web bash
ls -la /app/ | grep uploads

# Debería mostrar algo como:
# drwxr-xr-x  2 root root  4096 Dec  7 12:00 uploads
```

### Prueba 3: Verificar volumen en docker-compose

```bash
# Ver configuración actual
docker-compose config | grep -A 10 volumes

# Debería mostrar:
# volumes:
#   - ./uploads:/app/uploads
```

### Prueba 4: Probar acceso directo a una imagen

```bash
# Desde el servidor
curl -I http://localhost:8000/uploads/test.jpg

# Desde fuera
curl -I https://paquetex.papyrus.com.co/uploads/test.jpg

# Resultado esperado: 200 OK (imagen existe) o 404 (no existe)
# Resultado MALO: 302 Redirect o 401 Unauthorized
```

### Prueba 5: Verificar configuración de rutas estáticas

```bash
docker exec -it paquetex_web python3 -c "
import sys
sys.path.insert(0, '/app/src')
from app.config_routes import is_static_route, STATIC_PREFIXES
print('Prefijos estáticos:', STATIC_PREFIXES)
print('Test /uploads/image.jpg:', is_static_route('/uploads/image.jpg'))
print('Test /static/css/style.css:', is_static_route('/static/css/style.css'))
"

# Resultado esperado:
# Prefijos estáticos: {'/static/', '/uploads/'}
# Test /uploads/image.jpg: True
# Test /static/css/style.css: True
```

### Prueba 6: Ver logs del middleware

```bash
# Ver logs en tiempo real
docker logs -f paquetex_web | grep -E "(uploads|static|AuthMiddleware)"

# Luego intenta cargar una imagen en el navegador
# Deberías ver si el middleware está bloqueando o permitiendo
```

---

## 🎯 Posibles Causas (Si Aún No Funciona)

### 1. Directorio /app/uploads vacío o no existe
**Síntoma:** 404 Not Found  
**Solución:**
```bash
docker exec -it paquetex_web mkdir -p /app/uploads
docker exec -it paquetex_web chmod 755 /app/uploads
```

### 2. Volumen no montado correctamente
**Síntoma:** Imágenes subidas desaparecen al reiniciar  
**Solución:** Verificar `docker-compose.yml`:
```yaml
services:
  web:
    volumes:
      - ./uploads:/app/uploads  # Debe existir esta línea
```

### 3. Imágenes con rutas incorrectas en HTML
**Síntoma:** 404 Not Found en imágenes específicas  
**Solución:** Verificar que las rutas en HTML sean:
```html
<!-- CORRECTO -->
<img src="/uploads/image.jpg">

<!-- INCORRECTO -->
<img src="uploads/image.jpg">
<img src="/app/uploads/image.jpg">
```

### 4. Problema de CORS
**Síntoma:** Imágenes no cargan desde otro dominio  
**Solución:** Verificar headers CORS en navegador (F12 → Network → Click en imagen)

### 5. Middleware bloqueando incorrectamente
**Síntoma:** 302 Redirect o 401 Unauthorized  
**Solución:** Verificar que `is_static_route()` funciona correctamente (Prueba 5)

### 6. Nginx bloqueando (si usas nginx)
**Síntoma:** 403 Forbidden o 404 Not Found  
**Solución:** Verificar configuración de nginx:
```nginx
location /uploads/ {
    proxy_pass http://web:8000/uploads/;
}
```

---

## 🔧 Solución Rápida (Si Middleware Está Bloqueando)

Si las pruebas muestran que el middleware está bloqueando `/uploads/`, agregar temporalmente:

```python
# En CODE/src/app/middleware/auth_middleware.py
# Línea ~70, en el método dispatch()

async def dispatch(self, request: Request, call_next):
    path = request.url.path
    
    # DEBUG: Log para ver qué pasa con uploads
    if path.startswith("/uploads/"):
        logger.info(f"🖼️ Request a uploads: {path}")
        logger.info(f"   is_static_route: {is_static_route(path)}")
    
    # ... resto del código
```

Luego reiniciar y ver logs:
```bash
docker-compose restart web
docker logs -f paquetex_web | grep "🖼️"
```

---

## 📝 Resumen Ejecutivo

### ¿Qué commit rompió las imágenes?
**`b8fcaab`** - "fix: Montar archivos estáticos ANTES de middlewares"

### ¿Está el bug en main o staging?
**NO.** El bug fue revertido en staging (`d095700`) y main nunca lo tuvo.

### ¿Por qué las imágenes no funcionan entonces?
El problema es OTRO, no el orden de montaje. Posibles causas:
1. Directorio `/app/uploads/` vacío o sin permisos
2. Volumen no montado en `docker-compose.yml`
3. Rutas incorrectas en HTML
4. Problema de CORS
5. Nginx bloqueando (si aplica)

### ¿Qué hacer ahora?
1. Ejecutar **Prueba 1** para verificar que el directorio existe
2. Ejecutar **Prueba 4** para probar acceso directo
3. Ejecutar **Prueba 5** para verificar configuración de rutas
4. Si todo está bien, el problema es de infraestructura (nginx, volúmenes, etc.)

---

## 🚀 Acción Inmediata

**Ejecuta este comando para diagnóstico completo:**

```bash
#!/bin/bash
echo "=== DIAGNÓSTICO DE IMÁGENES ==="
echo ""
echo "1. Verificar directorio uploads:"
docker exec paquetex_web ls -la /app/uploads/ | head -10
echo ""
echo "2. Verificar permisos:"
docker exec paquetex_web stat /app/uploads
echo ""
echo "3. Verificar configuración de rutas:"
docker exec paquetex_web python3 -c "
import sys
sys.path.insert(0, '/app/src')
from app.config_routes import is_static_route, STATIC_PREFIXES
print('Prefijos:', STATIC_PREFIXES)
print('Test /uploads/test.jpg:', is_static_route('/uploads/test.jpg'))
"
echo ""
echo "4. Probar acceso directo:"
curl -I http://localhost:8000/uploads/test.jpg 2>&1 | head -5
echo ""
echo "5. Ver últimos logs:"
docker logs paquetex_web 2>&1 | grep -E "(uploads|static)" | tail -10
```

Guarda esto como `diagnostico_imagenes.sh`, dale permisos y ejecútalo:
```bash
chmod +x diagnostico_imagenes.sh
./diagnostico_imagenes.sh
```

---

**Conclusión:** El código está correcto en ambas ramas. Si las imágenes no funcionan, el problema es de infraestructura, no de código.
