# 📱 Detección Inteligente de Dispositivos Móviles

**Versión:** 2025-11-28-v3  
**Actualización:** Sistema mejorado para detectar dispositivos móviles modernos con pantallas grandes

---

## 🎯 Problema Resuelto

Los móviles modernos (iPhone 14 Pro Max, Samsung Galaxy S23 Ultra, etc.) tienen pantallas de más de 768px de ancho, por lo que la detección tradicional basada solo en `max-width: 768px` no funcionaba correctamente.

---

## ✅ Nueva Solución: Detección Multi-Criterio

El footer móvil ahora usa **6 criterios diferentes** para detectar si el dispositivo es móvil:

### 1. **Soporte Táctil**
```javascript
const hasTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
```
- Detecta si el dispositivo tiene pantalla táctil

### 2. **Ancho de Pantalla**
```javascript
const isNarrowScreen = window.innerWidth <= 1024;
```
- Incluye móviles grandes y tablets pequeñas (hasta 1024px)

### 3. **User Agent**
```javascript
const mobileRegex = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i;
const isMobileUA = mobileRegex.test(navigator.userAgent);
```
- Detecta dispositivos móviles conocidos por su identificador

### 4. **Orientación Portrait**
```javascript
const isPortrait = window.innerHeight > window.innerWidth;
```
- Los móviles típicamente se usan en vertical

### 5. **Pointer Coarse**
```javascript
const hasCoarsePointer = window.matchMedia('(pointer: coarse)').matches;
```
- Detecta si el dispositivo usa dedos (no mouse preciso)

### 6. **Sin Hover**
```javascript
const noHover = window.matchMedia('(hover: none)').matches;
```
- Los dispositivos táctiles no tienen hover

---

## 🧮 Sistema de Puntuación

El dispositivo se considera **móvil** si cumple:
- **2 o más criterios** de los 6 anteriores, O
- **User Agent** indica definitivamente que es móvil

```javascript
const mobileScore = [criterios].filter(Boolean).length;
return mobileScore >= 2 || isMobileUA;
```

---

## 📐 Media Queries CSS Mejoradas

### Regla 1: Dispositivos táctiles pequeños/medianos
```css
@media (max-width: 1024px) and (hover: none) and (pointer: coarse) {
    /* Mostrar footer móvil */
}
```

### Regla 2: Orientación portrait
```css
@media (orientation: portrait) and (max-width: 1024px) {
    /* Mostrar footer móvil */
}
```

### Regla 3: Desktop con mouse
```css
@media (min-width: 1025px) and (hover: hover) and (pointer: fine) {
    /* Ocultar footer móvil */
}
```

### Regla 4: Tablets en landscape
```css
@media (orientation: landscape) and (min-width: 1024px) {
    /* Ocultar footer móvil, mostrar desktop */
}
```

---

## 📱 Dispositivos Soportados

### ✅ Mostrarán Footer Móvil:

**iPhones:**
- iPhone 14 Pro Max (430 x 932 px)
- iPhone 14 Pro (393 x 852 px)
- iPhone 14 (390 x 844 px)
- iPhone 13 Pro Max (428 x 926 px)
- iPhone SE (375 x 667 px)
- Todos los modelos anteriores

**Android:**
- Samsung Galaxy S23 Ultra (480 x 1080 px)
- Samsung Galaxy S23 (360 x 780 px)
- Google Pixel 7 Pro (412 x 915 px)
- OnePlus 11 (450 x 1008 px)
- Xiaomi 13 Pro (440 x 986 px)
- Todos los dispositivos Android

**Tablets (en portrait):**
- iPad Mini (768 x 1024 px en portrait)
- iPad Air (820 x 1180 px en portrait)
- Samsung Galaxy Tab (800 x 1280 px en portrait)

### ❌ Mostrarán Footer Desktop:

**Desktop:**
- Computadoras con mouse (cualquier resolución)
- Laptops con trackpad

**Tablets en Landscape:**
- iPad en horizontal (1024 x 768 px)
- Tablets Android en horizontal (>1024px ancho)

---

## 🔍 Debug y Verificación

El script incluye logs en consola para debugging:

```javascript
console.log('🔍 Detección de dispositivo:', {
    isMobile: isMobileDevice,
    width: window.innerWidth,
    height: window.innerHeight,
    touchSupport: 'ontouchstart' in window,
    orientation: window.screen.orientation?.type,
    userAgent: navigator.userAgent.substring(0, 50)
});
```

Para ver estos logs:
1. Abre las **DevTools** del navegador (F12)
2. Ve a la pestaña **Console**
3. Recarga la página
4. Verás el log con toda la información de detección

---

## 🔄 Detección Dinámica

El sistema también detecta cambios de orientación:

```javascript
window.addEventListener('orientationchange', function() {
    setTimeout(() => {
        const newIsMobile = detectMobileDevice();
        if (newIsMobile !== isMobileDevice) {
            location.reload(); // Recargar para aplicar cambios
        }
    }, 200);
});
```

Si rotas tu dispositivo y cambia la clasificación (móvil ↔ desktop), la página se recarga automáticamente.

---

## 📊 Ejemplos de Detección

### iPhone 14 Pro Max (430px ancho):
```
✅ hasTouch: true
✅ isNarrowScreen: true (430 <= 1024)
✅ isMobileUA: true (iPhone)
✅ isPortrait: true (932 > 430)
✅ hasCoarsePointer: true
✅ noHover: true
Score: 6/6 → MÓVIL ✅
```

### iPad en Landscape (1024px ancho):
```
✅ hasTouch: true
❌ isNarrowScreen: false (1024 <= 1024, límite)
✅ isMobileUA: true (iPad)
❌ isPortrait: false (768 < 1024)
✅ hasCoarsePointer: true
✅ noHover: true
Score: 4/6 → MÓVIL ✅
Pero CSS landscape rule lo convierte a DESKTOP
```

### Desktop con Mouse (1920px ancho):
```
❌ hasTouch: false
❌ isNarrowScreen: false (1920 > 1024)
❌ isMobileUA: false
❌ isPortrait: false
❌ hasCoarsePointer: false
❌ noHover: false
Score: 0/6 → DESKTOP ✅
```

---

## 🚀 Ventajas del Nuevo Sistema

1. ✅ **Soporta móviles modernos** con pantallas grandes
2. ✅ **Detecta tablets** correctamente según orientación
3. ✅ **No depende solo del ancho** de pantalla
4. ✅ **Usa características del dispositivo** (touch, pointer, hover)
5. ✅ **Adaptable** a cambios de orientación
6. ✅ **Debugging fácil** con logs en consola
7. ✅ **Fallback robusto** con múltiples criterios

---

## 🔧 Mantenimiento

Si necesitas ajustar la detección:

### Cambiar el límite de ancho:
```javascript
const isNarrowScreen = window.innerWidth <= 1024; // Cambiar 1024
```

### Agregar más dispositivos al User Agent:
```javascript
const mobileRegex = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini|TuDispositivo/i;
```

### Ajustar el score mínimo:
```javascript
return mobileScore >= 2; // Cambiar 2 a otro número
```

---

## 📝 Archivos Modificados

- `CODE/src/templates/components/mobile-footer.html` - Detección inteligente implementada
- `DETECCION_INTELIGENTE_MOBILE.md` - Este documento

---

## ✅ Próximos Pasos

1. **Reiniciar el servidor** para aplicar cambios
2. **Limpiar caché** del navegador móvil
3. **Probar** en diferentes dispositivos
4. **Verificar logs** en consola para confirmar detección correcta

---

## 🆘 Troubleshooting

### El footer no aparece en mi móvil:
1. Abre DevTools (F12) en el navegador
2. Ve a Console
3. Busca el log "🔍 Detección de dispositivo"
4. Verifica que `isMobile: true`
5. Si es `false`, revisa los criterios que no se cumplen

### El footer aparece en desktop:
1. Verifica que tu pantalla sea >1024px
2. Verifica que tengas mouse (hover: hover)
3. Verifica que no estés en modo responsive de DevTools

### El footer no se actualiza al rotar:
1. Espera 200ms después de rotar
2. La página debería recargarse automáticamente
3. Si no, recarga manualmente
