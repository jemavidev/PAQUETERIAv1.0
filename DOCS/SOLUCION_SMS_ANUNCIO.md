# 🔧 Solución: SMS no se envía al anunciar paquete

## 🐛 Problema Reportado

Al anunciar el paquete con:
- **Guía:** DSE4GS
- **Código:** HTE3

**No se recibió ningún mensaje de texto (SMS)**

---

## 🔍 Diagnóstico

Se encontraron **3 problemas críticos** en el código:

### 1. ❌ Evento incorrecto en `announcements.py`

**Línea 66 (antes):**
```python
await sms_service.send_sms_by_event(
    db=db,
    event_type=NotificationEvent.ANNOUNCEMENT,  # ❌ Este evento NO EXISTE
    recipient=db_announcement.customer_phone,
    announcement_id=db_announcement.id
)
```

**Problema:** `NotificationEvent.ANNOUNCEMENT` no existe en el enum. Los eventos válidos son:
- `PACKAGE_ANNOUNCED` ✅
- `PACKAGE_RECEIVED`
- `PACKAGE_DELIVERED`
- `PACKAGE_CANCELLED`
- `PAYMENT_DUE`
- `CUSTOM_MESSAGE`

---

### 2. ❌ Parámetros incorrectos en `send_sms_by_event()`

**Problema:** El método `send_sms_by_event()` requiere un objeto `SMSByEventRequest`, no parámetros individuales.

**Antes:**
```python
await sms_service.send_sms_by_event(
    db=db,
    event_type=NotificationEvent.ANNOUNCEMENT,
    recipient=db_announcement.customer_phone,  # ❌ Parámetro incorrecto
    announcement_id=db_announcement.id
)
```

**Correcto:**
```python
await sms_service.send_sms_by_event(
    db=db,
    event_request=SMSByEventRequest(  # ✅ Objeto correcto
        event_type=NotificationEvent.PACKAGE_ANNOUNCED,
        announcement_id=db_announcement.id,
        custom_variables={...},
        priority=NotificationPriority.ALTA
    )
)
```

---

### 3. ❌ Método `_get_event_recipient()` no maneja anuncios

**Archivo:** `sms_service.py` línea ~560

**Antes:**
```python
async def _get_event_recipient(...):
    # ...
    # announcement_id ya no se usa (PackageAnnouncementNew eliminado)
    # Si se necesita en el futuro, usar Package directamente
    return None  # ❌ Siempre retorna None para anuncios
```

**Problema:** El comentario decía que `PackageAnnouncementNew` fue eliminado, pero en realidad **SÍ existe** y tiene el campo `customer_phone`.

---

## ✅ Soluciones Aplicadas

### 1. Corregir evento y parámetros en `announcements.py`

**Archivo:** `CODE/src/app/routes/announcements.py`

```python
# Enviar SMS de confirmación
try:
    from app.schemas.notification import SMSByEventRequest
    from app.models.notification import NotificationPriority
    
    sms_service = SMSService()
    
    # Preparar variables para el SMS
    custom_variables = {
        "guide_number": db_announcement.guide_number,
        "consult_code": db_announcement.tracking_code,
        "tracking_code": db_announcement.tracking_code,
        "customer_name": db_announcement.customer_name,
        "tracking_url": f"{settings.tracking_base_url}?auto_search={db_announcement.tracking_code}"
    }
    
    # Enviar SMS usando el evento correcto
    sms_result = await sms_service.send_sms_by_event(
        db=db,
        event_request=SMSByEventRequest(
            event_type=NotificationEvent.PACKAGE_ANNOUNCED,  # ✅ Evento correcto
            package_id=None,
            customer_id=None,
            announcement_id=db_announcement.id,  # ✅ ID del anuncio
            custom_variables=custom_variables,
            priority=NotificationPriority.ALTA,
            is_test=False
        )
    )
    
    if sms_result.status == "sent":
        logger.info(f"✅ SMS enviado para anuncio {db_announcement.id}")
    else:
        logger.warning(f"⚠️ SMS falló: {sms_result.message}")
        
except Exception as sms_error:
    logger.error(f"❌ Error al enviar SMS: {sms_error}", exc_info=True)
```

---

### 2. Actualizar `_get_event_recipient()` en `sms_service.py`

**Archivo:** `CODE/src/app/services/sms_service.py`

```python
async def _get_event_recipient(
    self,
    db: Session,
    event_type: NotificationEvent,
    package_id: Optional[str],
    customer_id: Optional[str],
    announcement_id: Optional[str]
) -> Optional[str]:
    """
    Determina el destinatario basado en el evento
    Prioridad: customer_id > package_id > announcement_id
    """
    if customer_id:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if customer and hasattr(customer, 'phone'):
            return customer.phone

    if package_id:
        package = db.query(Package).filter(Package.id == package_id).first()
        if package and package.customer and hasattr(package.customer, 'phone'):
            return package.customer.phone

    # ✅ Obtener teléfono del anuncio si está disponible
    if announcement_id:
        from app.models.announcement_new import PackageAnnouncementNew
        announcement = db.query(PackageAnnouncementNew).filter(
            PackageAnnouncementNew.id == announcement_id
        ).first()
        if announcement and hasattr(announcement, 'customer_phone'):
            return announcement.customer_phone

    return None
```

---

### 3. Actualizar `_prepare_event_variables()` en `sms_service.py`

**Archivo:** `CODE/src/app/services/sms_service.py`

```python
# Variables específicas por evento
if event_type == NotificationEvent.PACKAGE_ANNOUNCED and announcement_id:
    # ✅ Obtener datos del anuncio
    from app.models.announcement_new import PackageAnnouncementNew
    announcement = db.query(PackageAnnouncementNew).filter(
        PackageAnnouncementNew.id == announcement_id
    ).first()
    if announcement:
        variables.update({
            "guide_number": announcement.guide_number,
            "consult_code": announcement.tracking_code,
            "tracking_code": announcement.tracking_code,
            "customer_name": announcement.customer_name,
            "tracking_url": f"{settings.tracking_base_url}?auto_search={announcement.tracking_code}"
        })
```

---

## 🧪 Cómo Probar

### 1. Ejecutar diagnóstico

```bash
cd CODE
python diagnostico_sms_anuncio.py
```

Esto verificará:
- ✅ Si el anuncio existe
- ✅ Si se intentó enviar SMS
- ✅ Estado de las notificaciones
- ✅ Configuración SMS
- ✅ Plantillas disponibles

---

### 2. Reiniciar la aplicación

```bash
# Detener la aplicación actual
# Reiniciar para cargar el código actualizado
```

---

### 3. Crear un nuevo anuncio de prueba

**Opción A: Desde la interfaz web**
1. Ir a `/announce`
2. Llenar el formulario
3. Enviar

**Opción B: Desde API**
```bash
curl -X POST http://localhost:8000/api/announcements/ \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Juan Pérez",
    "customer_phone": "3001234567",
    "guide_number": "TEST001"
  }'
```

---

### 4. Verificar logs

```bash
# Ver logs en tiempo real
tail -f logs/app.log | grep -i sms

# Buscar mensajes específicos:
# ✅ "SMS enviado para anuncio"
# ⚠️ "SMS falló"
# ❌ "Error al enviar SMS"
```

---

### 5. Verificar en base de datos

```sql
-- Ver notificaciones SMS del anuncio
SELECT 
    n.id,
    n.notification_type,
    n.event_type,
    n.status,
    n.recipient,
    n.message,
    n.error_message,
    n.created_at
FROM notifications n
WHERE n.announcement_id = 'ID_DEL_ANUNCIO'
AND n.notification_type = 'sms';
```

---

## 📋 Checklist de Validación

- [ ] Código actualizado en `announcements.py`
- [ ] Código actualizado en `sms_service.py` (2 métodos)
- [ ] Aplicación reiniciada
- [ ] Plantillas SMS migradas (si no lo hiciste antes)
- [ ] Configuración SMS activa en BD
- [ ] Credenciales Liwa.co configuradas
- [ ] Nuevo anuncio creado
- [ ] SMS recibido en el teléfono
- [ ] Notificación registrada en BD con status "sent"

---

## 🔄 Flujo Correcto (Después de la Corrección)

```
1. Usuario crea anuncio
   POST /api/announcements/
   
2. Se crea registro en BD
   PackageAnnouncementNew
   
3. Se llama a send_sms_by_event()
   ✅ event_type = PACKAGE_ANNOUNCED
   ✅ announcement_id = db_announcement.id
   
4. Se obtiene plantilla
   ✅ status_change_unified
   
5. Se preparan variables
   ✅ guide_number, consult_code, status_text, etc.
   
6. Se obtiene destinatario
   ✅ announcement.customer_phone
   
7. Se renderiza mensaje
   "PAQUETES: Su paquete DSE4GS está ANUNCIADO. Código: HTE3..."
   
8. Se envía SMS via Liwa.co
   POST https://api.liwa.co/v2/sms/single
   
9. Se registra en BD
   Notification (status=sent)
   
10. Cliente recibe SMS ✅
```

---

## 🚨 Si Aún No Funciona

### Verificar plantillas SMS

```bash
cd CODE
python -m src.scripts.migrate_sms_templates_unified
# Opción 3: Ver plantillas actuales
```

Debe mostrar:
```
✅ ACTIVA ⭐ DEFAULT status_change_unified
```

Si no existe, ejecutar:
```bash
python -m src.scripts.migrate_sms_templates_unified
# Opción 1: Migrar a plantillas unificadas
```

---

### Verificar configuración Liwa.co

```python
# En Python shell
from app.database import SessionLocal
from app.models.notification import SMSConfiguration

db = SessionLocal()
config = db.query(SMSConfiguration).filter(SMSConfiguration.is_active == True).first()

print(f"Proveedor: {config.provider}")
print(f"API Key: {config.api_key[:10]}...")
print(f"Account: {config.account_id}")
print(f"Activa: {config.is_active}")
print(f"Modo test: {config.enable_test_mode}")
```

---

### Probar SMS manualmente

```python
# En Python shell
import asyncio
from app.database import SessionLocal
from app.services.sms_service import SMSService

db = SessionLocal()
sms_service = SMSService()

# Enviar SMS de prueba
result = asyncio.run(sms_service.send_sms(
    db=db,
    recipient="+573001234567",  # Tu número
    message="Test desde diagnóstico",
    is_test=True  # Cambiar a False para envío real
))

print(f"Status: {result.status}")
print(f"Message: {result.message}")
```

---

## 📞 Soporte

Si después de aplicar estas correcciones el SMS aún no se envía:

1. Ejecutar `python diagnostico_sms_anuncio.py`
2. Revisar logs completos
3. Verificar credenciales Liwa.co
4. Probar SMS manual (código arriba)
5. Contactar soporte de Liwa.co si el problema es con la API

---

## ✅ Resumen

**Problema:** SMS no se enviaba al anunciar paquetes

**Causa raíz:** 
1. Evento incorrecto (`ANNOUNCEMENT` no existe)
2. Parámetros incorrectos (no usaba `SMSByEventRequest`)
3. Método `_get_event_recipient()` no manejaba anuncios

**Solución:**
1. ✅ Corregir evento a `PACKAGE_ANNOUNCED`
2. ✅ Usar `SMSByEventRequest` correctamente
3. ✅ Actualizar `_get_event_recipient()` para obtener teléfono del anuncio
4. ✅ Actualizar `_prepare_event_variables()` para obtener datos del anuncio

**Próximos pasos:**
1. Reiniciar aplicación
2. Crear nuevo anuncio de prueba
3. Verificar que se reciba SMS

---

**Versión:** 1.0.0  
**Fecha:** 2025-01-24  
**Autor:** Equipo de Desarrollo
