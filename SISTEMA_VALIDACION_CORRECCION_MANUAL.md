# SISTEMA DE VALIDACIÓN Y CORRECCIÓN MANUAL

## 🎯 OBJETIVO

Permitir identificar y corregir manualmente campos problemáticos en facturas procesadas desde PDF (5% de casos edge).

---

## 📋 COMPONENTES IMPLEMENTADOS

### 1. Backend - ValidationService ✅

**Archivo**: `CODE/src/app/services/validation_service.py`

**Funcionalidad**:
- Valida facturas y detecta inconsistencias en campos críticos
- Solo aplica para facturas procesadas desde PDF (XML siempre retorna 100%)
- Retorna score de validación y lista de advertencias con severidad

**Campos validados**:
```python
CRITICAL_FIELDS = {
    'dian_total_neto': 'Total a pagar',
    'dian_subtotal': 'Subtotal',
    'dian_total_iva': 'Total IVA',
    'fecha_emision': 'Fecha de emisión',
    'numero_factura': 'Número de factura',
}
```

**Validaciones implementadas**:
1. ✅ Total a pagar (NULL o ≤ 0)
2. ✅ Subtotal (NULL)
3. ✅ IVA total (NULL)
4. ✅ Consistencia de totales (Total ≠ Subtotal + IVA)
5. ✅ Fecha de emisión (NULL, futura, o muy antigua)
6. ✅ Número de factura (NULL)
7. ✅ Productos (0 productos extraídos)
8. ✅ IVA en productos (productos sin IVA cuando deberían tenerlo)

**Severidades**:
- `critical` 🔴 - Campo crítico faltante
- `high` 🟠 - Campo importante faltante
- `medium` 🟡 - Inconsistencia detectada
- `low` 🔵 - Advertencia informativa

**Ejemplo de respuesta**:
```json
{
  "has_warnings": true,
  "warnings": [
    {
      "field": "dian_total_neto",
      "field_label": "Total a pagar",
      "severity": "critical",
      "message": "Total no extraído del PDF",
      "current_value": null,
      "suggestion": "Ingresar total manualmente"
    },
    {
      "field": "totales_inconsistentes",
      "field_label": "Totales",
      "severity": "high",
      "message": "Total no coincide: 1234567 ≠ 1037368 + 197198",
      "current_value": {
        "total": 1234567,
        "subtotal": 1037368,
        "iva": 197198,
        "diferencia": 1
      },
      "suggestion": "Verificar cálculos"
    }
  ],
  "validation_score": 60,
  "source": "PDF",
  "total_fields_checked": 5,
  "valid_fields": 3
}
```

---

### 2. Backend - Endpoints API ✅

**Archivo**: `CODE/src/app/routes/invoices_v2_routes.py`

#### Endpoint 1: Validar factura

```http
GET /api/v2/invoices/cufe/{cufe}/validate
```

**Respuesta**:
```json
{
  "has_warnings": true,
  "warnings": [...],
  "validation_score": 85,
  "source": "PDF"
}
```

#### Endpoint 2: Corregir campos

```http
PATCH /api/v2/invoices/cufe/{cufe}/correct
Content-Type: application/json

{
  "dian_total_neto": 1234567.89,
  "dian_subtotal": 1037368.98,
  "dian_total_iva": 197198.91,
  "fecha_emision": "2025-06-13T00:00:00",
  "numero_factura": "PAP22408"
}
```

**Respuesta**:
```json
{
  "message": "Correcciones aplicadas correctamente",
  "fields_corrected": ["dian_total_neto", "dian_subtotal", "dian_total_iva"],
  "invoice": { ... }
}
```

**Tracking de correcciones**:
Las correcciones se guardan en `dian_datos_raw.manual_corrections`:
```json
{
  "manual_corrections": [
    {
      "timestamp": "2026-02-10T15:30:00",
      "fields": ["dian_total_neto", "dian_subtotal"],
      "values": {
        "dian_total_neto": 1234567.89,
        "dian_subtotal": 1037368.98
      }
    }
  ]
}
```

---

### 3. Backend - Schema actualizado ✅

**Archivo**: `CODE/src/app/routes/invoices_v2_routes.py`

```python
class InvoiceResponse(BaseModel):
    # ... campos existentes ...
    validation_warnings: Optional[dict] = None  # ✅ NUEVO
    
class InvoiceCorrectionRequest(BaseModel):
    """Request para corrección manual de campos problemáticos"""
    dian_total_neto: Optional[float] = None
    dian_subtotal: Optional[float] = None
    dian_total_iva: Optional[float] = None
    fecha_emision: Optional[datetime] = None
    numero_factura: Optional[str] = None
    dian_emisor_razon_social: Optional[str] = None
    dian_emisor_nit: Optional[str] = None
```

---

### 4. Frontend - UI Components 🚧 (PENDIENTE)

#### A. Badge de advertencia en lista

**Ubicación**: Tab CUFE, columna "Estado"

**Visual**:
```
┌─────────────────────────────────────┐
│ Estado                              │
├─────────────────────────────────────┤
│ ● 5  ⚠️                             │  ← Verde con número + icono advertencia
│ ● 3                                 │  ← Verde sin advertencia
│ ○                                   │  ← Amarillo (pendiente)
└─────────────────────────────────────┘
```

**Implementación**:
```javascript
// En renderCufeRow()
const hasWarnings = invoice.validation_score && invoice.validation_score < 95;
const warningIcon = hasWarnings ? '<span class="ml-1 text-orange-500" title="Tiene advertencias">⚠️</span>' : '';

const dianBadge = dianValidado
    ? `<span class="inline-flex items-center justify-center px-2 py-0.5 rounded-full bg-green-500 text-white text-xs font-semibold min-w-[28px]" title="Validado - ${invoice.productos_count} productos">
         ${invoice.productos_count}${warningIcon}
       </span>`
    : '...';
```

#### B. Modal de corrección

**Trigger**: Click en icono ⚠️ o botón "Corregir"

**Contenido**:
```html
<div class="modal">
  <h3>Corregir campos problemáticos</h3>
  <p class="text-sm text-gray-600">
    Esta factura fue procesada desde PDF y tiene campos con posibles inconsistencias.
    Revisa y corrige los campos marcados.
  </p>
  
  <!-- Lista de advertencias -->
  <div class="warnings-list">
    <div class="warning-item critical">
      <span class="icon">⛔</span>
      <div>
        <strong>Total a pagar</strong>
        <p>Total no extraído del PDF</p>
        <input type="number" step="0.01" placeholder="Ingresar total" />
      </div>
    </div>
    
    <div class="warning-item high">
      <span class="icon">⚠️</span>
      <div>
        <strong>Subtotal</strong>
        <p>Subtotal no extraído</p>
        <input type="number" step="0.01" placeholder="Ingresar subtotal" />
      </div>
    </div>
  </div>
  
  <div class="actions">
    <button onclick="closeModal()">Cancelar</button>
    <button onclick="applyCorrections()">Aplicar correcciones</button>
  </div>
</div>
```

#### C. Indicadores en columnas

**Visual en tabla**:
```
┌──────────────┬──────────────┬──────────────┐
│ Proveedor    │ Total        │ Fecha        │
├──────────────┼──────────────┼──────────────┤
│ VENEPLAST    │ $ 1,234,567  │ 2025-06-13   │
│ PAPELERIA    │ ⚠️ -         │ ⚠️ 2027-06-13│  ← Campos con advertencia
│ DISTRIBUIDORA│ $ 987,654    │ 2025-05-20   │
└──────────────┴──────────────┴──────────────┘
```

---

## 🔄 FLUJO DE USO

### Escenario 1: Usuario carga PDF con problemas

```
1. Usuario sube archivo PDF DIAN
   ↓
2. Sistema procesa y detecta campos faltantes
   ↓
3. Factura se marca con validation_score < 95
   ↓
4. En la lista, aparece icono ⚠️ junto al badge
   ↓
5. Usuario hace click en ⚠️
   ↓
6. Se abre modal con lista de campos problemáticos
   ↓
7. Usuario ingresa valores correctos
   ↓
8. Sistema guarda correcciones y actualiza factura
   ↓
9. Icono ⚠️ desaparece (score = 100)
```

### Escenario 2: Usuario revisa factura existente

```
1. Usuario navega a tab CUFE
   ↓
2. Ve facturas con icono ⚠️
   ↓
3. Click en icono para ver detalles
   ↓
4. Modal muestra qué campos tienen problemas
   ↓
5. Usuario decide si corregir o dejar así
```

---

## 📊 CAMPOS CORREGIBLES

### Campos CRÍTICOS (siempre mostrar):
- ✅ `dian_total_neto` - Total a pagar
- ✅ `dian_subtotal` - Subtotal
- ✅ `dian_total_iva` - Total IVA
- ✅ `fecha_emision` - Fecha de emisión
- ✅ `numero_factura` - Número de factura

### Campos ALTOS (mostrar si hay problema):
- ✅ `dian_emisor_razon_social` - Nombre proveedor
- ✅ `dian_emisor_nit` - NIT proveedor

### Campos NO corregibles (requieren reprocesamiento):
- ❌ Productos completos (si no se extrajeron)
- ❌ IVA por producto (requiere editar cada producto)

---

## 🎨 DISEÑO VISUAL

### Colores por severidad:
```css
.severity-critical { color: #DC2626; }  /* Rojo */
.severity-high     { color: #F59E0B; }  /* Naranja */
.severity-medium   { color: #EAB308; }  /* Amarillo */
.severity-low      { color: #3B82F6; }  /* Azul */
```

### Iconos por severidad:
```
critical: ⛔
high:     ⚠️
medium:   ⚡
low:      ℹ️
```

---

## 🧪 TESTING

### Test 1: Validación de factura XML
```bash
curl http://localhost:8000/api/v2/invoices/cufe/{cufe}/validate
# Esperado: validation_score = 100, has_warnings = false
```

### Test 2: Validación de factura PDF con problemas
```bash
curl http://localhost:8000/api/v2/invoices/cufe/{cufe}/validate
# Esperado: validation_score < 95, has_warnings = true, warnings = [...]
```

### Test 3: Corrección de campos
```bash
curl -X PATCH http://localhost:8000/api/v2/invoices/cufe/{cufe}/correct \
  -H "Content-Type: application/json" \
  -d '{
    "dian_total_neto": 1234567.89,
    "dian_subtotal": 1037368.98,
    "dian_total_iva": 197198.91
  }'
# Esperado: fields_corrected = ["dian_total_neto", "dian_subtotal", "dian_total_iva"]
```

### Test 4: Verificar correcciones guardadas
```bash
curl http://localhost:8000/api/v2/invoices/cufe/{cufe}/full
# Verificar: dian_datos_raw.manual_corrections existe
```

---

## 📝 PRÓXIMOS PASOS

### Implementación Frontend (PENDIENTE):

1. **Agregar badge de advertencia en lista** ✅ Backend listo
   - Modificar `renderCufeRow()` en `cufe.html`
   - Agregar icono ⚠️ cuando `validation_score < 95`
   - Tooltip con mensaje "Tiene campos con advertencias"

2. **Crear modal de corrección** 🚧
   - HTML del modal en `cufe.html`
   - JavaScript para abrir/cerrar modal
   - Función `loadValidationWarnings(cufe)` para cargar advertencias
   - Función `applyCorrections(cufe, corrections)` para guardar

3. **Agregar indicadores en columnas** 🚧
   - Icono ⚠️ en columnas con valores problemáticos
   - Tooltip explicando el problema
   - Color diferente para valores con advertencia

4. **Testing en navegador** 🚧
   - Probar con facturas PDF reales
   - Verificar que las correcciones se guardan
   - Verificar que el icono desaparece después de corregir

---

## ✅ ESTADO ACTUAL

### Completado:
- ✅ ValidationService implementado
- ✅ Endpoints API creados
- ✅ Schema actualizado
- ✅ Tracking de correcciones
- ✅ Documentación completa

### Pendiente:
- 🚧 UI Frontend (modal de corrección)
- 🚧 Badge de advertencia en lista
- 🚧 Indicadores en columnas
- 🚧 Testing en navegador

---

**Fecha**: 10 de Febrero de 2026  
**Sistema**: Validación y Corrección Manual de Campos Edge  
**Precisión objetivo**: 100% (95% automático + 5% manual)
