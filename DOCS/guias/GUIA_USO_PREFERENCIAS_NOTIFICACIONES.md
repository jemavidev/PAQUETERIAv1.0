# 📘 Guía de Uso: Sistema de Preferencias de Notificaciones

## ✅ Implementación Completada

El sistema de preferencias de notificaciones ahora está **completamente funcional**. Los usuarios pueden controlar qué notificaciones reciben desde `/settings?tab=notifications`.

---

## 🎯 Comportamiento por Defecto

**Todas las notificaciones están ACTIVADAS por defecto** (opt-out):
- ✅ SMS habilitados por defecto: `sms_notifications_enabled = False` (pero se puede activar)
- ✅ Emails habilitados por defecto: `email_notifications_enabled = True`
- ✅ Notificaciones de paquetes activadas: `notify_package_received = True`, `notify_package_delivered = True`
- ✅ Notificaciones de mensajes activadas: `notify_messages = True`
- ❌ Marketing desactivado por defecto: `marketing = False`

Los usuarios pueden desactivar lo que no quieran recibir.

---

## 🔧 Cómo Usar en el Código

### **1. Enviar SMS con verificación de preferencias**

```python
from app.services.sms_service import SMSService
from app.models.notification import NotificationEvent, NotificationPriority

sms_service = SMSService()

# Ejemplo: Notificar cuando llega un paquete
await sms_service.send_sms(
    db=db,
    recipient=customer.phone,
    message="Su paquete con guía X123 ha sido RECIBIDO",
    event_type=NotificationEvent.PACKAGE_RECEIVED,
    priority=NotificationPriority.MEDIA,
    package_id=package.id,
    user_id=customer.user_id,  # ← IMPORTANTE: Agregar user_id
    is_test=False
)
```

**¿Qué pasa?**
1. El servicio verifica si `customer.user_id` tiene preferencias
2. Si `notify_package_received = False`, NO envía el SMS
3. Crea un registro con `status = "blocked"`
4. Retorna `status="blocked"` sin costo

---

### **2. Enviar Email con verificación de preferencias**

```python
from app.services.email_service import EmailService
from app.models.notification import NotificationEvent, NotificationPriority

email_service = EmailService()

# Ejemplo: Notificar entrega de paquete
await email_service.send_email(
    db=db,
    recipient=customer.email,
    subject="Paquete entregado exitosamente",
    html_content=html_content,
    event_type=NotificationEvent.PACKAGE_DELIVERED,
    priority=NotificationPriority.MEDIA,
    package_id=package.id,
    user_id=customer.user_id,  # ← IMPORTANTE: Agregar user_id
    is_test=False
)
```

---

### **3. Enviar notificación por evento (automático)**

```python
from app.services.sms_service import SMSService
from app.schemas.notification import SMSByEventRequest

sms_service = SMSService()

# El servicio obtiene automáticamente el user_id del package/customer
await sms_service.send_sms_by_event(
    db=db,
    event_request=SMSByEventRequest(
        event_type=NotificationEvent.PACKAGE_RECEIVED,
        package_id=package.id,
        priority=NotificationPriority.MEDIA
    )
)
# ✅ Automáticamente verifica preferencias del usuario asociado al paquete
```

---

### **4. Envíos masivos con preferencias**

```python
# SMS masivo
await sms_service.send_bulk_sms(
    db=db,
    recipients=["+573001234567", "+573007654321"],
    message="Promoción especial...",
    event_type=NotificationEvent.MARKETING,
    user_ids=[user1.id, user2.id],  # ← Lista de user_ids
    is_test=False
)

# Email masivo
await email_service.send_bulk_emails(
    db=db,
    recipients=["user1@example.com", "user2@example.com"],
    subject="Promoción especial",
    html_content=html_content,
    event_type=NotificationEvent.MARKETING,
    user_ids=[user1.id, user2.id],  # ← Lista de user_ids
    is_test=False
)
```

**Resultado:**
- Solo se envía a usuarios con `marketing_enabled = True`
- Los demás reciben `status="blocked"`

---

## 🚨 Notificaciones Críticas (Siempre se envían)

Algunos eventos **IGNORAN las preferencias** por seguridad:

```python
CRITICAL_EVENTS = [
    NotificationEvent.SECURITY_ALERT,      # Alertas de seguridad
    NotificationEvent.ACCOUNT_LOCKED,      # Cuenta bloqueada
    NotificationEvent.PASSWORD_CHANGED,    # Contraseña cambiada
    NotificationEvent.PASSWORD_RESET,      # Reset de contraseña
    NotificationEvent.LEGAL_NOTICE,        # Avisos legales
]
```

**Ejemplo:**
```python
# Este email SIEMPRE se envía, sin importar preferencias
await email_service.send_email(
    db=db,
    recipient=user.email,
    subject="Restablecimiento de contraseña",
    html_content=html_content,
    event_type=NotificationEvent.PASSWORD_RESET,  # ← Crítico
    user_id=user.id
)
```

---

## 📊 Mapeo de Eventos a Preferencias

| Evento | Campo verificado | Descripción |
|--------|------------------|-------------|
| `PACKAGE_RECEIVED` | `notify_package_received` | Paquete recibido en sistema |
| `PACKAGE_DELIVERED` | `notify_package_delivered` | Paquete entregado al cliente |
| `MESSAGE_RECEIVED` | `notify_messages` | Mensaje interno recibido |
| `MARKETING` | `additional_preferences['marketing_enabled']` | Campañas promocionales |
| `PACKAGE_ANNOUNCED` | ✅ Siempre se envía | Anuncio de nuevo paquete |
| `PAYMENT_DUE` | ✅ Siempre se envía | Recordatorio de pago |
| `PASSWORD_RESET` | ✅ Siempre se envía (crítico) | Reset de contraseña |

---

## 🔍 Verificar si un usuario permite notificaciones

```python
from app.models.user_preferences import UserPreferences
from app.models.notification import NotificationType, NotificationEvent

# Obtener preferencias del usuario
user_prefs = db.query(UserPreferences).filter(
    UserPreferences.user_id == user_id
).first()

if user_prefs:
    # Verificar si permite SMS de paquetes recibidos
    can_send = user_prefs.should_send_notification(
        NotificationType.SMS,
        NotificationEvent.PACKAGE_RECEIVED
    )
    
    if can_send:
        print("✅ Usuario permite SMS de paquetes recibidos")
    else:
        print("❌ Usuario bloqueó SMS de paquetes recibidos")
```

---

## 📝 Obtener user_id desde diferentes entidades

### **Desde Customer:**
```python
customer = db.query(Customer).filter(Customer.id == customer_id).first()
user_id = customer.user_id if customer else None
```

### **Desde Package:**
```python
package = db.query(Package).filter(Package.id == package_id).first()
user_id = package.customer.user_id if package and package.customer else None
```

### **Desde User directamente:**
```python
user_id = user.id
```

---

## 🎯 Ejemplos de Uso Completos

### **Ejemplo 1: Notificar recepción de paquete**

```python
# En routes/packages.py o services/package_service.py

async def notify_package_received(db: Session, package: Package):
    """Notifica al cliente que su paquete fue recibido"""
    
    if not package.customer:
        return
    
    # Obtener user_id del cliente
    user_id = package.customer.user_id if hasattr(package.customer, 'user_id') else None
    
    # Enviar SMS
    if package.customer.phone:
        sms_service = SMSService()
        await sms_service.send_sms(
            db=db,
            recipient=package.customer.phone,
            message=f"PAQUETEX: Su paquete {package.tracking_number} ha sido RECIBIDO",
            event_type=NotificationEvent.PACKAGE_RECEIVED,
            package_id=package.id,
            user_id=user_id  # ← Verifica preferencias
        )
    
    # Enviar Email
    if package.customer.email:
        email_service = EmailService()
        await email_service.send_email_by_event(
            db=db,
            event_type=NotificationEvent.PACKAGE_RECEIVED,
            recipient=package.customer.email,
            variables={
                "customer_name": package.customer.full_name,
                "tracking_number": package.tracking_number,
                "received_at": package.received_at.strftime("%d/%m/%Y %H:%M")
            },
            package_id=package.id,
            user_id=user_id  # ← Verifica preferencias
        )
```

---

### **Ejemplo 2: Campaña de marketing**

```python
async def send_marketing_campaign(db: Session):
    """Envía campaña de marketing solo a usuarios que lo permiten"""
    
    from app.models.user import User
    from app.models.user_preferences import UserPreferences
    
    # Obtener usuarios con marketing habilitado
    users_with_marketing = db.query(User).join(UserPreferences).filter(
        UserPreferences.additional_preferences['marketing_enabled'].astext == 'true'
    ).all()
    
    recipients = [user.email for user in users_with_marketing]
    user_ids = [user.id for user in users_with_marketing]
    
    email_service = EmailService()
    result = await email_service.send_bulk_emails(
        db=db,
        recipients=recipients,
        subject="¡Oferta especial! 20% de descuento",
        html_content=marketing_html,
        event_type=NotificationEvent.MARKETING,
        user_ids=user_ids
    )
    
    print(f"Campaña enviada: {result['sent_count']} enviados, {result['blocked_count']} bloqueados")
```

---

### **Ejemplo 3: Notificación crítica (siempre se envía)**

```python
async def notify_password_changed(db: Session, user: User):
    """Notifica cambio de contraseña (crítico, siempre se envía)"""
    
    email_service = EmailService()
    
    await email_service.send_email(
        db=db,
        recipient=user.email,
        subject="Contraseña cambiada exitosamente",
        html_content=password_changed_html,
        event_type=NotificationEvent.PASSWORD_CHANGED,  # ← Crítico
        priority=NotificationPriority.ALTA,
        user_id=user.id  # Se pasa pero se ignora (evento crítico)
    )
    # ✅ Se envía SIEMPRE, sin importar preferencias
```

---

## 📊 Monitoreo de Notificaciones Bloqueadas

```python
from app.models.notification import Notification, NotificationStatus

# Obtener notificaciones bloqueadas en los últimos 7 días
from datetime import timedelta
from app.utils.datetime_utils import get_colombia_now

start_date = get_colombia_now() - timedelta(days=7)

blocked_notifications = db.query(Notification).filter(
    Notification.status == NotificationStatus.BLOCKED,
    Notification.created_at >= start_date
).all()

print(f"Notificaciones bloqueadas: {len(blocked_notifications)}")

# Por tipo
sms_blocked = [n for n in blocked_notifications if n.notification_type == NotificationType.SMS]
email_blocked = [n for n in blocked_notifications if n.notification_type == NotificationType.EMAIL]

print(f"SMS bloqueados: {len(sms_blocked)}")
print(f"Emails bloqueados: {len(email_blocked)}")
```

---

## ⚠️ Consideraciones Importantes

### **1. ¿Quién tiene preferencias de notificaciones?**

**SOLO USUARIOS REGISTRADOS** (tabla `users` con cuenta en el sistema):
- ✅ Administradores
- ✅ Operadores  
- ✅ Usuarios del sistema con acceso a `/settings`

**NO tienen preferencias:**
- ❌ **Clientes** (tabla `customers`) - No tienen `user_id` ni acceso a Settings
- ❌ Personas con solo email/teléfono de contacto

**Implicación:** Los clientes reciben TODAS las notificaciones de sus paquetes (no pueden desactivarlas). Esto es intencional para asegurar que reciban información importante.

### **2. Usuarios sin preferencias**
Si un usuario registrado no tiene registro en `UserPreferences`, se usan los **valores por defecto** (todo activado).

### **3. Clientes (Customers)**
Los `Customer` actualmente **NO tienen `user_id`**, por lo tanto:
- Reciben TODAS las notificaciones de sus paquetes
- No pueden acceder a `/settings` (no tienen cuenta)
- No pueden desactivar notificaciones
- Esto asegura que siempre reciban información de llegada/entrega de paquetes

### **4. Modo de prueba**
Las notificaciones con `is_test=True` **NO verifican preferencias** (siempre se envían).

### **5. Costos**
Las notificaciones bloqueadas tienen `cost_cents=0` (no se cobra).

### **6. Logs**
Todas las notificaciones bloqueadas se registran en logs:
```
📵 SMS bloqueado por preferencias del usuario 123 (evento: package_received)
📧❌ Email bloqueado por preferencias del usuario 456 (evento: package_delivered)
```

---

## 🚀 Migración de Código Existente

### **Antes (sin verificación):**
```python
await sms_service.send_sms(
    db=db,
    recipient=customer.phone,
    message="Paquete recibido"
)
```

### **Después (con verificación):**
```python
await sms_service.send_sms(
    db=db,
    recipient=customer.phone,
    message="Paquete recibido",
    event_type=NotificationEvent.PACKAGE_RECEIVED,
    user_id=customer.user_id  # ← Solo agregar esta línea
)
```

---

## 📋 Checklist para Desarrolladores

Al enviar una notificación, asegúrate de:

- [ ] Especificar el `event_type` correcto
- [ ] Pasar el `user_id` del destinatario
- [ ] Usar el evento crítico si es necesario (seguridad, legal)
- [ ] Manejar el caso cuando `user_id` es `None`
- [ ] Verificar el resultado (`status="blocked"`)

---

## 🎓 Resumen

1. **Todo activado por defecto** → Los usuarios desactivan lo que no quieren
2. **Agregar `user_id`** → El servicio verifica automáticamente
3. **Eventos críticos** → Siempre se envían (seguridad)
4. **Sin `user_id`** → Se envía normalmente (sin verificación)
5. **Modo test** → No verifica preferencias

---

**Fecha:** 2025-01-24  
**Versión:** PAQUETEX v3.1  
**Estado:** ✅ Implementado y funcional
