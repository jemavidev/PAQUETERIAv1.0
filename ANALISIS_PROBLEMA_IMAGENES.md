# 🔍 Análisis: Problema de Visualización de Imágenes

**Fecha:** 7 de diciembre de 2025  
**Commit Base Funcional:** `ae4579ae52b0c5274428662124c7accad848b9b6` (1 dic 2025)  
**Estado:** ❌ Imágenes NO se visualizan después de este commit

---

## 🎯 CAUSA RAÍZ IDENTIFICADA

### El Problema: Orden de Montaje de Archivos Estáticos

**Commit Problemático:** `b8fcaab` (6 dic 2025)  
**Título:** "fix: Montar archivos estáticos ANTES de middlewares para evitar bloqueo de /uploads/"  
**Revertido por:** `d095700` (6 dic 2025)

---

## 📊 Cronología del Problema

### 1. Estado Original (FUNCIONABA) ✅
**Hasta commit:** `ae4579a` (1 dic 2025)

```python
# CODE/src/main.py - ORDEN CORRECTO

# 1. Configurar métricas
Instrumentator().instrument(app).expose(app)

# 2. Agregar middlewares
app.add_middleware(CORSMiddleware, ...)
app.add_middleware(AuthMiddleware, ...)
app.add_middleware(SlowAPIMiddleware)

# 3. Montar archivos estáticos DESPUÉS de middlewares
app.mount("/static", StaticFiles(...))
app.mount("/uploads", StaticFiles(...))
```

**¿Por qué funcionaba?**
- Los middlewares se ejecutan en orden INVERSO al que se agregan
- FastAPI procesa las rutas montadas (`app.mount`) ANTES que los middlewares
- El `AuthMiddleware` verifica `is_static_route()` y permite el acceso
- Las imágenes en `/uploads/` se sirven correctamente

---

### 2. Intento de Fix (ROMPIÓ TODO) ❌
**Commit:** `b8fcaab` (6 dic 2025, 07:28)

```python
# CODE/src/main.py - ORDEN INCORRECTO

# 1. Configurar métricas
Instrumentator().instrument(app).expose(app)

# 2. Montar archivos estáticos ANTES de middlewares
app.mount("/static", StaticFiles(...))
app.mount("/uploads", StaticFiles(...))

# 3. Agregar middlewares DESPUÉS
app.add_middleware(CORSMiddleware, ...)
app.add_middleware(AuthMiddleware, ...)
app.add_middleware(SlowAPIMiddleware)
```

**¿Por qué NO funciona?**
- Al montar ANTES de agregar middlewares, FastAPI cambia el orden de procesamiento
- Los middlewares se ejecutan ANTES que las rutas montadas
- El `AuthMiddleware` intercepta las peticiones a `/uploads/` ANTES de que lleguen a `StaticFiles`
- Aunque `is_static_route("/uploads/image.jpg")` retorna `True`, la petición nunca llega a verificarse correctamente

---

### 3. Reversión (DEBERÍA FUNCIONAR) ✅
**Commit:** `d095700` (6 dic 2025, 07:43)

```python
# CODE/src/main.py - VUELVE AL ORDEN CORRECTO

# 1. Configurar métricas
Instrumentator().instrument(app).expose(app)

# 2. Agregar middlewares PRIMERO
app.add_middleware(CORSMiddleware, ...)
app.add_middleware(AuthMiddleware, ...)
app.add_middleware(SlowAPIMiddleware)

# 3. Montar archivos estáticos DESPUÉS
app.mount("/static", StaticFiles(...))
app.mount("/uploads", StaticFiles(...))
```

**Estado:** Este es el orden correcto y debería funcionar

---

## 🔬 Análisis Técnico Detallado

### Cómo Funciona FastAPI con Middlewares y Rutas Montadas

#### Orden de Ejecución en FastAPI:

1. **Request llega al servidor**
2. **Middlewares se ejecutan** (en orden INVERSO al que se agregaron)
3. **Router principal busca coincidencias**
4. **Rutas montadas (`app.mount`) se procesan**
5. **Response regresa a través de los middlewares**

#### El Problema con el Orden Incorrecto:

```
Request: GET /uploads/image.jpg

ORDEN INCORRECTO (b8fcaab):
1. Request llega
2. AuthMiddleware se ejecuta
   - Verifica is_static_route("/uploads/image.jpg") → True
   - Debería continuar... PERO
3. FastAPI busca en router principal
4. NO encuentra la ruta (porque StaticFiles se montó ANTES)
5. Retorna 404 o redirección

ORDEN CORRECTO (d095700):
1. Request llega
2. AuthMiddleware se ejecuta
   - Verifica is_static_route("/uploads/image.jpg") → True
   - Continúa sin bloquear
3. FastAPI busca en router principal
4. Encuentra StaticFiles montado en /uploads/
5. Sirve la imagen correctamente
```

---

## 🐛 Por Qué el "Fix" Rompió las Imágenes

### Intención del Commit `b8fcaab`:
El desarrollador pensó que montar archivos estáticos ANTES de middlewares evitaría que el `AuthMiddleware` los bloqueara.

### Realidad:
En FastAPI, el orden de `app.mount()` vs `app.add_middleware()` NO afecta el orden de ejecución de middlewares. Los middlewares SIEMPRE se ejecutan primero, independientemente de cuándo se agreguen.

Lo que SÍ afecta es:
- **Cuándo se monta:** Afecta el registro interno de rutas en FastAPI
- **Orden de middlewares:** Se ejecutan en orden INVERSO (LIFO - Last In, First Out)

### El Verdadero Problema:
El commit `b8fcaab` rompió el registro interno de rutas de FastAPI, causando que las peticiones a `/uploads/` no coincidieran correctamente con el `StaticFiles` montado.

---

## ✅ Solución Confirmada

### Estado Actual de las Ramas:

#### Main (DEBERÍA FUNCIONAR) ✅
```python
# Orden correcto (después de ae4579a)
app.add_middleware(...)  # Middlewares primero
app.mount("/uploads", StaticFiles(...))  # Static files después
```

**Commits en main:**
- `ae4579a` → ... → `0e3f544` (24 commits)
- NO incluye `b8fcaab` (el commit problemático)
- NO incluye `d095700` (la reversión)

**Conclusión:** Main NUNCA tuvo el bug, debería funcionar

---

#### Staging (DEBERÍA FUNCIONAR) ✅
```python
# Orden correcto (después de revertir)
app.add_middleware(...)  # Middlewares primero
app.mount("/uploads", StaticFiles(...))  # Static files después
```

**Commits en staging:**
- `ae4579a` → ... → `b8fcaab` (bug introducido) → `d095700` (bug revertido)

**Conclusión:** Staging tuvo el bug por 15 minutos, luego se revirtió

---

## 🔍 Verificación del Problema

### Si las Imágenes NO Funcionan en Main:

El problema NO es el orden de montaje (porque main nunca tuvo ese bug).

**Posibles causas alternativas:**

1. **Problema de permisos en `/app/uploads/`**
   ```bash
   # Verificar en el contenedor
   docker exec -it <container> ls -la /app/uploads/
   ```

2. **Directorio no existe**
   ```bash
   # Verificar si se crea correctamente
   docker exec -it <container> python -c "from pathlib import Path; print(Path('/app/uploads').exists())"
   ```

3. **Volumen no montado correctamente**
   ```bash
   # Verificar docker-compose
   docker-compose config | grep -A 5 uploads
   ```

4. **Middleware bloqueando incorrectamente**
   ```bash
   # Verificar logs
   docker logs <container> | grep "uploads"
   ```

5. **Problema de CORS**
   ```bash
   # Verificar headers en navegador
   # Network tab → Click en imagen → Headers
   ```

---

## 🧪 Pruebas para Diagnosticar

### Prueba 1: Verificar Configuración de Rutas Estáticas

```bash
cd CODE
docker exec -it <container> python -c "
from src.app.config_routes import is_static_route
print('Test /uploads/image.jpg:', is_static_route('/uploads/image.jpg'))
print('Test /static/css/style.css:', is_static_route('/static/css/style.css'))
print('Test /admin:', is_static_route('/admin'))
"
```

**Resultado esperado:**
```
Test /uploads/image.jpg: True
Test /static/css/style.css: True
Test /admin: False
```

---

### Prueba 2: Verificar Orden de Middlewares

```bash
cd CODE
docker exec -it <container> python -c "
import sys
sys.path.insert(0, '/app/src')
from main import app
print('Middlewares:', [m.__class__.__name__ for m in app.user_middleware])
print('Routes:', [r.path for r in app.routes if hasattr(r, 'path')])
"
```

---

### Prueba 3: Probar Acceso Directo a Imagen

```bash
# Desde el servidor
curl -I http://localhost:8000/uploads/test.jpg

# Desde fuera
curl -I https://paquetex.papyrus.com.co/uploads/test.jpg
```

**Resultado esperado:** `200 OK` o `404 Not Found` (no `302 Redirect` ni `401 Unauthorized`)

---

### Prueba 4: Verificar Logs del Middleware

```bash
# Activar logging detallado
docker exec -it <container> python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
"

# Luego intentar cargar una imagen y ver logs
docker logs -f <container> | grep -E "(uploads|static|AuthMiddleware)"
```

---

## 🎯 Recomendaciones

### 1. Si Main NO Funciona (Problema Diferente)

El problema NO es el orden de montaje. Investigar:

**A. Verificar que el directorio existe y tiene permisos:**
```bash
docker exec -it <container> bash
ls -la /app/uploads/
# Debería mostrar archivos de imágenes
```

**B. Verificar que el volumen está montado:**
```bash
docker-compose config | grep -A 10 volumes
# Debería mostrar: - ./uploads:/app/uploads
```

**C. Verificar que las imágenes existen:**
```bash
docker exec -it <container> find /app/uploads -name "*.jpg" -o -name "*.png"
```

**D. Probar acceso directo sin middleware:**
```python
# Agregar temporalmente en main.py ANTES de middlewares
@app.get("/test-upload")
async def test_upload():
    from pathlib import Path
    uploads = list(Path("/app/uploads").glob("*"))
    return {"files": [str(f) for f in uploads]}
```

---

### 2. Si Staging NO Funciona (Problema de Reversión)

Verificar que la reversión se aplicó correctamente:

```bash
git show d095700:CODE/src/main.py | grep -A 20 "Montar archivos"
```

Debería mostrar que `app.mount()` está DESPUÉS de `app.add_middleware()`.

---

### 3. Solución Definitiva

**Asegurar el orden correcto en `main.py`:**

```python
# ✅ ORDEN CORRECTO (DEBE SER ASÍ)

# 1. Crear app
app = FastAPI(...)

# 2. Configurar métricas
Instrumentator().instrument(app).expose(app)

# 3. Agregar middlewares
app.add_middleware(CORSMiddleware, ...)
app.add_middleware(AuthMiddleware, ...)
app.add_middleware(SlowAPIMiddleware)

# 4. Montar archivos estáticos (DESPUÉS de middlewares)
app.mount("/static", StaticFiles(directory="/app/src/static"), name="static")

from pathlib import Path
uploads_dir = Path("/app/uploads")
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# 5. Configurar templates
templates = get_templates()

# 6. Agregar routers
app.include_router(...)
```

---

## 📝 Resumen Ejecutivo

### Causa del Problema:
El commit `b8fcaab` intentó "arreglar" el acceso a `/uploads/` montando archivos estáticos ANTES de middlewares, pero esto rompió el registro interno de rutas de FastAPI.

### Estado Actual:
- **Main:** NUNCA tuvo el bug (orden correcto desde `ae4579a`)
- **Staging:** Tuvo el bug por 15 minutos, luego se revirtió en `d095700`

### Si las Imágenes NO Funcionan:
El problema NO es el orden de montaje. Buscar en:
1. Permisos del directorio `/app/uploads/`
2. Volumen no montado en `docker-compose.yml`
3. Imágenes no existen en el servidor
4. Problema de CORS o headers
5. Middleware bloqueando incorrectamente (bug en `is_static_route()`)

### Próximo Paso:
Ejecutar las **Pruebas de Diagnóstico** (arriba) para identificar la causa real.

---

**Conclusión:** El commit `b8fcaab` fue el culpable, pero ya fue revertido. Si las imágenes aún no funcionan, el problema es OTRO (no el orden de montaje).
