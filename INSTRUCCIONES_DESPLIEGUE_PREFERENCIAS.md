# 🚀 Instrucciones de Despliegue: Sistema de Preferencias de Notificaciones

## ✅ Cambios Implementados

Se implementó el sistema de verificación de preferencias de usuario para notificaciones SMS y Email.

---

## 📋 Pasos para Desplegar

### **1. Revisar los cambios**

Archivos modificados:
```bash
CODE/src/app/models/user_preferences.py
CODE/src/app/models/notification.py
CODE/src/app/services/sms_service.py
CODE/src/app/services/email_service.py
CODE/src/app/services/notification_service.py
```

### **2. Ejecutar migración de base de datos**

```bash
cd CODE

# Revisar la migración
cat alembic/versions/add_blocked_status_to_notifications.py

# Ejecutar migración
alembic upgrade head
```

**Nota:** La migración agrega:
- Estado `blocked` al enum `NotificationStatus`
- Nuevos eventos al enum `NotificationEvent`

### **3. Reiniciar la aplicación**

```bash
# Si usas Docker
docker-compose restart

# Si usas systemd
sudo systemctl restart paquetex

# Si usas PM2
pm2 restart paquetex
```

### **4. Verificar que funciona**

#### **Prueba 1: Verificar que la app inicia sin errores**
```bash
# Ver logs
docker-compose logs -f app
# o
tail -f /var/log/paquetex/app.log
```

Buscar errores relacionados con:
- `UserPreferences`
- `NotificationStatus`
- `NotificationEvent`

#### **Prueba 2: Probar la interfaz de settings**
1. Ir a `http://localhost:8000/settings?tab=notifications`
2. Verificar que los toggles funcionan
3. Cambiar algunas preferencias
4. Guardar y recargar la página
5. Verificar que los cambios persisten

#### **Prueba 3: Probar bloqueo de notificaciones**
1. Desactivar "SMS cuando llega paquete" en settings
2. Crear un paquete de prueba que dispare un SMS
3. Verificar en logs:
   ```
   📵 SMS bloqueado por preferencias del usuario X (evento: package_received)
   ```
4. Verificar en base de datos:
   ```sql
   SELECT * FROM notifications 
   WHERE status = 'blocked' 
   ORDER BY created_at DESC 
   LIMIT 10;
   ```

#### **Prueba 4: Probar notificaciones críticas**
1. Desactivar todos los emails en settings
2. Solicitar reset de contraseña
3. Verificar que el email **SÍ se envía** (evento crítico)

---

## 🔍 Verificación en Base de Datos

### **Verificar que el enum se actualizó:**

```sql
-- PostgreSQL
SELECT enumlabel 
FROM pg_enum 
WHERE enumtypid = 'notificationstatus'::regtype;

-- Debe incluir: pending, sent, delivered, failed, cancelled, blocked
```

```sql
-- Verificar eventos
SELECT enumlabel 
FROM pg_enum 
WHERE enumtypid = 'notificationevent'::regtype;

-- Debe incluir los nuevos eventos: message_received, marketing, security_alert, etc.
```

### **Verificar preferencias de usuarios:**

```sql
-- Ver preferencias de un usuario
SELECT * FROM user_preferences WHERE user_id = 1;

-- Ver usuarios sin preferencias
SELECT u.id, u.username, u.email 
FROM users u 
LEFT JOIN user_preferences up ON u.id = up.user_id 
WHERE up.id IS NULL;
```

### **Ver notificaciones bloqueadas:**

```sql
-- Últimas notificaciones bloqueadas
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
LIMIT 20;
```

---

## 📊 Monitoreo Post-Despliegue

### **1. Verificar logs de aplicación**

Buscar estas líneas en los logs:

```bash
# Notificaciones bloqueadas
grep "bloqueado por preferencias" /var/log/paquetex/app.log

# Errores relacionados con preferencias
grep -i "userpreferences" /var/log/paquetex/app.log | grep -i error
```

### **2. Métricas a monitorear**

```sql
-- Notificaciones por estado (últimos 7 días)
SELECT 
    status,
    COUNT(*) as total,
    notification_type
FROM notifications
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY status, notification_type
ORDER BY notification_type, status;

-- Tasa de bloqueo
SELECT 
    notification_type,
    COUNT(*) FILTER (WHERE status = 'blocked') as blocked,
    COUNT(*) as total,
    ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'blocked') / COUNT(*), 2) as block_rate
FROM notifications
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY notification_type;
```

### **3. Dashboard de admin**

Agregar estas métricas al dashboard de admin:
- Total de notificaciones bloqueadas (últimos 30 días)
- Tasa de bloqueo por tipo (SMS vs Email)
- Usuarios con más notificaciones bloqueadas
- Eventos más bloqueados

---

## 🐛 Troubleshooting

### **Error: "column 'blocked' does not exist in enum"**

**Solución:**
```bash
# Ejecutar migración manualmente
cd CODE
alembic upgrade head

# Si falla, ejecutar SQL directamente
psql -U postgres -d paquetex_db -c "ALTER TYPE notificationstatus ADD VALUE IF NOT EXISTS 'blocked';"
```

### **Error: "UserPreferences has no attribute 'should_send_notification'"**

**Solución:**
```bash
# Verificar que el archivo se actualizó
cat CODE/src/app/models/user_preferences.py | grep "should_send_notification"

# Reiniciar la aplicación
docker-compose restart
```

### **Las preferencias no se respetan**

**Verificar:**
1. ¿Se está pasando `user_id` al enviar notificaciones?
2. ¿El usuario tiene preferencias en la BD?
3. ¿Los logs muestran "bloqueado por preferencias"?

```python
# Debug en el código
import logging
logger = logging.getLogger(__name__)
logger.info(f"Enviando notificación a user_id={user_id}")
```

### **Notificaciones críticas se bloquean**

**Verificar:**
```python
# En user_preferences.py
CRITICAL_EVENTS = [
    NotificationEvent.SECURITY_ALERT,
    NotificationEvent.ACCOUNT_LOCKED,
    NotificationEvent.PASSWORD_CHANGED,
    NotificationEvent.PASSWORD_RESET,
    NotificationEvent.LEGAL_NOTICE,
]
```

---

## 🔄 Rollback (Si es necesario)

Si algo sale mal y necesitas revertir:

### **1. Revertir código**
```bash
git revert <commit_hash>
git push
```

### **2. Revertir migración**
```bash
cd CODE
alembic downgrade -1
```

**Nota:** No se puede eliminar valores de enum en PostgreSQL fácilmente. El downgrade no hace nada. Si necesitas revertir completamente, tendrías que:
1. Cambiar el código para no usar `BLOCKED`
2. Actualizar registros existentes: `UPDATE notifications SET status = 'failed' WHERE status = 'blocked';`

### **3. Reiniciar aplicación**
```bash
docker-compose restart
```

---

## ✅ Checklist de Despliegue

- [ ] Revisar cambios en los archivos
- [ ] Ejecutar migración de base de datos
- [ ] Reiniciar aplicación
- [ ] Verificar que la app inicia sin errores
- [ ] Probar interfaz de settings
- [ ] Probar bloqueo de notificaciones
- [ ] Probar notificaciones críticas
- [ ] Verificar logs
- [ ] Verificar métricas en BD
- [ ] Monitorear por 24 horas
- [ ] Documentar cualquier issue

---

## 📞 Soporte

Si encuentras problemas:

1. **Revisar logs:** `/var/log/paquetex/app.log`
2. **Revisar base de datos:** Queries de verificación arriba
3. **Revisar documentación:** 
   - `ANALISIS_NOTIFICACIONES.md`
   - `GUIA_USO_PREFERENCIAS_NOTIFICACIONES.md`
   - `RESUMEN_IMPLEMENTACION_PREFERENCIAS.md`

---

## 🎯 Resultado Esperado

Después del despliegue:

✅ Los usuarios pueden controlar sus notificaciones desde `/settings?tab=notifications`  
✅ El sistema respeta las preferencias automáticamente  
✅ Las notificaciones críticas siempre se envían  
✅ Se registran notificaciones bloqueadas con `status='blocked'`  
✅ Los logs muestran notificaciones bloqueadas  
✅ No hay errores en la aplicación  

---

**Fecha:** 2025-01-24  
**Versión:** PAQUETEX v3.1  
**Estado:** ✅ Listo para desplegar
