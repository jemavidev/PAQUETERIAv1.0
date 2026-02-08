# 📊 Diagrama de Flujo - Sistema de Trazabilidad

## 🔄 Flujo Principal: Carga de Factura DIAN

```
┌─────────────────────────────────────────────────────────────────┐
│                    USUARIO SUBE ARCHIVO DIAN                     │
│                     (Tab CUFE - Upload PDF)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              PDFParserService.parse_dian_document()              │
│                                                                  │
│  • Extrae texto del PDF                                         │
│  • Busca sección de productos                                   │
│  • Extrae: código, descripción, cantidad, precio, IVA, total   │
│  • Retorna lista de productos                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│          InvoiceV2Service.process_dian_document()                │
│                                                                  │
│  1. Actualiza datos de la factura                               │
│  2. Elimina productos anteriores (si existen)                   │
│  3. Para cada producto extraído:                                │
│     ├─ Llama a calculate_product_traceability()                 │
│     ├─ Crea InvoiceProductV2 con trazabilidad                   │
│     └─ Guarda en base de datos                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│      InvoiceV2Service.calculate_product_traceability()           │
│                                                                  │
│  INPUT:                                                          │
│    • codigo_producto: "ABC123"                                  │
│    • precio_actual: 12000                                       │
│    • fecha_actual: 2025-02-01                                   │
│    • proveedor_actual: "FERRETERÍA XYZ"                         │
│                                                                  │
│  PROCESO:                                                        │
│    1. Buscar compras anteriores del mismo código                │
│       SELECT * FROM invoice_products_v2                         │
│       WHERE codigo_producto = 'ABC123'                          │
│       AND fecha_compra < '2025-02-01'                           │
│       ORDER BY fecha_compra DESC                                │
│                                                                  │
│    2. Si NO hay compras anteriores:                             │
│       ├─ variacion_tipo = "primera_compra"                      │
│       ├─ precio_promedio = precio_actual                        │
│       ├─ precio_minimo = precio_actual                          │
│       ├─ precio_maximo = precio_actual                          │
│       └─ total_compras = 1                                      │
│                                                                  │
│    3. Si HAY compras anteriores:                                │
│       ├─ precio_anterior = ultima_compra.precio_unitario        │
│       ├─ variacion_precio = ((actual - anterior) / anterior)*100│
│       ├─ variacion_tipo = "subio" | "bajo" | "igual"           │
│       ├─ precio_promedio = AVG(todos los precios)              │
│       ├─ precio_minimo = MIN(todos los precios)                │
│       ├─ precio_maximo = MAX(todos los precios)                │
│       ├─ total_compras = COUNT(compras) + 1                    │
│       ├─ ultimo_proveedor = ultima_compra.proveedor            │
│       └─ dias_desde_ultima = fecha_actual - ultima_fecha       │
│                                                                  │
│  OUTPUT:                                                         │
│    {                                                             │
│      proveedor_nombre: "FERRETERÍA XYZ",                        │
│      precio_anterior: 10000,                                    │
│      variacion_precio: 20.0,                                    │
│      variacion_tipo: "subio",                                   │
│      precio_promedio: 11000,                                    │
│      precio_minimo_historico: 10000,                            │
│      precio_maximo_historico: 12000,                            │
│      total_compras_producto: 2,                                 │
│      ultimo_proveedor: "FERRETERÍA XYZ",                        │
│      dias_desde_ultima_compra: 17                               │
│    }                                                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  GUARDAR EN BASE DE DATOS                        │
│                                                                  │
│  INSERT INTO invoice_products_v2 (                              │
│    cufe, codigo_producto, descripcion,                          │
│    cantidad, precio_unitario, total_item,                       │
│    proveedor_nombre, precio_anterior,                           │
│    variacion_precio, variacion_tipo,                            │
│    precio_promedio, precio_minimo_historico,                    │
│    precio_maximo_historico, total_compras_producto,             │
│    ultimo_proveedor, dias_desde_ultima_compra                   │
│  ) VALUES (...)                                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    USUARIO VE EN TAB PRODUCTOS                   │
│                                                                  │
│  Tabla muestra:                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Código │ Descripción │ Precio │ Variación │ Compras │...│  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ ABC123 │ TORNILLO M8 │ $12,000│  ↑ 20.0% │   2x    │...│  │
│  │        │             │Prom:$11k│   (rojo) │ (azul)  │   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Click en ⏰ abre modal con:                                    │
│  • Estadísticas generales                                       │
│  • Historial completo de compras                                │
│  • Comparación entre proveedores                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎨 Flujo Visual: Badges de Variación

```
┌─────────────────────────────────────────────────────────────────┐
│                    CÁLCULO DE VARIACIÓN                          │
└─────────────────────────────────────────────────────────────────┘

Compra 1: $10,000
    ↓
    ├─ NO hay compras anteriores
    └─ Badge: ⚪ "Primera" (gris)

Compra 2: $12,000
    ↓
    ├─ Precio anterior: $10,000
    ├─ Variación: ($12,000 - $10,000) / $10,000 * 100 = +20%
    └─ Badge: 🔴 "↑ 20.0%" (rojo)

Compra 3: $9,500
    ↓
    ├─ Precio anterior: $12,000
    ├─ Variación: ($9,500 - $12,000) / $12,000 * 100 = -20.8%
    └─ Badge: 🟢 "↓ 20.8%" (verde)

Compra 4: $9,500
    ↓
    ├─ Precio anterior: $9,500
    ├─ Variación: ($9,500 - $9,500) / $9,500 * 100 = 0%
    └─ Badge: 🔵 "→ 0.0%" (azul)
```

---

## 📊 Flujo de Datos: Estadísticas

```
┌─────────────────────────────────────────────────────────────────┐
│              CÁLCULO DE ESTADÍSTICAS HISTÓRICAS                  │
└─────────────────────────────────────────────────────────────────┘

Historial de Compras:
  Compra 1: $10,000 (15/01/2025)
  Compra 2: $12,000 (01/02/2025)
  Compra 3: $9,500  (15/02/2025)
  Compra 4: $9,500  (28/02/2025)  ← ACTUAL

Cálculos:
  ┌─────────────────────────────────────────────────────────┐
  │ Precio Promedio                                         │
  │   = (10000 + 12000 + 9500 + 9500) / 4                  │
  │   = $10,250                                             │
  └─────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────┐
  │ Precio Mínimo                                           │
  │   = MIN(10000, 12000, 9500, 9500)                      │
  │   = $9,500                                              │
  └─────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────┐
  │ Precio Máximo                                           │
  │   = MAX(10000, 12000, 9500, 9500)                      │
  │   = $12,000                                             │
  └─────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────┐
  │ Total Compras                                           │
  │   = COUNT(compras anteriores) + 1                       │
  │   = 3 + 1 = 4                                           │
  └─────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────┐
  │ Días desde Última Compra                                │
  │   = fecha_actual - fecha_ultima_compra                  │
  │   = 28/02/2025 - 15/02/2025 = 13 días                  │
  └─────────────────────────────────────────────────────────┘
```

---

## 🗄️ Estructura de Base de Datos

```
┌─────────────────────────────────────────────────────────────────┐
│                    invoice_products_v2                           │
├─────────────────────────────────────────────────────────────────┤
│ id                          INTEGER PRIMARY KEY                  │
│ cufe                        VARCHAR(96) FK → invoices_v2         │
│ codigo_producto             VARCHAR(100) [INDEXED]               │
│ descripcion                 TEXT                                 │
│ cantidad                    NUMERIC(10,2)                        │
│ precio_unitario             NUMERIC(15,2)                        │
│ total_item                  NUMERIC(15,2)                        │
│ fecha_compra                DATE [INDEXED]                       │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │              CAMPOS DE TRAZABILIDAD                         │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ proveedor_nombre          VARCHAR(255) [INDEXED]            │ │
│ │ precio_anterior           NUMERIC(15,2)                     │ │
│ │ variacion_precio          NUMERIC(10,2)                     │ │
│ │ variacion_tipo            VARCHAR(20) [INDEXED]             │ │
│ │ precio_promedio           NUMERIC(15,2)                     │ │
│ │ precio_minimo_historico   NUMERIC(15,2)                     │ │
│ │ precio_maximo_historico   NUMERIC(15,2)                     │ │
│ │ total_compras_producto    INTEGER                           │ │
│ │ ultimo_proveedor          VARCHAR(255)                      │ │
│ │ dias_desde_ultima_compra  INTEGER                           │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ created_at                  TIMESTAMP                            │
└─────────────────────────────────────────────────────────────────┘

Índices:
  • idx_products_codigo_producto (codigo_producto)
  • idx_products_fecha_compra (fecha_compra)
  • idx_products_proveedor (proveedor_nombre)
  • idx_products_variacion_tipo (variacion_tipo)
  • idx_products_codigo_fecha (codigo_producto, fecha_compra)
```

---

## 🔍 Query de Ejemplo

```sql
-- Buscar compras anteriores para calcular trazabilidad
SELECT 
    codigo_producto,
    precio_unitario,
    fecha_compra,
    proveedor_nombre
FROM invoice_products_v2
WHERE codigo_producto = 'ABC123'
  AND fecha_compra < '2025-02-28'
ORDER BY fecha_compra DESC;

-- Resultado:
┌─────────────────┬─────────────────┬──────────────┬──────────────────┐
│ codigo_producto │ precio_unitario │ fecha_compra │ proveedor_nombre │
├─────────────────┼─────────────────┼──────────────┼──────────────────┤
│ ABC123          │ 9500.00         │ 2025-02-15   │ DIST. ABC        │
│ ABC123          │ 12000.00        │ 2025-02-01   │ FERRETERÍA XYZ   │
│ ABC123          │ 10000.00        │ 2025-01-15   │ FERRETERÍA XYZ   │
└─────────────────┴─────────────────┴──────────────┴──────────────────┘

-- Con estos datos se calcula:
-- • precio_anterior = 9500.00 (última compra)
-- • variacion_precio = ((9500 - 9500) / 9500) * 100 = 0%
-- • variacion_tipo = "igual"
-- • precio_promedio = (10000 + 12000 + 9500 + 9500) / 4 = 10250
-- • precio_minimo = 9500
-- • precio_maximo = 12000
-- • total_compras = 4
-- • ultimo_proveedor = "DIST. ABC"
-- • dias_desde_ultima = 13
```

---

## 🎯 Decisiones de Diseño

### ¿Por qué denormalizar proveedor_nombre?
```
❌ Sin denormalización:
   SELECT p.*, i.proveedor_nombre
   FROM invoice_products_v2 p
   JOIN invoices_v2 i ON p.cufe = i.cufe
   WHERE p.codigo_producto = 'ABC123'
   
   → Requiere JOIN en cada query
   → Más lento

✅ Con denormalización:
   SELECT *
   FROM invoice_products_v2
   WHERE codigo_producto = 'ABC123'
   
   → Query directa, sin JOIN
   → Mucho más rápido
   → Índice en proveedor_nombre
```

### ¿Por qué calcular en inserción y no en query?
```
❌ Calcular en cada query:
   - Lento (recalcula cada vez)
   - Carga en el servidor
   - Inconsistente

✅ Calcular en inserción:
   - Rápido (ya está calculado)
   - Sin carga adicional
   - Consistente
   - Histórico preservado
```

### ¿Por qué índices compuestos?
```
Índice: (codigo_producto, fecha_compra)

Query optimizada:
  SELECT * FROM invoice_products_v2
  WHERE codigo_producto = 'ABC123'
  ORDER BY fecha_compra DESC
  
  → Usa índice compuesto
  → No necesita sort adicional
  → Muy rápido
```

---

## 📈 Performance

```
Operación: Calcular trazabilidad para 1 producto

Sin índices:
  ├─ Buscar compras anteriores: ~500ms (full table scan)
  ├─ Calcular estadísticas: ~50ms
  └─ Total: ~550ms

Con índices:
  ├─ Buscar compras anteriores: ~5ms (index scan)
  ├─ Calcular estadísticas: ~5ms
  └─ Total: ~10ms

Mejora: 55x más rápido ⚡
```

---

**Diagrama completo del sistema de trazabilidad** 📊
