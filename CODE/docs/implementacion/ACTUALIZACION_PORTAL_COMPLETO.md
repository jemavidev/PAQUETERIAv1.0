# 🔄 Actualización: Portal Completo con Verificación OTP

## 📋 Resumen de Cambios

Se modificó el flujo de verificación OTP para que después de verificar la identidad, el cliente acceda al **dashboard completo del portal** en lugar de solo a preferencias.

---

## 🎯 **Flujo Actualizado**

### **Antes:**
```
Cliente → Verifica OTP → Accede solo a preferencias
```

### **Ahora:**
```
Cliente → Verifica OTP → Accede al portal completo
                          ├─ Ver y editar datos personales
                          ├─ Ver historial de paquetes
                          └─ Gestionar preferencias de notificaciones
```

---

## 🔧 **Cambios Técnicos**

### **1. Endpoint de Verificación OTP**

**Archivo:** `CODE/src/app/routes/customer_preferences_otp.py`

**Cambios:**
- ✅ Ahora genera token JWT (igual que `/customer-portal`)
- ✅ Token válido por 1 hora
- ✅ Redirige a `/customer-portal/dashboard`
- ✅ Crea preferencias automáticamente si no existen

**Response Schema:**
```python
class PreferencesOTPVerifyResponse(BaseModel):
    success: bool
    message: str
    access_token: str          # ← JWT token
    token_type: str = "bearer"
    expires_in: int            # ← 3600 segundos (1 hora)
    redirect_url: str          # ← "/customer-portal/dashboard"
```

---

### **2. Vista de Verificación**

**Archivo:** `CODE/src/templates/customer/verify.html`

**Cambios:**
- ✅ Título cambiado a "Portal de Cliente"
- ✅ Descripción actualizada
- ✅ Guarda token JWT en `localStorage`
- ✅ Redirige a `/customer-portal/dashboard`
- ✅ Colores cambiados de morado a azul (consistencia visual)

**JavaScript:**
```javascript
// Guardar token JWT
localStorage.setItem('customer_token', data.access_token);

// Redirigir al dashboard completo
window.location.href = data.redirect_url; // "/customer-portal/dashboard"
```

---

### **3. Modal de Preferencias (Admin)**

**Archivo:** `CODE/src/templates/customers/manage.html`

**Cambios:**
- ✅ Título: "Acceso Seguro al Portal de Cliente"
- ✅ Descripción actualizada
- ✅ Colores cambiados de morado a azul
- ✅ Mensaje SMS actualizado

**Nuevo mensaje SMS:**
```
PAQUETEX: Accede a tu portal de cliente (datos, paquetes y preferencias). 
Ingresa aquí: https://staging.jemavi.co/customer/verify
```

---

## 🎨 **Experiencia de Usuario**

### **Paso 1: Admin envía link**
```
Admin en /customers/manage
  ↓
Click en botón azul 🔔 "Preferencias"
  ↓
Modal muestra link de verificación
  ↓
Click en "📱 Enviar Link por SMS"
  ↓
Cliente recibe SMS
```

### **Paso 2: Cliente verifica identidad**
```
Cliente abre link → /customer/verify
  ↓
Ingresa su teléfono
  ↓
Recibe código SMS de 6 dígitos
  ↓
Ingresa código
  ↓
Sistema valida
```

### **Paso 3: Cliente accede al portal completo**
```
Redirigido a /customer-portal/dashboard
  ↓
Puede ver 3 tabs:
  ├─ Mis Datos (editar información personal)
  ├─ Mis Paquetes (ver historial)
  └─ Preferencias (gestionar notificaciones)
```

---

## 📊 **Comparación de Funcionalidades**

| Funcionalidad | Antes | Ahora |
|---------------|-------|-------|
| **Verificación** | OTP por SMS | OTP por SMS ✅ |
| **Token** | Token de preferencias | JWT (1 hora) ✅ |
| **Acceso a datos** | ❌ No | ✅ Sí |
| **Editar datos** | ❌ No | ✅ Sí |
| **Ver paquetes** | ❌ No | ✅ Sí |
| **Gestionar preferencias** | ✅ Sí | ✅ Sí |
| **Estadísticas** | ❌ No | ✅ Sí |
| **Sesión** | Permanente | 1 hora ✅ |

---

## 🔐 **Seguridad**

### **Mejoras:**
- ✅ Token JWT con expiración (1 hora)
- ✅ Verificación de identidad por SMS
- ✅ Código OTP de 6 dígitos
- ✅ Máximo 3 intentos de verificación
- ✅ Expiración de código (5 minutos)
- ✅ Invalidación automática de códigos anteriores

### **Flujo de Seguridad:**
```
1. Cliente solicita acceso
2. Sistema verifica que cliente existe
3. Genera código OTP aleatorio
4. Envía código por SMS
5. Cliente ingresa código
6. Sistema valida (máx 3 intentos)
7. Genera token JWT firmado
8. Cliente accede con token
9. Token expira en 1 hora
```

---

## 🚀 **Ventajas del Nuevo Flujo**

### **Para el Cliente:**
✅ **Más funcionalidades:** Acceso completo a su información  
✅ **Mejor experiencia:** Todo en un solo lugar  
✅ **Más control:** Puede editar sus datos  
✅ **Transparencia:** Ve historial de paquetes  
✅ **Seguro:** Verificación por SMS cada vez  

### **Para el Negocio:**
✅ **Menos soporte:** Clientes pueden auto-gestionar datos  
✅ **Más engagement:** Clientes ven su historial  
✅ **Mejor comunicación:** Preferencias centralizadas  
✅ **Datos actualizados:** Clientes mantienen info al día  

---

## 📱 **URLs del Sistema**

### **Para Clientes:**
- **Verificación:** `https://staging.jemavi.co/customer/verify`
- **Dashboard:** `https://staging.jemavi.co/customer-portal/dashboard`

### **Para Administradores:**
- **Gestión:** `https://staging.jemavi.co/customers/manage`

---

## 🧪 **Pruebas**

### **Test 1: Flujo Completo**
```bash
1. Admin envía SMS desde /customers/manage
2. Cliente recibe SMS con link
3. Cliente abre /customer/verify
4. Cliente ingresa teléfono
5. Cliente recibe código OTP
6. Cliente ingresa código
7. Cliente es redirigido a /customer-portal/dashboard
8. Cliente ve sus datos, paquetes y preferencias
9. Cliente edita sus datos
10. Cliente gestiona preferencias
11. Cliente cierra sesión
```

### **Test 2: Seguridad**
```bash
1. Código incorrecto → Muestra intentos restantes
2. 3 intentos fallidos → Código expirado
3. Código después de 5 min → Código expirado
4. Token después de 1 hora → Sesión expirada
5. Acceso sin token → Redirige a /customer/verify
```

### **Test 3: Funcionalidades del Dashboard**
```bash
1. Tab "Mis Datos":
   - Ver estadísticas de paquetes
   - Editar nombre y apellido
   - Editar email
   - Editar dirección
   - Editar conjunto/torre/apartamento
   - Guardar cambios

2. Tab "Mis Paquetes":
   - Ver historial de paquetes
   - Ver estados (Anunciado, Recibido, Entregado)
   - Ver fechas
   - Ver tracking

3. Tab "Preferencias":
   - Activar/desactivar SMS
   - Activar/desactivar Email
   - Configurar eventos de notificación
   - Configurar marketing
   - Guardar preferencias
```

---

## 🔄 **Compatibilidad**

### **Rutas Existentes (NO afectadas):**
- ✅ `/customer-portal` - Portal original (sigue funcionando)
- ✅ `/customer-portal/verify` - Verificación original (sigue funcionando)
- ✅ `/customer-portal/dashboard` - Dashboard original (sigue funcionando)
- ✅ `/customer/preferences?token=XXX` - Preferencias directas (sigue funcionando)

### **Nuevas Rutas:**
- 🆕 `/customer/verify` - Nueva verificación (redirige al dashboard)
- 🆕 `/api/customer/preferences-otp/request` - Solicitar OTP
- 🆕 `/api/customer/preferences-otp/verify` - Verificar OTP
- 🆕 `/api/customer/preferences-otp/send-link` - Enviar SMS (admin)

---

## 📝 **Notas Importantes**

### **Diferencias entre `/customer-portal` y `/customer/verify`:**

| Aspecto | `/customer-portal` | `/customer/verify` |
|---------|-------------------|-------------------|
| **Propósito** | Portal completo (auto-acceso) | Portal completo (vía admin) |
| **Inicio** | Cliente ingresa directamente | Admin envía link |
| **Flujo OTP** | Mismo flujo | Mismo flujo |
| **Destino** | `/customer-portal/dashboard` | `/customer-portal/dashboard` |
| **Token** | JWT (1 hora) | JWT (1 hora) |
| **Funcionalidades** | Completas | Completas |

**Ambas rutas llevan al mismo dashboard**, solo difieren en cómo el cliente llega allí.

---

## 🎯 **Resultado Final**

El cliente ahora tiene acceso a un **portal completo de autogestión** donde puede:

1. ✅ **Ver sus datos personales** con estadísticas de paquetes
2. ✅ **Editar su información** (nombre, email, dirección, etc.)
3. ✅ **Ver historial de paquetes** (últimos 50)
4. ✅ **Gestionar preferencias** de notificaciones
5. ✅ **Cerrar sesión** cuando termine

Todo esto con **verificación segura por SMS** cada vez que accede.

---

**Fecha de Actualización:** 2025-02-07  
**Versión:** 2.0.0  
**Estado:** ✅ Listo para Testing
