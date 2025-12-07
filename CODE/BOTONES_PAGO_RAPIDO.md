# Botones de Pago Rápido - Modal "Entregar Paquete"

## Descripción
Se agregaron botones de valores predefinidos en la sección "CONFIRMACIÓN DE PAGO" del modal "Entregar Paquete" para facilitar la entrada rápida de montos comunes.

## Valores Predefinidos
Los botones incluyen los siguientes valores:
- **$0** - Para entregas sin costo
- **$1500** - Valor común
- **$2000** - Valor común
- **$2500** - Valor común
- **$3000** - Valor común
- **Otro** - Limpia el campo para ingresar un valor personalizado

## Características

### 1. Diseño Compacto
Los botones están diseñados para ser pequeños y compactos, dispuestos en una sola línea horizontal con wrap automático:
```
Layout: flex flex-wrap (se ajusta automáticamente al ancho disponible)
Tamaño: Botones pequeños (px-2.5 py-1.5, text-xs)
Espaciado: gap-1.5 (mínimo espacio entre botones)
Etiqueta: text-xs (texto pequeño)
```

### 2. Feedback Visual
- **Al seleccionar un valor**: 
  - El botón se resalta en azul
  - El campo de entrada muestra un anillo azul temporal
  - El cursor se enfoca en el campo de entrada

- **Al seleccionar "Otro"**:
  - Todos los botones vuelven a su estado normal
  - El campo se limpia
  - El campo muestra un anillo naranja temporal
  - El cursor se enfoca en el campo de entrada

### 3. Estados del Botón
- **Normal**: Fondo blanco, borde gris, texto gris
- **Hover**: Fondo azul claro, borde azul, texto azul
- **Seleccionado**: Fondo azul, borde azul oscuro, texto blanco
- **Activo**: Escala reducida (efecto de presión)

## Implementación

### HTML (línea ~354-385) - Diseño Compacto
```html
<!-- Botones de valores predefinidos - Compactos -->
<div class="mb-3">
    <label class="block text-xs font-medium text-gray-600 mb-1.5">
        Valores rápidos
    </label>
    <div class="flex flex-wrap gap-1.5">
        <button type="button" onclick="setPaymentAmount(0)" 
                class="payment-quick-btn px-2.5 py-1.5 border border-gray-300 rounded text-xs font-medium text-gray-700 bg-white hover:bg-blue-50 hover:border-blue-500 hover:text-blue-700 transition-all duration-150 active:scale-95">
            $0
        </button>
        <!-- ... más botones ... -->
        <button type="button" onclick="clearPaymentAmount()" 
                class="payment-quick-btn px-2.5 py-1.5 border border-gray-300 rounded text-xs font-medium text-gray-700 bg-white hover:bg-orange-50 hover:border-orange-500 hover:text-orange-700 transition-all duration-150 active:scale-95">
            Otro
        </button>
    </div>
</div>
```

### JavaScript (línea ~1912-1975)

#### Función: `setPaymentAmount(amount)`
Establece un valor predefinido en el campo de pago.

**Parámetros:**
- `amount` (number): El monto a establecer

**Comportamiento:**
1. Establece el valor en el campo de entrada (con 2 decimales)
2. Resalta el botón seleccionado
3. Enfoca el campo de entrada
4. Muestra feedback visual temporal (anillo azul)

```javascript
function setPaymentAmount(amount) {
    const paymentAmountInput = document.getElementById('paymentAmount');
    if (paymentAmountInput) {
        paymentAmountInput.value = amount.toFixed(2);
        highlightSelectedPaymentButton(amount);
        paymentAmountInput.focus();
        paymentAmountInput.classList.add('ring-2', 'ring-blue-500');
        setTimeout(() => {
            paymentAmountInput.classList.remove('ring-2', 'ring-blue-500');
        }, 500);
    }
}
```

#### Función: `clearPaymentAmount()`
Limpia el campo de pago para ingresar un valor personalizado.

**Comportamiento:**
1. Limpia el valor del campo de entrada
2. Remueve el resaltado de todos los botones
3. Enfoca el campo de entrada
4. Muestra feedback visual temporal (anillo naranja)

```javascript
function clearPaymentAmount() {
    const paymentAmountInput = document.getElementById('paymentAmount');
    if (paymentAmountInput) {
        paymentAmountInput.value = '';
        paymentAmountInput.focus();
        highlightSelectedPaymentButton(null);
        paymentAmountInput.classList.add('ring-2', 'ring-orange-500');
        setTimeout(() => {
            paymentAmountInput.classList.remove('ring-2', 'ring-orange-500');
        }, 500);
    }
}
```

#### Función: `highlightSelectedPaymentButton(amount)`
Resalta visualmente el botón de pago seleccionado.

**Parámetros:**
- `amount` (number|null): El monto del botón a resaltar, o null para limpiar

**Comportamiento:**
1. Remueve el resaltado de todos los botones
2. Si `amount` no es null, busca y resalta el botón correspondiente
3. Cambia los estilos del botón seleccionado (azul sólido)

```javascript
function highlightSelectedPaymentButton(amount) {
    const buttons = document.querySelectorAll('.payment-quick-btn');
    buttons.forEach(btn => {
        btn.classList.remove('bg-blue-500', 'text-white', 'border-blue-600');
        btn.classList.add('bg-white', 'text-gray-700', 'border-gray-300');
    });
    
    if (amount !== null) {
        const selectedBtn = Array.from(buttons).find(btn => {
            const btnText = btn.textContent.trim().replace('$', '');
            return parseFloat(btnText) === amount;
        });
        
        if (selectedBtn) {
            selectedBtn.classList.remove('bg-white', 'text-gray-700', 'border-gray-300');
            selectedBtn.classList.add('bg-blue-500', 'text-white', 'border-blue-600');
        }
    }
}
```

## Flujo de Usuario

### Escenario 1: Seleccionar un valor predefinido
1. Usuario abre el modal "Entregar Paquete"
2. El campo "Total" está **vacío** (sin valor por defecto)
3. Ve los botones compactos de valores rápidos en una línea
4. Hace clic en un botón (ej: $2000)
5. El botón se resalta en azul
6. El campo de entrada muestra "2000.00"
7. El campo se enfoca con un anillo azul temporal
8. Usuario puede confirmar o ajustar el valor manualmente

### Escenario 2: Ingresar un valor personalizado
1. Usuario abre el modal "Entregar Paquete"
2. El campo "Total" está **vacío** (sin valor por defecto)
3. Ve los botones compactos de valores rápidos
4. Hace clic en "Otro" o directamente en el campo
5. El campo se enfoca con un anillo naranja temporal (si usa "Otro")
6. Usuario ingresa el valor deseado manualmente

### Escenario 3: Cambiar de valor predefinido
1. Usuario selecciona $1500 (botón se resalta)
2. Usuario cambia de opinión y selecciona $2500
3. El botón $1500 vuelve a su estado normal
4. El botón $2500 se resalta
5. El campo muestra "2500.00"

## Beneficios

1. **Velocidad**: Entrada rápida de valores comunes con un solo clic
2. **Precisión**: Reduce errores de digitación
3. **UX Móvil**: Especialmente útil en dispositivos móviles donde escribir es más difícil
4. **Flexibilidad**: Mantiene la opción de ingresar valores personalizados
5. **Feedback Visual**: El usuario siempre sabe qué valor está seleccionado
6. **Soporte para $0**: Permite entregas sin costo (importante para el negocio)

## Consideraciones Especiales

### Valor Cero ($0)
El sistema permite ingresar valor cero (0) para casos especiales como:
- Entregas gratuitas
- Promociones
- Correcciones administrativas

### Validación
El campo de entrada mantiene sus validaciones originales:
- `type="number"` - Solo acepta números
- `step="0.01"` - Permite decimales
- `min="0"` - No permite valores negativos
- `required` - Campo obligatorio

## Pruebas Recomendadas

1. ✅ Hacer clic en cada botón de valor predefinido
2. ✅ Verificar que el campo se actualice correctamente
3. ✅ Verificar el resaltado visual del botón seleccionado
4. ✅ Hacer clic en "Otro" y verificar que el campo se limpie
5. ✅ Cambiar entre diferentes valores predefinidos
6. ✅ Ingresar un valor personalizado después de seleccionar un predefinido
7. ✅ Verificar el comportamiento en móvil (3 columnas)
8. ✅ Verificar el comportamiento en desktop (6 columnas)
9. ✅ Confirmar que el valor $0 funciona correctamente
10. ✅ Verificar que la entrega se procese con el valor seleccionado

## Fecha de Implementación
7 de diciembre de 2025
