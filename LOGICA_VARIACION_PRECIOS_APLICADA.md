# LÓGICA DE VARIACIÓN DE PRECIOS APLICADA

## 📊 TEORÍA IMPLEMENTADA

Se aplica la lógica de comparación de precios entre compras para mostrar solo cambios significativos.

---

## 🎯 REGLAS DE NEGOCIO

### 1. Precio SUBIÓ (↑X%)
**Condición:** `variacion_precio > 0.5%`

```javascript
if (variacion > 0.5) {
    // Mostrar badge ROJO con flecha arriba
    Badge: [↑15.5%]
    Color: Rojo (bg-red-500)
    Tooltip: "Precio subió 15.5%"
}
```

**Ejemplo:**
- Precio anterior: $10,000
- Precio actual: $11,550
- Variación: +15.5%
- **Resultado:** Muestra badge `[↑15.5%]` en rojo

---

### 2. Precio BAJÓ (↓X%)
**Condición:** `variacion_precio < -0.5%`

```javascript
if (variacion < -0.5) {
    // Mostrar badge VERDE OSCURO con flecha abajo
    Badge: [↓8.2%]
    Color: Verde oscuro (bg-green-600)
    Tooltip: "Precio bajó 8.2%"
}
```

**Ejemplo:**
- Precio anterior: $10,000
- Precio actual: $9,180
- Variación: -8.2%
- **Resultado:** Muestra badge `[↓8.2%]` en verde oscuro

---

### 3. Precio IGUAL (Sin badge)
**Condición:** `-0.5% ≤ variacion_precio ≤ 0.5%`

```javascript
if (variacion >= -0.5 && variacion <= 0.5) {
    // NO mostrar badge
    // El precio se considera estable
}
```

**Ejemplo:**
- Precio anterior: $10,000
- Precio actual: $10,030
- Variación: +0.3%
- **Resultado:** NO muestra badge (cambio insignificante)

---

### 4. Primera Compra (1ª)
**Condición:** `variacion_tipo === 'primera_compra'`

```javascript
if (product.variacion_tipo === 'primera_compra') {
    // Mostrar badge MORADO
    Badge: [1ª]
    Color: Morado (bg-purple-500)
    Tooltip: "Primera compra de este producto"
}
```

**Ejemplo:**
- No hay compras anteriores del producto
- **Resultado:** Muestra badge `[1ª]` en morado

---

## 📐 UMBRAL DE VARIACIÓN

### ¿Por qué 0.5%?

El umbral de **0.5%** se eligió para:

1. **Filtrar ruido**: Variaciones menores a 0.5% son insignificantes
2. **Evitar saturación**: No mostrar badges para cambios mínimos
3. **Destacar lo importante**: Solo alertar sobre cambios reales

### Ejemplos de Umbral

```
Precio anterior: $10,000

Variación +0.3% → $10,030  ❌ NO muestra badge (igual)
Variación +0.5% → $10,050  ❌ NO muestra badge (límite)
Variación +0.6% → $10,060  ✅ Muestra [↑0.6%] (subió)
Variación +5.0% → $10,500  ✅ Muestra [↑5.0%] (subió)

Variación -0.3% → $9,970   ❌ NO muestra badge (igual)
Variación -0.5% → $9,950   ❌ NO muestra badge (límite)
Variación -0.6% → $9,940   ✅ Muestra [↓0.6%] (bajó)
Variación -5.0% → $9,500   ✅ Muestra [↓5.0%] (bajó)
```

---

## 🎨 RESULTADO VISUAL

### Caso 1: Precio Subió
```
┌────────────────────────────────────────────┐
│ LECHE ENTERA 1L                            │
│ Precio: $3,800                             │
│ Estado: [+] [↑15.5%]                       │
│         └─IVA └─Subió 15.5%                │
└────────────────────────────────────────────┘
```

### Caso 2: Precio Bajó
```
┌────────────────────────────────────────────┐
│ CAFÉ MOLIDO 500G                           │
│ Precio: $18,500                            │
│ Estado: [+] [↓8.2%]                        │
│         └─IVA └─Bajó 8.2%                  │
└────────────────────────────────────────────┘
```

### Caso 3: Precio Igual (Sin badge)
```
┌────────────────────────────────────────────┐
│ ARROZ PREMIUM 1KG                          │
│ Precio: $4,500                             │
│ Estado: [+]                                │
│         └─IVA (sin variación significativa)│
└────────────────────────────────────────────┘
```

### Caso 4: Primera Compra
```
┌────────────────────────────────────────────┐
│ QUINOA ORGÁNICA 1KG                        │
│ Precio: $25,000                            │
│ Estado: [+] [1ª]                           │
│         └─IVA └─Primera compra             │
└────────────────────────────────────────────┘
```

---

## 🔄 FLUJO DE DECISIÓN

```
┌─────────────────────────────────────────────┐
│ ¿Existe compra anterior del producto?      │
└─────────────────┬───────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
       SÍ                  NO
        │                   │
        ▼                   ▼
┌───────────────┐   ┌──────────────┐
│ Calcular      │   │ Mostrar      │
│ variación %   │   │ badge [1ª]   │
└───────┬───────┘   └──────────────┘
        │
        ▼
┌───────────────────────────────────┐
│ ¿Variación > 0.5%?                │
└───────┬───────────────────────────┘
        │
    ┌───┴───┐
    │       │
   SÍ      NO
    │       │
    ▼       ▼
┌────────┐ ┌──────────────────────┐
│ Mostrar│ │ ¿Variación < -0.5%?  │
│ [↑X%]  │ └──────┬───────────────┘
└────────┘        │
              ┌───┴───┐
              │       │
             SÍ      NO
              │       │
              ▼       ▼
          ┌────────┐ ┌──────────────┐
          │ Mostrar│ │ NO mostrar   │
          │ [↓X%]  │ │ badge        │
          └────────┘ │ (precio igual)│
                     └──────────────┘
```

---

## 💡 VENTAJAS DE ESTA LÓGICA

### 1. Claridad Visual
- ✅ Solo muestra información relevante
- ✅ No satura la interfaz con badges innecesarios
- ✅ Destaca cambios significativos

### 2. Toma de Decisiones
- ✅ Alerta inmediata sobre aumentos de precio
- ✅ Identifica oportunidades (precios que bajaron)
- ✅ Reconoce productos nuevos (primera compra)

### 3. Eficiencia
- ✅ Menos ruido visual
- ✅ Fácil de escanear la tabla
- ✅ Información accionable

---

## 📊 ESTADÍSTICAS ESPERADAS

En una tabla típica de 100 productos:

```
Distribución esperada de badges de variación:

[↑X%]  Precio subió:     ~15-20 productos (15-20%)
[↓X%]  Precio bajó:      ~10-15 productos (10-15%)
[1ª]   Primera compra:   ~5-10 productos  (5-10%)
(Sin)  Precio igual:     ~55-70 productos (55-70%)
```

**Resultado:** Solo 30-45% de productos muestran badge de variación, manteniendo la tabla limpia y enfocada.

---

## 🧪 CASOS DE PRUEBA

### Test 1: Variación Positiva Significativa
```javascript
Precio anterior: 10000
Precio actual: 11550
Variación: +15.5%
Esperado: Badge [↑15.5%] en rojo ✅
```

### Test 2: Variación Negativa Significativa
```javascript
Precio anterior: 10000
Precio actual: 9180
Variación: -8.2%
Esperado: Badge [↓8.2%] en verde oscuro ✅
```

### Test 3: Variación Insignificante Positiva
```javascript
Precio anterior: 10000
Precio actual: 10030
Variación: +0.3%
Esperado: Sin badge ✅
```

### Test 4: Variación Insignificante Negativa
```javascript
Precio anterior: 10000
Precio actual: 9970
Variación: -0.3%
Esperado: Sin badge ✅
```

### Test 5: Variación en el Límite
```javascript
Precio anterior: 10000
Precio actual: 10050
Variación: +0.5%
Esperado: Sin badge (límite no incluido) ✅
```

### Test 6: Primera Compra
```javascript
No hay compra anterior
variacion_tipo: 'primera_compra'
Esperado: Badge [1ª] en morado ✅
```

---

## ✅ IMPLEMENTACIÓN COMPLETADA

La lógica de variación de precios está completamente implementada y probada:

- ✅ Muestra badge solo cuando precio subió > 0.5%
- ✅ Muestra badge solo cuando precio bajó < -0.5%
- ✅ NO muestra badge cuando precio está igual (-0.5% a +0.5%)
- ✅ Muestra badge especial para primera compra
- ✅ Colores semánticos (rojo=alerta, verde=bueno, morado=info)
- ✅ Tooltips informativos con porcentaje exacto

**Estado:** LISTO PARA PRODUCCIÓN
