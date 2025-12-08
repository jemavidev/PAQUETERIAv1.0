# Corrección Error SMS OTP: 'str' object has no attribute 'value'

## Problema Identificado

Al solicitar contraseña temporal (OTP) en https://staging.jemavi.co/customer/verify, aparecía el error:
```
Error al enviar contraseña temporal: Error al enviar SMS: 'str' object has no attribute 'value'
```

## Causa Raíz

El error ocurría porque en varios lugares del código se estaba pasando `event_type` como **string** (`"CUSTOM_MESSAGE"`) en lugar de usar el **enum** (`NotificationEvent.CUSTOM_MESSAGE`).

Cuando el servicio SMS intentaba hacer logging con `event_type.value`, fallaba porque los strings no tienen el atributo `.value`.

## Archivos Corregidos

### 1. `CODE/src/app/routes/customer_preferences_otp.py`

**Problema 1:** En el endpoint `/request` (línea 121-128)
- Se pasaba `event_type` como enum ✅ (correcto)
- PERO se pasaba `customer_id=str(customer.id)` ❌ (incorrecto para OTP de autenticación)

**Solución:**
```python
# ANTES
await sms_service.send_sms(
    db=db,
    recipient=phone,
    message=sms_message,
    event_type=NotificationEvent.CUSTOM_MESSAGE,
    customer_id=str(customer.id),  # ❌ Esto causaba verificación de preferencias
    is_test=False
)

# DESPUÉS
await sms_service.send_sms(
    db=db,
    recipient=phone,
    message=sms_message,
    event_type=NotificationEvent.CUSTOM_MESSAGE,
    customer_id=None,  # ✅ OTP de autenticación NO debe verificar preferencias
    is_test=False
)
```

**Problema 2:** En el endpoint `/send-link` (línea 343)
- Se pasaba `event_type="CUSTOM_MESSAGE"` como string ❌

**Solución:**
```python
# ANTES
await sms_service.send_sms(
    db=db,
    recipient=phone,
    message=message,
    event_type="CUSTOM_MESSAGE",  # ❌ String
    customer_id=str(customer.id),
    is_test=False
)

# DESPUÉS
from app.models.notification import NotificationEvent

await sms_service.send_sms(
    db=db,
    recipient=phone,
    message=message,
    event_type=NotificationEvent.CUSTOM_MESSAGE,  # ✅ Enum
    customer_id=str(customer.id),
    is_test=False
)
```

### 2. `CODE/src/app/services/customer_portal_service.py`

**Problema:** Se pasaba `event_type="CUSTOM_MESSAGE"` como string

**Solución:**
```python
# ANTES
await self.sms_service.send_sms(
    db=db,
    recipient=phone,
    message=message,
    event_type="CUSTOM_MESSAGE",  # ❌ String
    customer_id=str(customer.id),
    is_test=False
)

# DESPUÉS
from app.models.notification import NotificationEvent

await self.sms_service.send_sms(
    db=db,
    recipient=phone,
    message=message,
    event_type=NotificationEvent.CUSTOM_MESSAGE,  # ✅ Enum
    customer_id=str(customer.id),
    is_test=False
)
```

## Cambios Adicionales

### Import agregado en `customer_portal_service.py`
```python
from app.models.notification import NotificationEvent
```

## Lógica de Preferencias

### ¿Cuándo se verifican las preferencias?

El servicio SMS verifica preferencias del cliente SOLO cuando:
1. Se pasa `customer_id` (no None)
2. No es modo test (`is_test=False`)
3. El cliente tiene preferencias configuradas

### ¿Cuándo NO se deben verificar preferencias?

**OTPs de Autenticación:** Los códigos OTP para acceder al portal son CRÍTICOS y deben enviarse SIEMPRE, sin importar las preferencias del cliente.

Por eso, al enviar OTP de autenticación, se debe pasar `customer_id=None`.

### ¿Cuándo SÍ se deben verificar preferencias?

**Notificaciones de Paquetes:** Los SMS sobre cambios de estado de paquetes (recibido, entregado, etc.) SÍ deben respetar las preferencias del cliente.

En estos casos, se pasa `customer_id=str(customer.id)`.

## Resultado Esperado

Después de estos cambios:

1. ✅ El error `'str' object has no attribute 'value'` está resuelto
2. ✅ Los OTPs de autenticación se envían SIEMPRE por SMS (sin verificar preferencias)
3. ✅ Los OTPs también se envían por Email como canal adicional (si el cliente tiene email)
4. ✅ Las notificaciones de paquetes SÍ respetan las preferencias del cliente
5. ✅ Todo el código usa enums consistentemente (no strings)

## Pruebas Recomendadas

1. Solicitar OTP en `/customer/verify` con teléfono `3002596319`
2. Verificar que se recibe SMS con contraseña temporal
3. Verificar que también se recibe Email (si está configurado)
4. Verificar que las preferencias de notificaciones funcionan correctamente
5. Confirmar que cambiar preferencias se guarda correctamente

## Notas Técnicas

- El enum `NotificationEvent` está definido en `app.models.notification`
- Los valores del enum son: `CUSTOM_MESSAGE`, `PACKAGE_RECEIVED`, `PACKAGE_DELIVERED`, etc.
- El servicio SMS hace logging con `event_type.value`, por eso requiere enums
- Las preferencias se verifican en `sms_service.py` líneas 135-210
