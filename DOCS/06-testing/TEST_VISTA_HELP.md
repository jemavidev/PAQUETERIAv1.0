# 🧪 Guía de Pruebas para Vista /help

## ✅ Checklist de Verificación

### 1. Acceso a la Vista
- [ ] Abrir navegador en `http://localhost:8000/help`
- [ ] La página carga sin errores
- [ ] No hay errores en la consola del navegador

### 2. Header y Navegación
- [ ] El header es el mismo que en `/announce` y `/search`
- [ ] El logo de PAPYRUS se muestra correctamente
- [ ] Los enlaces de navegación funcionan:
  - [ ] Inicio
  - [ ] Anunciar
  - [ ] Buscar
  - [ ] Mensajes (si está autenticado)

### 3. Contenido Visual

#### Logo Principal
- [ ] Logo PAPYRUS visible y centrado
- [ ] Tamaño responsive en mobile y desktop

#### Sección "¿Qué es PAQUETEX?"
- [ ] Fondo azul con gradiente
- [ ] Emoji 📦 visible
- [ ] 3 tarjetas con emojis:
  - [ ] 🛡️ Seguro
  - [ ] ⚡ Rápido
  - [ ] 📱 Fácil
- [ ] Efecto hover en las tarjetas

#### Sección de Tarifas
- [ ] Emoji 💰 en el título
- [ ] Tarjeta "Paquete Normal" con emoji 📦
- [ ] Tarjeta "Extra Dimensionado" con emoji 📦📦
- [ ] Tarjeta "Almacenamiento" con emoji 🏪
- [ ] Ejemplo de cálculo con emoji 🧮
- [ ] Efectos hover en todas las tarjetas

#### FAQ Accordion
Verificar que cada pregunta tiene su emoji y funciona:

1. [ ] ℹ️ ¿Cómo funciona el servicio?
   - [ ] Se abre/cierra correctamente
   - [ ] Muestra 4 pasos con emojis (📢, ✅, 🔍, 🎁)

2. [ ] ⏰ ¿Cuánto tiempo tengo para recoger mi paquete?
   - [ ] Se abre/cierra correctamente
   - [ ] Muestra información de tiempos

3. [ ] 🔢 ¿Qué es el código de seguimiento?
   - [ ] Se abre/cierra correctamente
   - [ ] Muestra ejemplos de códigos

4. [ ] 🔍 ¿Cómo busco mi paquete?
   - [ ] Se abre/cierra correctamente
   - [ ] Muestra opciones de búsqueda

5. [ ] 💬 ¿Qué notificaciones recibiré?
   - [ ] Se abre/cierra correctamente
   - [ ] Muestra tipos de notificaciones

6. [ ] 💳 ¿Cómo puedo pagar?
   - [ ] Se abre/cierra correctamente
   - [ ] Muestra métodos de pago (💵 Efectivo, 📱 Transferencia)

7. [ ] 🛡️ ¿Mi paquete está seguro?
   - [ ] Se abre/cierra correctamente
   - [ ] Muestra medidas de seguridad

8. [ ] 🎧 ¿Cómo contacto con soporte?
   - [ ] Se abre/cierra correctamente
   - [ ] Muestra información de contacto con emojis

#### Quick Actions
- [ ] 3 tarjetas con gradientes:
  - [ ] 📢 Anunciar Paquete (verde)
  - [ ] 🔍 Buscar Paquete (púrpura)
  - [ ] 📞 Contactar (azul)
- [ ] Efecto hover con elevación
- [ ] Enlaces funcionan correctamente

#### Sección de Contacto
- [ ] Fondo azul con gradiente
- [ ] Emoji 🎧 en el título
- [ ] Botón de teléfono con emoji 📞
- [ ] Botón de email con emoji ✉️
- [ ] Horario con emoji 🕐

### 4. Footer
- [ ] Footer es el mismo que en otras vistas
- [ ] Enlaces funcionan:
  - [ ] Términos y Condiciones
  - [ ] Política de Privacidad
  - [ ] Cookies
  - [ ] Ayuda

### 5. Responsive Design

#### Mobile (< 640px)
- [ ] Logo se ajusta correctamente
- [ ] Texto legible
- [ ] Tarjetas en columna única
- [ ] FAQ se expande correctamente
- [ ] Botones accesibles
- [ ] No hay scroll horizontal

#### Tablet (640px - 768px)
- [ ] Layout se adapta
- [ ] Tarjetas en 2 columnas donde corresponde
- [ ] Espaciado adecuado

#### Desktop (> 768px)
- [ ] Layout completo
- [ ] Tarjetas en 3 columnas
- [ ] Espaciado óptimo
- [ ] Hover effects visibles

### 6. Interactividad

#### Accordion FAQ
- [ ] Click abre/cierra secciones
- [ ] Flecha rota al abrir
- [ ] Animación suave
- [ ] Solo una sección abierta a la vez (opcional)

#### Hover Effects
- [ ] Tarjetas de características cambian opacidad
- [ ] Tarjetas de tarifas muestran sombra
- [ ] Quick Actions se elevan
- [ ] Botones cambian de color

### 7. Performance
- [ ] Página carga en < 2 segundos
- [ ] No hay parpadeos o saltos de contenido
- [ ] Emojis se renderizan correctamente
- [ ] No hay errores de recursos faltantes

### 8. Accesibilidad
- [ ] Navegación con teclado funciona
- [ ] Tab order es lógico
- [ ] Botones tienen estados focus visibles
- [ ] Contraste de colores es adecuado
- [ ] Emojis tienen contexto textual

### 9. Compatibilidad de Navegadores

#### Chrome/Edge
- [ ] Vista funciona correctamente
- [ ] Emojis se muestran bien
- [ ] Animaciones suaves

#### Firefox
- [ ] Vista funciona correctamente
- [ ] Emojis se muestran bien
- [ ] Animaciones suaves

#### Safari
- [ ] Vista funciona correctamente
- [ ] Emojis se muestran bien
- [ ] Animaciones suaves

### 10. Integración con el Sistema

#### Sin Autenticación
- [ ] Vista accesible públicamente
- [ ] Header muestra opciones públicas
- [ ] No hay errores de autenticación

#### Con Autenticación
- [ ] Vista accesible
- [ ] Header muestra opciones de usuario
- [ ] Dropdown de usuario funciona

## 🐛 Problemas Comunes y Soluciones

### Problema: Emojis no se muestran
**Solución**: Verificar que el navegador soporta emojis Unicode. Actualizar navegador.

### Problema: Accordion no funciona
**Solución**: Verificar que Alpine.js está cargado correctamente en base.html

### Problema: Estilos no se aplican
**Solución**: Verificar que Tailwind CSS está cargado. Limpiar caché del navegador.

### Problema: Header/Footer diferentes
**Solución**: Verificar que el archivo usa `{% extends "base/base.html" %}`

## 📸 Screenshots Esperados

### Desktop
- Header con navegación completa
- Logo centrado grande
- Tarjetas en 3 columnas
- FAQ con emojis visibles
- Footer completo

### Mobile
- Header compacto
- Logo centrado mediano
- Tarjetas en 1 columna
- FAQ expandible
- Footer compacto

## ✅ Criterios de Aceptación

La vista `/help` está lista para producción cuando:

1. ✅ Todos los items del checklist están marcados
2. ✅ No hay errores en consola
3. ✅ Funciona en mobile, tablet y desktop
4. ✅ Todos los enlaces funcionan
5. ✅ Emojis se muestran correctamente
6. ✅ Accordion funciona suavemente
7. ✅ Header y footer son consistentes con otras vistas
8. ✅ Performance es óptima (< 2s carga)

---

**Última actualización**: 2025-01-XX  
**Versión**: 4.0
