# Inventario Completo de Vistas - Sistema OTP y Portal de Clientes

**Fecha**: 2025-02-07  
**Objetivo**: Identificar todas las vistas relacionadas con OTP y portal de clientes

---

## 📋 RESUMEN EJECUTIVO

Existen **2 FLUJOS PRINCIPALES** para que los clientes accedan al portal:

### Flujo 1: Portal Original (`/customer-portal/*`)
- Entrada: `/customer-portal`
- Verificación: `/customer-portal/verify`
- Dashboard: `/customer-portal/dashboard`

### Flujo 2: Portal Nuevo con OTP (`/customer/verify`)
- Entrada: `/customer/verify` (solicita y verifica OTP)
- Dashboard: `/customer-portal/dashboard` (mismo que Flujo 1)

**AMBOS FLUJOS LLEVAN AL MISMO DASHBOARD**

---

## 🌐 VISTAS HTML PÚBLICAS (Frontend)

### ✅ FLUJO NUEVO - Sistema OTP Mejorado (RECOMENDADO USAR)

#### 1. `/customer/verify` ⭐ **PRINCIPAL**
- **Archivo**: `CODE/src/templates/customer/verify.html`
- **Ruta definida en**: `CODE/src/app/routes/views.py`
- **Función**: Solicitar y verificar OTP en una sola vista
- **Características**:
  - ✅ Diseño moderno (igual que `/announce`)
  - ✅ 2 pasos en una sola página
  - ✅ Terminología "contraseña temporal"
  - ✅ Countdown timer
  - ✅ Reenviar contraseña
  - ✅ Validación en tiempo real
- **Estado**: ✅ ACTIVA Y FUNCIONAL
- **Uso**: Cliente ingresa teléfono → Recibe OTP → Verifica → Accede al dashboard

#### 2. `/customer/preferences`
- **Archivo**: `CODE/src/templates/customer/preferences.html`
- **Ruta definida en**: `CODE/src/app/routes/views.py`
- **Función**: Vista directa de preferencias con token en URL
- **Características**:
  - Acceso directo con token: `/customer/preferences?token=XXX`
  - Solo muestra preferencias de notificación
  - No requiere OTP
- **Estado**: ✅ ACTIVA (para acceso directo con token)
- **Uso**: Admin envía link directo al cliente

---

### ⚠️ FLUJO ORIGINAL - Portal con OTP Separado (DUPLICADO)

#### 3. `/customer-portal` (Entrada)
- **Archivo**: `CODE/src/templates/customer_portal/index.html`
- **Ruta definida en**: `CODE/src/app/routes/customer_portal_views.py`
- **Función**: Página de entrada para solicitar OTP
- **Estado**: ✅ ACTIVA pero **DUPLICADA** con `/customer/verify`
- **Recomendación**: ⚠️ CONSIDERAR ELIMINAR (duplica funcionalidad)

#### 4. `/customer-portal/verify` (Verificación)
- **Archivo**: `CODE/src/templates/customer_portal/verify.html`
- **Ruta definida en**: `CODE/src/app/routes/customer_portal_views.py`
- **Función**: Verificar código OTP
- **Estado**: ✅ ACTIVA pero **DUPLICADA** con `/customer/verify`
- **Recomendación**: ⚠️ CONSIDERAR ELIMINAR (duplica funcionalidad)

---

### ✅ DASHBOARD COMPARTIDO (Usado por ambos flujos)

#### 5. `/customer-portal/dashboard` ⭐ **DESTINO FINAL**
- **Archivo**: `CODE/src/templates/customer_portal/dashboard.html`
- **Ruta definida en**: `CODE/src/app/routes/customer_portal_views.py`
- **Función**: Dashboard completo del cliente
- **Características**:
  - ✅ 3 tabs: Mis Datos, Mis Paquetes, Preferencias
  - ✅ Ver/editar información personal
  - ✅ Historial de paquetes (formato cards compacto)
  - ✅ Configurar preferencias de notificación
  - ✅ Botón de cerrar sesión
- **Estado**: ✅ ACTIVA Y FUNCIONAL
- **Uso**: Destino final de ambos flujos OTP

---

## 🔌 APIs PÚBLICAS (Backend)

### ✅ APIs del Flujo Nuevo (RECOMENDADO)

#### 1. `POST /api/customer/preferences-otp/request`
- **Archivo**: `CODE/src/app/routes/customer_preferences_otp.py`
- **Función**: Solicitar OTP (envía por SMS y/o Email)
- **Estado**: ✅ ACTIVA Y FUNCIONAL
- **Características**:
  - Respeta preferencias del cliente
  - Envío multicanal (SMS + Email)
  - Terminología "contraseña temporal"

#### 2. `POST /api/customer/preferences-otp/verify`
- **Archivo**: `CODE/src/app/routes/customer_preferences_otp.py`
- **Función**: Verificar OTP y generar token JWT
- **Estado**: ✅ ACTIVA Y FUNCIONAL
- **Retorna**: Token JWT + URL de redirección

#### 3. `POST /api/customer/preferences-otp/send-link`
- **Archivo**: `CODE/src/app/routes/customer_preferences_otp.py`
- **Función**: Admin envía link de verificación por SMS
- **Estado**: ✅ ACTIVA Y FUNCIONAL
- **Uso**: Desde `/customers/manage` (modal de admin)

---

### ⚠️ APIs del Flujo Original (DUPLICADAS)

#### 4. `POST /api/customer-portal/request-otp`
- **Archivo**: `CODE/src/app/routes/customer_portal.py`
- **Función**: Solicitar OTP (solo SMS)
- **Estado**: ✅ ACTIVA pero **DUPLICADA**
- **Recomendación**: ⚠️ CONSIDERAR ELIMINAR

#### 5. `POST /api/customer-portal/verify-otp`
- **Archivo**: `CODE/src/app/routes/customer_portal.py`
- **Función**: Verificar OTP
- **Estado**: ✅ ACTIVA pero **DUPLICADA**
- **Recomendación**: ⚠️ CONSIDERAR ELIMINAR

---

### ✅ APIs del Dashboard (Compartidas)

#### 6. `GET /api/customer-portal/me`
- **Archivo**: `CODE/src/app/routes/customer_portal.py`
- **Función**: Obtener datos del cliente autenticado
- **Estado**: ✅ ACTIVA Y NECESARIA
- **Requiere**: Token JWT en header

#### 7. `PUT /api/customer-portal/me`
- **Archivo**: `CODE/src/app/routes/customer_portal.py`
- **Función**: Actualizar datos del cliente
- **Estado**: ✅ ACTIVA Y NECESARIA
- **Requiere**: Token JWT en header

#### 8. `GET /api/customer-portal/packages`
- **Archivo**: `CODE/src/app/routes/customer_portal.py`
- **Función**: Obtener historial de paquetes
- **Estado**: ✅ ACTIVA Y NECESARIA
- **Requiere**: Token JWT en header

#### 9. `GET /api/customer-portal/preferences/notifications`
- **Archivo**: `CODE/src/app/routes/customer_portal.py`
- **Función**: Obtener preferencias de notificación
- **Estado**: ✅ ACTIVA Y NECESARIA
- **Requiere**: Token JWT en header

#### 10. `PUT /api/customer-portal/preferences/notifications`
- **Archivo**: `CODE/src/app/routes/customer_portal.py`
- **Función**: Actualizar preferencias de notificación
- **Estado**: ✅ ACTIVA Y NECESARIA
- **Requiere**: Token JWT en header

#### 11. `POST /api/customer-portal/logout`
- **Archivo**: `CODE/src/app/routes/customer_portal.py`
- **Función**: Cerrar sesión del cliente
- **Estado**: ✅ ACTIVA Y NECESARIA

---

## 🔒 VISTAS PRIVADAS (Admin)

### ✅ Gestión de Clientes (Admin)

#### 1. `/customers/manage`
- **Archivo**: `CODE/src/templates/customers/manage.html`
- **Ruta definida en**: `CODE/src/app/routes/protected.py`
- **Función**: Gestión de clientes por admin
- **Características**:
  - Lista de clientes
  - Búsqueda y filtros
  - Modal para enviar link de verificación
  - Botón "Enviar Link de Verificación"
- **Estado**: ✅ ACTIVA Y NECESARIA
- **Requiere**: Autenticación de admin

#### 2. `/customers/create`
- **Archivo**: `CODE/src/templates/customers/create.html`
- **Ruta definida en**: `CODE/src/app/routes/protected.py`
- **Función**: Crear nuevo cliente
- **Estado**: ✅ ACTIVA Y NECESARIA
- **Requiere**: Autenticación de admin

#### 3. `/customers/edit/{customer_id}`
- **Archivo**: `CODE/src/templates/customers/edit.html`
- **Ruta definida en**: `CODE/src/app/routes/protected.py`
- **Función**: Editar cliente existente
- **Estado**: ✅ ACTIVA Y NECESARIA
- **Requiere**: Autenticación de admin

---

## 📊 ANÁLISIS Y RECOMENDACIONES

### ✅ VISTAS A MANTENER (Esenciales)

#### Flujo de Cliente (Público)
1. ✅ `/customer/verify` - Entrada principal con OTP
2. ✅ `/customer-portal/dashboard` - Dashboard completo
3. ✅ `/customer/preferences` - Acceso directo con token (opcional)

#### APIs de Cliente (Públicas)
4. ✅ `/api/customer/preferences-otp/request` - Solicitar OTP
5. ✅ `/api/customer/preferences-otp/verify` - Verificar OTP
6. ✅ `/api/customer/preferences-otp/send-link` - Enviar link (admin)
7. ✅ `/api/customer-portal/me` - Datos del cliente
8. ✅ `/api/customer-portal/packages` - Historial de paquetes
9. ✅ `/api/customer-portal/preferences/notifications` - Preferencias
10. ✅ `/api/customer-portal/logout` - Cerrar sesión

#### Vistas de Admin (Privadas)
11. ✅ `/customers/manage` - Gestión de clientes
12. ✅ `/customers/create` - Crear cliente
13. ✅ `/customers/edit/{id}` - Editar cliente

---

### ⚠️ VISTAS DUPLICADAS (Considerar eliminar)

#### Flujo Original (Redundante)
1. ⚠️ `/customer-portal` - Duplica `/customer/verify` (paso 1)
2. ⚠️ `/customer-portal/verify` - Duplica `/customer/verify` (paso 2)
3. ⚠️ `/api/customer-portal/request-otp` - Duplica `/api/customer/preferences-otp/request`
4. ⚠️ `/api/customer-portal/verify-otp` - Duplica `/api/customer/preferences-otp/verify`

**Razones para eliminar:**
- Duplican funcionalidad exacta
- El flujo nuevo (`/customer/verify`) es superior:
  - ✅ Mejor diseño (consistente con `/announce`)
  - ✅ Terminología más clara ("contraseña temporal")
  - ✅ Envío multicanal (SMS + Email)
  - ✅ Todo en una sola página (mejor UX)
- Mantener ambos flujos causa confusión
- Más difícil de mantener y actualizar

---

## 🎯 RECOMENDACIÓN FINAL

### Opción 1: Mantener Solo Flujo Nuevo (RECOMENDADO)

**Eliminar:**
- `/customer-portal` (index)
- `/customer-portal/verify`
- `/api/customer-portal/request-otp`
- `/api/customer-portal/verify-otp`
- `CODE/src/templates/customer_portal/index.html`
- `CODE/src/templates/customer_portal/verify.html`

**Mantener:**
- `/customer/verify` (entrada única)
- `/customer-portal/dashboard` (destino)
- Todas las APIs del dashboard
- Todas las vistas de admin

**Beneficios:**
- ✅ Un solo flujo claro
- ✅ Menos código que mantener
- ✅ Menos confusión para usuarios
- ✅ Mejor experiencia de usuario
- ✅ Funcionalidad superior (multicanal)

---

### Opción 2: Mantener Ambos Flujos (NO RECOMENDADO)

**Mantener todo** pero:
- Redirigir `/customer-portal` → `/customer/verify`
- Redirigir `/customer-portal/verify` → `/customer/verify`
- Deprecar APIs antiguas

**Desventajas:**
- ⚠️ Código duplicado
- ⚠️ Más difícil de mantener
- ⚠️ Confusión sobre cuál usar
- ⚠️ Inconsistencia en funcionalidad

---

## 📝 PLAN DE ACCIÓN SUGERIDO

### Fase 1: Validación (1-2 días)
1. ✅ Probar `/customer/verify` en staging
2. ✅ Verificar que todo funcione correctamente
3. ✅ Confirmar envío multicanal (SMS + Email)
4. ✅ Validar dashboard completo

### Fase 2: Migración (1 día)
1. ⚠️ Agregar redirecciones:
   - `/customer-portal` → `/customer/verify`
   - `/customer-portal/verify` → `/customer/verify`
2. ⚠️ Actualizar links en emails/SMS
3. ⚠️ Actualizar documentación

### Fase 3: Limpieza (1 día)
1. ❌ Eliminar archivos obsoletos:
   - `customer_portal/index.html`
   - `customer_portal/verify.html`
2. ❌ Eliminar endpoints duplicados
3. ❌ Limpiar rutas en `config_routes.py`
4. ✅ Actualizar tests

---

## 🔍 ARCHIVOS CLAVE

### Templates HTML
```
CODE/src/templates/
├── customer/
│   ├── verify.html              ✅ MANTENER (principal)
│   └── preferences.html          ✅ MANTENER (acceso directo)
├── customer_portal/
│   ├── index.html               ⚠️ ELIMINAR (duplicado)
│   ├── verify.html              ⚠️ ELIMINAR (duplicado)
│   └── dashboard.html           ✅ MANTENER (destino final)
└── customers/
    ├── manage.html              ✅ MANTENER (admin)
    ├── create.html              ✅ MANTENER (admin)
    └── edit.html                ✅ MANTENER (admin)
```

### Rutas Python
```
CODE/src/app/routes/
├── customer_preferences_otp.py  ✅ MANTENER (APIs nuevas)
├── customer_portal.py           ⚠️ REVISAR (tiene APIs duplicadas y necesarias)
├── customer_portal_views.py     ⚠️ REVISAR (tiene vistas duplicadas y necesarias)
├── views.py                     ✅ MANTENER (vistas públicas)
└── protected.py                 ✅ MANTENER (vistas admin)
```

---

## ✅ CONCLUSIÓN

**Tienes 2 flujos que hacen lo mismo:**
1. **Flujo Nuevo** (`/customer/verify`) - Mejor diseño, multicanal, todo en uno
2. **Flujo Original** (`/customer-portal` + `/customer-portal/verify`) - Separado en 2 pasos, solo SMS

**Recomendación:** Mantener solo el Flujo Nuevo y eliminar el Original para simplificar el sistema.
