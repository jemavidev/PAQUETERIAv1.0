# 🔐 Implementación: Verificación OTP para Preferencias de Cliente

## 📋 Resumen

Sistema de verificación por OTP (código SMS) para que los clientes accedan de forma segura a sus preferencias de notificaciones, sin necesidad de crear cuentas o recordar contraseñas.

---

## 🎯 Características Principales

### ✅ **Vista 100% Pública**
- No requiere autenticación previa
- No requiere crear cuenta
- Acceso mediante verificación por SMS cada vez que se necesite

### ✅ **Flujo Seguro**
1. Cliente ingresa su teléfono
2. Sistema verifica que el cliente existe
3. Envía código OTP de 6 dígitos por SMS
4. Cliente verifica el código
5. Accede automáticamente a sus preferencias

### ✅ **Integración con Panel Admin**
- Administradores pueden enviar link de verificación por SMS
- Botón morado en `/customers/manage` para gestionar preferencias
- Copia rápida del link de verificación

---

## 🗂️ Archivos Creados/Modificados

### **Nuevos Archivos**

1. **`CODE/src/app/routes/customer_preferences_otp.py`**
   - Rutas API para OTP de preferencias
   - Endpoints:
     - `POST /api/customer/preferences-otp/request` - Solicitar código OTP
     - `POST /api/customer/preferences-otp/verify` - Verificar código y obtener token
     - `POST /api/customer/preferences-otp/send-link` - Enviar link por SMS (admin)

2. **`CODE/src/templates/customer/verify.html`**
   - Vista pública de verificación
   - Paso 1: Ingreso de teléfono
   - Paso 2: Verificación de código OTP
   - Countdown timer de 5 minutos
   - Opción de reenviar código

### **Archivos Modificados**

1. **`CODE/src/main.py`**
   - Agregado import de `customer_preferences_otp_router`
   - Registrado router en la aplicación

2. **`CODE/src/app/routes/views.py`**
   - Agregada ruta `GET /customer/verify` para la vista de verificación

3. **`CODE/src/app/config_routes.py`**
   - Agregadas rutas públicas:
     - `/customer/verify`
     - `/api/customer/preferences-otp/request`
     - `/api/customer/preferences-otp/verify`
     - `/api/customer/preferences-otp/send-link`

4. **`CODE/src/templates/customers/manage.html`**
   - Modificado modal de preferencias
   - Cambiado de mostrar link directo a link de verificación
   - Agregado botón "Enviar Link por SMS"
   - Actualizadas funciones JavaScript:
     - `openPreferencesModal()` - Obtiene teléfono del cliente
     - `copyVerifyUrl()` - Copia link de verificación
     - `sendVerifySMS()` - Envía SMS con link

---

## 🔗 URLs y Endpoints

### **Vistas Públicas**

| URL | Descripción |
|-----|-------------|
| `/customer/verify` | Vista de verificación OTP (pública) |
| `/customer/preferences?token=XXX` | Vista de preferencias (pública con token) |

### **APIs Públicas**

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/customer/preferences-otp/request` | POST | Solicitar código OTP |
| `/api/customer/preferences-otp/verify` | POST | Verificar código OTP |
| `/api/customer/preferences-otp/send-link` | POST | Enviar link por SMS (admin) |
| `/api/customer/preferences` | GET | Obtener preferencias con token |
| `/api/customer/preferences` | PUT | Actualizar preferencias con token |

---

## 📱 Flujo de Usuario

### **Opción 1: Cliente Auto-Acceso**

```
1. Cliente abre: https://staging.jemavi.co/customer/verify
2. Ingresa su número de teléfono
3. Click en "Enviar Código de Verificación"
4. Recibe SMS con código de 6 dígitos
5. Ingresa el código
6. Sistema valida y redirige a /customer/preferences?token=XXX
7. Cliente gestiona sus preferencias
```

### **Opción 2: Admin Envía Link**

```
1. Admin en /customers/manage
2. Click en botón morado 🔔 "Preferencias"
3. Modal muestra link de verificación
4. Admin puede:
   a) Copiar link y enviarlo manualmente
   b) Click en "📱 Enviar Link por SMS"
5. Cliente recibe SMS con link
6. Cliente abre link → va a /customer/verify
7. Sigue flujo de verificación OTP
```

---

## 🔒 Seguridad

### **Validaciones Implementadas**

✅ Solo clientes registrados y activos pueden solicitar OTP  
✅ Código OTP de 6 dígitos aleatorios  
✅ Expiración de 5 minutos  
✅ Máximo 3 intentos de verificación por código  
✅ Invalidación automática de OTPs anteriores  
✅ Token de preferencias único y permanente por cliente  
✅ Normalización y validación de números de teléfono  

### **Mensajes SMS**

**Solicitud de OTP:**
```
PAQUETEX: Su código para gestionar preferencias es: 123456. 
Válido por 5 minutos. No comparta este código.
```

**Envío de Link (Admin):**
```
PAQUETEX: Para gestionar tus preferencias de notificaciones, 
ingresa aquí: https://staging.jemavi.co/customer/verify
```

---

## 🎨 Interfaz de Usuario

### **Vista de Verificación (`/customer/verify`)**

**Características:**
- Diseño moderno con gradiente purple-blue
- Dos pasos claramente diferenciados
- Countdown timer visible
- Opción de reenviar código
- Botón para cambiar número de teléfono
- Mensajes de error/éxito claros
- Responsive (mobile-first)

**Elementos visuales:**
- 🔐 Icono de seguridad
- 📱 Input de teléfono con placeholder
- 🔢 Input de código con formato mono
- ⏱️ Countdown en tiempo real
- ✅ Confirmación visual de éxito

### **Modal de Preferencias (Admin)**

**Cambios:**
- ❌ Removido: Link directo a preferencias
- ✅ Agregado: Link de verificación
- ✅ Agregado: Botón "Enviar Link por SMS"
- 🎨 Color morado para tema de seguridad
- 📋 Botón de copiar link

---

## 🧪 Testing

### **Pruebas Manuales**

1. **Flujo Completo de Cliente:**
   ```bash
   # 1. Abrir navegador
   https://staging.jemavi.co/customer/verify
   
   # 2. Ingresar teléfono de cliente existente
   # 3. Verificar recepción de SMS
   # 4. Ingresar código
   # 5. Verificar redirección a preferencias
   # 6. Modificar preferencias
   # 7. Guardar cambios
   ```

2. **Flujo Admin Envía SMS:**
   ```bash
   # 1. Login como admin
   # 2. Ir a /customers/manage
   # 3. Click en botón morado de un cliente
   # 4. Click en "Enviar Link por SMS"
   # 5. Verificar que el cliente recibe el SMS
   ```

3. **Casos de Error:**
   - Teléfono no registrado
   - Código incorrecto (3 intentos)
   - Código expirado (después de 5 min)
   - Reenvío de código

### **Pruebas con cURL**

```bash
# 1. Solicitar OTP
curl -X POST https://staging.jemavi.co/api/customer/preferences-otp/request \
  -H "Content-Type: application/json" \
  -d '{"phone": "3001234567"}'

# 2. Verificar OTP
curl -X POST https://staging.jemavi.co/api/customer/preferences-otp/verify \
  -H "Content-Type: application/json" \
  -d '{"phone": "3001234567", "code": "123456"}'

# 3. Enviar link por SMS (admin)
curl -X POST https://staging.jemavi.co/api/customer/preferences-otp/send-link \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "uuid-here", "phone": "3001234567"}'
```

---

## 📊 Modelo de Datos

### **Tabla: `customer_otps`**

Ya existe en el sistema, se reutiliza para este flujo.

```sql
CREATE TABLE customer_otps (
    id UUID PRIMARY KEY,
    customer_phone VARCHAR(20) NOT NULL,
    otp_code VARCHAR(6) NOT NULL,
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    is_verified BOOLEAN DEFAULT FALSE,
    is_expired BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    verified_at TIMESTAMP WITH TIME ZONE
);
```

### **Tabla: `customer_preferences`**

Ya existe, se usa para almacenar el token permanente.

```sql
CREATE TABLE customer_preferences (
    id SERIAL PRIMARY KEY,
    customer_id UUID NOT NULL UNIQUE,
    token VARCHAR(255) NOT NULL UNIQUE,
    sms_notifications_enabled BOOLEAN DEFAULT TRUE,
    email_notifications_enabled BOOLEAN DEFAULT TRUE,
    notify_package_announced BOOLEAN DEFAULT TRUE,
    notify_package_received BOOLEAN DEFAULT TRUE,
    notify_package_delivered BOOLEAN DEFAULT TRUE,
    notify_payment_due BOOLEAN DEFAULT TRUE,
    marketing_enabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);
```

---

## 🚀 Despliegue

### **Pasos para Producción**

1. **Verificar Configuración SMS:**
   ```bash
   # Asegurar que el servicio SMS está configurado
   # Verificar credenciales en .env
   ```

2. **Reiniciar Servidor:**
   ```bash
   cd CODE
   docker compose restart
   ```

3. **Verificar Rutas Públicas:**
   ```bash
   # Verificar que las rutas están accesibles sin autenticación
   curl https://staging.jemavi.co/customer/verify
   ```

4. **Probar Flujo Completo:**
   - Usar teléfono real de cliente de prueba
   - Verificar recepción de SMS
   - Completar flujo de verificación

---

## 📝 Notas Importantes

### **Diferencias con `/customer-portal`**

| Característica | `/customer/verify` | `/customer-portal` |
|----------------|-------------------|-------------------|
| **Propósito** | Solo preferencias | Portal completo |
| **Funcionalidad** | Gestionar notificaciones | Ver paquetes, editar datos, preferencias |
| **Token** | Permanente (preferencias) | JWT temporal (1 hora) |
| **Uso** | Cada vez que necesite cambiar preferencias | Sesión completa de autogestión |

### **Ventajas del Nuevo Flujo**

✅ **Sin fricción:** No requiere crear cuenta  
✅ **Seguro:** Verificación por SMS cada vez  
✅ **Simple:** Solo 2 pasos para acceder  
✅ **Flexible:** Admin puede enviar link o cliente auto-accede  
✅ **Reutilizable:** Usa infraestructura OTP existente  

### **Consideraciones**

⚠️ **Rate Limiting:** Actualmente desactivado, considerar activar en producción  
⚠️ **Costos SMS:** Cada verificación consume 1-2 SMS  
⚠️ **Experiencia:** Cliente debe tener teléfono a mano  

---

## 🔄 Próximas Mejoras (Opcional)

1. **Rate Limiting Inteligente:**
   - Limitar intentos por IP
   - Limitar solicitudes por teléfono

2. **Recordar Dispositivo:**
   - Cookie para no pedir OTP en mismo dispositivo por X días

3. **Notificación Email:**
   - Opción de recibir código por email además de SMS

4. **Analytics:**
   - Tracking de uso del flujo
   - Métricas de conversión

5. **Internacionalización:**
   - Soporte para múltiples idiomas
   - Formato de teléfono internacional

---

## 📞 Soporte

Para problemas o preguntas sobre esta implementación:

1. Revisar logs del servidor
2. Verificar configuración SMS
3. Probar con teléfono de prueba
4. Revisar consola del navegador (F12)

---

**Fecha de Implementación:** 2025-02-07  
**Versión:** 1.0.0  
**Estado:** ✅ Listo para Testing
