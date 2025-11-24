# 📊 Análisis Completo: Sistema de Notificaciones y Preferencias de Usuario

## 🔍 Estado Actual

### ✅ **Lo que SÍ funciona:**

#### 1. **Interfaz de Preferencias (Settings)**
- ✅ 7 toggles funcionales en `/settings?tab=notifications`
- ✅ API GET/PUT para cargar y guardar preferencias
- ✅ Modelo `UserPreferences` en base de datos
- ✅ Persistencia de preferencias por usuario

#### 2. **Servicios de Notificaciones**
- ✅ `SMSService` - Envío de SMS vía Liwa.co
- ✅ `EmailService` - Envío de emails vía SMTP
- ✅ `NotificationService` - Gestión de notificaciones
- ✅ Templates unificados para cambios de estado
- ✅ Sistema de eventos (`NotificationEvent`)

---

## ⚠️ **PROBLEMA CRÍTICO DETECTADO**

### 🚨 **Las preferencias NO se están verificando antes de enviar notificaciones**

**Evidencia:**
```python
# En SMSService.send_sms() - Línea ~130
async def send_sms(
    self,
    db: Session,
    recipient: str,
    message: str,
    ...
) -> SMSSendResponse:
    # ❌ NO HAY VERIFICACIÓN DE PREFERENCIAS
    # Envía directamente sin consultar UserPreferences
    
# En EmailService.send_email() - Línea ~150
async def send_email(
    self,
    db: Session,
    recipient: str,
    subject: str,
    ...
) -> Dict[str, Any]:
    # ❌ NO HAY VERIFICACIÓN DE PREFERENCIAS
    # Envía directamente sin consultar UserPreferences
```

**Resultado:** Los usuarios reciben notificaciones aunque las hayan desactivado en Settings.

---

## 🎯 **Cómo DEBERÍAN usarse las preferencias**

### **Escenarios de uso por campo:**

| Campo en UserPreferences | Cuándo verificar | Escenario de uso |
|--------------------------|------------------|------------------|
| `sms_notifications_enabled` | Antes de **cualquier** SMS | Usuario desactiva todos los SMS |
| `email_notifications_enabled` | Antes de **cualquier** email | Usuario desactiva todos los emails |
| `push_notifications_enabled` | Antes de notificaciones push | Usuario desactiva notificaciones del navegador |
| `notify_package_received` | Al recibir paquete | SMS/Email cuando paquete llega al sistema |
| `notify_package_delivered` | Al entregar paquete | SMS/Email cuando paquete se entrega al cliente |
| `notify_messages` | Al recibir mensaje | Notificaciones de mensajes internos |
| `additional_preferences['marketing_enabled']` | Envíos masivos/promociones | Campañas de marketing |

---

## 🔧 **Implementación Recomendada**

### **1. Crear método de verificación en UserPreferences**

```python
# En CODE/src/app/models/user_preferences.py

def should_send_notification(
    self, 
    notification_type: NotificationType,
    event_type: NotificationEvent
) -> bool:
    """
    Verifica si se debe enviar una notificación según las preferencias del usuario
    
    Args:
        notification_type: SMS, EMAIL, PUSH, etc.
        event_type: PACKAGE_RECEIVED, PACKAGE_DELIVERED, etc.
    
    Returns:
        bool: True si se debe enviar, False si está desactivado
    """
    # Verificar preferencia general por tipo
    if notification_type == NotificationType.SMS:
        if not self.sms_notifications_enabled:
            return False
    elif notification_type == NotificationType.EMAIL:
        if not self.email_notifications_enabled:
            return False
    elif notification_type == NotificationType.PUSH:
        if not self.push_notifications_enabled:
            return False
    
    # Verificar preferencia específica por evento
    if event_type == NotificationEvent.PACKAGE_RECEIVED:
        return self.notify_package_received
    elif event_type == NotificationEvent.PACKAGE_DELIVERED:
        return self.notify_package_delivered
    elif event_type == NotificationEvent.MESSAGE_RECEIVED:
        return self.notify_messages
    
    # Por defecto, permitir notificaciones críticas
    return True
```

### **2. Modificar SMSService para verificar preferencias**

```python
# En CODE/src/app/services/sms_service.py

async def send_sms(
    self,
    db: Session,
    recipient: str,
    message: str,
    event_type: NotificationEvent = NotificationEvent.CUSTOM_MESSAGE,
    priority: NotificationPriority = NotificationPriority.MEDIA,
    package_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    user_id: Optional[int] = None,  # ← NUEVO: ID del usuario
    ...
) -> SMSSendResponse:
    """Envía un SMS individual"""
    try:
        # ✅ NUEVO: Verificar preferencias del usuario
        if user_id:
            from app.models.user_preferences import UserPreferences
            user_prefs = db.query(UserPreferences).filter(
                UserPreferences.user_id == user_id
            ).first()
            
            if user_prefs:
                # Verificar si el usuario permite este tipo de notificación
                if not user_prefs.should_send_notification(
                    NotificationType.SMS, 
                    event_type
                ):
                    logger.info(f"SMS bloqueado por preferencias del usuario {user_id}")
                    return SMSSendResponse(
                        notification_id=None,
                        status="blocked",
                        message="Notificación bloqueada por preferencias del usuario",
                        cost_cents=0
                    )
        
        # Continuar con el envío normal...
        self._validate_phone_number(recipient)
        config = self.get_sms_config(db)
        # ... resto del código
```

### **3. Modificar EmailService para verificar preferencias**

```python
# En CODE/src/app/services/email_service.py

async def send_email(
    self,
    db: Session,
    recipient: str,
    subject: str,
    html_content: str,
    event_type: NotificationEvent = NotificationEvent.CUSTOM_MESSAGE,
    user_id: Optional[int] = None,  # ← NUEVO: ID del usuario
    ...
) -> Dict[str, Any]:
    """Envía un email individual"""
    try:
        # ✅ NUEVO: Verificar preferencias del usuario
        if user_id:
            from app.models.user_preferences import UserPreferences
            user_prefs = db.query(UserPreferences).filter(
                UserPreferences.user_id == user_id
            ).first()
            
            if user_prefs:
                if not user_prefs.should_send_notification(
                    NotificationType.EMAIL, 
                    event_type
                ):
                    logger.info(f"Email bloqueado por preferencias del usuario {user_id}")
                    return {
                        "success": False,
                        "status": "blocked",
                        "message": "Notificación bloqueada por preferencias del usuario"
                    }
        
        # Continuar con el envío normal...
        self._validate_smtp_config()
        # ... resto del código
```

---

## 📍 **Puntos de integración en el sistema**

### **Dónde se envían notificaciones actualmente:**

#### 1. **Cambios de estado de paquetes**
```python
# Cuando un paquete cambia de estado (RECIBIDO, ENTREGADO, etc.)
# Ubicación probable: routes/packages.py o services/package_service.py

# ANTES (sin verificar preferencias):
await sms_service.send_sms(
    db=db,
    recipient=customer.phone,
    message="Su paquete ha sido recibido",
    event_type=NotificationEvent.PACKAGE_RECEIVED,
    package_id=package.id
)

# DESPUÉS (verificando preferencias):
await sms_service.send_sms(
    db=db,
    recipient=customer.phone,
    message="Su paquete ha sido recibido",
    event_type=NotificationEvent.PACKAGE_RECEIVED,
    package_id=package.id,
    user_id=customer.user_id  # ← Agregar user_id
)
```

#### 2. **Reset de contraseña**
```python
# En notification_service.py - send_password_reset_email()
# Ya existe, solo necesita agregar verificación de preferencias

# DESPUÉS:
if user_prefs and not user_prefs.email_notifications_enabled:
    # No enviar email si el usuario desactivó emails
    logger.info(f"Email de reset bloqueado para usuario {user.id}")
    return False
```

#### 3. **Anuncios de paquetes**
```python
# Cuando se anuncia un nuevo paquete
# Ubicación: routes/announcements.py o similar

await sms_service.send_sms_by_event(
    db=db,
    event_request=SMSByEventRequest(
        event_type=NotificationEvent.PACKAGE_ANNOUNCED,
        announcement_id=announcement.id,
        user_id=customer.user_id  # ← Agregar
    )
)
```

#### 4. **Recordatorios de pago**
```python
# Cuando hay un pago pendiente
await sms_service.send_sms(
    db=db,
    recipient=customer.phone,
    message=f"Pago pendiente: ${amount}",
    event_type=NotificationEvent.PAYMENT_DUE,
    package_id=package.id,
    user_id=customer.user_id  # ← Agregar
)
```

#### 5. **Mensajes personalizados**
```python
# Cuando un admin envía un mensaje a un cliente
await sms_service.send_sms(
    db=db,
    recipient=customer.phone,
    message=custom_message,
    event_type=NotificationEvent.CUSTOM_MESSAGE,
    user_id=customer.user_id  # ← Agregar
)
```

---

## 🔐 **Excepciones: Notificaciones que SIEMPRE se envían**

Algunas notificaciones son críticas y deben enviarse independientemente de las preferencias:

```python
# Notificaciones críticas que ignoran preferencias:
CRITICAL_EVENTS = [
    NotificationEvent.SECURITY_ALERT,      # Alertas de seguridad
    NotificationEvent.ACCOUNT_LOCKED,      # Cuenta bloqueada
    NotificationEvent.PASSWORD_CHANGED,    # Contraseña cambiada
    NotificationEvent.LEGAL_NOTICE,        # Avisos legales
]

def should_send_notification(self, notification_type, event_type):
    # Siempre enviar notificaciones críticas
    if event_type in CRITICAL_EVENTS:
        return True
    
    # Verificar preferencias para el resto...
```

---

## 📋 **Checklist de implementación**

### **Fase 1: Preparación**
- [ ] Agregar método `should_send_notification()` a `UserPreferences`
- [ ] Agregar campo `user_id` a los métodos de envío
- [ ] Definir lista de eventos críticos

### **Fase 2: Modificar servicios**
- [ ] Actualizar `SMSService.send_sms()` para verificar preferencias
- [ ] Actualizar `EmailService.send_email()` para verificar preferencias
- [ ] Actualizar `send_sms_by_event()` para pasar `user_id`
- [ ] Actualizar `send_email_by_event()` para pasar `user_id`

### **Fase 3: Actualizar llamadas**
- [ ] Buscar todos los `send_sms()` en el código
- [ ] Buscar todos los `send_email()` en el código
- [ ] Agregar `user_id` a cada llamada
- [ ] Obtener `user_id` desde `customer.user_id` o `package.customer.user_id`

### **Fase 4: Testing**
- [ ] Probar desactivar SMS en settings
- [ ] Probar desactivar emails en settings
- [ ] Probar desactivar notificaciones específicas
- [ ] Verificar que notificaciones críticas siempre se envían
- [ ] Probar con usuarios sin preferencias (usar defaults)

---

## 🎯 **Beneficios de la implementación**

1. **Cumplimiento legal**: Respetar preferencias de usuario (GDPR, CCPA)
2. **Mejor experiencia**: Usuarios controlan sus notificaciones
3. **Ahorro de costos**: No enviar SMS innecesarios (cada SMS cuesta dinero)
4. **Reducción de spam**: Menos quejas de usuarios
5. **Profesionalismo**: Sistema más robusto y confiable

---

## 📊 **Ejemplo de flujo completo**

```
1. Usuario entra a /settings?tab=notifications
   ↓
2. Desactiva "SMS cuando llega paquete"
   ↓
3. Se guarda: notify_package_received = False
   ↓
4. Llega un paquete nuevo al sistema
   ↓
5. Sistema intenta enviar SMS
   ↓
6. SMSService verifica UserPreferences
   ↓
7. Encuentra notify_package_received = False
   ↓
8. ❌ NO envía el SMS
   ↓
9. Registra en logs: "SMS bloqueado por preferencias"
   ↓
10. Usuario NO recibe SMS (como lo configuró)
```

---

## 🚀 **Próximos pasos recomendados**

1. **Implementar verificación de preferencias** (Fase 1-2)
2. **Buscar y actualizar todas las llamadas** (Fase 3)
3. **Agregar tests unitarios** para verificación de preferencias
4. **Documentar en el código** qué notificaciones respetan preferencias
5. **Agregar métricas** de notificaciones bloqueadas por preferencias

---

## 📝 **Notas adicionales**

- **Customer vs User**: Algunos clientes pueden no tener cuenta de usuario. En ese caso, usar preferencias por defecto (enviar todo).
- **Marketing**: El campo `marketing` en `additional_preferences` debe verificarse para envíos masivos/promocionales.
- **Logs**: Registrar cuando se bloquea una notificación para auditoría.
- **Dashboard**: Agregar métricas de "notificaciones bloqueadas por preferencias" en el panel de admin.

---

**Fecha de análisis:** 2025-01-24  
**Versión del sistema:** PAQUETEX v3.1  
**Estado:** ⚠️ Preferencias configuradas pero NO implementadas en servicios
