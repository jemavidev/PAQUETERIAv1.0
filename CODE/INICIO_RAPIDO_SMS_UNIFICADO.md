# 🚀 Inicio Rápido: SMS Unificado

## ⚡ 3 Pasos para Implementar

### 1️⃣ Ejecutar Migración (2 minutos)

```bash
cd CODE
python -m src.scripts.migrate_sms_templates_unified
```

Seleccionar: **Opción 1 - Migrar a plantillas unificadas**

---

### 2️⃣ Verificar Plantillas (1 minuto)

```bash
python -m src.scripts.migrate_sms_templates_unified
```

Seleccionar: **Opción 3 - Ver plantillas actuales**

**Resultado esperado:**
```
✅ ACTIVA ⭐ DEFAULT status_change_unified
✅ ACTIVA ⭐ DEFAULT payment_due
✅ ACTIVA ⭐ DEFAULT custom_message
❌ INACTIVA package_announced (antigua)
❌ INACTIVA package_received (antigua)
❌ INACTIVA package_delivered (antigua)
❌ INACTIVA package_cancelled (antigua)
```

---

### 3️⃣ Probar Envío (2 minutos)

```python
from app.services.sms_service import SMSService
from app.models.notification import NotificationEvent
from app.schemas.notification import SMSByEventRequest

sms_service = SMSService()

# Enviar SMS de prueba
result = await sms_service.send_sms_by_event(
    db=db,
    event_request=SMSByEventRequest(
        event_type=NotificationEvent.PACKAGE_RECEIVED,
        package_id=123,
        is_test=True  # Modo prueba (sin costo)
    )
)

print(f"✅ Status: {result.status}")
print(f"📱 Mensaje: {result.message}")
```

---

## ✅ ¡Listo!

Tu sistema SMS ahora usa plantillas unificadas, igual que el sistema de emails.

---

## 📚 Documentación Completa

- **Guía completa:** [UNIFICACION_PLANTILLAS_SMS.md](./UNIFICACION_PLANTILLAS_SMS.md)
- **Ejemplos de uso:** [EJEMPLO_USO_SMS_UNIFICADO.md](./EJEMPLO_USO_SMS_UNIFICADO.md)
- **Resumen detallado:** [RESUMEN_UNIFICACION_SMS.md](./RESUMEN_UNIFICACION_SMS.md)
- **Diagrama visual:** [DIAGRAMA_SMS_UNIFICADO.txt](./DIAGRAMA_SMS_UNIFICADO.txt)

---

## 🆘 Ayuda Rápida

### Problema: SMS no se envía

```bash
# Verificar plantillas activas
python -m src.scripts.migrate_sms_templates_unified
# Opción 3
```

### Problema: Quiero volver atrás

```bash
# Ejecutar rollback
python -m src.scripts.migrate_sms_templates_unified
# Opción 2
```

### Problema: Variable no se reemplaza

Verificar que `status_text` esté en el mapeo:
```python
# En sms_service.py, método _prepare_event_variables
status_text_map = {
    NotificationEvent.PACKAGE_RECEIVED: "RECIBIDO en nuestras instalaciones",
    # ...
}
```

---

## 💡 Ejemplo Completo

```python
# 1. Importar
from app.services.sms_service import SMSService
from app.models.notification import NotificationEvent, NotificationPriority
from app.schemas.notification import SMSByEventRequest

# 2. Inicializar servicio
sms_service = SMSService()

# 3. Enviar SMS cuando paquete es recibido
result = await sms_service.send_sms_by_event(
    db=db,
    event_request=SMSByEventRequest(
        event_type=NotificationEvent.PACKAGE_RECEIVED,
        package_id=123,
        priority=NotificationPriority.ALTA,
        is_test=False  # Cambiar a False para envío real
    )
)

# 4. Verificar resultado
if result.status == "sent":
    print(f"✅ SMS enviado exitosamente")
    print(f"📱 ID: {result.notification_id}")
    print(f"💰 Costo: ${result.cost_cents / 100} COP")
else:
    print(f"❌ Error: {result.message}")
```

**SMS enviado:**
```
PAQUETES: Su paquete 123456789 está RECIBIDO en nuestras instalaciones. 
Código: ABC123. Info: https://paquetes.com.co/seguimiento/123456789
```

---

## 🎯 Beneficios Inmediatos

✅ **1 plantilla** en lugar de 4  
✅ **Mensajes consistentes** para usuarios  
✅ **Alineado con emails** (mismo patrón)  
✅ **Fácil de mantener** (cambios en un solo lugar)  
✅ **Historial preservado** (plantillas antiguas inactivas)  

---

## 📊 Comparación Rápida

| Aspecto | Antes | Después |
|---------|-------|---------|
| Plantillas | 4 separadas | 1 unificada |
| Mantenimiento | Difícil | Fácil |
| Consistencia | Media | Alta |
| Alineación Email | No | Sí |

---

**¿Listo para empezar?** → Ejecuta el paso 1 ⬆️

---

**Versión:** 1.0.0  
**Fecha:** 2025-01-24
