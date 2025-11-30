# 🧪 Plan de Pruebas - Staging (Últimos Commits)

**Fecha:** 2024-11-29  
**Rama:** staging  
**Commits a probar:** f9b3910 hasta d0754e5 (últimos 6 commits)

---

## 📋 Resumen de Cambios a Probar

### 1. FIX MENSAJE DE WHATSAPP (f9b3910)
- ✅ Link de búsqueda en mensajes de WhatsApp
- ✅ Formato: `Hola [NOMBRE], te contacto por tu paquete. Puedes consultar el estado aquí: [LINK]`

### 2. FIX DEL DEVTOOLS (e09383d, 12c0480, a7e3836)
- ✅ Deshabilitados logs excesivos
- ✅ Caché en `isMobileDevice()`
- ✅ Flag `ENABLE_VERBOSE_LOGS = false`
- ✅ Navegador NO se bloquea al abrir DevTools

### 3. FIX BOTONES EN VISTA MENSAJES (d0754e5, 01f38d7)
- ✅ Botones inline en vista de mensajes
- ✅ Mejoras visuales en botones

---

## 🎯 Pruebas Críticas

### PRUEBA 1: DevTools NO se Bloquea ⚠️ CRÍTICO
**Objetivo:** Verificar que el navegador no se congela al abrir DevTools

**Pasos:**
1. Abre staging: `https://staging.jemavi.co`
2. Inicia sesión
3. Ve a `/packages`
4. Presiona `F12` para abrir DevTools
5. Presiona `Ctrl+Shift+M` para modo móvil
6. Cambia entre dispositivos (iPhone, Android, iPad)

**Resultado Esperado:**
- ✅ El navegador NO se bloquea
- ✅ La consola muestra solo logs esenciales
- ✅ NO hay miles de logs por segundo
- ✅ Puedes navegar normalmente

**Logs Esperados:**
```
🔧 Configuración PAQUETES EL CLUB v4.0 cargada correctamente
🔐 AuthRedirectHandler v2.0 inicializado
Ruta protegida detectada: /packages
```

---

### PRUEBA 2: WhatsApp Link con Búsqueda ⚠️ CRÍTICO
**Objetivo:** Verificar que el mensaje de WhatsApp incluye el link de búsqueda

**Pasos:**
1. Ve a `/packages`
2. Busca un paquete con tracking number (ej: 8ZWG)
3. Haz clic en el botón verde de WhatsApp
4. Verifica el mensaje pre-llenado

**Resultado Esperado:**
```
Hola [NOMBRE], te contacto por tu paquete. Puedes consultar el estado aquí: https://staging.jemavi.co/search?auto_search=8ZWG
```

**Verificar:**
- ✅ El nombre del cliente está correcto
- ✅ El link incluye el tracking number correcto
- ✅ El link es clickeable
- ✅ El dominio es `staging.jemavi.co`

---

### PRUEBA 3: WhatsApp desde Modal de Recepción
**Objetivo:** Verificar link de WhatsApp en modal de recepción

**Pasos:**
1. Ve a `/packages`
2. Haz clic en "Recibir" en un paquete
3. En el modal, busca el teléfono del cliente
4. Haz clic en el link de WhatsApp

**Resultado Esperado:**
- ✅ El mensaje incluye el link de búsqueda
- ✅ El formato es correcto

---

### PRUEBA 4: WhatsApp desde Modal de Entrega
**Objetivo:** Verificar link de WhatsApp en modal de entrega

**Pasos:**
1. Ve a `/packages`
2. Haz clic en "Entregar" en un paquete
3. En el modal, busca el teléfono del cliente
4. Haz clic en el link de WhatsApp

**Resultado Esperado:**
- ✅ El mensaje incluye el link de búsqueda
- ✅ El formato es correcto

---

### PRUEBA 5: Botones en Vista Mensajes
**Objetivo:** Verificar que los botones se ven correctamente en `/messages`

**Pasos:**
1. Ve a `/messages`
2. Verifica los botones de acción
3. Prueba en desktop y móvil

**Resultado Esperado:**
- ✅ Botones inline (no apilados)
- ✅ Se ven bien en desktop
- ✅ Se ven bien en móvil

---

## 🔍 Pruebas de Regresión

### PRUEBA 6: Funcionalidad General de Paquetes
**Objetivo:** Verificar que nada se rompió

**Pasos:**
1. Ve a `/packages`
2. Busca un paquete
3. Filtra por estado
4. Ordena por columna
5. Abre un modal de recepción
6. Abre un modal de entrega

**Resultado Esperado:**
- ✅ Todo funciona como antes
- ✅ No hay errores en consola
- ✅ Los modales se abren correctamente

---

### PRUEBA 7: Búsqueda Automática
**Objetivo:** Verificar que el parámetro `auto_search` funciona

**Pasos:**
1. Abre: `https://staging.jemavi.co/search?auto_search=8ZWG`
2. Verifica que se ejecuta la búsqueda automáticamente

**Resultado Esperado:**
- ✅ La búsqueda se ejecuta automáticamente
- ✅ Se muestra el resultado del paquete
- ✅ No hay errores

---

### PRUEBA 8: Logs en Consola (Desktop)
**Objetivo:** Verificar que los logs están deshabilitados

**Pasos:**
1. Abre staging en desktop
2. Abre DevTools (F12)
3. Ve a la pestaña Console
4. Navega por la aplicación

**Resultado Esperado:**
- ✅ Solo logs esenciales (configuración, auth)
- ✅ NO hay logs de `isMobileDevice()`
- ✅ NO hay logs de validación
- ✅ NO hay logs de MutationObserver

---

### PRUEBA 9: Logs en Consola (Móvil)
**Objetivo:** Verificar que los logs están deshabilitados en móvil

**Pasos:**
1. Abre staging en desktop
2. Abre DevTools (F12)
3. Activa modo móvil (Ctrl+Shift+M)
4. Navega por la aplicación

**Resultado Esperado:**
- ✅ Solo logs esenciales
- ✅ NO hay logs cada segundo
- ✅ El navegador NO se bloquea

---

### PRUEBA 10: Rendimiento General
**Objetivo:** Verificar que el rendimiento mejoró

**Pasos:**
1. Abre staging
2. Abre DevTools > Performance
3. Graba 10 segundos de navegación
4. Analiza el resultado

**Resultado Esperado:**
- ✅ No hay picos de CPU por logs
- ✅ No hay memory leaks
- ✅ La aplicación responde rápido

---

## 📱 Pruebas en Dispositivos Reales

### PRUEBA 11: WhatsApp en Móvil Real
**Objetivo:** Verificar que WhatsApp se abre correctamente

**Pasos:**
1. Abre staging en tu celular
2. Ve a `/packages`
3. Haz clic en el botón de WhatsApp
4. Verifica que se abre la app de WhatsApp

**Resultado Esperado:**
- ✅ Se abre WhatsApp
- ✅ El mensaje está pre-llenado
- ✅ El link es clickeable
- ✅ El link abre el navegador con la búsqueda

---

### PRUEBA 12: Link de Búsqueda desde WhatsApp
**Objetivo:** Verificar el flujo completo

**Pasos:**
1. Envía el mensaje de WhatsApp a ti mismo
2. Haz clic en el link de búsqueda
3. Verifica que se abre staging con la búsqueda

**Resultado Esperado:**
- ✅ Se abre `staging.jemavi.co/search?auto_search=[TRACKING]`
- ✅ La búsqueda se ejecuta automáticamente
- ✅ Se muestra el resultado correcto

---

## 🐛 Casos Edge

### PRUEBA 13: Paquete sin Tracking Number
**Objetivo:** Verificar fallback cuando no hay tracking

**Pasos:**
1. Busca un paquete sin tracking number (si existe)
2. Haz clic en WhatsApp

**Resultado Esperado:**
- ✅ El mensaje NO incluye el link
- ✅ Solo dice: `Hola [NOMBRE], te contacto por tu paquete`
- ✅ No hay errores en consola

---

### PRUEBA 14: Nombre con Caracteres Especiales
**Objetivo:** Verificar encoding correcto

**Pasos:**
1. Busca un cliente con nombre especial (ej: "María José")
2. Haz clic en WhatsApp

**Resultado Esperado:**
- ✅ El nombre se codifica correctamente
- ✅ Los acentos se muestran bien
- ✅ No hay caracteres raros

---

### PRUEBA 15: Tracking Number con Caracteres Especiales
**Objetivo:** Verificar encoding del tracking

**Pasos:**
1. Busca un tracking con caracteres especiales
2. Haz clic en WhatsApp

**Resultado Esperado:**
- ✅ El tracking se codifica correctamente
- ✅ El link funciona

---

## ✅ Checklist de Pruebas

### Críticas (Deben pasar SÍ o SÍ)
- [ ] PRUEBA 1: DevTools NO se bloquea
- [ ] PRUEBA 2: WhatsApp link con búsqueda
- [ ] PRUEBA 6: Funcionalidad general
- [ ] PRUEBA 8: Logs deshabilitados (desktop)
- [ ] PRUEBA 9: Logs deshabilitados (móvil)

### Importantes
- [ ] PRUEBA 3: WhatsApp desde modal recepción
- [ ] PRUEBA 4: WhatsApp desde modal entrega
- [ ] PRUEBA 5: Botones en vista mensajes
- [ ] PRUEBA 7: Búsqueda automática
- [ ] PRUEBA 11: WhatsApp en móvil real

### Opcionales
- [ ] PRUEBA 10: Rendimiento general
- [ ] PRUEBA 12: Link desde WhatsApp
- [ ] PRUEBA 13: Paquete sin tracking
- [ ] PRUEBA 14: Nombre con caracteres especiales
- [ ] PRUEBA 15: Tracking con caracteres especiales

---

## 🚀 Comandos Útiles

### Ver logs del servidor staging
```bash
ssh staging "cd /home/ubuntu/paquetes-el-club && docker-compose -f docker-compose.staging.yml logs -f --tail=100"
```

### Verificar archivos modificados
```bash
git --no-pager diff d0754e5..f9b3910 --stat
```

### Ver un commit específico
```bash
git --no-pager show f9b3910
```

### Verificar flags de debug
```bash
grep -n "ENABLE_VERBOSE_LOGS" CODE/src/templates/packages/packages.html
grep -n "DEBUG_VALIDATION" CODE/src/static/js/validation-override.js
grep -n "ENABLE_MONITOR" CODE/src/static/js/mobile-scroll-debug.js
```

---

## 📊 Reporte de Resultados

### Formato de Reporte
Para cada prueba, reporta:
```
PRUEBA X: [NOMBRE]
Estado: ✅ PASS / ❌ FAIL / ⚠️ PARCIAL
Notas: [Observaciones]
Errores: [Si los hay]
```

### Ejemplo:
```
PRUEBA 1: DevTools NO se bloquea
Estado: ✅ PASS
Notas: Funciona perfectamente en Chrome y Firefox
Errores: Ninguno
```

---

## 🎯 Criterios de Aceptación

Para considerar los cambios como exitosos:

1. ✅ **DevTools funciona sin bloqueos** (CRÍTICO)
2. ✅ **WhatsApp incluye link de búsqueda** (CRÍTICO)
3. ✅ **No hay regresiones** en funcionalidad existente
4. ✅ **Logs están deshabilitados** por defecto
5. ✅ **Rendimiento mejoró** (menos logs = más rápido)

---

**Creado por:** Kiro AI Assistant  
**Fecha:** 2024-11-29  
**Versión:** 1.0
