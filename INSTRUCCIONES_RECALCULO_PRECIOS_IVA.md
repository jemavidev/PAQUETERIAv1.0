# Recálculo de Precios con IVA en Productos

## Problema Identificado

Algunas facturas tienen precios que **YA incluyen IVA** en los campos `precio_unitario` y `total_item`, mientras que otras tienen precios **SIN IVA** y el IVA está en el campo `iva_valor` separado.

Ejemplo:
- **Factura con IVA incluido**: precio_unitario = $6.600 (con IVA), total_item = $39.600 (6 × $6.600)
- **Factura con IVA separado**: precio_unitario = $5.546 (sin IVA), iva_valor = $6.322, total = $39.598

## Solución Implementada

### 1. Detección Automática en el Backend

**Archivo**: `CODE/src/app/routes/invoices_v2_routes.py`

El endpoint `/api/v2/invoices/productos` ahora incluye lógica para detectar automáticamente si cada producto tiene IVA incluido:

```python
# Lógica de detección:
if iva_valor > 0 y es significativo:
    # Verificar si total + iva_valor ≈ precio × cantidad × (1 + IVA%)
    if coincide:
        iva_incluido_en_precio = False  # IVA está separado
    else:
        iva_incluido_en_precio = True   # IVA ya está incluido
else:
    # Comparar total con precio × cantidad × (1 + IVA%)
    if coincide:
        iva_incluido_en_precio = True   # IVA ya está incluido
    else:
        iva_incluido_en_precio = False  # IVA está separado
```

El backend retorna un nuevo campo: `iva_incluido_en_precio` (true/false)

### 2. Cálculo Correcto en el Frontend

**Archivo**: `CODE/src/templates/invoices_v2/productos.html`

El frontend ahora usa el campo `iva_incluido_en_precio` para mostrar los precios correctamente:

```javascript
// Precio unitario CON IVA
if (ivaIncluidoEnPrecio) {
    precioConIva = precio_unitario;  // Ya incluye IVA
} else {
    precioConIva = precio_unitario × (1 + IVA%/100);  // Calcular IVA
}

// Total CON IVA
if (ivaIncluidoEnPrecio) {
    totalConIva = total_item;  // Ya incluye IVA
} else {
    totalConIva = total_item + iva_valor;  // Sumar IVA
}
```

### 3. Mejoras Visuales

- ✅ Cada producto en una sola línea
- ✅ Textos truncados con tooltips
- ✅ Etiquetas "IVA incluido" en encabezados
- ✅ Badges compactos para estado
- ✅ Tabla con anchos fijos optimizados

## Análisis de Facturas Existentes

### Script de Análisis

**Archivo**: `CODE/recalcular_precios_iva_productos.py`

Este script analiza todas las facturas y productos en la base de datos para:
- Detectar qué facturas tienen IVA incluido y cuáles no
- Generar un reporte detallado
- Mostrar ejemplos de cada tipo

### Cómo Ejecutar el Análisis

#### Opción 1: Dentro del contenedor Docker (RECOMENDADO)

```bash
docker-compose exec web python recalcular_precios_iva_productos.py
```

#### Opción 2: Con el script bash

```bash
cd CODE
./analizar_precios_iva.sh
```

#### Opción 3: Manualmente con entorno virtual

```bash
cd CODE
source .venv/bin/activate
python recalcular_precios_iva_productos.py
```

## Resultado Esperado

El script mostrará:

```
================================================================================
ANÁLISIS DE PRECIOS CON IVA EN PRODUCTOS
================================================================================

📊 Total de facturas a analizar: 150

================================================================================
RESULTADOS DEL ANÁLISIS
================================================================================

📦 Total de productos analizados: 1907
✅ Productos con IVA incluido en precio: 450 (23.6%)
❌ Productos con IVA separado: 1457 (76.4%)

📄 Facturas con IVA incluido: 35
📄 Facturas con IVA separado: 115

================================================================================
EJEMPLOS DE FACTURAS CON IVA INCLUIDO EN PRECIOS
================================================================================

📄 Factura: FV-12345
   Proveedor: PROVEEDOR XYZ
   Fecha: 2024-01-15
   CUFE: abc123...

   📦 TABLA LEAJADORA PLASTICA
      Precio unitario: $6,600 (YA incluye IVA)
      Cantidad: 6
      Total: $39,600 (YA incluye IVA)
      IVA %: 19%
```

## Verificación

Después de reiniciar el servidor, verifica en `/invoices/productos`:

1. **TABLA LEAJADORA PLASTICA**:
   - Precio: $6.600 ✅
   - Total: $39.600 ✅

2. **Otros productos**:
   - Los precios se mostrarán correctamente con IVA incluido
   - Cada producto en una sola línea

## Archivos Modificados

1. ✅ `CODE/src/app/routes/invoices_v2_routes.py` - Lógica de detección en backend
2. ✅ `CODE/src/templates/invoices_v2/productos.html` - Cálculo correcto en frontend
3. ✅ `CODE/recalcular_precios_iva_productos.py` - Script de análisis
4. ✅ `CODE/analizar_precios_iva.sh` - Script bash para ejecutar análisis

## Próximos Pasos

1. Ejecutar el script de análisis para ver el reporte completo
2. Reiniciar el servidor para aplicar los cambios
3. Verificar en la interfaz que los precios se muestren correctamente
4. Si hay casos específicos que no se detectan bien, ajustar la tolerancia en el código

## Notas Técnicas

- **Tolerancia**: 3% para errores de redondeo
- **Detección**: Se basa en comparar `total_item` con cálculos esperados
- **Prioridad**: Si hay `iva_valor` significativo, se usa para la detección
- **Fallback**: Si no se puede determinar, asume que NO incluye IVA (más común en DIAN)
