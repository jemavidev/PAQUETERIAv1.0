# Implementación de Botón de WhatsApp en Anuncio Rápido

**Fecha**: 2025-12-13  
**Versión**: 1.0.0  
**Estado**: ✅ COMPLETADO

## Resumen

Se ha implementado un botón opcional de WhatsApp en la vista de anuncio rápido (`/announce-papyrus`) que permite contactar al cliente antes de anunciar el paquete.

## Funcionalidad

### Comportamiento

1. **Búsqueda de Cliente**: Cuando el usuario ingresa un número de teléfono (mínimo 10 dígitos), el sistema busca automáticamente al cliente.

2. **Aparición del Botón**: El botón de WhatsApp aparece automáticamente después de buscar el cliente, independientemente de si:
   - ✅ El cliente existe en el sistema
   - ✅ El cliente es nuevo (no existe)

3. **Mensaje Predefinido**: Al hacer clic en el botón, se abre WhatsApp con el siguiente mensaje:

```
¡Buen dia veci!

Le saludamos desde la papelería Papyrus.

Un domiciliario está aquí en nuestras instalaciones con un paquete a su nombre.

¿Nos autoriza recibirlo por usted?
```

4. **Opcional**: El botón es completamente opcional. El usuario puede:
   - Contactar al cliente por WhatsApp antes de anunciar
   - Ignorar el botón y proceder directamente a anunciar el paquete

## Cambios Realizados

### Archivo: `CODE/src/templates/announce/announce_quick.html`

#### 1. Nuevo Elemento HTML (después del campo de nombre)

```html
{# Botón de WhatsApp (opcional) #}
<div id="whatsappButtonContainer" class="hidden">
    <a id="whatsappButton" 
       href="#" 
       target="_blank"
       class="flex items-center justify-center w-full px-4 py-3 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors shadow-sm">
        <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
            <!-- Icono de WhatsApp -->
        </svg>
        <span>Contactar por WhatsApp</span>
    </a>
    <p class="text-xs text-gray-500 text-center mt-2">
        Opcional: Contacta al cliente antes de anunciar el paquete
    </p>
</div>
```

#### 2. Función JavaScript: `setupWhatsAppButton(phone)`

Nueva función que configura el enlace de WhatsApp:

```javascript
function setupWhatsAppButton(phone) {
    const whatsappButton = document.getElementById('whatsappButton');
    
    // Limpiar el teléfono (solo números)
    const cleanPhone = phone.replace(/\D/g, '');
    
    // Asegurar que tenga el código de país (57 para Colombia)
    let whatsappPhone = cleanPhone;
    if (!whatsappPhone.startsWith('57')) {
        whatsappPhone = '57' + whatsappPhone;
    }
    
    // Mensaje predefinido
    const message = '¡Buen dia veci!\n\n' +
                   'Le saludamos desde la papelería Papyrus.\n\n' +
                   'Un domiciliario está aquí en nuestras instalaciones con un paquete a su nombre.\n\n' +
                   '¿Nos autoriza recibirlo por usted?';
    
    // Crear URL de WhatsApp
    const whatsappUrl = `https://wa.me/${whatsappPhone}?text=${encodeURIComponent(message)}`;
    
    whatsappButton.href = whatsappUrl;
}
```

#### 3. Actualización de `searchCustomerByPhone(phone)`

Modificada para mostrar el botón de WhatsApp:

```javascript
// Cliente existente
setupWhatsAppButton(normalizedPhone);
whatsappButtonContainer.classList.remove('hidden');

// Cliente nuevo
setupWhatsAppButton(normalizedPhone);
whatsappButtonContainer.classList.remove('hidden');
```

#### 4. Actualización de Event Listeners

- Ocultar botón cuando el teléfono es muy corto
- Ocultar botón al limpiar el formulario después de anunciar

## Flujo de Usuario

### Escenario 1: Cliente Existente

1. Usuario ingresa teléfono: `3001234567`
2. Sistema busca y encuentra al cliente
3. ✅ Muestra nombre del cliente (solo lectura)
4. ✅ Muestra botón de WhatsApp
5. Usuario puede:
   - **Opción A**: Hacer clic en WhatsApp → Se abre chat con mensaje predefinido
   - **Opción B**: Ignorar WhatsApp → Hacer clic en "Anunciar Paquete"

### Escenario 2: Cliente Nuevo

1. Usuario ingresa teléfono: `3009876543`
2. Sistema no encuentra al cliente
3. ✅ Muestra campo de nombre (editable)
4. ✅ Muestra botón de WhatsApp
5. Usuario ingresa nombre del cliente
6. Usuario puede:
   - **Opción A**: Hacer clic en WhatsApp → Se abre chat con mensaje predefinido
   - **Opción B**: Ignorar WhatsApp → Hacer clic en "Anunciar Paquete"

## Características Técnicas

### Normalización de Teléfono

- Limpia caracteres no numéricos
- Agrega código de país (57) si no está presente
- Formato final: `57XXXXXXXXXX`

### URL de WhatsApp

Formato: `https://wa.me/57XXXXXXXXXX?text=MENSAJE_CODIFICADO`

Ejemplo:
```
https://wa.me/573001234567?text=%C2%A1Buen%20dia%20veci!%0A%0ALe%20saludamos...
```

### Diseño Responsive

- ✅ Botón verde con icono de WhatsApp
- ✅ Hover effect (verde más oscuro)
- ✅ Texto descriptivo debajo del botón
- ✅ Se adapta a móviles y escritorio

## Personalización

### Cambiar el Mensaje

Para modificar el mensaje de WhatsApp, editar la función `setupWhatsAppButton` en `announce_quick.html`:

```javascript
const message = 'TU MENSAJE AQUÍ\n\n' +
               'Segunda línea\n\n' +
               'Tercera línea';
```

**Nota**: Usar `\n\n` para saltos de línea en WhatsApp.

### Cambiar el Estilo del Botón

Modificar las clases CSS en el elemento `<a id="whatsappButton">`:

```html
<!-- Verde actual -->
class="... bg-green-500 hover:bg-green-600 ..."

<!-- Ejemplo: Azul -->
class="... bg-blue-500 hover:bg-blue-600 ..."
```

### Ocultar el Botón Permanentemente

Si deseas deshabilitar el botón, comentar estas líneas en `searchCustomerByPhone`:

```javascript
// setupWhatsAppButton(normalizedPhone);
// whatsappButtonContainer.classList.remove('hidden');
```

## Pruebas

### Prueba 1: Cliente Existente
1. Ir a: https://staging.jemavi.co/announce-papyrus
2. Ingresar teléfono de cliente existente
3. Verificar que aparece el botón de WhatsApp
4. Hacer clic en el botón
5. Verificar que se abre WhatsApp con el mensaje correcto

### Prueba 2: Cliente Nuevo
1. Ir a: https://staging.jemavi.co/announce-papyrus
2. Ingresar teléfono nuevo (no registrado)
3. Verificar que aparece el botón de WhatsApp
4. Ingresar nombre del cliente
5. Hacer clic en el botón de WhatsApp
6. Verificar que se abre WhatsApp con el mensaje correcto

### Prueba 3: Flujo Completo sin WhatsApp
1. Ingresar teléfono
2. Ignorar botón de WhatsApp
3. Hacer clic en "Anunciar Paquete"
4. Verificar que el anuncio se crea correctamente

### Prueba 4: Limpieza de Formulario
1. Ingresar teléfono (aparece botón de WhatsApp)
2. Anunciar paquete
3. Verificar que el botón de WhatsApp desaparece después del anuncio

## Compatibilidad

### Navegadores
- ✅ Chrome/Edge (Desktop y Mobile)
- ✅ Firefox (Desktop y Mobile)
- ✅ Safari (Desktop y Mobile)

### Dispositivos
- ✅ Desktop: Abre WhatsApp Web
- ✅ Mobile: Abre app de WhatsApp
- ✅ Tablet: Abre WhatsApp según configuración

## Notas Importantes

1. **No Afecta el Flujo Principal**: El botón es completamente opcional y no interfiere con el proceso de anuncio de paquetes.

2. **Funciona para Todos**: El botón aparece tanto para clientes existentes como nuevos.

3. **Mensaje Personalizable**: El mensaje puede ser modificado fácilmente en el código.

4. **Código de País**: El sistema agrega automáticamente el código de Colombia (57) si no está presente.

5. **Apertura en Nueva Pestaña**: El enlace se abre en una nueva pestaña/ventana (`target="_blank"`).

## Archivos Modificados

```
CODE/
└── src/
    └── templates/
        └── announce/
            └── announce_quick.html    [MODIFICADO]
```

## Despliegue

Los cambios están listos para ser desplegados:

```bash
git add CODE/src/templates/announce/announce_quick.html
git commit -m "feat: Agregar botón opcional de WhatsApp en anuncio rápido"
git push
```

No requiere reinicio de servicios, solo actualizar el template.

---

**Estado Final**: ✅ IMPLEMENTACIÓN COMPLETADA Y LISTA PARA PRODUCCIÓN
