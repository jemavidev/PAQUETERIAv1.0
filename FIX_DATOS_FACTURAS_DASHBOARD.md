# Fix: Captura y Visualización de Datos de Facturas

## Problema Identificado

La tabla del dashboard mostraba datos incompletos o incorrectos:
- Proveedores mostrando "N/A" o texto muy largo
- Números de documento faltantes
- Información no estructurada correctamente
- Datos de `SupplierInvoice` vs `Invoice` procesada no se manejaban bien

## Solución Implementada

### 1. Backend: Endpoint `/api/supplier-invoices/list` Mejorado

**Cambios principales:**

#### A. Priorización de Datos
```python
# 1. Inicializar con datos de SupplierInvoice (siempre disponibles)
proveedor = inv.supplier_name or "N/A"
fecha_emision = inv.invoice_date
numero_documento = inv.invoice_number or "N/A"
total = inv.total_amount or 0

# 2. Si existe factura procesada, sobrescribir con esos datos (más completos)
if inv.processed_invoice_id:
    processed_inv = db.query(Invoice).filter(...)
    if processed_inv:
        proveedor = processed_inv.supplier.razon_social
        fecha_emision = processed_inv.fecha_emision
        # etc...
```

#### B. Limpieza de Datos de Proveedor
```python
# Limpiar texto largo o con datos extraños
if proveedor and len(proveedor) > 100:
    proveedor = proveedor.split('FECHA')[0].strip()
    proveedor = proveedor.split('NIT')[0].strip()
    if len(proveedor) > 50:
        proveedor = proveedor[:50] + "..."
```

#### C. Manejo Robusto de Errores
```python
try:
    # Procesar factura
except Exception as e:
    logger.error(f"Error procesando invoice {inv.id}: {e}", exc_info=True)
    # Agregar con datos mínimos para no perder la factura
    result.append({
        "id": inv.id,
        "proveedor": "Error al cargar",
        "status": "error",
        # ...
    })
```

#### D. Datos Adicionales Retornados
```python
{
    "id": inv.id,
    "original_filename": inv.original_filename,  # NUEVO
    "fecha_emision": fecha_emision,
    "proveedor": proveedor,
    "numero_documento": numero_documento,
    "cufe": inv.cufe,
    "cufe_source": inv.cufe_source,  # NUEVO
    "status": inv.status.value,
    "total": total,
    "uploaded_at": inv.uploaded_at,  # NUEVO
    "processed_invoice_id": inv.processed_invoice_id,  # NUEVO
}
```

### 2. Frontend: Renderizado Mejorado

**Cambios principales:**

#### A. Formateo de Fecha Robusto
```javascript
let fecha = 'N/A';
if (inv.fecha_emision) {
    try {
        fecha = new Date(inv.fecha_emision).toLocaleDateString('es-CO', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    } catch (e) {
        fecha = inv.fecha_emision.split('T')[0];
    }
}
```

#### B. Limpieza de Proveedor
```javascript
let proveedor = inv.proveedor || 'Sin información';
if (proveedor === 'N/A' || proveedor === 'null' || !proveedor.trim()) {
    proveedor = '<span class="text-gray-400 italic">Sin proveedor</span>';
} else {
    // Truncar si es muy largo
    if (proveedor.length > 40) {
        proveedor = `<span title="${proveedor}">${proveedor.substring(0, 40)}...</span>`;
    }
}
```

#### C. Número de Documento con Validación
```javascript
let numeroDoc = inv.numero_documento || 'N/A';
if (numeroDoc === 'N/A' || numeroDoc === 'null' || !numeroDoc.trim()) {
    numeroDoc = '<span class="text-gray-400 italic">Sin número</span>';
}
```

#### D. CUFE Mejorado
```javascript
const cufeDisplay = inv.cufe ? `
    <div class="flex items-center gap-2">
        <span class="text-xs text-gray-600 font-mono truncate max-w-[120px]" 
              title="${inv.cufe}">
            ${inv.cufe.substring(0, 16)}...
        </span>
        <button onclick="copyCufe('${inv.cufe}')" 
                class="p-1 text-gray-400 hover:text-papyrus-blue transition-colors" 
                title="Copiar CUFE completo">
            <!-- SVG icon -->
        </button>
    </div>
` : '<span class="text-xs px-2 py-1 bg-red-50 text-red-600 rounded">Sin CUFE</span>';
```

#### E. Mensajes de Estado Vacío Mejorados
```javascript
// Cuando no hay facturas
<svg class="mx-auto h-12 w-12 text-gray-400 mb-3">...</svg>
<p class="text-lg font-medium mb-2">No hay facturas cargadas</p>
<p class="text-sm text-gray-400 mb-4">Comienza subiendo tu primera factura de proveedor</p>
<button onclick="openUploadModal()" class="px-4 py-2 bg-papyrus-blue text-white rounded-lg">
    Subir primera factura
</button>
```

## Mejoras Visuales

1. **Tooltips**: Hover sobre proveedor largo muestra el nombre completo
2. **Font mono para CUFE**: Mejor legibilidad del código
3. **Badges coloridos**: Estados más visibles
4. **Transiciones suaves**: Hover effects en botones y filas
5. **Iconos mejorados**: SVG más claros y consistentes
6. **Mensajes informativos**: Estados vacíos y errores más amigables

## Flujo de Datos

```
SupplierInvoice (BD)
    ↓
    ├─ Datos básicos (siempre disponibles)
    │  ├─ supplier_name
    │  ├─ invoice_date
    │  ├─ invoice_number
    │  └─ total_amount
    ↓
    └─ Si processed_invoice_id existe
       ↓
       Invoice (BD) - Datos procesados (más completos)
       ├─ supplier.razon_social
       ├─ fecha_emision
       ├─ numero_documento
       └─ total_neto
       ↓
Backend API
    ↓
    ├─ Limpieza de datos
    ├─ Validación
    └─ Formateo
    ↓
JSON Response
    ↓
Frontend JavaScript
    ↓
    ├─ Formateo de fecha
    ├─ Truncado de texto
    ├─ Validación de campos
    └─ Generación de HTML
    ↓
Tabla HTML renderizada
```

## Testing

Después de desplegar, verificar:

1. ✅ Proveedores se muestran correctamente (sin texto extraño)
2. ✅ Fechas formateadas como DD/MM/YYYY
3. ✅ Números de documento visibles
4. ✅ CUFE truncado con tooltip mostrando completo
5. ✅ Botón copiar CUFE funciona
6. ✅ Estados con badges coloridos
7. ✅ Botones "Ver detalles" y "Ver PDF" funcionan
8. ✅ Hover effects en filas y botones
9. ✅ Mensaje amigable cuando no hay facturas
10. ✅ Manejo de errores sin romper la tabla

## Archivos Modificados

1. `CODE/src/app/routes/invoices.py`
   - Endpoint `/api/supplier-invoices/list` completamente reescrito
   - Mejor priorización de datos
   - Limpieza de texto largo
   - Manejo robusto de errores

2. `CODE/src/templates/invoices/dashboard.html`
   - Función `loadFacturasTab()` mejorada
   - Mejor formateo de datos
   - Validación de campos
   - Mensajes de estado mejorados
