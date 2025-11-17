# 📱 Unificación de Plantillas SMS

## 🎯 Objetivo

Unificar las plantillas SMS siguiendo el mismo patrón que se implementó en el servicio de Email (SMTP), donde se usa una sola plantilla `status_change.html` para todos los cambios de estado de paquetes.

## 📊 Antes vs Después

### ❌ Antes (Plantillas Separadas)

```
package_announced    → "Su paquete ha sido anunciado..."
package_received     → "Su paquete ha sido RECIBIDO..."
package_delivered    → "Su paquete ha sido ENTREGADO..."
package_cancelled    → "Su paquete ha sido CANCELADO..."
```

**Problemas:**
- 4 plantillas diferentes para mantener
- Inconsistencia en mensajes
- Difícil de actualizar (cambiar en 4 lugares)
- No alineado con EmailService

### ✅ Después (Plantilla Unificada)

```
status_change_unified → "Su paquete {guide_number} está {status_text}..."
```

**Beneficios:**
- ✅ 1 sola plantilla para todos los estados
- ✅ Consistencia con EmailService
- ✅ Fácil mantenimiento
- ✅ Mensajes uniformes
- ✅ Variable dinámica `{status_text}` según evento

## 🔄 Mapeo de Estados

El servicio SMS ahora mapea automáticamente cada evento a un texto de estado:

```python
status_text_map = {
    NotificationEvent.PACKAGE_ANNOUNCED: "ANUNCIADO",
    NotificationEvent.PACKAGE_RECEIVED: "RECIBIDO en nuestras instalaciones",
    NotificationEvent.PACKAGE_DELIVERED: "ENTREGADO exitosamente",
    NotificationEvent.PACKAGE_CANCELLED: "CANCELADO"
}
```

## 📝 Plantillas Unificadas

### 1. **status_change_unified** (Principal)

**Uso:** Todos los cambios de estado de paquetes

**Template:**
```
PAQUETES: Su paquete {guide_number} está {status_text}. Código: {consult_code}. Info: {tracking_url}
```

**Variables disponibles:**
- `guide_number` - Número de guía del paquete
- `consult_code` - Código de consulta
- `tracking_code` - Código de seguimiento
- `status_text` - Texto dinámico del estado (ANUNCIADO, RECIBIDO, etc.)
- `customer_name` - Nombre del cliente
- `tracking_url` - URL de seguimiento
- `company_name` - Nombre de la empresa
- `company_phone` - Teléfono de contacto

**Eventos que usan esta plantilla:**
- `PACKAGE_ANNOUNCED`
- `PACKAGE_RECEIVED`
- `PACKAGE_DELIVERED`
- `PACKAGE_CANCELLED`

### 2. **payment_due** (Pagos)

**Uso:** Recordatorios de pago pendiente

**Template:**
```
PAQUETES: Tiene un pago pendiente de ${amount} COP para el paquete {guide_number}. Realice el pago para continuar con la entrega.
```

**Variables disponibles:**
- `guide_number`
- `consult_code`
- `amount` - Monto a pagar
- `due_date` - Fecha límite
- `customer_name`
- `company_phone`

### 3. **custom_message** (Genérico)

**Uso:** Mensajes personalizados

**Template:**
```
PAQUETES: {message}
```

**Variables disponibles:**
- `message` - Mensaje personalizado
- `customer_name`
- `company_phone`

## 🚀 Migración

### Ejecutar Migración

```bash
# Desde el directorio CODE
python -m src.scripts.migrate_sms_templates_unified
```

### Opciones del Script

1. **Migrar a plantillas unificadas** (recomendado)
   - Desactiva plantillas antiguas
   - Crea/actualiza plantillas unificadas
   - Preserva historial

2. **Rollback** (revertir)
   - Reactiva plantillas antiguas
   - Desactiva plantillas unificadas

3. **Ver plantillas actuales**
   - Lista todas las plantillas
   - Muestra estado (activa/inactiva)

4. **Cancelar**

### Qué hace la migración

1. ✅ Desactiva plantillas antiguas (no las elimina)
2. ✅ Crea plantilla unificada `status_change_unified`
3. ✅ Mantiene plantillas de `payment_due` y `custom_message`
4. ✅ Preserva historial de notificaciones antiguas

## 💻 Uso en Código

### Enviar SMS con evento (automático)

```python
from app.services.sms_service import SMSService
from app.models.notification import NotificationEvent, NotificationPriority

sms_service = SMSService()

# El servicio automáticamente usa la plantilla unificada
result = await sms_service.send_sms_by_event(
    db=db,
    event_request=SMSByEventRequest(
        event_type=NotificationEvent.PACKAGE_RECEIVED,
        package_id=123,
        priority=NotificationPriority.ALTA,
        is_test=False
    )
)
```

### Resultado del SMS

```
PAQUETES: Su paquete 123456789 está RECIBIDO en nuestras instalaciones. 
Código: ABC123. Info: https://paquetes.com.co/seguimiento/123456789
```

## 🔍 Comparación con EmailService

| Aspecto | EmailService | SMSService (Nuevo) |
|---------|--------------|-------------------|
| **Plantilla unificada** | ✅ `status_change.html` | ✅ `status_change_unified` |
| **Variable dinámica** | ✅ `current_status` | ✅ `status_text` |
| **Eventos soportados** | 4 estados | 4 estados |
| **Plantilla pago** | ✅ `payment_reminder.html` | ✅ `payment_due` |
| **Plantilla genérica** | ✅ `generic_notification.html` | ✅ `custom_message` |
| **Almacenamiento** | Archivos HTML | Base de datos |

## 📋 Checklist Post-Migración

- [ ] Ejecutar script de migración
- [ ] Verificar plantillas activas en BD
- [ ] Probar envío SMS con `PACKAGE_RECEIVED`
- [ ] Probar envío SMS con `PACKAGE_DELIVERED`
- [ ] Probar envío SMS con `PACKAGE_CANCELLED`
- [ ] Verificar que los mensajes sean consistentes
- [ ] Revisar logs de notificaciones
- [ ] Actualizar documentación de API si es necesario

## 🛠️ Personalización

### Cambiar texto de estado

Editar en `sms_service.py`:

```python
status_text_map = {
    NotificationEvent.PACKAGE_RECEIVED: "RECIBIDO y listo para entrega",  # Personalizado
    # ...
}
```

### Cambiar plantilla unificada

Actualizar en base de datos:

```sql
UPDATE sms_message_templates 
SET message_template = 'NUEVO TEXTO: {guide_number} - {status_text}'
WHERE template_id = 'status_change_unified';
```

O usar el admin panel de SMS.

## 🐛 Troubleshooting

### Problema: SMS sigue usando plantillas antiguas

**Solución:** Verificar que la migración se ejecutó correctamente:

```bash
python -m src.scripts.migrate_sms_templates_unified
# Opción 3: Ver plantillas actuales
```

### Problema: Variable `{status_text}` no se reemplaza

**Solución:** Verificar que `_prepare_event_variables` incluye el mapeo:

```python
variables["status_text"] = status_text_map.get(event_type, "en proceso")
```

### Problema: Quiero volver a plantillas antiguas

**Solución:** Ejecutar rollback:

```bash
python -m src.scripts.migrate_sms_templates_unified
# Opción 2: Rollback
```

## 📚 Referencias

- `CODE/src/app/services/sms_service.py` - Servicio SMS unificado
- `CODE/src/app/services/email_service.py` - Patrón de referencia
- `CODE/src/templates/emails/status_change.html` - Template email equivalente
- `CODE/src/scripts/migrate_sms_templates_unified.py` - Script de migración

## ✅ Conclusión

La unificación de plantillas SMS:

1. ✅ Simplifica el mantenimiento (1 plantilla vs 4)
2. ✅ Alinea SMS con Email para consistencia
3. ✅ Mejora la experiencia del usuario con mensajes uniformes
4. ✅ Facilita futuras actualizaciones
5. ✅ Preserva el historial de notificaciones antiguas

---

**Versión:** 1.0.0  
**Fecha:** 2025-01-24  
**Autor:** Equipo de Desarrollo
