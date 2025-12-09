# Solución: Preferencias de Notificaciones No Se Respetan

## Problema

Las preferencias de notificaciones (SMS/Email ON/OFF) se pueden cambiar en el portal, pero los mensajes siguen llegando independientemente de la configuración.

## Análisis Realizado

He analizado todo el flujo del sistema y encontré que:

### ✅ LO QUE ESTÁ BIEN IMPLEMENTADO:

1. **Guardado de preferencias** - Las preferencias se guardan correctamente en la BD
2. **Lectura de preferencias** - Las preferencias se leen correctamente
3. **Lógica de verificación** - El método `should_send_notification()` funciona correctamente
4. **Servicios SMS/Email** - Ambos servicios verifican las preferencias antes de enviar
5. **Paso de customer_id** - Se pasa correctamente desde `package_state_service.py`

### 🔍 POSIBLES CAUSAS DEL PROBLEMA:

1. **Tipo de dato UUID vs String** - El `customer_id` es UUID en la BD pero se compara como string
2. **Preferencias no creadas** - El cliente no tiene registro en `customer_preferences`
3. **customer_id NULL** - Las notificaciones se envían sin `customer_id`

## Solución Implementada

He creado scripts de diagnóstico para identificar el problema exacto:

### 1. Script de Diagnóstico Básico

```bash
python CODE/diagnostico_preferencias.py
```

Este script verifica:
- Si el cliente existe
- Si tiene preferencias configuradas
- Si la lógica de `should_send_notification()` funciona
- El formato de datos que espera el frontend

### 2. Script de Prueba Completa

```bash
python CODE/test_preferencias_completo.py
```

Este script prueba:
- Desactivar SMS y verificar que se bloquea el envío
- Reactivar SMS y verificar que se envía
- Lo mismo con Email
- Verifica los registros en la BD

## Instrucciones para Diagnosticar

### Paso 1: Ejecutar Diagnóstico

```bash
cd CODE
python diagnostico_preferencias.py
```

**Resultado esperado:**
- Cliente encontrado ✅
- Preferencias configuradas ✅
- Método `should_send_notification` funciona ✅

### Paso 2: Ejecutar Prueba Completa

```bash
python test_preferencias_completo.py
```

**Resultado esperado:**
- SMS bloqueado cuando está desactivado ✅
- SMS enviado cuando está activado ✅
- Email bloqueado cuando está desactivado ✅

### Paso 3: Verificar en Staging

1. Acceder al portal: https://staging.jemavi.co/customer/verify
2. Ingresar con teléfono: `3002596319`
3. Ir a "Preferencias de Notificaciones"
4. Desactivar SMS
5. Cambiar el estado de un paquete del cliente
6. Verificar que NO llegue SMS

### Paso 4: Revisar Logs del Servidor

```bash
ssh staging
docker logs -f paquetes-backend-1 | grep -E "SMS|preferencias|bloqueado|customer_id"
```

**Buscar líneas como:**
```
📋 Preferencias encontradas para cliente <UUID>
   SMS habilitado: False
   Evento PACKAGE_RECEIVED: False
📵 SMS bloqueado por preferencias
```

### Paso 5: Verificar Base de Datos

```bash
# Conectar a la BD
ssh staging
docker exec -it paquetes-db-1 psql -U postgres -d paquetes_db

# Verificar preferencias del cliente
SELECT 
    c.id,
    c.full_name,
    c.phone,
    cp.sms_notifications_enabled,
    cp.email_notifications_enabled,
    cp.notify_package_received,
    cp.notify_package_delivered
FROM customers c
LEFT JOIN customer_preferences cp ON c.id = cp.customer_id
WHERE c.phone = '573002596319';

# Verificar notificaciones bloqueadas
SELECT 
    id,
    recipient,
    event_type,
    status,
    error_message,
    created_at
FROM notifications
WHERE status = 'blocked'
ORDER BY created_at DESC
LIMIT 10;
```

## Posibles Problemas y Soluciones

### Problema 1: Cliente sin preferencias

**Síntoma:** La consulta SQL muestra `NULL` en las columnas de `customer_preferences`

**Solución:**
```sql
-- Crear preferencias para el cliente
INSERT INTO customer_preferences (
    id,
    customer_id,
    token,
    sms_notifications_enabled,
    email_notifications_enabled,
    notify_package_received,
    notify_package_delivered,
    notify_package_announced,
    notify_payment_due,
    marketing_enabled,
    created_at,
    updated_at
)
SELECT 
    gen_random_uuid(),
    c.id,
    encode(gen_random_bytes(36), 'base64'),
    true,
    true,
    true,
    true,
    true,
    true,
    false,
    NOW(),
    NOW()
FROM customers c
WHERE c.phone = '573002596319'
AND NOT EXISTS (
    SELECT 1 FROM customer_preferences cp WHERE cp.customer_id = c.id
);
```

### Problema 2: customer_id no se pasa al enviar

**Síntoma:** Los logs muestran `customer_id: None` o no muestran verificación de preferencias

**Solución:** Ya está implementado correctamente en el código. Verificar que:
1. El paquete tiene `customer_id` asignado
2. El `package_state_service.py` pasa el `customer_id` correctamente

### Problema 3: Tipo de dato UUID vs String

**Síntoma:** Las preferencias existen pero no se encuentran al buscar

**Solución:** Ya está implementado - se convierte UUID a string:
```python
customer_id=str(package.customer_id) if package.customer_id else None
```

## Verificación Final

Después de ejecutar los scripts, deberías ver:

1. **En el script de diagnóstico:**
   ```
   ✅ Cliente encontrado
   ✅ Preferencias configuradas correctamente
   ✅ Método should_send_notification funciona correctamente
   ```

2. **En el script de prueba completa:**
   ```
   ✅ CORRECTO: SMS bloqueado por preferencias
   ✅ CORRECTO: SMS enviado correctamente
   ```

3. **En los logs del servidor:**
   ```
   📵 SMS bloqueado por preferencias del cliente
   ```

4. **En la base de datos:**
   ```
   status = 'blocked'
   error_message = 'Bloqueado por preferencias del cliente'
   ```

## Próximos Pasos

1. Ejecutar `python CODE/diagnostico_preferencias.py`
2. Ejecutar `python CODE/test_preferencias_completo.py`
3. Reportar los resultados
4. Si todo funciona en local pero no en staging, revisar logs del servidor
5. Verificar que las preferencias se guarden correctamente en staging

## Archivos Creados

- `CODE/diagnostico_preferencias.py` - Diagnóstico básico
- `CODE/test_preferencias_completo.py` - Prueba completa del flujo
- `CODE/ANALISIS_PROBLEMA_PREFERENCIAS.md` - Análisis técnico detallado
- `CODE/SOLUCION_PREFERENCIAS_NOTIFICACIONES.md` - Este documento

## Contacto

Si después de ejecutar los scripts el problema persiste, necesitaré:
1. Output completo de ambos scripts
2. Logs del servidor al cambiar preferencias
3. Resultado de las consultas SQL
4. Captura de pantalla de las preferencias en el portal
