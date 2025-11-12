# 🚨 Sistema de Alertas Unificado - PAQUETES EL CLUB v4.0

## 📋 Descripción General

El Sistema de Alertas Unificado es una solución completa para manejar todos los mensajes de error, advertencia, información y éxito en la aplicación PAQUETES EL CLUB v4.0. Reemplaza todos los `alert()` nativos del navegador con un sistema moderno, responsive y consistente.

## 🎯 Características Principales

- **Unificado**: Un solo sistema para todos los tipos de mensajes
- **Responsive**: Optimizado para móviles (80% prioridad)
- **Consistente**: Diseño uniforme en toda la aplicación
- **Accesible**: Cumple estándares WCAG 2.1 AA
- **Personalizable**: Múltiples opciones de configuración
- **Integrado**: Funciona con Alpine.js y Tailwind CSS

## 🏗️ Arquitectura del Sistema

### Componentes Principales

1. **`error_alert.html`** - Componente base de alertas
2. **`error_alert_helper.html`** - Helper para mensajes flash
3. **`form-validation.js`** - Sistema de validación de formularios
4. **`flash_messages.py`** - Utilidades del backend
5. **Funciones JavaScript globales** - API para mostrar alertas

### Flujo de Datos

```
Backend (Python) → flash_messages.py → Template Context → error_alert_helper.html → error_alert.html
Frontend (JS) → showAlert() → error_alert.html (dinámico)
Formularios → form-validation.js → showValidationErrors() → error_alert.html
```

## 🚀 Uso Básico

### 1. Alertas Simples

```javascript
// Error
showError('Error del Sistema', 'Ha ocurrido un error inesperado');

// Advertencia
showWarning('Advertencia', 'El paquete ya fue anunciado');

// Información
showInfo('Información', 'El sistema se reiniciará en 5 minutos');

// Éxito
showSuccess('Éxito', 'El paquete se anunció correctamente');
```

### 2. Alertas Avanzadas

```javascript
// Con opciones personalizadas
showAlert('Título', 'Mensaje', 'error', {
    autoClose: true,
    closeDelay: 5000,
    buttonText: 'Cerrar',
    onClose: 'console.log("Alerta cerrada")'
});
```

### 3. Errores de Validación

```javascript
// Errores de formulario
const errors = {
    'email': ['El email es requerido', 'El email no es válido'],
    'password': ['La contraseña debe tener al menos 8 caracteres']
};
showValidationErrors(errors);
```

## 📱 Responsive Design

### Breakpoints
- **Mobile**: 320px - 767px (80% prioridad)
- **Tablet**: 768px - 1023px
- **Desktop**: 1024px+

### Características Móviles
- Touch targets mínimo 44px
- Ancho completo en móviles
- Posicionamiento fijo en esquina superior derecha
- Animaciones suaves y rápidas

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

## 🔧 Configuración Avanzada

### Parámetros del Componente

| Parámetro | Tipo | Valor por Defecto | Descripción |
|-----------|------|-------------------|-------------|
| `title` | string | "Error del Sistema" | Título del mensaje |
| `message` | string | "Error del sistema..." | Descripción del error |
| `type` | string | "error" | Tipo: `error`, `warning`, `info`, `success` |
| `show` | boolean | `true` | Si mostrar la alerta inicialmente |
| `auto_close` | boolean | `false` | Si cerrar automáticamente |
| `close_delay` | number | `5000` | Tiempo en ms antes de auto-cerrar |
| `button_text` | string | "Cerrar" | Texto del botón de cerrar |
| `on_close` | string | `""` | Código JavaScript a ejecutar al cerrar |

### Opciones JavaScript

```javascript
const options = {
    autoClose: true,        // Cerrar automáticamente
    closeDelay: 3000,       // Tiempo en milisegundos
    buttonText: 'Cerrar',   // Texto del botón
    onClose: 'reload()'     // Código a ejecutar al cerrar
};
```

## 📝 Validación de Formularios

### Auto-validación

```html
<form id="myForm" data-validation="true" data-validate-on-change="true">
    <input type="email" name="email" required minlength="5">
    <input type="password" name="password" required minlength="8">
    <button type="submit">Enviar</button>
</form>
```

### Validación Manual

```javascript
const validator = new FormValidator('myForm', {
    validateOnSubmit: true,
    validateOnChange: true,
    showErrors: true,
    showSuccess: true,
    onSuccess: function(formData) {
        showSuccessMessage('Formulario enviado correctamente');
    },
    onError: function(errors) {
        showValidationErrors(errors);
    }
});
```

### Validadores Personalizados

```javascript
// Validar número de guía
const error = CustomValidators.trackingNumber('ABC123456');

// Validar teléfono colombiano
const error = CustomValidators.colombianPhone('+573001234567');

// Validar que dos campos coincidan
const error = CustomValidators.matchFields('password', 'confirmPassword');
```

## 🔄 Mensajes Flash del Backend

### Python (FastAPI)

```python
from app.utils.flash_messages import add_success_message, add_error_message

# En una ruta
@router.post("/api/packages")
async def create_package(request: Request):
    context = get_auth_context_from_request(request)
    
    try:
        # Lógica de creación
        add_success_message(context, "Paquete creado exitosamente")
    except Exception as e:
        add_error_message(context, f"Error al crear paquete: {str(e)}")
    
    return templates.TemplateResponse("packages/list.html", context)
```

### Template Helper

```html
<!-- En cualquier template -->
{% include 'components/error_alert_helper.html' %}
```

## 🎯 Uso con Alpine.js

### Control Dinámico

```html
<div x-data="errorController()">
    <button @click="showError()">Mostrar Error</button>
    
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
```

## 📊 Eventos Emitidos

### `error-alert-closed`

Se emite cuando una alerta se cierra.

```javascript
document.addEventListener('error-alert-closed', (event) => {
    console.log('Alerta cerrada:', event.detail);
    // event.detail contiene: { type, title, message }
});
```

## 🧪 Testing

### Página de Demo

Visita `/demo-error-system` para probar todas las funcionalidades:

- Alertas básicas (error, warning, info, success)
- Auto-cierre con diferentes tiempos
- Errores de validación
- Formularios con validación automática
- Alertas personalizadas

### Casos de Prueba

1. **Alertas Básicas**: Verificar que todos los tipos se muestren correctamente
2. **Auto-cierre**: Confirmar que se cierren en el tiempo especificado
3. **Validación**: Probar formularios con diferentes errores
4. **Responsive**: Verificar en diferentes tamaños de pantalla
5. **Accesibilidad**: Probar con lectores de pantalla

## 🔧 Personalización

### Variables CSS

```css
:root {
    --error-alert-border-radius: 0.5rem;
    --error-alert-padding: 1.5rem;
    --error-alert-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}
```

### Clases Personalizables

- `.error-alert-container` - Contenedor principal
- `.error-alert-title` - Título de la alerta
- `.error-alert-message` - Mensaje de la alerta
- `.error-alert-close-btn` - Botón de cerrar

## ⚡ Rendimiento

- **Tamaño**: ~3KB (HTML + CSS + JS)
- **Dependencias**: Alpine.js, Tailwind CSS
- **Carga**: Lazy loading compatible
- **Memoria**: Mínimo uso de memoria
- **Animaciones**: 60fps con CSS transitions

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

### La validación no funciona
1. Verificar que `form-validation.js` esté cargado
2. Comprobar que el formulario tiene `data-validation="true"`
3. Revisar que los campos tienen los atributos correctos

## 📞 Soporte

Para problemas o mejoras, contactar al equipo de desarrollo de PAQUETES EL CLUB v4.0.

---

**Sistema de Alertas Unificado v1.0.0** - PAQUETES EL CLUB v4.0
**Última actualización**: 2025-01-24
**Mantenido por**: Equipo de Desarrollo PAQUETES EL CLUB
