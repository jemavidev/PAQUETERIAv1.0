# Solución: Redirección al Dashboard después de OTP

**Fecha**: 2025-02-07  
**Problema**: Después de verificar el OTP, el cliente era redirigido a `/auth/login` en lugar de acceder al dashboard

## Diagnóstico del Problema

### Síntoma
Después de ingresar la contraseña temporal (OTP) correctamente en `/customer/verify`, el usuario era redirigido a:
```
https://staging.jemavi.co/auth/login?redirect=%2Fapi%2Fcustomer-portal%2Fpreferences%2Fnotifications
```

### Causa Raíz
El dashboard (`/customer-portal/dashboard`) verifica si existe un token JWT en `localStorage` al cargar:

```javascript
async init() {
    const token = localStorage.getItem('customer_token');
    if (!token) {
        window.location.href = '/customer-portal';  // ← Redirige si no hay token
        return;
    }
    // ...
}
```

El problema era que el token se estaba guardando pero había un problema de **timing** o **sincronización** entre:
1. Guardar el token en localStorage
2. Redirigir al dashboard
3. El dashboard verificar el token

## Solución Implementada

### 1. Mejora en el Guardado del Token (`verify.html`)

**Antes:**
```javascript
// Guardar token JWT en localStorage
localStorage.setItem('customer_token', data.access_token);

// Redirigir al dashboard
setTimeout(() => {
    window.location.href = data.redirect_url;
}, 1500);
```

**Después:**
```javascript
// Detener countdown primero
if (countdownInterval) {
    clearInterval(countdownInterval);
}

// Guardar token JWT en localStorage de forma síncrona
try {
    localStorage.setItem('customer_token', data.access_token);
    
    // Verificar que el token se guardó correctamente
    const savedToken = localStorage.getItem('customer_token');
    console.log('🔑 Token guardado:', savedToken ? 'Sí' : 'No');
    console.log('🔑 Token length:', savedToken ? savedToken.length : 0);
    
    if (!savedToken) {
        throw new Error('No se pudo guardar el token');
    }
    
    // Redirigir usando replace (evita problemas de caché)
    setTimeout(() => {
        window.location.replace(data.redirect_url);
    }, 1500);
    
} catch (storageError) {
    console.error('❌ Error al guardar token:', storageError);
    // Mostrar mensaje de error al usuario
}
```

**Mejoras:**
- ✅ Detiene el countdown antes de guardar el token
- ✅ Usa `try-catch` para manejar errores de localStorage
- ✅ Verifica que el token se guardó correctamente antes de redirigir
- ✅ Usa `window.location.replace()` en lugar de `href` (evita caché)
- ✅ Logs de debugging para facilitar diagnóstico
- ✅ Manejo de errores con feedback al usuario

### 2. Configuración de Rutas Públicas

Se agregó la ruta de preferencias a las APIs públicas:

```python
# CODE/src/app/config_routes.py
API_PUBLIC_ROUTES: Set[str] = {
    # ...
    "/api/customer-portal/me",
    "/api/customer-portal/packages",
    "/api/customer-portal/preferences/notifications",  # ← Agregado
    "/api/customer-portal/logout",
    # ...
}
```

### 3. Verificación del Token JWT

El token generado por `/api/customer/preferences-otp/verify` tiene la estructura correcta:

```python
to_encode = {
    "customer_id": str(customer.id),
    "phone": phone,
    "exp": expire,
    "type": "customer_portal"  # ← Requerido por verify_token()
}
```

El servicio `CustomerPortalService.verify_token()` verifica:
- ✅ Que el token sea válido (firma JWT)
- ✅ Que tenga `type: "customer_portal"`
- ✅ Que contenga `customer_id` y `phone`

## Flujo Completo Corregido

```
1. Cliente ingresa teléfono en /customer/verify
   ↓
2. Backend envía SMS con contraseña temporal (6 dígitos)
   ↓
3. Cliente ingresa contraseña temporal
   ↓
4. Backend verifica contraseña y genera token JWT
   ↓
5. Frontend guarda token en localStorage (con verificación)
   ↓
6. Frontend redirige a /customer-portal/dashboard
   ↓
7. Dashboard verifica token en localStorage
   ↓
8. Dashboard carga datos del cliente usando el token JWT
   ↓
9. Cliente accede a sus datos, paquetes y preferencias
```

## Rutas Involucradas

### Rutas HTML (Públicas)
- `/customer/verify` - Solicitar y verificar OTP
- `/customer-portal/dashboard` - Dashboard del cliente

### APIs Públicas (Requieren Token JWT)
- `/api/customer/preferences-otp/request` - Solicitar OTP
- `/api/customer/preferences-otp/verify` - Verificar OTP y obtener token
- `/api/customer-portal/me` - Obtener datos del cliente
- `/api/customer-portal/packages` - Obtener historial de paquetes
- `/api/customer-portal/preferences/notifications` - Obtener/actualizar preferencias

## Testing

### Script de Prueba
Se creó `CODE/test_otp_flow_complete.py` para probar el flujo completo:

```bash
python CODE/test_otp_flow_complete.py
```

El script prueba:
1. ✅ Solicitar OTP
2. ✅ Verificar OTP
3. ✅ Obtener datos del cliente con token
4. ✅ Obtener historial de paquetes
5. ✅ Obtener preferencias

### Prueba Manual en Navegador

1. Abrir: `https://staging.jemavi.co/customer/verify`
2. Ingresar teléfono registrado
3. Recibir SMS con contraseña temporal
4. Ingresar contraseña temporal
5. Verificar que se redirige a `/customer-portal/dashboard`
6. Verificar que se cargan los datos correctamente

### Verificar Token en Consola del Navegador

```javascript
// Ver token guardado
console.log(localStorage.getItem('customer_token'));

// Verificar longitud (debe ser ~200+ caracteres)
console.log(localStorage.getItem('customer_token').length);

// Decodificar token (solo para debugging)
const token = localStorage.getItem('customer_token');
const payload = JSON.parse(atob(token.split('.')[1]));
console.log(payload);
// Debe mostrar: { customer_id, phone, exp, type: "customer_portal" }
```

## Posibles Problemas y Soluciones

### Problema 1: Token no se guarda
**Síntoma**: Console muestra "Token guardado: No"  
**Causa**: localStorage bloqueado (modo incógnito, configuración del navegador)  
**Solución**: Usar navegador normal, verificar configuración de cookies/storage

### Problema 2: Token se guarda pero dashboard redirige
**Síntoma**: Token existe pero dashboard redirige a `/customer-portal`  
**Causa**: Token inválido o expirado  
**Solución**: Verificar estructura del token en consola, regenerar OTP

### Problema 3: APIs retornan 401 Unauthorized
**Síntoma**: Dashboard carga pero no muestra datos  
**Causa**: Token no se está enviando en headers o es inválido  
**Solución**: Verificar en Network tab que el header `Authorization: Bearer {token}` se envía

### Problema 4: CORS errors
**Síntoma**: Errores de CORS en consola  
**Causa**: Configuración de CORS en backend  
**Solución**: Verificar que el dominio esté en la lista de orígenes permitidos

## Archivos Modificados

1. ✅ `CODE/src/templates/customer/verify.html` - Mejorado guardado de token
2. ✅ `CODE/src/app/config_routes.py` - Agregada ruta de preferencias
3. ✅ `CODE/test_otp_flow_complete.py` - Script de prueba (nuevo)
4. ✅ `CODE/SOLUCION_REDIRECCION_DASHBOARD.md` - Documentación (este archivo)

## Próximos Pasos

1. ✅ Probar en staging con teléfono real
2. ✅ Verificar que todos los tabs del dashboard funcionen
3. ✅ Probar edición de datos personales
4. ✅ Probar actualización de preferencias
5. ✅ Verificar que el logout funcione correctamente
6. ✅ Probar en diferentes navegadores (Chrome, Firefox, Safari)
7. ✅ Probar en móvil (iOS y Android)

## Notas de Seguridad

- ✅ Token JWT válido por 1 hora (configurable)
- ✅ Token incluye `customer_id` y `phone` para validación
- ✅ Token tiene tipo específico `customer_portal` para evitar confusión con otros tokens
- ✅ OTP válido por 5 minutos
- ✅ Máximo 3 intentos por OTP
- ✅ OTPs anteriores se invalidan al solicitar uno nuevo
- ✅ Token se guarda solo en localStorage (no en cookies)
- ✅ APIs verifican token en cada petición
