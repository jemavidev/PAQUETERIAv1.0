# 📱 Fix: Soporte de Cámara en Dispositivos Móviles

**Fecha:** 2025-11-19  
**Problema:** El botón "Seleccionar imágenes" en móviles solo mostraba la galería, no permitía tomar fotos con la cámara.

---

## 🔍 Diagnóstico del Problema

### Causa Raíz:
Había **múltiples listeners** configurándose en diferentes momentos que entraban en conflicto:

1. **Listener del modal (línea ~1415)**: Se configuraba cuando se abría el modal de "Recibir"
2. **Interceptor global (línea ~4055)**: Listener general para todos los clicks
3. **Funciones duplicadas (línea ~4260)**: `isMobileDevice()` y `showMobileCaptureOptions()` definidas tarde

El listener del modal se ejecutaba **primero** y hacía click directo en el input sin verificar si era móvil, evitando que se mostrara el modal de opciones.

---

## ✅ Solución Implementada

### 1. **Mover Funciones al Inicio del Script**

Las funciones `isMobileDevice()` y `showMobileCaptureOptions()` se movieron al inicio del `<script>` (después de la línea 665) para que estén disponibles globalmente desde el principio.

```javascript
// ========================================
// DETECCIÓN DE DISPOSITIVOS MÓVILES
// ========================================
function isMobileDevice() {
    const userAgent = navigator.userAgent.toLowerCase();
    const isMobileUA = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent);
    const isSmallScreen = window.innerWidth <= 768;
    const hasTouchOnly = navigator.maxTouchPoints > 0 && !window.matchMedia('(pointer: fine)').matches;
    
    const result = isMobileUA || (isSmallScreen && hasTouchOnly);
    
    // Log de depuración
    console.log('🔍 Detección de dispositivo:', {
        userAgent: userAgent,
        isMobileUA: isMobileUA,
        screenWidth: window.innerWidth,
        isSmallScreen: isSmallScreen,
        touchPoints: navigator.maxTouchPoints,
        hasFinePonter: window.matchMedia('(pointer: fine)').matches,
        hasTouchOnly: hasTouchOnly,
        resultado: result ? '📱 MÓVIL' : '💻 ESCRITORIO'
    });
    
    return result;
}

function showMobileCaptureOptions() {
    // ... código del modal ...
}
```

### 2. **Actualizar Listener del Modal**

El listener que se configura cuando se abre el modal de "Recibir" ahora verifica el tipo de dispositivo:

```javascript
newBtn.addEventListener('click', function(e) {
    console.log('🔘 ===== CLICK DIRECTO EN BOTÓN =====');
    e.preventDefault();
    e.stopPropagation();
    
    // Verificar límite
    if (selectedImages.length >= 3) {
        showInfoToast('Límite alcanzado', 'Ya tienes el máximo de 3 imágenes seleccionadas.', 3000);
        return;
    }
    
    const packageImagesInput = document.getElementById('packageImages');
    if (packageImagesInput) {
        // Detectar si es dispositivo móvil
        if (isMobileDevice()) {
            console.log('📱 Dispositivo móvil detectado - mostrando opciones');
            showMobileCaptureOptions();
        } else {
            console.log('💻 Escritorio detectado - abriendo selector');
            packageImagesInput.removeAttribute('capture');
            packageImagesInput.setAttribute('accept', 'image/jpeg,image/jpg,image/png,image/webp');
            packageImagesInput.click();
        }
    }
});
```

### 3. **Actualizar Interceptor Global**

El interceptor global también usa la misma lógica:

```javascript
if (isMobileDevice()) {
    console.log('📱 Dispositivo móvil detectado - mostrando opciones');
    showMobileCaptureOptions();
} else {
    console.log('💻 Escritorio detectado - abriendo selector de archivos');
    packageImagesInput.removeAttribute('capture');
    packageImagesInput.setAttribute('accept', 'image/jpeg,image/jpg,image/png,image/webp');
    packageImagesInput.click();
}
```

### 4. **Eliminar Duplicados**

Se eliminaron las definiciones duplicadas de las funciones que estaban en la línea ~4260.

### 5. **Actualizar `image-upload-optimized.js`**

El archivo JavaScript externo también configura el input dinámicamente:

```javascript
function optimizeFileInput() {
    const input = document.getElementById('packageImages');
    if (!input) return;
    
    if (isDesktopDevice()) {
        input.removeAttribute('capture');
        input.setAttribute('accept', CONFIG.ALLOWED_TYPES.join(','));
        console.log('📁 Configurado para escritorio: solo galería');
    } else {
        input.setAttribute('capture', 'environment');
        input.setAttribute('accept', 'image/*');
        console.log('📱 Configurado para móvil: cámara + galería');
    }
}
```

---

## 🧪 Cómo Probar

### En Móvil:
1. Abrir http://localhost:8000/packages en un dispositivo móvil
2. Click en un paquete → "Recibir"
3. Click en "Seleccionar imágenes"
4. **Debe aparecer un modal** con dos opciones:
   - 🔵 **"Tomar foto"** → Abre la cámara
   - 🟣 **"Seleccionar de galería"** → Abre la galería

### En Escritorio:
1. Abrir http://localhost:8000/packages en un PC
2. Click en un paquete → "Recibir"
3. Click en "Seleccionar imágenes"
4. **Debe abrir directamente** el selector de archivos

### Archivo de Prueba:
También puedes abrir `CODE/test_mobile_detection.html` en cualquier navegador para ver cómo se detecta tu dispositivo.

---

## 📊 Logs de Depuración

Al hacer click en "Seleccionar imágenes", verás en la consola del navegador:

```
🔍 Detección de dispositivo: {
    userAgent: "...",
    isMobileUA: true/false,
    screenWidth: 375,
    isSmallScreen: true/false,
    touchPoints: 5,
    hasFinePonter: false,
    hasTouchOnly: true/false,
    resultado: "📱 MÓVIL" o "💻 ESCRITORIO"
}
```

Seguido de:
- `📱 Dispositivo móvil detectado - mostrando opciones` (móvil)
- `💻 Escritorio detectado - abriendo selector` (escritorio)

---

## 📁 Archivos Modificados

1. **`CODE/src/templates/packages/packages.html`**
   - Movidas funciones al inicio del script
   - Actualizado listener del modal
   - Actualizado interceptor global
   - Eliminadas definiciones duplicadas
   - Agregados logs de depuración

2. **`CODE/src/static/js/image-upload-optimized.js`**
   - Configuración dinámica del input según dispositivo
   - Agregados logs de depuración

3. **`DOCS/OPTIMIZACION_SELECCION_IMAGENES.md`**
   - Actualizada documentación con nuevos cambios

4. **`CODE/test_mobile_detection.html`** *(Nuevo)*
   - Archivo de prueba para verificar detección

---

## ✅ Resultado Final

| Dispositivo | Comportamiento |
|-------------|----------------|
| 📱 **Móvil** | Modal con opciones → Tomar foto (cámara) o Galería |
| 💻 **Escritorio** | Selector de archivos directo (solo galería) |

**Estado:** ✅ Funcionando correctamente en ambos dispositivos
