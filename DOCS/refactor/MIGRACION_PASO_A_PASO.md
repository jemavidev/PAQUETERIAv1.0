# Migración Paso a Paso - Refactor de Autenticación

## Objetivo

Migrar del sistema actual al sistema refactorizado sin breaking changes.

## Estrategia

Migración gradual en 4 fases, cada una verificable con tests.

## Pre-requisitos

1. ✅ Todos los tests actuales pasando
2. ✅ Backup de base de datos
3. ✅ Branch de desarrollo creado
4. ✅ Playwright instalado

```bash
cd CODE
pip install -r tests/requirements-test.txt
playwright install chromium
```

## Fase 1: Preparación (Sin Breaking Changes)

**Duración estimada**: 2 horas

### 1.1. Crear configuración centralizada

```bash
# Ya creado en: CODE/src/app/config/routes.py
```

**Verificar**:
```python
from app.config.routes import is_public_route, get_all_public_routes

# Test
assert is_public_route("/auth/login") == True
assert is_public_route("/admin") == False
print("✅ Configuración de rutas funciona")
```

### 1.2. Crear endpoint de configuración

```bash
# Ya creado en: CODE/src/app/routes/config.py
```

**Agregar al main.py**:
```python
# En CODE/src/main.py
from src.app.routes import config

# Después de las otras rutas
app.include_router(config.router, tags=["Configuración"])
```

**Verificar**:
```bash
curl http://localhost:8000/api/config/public-routes
# Debería retornar JSON con rutas públicas
```

### 1.3. Crear nuevo middleware (sin activar)

```bash
# Ya creado en: CODE/src/app/middleware/auth_middleware_v2.py
```

**NO activar todavía**, solo verificar que compila:
```python
from app.middleware.auth_middleware_v2 import AuthMiddlewareV2
print("✅ Middleware v2 importa correctamente")
```

### 1.4. Crear JavaScript refactorizado (sin activar)

```bash
# Ya creado en: CODE/src/static/js/auth-redirect-v2.js
```

**NO incluir en templates todavía**.

### 1.5. Crear tests de comportamiento

```bash
# Ya creados en: CODE/tests/e2e/
```

**Ejecutar tests contra sistema actual**:
```bash
cd CODE
pytest tests/e2e/test_auth_flows.py -v
```

**Resultado esperado**: Algunos tests pueden fallar (es normal, estamos probando el sistema actual).

**Documentar qué tests fallan**:
```bash
pytest tests/e2e/ -v > tests_fase1_baseline.txt
```

## Fase 2: Refactor Backend

**Duración estimada**: 3 horas

### 2.1. Reemplazar middleware

**Archivo**: `CODE/src/main.py`

**Cambio**:
```python
# ANTES
from src.app.middleware.auth_redirect import AuthRedirectMiddleware
app.add_middleware(AuthRedirectMiddleware, login_url="/auth/login")

# DESPUÉS
from src.app.middleware.auth_middleware_v2 import AuthMiddlewareV2
app.add_middleware(AuthMiddlewareV2, login_url="/auth/login")
```

**Verificar**:
```bash
# Reiniciar servidor
docker-compose restart app

# Verificar que inicia sin errores
docker-compose logs -f app | grep "ERROR"
```

### 2.2. Simplificar endpoint /auth/login

**Archivo**: `CODE/src/app/routes/public.py`

**Cambio**: Eliminar lógica duplicada, mantener solo:
- Verificar si ya está autenticado → redirect
- Limpiar cookies inválidas
- Mostrar mensaje de sesión expirada

**Código simplificado**:
```python
@router.get("/auth/login")
async def login_page(request: Request):
    """Página de login - Simplificada"""
    redirect_url = request.query_params.get("redirect", "/packages")
    
    # Verificar si ya está autenticado
    try:
        context = get_auth_context_from_request(request)
        if context.get("is_authenticated"):
            return RedirectResponse(url=redirect_url, status_code=302)
    except:
        pass
    
    # Verificar si hay token expirado
    access_token = request.cookies.get("access_token")
    show_expired_message = bool(access_token)
    
    # Renderizar login
    response = templates.TemplateResponse("auth/login.html", {
        "request": request,
        "is_authenticated": False,
        "redirect_url": redirect_url,
        "show_session_expired_message": show_expired_message
    })
    
    # Limpiar cookies si hay token expirado
    if access_token:
        response.delete_cookie("access_token")
        response.delete_cookie("user_id")
        response.delete_cookie("user_name")
        response.delete_cookie("user_role")
    
    return response
```

**Verificar**:
```bash
# Test manual
curl -I http://localhost:8000/auth/login
# Debería retornar 200

# Test con token expirado
curl -b "access_token=expired" http://localhost:8000/auth/login | grep "sesión ha expirado"
# Debería mostrar mensaje
```

### 2.3. Ejecutar tests

```bash
cd CODE
pytest tests/e2e/test_auth_flows.py -v
```

**Resultado esperado**: Más tests deberían pasar ahora.

**Si fallan tests**:
1. Revisar logs: `docker-compose logs -f app`
2. Verificar que el middleware está activo
3. Verificar que las rutas públicas están en `routes.py`

## Fase 3: Refactor Frontend

**Duración estimada**: 2 horas

### 3.1. Reemplazar JavaScript

**Archivo**: `CODE/src/templates/base/base.html`

**Cambio**:
```html
<!-- ANTES -->
<script src="/static/js/auth-redirect.js"></script>

<!-- DESPUÉS -->
<script src="/static/js/auth-redirect-v2.js"></script>
```

**Verificar**:
```bash
# Abrir navegador
# Ir a: http://localhost:8000/auth/login
# Abrir consola (F12)
# Debería ver: "🔐 AuthRedirectHandlerV2 inicializado (solo intercepta 401)"
```

### 3.2. Simplificar template de login

**Archivo**: `CODE/src/templates/auth/login.html`

**Eliminar**:
- Verificación de autenticación en JavaScript
- Llamadas a `checkAuthStatus()`
- Uso de `localStorage` para tokens

**Mantener**:
- Formulario de login
- Submit handler
- Mensajes de error

**Código simplificado** (en la sección `{% block extra_scripts %}`):
```javascript
<script>
(function() {
    const loginForm = document.getElementById('loginForm');
    
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const username_or_email = document.getElementById('username_or_email').value;
        const password = document.getElementById('password').value;
        
        // Validaciones...
        
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: new URLSearchParams({username: username_or_email, password})
            });
            
            if (!response.ok) {
                showToast('Error', 'Usuario o contraseña incorrectos', 'error');
                return;
            }
            
            // Redirigir (las cookies se establecen automáticamente)
            const urlParams = new URLSearchParams(window.location.search);
            const redirectUrl = urlParams.get('redirect') || '/packages';
            window.location.href = redirectUrl;
            
        } catch (error) {
            showToast('Error', 'Problema de conexión', 'error');
        }
    });
    
    // Solo focus
    document.addEventListener('DOMContentLoaded', function() {
        document.getElementById('username_or_email')?.focus();
    });
})();
</script>
```

**Verificar**:
```bash
# Test manual
# 1. Ir a http://localhost:8000/auth/login
# 2. Verificar que NO se refresca automáticamente
# 3. Hacer login
# 4. Verificar que funciona
```

### 3.3. Ejecutar tests completos

```bash
cd CODE
pytest tests/e2e/ -v
```

**Resultado esperado**: TODOS los tests deberían pasar.

## Fase 4: Limpieza

**Duración estimada**: 1 hora

### 4.1. Eliminar archivos antiguos

```bash
# Backup primero
cp CODE/src/app/middleware/auth_redirect.py CODE/src/app/middleware/auth_redirect.py.backup
cp CODE/src/static/js/auth-redirect.js CODE/src/static/js/auth-redirect.js.backup

# Eliminar (después de verificar que todo funciona)
rm CODE/src/app/middleware/auth_redirect.py
rm CODE/src/static/js/auth-redirect.js
```

### 4.2. Renombrar archivos v2

```bash
# Middleware
mv CODE/src/app/middleware/auth_middleware_v2.py CODE/src/app/middleware/auth_middleware.py

# JavaScript
mv CODE/src/static/js/auth-redirect-v2.js CODE/src/static/js/auth-redirect.js
```

### 4.3. Actualizar imports

**Archivo**: `CODE/src/main.py`

```python
# Actualizar import
from src.app.middleware.auth_middleware import AuthMiddlewareV2 as AuthMiddleware
app.add_middleware(AuthMiddleware, login_url="/auth/login")
```

### 4.4. Actualizar documentación

```bash
# Actualizar README.md
# Actualizar CHANGELOG.md
# Actualizar comentarios en código
```

### 4.5. Ejecutar tests finales

```bash
cd CODE
pytest tests/ -v --cov=src/app --cov-report=html
```

**Resultado esperado**: 100% de tests pasando.

## Verificación Final

### Checklist

- [ ] Todos los tests E2E pasando
- [ ] Todos los tests de integración pasando
- [ ] No hay errores en logs
- [ ] Login funciona correctamente
- [ ] Auto-redirect funciona
- [ ] Mensaje de sesión expirada funciona
- [ ] AJAX 401 funciona
- [ ] Múltiples pestañas funcionan
- [ ] Rutas públicas accesibles
- [ ] Rutas protegidas requieren auth

### Tests Manuales

1. **Login normal**:
   - Ir a `/admin` sin autenticación
   - Debería redirigir a `/auth/login?redirect=/admin`
   - Hacer login
   - Debería redirigir a `/admin`

2. **Página de login estable**:
   - Ir a `/auth/login`
   - Esperar 5 segundos
   - Página NO debería refrescarse

3. **Auto-redirect**:
   - Hacer login
   - Ir a `/auth/login`
   - Debería redirigir automáticamente a `/packages`

4. **Token expirado**:
   - Establecer cookie con token inválido
   - Ir a `/auth/login`
   - Debería ver mensaje "Tu sesión ha expirado"

5. **AJAX 401**:
   - Estar en página protegida
   - Eliminar cookies
   - Hacer llamada AJAX
   - Debería ver notificación y redirigir

## Rollback

Si algo sale mal, rollback inmediato:

```bash
# Restaurar archivos
cp CODE/src/app/middleware/auth_redirect.py.backup CODE/src/app/middleware/auth_redirect.py
cp CODE/src/static/js/auth-redirect.js.backup CODE/src/static/js/auth-redirect.js

# Revertir cambios en main.py
git checkout CODE/src/main.py

# Reiniciar servidor
docker-compose restart app
```

## Monitoreo Post-Migración

### Primeras 24 horas

- Monitorear logs de errores
- Verificar métricas de login
- Revisar reportes de usuarios

### Primera semana

- Ejecutar tests diariamente
- Revisar performance
- Recopilar feedback

## Conclusión

Después de completar las 4 fases:

- ✅ Sistema refactorizado
- ✅ Responsabilidades claras
- ✅ Tests de comportamiento
- ✅ Sin breaking changes
- ✅ Código mantenible

**Tiempo total estimado**: 8 horas (1 día de desarrollo)
