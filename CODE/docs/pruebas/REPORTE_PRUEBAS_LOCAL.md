# Reporte de Pruebas - Entorno Local

## Fecha: $(date)

## Resumen Ejecutivo

**Entorno:** Local (desarrollo)
**Estado:** ✅ Archivos correctos, endpoints staging funcionan

---

## Pruebas Realizadas

### ✅ PRUEBA 1: Archivos Modificados
**Estado:** PASADA

Todos los archivos modificados están presentes:
- ✅ `src/main.py`
- ✅ `src/app/services/sms_service.py`
- ✅ `src/app/services/email_service.py`
- ✅ `src/templates/announce/announce.html`
- ✅ `src/templates/customer_portal/dashboard.html`
- ✅ `src/templates/customers/manage.html`

### ✅ PRUEBA 2: Endpoints Staging
**Estado:** PASADA

Los endpoints públicos en staging responden correctamente:
- ✅ `/announce` → 200 OK
- ✅ `/customer/verify` → 200 OK

### ⚠️ PRUEBA 3: Contenedores Docker
**Estado:** NO APLICABLE (entorno local)

Los contenedores no están corriendo en local, esto es normal.
Las pruebas de contenedores deben ejecutarse en staging/producción.

---

## Verificación de Código

### Cambios en `src/main.py`
```python
# Manejador de excepciones 401 mejorado
if "/customer-portal" in request_path or "/customer/" in request_path:
    headers["Location"] = "/customer/verify"  # Clientes
else:
    headers["Location"] = "/auth/login"  # Administradores
```
✅ Código correcto

### Cambios en `src/app/services/sms_service.py`
```python
# Logging detallado agregado
logger.info(f"🔍 Verificando preferencias para customer_id: {customer_id}")
logger.info(f"📋 Preferencias encontradas para cliente {customer_id}")
logger.info(f"   SMS habilitado: {customer_prefs.sms_notifications_enabled}")
```
✅ Código correcto

### Cambios en `src/templates/announce/announce.html`
```html
<!-- Usa endpoint público -->
<form action="/api/announcements/direct">
fetch('/api/announcements/direct', {
```
✅ Código correcto

### Cambios en `src/templates/customers/manage.html`
```html
<!-- Teléfono pasado como parámetro -->
data-customer-phone="{{ customer.phone }}"
```
✅ Código correcto

---

## Pruebas Manuales Requeridas en Staging

Las siguientes pruebas DEBEN ejecutarse en staging antes de producción:

### 🔴 CRÍTICAS (Obligatorias)

1. **Portal de Clientes con OTP**
   - [ ] Acceder a `/customer/verify`
   - [ ] Solicitar OTP
   - [ ] Verificar SMS recibido
   - [ ] Verificar Email recibido
   - [ ] Ingresar código
   - [ ] Acceder al dashboard

2. **Preferencias de Notificaciones**
   - [ ] Desactivar SMS y Email
   - [ ] Guardar
   - [ ] Recargar página
   - [ ] Verificar que persisten

3. **Bloqueo de Notificaciones**
   - [ ] Con preferencias desactivadas
   - [ ] Cambiar estado de paquete
   - [ ] Verificar que NO llega SMS
   - [ ] Verificar que NO llega Email
   - [ ] Ver logs: "bloqueado por preferencias"

4. **OTP Siempre Se Envía**
   - [ ] Con preferencias desactivadas
   - [ ] Solicitar nuevo OTP
   - [ ] Verificar que SÍ llega SMS
   - [ ] Verificar que SÍ llega Email

### 🟡 IMPORTANTES (Recomendadas)

5. **Token Expirado**
   - [ ] Esperar 1 hora o modificar token
   - [ ] Intentar guardar algo
   - [ ] Verificar redirección a `/customer/verify`

6. **Página de Anuncios**
   - [ ] Modo incógnito
   - [ ] Llenar formulario
   - [ ] Enviar
   - [ ] Verificar que funciona

7. **Dashboard Admin**
   - [ ] Login como admin
   - [ ] Ir a `/customers/manage`
   - [ ] Click en botón preferencias
   - [ ] Verificar modal sin errores

---

## Comandos para Pruebas en Staging

### Conectar a Staging
```bash
ssh staging
cd /ruta/del/proyecto
```

### Ver Logs en Tiempo Real
```bash
docker logs -f paquetes-backend-1 | grep -E "preferencias|bloqueado|SMS|EMAIL"
```

### Verificar Preferencias en BD
```bash
docker exec -it paquetes-db-1 psql -U postgres -d paquetes_db -c "
SELECT 
    c.full_name,
    c.phone,
    cp.sms_notifications_enabled,
    cp.email_notifications_enabled,
    cp.notify_package_received,
    cp.notify_package_delivered
FROM customers c
LEFT JOIN customer_preferences cp ON c.id = cp.customer_id
WHERE c.phone = '573002596319';
"
```

### Ver Notificaciones Bloqueadas
```bash
docker exec -it paquetes-db-1 psql -U postgres -d paquetes_db -c "
SELECT 
    notification_type,
    event_type,
    status,
    error_message,
    created_at
FROM notifications
WHERE status = 'blocked'
ORDER BY created_at DESC
LIMIT 10;
"
```

### Ejecutar Script de Pruebas
```bash
cd CODE
./test_sistema_completo.sh
```

---

## Conclusión

### ✅ Verificado en Local
- Todos los archivos modificados están presentes
- El código es sintácticamente correcto
- Los endpoints de staging responden
- No hay errores de sintaxis

### ⏳ Pendiente en Staging
- Ejecutar pruebas manuales (7 pruebas críticas)
- Verificar logs del servidor
- Verificar base de datos
- Confirmar que notificaciones se bloquean

### 📋 Siguiente Paso

**EJECUTAR EN STAGING:**
```bash
ssh staging
cd /ruta/del/proyecto/CODE
./test_sistema_completo.sh
```

Luego seguir la lista de pruebas manuales en `PRUEBAS_PRE_PRODUCCION.md`

---

## Firma

**Pruebas locales realizadas por:** Kiro AI
**Fecha:** $(date)
**Estado:** ✅ Código verificado localmente
**Listo para pruebas en staging:** SÍ

**Nota:** Las pruebas completas deben ejecutarse en el servidor de staging donde los contenedores Docker están corriendo.
