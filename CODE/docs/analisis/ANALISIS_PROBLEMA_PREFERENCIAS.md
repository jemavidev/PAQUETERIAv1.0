# Análisis: Problema con Preferencias de Notificaciones

## Problema Reportado

El usuario puede cambiar las preferencias de notificaciones (ON/OFF para SMS y Email), pero independientemente de lo que elija, los mensajes SMS y Emails siguen llegando. Las preferencias no se están respetando.

## Análisis del Sistema

### 1. Flujo de Preferencias

#### Guardado de Preferencias ✅
**Archivo:** `CODE/src/app/services/customer_portal_service.py` (líneas 330-380)

```python
def update_notification_preferences(self, db, customer_id, preferences_data):
    # Obtener o crear preferencias
    preferences = db.query(CustomerPreferences).filter(
        CustomerPreferences.customer_id == customer_id
    ).first()
    
    # Actualizar campos
    allowed_fields = [
        "sms_notifications_enabled",
        "email_notifications_enabled",
        "notify_package_announced",
        "notify_package_received",
        "notify_package_delivered",
        "notify_payment_due",
        "marketing_enabled"
    ]
    
    for field in allowed_fields:
        if field in preferences_data:
            setattr(preferences, field, preferences_data[field])
    
    db.commit()
```

**Estado:** ✅ FUNCIONA CORRECTAMENTE
- Las preferencias se guardan en la base de datos
- Los campos se actualizan correctamente

#### Lectura de Preferencias ✅
**Archivo:** `CODE/src/app/services/customer_portal_service.py` (líneas 285-328)

```python
def get_notification_preferences(self, db, customer_id):
    preferences = db.query(CustomerPreferences).filter(
        CustomerPreferences.customer_id == customer_id
    ).first()
    
    return {
        "sms_notifications_enabled": preferences.sms_notifications_enabled,
        "email_notifications_enabled": preferences.email_notifications_enabled,
        # ... otros campos
    }
```

**Estado:** ✅ FUNCIONA CORRECTAMENTE
- Las preferencias se leen correctamente de la base de datos

### 2. Verificación de Preferencias al Enviar

#### Método should_send_notification ✅
**Archivo:** `CODE/src/app/models/customer_preferences.py` (líneas 50-95)

```python
def should_send_notification(self, notification_type, event_type):
    # Eventos críticos siempre se envían
    CRITICAL_EVENTS = [
        NotificationEvent.SECURITY_ALERT,
        NotificationEvent.LEGAL_NOTICE,
    ]
    
    if event_type in CRITICAL_EVENTS:
        return True
    
    # Verificar preferencia general por tipo
    if notification_type == NotificationType.SMS:
        if not self.sms_notifications_enabled:
            return False  # ✅ Bloquea si SMS está desactivado
    
    elif notification_type == NotificationType.EMAIL:
        if not self.email_notifications_enabled:
            return False  # ✅ Bloquea si Email está desactivado
    
    # Verificar preferencia específica por evento
    if event_type == NotificationEvent.PACKAGE_RECEIVED:
        return self.notify_package_received
    elif event_type == NotificationEvent.PACKAGE_DELIVERED:
        return self.notify_package_delivered
    # ... otros eventos
    
    return True  # Por defecto, permitir
```

**Estado:** ✅ LÓGICA CORRECTA
- Verifica primero si el canal (SMS/Email) está habilitado
- Luego verifica si el evento específico está habilitado
- Retorna False si cualquiera está desactivado

### 3. Envío de Notificaciones

#### Servicio SMS
**Archivo:** `CODE/src/app/services/sms_service.py` (líneas 173-210)

```python
async def send_sms(self, db, recipient, message, event_type, customer_id, ...):
    # ✅ NUEVO: Verificar preferencias del cliente
    if customer_id and not is_test:
        customer_prefs = db.query(CustomerPreferences).filter(
            CustomerPreferences.customer_id == customer_id
        ).first()
        
        if customer_prefs:
            # Verificar si el cliente permite este tipo de notificación
            if not customer_prefs.should_send_notification(NotificationType.SMS, event_type):
                # Crear registro de notificación bloqueada
                notification = Notification(
                    status=NotificationStatus.BLOCKED,
                    error_message="Bloqueado por preferencias del cliente"
                )
                return SMSSendResponse(status="blocked", ...)
```

**Estado:** ✅ IMPLEMENTADO CORRECTAMENTE
- Verifica preferencias antes de enviar
- Bloquea el envío si las preferencias lo indican
- Crea registro de notificación bloqueada

#### Servicio Email
**Archivo:** `CODE/src/app/services/email_service.py` (líneas similares)

**Estado:** ✅ IMPLEMENTADO CORRECTAMENTE
- Misma lógica que SMS

### 4. Envío desde Cambios de Estado de Paquetes

#### Package State Service
**Archivo:** `CODE/src/app/services/package_state_service.py`

**Método _send_sms_notification (líneas 381-447):**
```python
async def _send_sms_notification(cls, db, package, new_status, changed_by):
    # Mapear estados a eventos
    event_mapping = {
        PackageStatus.RECIBIDO: NotificationEvent.PACKAGE_RECEIVED,
        PackageStatus.ENTREGADO: NotificationEvent.PACKAGE_DELIVERED,
        # ...
    }
    
    # Enviar SMS usando el servicio
    await sms_service.send_sms_by_event(
        db=db,
        event_request=SMSByEventRequest(
            event_type=event_type,
            package_id=package.id,
            customer_id=package.customer_id,  # ✅ Pasa customer_id
            # ...
        )
    )
```

**Estado:** ✅ PASA customer_id CORRECTAMENTE
- El customer_id se pasa al servicio SMS
- El servicio SMS debería verificar las preferencias

## PROBLEMA IDENTIFICADO 🔴

### Hipótesis 1: customer_id como UUID vs String

En `package_state_service.py` se pasa:
```python
customer_id=package.customer_id  # UUID object
```

Pero en `sms_service.py` se espera:
```python
customer_id: Optional[str] = None
```

Y luego se hace:
```python
customer_prefs = db.query(CustomerPreferences).filter(
    CustomerPreferences.customer_id == customer_id  # Comparación UUID vs String
).first()
```

**Solución:** Convertir el UUID a string al pasar:
```python
customer_id=str(package.customer_id) if package.customer_id else None
```

### Hipótesis 2: send_sms_by_event no pasa customer_id correctamente

El método `send_sms_by_event` recibe el customer_id pero necesitamos verificar que lo pase al método `send_sms`.

**Archivo:** `CODE/src/app/services/sms_service.py` (líneas 330-380)

Necesito verificar esta parte del código.

## SOLUCIÓN PROPUESTA

### Paso 1: Verificar conversión de UUID a String

En `package_state_service.py`, cambiar:

```python
# ANTES
await sms_service.send_sms_by_event(
    db=db,
    event_request=SMSByEventRequest(
        event_type=event_type,
        package_id=package.id,
        customer_id=package.customer_id,  # UUID
        # ...
    )
)

# DESPUÉS
await sms_service.send_sms_by_event(
    db=db,
    event_request=SMSByEventRequest(
        event_type=event_type,
        package_id=package.id,
        customer_id=str(package.customer_id) if package.customer_id else None,  # String
        # ...
    )
)
```

### Paso 2: Verificar que send_sms_by_event pasa el customer_id

Necesito leer el código de `send_sms_by_event` para confirmar que pasa el `customer_id` al método `send_sms`.

### Paso 3: Agregar Logging Detallado

Agregar logs en el servicio SMS para ver si las preferencias se están verificando:

```python
if customer_prefs:
    logger.info(f"📋 Preferencias encontradas para cliente {customer_id}")
    logger.info(f"   SMS habilitado: {customer_prefs.sms_notifications_enabled}")
    logger.info(f"   Evento {event_type}: {customer_prefs.should_send_notification(NotificationType.SMS, event_type)}")
    
    if not customer_prefs.should_send_notification(NotificationType.SMS, event_type):
        logger.info(f"📵 SMS bloqueado por preferencias")
        # ... bloquear envío
else:
    logger.warning(f"⚠️ No se encontraron preferencias para cliente {customer_id}")
```

## PRUEBAS RECOMENDADAS

1. Ejecutar `python CODE/diagnostico_preferencias.py` para verificar que las preferencias se guardan correctamente

2. Desactivar SMS en las preferencias del cliente

3. Cambiar el estado de un paquete del cliente (ej: ANUNCIADO → RECIBIDO)

4. Verificar en los logs si:
   - Se encontraron las preferencias del cliente
   - Se verificó el método `should_send_notification`
   - Se bloqueó el envío correctamente

5. Verificar en la base de datos la tabla `notifications` que el registro tenga:
   - `status = 'blocked'`
   - `error_message = 'Bloqueado por preferencias del cliente'`

## ARCHIVOS A MODIFICAR

1. `CODE/src/app/services/package_state_service.py` - Convertir UUID a string
2. `CODE/src/app/services/sms_service.py` - Agregar logging detallado
3. `CODE/src/app/services/email_service.py` - Agregar logging detallado (mismo patrón)

## COMANDOS PARA PROBAR

```bash
# 1. Ejecutar diagnóstico
python CODE/diagnostico_preferencias.py

# 2. Ver logs del servidor en tiempo real
ssh staging
docker logs -f paquetes-backend-1 | grep -E "SMS|preferencias|bloqueado"

# 3. Verificar notificaciones bloqueadas en la base de datos
psql -U postgres -d paquetes_db -c "SELECT id, recipient, event_type, status, error_message FROM notifications WHERE status = 'blocked' ORDER BY created_at DESC LIMIT 10;"
```
