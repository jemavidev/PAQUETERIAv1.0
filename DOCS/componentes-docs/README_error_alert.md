# 🚨 Componente Error Alert - PAQUETES EL CLUB v1.0

## 📋 Descripción

Componente reutilizable para mostrar mensajes de error, advertencia, información y éxito en cualquier parte de la aplicación. Basado en el diseño original del sistema de anuncios de paquetes.

## 🚀 Uso Básico

### 1. Incluir el Componente

```html
{% include 'components/error_alert.html' %}
```

### 2. Uso con Parámetros Básicos

```html
{% include 'components/error_alert.html' with 
    title="Error de Validación" 
    message="El número de guía ingresado no es válido." 
    type="error" 
%}
```

## 📝 Parámetros Disponibles

| Parámetro | Tipo | Valor por Defecto | Descripción |
|-----------|------|-------------------|-------------|
| `title` | string | "Error del Sistema" | Título del mensaje |
| `message` | string | "Error del sistema..." | Descripción del error |
| `type` | string | "error" | Tipo de alerta: `error`, `warning`, `info`, `success` |
| `show` | boolean | `true` | Si mostrar la alerta inicialmente |
| `auto_close` | boolean | `false` | Si cerrar automáticamente |
| `close_delay` | number | `5000` | Tiempo en ms antes de auto-cerrar |
| `button_text` | string | "Cerrar" | Texto del botón de cerrar |
| `on_close` | string | `""` | Código JavaScript a ejecutar al cerrar |

## 🎨 Tipos de Alertas

### Error (Rojo)
```html
{% include 'components/error_alert.html' with 
    title="Error del Sistema" 
    message="Ha ocurrido un error inesperado." 
    type="error" 
%}
```

### Advertencia (Amarillo)
```html
{% include 'components/error_alert.html' with 
    title="Advertencia" 
    message="El paquete ya fue anunciado anteriormente." 
    type="warning" 
%}
```

### Información (Azul)
```html
{% include 'components/error_alert.html' with 
    title="Información" 
    message="El sistema se reiniciará en 5 minutos." 
    type="info" 
%}
```

### Éxito (Verde)
```html
{% include 'components/error_alert.html' with 
    title="Éxito" 
    message="El paquete se anunció correctamente." 
    type="success" 
%}
```

## 🔧 Uso Avanzado

### Con Auto-Cierre
```html
{% include 'components/error_alert.html' with 
    title="Éxito" 
    message="Operación completada exitosamente." 
    type="success" 
    auto_close=true 
    close_delay=3000 
%}
```

### Con Callback Personalizado
```html
{% include 'components/error_alert.html' with 
    title="Error de Conexión" 
    message="No se pudo conectar con el servidor." 
    type="error" 
    on_close="window.location.reload()" 
%}
```

### Oculto Inicialmente
```html
{% include 'components/error_alert.html' with 
    title="Mensaje Importante" 
    message="Este mensaje se mostrará cuando sea necesario." 
    type="info" 
    show=false 
%}
```

## 🎯 Uso con Alpine.js

### Control Dinámico
```html
<div x-data="errorController()">
    <!-- Botón para mostrar error -->
    <button @click="showError()" class="bg-red-500 text-white px-4 py-2 rounded">
        Mostrar Error
    </button>
    
    <!-- Componente de error -->
    <div x-show="error.show">
        {% include 'components/error_alert.html' with 
            title="Error Dinámico" 
            message="Este error se muestra dinámicamente." 
            type="error" 
        %}
    </div>
</div>

<script>
document.addEventListener('alpine:init', () => {
    Alpine.data('errorController', () => ({
        error: { show: false },
        
        showError() {
            this.error.show = true;
        }
    }));
});
</script>
```

### Con Eventos
```html
<div x-data="errorHandler()" @error-alert-closed="handleErrorClosed">
    {% include 'components/error_alert.html' with 
        title="Error con Eventos" 
        message="Este error emite eventos al cerrarse." 
        type="error" 
    %}
</div>

<script>
document.addEventListener('alpine:init', () => {
    Alpine.data('errorHandler', () => ({
        handleErrorClosed(event) {
            console.log('Error cerrado:', event.detail);
            // Lógica adicional aquí
        }
    }));
});
</script>
```

## 📱 Responsive Design

El componente es completamente responsive y se adapta a:
- **Desktop**: Ancho máximo de 448px (max-w-md)
- **Tablet**: Padding reducido
- **Mobile**: Ancho completo con márgenes laterales

## 🎨 Personalización CSS

### Variables CSS Disponibles
```css
:root {
    --error-alert-border-radius: 0.5rem;
    --error-alert-padding: 1.5rem;
    --error-alert-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}
```

### Clases CSS Personalizables
- `.error-alert-container` - Contenedor principal
- `.error-alert-title` - Título de la alerta
- `.error-alert-message` - Mensaje de la alerta
- `.error-alert-close-btn` - Botón de cerrar

## 🔍 Eventos Emitidos

### `error-alert-closed`
Se emite cuando la alerta se cierra.

```javascript
// Escuchar evento
document.addEventListener('error-alert-closed', (event) => {
    console.log('Alerta cerrada:', event.detail);
    // event.detail contiene: { type, title, message }
});
```

## 🧪 Ejemplos de Integración

### En Formularios
```html
<form x-data="packageForm()" @submit.prevent="submitForm()">
    <input type="text" x-model="guideNumber" placeholder="Número de guía">
    <button type="submit">Anunciar</button>
    
    <!-- Error de validación -->
    <div x-show="error.show">
        {% include 'components/error_alert.html' with 
            title="Error de Validación" 
            message="El número de guía es requerido." 
            type="error" 
        %}
    </div>
</form>
```

### En Páginas de Error
```html
<!-- 404 Error -->
{% include 'components/error_alert.html' with 
    title="Página No Encontrada" 
    message="La página que buscas no existe." 
    type="error" 
    button_text="Volver al Inicio" 
%}
```

### En Notificaciones del Sistema
```html
<!-- Mantenimiento programado -->
{% include 'components/error_alert.html' with 
    title="Mantenimiento Programado" 
    message="El sistema estará en mantenimiento de 2:00 AM a 4:00 AM." 
    type="info" 
    auto_close=true 
    close_delay=10000 
%}
```

## ⚡ Rendimiento

- **Tamaño**: ~2KB (HTML + CSS + JS)
- **Dependencias**: Alpine.js (ya incluido en el proyecto)
- **Carga**: Lazy loading compatible
- **Memoria**: Mínimo uso de memoria

## 🐛 Solución de Problemas

### La alerta no se muestra
1. Verificar que Alpine.js esté cargado
2. Comprobar que `show=true`
3. Revisar la consola para errores JavaScript

### Los estilos no se aplican
1. Verificar que Tailwind CSS esté cargado
2. Comprobar que no hay conflictos de CSS
3. Revisar la especificidad de los estilos

### El auto-cerrar no funciona
1. Verificar que `auto_close=true`
2. Comprobar que `close_delay` es un número válido
3. Revisar que no hay errores en el callback `on_close`

## 📞 Soporte

Para problemas o mejoras, contactar al equipo de desarrollo de PAQUETES EL CLUB v1.0.
