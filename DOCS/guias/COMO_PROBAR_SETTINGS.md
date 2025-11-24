# Cómo Probar la Página /settings

## Problema Actual
La ruta `/settings` requiere autenticación. Si no estás logueado, serás redirigido a `/auth/login`.

## Solución: Opciones para Probar

### Opción 1: Login Normal (Recomendado)

1. **Ir a la página de login**:
   ```
   http://localhost:8000/auth/login
   ```

2. **Iniciar sesión** con tus credenciales

3. **Ir a settings**:
   ```
   http://localhost:8000/settings
   ```

### Opción 2: Usar Endpoint de Desarrollo (Solo para Testing)

Si estás en modo desarrollo, puedes usar el endpoint especial:

```bash
# Establecer cookies de desarrollo
curl -X POST http://localhost:8000/api/auth/dev/set-cookies \
  -H "Content-Type: application/json" \
  -d '{"username":"jesus"}' \
  -c cookies.txt

# Luego acceder a settings con las cookies
curl -b cookies.txt http://localhost:8000/settings
```

### Opción 3: Desde el Navegador

1. Abre las **DevTools** del navegador (F12)
2. Ve a la pestaña **Console**
3. Ejecuta este código:

```javascript
// Establecer cookies de desarrollo
fetch('/api/auth/dev/set-cookies', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username: 'jesus'})
})
.then(r => r.json())
.then(data => {
    console.log('✅ Cookies establecidas:', data);
    // Recargar la página
    window.location.href = '/settings';
});
```

## Verificar que Funciona

Una vez autenticado, deberías ver:

✅ **Página de Configuración** con 4-5 tabs:
- 👤 Mi Cuenta
- 🔐 Seguridad  
- 🔔 Notificaciones
- 👥 Usuarios (solo admin/operador)
- 🎛️ Sistema (solo admin/operador)

## Tabs Disponibles

### Tab: Mi Cuenta (`/settings?tab=account`)
- Editar nombre completo
- Cambiar email
- Actualizar teléfono
- Ver rol

### Tab: Seguridad (`/settings?tab=security`)
- Cambiar contraseña
- Requiere contraseña actual
- Nueva contraseña (mínimo 8 caracteres)

### Tab: Notificaciones (`/settings?tab=notifications`)
- SMS cuando llega paquete
- Email de confirmación
- Notificaciones Push
- Paquete Recibido
- Paquete Entregado
- Mensajes
- Marketing

### Tab: Usuarios (`/settings?tab=users`) - Solo Admin/Operador
- Lista de todos los usuarios
- Crear nuevo usuario
- Editar usuarios existentes
- Activar/desactivar usuarios

### Tab: Sistema (`/settings?tab=system`) - Solo Admin/Operador
- Configuración avanzada (en desarrollo)

## Solución de Problemas

### Error: "No autenticado"
**Causa**: No hay sesión activa
**Solución**: Hacer login primero en `/auth/login`

### Error: "Template not found"
**Causa**: Archivo de template faltante
**Solución**: Verificar que exista `CODE/src/templates/settings/settings.html`

### Error: "unexpected '}'"
**Causa**: Error de sintaxis en el template
**Solución**: Ya corregido en el último commit

### La página se ve pero no funciona
**Causa**: JavaScript no carga o Alpine.js no está disponible
**Solución**: Verificar en DevTools > Console si hay errores

## Endpoints API Relacionados

```bash
# Obtener preferencias de notificaciones
GET /api/settings/notifications

# Actualizar perfil
PUT /api/settings/profile
Body: {"full_name": "...", "email": "...", "phone": "..."}

# Cambiar contraseña
POST /api/settings/change-password
Body: {"current_password": "...", "new_password": "..."}

# Actualizar notificaciones
PUT /api/settings/notifications
Body: {"sms_arrival": true, "email_confirmation": true, ...}
```

## Estado Actual

✅ Template corregido (sin errores de sintaxis)
✅ API endpoints implementados
✅ Protección de autenticación activa
✅ Roles verificados (ADMIN, OPERADOR, CLIENTE)
⚠️ Requiere login para acceder

## Próximos Pasos

1. Hacer login en `/auth/login`
2. Navegar a `/settings`
3. Probar cada tab
4. Verificar que los cambios se guarden correctamente
