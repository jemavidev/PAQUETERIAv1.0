# 🚨 Manejador de Errores de JavaScript - PAQUETES EL CLUB v1.0

## 📋 Descripción

Sistema avanzado para capturar y mostrar errores de JavaScript usando el mismo formato visual de los componentes de error del sistema. Captura automáticamente errores, promesas rechazadas y errores de recursos.

## 🚀 Uso Básico

### 1. Incluir el Componente

```html
<!-- Incluir en tu template -->
{% include 'components/javascript_error_handler.html' %}
```

### 2. El Componente se Activa Automáticamente

Una vez incluido, el manejador captura automáticamente:
- **Errores de JavaScript** (window.onerror)
- **Promesas rechazadas** (unhandledrejection)
- **Errores de recursos** (imágenes, scripts, CSS, etc.)
- **Errores de Alpine.js**

## 📝 Funciones Globales Disponibles

### Mostrar Error Personalizado
```javascript
window.mostrarErrorJS('Título', 'Mensaje', 'tipo', 'Detalles opcionales');
```

**Parámetros:**
- `titulo` (string): Título del error
- `mensaje` (string): Mensaje descriptivo
- `tipo` (string): 'error', 'warning', 'info', 'success'
- `detalles` (string, opcional): Detalles técnicos del error

### Mostrar Error de Validación
```javascript
window.mostrarErrorValidacion('El campo es requerido');
```

### Mostrar Advertencia
```javascript
window.mostrarAdvertencia('Esta operación es irreversible');
```

### Mostrar Información
```javascript
window.mostrarInformacion('El sistema se reiniciará en 5 minutos');
```

### Mostrar Éxito
```javascript
window.mostrarExito('Operación completada exitosamente');
```

## 🎯 Ejemplos de Uso

### En Formularios de Validación
```javascript
function validarFormulario() {
    const numeroGuia = document.getElementById('numeroGuia').value;
    
    if (!numeroGuia) {
        window.mostrarErrorValidacion('El número de guía es requerido');
        return false;
    }
    
    if (numeroGuia.length < 10) {
        window.mostrarErrorValidacion('El número de guía debe tener al menos 10 caracteres');
        return false;
    }
    
    // Si todo está bien
    window.mostrarExito('Formulario validado correctamente');
    return true;
}
```

### En Llamadas AJAX
```javascript
async function enviarDatos() {
    try {
        const response = await fetch('/api/paquetes', {
            method: 'POST',
            body: JSON.stringify(datos)
        });
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const resultado = await response.json();
        window.mostrarExito('Datos enviados correctamente');
        
    } catch (error) {
        window.mostrarErrorJS(
            'Error de Conexión',
            'No se pudieron enviar los datos al servidor',
            'error',
            `Detalles: ${error.message}`
        );
    }
}
```

### En Validación de Email
```javascript
function validarEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (!regex.test(email)) {
        window.mostrarErrorValidacion('El email no tiene un formato válido');
        return false;
    }
    
    return true;
}
```

## 🎨 Tipos de Errores Soportados

### Error (Rojo)
- **Uso**: Errores críticos del sistema
- **Ejemplo**: "Error de conexión con el servidor"

### Advertencia (Amarillo)
- **Uso**: Advertencias y notificaciones importantes
- **Ejemplo**: "Esta operación eliminará todos los datos"

### Información (Azul)
- **Uso**: Información general del sistema
- **Ejemplo**: "El sistema se reiniciará en 5 minutos"

### Éxito (Verde)
- **Uso**: Confirmaciones de operaciones exitosas
- **Ejemplo**: "El paquete se anunció correctamente"

## 🔧 Características Técnicas

### Captura Automática
- **Errores de JavaScript**: Captura automáticamente todos los errores
- **Promesas rechazadas**: Detecta promesas no manejadas
- **Errores de recursos**: Captura errores de carga de imágenes, scripts, CSS
- **Stack trace**: Muestra detalles técnicos del error

### Posicionamiento
- **Posición fija**: Aparece en la esquina superior derecha
- **Z-index alto**: Siempre visible sobre otros elementos
- **Responsive**: Se adapta a móviles y tablets

### Auto-cierre
- **Errores**: Se cierran automáticamente después de 10 segundos
- **Otros tipos**: Permanecen hasta que el usuario los cierre
- **Cierre manual**: Botón "Cerrar" siempre disponible

## 📱 Diseño Responsive

### Desktop
- **Posición**: Esquina superior derecha
- **Ancho**: Máximo 400px
- **Z-index**: 9999

### Tablet
- **Posición**: Esquina superior derecha con margen reducido
- **Ancho**: Máximo 350px

### Mobile
- **Posición**: Ancho completo con márgenes laterales
- **Ancho**: calc(100vw - 20px)
- **Padding**: Reducido para pantallas pequeñas

## 🔍 Detalles Técnicos Mostrados

### Para Errores de JavaScript
```
Archivo: script.js
Línea: 25
Columna: 10

Stack trace:
Error: Cannot read property 'propiedad' of null
    at funcionError (script.js:25:10)
    at HTMLButtonElement.onclick (index.html:15:5)
```

### Para Promesas Rechazadas
```
Razón: Error de conexión con el servidor

Stack trace:
Error: Failed to fetch
    at enviarDatos (script.js:30:15)
    at async procesarFormulario (script.js:45:8)
```

### Para Errores de Recursos
```
Elemento: IMG
Origen: https://ejemplo.com/imagen.jpg
Tipo: error
```

## 🚀 Implementación en PAQUETES EL CLUB

### 1. Incluir en Layout Principal
```html
<!-- En templates/base.html o layout principal -->
{% include 'components/javascript_error_handler.html' %}
```

### 2. Usar en Formularios
```javascript
// En formularios de anuncio de paquetes
function anunciarPaquete() {
    if (!validarDatos()) {
        window.mostrarErrorValidacion('Por favor, complete todos los campos requeridos');
        return;
    }
    
    // Continuar con el envío...
}
```

### 3. Usar en Búsquedas
```javascript
// En búsqueda de paquetes
function buscarPaquete() {
    const numeroGuia = document.getElementById('numeroGuia').value;
    
    if (!numeroGuia) {
        window.mostrarErrorValidacion('Ingrese un número de guía para buscar');
        return;
    }
    
    // Realizar búsqueda...
}
```

## ⚡ Rendimiento

- **Tamaño**: ~3KB (HTML + CSS + JS)
- **Dependencias**: Alpine.js (ya incluido en el proyecto)
- **Memoria**: Mínimo uso de memoria
- **Impacto**: No afecta el rendimiento de la aplicación

## 🐛 Solución de Problemas

### El manejador no captura errores
1. Verificar que Alpine.js esté cargado
2. Comprobar que el componente esté incluido en el template
3. Revisar la consola para errores de JavaScript

### Los errores no se muestran
1. Verificar que no hay conflictos de CSS
2. Comprobar que el z-index no está siendo sobrescrito
3. Revisar que las funciones globales estén disponibles

### Errores duplicados
1. Verificar que el componente solo se incluye una vez
2. Comprobar que no hay múltiples manejadores de errores
3. Revisar la configuración de Alpine.js

## 📞 Soporte

Para problemas o mejoras en el manejador de errores de JavaScript, contactar al equipo de desarrollo de PAQUETES EL CLUB v1.0.

---

**Última actualización**: 2025-01-24
**Versión**: 1.0.0
**Mantenido por**: Equipo de Desarrollo PAQUETES EL CLUB
