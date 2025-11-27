# Diagnóstico: Redirección Constante a Login desde /admin

## Problema
El usuario es redirigido constantemente a `/auth/login?redirect=/admin` cuando intenta acceder al panel de administración.

## Causa Raíz
El middleware `AuthRedirectMiddleware` intercepta todas las peticiones a `/admin` y verifica autenticación mediante cookies. Si la verificación falla, redirige automáticamente al login.

## Razones Comunes

### 1. Token Expirado
- **Duración**: 24 horas (86400 segundos)
- **Verificación**: El token se valida en cada petición
- **Problema**: Si el token expiró, cada acceso genera redirección

### 2. Cookies No Persistentes
- **Cookies requeridas**:
  - `access_token`: Token JWT
  - `user_id`: ID del usuario
  - `user_name`: Nombre de usuario
  - `user_role`: Rol del usuario
- **Configuración actual**:
  ```python
  httponly=True
  secure=False (en development)
  samesite="Lax"
  max_age=86400  # 24 horas
  ```

### 3. Verificación de Token Falla
Posibles causas en `get_user_from_token()`:
- Token mal formado
- Secret key incorrecta
- Problemas de zona horaria (UTC vs Colombia)
- Usuario no existe en BD
- Usuario inactivo

### 4. Middleware Intercepta Todo
El middleware verifica TODAS las rutas excepto las públicas:
```python
public_paths = {
    "/",
    "/announce",
    "/search",
    "/help",
    "/cookies",
    "/policies",
    "/auth/login",
    "/auth/register",
    # ... /admin NO está aquí
}
```

## Soluciones

### Solución 1: Verificar Cookies en el Navegador
1. Abre DevTools (F12)
2. Ve a Application > Cookies
3. Verifica que existan:
   - `access_token`
   - `user_id`
   - `user_name`
   - `user_role`
4. Si no existen o están vacías, el login no funcionó correctamente

### Solución 2: Revisar Logs de Autenticación
Busca en los logs del servidor:
```bash
# Logs de verificación de token
grep "Token verificado" logs/app.log
grep "Token expirado" logs/app.log
grep "Usuario extraído del token" logs/app.log

# Logs de cookies
grep "No se encontró token access_token" logs/app.log
grep "get_user_from_token retornó None" logs/app.log
```

### Solución 3: Hacer Login Nuevamente
1. Ve a `/auth/login`
2. Ingresa credenciales
3. Verifica que el login sea exitoso (status 200)
4. Verifica que las cookies se establezcan
5. Intenta acceder a `/admin` nuevamente

### Solución 4: Aumentar Duración del Token (Temporal)
En `CODE/src/app/routes/auth.py`, línea ~100:
```python
# Cambiar de 86400 (24h) a 604800 (7 días)
response.set_cookie(
    "access_token",
    access_token,
    max_age=604800,  # 7 días
    httponly=True,
    secure=secure_cookie,
    samesite="Lax"
)
```

### Solución 5: Agregar Logging Detallado
Agregar logs en `get_current_user_from_cookies()` para diagnosticar:
```python
logger.debug(f"Cookies recibidas: {list(request.cookies.keys())}")
logger.debug(f"Token length: {len(token) if token else 0}")
logger.debug(f"Token válido: {user_data is not None}")
```

## Verificación Rápida

### Comando para verificar si estás autenticado:
```bash
curl -v http://localhost:8000/api/auth/me \
  -H "Cookie: access_token=TU_TOKEN_AQUI"
```

### Respuesta esperada si estás autenticado:
```json
{
  "id": "1",
  "username": "admin",
  "email": "admin@example.com",
  "role": "admin",
  "is_active": true
}
```

### Respuesta si NO estás autenticado:
```json
{
  "detail": "No autenticado"
}
```

## Próximos Pasos

1. **Verificar cookies en el navegador** (DevTools > Application > Cookies)
2. **Revisar logs del servidor** para ver qué está fallando
3. **Hacer login nuevamente** y verificar que las cookies se establezcan
4. **Si el problema persiste**, agregar logging detallado en `dependencies.py`

## Archivos Relevantes

- `CODE/src/app/middleware/auth_redirect.py` - Middleware de redirección
- `CODE/src/app/dependencies.py` - Verificación de autenticación
- `CODE/src/app/routes/auth.py` - Endpoint de login
- `CODE/src/app/utils/auth.py` - Utilidades de JWT
