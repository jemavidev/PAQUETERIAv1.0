# Lista de Pruebas Pre-Producción

## Resumen de Cambios Realizados

### 1. Sistema de Preferencias de Notificaciones
- ✅ Guardado y lectura de preferencias
- ✅ Verificación de preferencias antes de enviar SMS/Email
- ✅ Logging detallado para diagnóstico

### 2. Corrección de Redirecciones 401
- ✅ Clientes → `/customer/verify`
- ✅ Administradores → `/auth/login`

### 3. Página de Anuncios Pública
- ✅ Usa endpoint público `/api/announcements/direct`

### 4. Gestión de Preferencias desde Admin
- ✅ Modal de preferencias en `/customers/manage`
- ✅ Sin errores de consola

---

## PRUEBAS OBLIGATORIAS

### PRUEBA 1: Portal de Clientes - Acceso con OTP ⭐ CRÍTICO

**Objetivo:** Verificar que los clientes pueden acceder al portal

**Pasos:**
1. Ir a: https://staging.jemavi.co/customer/verify
2. Ingresar teléfono: `3002596319`
3. Click en "Solicitar Contraseña Temporal"
4. Verificar que llega SMS ✅
5. Verificar que llega Email ✅
6. Ingresar el código OTP
7. Click en "Acceder a mi Portal"
8. Verificar que redirige a `/customer-portal/dashboard` ✅

**Resultado Esperado:**
- ✅ SMS recibido
- ✅ Email recibido
- ✅ Acceso exitoso al dashboard
- ✅ Se muestran los datos del cliente

---

### PRUEBA 2: Preferencias de Notificaciones - Cliente ⭐ CRÍTICO

**Objetivo:** Verificar que las preferencias se guardan y respetan

**Pasos:**
1. Acceder al portal (usar PRUEBA 1)
2. Ir a tab "Preferencias"
3. **Desactivar** ambos switches (SMS y Email)
4. Click en "Guardar"
5. Verificar mensaje de éxito ✅
6. Recargar la página (F5)
7. Verificar que los switches siguen desactivados ✅
8. Ir a tab "Mis Datos"
9. Volver a tab "Preferencias"
10. Verificar que los switches siguen desactivados ✅

**Resultado Esperado:**
- ✅ Preferencias se guardan correctamente
- ✅ Preferencias persisten después de recargar
- ✅ No hay errores en consola

---

### PRUEBA 3: Bloqueo de Notificaciones ⭐ CRÍTICO

**Objetivo:** Verificar que las notificaciones se bloquean según preferencias

**Requisito:** Tener preferencias desactivadas (PRUEBA 2)

**Pasos:**
1. Desde el dashboard administrativo
2. Buscar un paquete del cliente (tel: 3002596319)
3. Cambiar el estado del paquete:
   - Si está ANUNCIADO → cambiar a RECIBIDO
   - Si está RECIBIDO → cambiar a ENTREGADO
4. Verificar que NO llega SMS ✅
5. Verificar que NO llega Email ✅

**Verificación en Logs:**
```bash
ssh staging
docker logs -f paquetes-backend-1 | grep -E "preferencias|bloqueado"
```

**Logs Esperados:**
```
🔍 Verificando preferencias para customer_id: <UUID>
📋 Preferencias encontradas para cliente <UUID>
   SMS habilitado: False
   Evento: package_received
   ¿Debe enviar?: False
📵 SMS bloqueado por preferencias del cliente
```

**Resultado Esperado:**
- ✅ NO se recibe SMS
- ✅ NO se recibe Email
- ✅ Logs muestran "bloqueado por preferencias"

---

### PRUEBA 4: Reactivar Notificaciones ⭐ CRÍTICO

**Objetivo:** Verificar que al reactivar preferencias, las notificaciones vuelven a llegar

**Pasos:**
1. Acceder al portal del cliente
2. Ir a "Preferencias"
3. **Activar** ambos switches (SMS y Email)
4. Click en "Guardar"
5. Cambiar el estado de otro paquete del cliente
6. Verificar que SÍ llega SMS ✅
7. Verificar que SÍ llega Email ✅

**Resultado Esperado:**
- ✅ SMS recibido
- ✅ Email recibido
- ✅ Logs muestran "permitido por preferencias"

---

### PRUEBA 5: Token Expirado - Cliente

**Objetivo:** Verificar redirección correcta cuando expira el token

**Pasos:**
1. Acceder al portal del cliente
2. Esperar 1 hora (o modificar token en localStorage para que expire)
3. Intentar cambiar algo en "Mis Datos" o "Preferencias"
4. Verificar que aparece mensaje: "Tu sesión ha expirado" ✅
5. Verificar que redirige a `/customer/verify` ✅
6. Verificar que NO redirige a `/auth/login` ✅

**Resultado Esperado:**
- ✅ Mensaje de sesión expirada
- ✅ Redirige a `/customer/verify`
- ❌ NO redirige a `/auth/login`

---

### PRUEBA 6: Página de Anuncios Pública

**Objetivo:** Verificar que la página de anuncios funciona sin autenticación

**Pasos:**
1. Abrir navegador en modo incógnito
2. Ir a: https://staging.jemavi.co/announce
3. Llenar el formulario:
   - Nombre: "Test Cliente"
   - Teléfono: "3001234567"
   - Número de guía: "TEST123456"
4. Aceptar términos
5. Click en "Anunciar"
6. Verificar que se crea el anuncio ✅
7. Verificar que NO redirige a `/auth/login` ✅

**Resultado Esperado:**
- ✅ Formulario funciona sin login
- ✅ Anuncio se crea exitosamente
- ✅ No hay errores en consola

---

### PRUEBA 7: Gestión de Preferencias desde Admin

**Objetivo:** Verificar que los administradores pueden gestionar preferencias de clientes

**Pasos:**
1. Login como administrador
2. Ir a: https://staging.jemavi.co/customers/manage
3. Buscar cliente: "JESUS VILLALOBOS"
4. Click en botón morado (🔔) "Gestionar Preferencias"
5. Verificar que abre el modal ✅
6. Verificar que NO hay errores en consola ✅
7. Verificar que muestra el link de verificación ✅
8. Click en "Copiar" link
9. Verificar que se copia correctamente ✅
10. Cerrar modal

**Resultado Esperado:**
- ✅ Modal abre sin errores
- ✅ No hay errores 403 en consola
- ✅ Link se copia correctamente
- ✅ No hay errores de Alpine.js

---

### PRUEBA 8: OTP NO Respeta Preferencias ⭐ IMPORTANTE

**Objetivo:** Confirmar que los OTPs de autenticación SIEMPRE se envían

**Pasos:**
1. Tener preferencias desactivadas (PRUEBA 2)
2. Cerrar sesión del portal
3. Ir a `/customer/verify`
4. Solicitar nuevo OTP
5. Verificar que SÍ llega SMS ✅
6. Verificar que SÍ llega Email ✅

**Resultado Esperado:**
- ✅ SMS de OTP llega (aunque preferencias estén desactivadas)
- ✅ Email de OTP llega (aunque preferencias estén desactivadas)
- ✅ Esto es CORRECTO por seguridad

---

### PRUEBA 9: Verificación de Base de Datos

**Objetivo:** Confirmar que las preferencias se guardan en BD

**Pasos:**
```bash
ssh staging
docker exec -it paquetes-db-1 psql -U postgres -d paquetes_db

-- Verificar preferencias del cliente de prueba
SELECT 
    c.id,
    c.full_name,
    c.phone,
    cp.sms_notifications_enabled,
    cp.email_notifications_enabled,
    cp.notify_package_received,
    cp.notify_package_delivered,
    cp.updated_at
FROM customers c
LEFT JOIN customer_preferences cp ON c.id = cp.customer_id
WHERE c.phone = '573002596319';

-- Verificar notificaciones bloqueadas
SELECT 
    id,
    notification_type,
    event_type,
    status,
    error_message,
    created_at
FROM notifications
WHERE status = 'blocked'
ORDER BY created_at DESC
LIMIT 5;
```

**Resultado Esperado:**
- ✅ Cliente tiene registro en `customer_preferences`
- ✅ Valores de preferencias coinciden con lo configurado
- ✅ Hay registros con `status = 'blocked'` cuando se probó con preferencias desactivadas

---

### PRUEBA 10: Logs del Servidor

**Objetivo:** Verificar que el logging funciona correctamente

**Pasos:**
```bash
ssh staging
docker logs -f paquetes-backend-1 | grep -E "SMS|EMAIL|preferencias|bloqueado"
```

**Realizar acciones:**
1. Solicitar OTP
2. Cambiar estado de paquete con preferencias desactivadas
3. Cambiar estado de paquete con preferencias activadas

**Logs Esperados:**
```
# Al solicitar OTP (siempre se envía)
✅ Contraseña temporal enviada por SMS
✅ Contraseña temporal también enviada por Email

# Con preferencias desactivadas
🔍 Verificando preferencias para customer_id: <UUID>
📋 Preferencias encontradas
   SMS habilitado: False
📵 SMS bloqueado por preferencias

# Con preferencias activadas
🔍 Verificando preferencias para customer_id: <UUID>
📋 Preferencias encontradas
   SMS habilitado: True
✅ SMS permitido por preferencias
```

---

## CHECKLIST FINAL PRE-PRODUCCIÓN

Antes de desplegar a producción, confirmar:

### Funcionalidad
- [ ] PRUEBA 1: Acceso con OTP funciona
- [ ] PRUEBA 2: Preferencias se guardan
- [ ] PRUEBA 3: Notificaciones se bloquean
- [ ] PRUEBA 4: Notificaciones se reactivan
- [ ] PRUEBA 5: Redirección 401 correcta
- [ ] PRUEBA 6: Página de anuncios funciona
- [ ] PRUEBA 7: Modal de admin funciona
- [ ] PRUEBA 8: OTP siempre se envía
- [ ] PRUEBA 9: BD tiene datos correctos
- [ ] PRUEBA 10: Logs funcionan

### Errores de Consola
- [ ] No hay errores en `/customer/verify`
- [ ] No hay errores en `/customer-portal/dashboard`
- [ ] No hay errores en `/announce`
- [ ] No hay errores en `/customers/manage`

### Base de Datos
- [ ] Tabla `customer_preferences` existe
- [ ] Clientes tienen preferencias creadas
- [ ] Notificaciones bloqueadas se registran

### Seguridad
- [ ] OTPs de autenticación SIEMPRE se envían
- [ ] Preferencias solo afectan notificaciones de paquetes
- [ ] Clientes solo ven sus propios datos
- [ ] Redirecciones 401 son correctas

---

## ARCHIVOS MODIFICADOS (Para Revisión)

### Backend
1. `CODE/src/main.py` - Manejador de excepciones 401
2. `CODE/src/app/services/sms_service.py` - Logging de preferencias
3. `CODE/src/app/services/email_service.py` - Logging de preferencias
4. `CODE/src/app/routes/customer_preferences_otp.py` - OTP sin verificar preferencias

### Frontend
5. `CODE/src/templates/announce/announce.html` - Ruta pública
6. `CODE/src/templates/customer_portal/dashboard.html` - Manejo de 401
7. `CODE/src/templates/customers/manage.html` - Modal de preferencias

---

## COMANDOS ÚTILES PARA PRUEBAS

### Ver logs en tiempo real
```bash
ssh staging
docker logs -f paquetes-backend-1 | grep -E "preferencias|bloqueado|SMS|EMAIL"
```

### Verificar preferencias en BD
```bash
docker exec -it paquetes-db-1 psql -U postgres -d paquetes_db -c "
SELECT c.full_name, c.phone, cp.sms_notifications_enabled, cp.email_notifications_enabled 
FROM customers c 
LEFT JOIN customer_preferences cp ON c.id = cp.customer_id 
WHERE c.phone = '573002596319';
"
```

### Ver notificaciones bloqueadas
```bash
docker exec -it paquetes-db-1 psql -U postgres -d paquetes_db -c "
SELECT notification_type, event_type, status, error_message, created_at 
FROM notifications 
WHERE status = 'blocked' 
ORDER BY created_at DESC 
LIMIT 10;
"
```

---

## ROLLBACK (Si algo falla)

Si encuentras problemas en producción:

```bash
# 1. Volver a la versión anterior
git log --oneline -10  # Ver últimos commits
git revert <commit-hash>  # Revertir cambios
git push

# 2. En el servidor
ssh production
git pull
docker-compose restart backend

# 3. Verificar que funciona
curl https://production.jemavi.co/health
```

---

## CONTACTO PARA SOPORTE

Si algo falla después del despliegue:
1. Revisar logs: `docker logs paquetes-backend-1`
2. Verificar BD: Consultas SQL arriba
3. Revisar errores de consola del navegador
4. Contactar con los detalles específicos del error

---

**IMPORTANTE:** Realiza TODAS las pruebas en staging antes de desplegar a producción.
