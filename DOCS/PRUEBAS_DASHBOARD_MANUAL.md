# 🧪 GUÍA DE PRUEBAS MANUALES - DASHBOARD UNIFICADO

**URL:** https://staging.jemavi.co/admin  
**Fecha:** 2024-12-14  
**Estado:** Listo para probar

---

## 📋 CHECKLIST DE PRUEBAS

### ✅ PASO 1: ACCESO Y LOGIN

- [ ] 1.1. Ir a https://staging.jemavi.co
- [ ] 1.2. Hacer login con usuario ADMIN o OPERADOR
- [ ] 1.3. Verificar que el login es exitoso

**Resultado esperado:** Redirige al dashboard o página principal

---

### ✅ PASO 2: MENÚ DE USUARIO

- [ ] 2.1. Hacer clic en el avatar del usuario (esquina superior derecha)
- [ ] 2.2. Verificar que se abre el menú dropdown
- [ ] 2.3. Verificar que solo aparece "Dashboard" (NO debe aparecer "Settings")
- [ ] 2.4. Hacer clic en "Dashboard"

**Resultado esperado:** 
- Menú muestra solo: Dashboard y Cerrar Sesión
- Al hacer clic en Dashboard, redirige a `/admin`

---

### ✅ PASO 3: NAVEGACIÓN DE TABS

#### Tab 1: 📊 Dashboard (Estadísticas)

- [ ] 3.1. Verificar que el tab "Dashboard" está activo por defecto (color azul)
- [ ] 3.2. Verificar que se muestran las 6 secciones:
  - [ ] 💰 Financiero
  - [ ] 📦 Paquetes
  - [ ] 👥 Clientes
  - [ ] 📱 SMS y Notificaciones
  - [ ] ⚡ Performance Operacional
  - [ ] 🏥 Salud del Sistema

**Resultado esperado:** Todas las secciones visibles con datos cargados

#### Tab 2: 👥 Usuarios

- [ ] 3.3. Hacer clic en el tab "Usuarios"
- [ ] 3.4. Verificar que el tab cambia sin recargar la página
- [ ] 3.5. Verificar que se muestran 3 tarjetas:
  - [ ] Total Usuarios
  - [ ] Usuarios Activos
  - [ ] Administradores
- [ ] 3.6. Hacer clic en el botón "Ir a Gestión de Usuarios"
- [ ] 3.7. Verificar que redirige a `/admin/users`

**Resultado esperado:** Vista rápida de usuarios + botón funcional

#### Tab 3: 📦 Paquetes

- [ ] 3.8. Volver a `/admin` y hacer clic en el tab "Paquetes"
- [ ] 3.9. Verificar que se muestran 4 tarjetas de estado:
  - [ ] Anunciados (amarillo)
  - [ ] Recibidos (azul)
  - [ ] Entregados (verde)
  - [ ] Cancelados (rojo)
- [ ] 3.10. Hacer clic en el botón "Ver Todos los Paquetes"
- [ ] 3.11. Verificar que redirige a `/packages`

**Resultado esperado:** Vista rápida de paquetes por estado + botón funcional

#### Tab 4: 🏢 Clientes

- [ ] 3.12. Volver a `/admin` y hacer clic en el tab "Clientes"
- [ ] 3.13. Verificar que se muestran 3 tarjetas:
  - [ ] Total Clientes
  - [ ] Clientes VIP
  - [ ] Nuevos Este Mes
- [ ] 3.14. Hacer clic en el botón "Ver Todos los Clientes"
- [ ] 3.15. Verificar que redirige a `/customers`

**Resultado esperado:** Vista rápida de clientes + botón funcional

#### Tab 5: 💬 Mensajes

- [ ] 3.16. Volver a `/admin` y hacer clic en el tab "Mensajes"
- [ ] 3.17. Verificar que se muestran 2 tarjetas:
  - [ ] Mensajes Pendientes
  - [ ] Mensajes Resueltos
- [ ] 3.18. Hacer clic en el botón "Ver Todos los Mensajes"
- [ ] 3.19. Verificar que redirige a `/messages`

**Resultado esperado:** Vista rápida de mensajes + botón funcional

#### Tab 6: ⚙️ Settings

- [ ] 3.20. Volver a `/admin` y hacer clic en el tab "Settings"
- [ ] 3.21. Verificar que se muestran 3 secciones:
  - [ ] Enlaces Rápidos (4 tarjetas)
  - [ ] Información del Sistema
  - [ ] Límites y Configuración (6 tarjetas)
- [ ] 3.22. Hacer clic en cada enlace rápido y verificar que funcionan:
  - [ ] Gestión de Usuarios → `/admin/users`
  - [ ] Lista de Paquetes → `/packages`
  - [ ] Clientes → `/customers`
  - [ ] Mensajes → `/messages`

**Resultado esperado:** Todas las secciones visibles + enlaces funcionales

---

### ✅ PASO 4: BOTÓN ACTUALIZAR

- [ ] 4.1. Hacer clic en el botón "Actualizar" (esquina superior derecha)
- [ ] 4.2. Verificar que la página se recarga
- [ ] 4.3. Verificar que los datos se actualizan

**Resultado esperado:** Página se recarga y datos se actualizan

---

### ✅ PASO 5: RESPONSIVE DESIGN

#### Desktop (> 1024px)

- [ ] 5.1. Verificar que todos los tabs se muestran en una línea
- [ ] 5.2. Verificar que los iconos y texto son visibles
- [ ] 5.3. Verificar que las tarjetas se muestran en grid de 3-4 columnas

**Resultado esperado:** Layout optimizado para desktop

#### Tablet (768px - 1024px)

- [ ] 5.4. Reducir el ancho del navegador a ~800px
- [ ] 5.5. Verificar que los tabs tienen scroll horizontal si es necesario
- [ ] 5.6. Verificar que las tarjetas se muestran en grid de 2 columnas

**Resultado esperado:** Layout adaptado para tablet

#### Mobile (< 768px)

- [ ] 5.7. Reducir el ancho del navegador a ~400px
- [ ] 5.8. Verificar que los tabs muestran solo iconos (texto oculto)
- [ ] 5.9. Verificar que las tarjetas se apilan verticalmente (1 columna)
- [ ] 5.10. Verificar que el scroll horizontal funciona en los tabs

**Resultado esperado:** Layout optimizado para móvil

---

### ✅ PASO 6: CARGA DE DATOS

#### Tab Dashboard

- [ ] 6.1. Ir al tab Dashboard
- [ ] 6.2. Verificar que todas las métricas muestran números (no "0" o "Cargando...")
- [ ] 6.3. Verificar que la tabla "Top 5 Clientes" tiene datos
- [ ] 6.4. Verificar que las barras de progreso de SMS se muestran correctamente

**Resultado esperado:** Todos los datos cargados correctamente

#### Tabs de Vista Rápida

- [ ] 6.5. Ir al tab Usuarios y verificar que los números cargan
- [ ] 6.6. Ir al tab Paquetes y verificar que los números cargan
- [ ] 6.7. Ir al tab Clientes y verificar que los números cargan
- [ ] 6.8. Ir al tab Mensajes y verificar que los números cargan

**Resultado esperado:** Datos cargados en todos los tabs

---

### ✅ PASO 7: TRANSICIONES Y ANIMACIONES

- [ ] 7.1. Cambiar entre tabs rápidamente
- [ ] 7.2. Verificar que las transiciones son suaves
- [ ] 7.3. Verificar que no hay parpadeos o saltos
- [ ] 7.4. Verificar que el tab activo cambia de color correctamente

**Resultado esperado:** Transiciones suaves sin errores visuales

---

### ✅ PASO 8: CONSOLA DEL NAVEGADOR

- [ ] 8.1. Abrir la consola del navegador (F12)
- [ ] 8.2. Ir a la pestaña "Console"
- [ ] 8.3. Verificar que no hay errores en rojo
- [ ] 8.4. Cambiar entre tabs y verificar que no aparecen errores

**Resultado esperado:** Sin errores en la consola

---

### ✅ PASO 9: NETWORK (Red)

- [ ] 9.1. Abrir las herramientas de desarrollo (F12)
- [ ] 9.2. Ir a la pestaña "Network"
- [ ] 9.3. Cambiar al tab Dashboard
- [ ] 9.4. Verificar que se hace una llamada a `/api/admin/dashboard`
- [ ] 9.5. Verificar que la respuesta es 200 OK
- [ ] 9.6. Cambiar a otros tabs y verificar las llamadas API

**Resultado esperado:** Todas las llamadas API exitosas (200 OK)

---

### ✅ PASO 10: PRUEBAS DE ESTRÉS

- [ ] 10.1. Cambiar entre tabs rápidamente 10 veces
- [ ] 10.2. Verificar que no hay errores
- [ ] 10.3. Hacer clic en "Actualizar" varias veces seguidas
- [ ] 10.4. Verificar que la aplicación responde correctamente

**Resultado esperado:** Aplicación estable sin errores

---

## 📊 TABLA DE RESULTADOS

| # | Prueba | Estado | Notas |
|---|--------|--------|-------|
| 1 | Acceso y Login | ⬜ | |
| 2 | Menú de Usuario | ⬜ | |
| 3.1 | Tab Dashboard | ⬜ | |
| 3.2 | Tab Usuarios | ⬜ | |
| 3.3 | Tab Paquetes | ⬜ | |
| 3.4 | Tab Clientes | ⬜ | |
| 3.5 | Tab Mensajes | ⬜ | |
| 3.6 | Tab Settings | ⬜ | |
| 4 | Botón Actualizar | ⬜ | |
| 5 | Responsive Design | ⬜ | |
| 6 | Carga de Datos | ⬜ | |
| 7 | Transiciones | ⬜ | |
| 8 | Consola | ⬜ | |
| 9 | Network | ⬜ | |
| 10 | Estrés | ⬜ | |

**Leyenda:**
- ⬜ Pendiente
- ✅ Pasó
- ❌ Falló
- ⚠️ Con observaciones

---

## 🐛 REPORTE DE BUGS

Si encuentras algún problema, documéntalo aquí:

### Bug #1
- **Descripción:**
- **Pasos para reproducir:**
- **Resultado esperado:**
- **Resultado actual:**
- **Severidad:** Alta / Media / Baja
- **Screenshot:**

### Bug #2
- **Descripción:**
- **Pasos para reproducir:**
- **Resultado esperado:**
- **Resultado actual:**
- **Severidad:** Alta / Media / Baja
- **Screenshot:**

---

## 📸 SCREENSHOTS RECOMENDADOS

Toma screenshots de:

1. ✅ Menú de usuario mostrando solo "Dashboard"
2. ✅ Tab Dashboard con todas las secciones
3. ✅ Tab Usuarios con vista rápida
4. ✅ Tab Paquetes con distribución por estado
5. ✅ Tab Clientes con resumen
6. ✅ Tab Mensajes con estadísticas
7. ✅ Tab Settings con configuración
8. ✅ Vista móvil (tabs con solo iconos)
9. ✅ Consola del navegador sin errores
10. ✅ Network tab mostrando llamadas API exitosas

---

## ✅ CRITERIOS DE ACEPTACIÓN

Para considerar las pruebas exitosas, se debe cumplir:

1. ✅ Menú de usuario muestra solo "Dashboard" (Settings eliminado)
2. ✅ Dashboard redirige a `/admin`
3. ✅ Los 6 tabs son visibles y funcionales
4. ✅ Navegación entre tabs sin recargar página
5. ✅ Todos los botones de navegación funcionan
6. ✅ Datos se cargan correctamente en todos los tabs
7. ✅ Responsive funciona en móvil, tablet y desktop
8. ✅ Sin errores en la consola del navegador
9. ✅ Todas las llamadas API son exitosas
10. ✅ Transiciones suaves entre tabs

---

## 🎯 RESULTADO FINAL

**Fecha de prueba:** _______________  
**Probado por:** _______________  
**Navegador:** _______________  
**Versión:** _______________

**Resumen:**
- Total de pruebas: 10
- Pruebas exitosas: ___
- Pruebas fallidas: ___
- Bugs encontrados: ___

**Estado general:** ⬜ Aprobado / ⬜ Rechazado / ⬜ Con observaciones

**Comentarios adicionales:**
_______________________________________________
_______________________________________________
_______________________________________________

---

**Última actualización:** 2024-12-14  
**Versión del dashboard:** 4.1.0  
**Autor:** Kiro AI Assistant

