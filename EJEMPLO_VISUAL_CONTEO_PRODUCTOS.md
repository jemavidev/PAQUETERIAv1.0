# Ejemplo Visual - Conteo de Productos en Estado

## Vista del Tab FACTURAS

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ FACTURAS                                                    Mostrando 1-10 de 45     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ ☐  CUFE          Proveedor              Número      Fecha       Total      Estado   │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ ☐  8cf8ec536...  DISTRIBUIDORA XYZ     FV-001234   2026-01-15  $1,250,000  🟢 15 prod. │
│ ☐  b95d05e6f...  COMERCIAL ABC S.A.S   FV-005678   2026-01-14  $850,000    🟢 8 prod.  │
│ ☐  dce84f5f4...  PROVEEDOR LTDA        FV-009012   2026-01-13  $2,100,000  🟢 23 prod. │
│ ☐  TEMP_12345... IMPORTADORA DEL SUR   -           -           -           🟡          │
│ ☐  fc5ffaf46...  SUMINISTROS NORTE     FV-003456   2026-01-12  $450,000    🟢 5 prod.  │
│ ☐  a63954bad...  MAYORISTA CENTRAL     -           -           -           🟡          │
│ ☐  8d4f3b4bb...  DISTRIBUCIONES S.A.   FV-007890   2026-01-11  $1,750,000  🟢 18 prod. │
│ ☐  752c9406b...  COMERCIO INTEGRAL     FV-002345   2026-01-10  $920,000    🟢 12 prod. │
│ ☐  703f6357a...  PROVEEDOR ERROR       -           -           -           🔴          │
│ ☐  6840c2056...  SUMINISTROS OESTE     FV-006789   2026-01-09  $1,350,000  🟢 9 prod.  │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## Vista del Tab CUFE

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ CUFE                                                        Mostrando 1-10 de 38     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ ☐  CUFE          Proveedor              Número      Fecha       Total      Estado   │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ ☐  8cf8ec536...  DISTRIBUIDORA XYZ     FV-001234   2026-01-15  $1,250,000  🟢 15 prod. │
│ ☐  b95d05e6f...  COMERCIAL ABC S.A.S   FV-005678   2026-01-14  $850,000    🟢 8 prod.  │
│ ☐  dce84f5f4...  PROVEEDOR LTDA        FV-009012   2026-01-13  $2,100,000  🟢 23 prod. │
│ ☐  fc5ffaf46...  SUMINISTROS NORTE     FV-003456   2026-01-12  $450,000    🟢 5 prod.  │
│ ☐  8d4f3b4bb...  DISTRIBUCIONES S.A.   FV-007890   2026-01-11  $1,750,000  🟢 18 prod. │
│ ☐  752c9406b...  COMERCIO INTEGRAL     FV-002345   2026-01-10  $920,000    🟢 12 prod. │
│ ☐  6840c2056...  SUMINISTROS OESTE     FV-006789   2026-01-09  $1,350,000  🟢 9 prod.  │
│ ☐  34d3ec883...  MAYORISTA SUR         FV-004567   2026-01-08  $680,000    🟢 7 prod.  │
│ ☐  11923ccd0...  IMPORTADORA NORTE     FV-008901   2026-01-07  $1,950,000  🟢 21 prod. │
│ ☐  03391745b...  COMERCIAL ESTE        FV-001122   2026-01-06  $1,120,000  🟢 14 prod. │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## Detalle de Estados

### Estado: Completo (con productos)
```
┌──────────────────────────────────────┐
│ Estado                               │
├──────────────────────────────────────┤
│ 🟢 15 prod.                          │
│                                      │
│ Tooltip: "Completo - 15 productos"   │
└──────────────────────────────────────┘
```

### Estado: Validado (con productos)
```
┌──────────────────────────────────────┐
│ Estado                               │
├──────────────────────────────────────┤
│ 🟢 8 prod.                           │
│                                      │
│ Tooltip: "Validado - 8 productos"    │
└──────────────────────────────────────┘
```

### Estado: Pendiente DIAN (sin conteo)
```
┌──────────────────────────────────────┐
│ Estado                               │
├──────────────────────────────────────┤
│ 🟡                                   │
│                                      │
│ Tooltip: "Pendiente DIAN"            │
└──────────────────────────────────────┘
```

### Estado: Error (sin conteo)
```
┌──────────────────────────────────────┐
│ Estado                               │
├──────────────────────────────────────┤
│ 🔴                                   │
│                                      │
│ Tooltip: "Error"                     │
└──────────────────────────────────────┘
```

## Casos de Uso

### Caso 1: Factura Completa con Productos
```
Factura: FV-001234
Estado: Completo
Productos extraídos del DIAN: 15 items
Visualización: 🟢 15 prod.
```

### Caso 2: Factura Completa sin Productos (posible error)
```
Factura: FV-005678
Estado: Completo
Productos extraídos del DIAN: 0 items
Visualización: 🟢 0 prod.
⚠️ Esto podría indicar un error en la extracción
```

### Caso 3: Factura Pendiente DIAN
```
Factura: FV-009012
Estado: Pendiente DIAN
Productos: No disponibles aún
Visualización: 🟡
```

### Caso 4: Factura con CUFE Temporal
```
Factura: TEMP_12345...
Estado: Sin CUFE
Productos: No disponibles
Visualización: 🟠
```

## Beneficios Visuales

### ✅ Identificación Rápida
- **Un vistazo**: Ver cuántos productos tiene cada factura
- **Sin clicks**: No necesitas abrir detalles para ver el conteo
- **Comparación**: Fácil comparar facturas por cantidad de productos

### ✅ Validación Visual
- **Facturas completas**: Verde con número = procesada correctamente
- **Facturas pendientes**: Amarillo sin número = esperando DIAN
- **Facturas con error**: Rojo sin número = revisar

### ✅ Trazabilidad
- **Historial**: Ver evolución de productos por proveedor
- **Anomalías**: Detectar facturas con 0 productos
- **Estadísticas**: Calcular promedios mentalmente

## Responsive Design

### Desktop (pantalla grande)
```
🟢 15 prod.  ← Círculo + texto completo
```

### Tablet (pantalla mediana)
```
🟢 15 prod.  ← Círculo + texto completo
```

### Mobile (pantalla pequeña)
```
🟢 15  ← Círculo + solo número (sin "prod.")
```

## Colores y Estilos

### Círculo de Estado
- **Verde** 🟢: Completo/Validado
- **Amarillo** 🟡: Pendiente DIAN
- **Rojo** 🔴: Error
- **Gris** ⚫: Sin DIAN
- **Naranja** 🟠: Sin CUFE

### Texto del Conteo
- **Color**: `text-gray-700` (gris oscuro)
- **Tamaño**: `text-xs` (pequeño)
- **Peso**: `font-medium` (medio)
- **Formato**: "X prod." donde X es el número

### Espaciado
- **Gap**: `gap-1.5` entre círculo y texto
- **Alineación**: `inline-flex items-center` (centrado vertical)

## Interacción

### Hover sobre Estado
```
┌──────────────────────────────────────┐
│ 🟢 15 prod.                          │
│                                      │
│ [Tooltip aparece]                    │
│ "Completo - 15 productos"            │
└──────────────────────────────────────┘
```

### Click en Fila
```
→ Abre modal de detalles
→ Muestra lista completa de productos
→ Permite ver descripción, cantidad, precio de cada producto
```

## Ejemplo Real con Datos

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ FACTURAS - DISTRIBUIDORA XYZ                                                        │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│ CUFE: 8cf8ec5366fa9eaccea38cdffdfa0a7690edbaf31b89adce444ca0a322d19e50...        │
│ Proveedor: DISTRIBUIDORA XYZ S.A.S                                                  │
│ NIT: 900.123.456-7                                                                  │
│ Número: FV-001234                                                                   │
│ Fecha: 2026-01-15                                                                   │
│ Total: $1,250,000                                                                   │
│ Estado: 🟢 15 prod.                                                                 │
│                                                                                     │
│ PRODUCTOS (15 items):                                                               │
│ ┌─────────────────────────────────────────────────────────────────────────────┐   │
│ │ 1. ARROZ DIANA X 500G              Cant: 50    Precio: $2,500   Total: $125,000 │
│ │ 2. ACEITE GIRASOL X 1L             Cant: 30    Precio: $8,500   Total: $255,000 │
│ │ 3. AZÚCAR REFINADA X 1KG           Cant: 40    Precio: $3,200   Total: $128,000 │
│ │ 4. CAFÉ MOLIDO X 250G              Cant: 25    Precio: $12,000  Total: $300,000 │
│ │ 5. LECHE ENTERA X 1L               Cant: 60    Precio: $4,500   Total: $270,000 │
│ │ ... (10 productos más)                                                           │
│ └─────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

**Nota**: Los emojis de círculos (🟢🟡🔴) son representaciones visuales. En la interfaz real se usan elementos HTML con clases CSS para los colores.
