# 🚀 Guía Rápida de Uso: Sistema de Preferencias de Notificaciones

## 📋 Pasos para Empezar

### **Paso 1: Ejecutar Migraciones de Base de Datos**

```bash
cd CODE

# Ejecutar todas las migraciones pendientes
alembic upgrade head

# Deberías ver:
# INFO  [alembic.runtime.migration] Running upgrade -> add_blocked_status
# INFO  [alembic.runtime.migration] Running upgrade add_blocked_status -> create_customer_prefs
```

### **Paso 2: Reiniciar la Aplicación**

```bash
# Si usas Docker
docker-compose restart

# Si usas otro método
# Reinicia tu servidor FastAPI
```

### **Paso 3: Verificar que Funciona**

```bash
# Verificar que la tabla se creó
psql -U postgres -d paquetex_db -c "SELECT * FROM customer_preferences LIMIT 1;"

# Verificar que las rutas están disponibles
curl http://localhost:8000/api/customer/preferences/create
```

---

## 🎯 Casos de Uso Prácticos

### **Caso 1: Enviar Notificación a un Cliente**

```python
# En tu código donde envías notificaciones (ej: routes/packages.py)

from app.services.sms_service import SMSService
from app.models.notification import NotificationEvent

async def notify_package_received(db: Session, package: Package):
    """Notifica al cliente que su paquete fue recibido"""
    
    if not package.customer:
        return
    
    sms_service = SMSService()
    
    # Enviar SMS
    if package.customer.phone:
        await sms_service.send_sms(
            db=db,
            recipient=package.customer.phone,
            message=f"PAQUETEX: Su paquete {package.tracking_number} ha sido RECIBIDO",
            event_type=NotificationEvent.PACKAGE_RECEIVED,
            customer_id=package.customer.id,  # ← IMPORTANTE: Pasar customer_id
            is_test=False
        )
        # ✅ El sistema verifica automáticamente si el cliente permite SMS
        # ✅ Si el cliente desactivó notificaciones → NO se envía
```

**Resultado:**
- Si el cliente NO tiene preferencias → Se envía (comportamiento por defecto)
- Si el cliente tiene preferencias y las permite → Se envía
- Si el cliente desactivó notificaciones → NO se envía (se registra como "blocked")

---

### **Caso 2: Crear Preferencias para un Cliente**

```python
# Opción A: Crear preferencias manualmente (ej: en un endpoint admin)

from app.utils.customer_preferences_helper import get_or_create_customer_preferences

@router.post("/admin/customers/{customer_id}/create-preferences")
async def create_customer_preferences(
    customer_id: UUID,
    db: Session = Depends(get_db)
):
    # Crear o obtener preferencias
    prefs = get_or_create_customer_preferences(db, customer_id)
    
    # Obtener URL para el cliente
    from app.utils.customer_preferences_helper import get_preferences_url
    prefs_url = get_preferences_url(db, customer_id)
    
    return {
        "success": True,
        "token": prefs.token,
        "url": prefs_url
    }
```

```python
# Opción B: Crear automáticamente al enviar primera notificación

from app.utils.customer_preferences_helper import (
    get_or_create_customer_preferences,
    get_preferences_url,
    add_preferences_footer_to_sms
)

async def send_first_notification(db: Session, customer: Customer):
    # Crear preferencias automáticamente
    prefs = get_or_create_customer_preferences(db, customer.id)
    
    # Obtener URL de preferencias
    prefs_url = get_preferences_url(db, customer.id)
    
    # Crear mensaje con link
    message = f"PAQUETEX: Bienvenido! Tu paquete ha sido recibido."
    message = add_preferences_footer_to_sms(message, prefs_url)
    
    # Enviar SMS
    sms_service = SMSService()
    await sms_service.send_sms(
        db=db,
        recipient=customer.phone,
        message=message,
        event_type=NotificationEvent.PACKAGE_RECEIVED,
        customer_id=customer.id
    )
```

---

### **Caso 3: Enviar Email con Link de Preferencias**

```python
from app.services.email_service import EmailService
from app.utils.customer_preferences_helper import (
    get_preferences_url,
    add_preferences_footer_to_email
)

async def send_package_notification_email(db: Session, customer: Customer, package: Package):
    # Obtener URL de preferencias
    prefs_url = get_preferences_url(db, customer.id)
    
    # Crear contenido HTML
    html_content = f"""
    <h1>Paquete Recibido</h1>
    <p>Hola {customer.full_name},</p>
    <p>Tu paquete con guía {package.tracking_number} ha sido recibido.</p>
    """
    
    # Agregar footer con link de preferencias
    html_content = add_preferences_footer_to_email(html_content, prefs_url)
    
    # Enviar email
    email_service = EmailService()
    await email_service.send_email(
        db=db,
        recipient=customer.email,
        subject="Paquete Recibido - PAQUETEX",
        html_content=html_content,
        event_type=NotificationEvent.PACKAGE_RECEIVED,
        customer_id=customer.id
    )
```

---

### **Caso 4: Verificar si un Cliente Permite Notificaciones**

```python
from app.models.customer_preferences import CustomerPreferences
from app.models.notification import NotificationType, NotificationEvent

def can_send_notification(db: Session, customer_id: UUID, notification_type: str, event_type: str) -> bool:
    """Verifica si se puede enviar una notificación a un cliente"""
    
    # Buscar preferencias del cliente
    prefs = db.query(CustomerPreferences).filter(
        CustomerPreferences.customer_id == customer_id
    ).first()
    
    # Si no tiene preferencias, permitir (comportamiento por defecto)
    if not prefs:
        return True
    
    # Verificar preferencias
    return prefs.should_send_notification(notification_type, event_type)

# Uso:
if can_send_notification(db, customer.id, NotificationType.SMS, NotificationEvent.PACKAGE_RECEIVED):
    # Enviar SMS
    pass
else:
    print("Cliente bloqueó notificaciones de paquetes recibidos")
```

---

### **Caso 5: Obtener Link de Preferencias para un Cliente**

```python
from app.utils.customer_preferences_helper import get_preferences_url

# En cualquier parte de tu código
prefs_url = get_preferences_url(db, customer.id)

print(f"Link de preferencias: {prefs_url}")
# Resultado: https://paquetex.com/customer/preferences?token=abc123xyz...

# Puedes enviar este link por:
# - SMS
# - Email
# - WhatsApp
# - Mostrar en interfaz web
```

---

## 🧪 Pruebas Paso a Paso

### **Prueba 1: Crear Preferencias para un Cliente**

```bash
# 1. Obtener ID de un cliente existente
psql -U postgres -d paquetex_db -c "SELECT id, full_name, phone FROM customers LIMIT 1;"

# 2. Crear preferencias usando la API
curl -X POST "http://localhost:8000/api/customer/preferences/create" \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "PEGAR-UUID-AQUI"}'

# 3. Copiar el token de la respuesta
# Respuesta:
# {
#   "success": true,
#   "token": "abc123xyz...",
#   "preferences_url": "/customer/preferences?token=abc123xyz"
# }
```

### **Prueba 2: Ver Página de Preferencias**

```bash
# Abrir en navegador:
http://localhost:8000/customer/preferences?token=PEGAR-TOKEN-AQUI

# Deberías ver:
# - Nombre del cliente
# - Teléfono y email
# - Toggles de preferencias
# - Botón "Guardar Preferencias"
```

### **Prueba 3: Modificar Preferencias**

1. En la página de preferencias, desactiva "SMS cuando llega paquete"
2. Haz clic en "Guardar Preferencias"
3. Deberías ver mensaje: "Preferencias guardadas correctamente"

### **Prueba 4: Verificar que se Respetan las Preferencias**

```python
# En Python shell o en tu código
from app.services.sms_service import SMSService
from app.models.notification import NotificationEvent
from app.database import SessionLocal

db = SessionLocal()
sms_service = SMSService()

# Enviar SMS al cliente que desactivó notificaciones
result = await sms_service.send_sms(
    db=db,
    recipient="+573001234567",  # Teléfono del cliente
    message="Prueba de notificación",
    event_type=NotificationEvent.PACKAGE_RECEIVED,
    customer_id="uuid-del-cliente"
)

print(result.status)  # Debería ser "blocked"
print(result.message)  # "Notificación bloqueada por preferencias del cliente"
```

### **Prueba 5: Verificar en Base de Datos**

```sql
-- Ver preferencias de clientes
SELECT 
    cp.id,
    c.full_name,
    c.phone,
    cp.sms_notifications_enabled,
    cp.email_notifications_enabled,
    cp.notify_package_received,
    cp.token
FROM customer_preferences cp
JOIN customers c ON c.id = cp.customer_id
LIMIT 10;

-- Ver notificaciones bloqueadas
SELECT 
    n.id,
    n.notification_type,
    n.event_type,
    n.recipient,
    n.status,
    n.error_message,
    n.created_at
FROM notifications n
WHERE n.status = 'blocked'
ORDER BY n.created_at DESC
LIMIT 10;
```

---

## 📱 Flujo Completo de Usuario Final

### **Desde la Perspectiva del Cliente:**

```
1. Cliente recibe SMS:
   "PAQUETEX: Su paquete X123 ha sido RECIBIDO
   
   Gestiona tus notificaciones: https://paquetex.com/customer/preferences?token=abc123"

2. Cliente hace clic en el link

3. Ve página con su información:
   - Nombre: Juan Pérez
   - Teléfono: +57 300 123 4567
   - Email: juan@example.com

4. Ve toggles de preferencias:
   ✅ Notificaciones por SMS
   ✅ Notificaciones por Email
   ✅ Paquete Anunciado
   ✅ Paquete Recibido
   ✅ Paquete Entregado
   ✅ Recordatorios de Pago
   ❌ Ofertas y Promociones

5. Cliente desactiva "Paquete Recibido"

6. Hace clic en "Guardar Preferencias"

7. Ve mensaje: "Preferencias guardadas correctamente"

8. Próxima vez que llegue un paquete:
   - NO recibe SMS de "Paquete Recibido"
   - SÍ recibe SMS de "Paquete Entregado" (sigue activado)
```

---

## 🔧 Integración en Código Existente

### **Opción 1: Modificar Código Existente**

Si ya tienes código que envía notificaciones, solo agrega `customer_id`:

```python
# ANTES
await sms_service.send_sms(
    db=db,
    recipient=customer.phone,
    message="Paquete recibido"
)

# DESPUÉS (solo agregar customer_id)
await sms_service.send_sms(
    db=db,
    recipient=customer.phone,
    message="Paquete recibido",
    event_type=NotificationEvent.PACKAGE_RECEIVED,
    customer_id=customer.id  # ← Solo agregar esta línea
)
```

### **Opción 2: Crear Función Helper**

```python
# En utils/notifications.py (crear si no existe)

from app.services.sms_service import SMSService
from app.services.email_service import EmailService
from app.utils.customer_preferences_helper import get_preferences_url

async def notify_customer(
    db: Session,
    customer: Customer,
    event_type: NotificationEvent,
    message: str,
    subject: str = None,
    html_content: str = None
):
    """
    Función helper para notificar a un cliente respetando sus preferencias
    """
    # SMS
    if customer.phone:
        sms_service = SMSService()
        await sms_service.send_sms(
            db=db,
            recipient=customer.phone,
            message=message,
            event_type=event_type,
            customer_id=customer.id
        )
    
    # Email
    if customer.email and html_content:
        email_service = EmailService()
        await email_service.send_email(
            db=db,
            recipient=customer.email,
            subject=subject or "Notificación PAQUETEX",
            html_content=html_content,
            event_type=event_type,
            customer_id=customer.id
        )

# Uso:
await notify_customer(
    db=db,
    customer=customer,
    event_type=NotificationEvent.PACKAGE_RECEIVED,
    message="Su paquete ha sido recibido",
    subject="Paquete Recibido",
    html_content="<h1>Paquete Recibido</h1>..."
)
```

---

## 📊 Monitoreo y Estadísticas

### **Ver Notificaciones Bloqueadas**

```python
from app.models.notification import Notification, NotificationStatus
from datetime import timedelta
from app.utils.datetime_utils import get_colombia_now

# Últimas 24 horas
start_date = get_colombia_now() - timedelta(days=1)

blocked = db.query(Notification).filter(
    Notification.status == NotificationStatus.BLOCKED,
    Notification.created_at >= start_date
).all()

print(f"Notificaciones bloqueadas: {len(blocked)}")

# Por tipo
sms_blocked = [n for n in blocked if n.notification_type == NotificationType.SMS]
email_blocked = [n for n in blocked if n.notification_type == NotificationType.EMAIL]

print(f"SMS bloqueados: {len(sms_blocked)}")
print(f"Emails bloqueados: {len(email_blocked)}")
```

### **Ver Clientes con Preferencias**

```sql
-- Clientes que han configurado preferencias
SELECT COUNT(*) FROM customer_preferences;

-- Clientes que desactivaron SMS
SELECT COUNT(*) 
FROM customer_preferences 
WHERE sms_notifications_enabled = false;

-- Clientes que desactivaron notificaciones de paquetes recibidos
SELECT COUNT(*) 
FROM customer_preferences 
WHERE notify_package_received = false;
```

---

## ⚠️ Troubleshooting

### **Problema: "Token inválido o preferencias no encontradas"**

**Solución:**
```python
# Verificar que el cliente tiene preferencias
from app.models.customer_preferences import CustomerPreferences

prefs = db.query(CustomerPreferences).filter(
    CustomerPreferences.customer_id == customer_id
).first()

if not prefs:
    # Crear preferencias
    from app.utils.customer_preferences_helper import get_or_create_customer_preferences
    prefs = get_or_create_customer_preferences(db, customer_id)
```

### **Problema: Las preferencias no se respetan**

**Verificar:**
1. ¿Estás pasando `customer_id` al enviar notificaciones?
2. ¿El cliente tiene preferencias en la BD?
3. ¿Los logs muestran "bloqueado por preferencias"?

```bash
# Ver logs
docker-compose logs -f app | grep "bloqueado"
```

### **Problema: La página de preferencias no carga**

**Verificar:**
1. ¿El token es válido?
2. ¿La ruta está registrada en main.py?
3. ¿El template existe en `templates/customer/preferences.html`?

```bash
# Verificar rutas
curl http://localhost:8000/customer/preferences?token=test
```

---

## 🎯 Resumen de Comandos Útiles

```bash
# Crear preferencias para un cliente
curl -X POST "http://localhost:8000/api/customer/preferences/create" \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "uuid"}'

# Ver preferencias de un cliente
curl "http://localhost:8000/api/customer/preferences?token=abc123"

# Actualizar preferencias
curl -X PUT "http://localhost:8000/api/customer/preferences?token=abc123" \
  -H "Content-Type: application/json" \
  -d '{
    "sms_notifications_enabled": false,
    "email_notifications_enabled": true,
    "notify_package_received": false
  }'

# Ver notificaciones bloqueadas en BD
psql -U postgres -d paquetex_db -c \
  "SELECT * FROM notifications WHERE status = 'blocked' ORDER BY created_at DESC LIMIT 10;"
```

---

## 📚 Recursos Adicionales

- **Documentación completa:** `IMPLEMENTACION_PREFERENCIAS_CLIENTES.md`
- **Guía de usuario:** `GUIA_USO_PREFERENCIAS_NOTIFICACIONES.md`
- **Opciones futuras:** `FUTURO_PREFERENCIAS_CLIENTES.md`

---

**¿Necesitas ayuda?** Revisa los logs y la documentación, o contacta al equipo de desarrollo.

**Fecha:** 2025-01-24  
**Versión:** PAQUETEX v3.1  
**Estado:** ✅ Listo para usar
