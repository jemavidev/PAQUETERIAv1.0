# 📱 Ejemplos de Uso: SMS Unificado

## 🎯 Casos de Uso Comunes

### 1. Enviar SMS cuando un paquete es recibido

```python
from app.services.sms_service import SMSService
from app.models.notification import NotificationEvent, NotificationPriority
from app.schemas.notification import SMSByEventRequest

# Inicializar servicio
sms_service = SMSService()

# Enviar SMS usando plantilla unificada
result = await sms_service.send_sms_by_event(
    db=db,
    event_request=SMSByEventRequest(
        event_type=NotificationEvent.PACKAGE_RECEIVED,
        package_id=123,  # ID del paquete
        priority=NotificationPriority.ALTA,
        is_test=False
    )
)

# Resultado
print(f"SMS enviado: {result.status}")
print(f"ID notificación: {result.notification_id}")
print(f"Costo: ${result.cost_cents / 100} COP")
```

**SMS enviado:**
```
PAQUETES: Su paquete 123456789 está RECIBIDO en nuestras instalaciones. 
Código: ABC123. Info: https://paquetes.com.co/seguimiento/123456789
```

---

### 2. Enviar SMS cuando un paquete es entregado

```python
result = await sms_service.send_sms_by_event(
    db=db,
    event_request=SMSByEventRequest(
        event_type=NotificationEvent.PACKAGE_DELIVERED,
        package_id=123,
        priority=NotificationPriority.ALTA,
        is_test=False
    )
)
```

**SMS enviado:**
```
PAQUETES: Su paquete 123456789 está ENTREGADO exitosamente. 
Código: ABC123. Info: https://paquetes.com.co/seguimiento/123456789
```

---

### 3. Enviar SMS cuando un paquete es cancelado

```python
result = await sms_service.send_sms_by_event(
    db=db,
    event_request=SMSByEventRequest(
        event_type=NotificationEvent.PACKAGE_CANCELLED,
        package_id=123,
        priority=NotificationPriority.URGENTE,
        is_test=False
    )
)
```

**SMS enviado:**
```
PAQUETES: Su paquete 123456789 está CANCELADO. 
Código: ABC123. Info: https://paquetes.com.co/seguimiento/123456789
```

---

### 4. Enviar SMS con variables personalizadas

```python
result = await sms_service.send_sms_by_event(
    db=db,
    event_request=SMSByEventRequest(
        event_type=NotificationEvent.PACKAGE_RECEIVED,
        package_id=123,
        custom_variables={
            "additional_info": "Recoger en horario de 8am-5pm"
        },
        priority=NotificationPriority.MEDIA,
        is_test=False
    )
)
```

---

### 5. Enviar SMS de prueba (sin costo)

```python
result = await sms_service.send_sms_by_event(
    db=db,
    event_request=SMSByEventRequest(
        event_type=NotificationEvent.PACKAGE_RECEIVED,
        package_id=123,
        priority=NotificationPriority.MEDIA,
        is_test=True  # ✅ Modo prueba
    )
)

# En modo prueba:
# - No se envía SMS real
# - No tiene costo
# - Se registra en BD con is_test=True
```

---

### 6. Enviar SMS directo (sin plantilla)

```python
from app.schemas.notification import SMSSendRequest

result = await sms_service.send_sms(
    db=db,
    recipient="+573001234567",
    message="Hola, este es un mensaje personalizado",
    event_type=NotificationEvent.CUSTOM_MESSAGE,
    priority=NotificationPriority.MEDIA,
    is_test=False
)
```

---

### 7. Enviar SMS masivo

```python
from app.schemas.notification import SMSBulkSendRequest

result = await sms_service.send_bulk_sms(
    db=db,
    recipients=[
        "+573001234567",
        "+573009876543",
        "+573005555555"
    ],
    message="Recordatorio: Tenemos paquetes pendientes de entrega",
    event_type=NotificationEvent.CUSTOM_MESSAGE,
    priority=NotificationPriority.MEDIA,
    is_test=False
)

print(f"Enviados: {result.sent_count}")
print(f"Fallidos: {result.failed_count}")
print(f"Costo total: ${result.total_cost_cents / 100} COP")
```

---

### 8. Enviar recordatorio de pago

```python
result = await sms_service.send_sms_by_event(
    db=db,
    event_request=SMSByEventRequest(
        event_type=NotificationEvent.PAYMENT_DUE,
        package_id=123,
        custom_variables={
            "amount": "15000",
            "due_date": "25/01/2025"
        },
        priority=NotificationPriority.ALTA,
        is_test=False
    )
)
```

**SMS enviado:**
```
PAQUETES: Tiene un pago pendiente de $15000 COP para el paquete 123456789. 
Realice el pago para continuar con la entrega.
```

---

## 🔄 Integración con Rutas (API)

### Endpoint: Enviar SMS por evento

```python
# En tu archivo de rutas (routes/packages.py o similar)

@router.post("/packages/{package_id}/notify/received")
async def notify_package_received(
    package_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Notifica al cliente que su paquete fue recibido"""
    
    # Verificar que el paquete existe
    package = db.query(Package).filter(Package.id == package_id).first()
    if not package:
        raise HTTPException(status_code=404, detail="Paquete no encontrado")
    
    # Enviar SMS
    sms_service = SMSService()
    result = await sms_service.send_sms_by_event(
        db=db,
        event_request=SMSByEventRequest(
            event_type=NotificationEvent.PACKAGE_RECEIVED,
            package_id=package_id,
            priority=NotificationPriority.ALTA,
            is_test=False
        )
    )
    
    return {
        "message": "SMS enviado exitosamente",
        "notification_id": result.notification_id,
        "status": result.status
    }
```

---

## 🧪 Testing

### Test unitario

```python
import pytest
from app.services.sms_service import SMSService
from app.models.notification import NotificationEvent

@pytest.mark.asyncio
async def test_send_sms_unified_template(db_session):
    """Test envío SMS con plantilla unificada"""
    
    sms_service = SMSService()
    
    # Enviar SMS de prueba
    result = await sms_service.send_sms_by_event(
        db=db_session,
        event_request=SMSByEventRequest(
            event_type=NotificationEvent.PACKAGE_RECEIVED,
            package_id=1,
            priority=NotificationPriority.MEDIA,
            is_test=True  # Modo prueba
        )
    )
    
    # Verificar resultado
    assert result.status == "sent"
    assert result.notification_id is not None
    assert result.cost_cents == 0  # Sin costo en modo prueba
```

---

## 📊 Comparación: Antes vs Después

### ❌ Antes (Plantillas Separadas)

```python
# Necesitabas saber qué plantilla usar
if event == "received":
    template = "package_received"
elif event == "delivered":
    template = "package_delivered"
elif event == "cancelled":
    template = "package_cancelled"
# ... más código
```

### ✅ Después (Plantilla Unificada)

```python
# El servicio maneja todo automáticamente
result = await sms_service.send_sms_by_event(
    db=db,
    event_request=SMSByEventRequest(
        event_type=NotificationEvent.PACKAGE_RECEIVED,  # Solo especificas el evento
        package_id=123
    )
)
# ✅ Usa automáticamente la plantilla unificada
# ✅ Inserta el status_text correcto
# ✅ Obtiene el destinatario del paquete
```

---

## 🎨 Personalización de Mensajes

### Cambiar el texto de estado

```python
# En sms_service.py, método _prepare_event_variables

status_text_map = {
    NotificationEvent.PACKAGE_RECEIVED: "RECIBIDO y listo para entrega",  # ✏️ Personalizado
    NotificationEvent.PACKAGE_DELIVERED: "ENTREGADO con éxito",           # ✏️ Personalizado
    NotificationEvent.PACKAGE_CANCELLED: "CANCELADO por solicitud",       # ✏️ Personalizado
}
```

### Cambiar la plantilla completa

```python
# Actualizar en base de datos
from app.models.notification import SMSMessageTemplate

template = db.query(SMSMessageTemplate).filter(
    SMSMessageTemplate.template_id == "status_change_unified"
).first()

template.message_template = "NUEVO FORMATO: Paquete {guide_number} - Estado: {status_text}. Ver: {tracking_url}"
db.commit()
```

---

## 🔍 Debugging

### Ver plantilla que se está usando

```python
# Obtener plantilla
template = sms_service.get_template_by_event(
    db=db,
    event_type=NotificationEvent.PACKAGE_RECEIVED
)

print(f"Template ID: {template.template_id}")
print(f"Template: {template.message_template}")
print(f"Variables: {template.available_variables}")
```

### Ver variables preparadas

```python
# Preparar variables
variables = await sms_service._prepare_event_variables(
    db=db,
    event_type=NotificationEvent.PACKAGE_RECEIVED,
    package_id=123,
    customer_id=None,
    announcement_id=None,
    custom_variables={}
)

print("Variables disponibles:")
for key, value in variables.items():
    print(f"  {key}: {value}")
```

---

## 📈 Monitoreo

### Ver estadísticas de SMS

```python
stats = sms_service.get_sms_stats(db=db, days=30)

print(f"Total enviados: {stats['total_sent']}")
print(f"Total entregados: {stats['total_delivered']}")
print(f"Total fallidos: {stats['total_failed']}")
print(f"Tasa de entrega: {stats['delivery_rate']:.2f}%")
print(f"Costo total: ${stats['total_cost_cents'] / 100} COP")
```

---

## ✅ Checklist de Implementación

- [ ] Ejecutar migración de plantillas
- [ ] Probar envío SMS con cada evento
- [ ] Verificar que los mensajes sean correctos
- [ ] Ajustar textos de estado si es necesario
- [ ] Actualizar tests unitarios
- [ ] Documentar en API docs
- [ ] Capacitar al equipo en nuevo formato

---

**Versión:** 1.0.0  
**Fecha:** 2025-01-24  
**Autor:** Equipo de Desarrollo
