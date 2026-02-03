# 📊 Estados de Facturas en el Sistema

## 🎯 Estados Disponibles

El sistema maneja **5 estados** diferentes para las facturas:

### 1. 🟡 `pendiente_dian` - Pendiente DIAN
**Descripción**: La factura del proveedor fue cargada, pero aún no se ha subido el documento DIAN.

**Cuándo se asigna**:
- Al cargar una factura de proveedor con CUFE válido
- Después de asociar un CUFE a una factura temporal

**Información disponible**:
- ✅ CUFE
- ✅ Proveedor (nombre y NIT)
- ✅ Número de factura
- ✅ Fecha de emisión
- ✅ Total
- ❌ Datos DIAN (no disponibles aún)
- ❌ Productos (no disponibles aún)

**Badge visual**: 🟡 Amarillo - "Pend. DIAN"

**Próximo paso**: Subir el archivo DIAN para completar la información

---

### 2. 🟢 `completo` - Completo
**Descripción**: La factura tiene TODA la información: datos del proveedor Y datos DIAN.

**Cuándo se asigna**:
- Después de subir el archivo DIAN a una factura con estado `pendiente_dian`
- Cuando el sistema procesa exitosamente el documento DIAN

**Información disponible**:
- ✅ CUFE
- ✅ Proveedor (nombre y NIT)
- ✅ Número de factura
- ✅ Fecha de emisión
- ✅ Total
- ✅ Datos DIAN completos (emisor, adquiriente, totales, etc.)
- ✅ Productos extraídos del documento DIAN

**Badge visual**: 🟢 Verde - "Completo"

**Estado final**: Esta es la factura completamente procesada

---

### 3. 🔴 `error` - Error
**Descripción**: Hubo un error al procesar la factura.

**Cuándo se asigna**:
- Error al extraer información del PDF
- Error al subir archivos a S3
- Error de validación de datos
- Error al procesar el documento DIAN

**Información disponible**:
- Variable (depende de dónde ocurrió el error)
- Revisar campo `notas` para detalles del error

**Badge visual**: 🔴 Rojo - "Error"

**Acción requerida**: Revisar el error y volver a cargar la factura

---

### 4. ⚪ `sin_dian` - Sin DIAN
**Descripción**: La factura del proveedor está completa, pero no se subirá documento DIAN.

**Cuándo se asigna**:
- Manualmente por el usuario
- Cuando se decide que no se necesita el documento DIAN

**Información disponible**:
- ✅ CUFE
- ✅ Proveedor (nombre y NIT)
- ✅ Número de factura
- ✅ Fecha de emisión
- ✅ Total
- ❌ Datos DIAN (no se subirán)
- ❌ Productos (no disponibles)

**Badge visual**: ⚪ Gris - "Sin DIAN"

**Estado final**: La factura se considera completa sin documento DIAN

---

### 5. 🟠 `sin_cufe` - Sin CUFE
**Descripción**: La factura fue cargada pero no se pudo extraer el CUFE automáticamente.

**Cuándo se asigna**:
- Al cargar una factura de proveedor cuando no se detecta el CUFE
- Se genera un CUFE temporal con formato `TEMP_xxxxxxxx`

**Información disponible**:
- ⚠️ CUFE temporal (no válido)
- ✅ Proveedor (si se pudo extraer)
- ✅ Número de factura (si se pudo extraer)
- ✅ Fecha de emisión (si se pudo extraer)
- ✅ Total (si se pudo extraer)
- ❌ Datos DIAN (no disponibles)

**Badge visual**: 🟠 Naranja - "Sin CUFE"

**Acción requerida**: Asociar el CUFE real manualmente

**Próximo paso**: Después de asociar el CUFE, cambia a `pendiente_dian`

---

## 🔄 Flujo de Estados

### Flujo Normal (Con CUFE)
```
1. Cargar factura proveedor (con CUFE detectado)
   ↓
   🟡 pendiente_dian
   ↓
2. Subir documento DIAN
   ↓
   🟢 completo
```

### Flujo Sin CUFE
```
1. Cargar factura proveedor (sin CUFE detectado)
   ↓
   🟠 sin_cufe
   ↓
2. Asociar CUFE manualmente
   ↓
   🟡 pendiente_dian
   ↓
3. Subir documento DIAN
   ↓
   🟢 completo
```

### Flujo Sin DIAN
```
1. Cargar factura proveedor (con CUFE detectado)
   ↓
   🟡 pendiente_dian
   ↓
2. Marcar como "Sin DIAN" (manual)
   ↓
   ⚪ sin_dian
```

### Flujo con Error
```
1. Cargar factura proveedor
   ↓
   🔴 error (si falla la carga)
   
O

1. Cargar factura proveedor
   ↓
   🟡 pendiente_dian
   ↓
2. Subir documento DIAN (falla)
   ↓
   🔴 error
```

---

## 📊 Estadísticas por Estado

En tu sistema actual (43 facturas):

| Estado | Cantidad | Porcentaje | Descripción |
|--------|----------|------------|-------------|
| 🟡 `pendiente_dian` | ~35 | ~81% | Mayoría de facturas esperando documento DIAN |
| 🟢 `completo` | ~5 | ~12% | Facturas completamente procesadas |
| 🟠 `sin_cufe` | ~3 | ~7% | Facturas sin CUFE (necesitan asociación manual) |
| 🔴 `error` | 0 | 0% | Sin errores actualmente |
| ⚪ `sin_dian` | 0 | 0% | Ninguna marcada como "sin DIAN" |

---

## 🎨 Colores y Badges

### En la Interfaz

```html
<!-- Pendiente DIAN -->
<span class="bg-yellow-100 text-yellow-800">Pend. DIAN</span>

<!-- Completo -->
<span class="bg-green-100 text-green-800">Completo</span>

<!-- Error -->
<span class="bg-red-100 text-red-800">Error</span>

<!-- Sin DIAN -->
<span class="bg-gray-100 text-gray-800">Sin DIAN</span>

<!-- Sin CUFE -->
<span class="bg-orange-100 text-orange-800">Sin CUFE</span>
```

### Código de Colores

- 🟡 **Amarillo**: Acción pendiente (necesita documento DIAN)
- 🟢 **Verde**: Completado exitosamente
- 🔴 **Rojo**: Error que requiere atención
- ⚪ **Gris**: Estado final sin acción adicional
- 🟠 **Naranja**: Requiere intervención manual (asociar CUFE)

---

## 🔧 Cambiar Estado Manualmente

Puedes cambiar el estado de una factura desde la interfaz:

1. Haz clic en el botón de **editar** (✏️) en la factura
2. Selecciona el nuevo estado en el dropdown
3. Guarda los cambios

**Estados disponibles en el selector**:
- Pendiente DIAN
- Completo
- Error
- Sin DIAN
- Sin CUFE

---

## 💡 Recomendaciones

### Para `pendiente_dian`
- ✅ Subir el documento DIAN lo antes posible
- ✅ Verificar que el CUFE sea correcto
- ✅ Asegurarse de tener el PDF DIAN disponible

### Para `sin_cufe`
- ✅ Asociar el CUFE real manualmente
- ✅ Verificar que el CUFE tenga exactamente 96 caracteres
- ✅ Copiar el CUFE directamente del PDF DIAN

### Para `error`
- ✅ Revisar el campo "Notas" para ver el error específico
- ✅ Volver a cargar la factura si es necesario
- ✅ Verificar que el PDF no esté corrupto

### Para `completo`
- ✅ No requiere acción adicional
- ✅ Todos los datos están disponibles
- ✅ Se pueden consultar productos y detalles completos

---

## 📝 Notas Técnicas

### En la Base de Datos
```sql
-- Columna estado en la tabla invoices_v2
estado VARCHAR(20) DEFAULT 'pendiente_dian' NOT NULL

-- Valores permitidos:
-- 'pendiente_dian', 'completo', 'error', 'sin_dian', 'sin_cufe'
```

### En el Código
```python
# Asignar estado al crear factura
invoice.estado = 'sin_cufe' if cufe.startswith('TEMP_') else 'pendiente_dian'

# Cambiar estado al subir DIAN
invoice.estado = 'completo'

# Cambiar estado manualmente
invoice.estado = 'sin_dian'
```

---

## 🎯 Resumen Rápido

| Estado | Emoji | Color | Acción Requerida |
|--------|-------|-------|------------------|
| `pendiente_dian` | 🟡 | Amarillo | Subir documento DIAN |
| `completo` | 🟢 | Verde | Ninguna (completado) |
| `error` | 🔴 | Rojo | Revisar y corregir error |
| `sin_dian` | ⚪ | Gris | Ninguna (estado final) |
| `sin_cufe` | 🟠 | Naranja | Asociar CUFE manualmente |
