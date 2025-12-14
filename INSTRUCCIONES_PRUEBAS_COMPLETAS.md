# 🧪 INSTRUCCIONES COMPLETAS DE PRUEBAS - DASHBOARD UNIFICADO

**URL:** https://staging.jemavi.co/admin  
**Fecha:** 2024-12-14  
**Versión:** 4.1.0

---

## 📋 MÉTODOS DE PRUEBA DISPONIBLES

Tienes 3 formas de probar el dashboard:

1. **Pruebas Manuales** - Checklist paso a paso
2. **Pruebas Automáticas en Navegador** - Script JavaScript
3. **Pruebas Visuales** - Verificación de UI/UX

---

## 🔧 MÉTODO 1: PRUEBAS AUTOMÁTICAS EN NAVEGADOR (RECOMENDADO)

### Paso 1: Acceder al Dashboard
1. Ir a https://staging.jemavi.co
2. Hacer login con usuario ADMIN o OPERADOR
3. Hacer clic en el avatar del usuario (esquina superior derecha)
4. Hacer clic en "Dashboard"
5. Verificar que estás en `/admin`

### Paso 2: Abrir la Consola del Navegador
- **Chrome/Edge:** Presiona `F12` o `Ctrl+Shift+J` (Windows) / `Cmd+Option+J` (Mac)
- **Firefox:** Presiona `F12` o `Ctrl+Shift+K` (Windows) / `Cmd+Option+K` (Mac)
- **Safari:** Presiona `Cmd+Option+C`

### Paso 3: Ejecutar el Script de Pruebas
1. Abre el archivo `test_dashboard_browser.js`
2. Copia TODO el contenido del archivo
3. Pega en la consola del navegador
4. Presiona `Enter`

### Paso 4: Ver Resultados
El script ejecutará automáticamente todas las pruebas y mostrará:
- ✓ Pruebas exitosas en verde
- ✗ Pruebas fallidas en rojo
- Resumen final con porcentaje de éxito

**Resultado esperado:** 
```
════════════════════════════════════════════════════════════════
✓ TODAS LAS PRUEBAS PASARON EXITOSAMENTE
════════════════════════════════════════════════════════════════

Total de pruebas: 40+
✓ Pruebas exitosas: 40+
✗ Pruebas fallidas: 0
Porcentaje de éxito: 100%
```

---

## 📝 MÉTODO 2: PRUEBAS MANUALES DETALLADAS

Sigue el checklist completo en el archivo `PRUEBAS_DASHBOARD_MANUAL.md`

### Resumen de Pruebas Manuales:

#### ✅ Prueba 1: Menú de Usuario
- [ ] Verificar que solo aparece "Dashboard" (NO "Settings")
- [ ] Hacer clic en "Dashboard" y verificar que va a `/admin`

#### ✅ Prueba 2: Navegación de Tabs
- [ ] Hacer clic en cada uno de los 6 tabs
- [ ] Verificar que cambian sin recargar la página
- [ ] Verificar que el tab activo cambia de color

#### ✅ Prueba 3: Tab Dashboard (Estadísticas)
- [ ] Verificar 6 secciones: Financiero, Paquetes, Clientes, SMS, Performance, Salud
- [ ] Verificar que todos los números cargan correctamente
- [ ] Verificar tabla "Top 5 Clientes"
- [ ] Verificar barras de progreso de SMS

#### ✅ Prueba 4: Tab Usuarios
- [ ] Verificar 3 tarjetas: Total, Activos, Administradores
- [ ] Hacer clic en "Ir a Gestión de Usuarios"
- [ ] Verificar que redirige a `/admin/users`

#### ✅ Prueba 5: Tab Paquetes
- [ ] Verificar 4 tarjetas de estado (Anunciados, Recibidos, Entregados, Cancelados)
- [ ] Hacer clic en "Ver Todos los Paquetes"
- [ ] Verificar que redirige a `/packages`

#### ✅ Prueba 6: Tab Clientes
- [ ] Verificar 3 tarjetas: Total, VIP, Nuevos
- [ ] Hacer clic en "Ver Todos los Clientes"
- [ ] Verificar que redirige a `/customers`

#### ✅ Prueba 7: Tab Mensajes
- [ ] Verificar 2 tarjetas: Pendientes, Resueltos
- [ ] Hacer clic en "Ver Todos los Mensajes"
- [ ] Verificar que redirige a `/messages`

#### ✅ Prueba 8: Tab Settings
- [ ] Verificar sección "Enlaces Rápidos" (4 enlaces)
- [ ] Verificar sección "Información del Sistema"
- [ ] Verificar sección "Límites y Configuración" (6 tarjetas)
- [ ] Probar cada enlace rápido

#### ✅ Prueba 9: Responsive Design
- [ ] Desktop (> 1024px): Todos los tabs visibles, grid 3-4 columnas
- [ ] Tablet (768-1024px): Scroll horizontal, grid 2 columnas
- [ ] Mobile (< 768px): Solo iconos, grid 1 columna

#### ✅ Prueba 10: Botón Actualizar
- [ ] Hacer clic en "Actualizar" (esquina superior derecha)
- [ ] Verificar que la página se recarga
- [ ] Verificar que los datos se actualizan

---

## 👁️ MÉTODO 3: PRUEBAS VISUALES

### Verificaciones Visuales Rápidas:

#### 1. Colores y Estilos
- [ ] Tab activo tiene borde azul (`border-papyrus-blue`)
- [ ] Tabs inactivos tienen borde transparente
- [ ] Hover en tabs muestra efecto visual
- [ ] Tarjetas tienen sombra y bordes redondeados

#### 2. Iconos
- [ ] Cada tab tiene su icono correspondiente
- [ ] Iconos son visibles y del tamaño correcto
- [ ] En móvil, solo se muestran iconos (texto oculto)

#### 3. Espaciado y Layout
- [ ] Espaciado consistente entre elementos
- [ ] Tarjetas alineadas correctamente
- [ ] Sin elementos superpuestos
- [ ] Scroll funciona correctamente

#### 4. Tipografía
- [ ] Títulos son legibles y del tamaño correcto
- [ ] Números grandes y destacados
- [ ] Texto secundario en gris
- [ ] Sin texto cortado o truncado

#### 5. Animaciones
- [ ] Transiciones suaves al cambiar tabs
- [ ] Sin parpadeos o saltos
- [ ] Loading states visibles mientras carga
- [ ] Hover effects funcionan correctamente

---

## 🐛 CHECKLIST DE ERRORES COMUNES

### Errores que NO deben aparecer:

- [ ] ❌ Error 404 en alguna ruta
- [ ] ❌ Error 500 en el servidor
- [ ] ❌ Errores en la consola del navegador
- [ ] ❌ Warnings de JavaScript
- [ ] ❌ Datos que no cargan (quedan en "Cargando...")
- [ ] ❌ Tabs que no cambian al hacer clic
- [ ] ❌ Botones que no funcionan
- [ ] ❌ Enlaces rotos
- [ ] ❌ Imágenes o iconos que no cargan
- [ ] ❌ Estilos CSS que no se aplican

### Comportamientos Correctos:

- [ ] ✅ Todos los tabs cambian sin recargar
- [ ] ✅ Datos cargan en menos de 2 segundos
- [ ] ✅ Botones responden al primer clic
- [ ] ✅ Enlaces redirigen correctamente
- [ ] ✅ Responsive funciona en todos los tamaños
- [ ] ✅ Sin errores en consola
- [ ] ✅ Transiciones suaves
- [ ] ✅ Iconos visibles
- [ ] ✅ Colores correctos
- [ ] ✅ Texto legible

---

## 📊 TABLA DE VERIFICACIÓN RÁPIDA

| Componente | Funciona | Notas |
|------------|----------|-------|
| Menú Usuario | ⬜ | Solo "Dashboard" visible |
| Tab Dashboard | ⬜ | 6 secciones con datos |
| Tab Usuarios | ⬜ | 3 tarjetas + botón |
| Tab Paquetes | ⬜ | 4 tarjetas + botón |
| Tab Clientes | ⬜ | 3 tarjetas + botón |
| Tab Mensajes | ⬜ | 2 tarjetas + botón |
| Tab Settings | ⬜ | 3 secciones completas |
| Navegación | ⬜ | Sin recargar página |
| Botones | ⬜ | Todos funcionan |
| Responsive | ⬜ | Móvil, tablet, desktop |
| Carga de datos | ⬜ | Rápida y correcta |
| Sin errores | ⬜ | Consola limpia |

---

## 🎯 CRITERIOS DE ÉXITO

Para considerar las pruebas exitosas:

### Funcionalidad (70%)
- ✅ Todos los tabs funcionan
- ✅ Navegación sin recargar
- ✅ Botones funcionan
- ✅ Datos cargan correctamente
- ✅ Enlaces redirigen bien

### UI/UX (20%)
- ✅ Diseño responsive
- ✅ Colores correctos
- ✅ Iconos visibles
- ✅ Transiciones suaves
- ✅ Sin errores visuales

### Performance (10%)
- ✅ Carga rápida (< 2s)
- ✅ Sin errores en consola
- ✅ Sin memory leaks
- ✅ Navegación fluida

---

## 📸 SCREENSHOTS REQUERIDOS

Toma screenshots de:

1. **Menú de usuario** mostrando solo "Dashboard"
2. **Tab Dashboard** con todas las secciones visibles
3. **Tab Usuarios** con vista rápida
4. **Tab Paquetes** con distribución por estado
5. **Tab Clientes** con resumen
6. **Tab Mensajes** con estadísticas
7. **Tab Settings** con configuración completa
8. **Vista móvil** (< 768px) mostrando tabs con solo iconos
9. **Consola del navegador** sin errores
10. **Network tab** mostrando llamadas API exitosas (200 OK)

---

## 📝 REPORTE DE RESULTADOS

### Información General
- **Fecha de prueba:** _______________
- **Probado por:** _______________
- **Navegador:** _______________
- **Versión del navegador:** _______________
- **Sistema operativo:** _______________
- **Resolución de pantalla:** _______________

### Resultados
- **Total de pruebas:** _______________
- **Pruebas exitosas:** _______________
- **Pruebas fallidas:** _______________
- **Porcentaje de éxito:** _______________%

### Estado General
- [ ] ✅ Aprobado - Todo funciona correctamente
- [ ] ⚠️ Aprobado con observaciones - Funciona pero hay mejoras menores
- [ ] ❌ Rechazado - Hay errores críticos que deben corregirse

### Bugs Encontrados
1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

### Observaciones
_______________________________________________
_______________________________________________
_______________________________________________

### Recomendaciones
_______________________________________________
_______________________________________________
_______________________________________________

---

## 🚀 PRÓXIMOS PASOS

Después de completar las pruebas:

1. **Si todo pasa:** ✅
   - Documentar resultados
   - Tomar screenshots
   - Aprobar para producción

2. **Si hay errores menores:** ⚠️
   - Documentar bugs
   - Crear tickets
   - Priorizar correcciones

3. **Si hay errores críticos:** ❌
   - Reportar inmediatamente
   - No desplegar a producción
   - Corregir antes de continuar

---

## 📞 SOPORTE

Si encuentras problemas durante las pruebas:

1. **Verificar logs del servidor:**
   ```bash
   ssh ubuntu@staging "cd /home/ubuntu/paqueteria-staging && docker compose -f docker-compose.staging.yml logs --tail=50 app"
   ```

2. **Verificar estado de servicios:**
   ```bash
   ssh ubuntu@staging "cd /home/ubuntu/paqueteria-staging && docker compose -f docker-compose.staging.yml ps"
   ```

3. **Reiniciar servicios si es necesario:**
   ```bash
   ssh ubuntu@staging "cd /home/ubuntu/paqueteria-staging && docker compose -f docker-compose.staging.yml restart app"
   ```

4. **Verificar health check:**
   ```bash
   curl -sL https://staging.jemavi.co/health
   ```

---

**Última actualización:** 2024-12-14  
**Versión del dashboard:** 4.1.0  
**Autor:** Kiro AI Assistant

