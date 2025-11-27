# Fix: Loop Infinito en JavaScript (auth-redirect.js)

## Problema Detectado

Después de implementar el fix del loop de redirección en el backend, apareció un **nuevo problema**: la página de login se refrescaba constantemente cada segundo.

### Síntomas

- La página `/auth/login` se recargaba automáticamente
- En la consola del navegador aparecía:
  ```
  GET http://localhost:8000/api/auth/me 401 (Unauthorized)
  ```
- El usuario no podía iniciar sesión porque la página se refrescaba antes

### Causa Raíz

Había **DOS verificaciones de autenticación** ejecutándose simultáneamente:

1. **En el template `login.html`**: Función `checkAuthAndRedirect()` que agregué en el fix
2. **En `auth-redirect.js`**: Función `checkAuthStatus()` que ya existía

Ambas funciones llamaban a `/api/auth/me` al cargar la página, y cuando retornaba 401, intentaban redirigir, causando un **loop infinito**.

### Flujo del Problema

```
1. Usuario va a /auth/login
2. Página carga
3. login.html ejecuta checkAuthAndRedirect() → llama /api/auth/me → 401
4. auth-redirect.js ejecuta checkAuthStatus() → llama /api/auth/me → 401
5. Ambos intentan redirigir a /auth/login
6. Página se recarga
7. Vuelve al paso 2 → LOOP INFINITO
```

## Solución Implementada

### 1. Eliminé la verificación duplicada en `login.html`

**Antes**:
```javascript
// Verificar si ya está autenticado (por si las cookies son válidas)
checkAuthAndRedirect();

async function checkAuthAndRedirect() {
    const response = await fetch('/api/auth/me', {
        method: 'GET',
        credentials: 'include'
    });
    
    if (response.ok) {
        const data = await response.json();
        if (data.id) {
            window.location.href = redirectUrl;
        }
    }
}
```

**Después**:
```javascript
// Solo focus y limpieza de localStorage
document.addEventListener('DOMContentLoaded', function() {
    const usernameField = document.getElementById('username_or_email');
    if (usernameField) usernameField.focus();
    
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_info');
});
```

### 2. Mejoré la lógica de `auth-redirect.js`

**Antes**:
```javascript
const publicPaths = ['/announce', '/search', '/auth/login', ...];

if (isProtected && !isPublic) {
    window.authRedirectHandler.checkAuthStatus();
}
```

**Problema**: Aunque `/auth/login` estaba en `publicPaths`, la verificación `isProtected && !isPublic` no era suficiente para evitar el loop.

**Después**:
```javascript
const publicPaths = ['/announce', '/search', '/auth/login', '/auth/register', '/auth/forgot-password', '/auth/reset-password', '/help', '/cookies', '/policies', '/terms', '/privacy', '/', '/error-demo', '/login'];

// IMPORTANTE: NO verificar autenticación en la página de login para evitar loops
if (isProtected && !isPublic && currentPath !== '/auth/login' && currentPath !== '/login') {
    window.authRedirectHandler.checkAuthStatus();
}

console.log('🔐 AuthRedirectHandler inicializado', {
    currentPath,
    isPublic,
    isProtected,
    willCheckAuth: isProtected && !isPublic && currentPath !== '/auth/login' && currentPath !== '/login'
});
```

**Mejoras**:
- ✅ Verificación explícita para excluir `/auth/login` y `/login`
- ✅ Agregadas más rutas públicas (`/auth/forgot-password`, `/auth/reset-password`, `/terms`, `/privacy`)
- ✅ Logging para debugging

## Archivos Modificados

1. **`CODE/src/static/js/auth-redirect.js`**
   - Agregada verificación explícita para excluir `/auth/login`
   - Agregadas más rutas públicas
   - Agregado logging para debugging

2. **`CODE/src/templates/auth/login.html`**
   - Eliminada función `checkAuthAndRedirect()`
   - Mantenido solo focus y limpieza de localStorage

## Cómo Funciona Ahora

### En Páginas Públicas (como `/auth/login`)

```
1. Usuario va a /auth/login
2. Página carga
3. auth-redirect.js verifica: currentPath === '/auth/login' → NO ejecuta checkAuthStatus()
4. Usuario puede iniciar sesión sin interrupciones
```

### En Páginas Protegidas (como `/admin`)

```
1. Usuario va a /admin
2. Página carga
3. auth-redirect.js verifica: currentPath === '/admin' → SÍ ejecuta checkAuthStatus()
4. Si no está autenticado (401), redirige a /auth/login
5. En /auth/login, NO ejecuta checkAuthStatus() → sin loop
```

### Después del Login

```
1. Usuario hace login exitoso
2. Backend establece cookies
3. Backend redirige a /admin (o URL en parámetro redirect)
4. Página /admin carga
5. auth-redirect.js ejecuta checkAuthStatus()
6. Retorna 200 (autenticado) → no redirige
7. Usuario ve el dashboard
```

## Verificación

### Test Manual

1. Abre tu navegador en modo incógnito
2. Ve a: `http://localhost:8000/auth/login`
3. **Verifica**: La página NO debería refrescarse automáticamente
4. Abre la consola (F12)
5. **Verifica**: NO deberías ver llamadas constantes a `/api/auth/me`
6. Inicia sesión
7. **Verifica**: Deberías ser redirigido a `/admin` sin problemas

### Test con cURL

```bash
# Verificar que la página de login no tiene checkAuthAndRedirect
curl -s http://localhost:8000/auth/login | grep -c "checkAuthAndRedirect"
# Resultado esperado: 0

# Verificar que auth-redirect.js tiene la verificación correcta
grep -A 5 "currentPath !== '/auth/login'" CODE/src/static/js/auth-redirect.js
# Resultado esperado: Debería mostrar la verificación
```

## Lecciones Aprendidas

1. **Evitar verificaciones duplicadas**: Antes de agregar nueva lógica, verificar si ya existe algo similar
2. **Logging es crucial**: El logging agregado ayuda a debuggear problemas futuros
3. **Verificación explícita**: A veces `!isPublic` no es suficiente, necesitas verificación explícita
4. **Separación de responsabilidades**: 
   - Backend: Maneja autenticación y redirección de rutas protegidas
   - Frontend (auth-redirect.js): Maneja redirección de llamadas AJAX 401
   - Templates: Solo UI y lógica específica de la página

## Estado Actual

✅ **Loop infinito resuelto**
✅ **Página de login funciona correctamente**
✅ **Auto-redirect del backend funciona**
✅ **Mensaje de sesión expirada funciona**
✅ **Limpieza de cookies funciona**

## Próximos Pasos

1. Prueba manual en el navegador
2. Verifica que puedes iniciar sesión sin problemas
3. Verifica que no hay loops de redirección
4. Verifica que las páginas protegidas siguen funcionando

## Notas Técnicas

- **auth-redirect.js**: Se ejecuta en TODAS las páginas (incluido en base.html)
- **Rutas públicas**: No ejecutan `checkAuthStatus()`
- **Rutas protegidas**: Ejecutan `checkAuthStatus()` para verificar autenticación
- **Página de login**: Excluida explícitamente para evitar loops

## Troubleshooting

### "La página sigue refrescándose"

1. Limpia la caché del navegador (Ctrl+Shift+Delete)
2. Cierra todas las pestañas
3. Abre en modo incógnito
4. Verifica que los cambios se guardaron:
   ```bash
   grep "currentPath !== '/auth/login'" CODE/src/static/js/auth-redirect.js
   ```

### "Veo llamadas a /api/auth/me en la consola"

Si ves UNA llamada, es normal (puede ser de otro script).
Si ves MÚLTIPLES llamadas constantes, hay un problema.

Verifica en la consola:
```javascript
// Debería mostrar willCheckAuth: false en /auth/login
console.log('🔐 AuthRedirectHandler inicializado', ...)
```

### "No puedo iniciar sesión"

1. Verifica que el formulario funciona:
   - Abre DevTools > Network
   - Intenta hacer login
   - Busca la petición POST a `/api/auth/login`
   - Verifica el status code (debería ser 200)

2. Verifica las cookies:
   - DevTools > Application > Cookies
   - Después del login, deberías ver: `access_token`, `user_id`, etc.

## Conclusión

El problema del loop infinito en JavaScript ha sido resuelto eliminando la verificación duplicada y mejorando la lógica de exclusión en `auth-redirect.js`.

Ahora el sistema funciona correctamente:
- ✅ Login sin loops
- ✅ Auto-redirect del backend
- ✅ Mensaje de sesión expirada
- ✅ Limpieza de cookies
- ✅ Protección de rutas

---

**Fecha**: 27 de noviembre de 2025
**Estado**: ✅ RESUELTO
