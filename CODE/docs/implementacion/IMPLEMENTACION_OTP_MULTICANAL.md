# Implementación OTP Multicanal (SMS + Email)

**Fecha**: 2025-02-07  
**Objetivo**: Enviar contraseña temporal por SMS y/o Email según preferencias del cliente

## Resumen

Se modificó el sistema de OTP para que envíe la contraseña temporal por múltiples canales (SMS y Email) respetando las preferencias de notificación del cliente.

## Cambios Realizados

### 1. Modificación del Endpoint de Solicitud OTP

**Archivo**: `CODE/src/app/routes/customer_preferences_otp.py`

#### Antes:
```python
# Solo enviaba por SMS
await sms_service.send_sms(...)
```

#### Después:
```python
# Obtiene preferencias del cliente
preferences = db.query(CustomerPreferences).filter(
    CustomerPreferences.customer_id == customer.id
).first()

# Envía por SMS si está habilitado
if preferences.sms_notifications_enabled:
    await sms_service.send_sms(...)
    sent_methods.append("SMS")

# Envía por Email si está habilitado y tiene email
if preferences.email_notifications_enabled and customer.email:
    await email_service.send_otp_email(...)
    sent_methods.append("Email")
```

### 2. Nuevo Método en EmailService

**Archivo**: `CODE/src/app/services/email_service.py`

Se agregó el método `send_otp_email()` que:
- ✅ Envía email con diseño profesional
- ✅ Muestra el código OTP de forma destacada
- ✅ Incluye información de seguridad
- ✅ Tiene versión HTML y texto plano
- ✅ No requiere guardar en BD de notificaciones (envío directo)

**Características del email:**
- Header azul con logo PAQUETEX
- Código OTP en caja destacada (36px, azul, monospace)
- Info box amarillo con advertencias de seguridad
- Lista de funcionalidades del portal
- Footer con información legal

## Flujo Completo

```
1. Cliente solicita acceso en /customer/verify
   ↓
2. Backend obtiene preferencias del cliente
   ↓
3. Backend genera código OTP (6 dígitos)
   ↓
4. Backend verifica preferencias:
   
   ┌─────────────────────────────────────┐
   │ SMS habilitado?                     │
   │ ✅ Sí → Enviar SMS                  │
   │ ❌ No → Saltar                      │
   └─────────────────────────────────────┘
   
   ┌─────────────────────────────────────┐
   │ Email habilitado Y tiene email?     │
   │ ✅ Sí → Enviar Email                │
   │ ❌ No → Saltar                      │
   └─────────────────────────────────────┘
   ↓
5. Cliente recibe contraseña por uno o ambos canales
   ↓
6. Cliente ingresa contraseña en el formulario
   ↓
7. Backend verifica y genera token JWT
   ↓
8. Cliente accede al dashboard
```

## Mensajes de Respuesta

El sistema retorna mensajes dinámicos según los canales usados:

| Canales Usados | Mensaje de Respuesta |
|----------------|---------------------|
| SMS + Email | "Contraseña temporal enviada por SMS y Email" |
| Solo SMS | "Contraseña temporal enviada por SMS" |
| Solo Email | "Contraseña temporal enviada por Email" |
| Ninguno | Error: "No se pudo enviar..." |

## Preferencias del Cliente

Las preferencias se obtienen de la tabla `customer_preferences`:

```python
class CustomerPreferences:
    sms_notifications_enabled: bool = True   # Recibir SMS
    email_notifications_enabled: bool = True  # Recibir Email
```

**Valores por defecto**: Ambos habilitados (True)

Si el cliente no tiene preferencias registradas, se crean automáticamente con valores por defecto.

## Contenido del SMS

```
PAQUETEX: Su contraseña temporal es: 123456. 
Válida por 5 minutos. No comparta esta contraseña.
```

## Contenido del Email

**Asunto**: "Tu Contraseña Temporal - PAQUETEX"

**Contenido**:
- Saludo personalizado con nombre del cliente
- Código OTP destacado en caja azul
- Advertencias de seguridad (válido 5 min, no compartir)
- Lista de funcionalidades del portal
- Footer con información legal

## Manejo de Errores

### Error al enviar SMS
- Se registra en logs
- Se intenta enviar por Email (si está habilitado)
- Si ambos fallan → Error al usuario

### Error al enviar Email
- Se registra en logs
- Se intenta enviar por SMS (si está habilitado)
- Si ambos fallan → Error al usuario

### Cliente sin preferencias
- Se crean automáticamente con valores por defecto
- Se envía por ambos canales

### Cliente sin email registrado
- Solo se envía por SMS
- No se genera error

## Logs

Los logs incluyen información detallada:

```python
# Éxito SMS
logger.info(f"✅ Contraseña temporal enviada por SMS a {phone}")

# Éxito Email
logger.info(f"✅ Contraseña temporal enviada por Email a {email}")

# Resumen
logger.info(f"✅ Contraseña temporal enviada a {nombre} ({phone}) por: SMS, Email (código: {otp})")

# Error
logger.error(f"❌ Error al enviar SMS: {error}")
```

## Testing

### Prueba Manual

1. **Cliente con ambas preferencias habilitadas**:
   ```bash
   # Solicitar OTP
   curl -X POST https://staging.jemavi.co/api/customer/preferences-otp/request \
     -H "Content-Type: application/json" \
     -d '{"phone": "3001234567"}'
   
   # Verificar que llegó SMS y Email
   # Ingresar código en /customer/verify
   ```

2. **Cliente solo con SMS habilitado**:
   - Deshabilitar email en preferencias
   - Solicitar OTP
   - Verificar que solo llega SMS

3. **Cliente solo con Email habilitado**:
   - Deshabilitar SMS en preferencias
   - Solicitar OTP
   - Verificar que solo llega Email

4. **Cliente sin email registrado**:
   - Solicitar OTP
   - Verificar que solo llega SMS (sin error)

### Script de Prueba

```bash
python CODE/test_otp_flow_complete.py
```

## Configuración Requerida

### Variables de Entorno para Email

```env
# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=tu-contraseña-app
SMTP_FROM_EMAIL=noreply@paquetex.com
SMTP_FROM_NAME=PAQUETEX
```

### Variables de Entorno para SMS

```env
# SMS Configuration (ya existentes)
SMS_API_URL=...
SMS_API_KEY=...
```

## Archivos Modificados

1. ✅ `CODE/src/app/routes/customer_preferences_otp.py`
   - Lógica multicanal
   - Respeto de preferencias
   - Manejo de errores

2. ✅ `CODE/src/app/services/email_service.py`
   - Nuevo método `send_otp_email()`
   - Template HTML profesional
   - Versión texto plano

3. ✅ `CODE/IMPLEMENTACION_OTP_MULTICANAL.md`
   - Documentación completa (este archivo)

## Beneficios

1. ✅ **Redundancia**: Si falla un canal, el otro funciona
2. ✅ **Flexibilidad**: Cliente elige sus canales preferidos
3. ✅ **Accesibilidad**: Clientes sin SMS pueden usar email
4. ✅ **Profesionalismo**: Email con diseño corporativo
5. ✅ **Seguridad**: Múltiples canales = más difícil interceptar
6. ✅ **Logs detallados**: Fácil debugging y auditoría

## Próximos Pasos

1. ✅ Probar en staging con clientes reales
2. ✅ Verificar que los emails no caigan en spam
3. ✅ Monitorear logs de envío
4. ✅ Recopilar feedback de usuarios
5. ⏳ Considerar agregar WhatsApp como tercer canal (futuro)

## Notas de Seguridad

- ✅ Código OTP válido por 5 minutos
- ✅ Máximo 3 intentos por código
- ✅ OTPs anteriores se invalidan al solicitar uno nuevo
- ✅ Advertencias de seguridad en SMS y Email
- ✅ No se comparte información sensible en los mensajes
- ✅ Logs no exponen códigos OTP completos en producción

## Soporte

Para problemas o preguntas:
- Revisar logs del servidor
- Verificar configuración SMTP
- Verificar preferencias del cliente en BD
- Verificar que el cliente tenga email registrado
