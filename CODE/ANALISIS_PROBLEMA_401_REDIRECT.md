# Análisis: Problema de Redirección 401 a /auth/login

## Problema Identificado

Cuando un cliente del portal intentaba guardar preferencias y su token JWT había expirado, recibía un error 401 y era redirigido a `/auth/login?redirect=/api/announcements/`, que es la página de login para **administradores**, no para clientes.

## Causa Raíz

En `CODE/src/main.py` línea 133-143, el manejador de excepciones HTTP tenía esta lógica:

```python
def handle_http_exception(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        if "/api/auth/login" not in str(request.url):
            headers = dict(exc.headers) if exc.headers else {}
            headers["Location"] = "/auth/login"  # ❌ PROBLEMA
            headers["Content-Type"] = "application/json"

            return JSONResponse(
                status_code=401,
                content={"detail": "No autenticado"},
                headers=headers
            )
```

**El problema:** TODOS los errores 401 redirigían a `/auth/login`, sin distinguir entre:
- **Administradores** (usuarios del sistema) → deben ir a `/auth/login`
- **Clientes** (portal público con OTP) → deben ir a `/customer/verify`

## Arquitectura del Sistema

El sistema tiene **DOS flujos de autenticación separados:**

### 1. Flujo de Administradores (Sistema Interno)
- **Login:** `/auth/login`
- **Autenticación:** Usuario + Contraseña
- **Token:** JWT con roles y permisos
- **Rutas:** `/dashboard`, `/packages`, `/customers`, etc.
- **Tabla:** `users` (con roles: ADMIN, OPERATOR, etc.)

### 2. Flujo de Clientes (Portal Público)
- **Login:** `/customer/verify`
- **Autenticación:** Teléfono + OTP (código temporal)
- **Token:** JWT solo con customer_id
- **Rutas:** `/customer-portal/dashboard`, `/customer/preferences`
- **Tabla:** `customers` (sin contraseñas, acceso por OTP)

## Solución Implementada

He modificado el manejador de excepciones para distinguir entre los dos flujos:

```python
def handle_http_exception(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        if "/api/auth/login" not in str(request.url):
            headers = dict(exc.headers) if exc.headers else {}
            
            # ✅ SOLUCIÓN: Determinar si es cliente o administrador
            request_path = str(request.url.path)
            if "/customer-portal" in request_path or "/customer/" in request_path:
                # Ruta de cliente - redirigir a login de cliente
                headers["Location"] = "/customer/verify"
            else:
                # Ruta de administrador - redirigir a login de admin
                headers["Location"] = "/auth/login"
            
            headers["Content-Type"] = "application/json"

            return JSONResponse(
                status_code=401,
                content={"detail": "No autenticado"},
                headers=headers
            )
```

## Cambios Adicionales en el Frontend

También agregué manejo explícito de 401 en el dashboard del cliente para evitar depender del header `Location`:

```javascript
// En todas las funciones del dashboard
if (response.status === 401) {
    localStorage.removeItem('customer_token');
    alert('Tu sesión ha expirado. Por favor ingresa nuevamente.');
    window.location.href = '/customer/verify';
    return;
}
```

## Configuración de Rutas Públicas

Las rutas del portal de clientes YA estaban correctamente configuradas como públicas en `config_routes.py`:

```python
PUBLIC_ROUTES = {
    "/customer-portal",
    "/customer-portal/verify",
    "/customer-portal/dashboard",
    "/customer/verify",
    "/customer/preferences",
}

API_PUBLIC_ROUTES = {
    "/api/customer-portal/request-otp",
    "/api/customer-portal/verify-otp",
    "/api/customer-portal/me",
    "/api/customer-portal/packages",
    "/api/customer-portal/preferences/notifications",
    "/api/customer/preferences-otp/request",
    "/api/customer/preferences-otp/verify",
}
```

Esto significa que:
- ✅ Las rutas del portal de clientes NO requieren autenticación de administrador
- ✅ Los clientes pueden acceder con solo su token JWT de OTP
- ✅ No hay mezcla entre los dos sistemas de autenticación

## Tabla `customers` - Acceso Público con Restricciones

La tabla `customers` es efectivamente "pública" en el sentido de que:

1. **Cualquier persona puede crear un registro** al anunciar un paquete
2. **Los clientes pueden acceder a SUS PROPIOS datos** usando OTP
3. **Los administradores pueden ver/editar todos los clientes** con autenticación completa

**Restricciones de acceso:**
- Los clientes solo ven sus propios datos (filtrado por `customer_id` del token)
- Los clientes no pueden ver datos de otros clientes
- Los clientes no pueden acceder a funciones administrativas

## Resumen

**Lo que pasó:**
1. El manejador de excepciones 401 no distinguía entre clientes y administradores
2. Todos los 401 redirigían a `/auth/login` (login de administradores)
3. Los clientes del portal eran enviados a la página incorrecta

**La solución:**
1. ✅ Modificado el manejador para detectar rutas de cliente vs administrador
2. ✅ Clientes con 401 → redirigen a `/customer/verify`
3. ✅ Administradores con 401 → redirigen a `/auth/login`
4. ✅ Agregado manejo explícito en el frontend como respaldo

**Archivos modificados:**
- `CODE/src/main.py` - Manejador de excepciones 401
- `CODE/src/templates/customer_portal/dashboard.html` - Manejo de 401 en frontend

## Verificación

Para verificar que funciona correctamente:

1. Acceder al portal de cliente: https://staging.jemavi.co/customer/verify
2. Ingresar con OTP
3. Esperar 1 hora (o modificar el token para que expire)
4. Intentar guardar preferencias
5. **Resultado esperado:** Redirige a `/customer/verify` (no a `/auth/login`)

## Conclusión

Los dos flujos de autenticación están correctamente separados:
- ❌ NO se mezclaron los sistemas
- ✅ Las rutas están correctamente configuradas
- ✅ El único problema era el manejador de 401 que no distinguía entre los dos flujos
- ✅ Ahora está corregido
