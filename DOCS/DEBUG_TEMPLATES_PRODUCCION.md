# 🔍 Debug: Por qué funciona en localhost pero no en producción

## 🤔 La Pregunta

**¿Por qué las vistas de términos y privacidad funcionan en localhost pero no en el servidor de la nube?**

## 📊 Diferencias entre Localhost y Producción

### 1. Configuración de Uvicorn

**Localhost (dev):**
```bash
uvicorn src.main:app --reload --log-level debug
```
- ✅ `--reload`: Recarga automática de código
- ✅ `--log-level debug`: Logs detallados
- ✅ Auto-reload de templates activado

**Producción:**
```bash
uvicorn src.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker
```
- ❌ Sin `--reload`
- ❌ Log level INFO (menos detallado)
- ⚠️ Templates pueden estar cacheados

### 2. Variables de Entorno

**Localhost:**
```yaml
environment:
  - ENVIRONMENT=development
```

**Producción:**
```yaml
environment:
  - ENVIRONMENT=production
```

### 3. Volúmenes y Sincronización

**Localhost:**
```yaml
volumes:
  - ./CODE/src:/app/src  # Sincronización en tiempo real
```

**Producción:**
```yaml
volumes:
  - ./CODE/src:/app/src  # Puede no estar sincronizado si no se reinicia
```

## 🐛 Posibles Causas del Error

### Causa 1: Templates No Sincronizados

**Síntoma:** JSON de error en lugar de HTML

**Razón:** Los archivos `terms.html` y `privacy.html` no están en el contenedor de producción.

**Solución:**
```bash
# Verificar en el servidor
docker exec paqueteria_v1_prod_app ls -lh /app/src/templates/general/

# Si no existen, hacer pull y reiniciar
git pull origin main
docker compose -f docker-compose.prod.yml restart app
```

### Causa 2: Error en el Contexto

**Síntoma:** Excepción al renderizar el template

**Razón:** Alguna variable del contexto causa error en producción pero no en desarrollo.

**Ejemplo:**
```python
# En el template
{{ user.email }}  # Si user es None, puede fallar

# Solución: usar filtros seguros
{{ user.email if user else 'N/A' }}
```

**Fix aplicado:**
- Agregado try/catch en las rutas
- Contexto mínimo como fallback
- Logs detallados para debug

### Causa 3: Template Base con Errores

**Síntoma:** Error al extender `base/base.html`

**Razón:** El template base puede tener referencias a variables que no existen en el contexto.

**Verificación:**
```bash
# Ver el template base
docker exec paqueteria_v1_prod_app cat /app/src/templates/base/base.html | head -50
```

### Causa 4: Caché de Templates

**Síntoma:** Cambios no se reflejan

**Razón:** Jinja2 puede cachear templates en producción.

**Solución:**
```python
# En template_loader.py
Jinja2Templates(directory=templates_dir, auto_reload=True)  # ✅ Ya configurado
```

### Causa 5: Permisos de Archivos

**Síntoma:** Error de lectura de archivos

**Razón:** Los archivos no tienen permisos de lectura en el contenedor.

**Solución:**
```bash
# En el servidor
chmod 644 CODE/src/templates/general/*.html
```

### Causa 6: Error Handler Capturando Excepciones

**Síntoma:** JSON en lugar de HTML

**Razón:** El error handler estaba devolviendo siempre JSON.

**Solución:** ✅ Ya corregido en commit `76ff7e0`

## 🔧 Fixes Aplicados

### Fix 1: Error Handler Inteligente

**Antes:**
```python
# Siempre devolvía JSON
return JSONResponse({"success": False, "message": "Error"})
```

**Después:**
```python
# Detecta tipo de petición
if is_api_request:
    return JSONResponse(...)
else:
    return HTMLResponse(...)
```

### Fix 2: Rutas con Try/Catch

**Antes:**
```python
@router.get("/terms")
async def terms_page(request: Request):
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("general/terms.html", context)
```

**Después:**
```python
@router.get("/terms")
async def terms_page(request: Request):
    try:
        context = get_auth_context_from_request(request)
        logger.info(f"Renderizando /terms con contexto: {list(context.keys())}")
        return templates.TemplateResponse("general/terms.html", context)
    except Exception as e:
        logger.error(f"Error al renderizar /terms: {str(e)}", exc_info=True)
        # Fallback con contexto mínimo
        minimal_context = {"request": request, "is_authenticated": False, ...}
        return templates.TemplateResponse("general/terms.html", minimal_context)
```

### Fix 3: Logs Detallados

Ahora los logs mostrarán:
- ✅ Qué contexto se está usando
- ✅ Errores específicos al renderizar
- ✅ Stack trace completo

## 🧪 Cómo Debuggear en Producción

### 1. Ver Logs en Tiempo Real

```bash
docker logs -f paqueteria_v1_prod_app
```

### 2. Buscar Errores Específicos

```bash
docker logs paqueteria_v1_prod_app 2>&1 | grep -i "error\|exception\|terms\|privacy"
```

### 3. Verificar Templates en el Contenedor

```bash
# Listar templates
docker exec paqueteria_v1_prod_app find /app/src/templates -name "*.html"

# Ver contenido de un template
docker exec paqueteria_v1_prod_app cat /app/src/templates/general/terms.html | head -20
```

### 4. Probar Endpoint Directamente

```bash
# Desde el servidor
curl -v http://localhost:8000/terms

# Ver headers de respuesta
curl -I http://localhost:8000/terms
```

### 5. Entrar al Contenedor

```bash
docker exec -it paqueteria_v1_prod_app bash

# Dentro del contenedor
cd /app/src/templates/general
ls -lh
cat terms.html | head -50
```

## 📋 Checklist de Verificación

Cuando algo funciona en localhost pero no en producción:

- [ ] ¿Se hizo `git pull` en el servidor?
- [ ] ¿Se reinició el contenedor después del pull?
- [ ] ¿Los archivos existen en el contenedor?
- [ ] ¿Los permisos son correctos (644)?
- [ ] ¿Los logs muestran algún error?
- [ ] ¿El error handler está devolviendo el formato correcto?
- [ ] ¿El contexto tiene todas las variables necesarias?
- [ ] ¿El template base existe y es válido?

## 🎯 Solución Definitiva

### Paso 1: Actualizar Código

```bash
# En el servidor
cd /ruta/al/proyecto
git pull origin main
```

### Paso 2: Reiniciar Contenedor

```bash
docker compose -f docker-compose.prod.yml restart app
sleep 10
```

### Paso 3: Verificar Logs

```bash
docker logs paqueteria_v1_prod_app --tail 50
```

### Paso 4: Probar Endpoints

```bash
curl -I http://localhost:8000/terms
curl -I http://localhost:8000/privacy
```

### Paso 5: Si Sigue Fallando

```bash
# Ver logs en tiempo real
docker logs -f paqueteria_v1_prod_app

# En otra terminal, probar el endpoint
curl http://localhost:8000/terms

# Los logs mostrarán el error exacto
```

## 💡 Lecciones Aprendidas

1. **Siempre reiniciar después de cambios** en templates o código Python
2. **Usar logs detallados** para debug en producción
3. **Tener fallbacks** en caso de errores
4. **Detectar tipo de petición** (API vs navegador) en error handlers
5. **Verificar sincronización** de archivos en volúmenes Docker

## 🔗 Documentación Relacionada

- `DOCS/FIX_ERROR_HANDLER_JSON.md` - Fix del error handler
- `COMANDO_AWS_ACTUALIZAR.txt` - Comandos para actualizar
- `DOCS/SOLUCION_SINCRONIZACION_TEMPLATES.md` - Solución de sincronización

---

**Fecha:** 2025-11-21  
**Versión:** 1.0  
**Estado:** ✅ Documentado  
**Autor:** Sistema Kiro
