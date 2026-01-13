# Resumen: Corrección de Validación de IVA

## Problema Identificado

Las facturas mostraban irregularidades falsas donde los totales realmente coincidían. El problema estaba en cómo se calculaba y almacenaba el campo `valor_total` de los items durante la extracción del PDF.

### Causa Raíz

En el código de extracción (`pdf_extractor_service.py`), cuando `valor_total` no venía en el PDF y necesitaba ser calculado, **siempre se sumaba el IVA**:

```python
# CÓDIGO ANTERIOR (INCORRECTO)
subtotal_item = (precio_unitario * cantidad) - descuento + recargo
valor_total = subtotal_item + iva_valor + inc_valor  # ❌ Siempre suma IVA
```

Esto causaba un desajuste porque:
- En facturas con **IVA NO incluido** (mayoría en Colombia), el `valor_total` del item debería ser el subtotal **SIN IVA**
- La validación esperaba que `suma(valor_total) = subtotal` cuando IVA NO está incluido
- Pero el código guardaba `valor_total` con IVA incluido, causando que `suma(valor_total) > subtotal`

## Solución Implementada

### 1. Corrección en Extracción de PDF

Modificamos la lógica para detectar correctamente si el IVA está incluido en el precio:

```python
# CÓDIGO NUEVO (CORRECTO)
# REGLA: En facturas colombianas, cuando el IVA se lista por separado
# en la tabla de items, significa que NO está incluido en el precio
if iva_valor > 0:
    # IVA listado por separado = NO incluido en precio
    iva_incluido = False
    valor_total = subtotal_item + inc_valor  # ✓ Sin IVA
else:
    # Sin IVA o IVA incluido en precio
    valor_total = subtotal_item + inc_valor
```

### 2. Validación Correcta

La validación ahora funciona correctamente para ambos casos:

**Caso A: IVA NO incluido** (mayoría de facturas colombianas)
- PDF muestra: Subtotal $1,000,000 + IVA $190,000 = Total $1,190,000
- Extracción: `valor_total` = $1,000,000 (sin IVA)
- Validación: 
  - ✓ `suma(valor_total)` = `subtotal` → $1,000,000 = $1,000,000
  - ✓ `suma(valor_total) + suma(iva_valor)` = `total_neto` → $1,190,000 = $1,190,000

**Caso B: IVA incluido** (menos común)
- PDF muestra: Total $1,190,000 (incluye IVA $190,000)
- Extracción: `valor_total` = $1,190,000 (con IVA)
- Validación:
  - ✓ `suma(valor_total)` = `total_neto` → $1,190,000 = $1,190,000
  - ✓ `suma(valor_total) - suma(iva_valor)` = `subtotal` → $1,000,000 = $1,000,000

## Archivos Modificados

1. **`CODE/src/app/services/pdf_extractor_service.py`**
   - Líneas 647-670: Reordenada la lógica de detección de IVA incluido
   - Ahora detecta primero si IVA está incluido antes de calcular `valor_total`
   - Aplica regla: "IVA listado por separado = NO incluido"

2. **`CODE/src/app/services/invoice_service.py`**
   - Líneas 183-230: Validación ya estaba correcta
   - Detecta automáticamente si mayoría de items tienen IVA incluido o no
   - Aplica validaciones diferentes según el caso

## Pruebas

Se creó `test_iva_validation.py` que verifica ambos casos:
- ✓ Caso 1: IVA NO incluido - Validación correcta
- ✓ Caso 2: IVA incluido - Validación correcta

## Próximos Pasos

1. **Desplegar a staging** ✓ (commit 921555f)
2. **Re-procesar facturas con errores**: Usar el botón "Re-procesar todas" en el dashboard
3. **Verificar**: Las irregularidades falsas deberían desaparecer

## Comando para Re-procesar

Una vez desplegado en staging, hacer clic en:
- Dashboard → Alerta de irregularidades → Botón "Re-procesar todas"

O para una factura específica:
- Detalle de factura → Botón "Re-procesar"

Esto volverá a extraer los datos del PDF con la nueva lógica corregida.
