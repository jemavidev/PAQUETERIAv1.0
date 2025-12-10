# 🔍 ANÁLISIS DE PROBLEMAS ENCONTRADOS

**Fecha:** 2025-12-09  
**Reporte de:** Pruebas manuales en staging

---

## ❌ PROBLEMA 1: Link incorrecto en email de preferencias

### Descripción:
Al presionar "Enviar email con link de preferencias" desde `/packages`, el email contiene:
```
http://localhost:8000/customer/preferences?token=3NnkZ093WzWyLEF08jr7o9ThccTcL4_k3hwxxHrEAehIdxfab4QkRtCur5tk8bfN
```

Debería ser:
```
https://staging.jemavi.co/customer/verify
```

### Ubicación del código:
- **Archivo:** `CODE/src/app/routes/packages.py` (línea ~1682)
- **Endpoint:** `POST /api/packages/{package_id}/send-email`
- **Helper:** `CODE/src/app/utils/customer_preferences_helper.py` (función `get_preferences_url`)

### Causa:
El helper `get_preferences_url()` genera un link con token antiguo (`/customer/preferences?token=XXX`) en lugar del nuevo flujo OTP (`/customer/verify`).

### Solución propuesta:
Cambiar `get_preferences_url()` para que retorne `/customer/verify` sin token, ya que el nuevo flujo usa OTP por SMS.

---

## ❌ PROBLEMA 2: Falta información de preferencias en /help

### Descripción:
La página `/help` no menciona nada sobre:
- Gestión de preferencias de notificaciones
- Link para acceder al portal (`/customer/verify`)
- Cómo controlar qué notificaciones recibir

### Ubicación del código:
- **Archivo:** `CODE/src/templates/general/help.html`

### Solución propuesta:
Agregar una nueva sección FAQ sobre preferencias de notificaciones que explique:
1. Cómo acceder al portal de clientes
2. Cómo gestionar preferencias (SMS/Email)
3. Link directo a `/customer/verify`

---

## ❌ PROBLEMA 3: Dashboard no muestra todos los paquetes

### Descripción:
Para el cliente "JESUS VILLALOBOS":
- **Real:** 1 ANUNCIADO, 4 ENTREGADOS, 2 CANCELADOS (Total: 7)
- **Dashboard muestra:** Menos paquetes (omite 1 CANCELADO y 1 ANUNCIADO)

### Ubicación del código:
- **Archivo:** `CODE/src/app/services/customer_portal_service.py`
- **Método:** `get_customer_packages()` (línea ~385)

### Causa posible:
1. El límite por defecto es 20, pero puede haber un problema con la query
2. Puede estar filtrando por `is_active` o algún otro campo
3. Puede haber paquetes con `customer_id` NULL o diferente

### Investigación necesaria:
- Verificar la query SQL exacta que se ejecuta
- Verificar que todos los paquetes tengan `customer_id` correcto
- Verificar que no haya filtros adicionales ocultos

---

## ❌ PROBLEMA 4: Botones en /messages redirigen a /packages

### Descripción:
Al presionar cualquier botón en `/messages`, el usuario es redirigido a `/packages`.

### Ubicación del código:
- **Archivo:** `CODE/src/templates/messages/messages.html`

### Causa posible:
1. JavaScript mal configurado que captura eventos de botones
2. Formulario que envía a URL incorrecta
3. Event listener global que redirige

### Investigación necesaria:
- Revisar el JavaScript completo de messages.html
- Buscar event listeners globales
- Verificar si hay un formulario que envuelve los botones

---

## 📋 PRIORIDAD DE SOLUCIÓN

1. **ALTA:** Problema 1 (Link incorrecto) - Afecta funcionalidad crítica
2. **ALTA:** Problema 4 (Redirección) - Bloquea uso de mensajes
3. **MEDIA:** Problema 3 (Paquetes faltantes) - Afecta experiencia del usuario
4. **BAJA:** Problema 2 (Documentación) - Mejora de UX

---

## ⚠️ NOTA IMPORTANTE

**NO TOCAR** funcionalidades que ya están funcionando:
- Sistema OTP actual
- Envío de SMS/Email
- Gestión de preferencias desde dashboard
- Panel administrativo

**SOLO CORREGIR** los problemas específicos identificados sin afectar el resto del sistema.
