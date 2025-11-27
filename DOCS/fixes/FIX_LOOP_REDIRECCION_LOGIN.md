# Fix: Loop de Redirección Infinito en Login

## Problema Original

El usuario experimentaba un **loop de redirección infinito**:
1. Intenta acceder a `/admin`
2. Es redirigido a `/auth/login?redirect=/admin`
3. Aunque aparece autenticado (nombre visible en el header), se muestra el formulario de login
4. Al hacer login, vuelve a `/admin`
5. El ciclo se repite indefinidamente

## Causa Raíz

El problema ocurría porque:

1. **Token expirado**: Las cookies de autenticación tienen una duración de 24 horas. Si el token expiraba, cada petición parecía no autenticada.

2. **Cookies no se limpiaban**: Cuando el token expiraba, las cookies seguían presentes pero inválidas, causando confusión en el sistema.

3. **No había auto-redirect**: La página de login no verificaba si el usuario ya estaba autenticado antes de mostrar el formulario.

4. **Verificación silenciosa**: La función `get_auth_context()` fallaba silenciosamente cuando el token era inválido, sin limpiar las cookies.

## Solución Implementada

### 1. Limpieza de Cookies Inválidas (`public.py`)

```python
@router.get("/auth/login")
async def login_page(request: Request):
    """Página de login - Pública"""
    redirect_url = request.query_params.get("redirect", "/packages")
    
    try:
        context = get_auth_context_from_request(request)
        
        # Si ya está autenticado, redirigir inmediatamente
        if context.get("is_authenticated"):
            logger.info(f"Usuario ya autenticado, redirigiendo a: {redirect_url}")
            return RedirectResponse(url=redirect_url, status_code=302)
        
        # Si hay cookies pero no está autenticado, significa que el token expiró
        # Limpiar cookies inválidas
        access_token = request.cookies.get("access_token")
        if access_token:
            logger.warning("Token expirado o inválido detectado, limpiando cookies")
            response = templates.TemplateResponse("auth/login.html", {
                "request": request,
                "is_authenticated": False,
                "user": None,
                "user_name": None,
                "user_role": None,
                "redirect_url": redirect_url,
                "show_session_expired_message": True  # Mostrar mensaje
            })
            # Limpiar cookies inválidas
            response.delete_cookie("access_token")
            response.delete_cookie("user_id")
            response.delete_cookie("user_name")
            response.delete_cookie("user_role")
            return response
```

**Cambios clave**:
- ✅ Detecta cuando hay cookies pero el token es inválido
- ✅ Limpia las cookies automáticamente
- ✅ Muestra un mensaje al usuario explicando que su sesión expiró
- ✅ Redirige inmediatamente si el usuario ya está autenticado

### 2. Auto-Redirect en el Frontend (`login.html`)

```javascript
// Verificar autenticación y redirigir si ya está logueado
async function checkAuthAndRedirect() {
    try {
        const response = await fetch('/api/auth/me', {
            method: 'GET',
            credentials: 'include'  // Incluir cookies
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.id) {
                // Usuario ya autenticado, redirigir
                const urlParams = new URLSearchParams(window.location.search);
                const redirectUrl = resolveRedirectUrl(urlParams.get('redirect'));
                console.log('Usuario ya autenticado, redirigiendo a:', redirectUrl);
                window.location.href = redirectUrl;
            }
        }
    } catch (error) {
        // Ignorar errores, el usuario no está autenticado
        console.debug('Usuario no autenticado');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // ... código existente ...
    
    // Verificar si ya está autenticado
    checkAuthAndRedirect();
});
```

**Cambios clave**:
- ✅ Verifica automáticamente si el usuario ya está autenticado al cargar la página
- ✅ Redirige inmediatamente si detecta una sesión válida
- ✅ Evita mostrar el formulario de login innecesariamente

### 3. Mensaje de Sesión Expirada

```html
<!-- Mensaje de sesión expirada -->
{% if show_session_expired_message %}
<div class="max-w-md mx-auto mb-6">
    <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-lg">
        <div class="flex">
            <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                </svg>
            </div>
            <div class="ml-3">
                <p class="text-sm text-yellow-700">
                    Tu sesión ha expirado. Por favor, inicia sesión nuevamente.
                </p>
            </div>
        </div>
    </div>
</div>
{% endif %}
```

**Cambios clave**:
- ✅ Informa al usuario por qué debe volver a iniciar sesión
- ✅ Mejora la experiencia de usuario (UX)

## Cómo Probar

### Escenario 1: Token Expirado

1. Inicia sesión normalmente
2. Espera 24 horas (o modifica el `max_age` a 60 segundos para pruebas rápidas)
3. Intenta acceder a `/admin`
4. **Resultado esperado**:
   - Eres redirigido a `/auth/login?redirect=/admin`
   - Ves el mensaje "Tu sesión ha expirado"
   - Las cookies inválidas se limpian automáticamente
   - Puedes iniciar sesión nuevamente sin problemas

### Escenario 2: Ya Autenticado

1. Inicia sesión normalmente
2. Intenta acceder directamente a `/auth/login`
3. **Resultado esperado**:
   - Eres redirigido automáticamente a `/packages` (o a la URL en el parámetro `redirect`)
   - No ves el formulario de login

### Escenario 3: Primera Vez (No Autenticado)

1. Abre el navegador en modo incógnito
2. Intenta acceder a `/admin`
3. **Resultado esperado**:
   - Eres redirigido a `/auth/login?redirect=/admin`
   - Ves el formulario de login (sin mensaje de sesión expirada)
   - Puedes iniciar sesión normalmente
   - Después del login, eres redirigido a `/admin`

## Archivos Modificados

1. **`CODE/src/app/routes/public.py`**
   - Función `login_page()` actualizada
   - Limpieza de cookies inválidas
   - Mensaje de sesión expirada

2. **`CODE/src/templates/auth/login.html`**
   - Función `checkAuthAndRedirect()` agregada
   - Mensaje de sesión expirada en el template
   - Auto-redirect al cargar la página

## Mejoras Futuras

1. **Refresh Token**: Implementar un sistema de refresh tokens para renovar automáticamente la sesión antes de que expire.

2. **Logging Mejorado**: Agregar más logs en `auth_context.py` para diagnosticar problemas de autenticación.

3. **Notificación Proactiva**: Mostrar una notificación al usuario 5 minutos antes de que expire su sesión.

4. **Heartbeat**: Implementar un sistema de "heartbeat" que renueve automáticamente la sesión mientras el usuario esté activo.

## Notas Técnicas

- **Duración del token**: 24 horas (86400 segundos)
- **Cookies utilizadas**: `access_token`, `user_id`, `user_name`, `user_role`
- **Endpoint de verificación**: `/api/auth/me`
- **Middleware**: `AuthRedirectMiddleware` intercepta todas las rutas protegidas

## Verificación

Para verificar que el fix funciona correctamente:

```bash
# 1. Ver logs del servidor
docker-compose logs -f app

# 2. Buscar mensajes como:
# "Usuario ya autenticado, redirigiendo a: /admin"
# "Token expirado o inválido detectado, limpiando cookies"

# 3. Verificar cookies en el navegador (DevTools > Application > Cookies)
# Deben estar presentes: access_token, user_id, user_name, user_role
```

## Conclusión

El fix resuelve el problema del loop de redirección infinito mediante:
1. Limpieza automática de cookies inválidas
2. Auto-redirect cuando el usuario ya está autenticado
3. Mensaje claro cuando la sesión expira
4. Mejor manejo de errores en el flujo de autenticación

El usuario ahora puede:
- ✅ Iniciar sesión sin problemas
- ✅ Ser redirigido correctamente después del login
- ✅ Ver un mensaje claro cuando su sesión expira
- ✅ No quedar atrapado en un loop infinito
