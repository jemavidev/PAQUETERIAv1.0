# Instrucciones para Diagnosticar Preferencias en Staging

## Problema
Las preferencias de notificaciones no se están respetando. Los SMS y Emails siguen llegando aunque estén desactivados.

## Scripts Creados

He creado 3 scripts para diagnosticar el problema:

1. `check_preferencias_staging.sh` - Script bash para ejecutar en staging
2. `check_preferencias.sql` - Consultas SQL para verificar en la base de datos
3. Scripts Python (requieren entorno local configurado)

## Opción 1: Ejecutar Script Bash en Staging (RECOMENDADO)

```bash
# 1. Conectar a staging
ssh staging

# 2. Ir al directorio del proyecto
cd /ruta/del/proyecto/CODE

# 3. Ejecutar el script
./check_preferencias_staging.sh
```

**Resultado esperado:**
```
✅ Cliente: [Nombre del cliente]
   ID: [UUID]
📋 Preferencias:
   SMS: True/False
   Email: True/False
   Paquete Recibido: True/False
   Paquete Entregado: True/False
```

## Opción 2: Consultas SQL Directas (MÁS RÁPIDO)

```bash
# 1. Conectar a staging
ssh staging

# 2. Conectar a la base de datos
docker exec -it paquetes-db-1 psql -U postgres -d paquetes_db

# 3. Ejecutar consultas
```

### Consulta 1: Verificar cliente y preferencias

```sql
SELECT 
    c.id as customer_id,
    c.full_name,
    c.phone,
    c.email,
    cp.id as preferences_id,
    cp.sms_notifications_enabled,
    cp.email_notifications_enabled,
    cp.notify_package_received,
    cp.notify_package_delivered,
    cp.updated_at as preferences_updated
FROM customers c
LEFT JOIN customer_preferences cp ON c.id = cp.customer_id
WHERE c.phone = '573002596319';
```

**¿Qué buscar?**
- Si `preferences_id` es NULL → El cliente NO tiene preferencias (PROBLEMA)
- Si `sms_notifications_enabled` es FALSE → SMS debería estar bloqueado
- Si `email_notifications_enabled` es FALSE → Email debería estar bloqueado

### Consulta 2: Verificar últimas notificaciones

```sql
SELECT 
    n.id,
    n.notification_type,
    n.event_type,
    n.status,
    n.recipient,
    n.customer_id,
    n.error_message,
    n.created_at
FROM notifications n
JOIN customers c ON n.customer_id = c.id
WHERE c.phone = '573002596319'
ORDER BY n.created_at DESC
LIMIT 10;
```

**¿Qué buscar?**
- Si `status` = 'blocked' → Las preferencias SÍ se están respetando ✅
- Si `status` = 'sent' y las preferencias están desactivadas → PROBLEMA ❌
- Si `customer_id` es NULL → No se está pasando el customer_id (PROBLEMA)

### Consulta 3: Ver notificaciones bloqueadas

```sql
SELECT 
    n.id,
    n.notification_type,
    n.event_type,
    n.recipient,
    n.error_message,
    n.created_at
FROM notifications n
WHERE n.status = 'blocked'
ORDER BY n.created_at DESC
LIMIT 10;
```

**¿Qué buscar?**
- Si hay registros con `error_message` = 'Bloqueado por preferencias del cliente' → El sistema FUNCIONA ✅
- Si NO hay registros bloqueados → El sistema NO está verificando preferencias ❌

## Opción 3: Verificar desde el Portal Web

1. Ir a: https://staging.jemavi.co/customer/verify
2. Ingresar teléfono: `3002596319`
3. Solicitar OTP y verificar
4. Ir a "Preferencias de Notificaciones"
5. Verificar el estado actual de las preferencias
6. Cambiar una preferencia (ej: desactivar SMS)
7. Guardar
8. Recargar la página
9. **Verificar si el cambio se mantuvo**

**Si el cambio NO se mantiene:**
- Problema en el frontend o en el endpoint de guardado
- Revisar logs del servidor al guardar

**Si el cambio SÍ se mantiene:**
- Las preferencias se guardan correctamente
- El problema está en que no se verifican al enviar notificaciones

## Opción 4: Revisar Logs del Servidor

```bash
# 1. Conectar a staging
ssh staging

# 2. Ver logs en tiempo real
docker logs -f paquetes-backend-1 | grep -E "SMS|preferencias|bloqueado|customer_id"

# 3. En otra terminal, cambiar el estado de un paquete del cliente
# Esto debería generar logs de verificación de preferencias
```

**Logs esperados si funciona correctamente:**
```
📋 Preferencias encontradas para cliente <UUID>
   SMS habilitado: False
   Evento PACKAGE_RECEIVED: False
📵 SMS bloqueado por preferencias del cliente
```

**Logs si NO funciona:**
```
⚠️ No se encontraron preferencias para cliente <UUID>
```
O simplemente no aparecen logs de verificación.

## Diagnóstico Según Resultados

### Caso 1: Cliente SIN preferencias en BD
```
preferences_id | NULL
```

**Solución:** Crear preferencias para el cliente

```sql
INSERT INTO customer_preferences (
    id, customer_id, token,
    sms_notifications_enabled, email_notifications_enabled,
    notify_package_received, notify_package_delivered,
    notify_package_announced, notify_payment_due,
    marketing_enabled, created_at, updated_at
)
SELECT 
    gen_random_uuid(),
    c.id,
    encode(gen_random_bytes(36), 'base64'),
    true, true, true, true, true, true, false,
    NOW(), NOW()
FROM customers c
WHERE c.phone = '573002596319'
AND NOT EXISTS (
    SELECT 1 FROM customer_preferences cp WHERE cp.customer_id = c.id
);
```

### Caso 2: Preferencias existen pero notificaciones NO se bloquean

**Verificar:**
1. ¿Las notificaciones tienen `customer_id`?
2. ¿El `customer_id` coincide con el de las preferencias?
3. ¿Los logs muestran verificación de preferencias?

**Si NO hay logs de verificación:**
- El código no está verificando las preferencias
- Necesito revisar el código de `package_state_service.py`

### Caso 3: Preferencias se restablecen al recargar

**Problema:** Frontend no está guardando correctamente

**Verificar:**
1. Abrir DevTools del navegador
2. Ir a Network tab
3. Cambiar una preferencia y guardar
4. Ver la petición PUT a `/api/customer-portal/preferences/notifications`
5. Verificar que el body contiene los valores correctos

## Siguiente Paso

**Por favor ejecuta la Opción 2 (Consultas SQL) y comparte los resultados.**

Necesito ver:
1. ¿El cliente tiene preferencias configuradas?
2. ¿Cuál es el estado actual de las preferencias?
3. ¿Hay notificaciones bloqueadas en la BD?
4. ¿Las últimas notificaciones tienen customer_id?

Con esa información podré identificar exactamente dónde está el problema.
