# Guía de Pruebas - Scroll en Dispositivos Móviles

## Objetivo
Verificar que todas las vistas del sistema permitan hacer scroll completo hasta el final del contenido en dispositivos móviles pequeños.

## Dispositivos de Prueba Recomendados

### Dispositivos Físicos
1. **iPhone SE (2020)** - 375x667px
2. **iPhone 12/13 Mini** - 375x812px
3. **Samsung Galaxy S10** - 360x760px
4. **Dispositivos Android pequeños** - 320x568px

### Emuladores/Simuladores
1. Chrome DevTools - Modo dispositivo móvil
2. Firefox Responsive Design Mode
3. Safari iOS Simulator (macOS)

## Vistas Críticas a Probar

### 1. Vista de Anunciar Paquete (`/announce`)
- [ ] Formulario completo visible
- [ ] Scroll hasta el botón de envío
- [ ] Campos de entrada accesibles
- [ ] Sin contenido cortado

### 2. Vista de Paquetes (`/packages`)
- [ ] Lista completa de paquetes visible
- [ ] Scroll hasta el último paquete
- [ ] Botones de acción accesibles
- [ ] Filtros y búsqueda funcionales

### 3. Vista de Dashboard (`/dashboard`)
- [ ] Todas las tarjetas de estadísticas visibles
- [ ] Gráficos completos
- [ ] Scroll hasta el footer
- [ ] Sin elementos superpuestos

### 4. Vista de Mensajes (`/messages`)
- [ ] Lista completa de mensajes
- [ ] Scroll hasta el último mensaje
- [ ] Formulario de respuesta accesible
- [ ] Sin contenido oculto

### 5. Vista de Clientes (`/customers/manage`)
- [ ] Tabla completa de clientes
- [ ] Scroll horizontal si es necesario
- [ ] Scroll vertical hasta el último cliente
- [ ] Botones de acción visibles

### 6. Vista de Búsqueda (`/search`)
- [ ] Formulario de búsqueda completo
- [ ] Resultados completos visibles
- [ ] Scroll hasta el último resultado
- [ ] Paginación accesible

### 7. Vista de Configuración (`/settings`)
- [ ] Todas las secciones accesibles
- [ ] Formularios completos
- [ ] Botones de guardar visibles
- [ ] Sin contenido cortado

### 8. Vista de Login (`/auth/login`)
- [ ] Formulario completo visible
- [ ] Botones accesibles
- [ ] Enlaces de recuperación visibles
- [ ] Sin elementos superpuestos

## Procedimiento de Prueba

### Paso 1: Preparación
1. Abrir el navegador en modo incógnito
2. Activar las herramientas de desarrollador
3. Seleccionar un dispositivo móvil de la lista
4. Configurar la orientación (portrait y landscape)

### Paso 2: Prueba de Scroll Básico
1. Cargar la vista a probar
2. Intentar hacer scroll hasta el final de la página
3. Verificar que se puede llegar al footer
4. Verificar que no hay contenido cortado

### Paso 3: Prueba de Interacción
1. Hacer clic en elementos interactivos
2. Verificar que los modales/overlays permiten scroll
3. Probar formularios largos
4. Verificar que los teclados virtuales no bloquean contenido

### Paso 4: Prueba de Orientación
1. Rotar el dispositivo a landscape
2. Verificar que el scroll sigue funcionando
3. Rotar de vuelta a portrait
4. Verificar consistencia

### Paso 5: Prueba de Contenido Dinámico
1. Cargar contenido dinámicamente (si aplica)
2. Verificar que el scroll se ajusta
3. Probar lazy loading de imágenes
4. Verificar que no hay saltos de contenido

## Checklist de Verificación

### Comportamiento Esperado
- [ ] El scroll es suave y natural
- [ ] Se puede llegar al final del contenido
- [ ] No hay "rebote" excesivo en iOS
- [ ] El header sticky no bloquea contenido
- [ ] El footer es visible al final
- [ ] Los modales permiten scroll interno
- [ ] Los formularios largos son completamente accesibles
- [ ] Las tablas permiten scroll horizontal
- [ ] No hay contenido oculto o cortado
- [ ] El teclado virtual no bloquea campos de entrada

### Problemas Comunes a Detectar
- [ ] Contenido cortado en la parte inferior
- [ ] Scroll bloqueado en cierto punto
- [ ] Elementos superpuestos que impiden scroll
- [ ] Altura fija que limita el contenido
- [ ] Overflow hidden que oculta contenido
- [ ] Problemas con 100vh en iOS Safari
- [ ] Teclado virtual que oculta campos
- [ ] Modales que no permiten scroll

## Herramientas de Debug

### Consola del Navegador
```javascript
// Verificar altura del documento
console.log('Document height:', document.documentElement.scrollHeight);
console.log('Viewport height:', window.innerHeight);
console.log('Body height:', document.body.scrollHeight);

// Verificar scroll actual
console.log('Scroll position:', window.pageYOffset);

// Usar herramienta de debug incluida
scrollDebug.analyze(); // Analizar problemas
scrollDebug.fix();     // Aplicar correcciones
scrollDebug.report();  // Reportar problemas
```

### Modo Debug
Para activar el modo debug detallado:
1. Abrir `CODE/src/static/js/mobile-scroll-debug.js`
2. Cambiar `DEBUG_MODE = false` a `DEBUG_MODE = true`
3. Recargar la página
4. Ver información de debug en la esquina inferior izquierda

## Criterios de Éxito

### Mínimo Aceptable
- ✅ Todas las vistas permiten scroll hasta el final
- ✅ No hay contenido inaccesible
- ✅ Los formularios son completamente funcionales
- ✅ El scroll es suave en iOS y Android

### Óptimo
- ✅ Scroll suave con `-webkit-overflow-scrolling: touch`
- ✅ Sin problemas de viewport en iOS Safari
- ✅ Rendimiento óptimo sin lag
- ✅ Experiencia consistente en todos los dispositivos

## Registro de Problemas

### Formato de Reporte
```
Vista: [Nombre de la vista]
Dispositivo: [Modelo o tamaño]
Navegador: [Chrome/Safari/Firefox + versión]
Problema: [Descripción detallada]
Pasos para reproducir:
1. [Paso 1]
2. [Paso 2]
3. [Paso 3]
Comportamiento esperado: [Descripción]
Comportamiento actual: [Descripción]
Screenshot: [Si es posible]
```

## Correcciones Aplicadas

### Archivos Modificados
1. ✅ `CODE/src/static/css/utilities/mobile-scroll-fix.css` - Nuevo archivo con correcciones
2. ✅ `CODE/src/static/css/main.css` - Importa el nuevo archivo
3. ✅ `CODE/src/static/css/responsive/mobile.css` - Reglas adicionales de scroll
4. ✅ `CODE/src/templates/base/base.html` - Estructura mejorada
5. ✅ `CODE/src/static/js/mobile-scroll-debug.js` - Script de debug y auto-fix

### Principales Correcciones
- Eliminación de alturas fijas en body y main
- Habilitación de `-webkit-overflow-scrolling: touch`
- Fix específico para iOS Safari viewport
- Prevención de overflow hidden en contenedores
- Scroll automático en contenido dinámico

## Próximos Pasos

1. **Pruebas Iniciales**
   - Probar en Chrome DevTools con diferentes dispositivos
   - Verificar las 8 vistas críticas
   - Documentar cualquier problema encontrado

2. **Pruebas en Dispositivos Reales**
   - Probar en al menos 2 dispositivos iOS
   - Probar en al menos 2 dispositivos Android
   - Verificar en diferentes tamaños de pantalla

3. **Ajustes Finos**
   - Corregir problemas específicos encontrados
   - Optimizar rendimiento si es necesario
   - Ajustar estilos para casos edge

4. **Validación Final**
   - Pruebas de regresión en todas las vistas
   - Verificación de accesibilidad
   - Aprobación del usuario final

## Contacto y Soporte

Si encuentras problemas durante las pruebas:
1. Documenta el problema usando el formato de reporte
2. Captura screenshots o videos si es posible
3. Incluye información del dispositivo y navegador
4. Reporta al equipo de desarrollo

---

**Última actualización:** 2024-11-27
**Versión:** 4.0.1
