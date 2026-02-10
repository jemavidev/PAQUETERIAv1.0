# RESUMEN: SISTEMA DE VALIDACIÓN Y CORRECCIÓN MANUAL

## ✅ ESTADO: BACKEND COMPLETADO - FRONTEND PENDIENTE

---

## 🎯 OBJETIVO CUMPLIDO

Crear un sistema para identificar y corregir manualmente campos problemáticos en facturas procesadas desde PDF (5% de casos edge).

---

## 📦 COMPONENTES IMPLEMENTADOS

### 1. ValidationService ✅ COMPLETADO

**Archivo**: `CODE/src/app/services/validation_service.py`

**Funcionalidades**:
- ✅ Valida 8 tipos de inconsistencias
- ✅ Retorna score de validación (0-100%)
- ✅ Lista de advertencias con severidad (critical, high, medium, low)
- ✅ Solo valida PDFs (XML siempre retorna 100%)
- ✅ Detecta campos NULL, valores incorrectos, inconsistencias

**Validaciones implementadas**:
1. Total a pagar (NULL o ≤ 0)
2. Subtotal (NULL)
3. IVA total (NULL)
4. Consistencia de totales (Total ≠ Subtotal + IVA)
5. Fecha de emisión (NULL, futura, o muy antigua)
6. Número de factura (NULL)
7. Productos (0 productos extraídos)
8. IVA en productos (productos sin IVA cuando deberían tenerlo)

---

### 2. Endpoints API ✅ COMPLETADO

**Archivo**: `CODE/src/app/routes/invoices_v2_routes.py`

#### GET `/api/v2/invoices/cufe/{cufe}/validate`
Valida una factura y retorna advertencias

**Respuesta**:
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
    }
  ],
  "validation_score": 60,
  "source": "PDF"
}
```

#### PATCH `/api/v2/invoices/cufe/{cufe}/correct`
Corrige campos problemáticos

**Request**:
```json
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

---

### 3. Schema actualizado ✅ COMPLETADO

**Cambios en `InvoiceResponse`**:
```python
class InvoiceResponse(BaseModel):
    # ... campos existentes ...
    validation_warnings: Optional[dict] = None  # ✅ NUEVO
```

**Nuevo schema `InvoiceCorrectionRequest`**:
```python
class InvoiceCorrectionRequest(BaseModel):
    dian_total_neto: Optional[float] = None
    dian_subtotal: Optional[float] = None
    dian_total_iva: Optional[float] = None
    fecha_emision: Optional[datetime] = None
    numero_factura: Optional[str] = None
    dian_emisor_razon_social: Optional[str] = None
    dian_emisor_nit: Optional[str] = None
```

---

### 4. Tracking de correcciones ✅ COMPLETADO

Las correcciones manuales se guardan en `dian_datos_raw.manual_corrections`:

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

## 🚧 COMPONENTES PENDIENTES (FRONTEND)

### 1. Badge de advertencia en lista 🚧

**Ubicación**: `CODE/src/templates/invoices_v2/cufe.html`

**Modificar función**: `renderCufeRow()`

**Implementación sugerida**:
```javascript
// Después de obtener la factura, validar si tiene advertencias
const hasWarnings = invoice.archivo_dian_s3_key && 
                    invoice.dian_datos_raw?.fuente === 'PDF' &&
                    (invoice.dian_total_neto === null || 
                     invoice.dian_subtotal === null ||
                     invoice.numero_factura === null);

const warningIcon = hasWarnings 
    ? '<button onclick="openValidationModal(\'' + invoice.cufe + '\')" class="ml-1 text-orange-500 hover:text-orange-700" title="Tiene advertencias - Click para corregir">⚠️</button>'
    : '';

const dianBadge = dianValidado
    ? `<span class="inline-flex items-center">
         <span class="inline-flex items-center justify-center px-2 py-0.5 rounded-full bg-green-500 text-white text-xs font-semibold min-w-[28px]">
           ${invoice.productos_count}
         </span>
         ${warningIcon}
       </span>`
    : '...';
```

---

### 2. Modal de corrección 🚧

**Agregar al final de `cufe.html`**:

```html
<!-- Modal de validación y corrección -->
<div id="validation-modal" class="hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
            <!-- Header -->
            <div class="flex items-center justify-between mb-4">
                <div>
                    <h3 class="text-lg font-bold text-gray-900">Corregir campos problemáticos</h3>
                    <p class="text-sm text-gray-600 mt-1">
                        Esta factura fue procesada desde PDF y tiene campos con posibles inconsistencias
                    </p>
                </div>
                <button onclick="closeValidationModal()" class="text-gray-400 hover:text-gray-600">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>

            <!-- Score de validación -->
            <div id="validation-score-container" class="mb-4">
                <!-- Se llena dinámicamente -->
            </div>

            <!-- Lista de advertencias -->
            <div id="validation-warnings-list" class="space-y-3 mb-6">
                <!-- Se llena dinámicamente -->
            </div>

            <!-- Botones -->
            <div class="flex justify-end gap-3 pt-4 border-t">
                <button onclick="closeValidationModal()" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium">
                    Cancelar
                </button>
                <button onclick="applyCorrections()" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center gap-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                    Aplicar correcciones
                </button>
            </div>
        </div>
    </div>
</div>
```

**JavaScript necesario**:

```javascript
let currentValidationCufe = null;
let currentValidationData = null;

async function openValidationModal(cufe) {
    currentValidationCufe = cufe;
    
    // Cargar datos de validación
    try {
        const response = await fetch(`/api/v2/invoices/cufe/${cufe}/validate`);
        const data = await response.json();
        currentValidationData = data;
        
        // Mostrar modal
        document.getElementById('validation-modal').classList.remove('hidden');
        
        // Renderizar score
        renderValidationScore(data);
        
        // Renderizar advertencias
        renderValidationWarnings(data.warnings);
        
    } catch (error) {
        console.error('Error cargando validación:', error);
        showToast('Error cargando datos de validación', 'error');
    }
}

function closeValidationModal() {
    document.getElementById('validation-modal').classList.add('hidden');
    currentValidationCufe = null;
    currentValidationData = null;
}

function renderValidationScore(data) {
    const score = data.validation_score || 0;
    const scoreColor = score >= 95 ? 'green' : score >= 80 ? 'yellow' : score >= 60 ? 'orange' : 'red';
    
    const html = `
        <div class="bg-${scoreColor}-50 border border-${scoreColor}-200 rounded-lg p-4">
            <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-gray-700">Score de validación</span>
                <span class="text-2xl font-bold text-${scoreColor}-600">${score}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="bg-${scoreColor}-500 h-2 rounded-full" style="width: ${score}%"></div>
            </div>
            <p class="text-xs text-gray-600 mt-2">
                ${data.valid_fields} de ${data.total_fields_checked} campos validados correctamente
            </p>
        </div>
    `;
    
    document.getElementById('validation-score-container').innerHTML = html;
}

function renderValidationWarnings(warnings) {
    const severityConfig = {
        critical: { color: 'red', icon: '⛔', label: 'CRÍTICO' },
        high: { color: 'orange', icon: '⚠️', label: 'ALTO' },
        medium: { color: 'yellow', icon: '⚡', label: 'MEDIO' },
        low: { color: 'blue', icon: 'ℹ️', label: 'BAJO' }
    };
    
    const html = warnings.map(warning => {
        const config = severityConfig[warning.severity] || severityConfig.low;
        
        return `
            <div class="border-l-4 border-${config.color}-500 bg-${config.color}-50 p-4 rounded-r-lg">
                <div class="flex items-start gap-3">
                    <span class="text-2xl">${config.icon}</span>
                    <div class="flex-1">
                        <div class="flex items-center justify-between mb-2">
                            <h4 class="font-semibold text-gray-900">${warning.field_label}</h4>
                            <span class="text-xs px-2 py-1 bg-${config.color}-100 text-${config.color}-800 rounded-full font-medium">
                                ${config.label}
                            </span>
                        </div>
                        <p class="text-sm text-gray-600 mb-3">${warning.message}</p>
                        ${renderWarningInput(warning)}
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    document.getElementById('validation-warnings-list').innerHTML = html;
}

function renderWarningInput(warning) {
    // Solo mostrar input para campos corregibles
    const editableFields = ['dian_total_neto', 'dian_subtotal', 'dian_total_iva', 'numero_factura', 'fecha_emision'];
    
    if (!editableFields.includes(warning.field)) {
        return `<p class="text-xs text-gray-500 italic">${warning.suggestion}</p>`;
    }
    
    const inputType = warning.field === 'fecha_emision' ? 'datetime-local' : 'number';
    const step = inputType === 'number' ? '0.01' : '';
    
    return `
        <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">${warning.suggestion}</label>
            <input type="${inputType}" 
                   ${step ? `step="${step}"` : ''}
                   id="correction-${warning.field}"
                   class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                   placeholder="${warning.current_value || ''}">
        </div>
    `;
}

async function applyCorrections() {
    if (!currentValidationCufe || !currentValidationData) {
        return;
    }
    
    // Recopilar correcciones
    const corrections = {};
    const editableFields = ['dian_total_neto', 'dian_subtotal', 'dian_total_iva', 'numero_factura', 'fecha_emision'];
    
    editableFields.forEach(field => {
        const input = document.getElementById(`correction-${field}`);
        if (input && input.value) {
            corrections[field] = input.value;
        }
    });
    
    if (Object.keys(corrections).length === 0) {
        showToast('No hay correcciones para aplicar', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`/api/v2/invoices/cufe/${currentValidationCufe}/correct`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(corrections)
        });
        
        if (response.ok) {
            const result = await response.json();
            showToast(`Correcciones aplicadas: ${result.fields_corrected.join(', ')}`, 'success');
            closeValidationModal();
            loadCufeRecords(); // Recargar lista
        } else {
            const error = await response.json();
            showToast(error.detail || 'Error aplicando correcciones', 'error');
        }
    } catch (error) {
        console.error('Error aplicando correcciones:', error);
        showToast('Error aplicando correcciones', 'error');
    }
}
```

---

### 3. Indicadores en columnas 🚧

**Modificar `renderCufeRow()` para agregar iconos en columnas problemáticas**:

```javascript
// Para el total
const totalHasWarning = invoice.dian_total_neto === null;
const totalIcon = totalHasWarning ? '<span class="text-red-500 mr-1" title="Total no extraído">⛔</span>' : '';
const total = dianValidado 
    ? `${totalIcon}${formatCurrency(invoice.dian_total_neto || 0)}` 
    : '<span class="text-gray-400 italic text-xs">-</span>';

// Para la fecha
const fechaHasWarning = invoice.fecha_emision && new Date(invoice.fecha_emision) > new Date();
const fechaIcon = fechaHasWarning ? '<span class="text-orange-500 mr-1" title="Fecha posiblemente incorrecta">⚠️</span>' : '';
const fecha = dianValidado 
    ? `${fechaIcon}${formatDate(invoice.fecha_emision)}` 
    : '<span class="text-gray-400 italic text-xs">-</span>';

// Para el número
const numeroHasWarning = !invoice.numero_factura;
const numeroIcon = numeroHasWarning ? '<span class="text-red-500 mr-1" title="Número no extraído">⛔</span>' : '';
const numero = dianValidado 
    ? `${numeroIcon}${invoice.numero_factura || '-'}` 
    : '<span class="text-gray-400 italic text-xs">-</span>';
```

---

## 📊 CAMPOS CORREGIBLES

### Implementados en backend:
- ✅ `dian_total_neto` - Total a pagar
- ✅ `dian_subtotal` - Subtotal
- ✅ `dian_total_iva` - Total IVA
- ✅ `fecha_emision` - Fecha de emisión
- ✅ `numero_factura` - Número de factura
- ✅ `dian_emisor_razon_social` - Nombre proveedor
- ✅ `dian_emisor_nit` - NIT proveedor

### No corregibles (requieren reprocesamiento):
- ❌ Productos completos
- ❌ IVA por producto individual

---

## 🧪 TESTING

### Test Backend (con curl):

```bash
# 1. Validar factura
curl http://localhost:8000/api/v2/invoices/cufe/{cufe}/validate

# 2. Corregir campos
curl -X PATCH http://localhost:8000/api/v2/invoices/cufe/{cufe}/correct \
  -H "Content-Type: application/json" \
  -d '{
    "dian_total_neto": 1234567.89,
    "dian_subtotal": 1037368.98,
    "dian_total_iva": 197198.91
  }'

# 3. Verificar correcciones
curl http://localhost:8000/api/v2/invoices/cufe/{cufe}/full | jq '.dian_datos_raw.manual_corrections'
```

### Test Frontend (pendiente):
1. Abrir navegador en http://localhost:8000/invoices/cufe
2. Buscar factura con icono ⚠️
3. Click en icono para abrir modal
4. Ingresar correcciones
5. Verificar que se guardan correctamente

---

## 📁 ARCHIVOS CREADOS/MODIFICADOS

### Creados:
- ✅ `CODE/src/app/services/validation_service.py` - Servicio de validación
- ✅ `CODE/test_validation_system.py` - Test del servicio
- ✅ `SISTEMA_VALIDACION_CORRECCION_MANUAL.md` - Documentación completa
- ✅ `test_validation_ui_demo.html` - Demo visual de componentes UI
- ✅ `RESUMEN_IMPLEMENTACION_VALIDACION.md` - Este archivo

### Modificados:
- ✅ `CODE/src/app/routes/invoices_v2_routes.py` - Endpoints y schemas
  - Agregado `validation_warnings` a `InvoiceResponse`
  - Creado `InvoiceCorrectionRequest`
  - Agregado endpoint `/cufe/{cufe}/validate`
  - Agregado endpoint `/cufe/{cufe}/correct`

### Pendientes de modificar:
- 🚧 `CODE/src/templates/invoices_v2/cufe.html` - UI frontend
  - Agregar badge de advertencia
  - Agregar modal de corrección
  - Agregar indicadores en columnas

---

## 🎯 PRÓXIMOS PASOS

### Paso 1: Implementar badge de advertencia
1. Modificar `renderCufeRow()` en `cufe.html`
2. Agregar lógica para detectar advertencias
3. Agregar icono ⚠️ clickeable

### Paso 2: Implementar modal de corrección
1. Agregar HTML del modal al final de `cufe.html`
2. Agregar funciones JavaScript:
   - `openValidationModal(cufe)`
   - `closeValidationModal()`
   - `renderValidationScore(data)`
   - `renderValidationWarnings(warnings)`
   - `applyCorrections()`

### Paso 3: Agregar indicadores en columnas
1. Modificar `renderCufeRow()` para agregar iconos
2. Agregar tooltips explicativos
3. Agregar colores para valores problemáticos

### Paso 4: Testing completo
1. Probar con facturas PDF reales
2. Verificar que las correcciones se guardan
3. Verificar que el icono desaparece después de corregir
4. Probar con diferentes tipos de advertencias

---

## ✅ CONCLUSIÓN

### Completado (Backend):
- ✅ ValidationService con 8 validaciones
- ✅ 2 endpoints API (validate + correct)
- ✅ Schema actualizado
- ✅ Tracking de correcciones
- ✅ Documentación completa

### Pendiente (Frontend):
- 🚧 Badge de advertencia en lista
- 🚧 Modal de corrección
- 🚧 Indicadores en columnas
- 🚧 Testing en navegador

### Impacto esperado:
- **Antes**: 95% de precisión automática, 5% sin solución
- **Después**: 95% automático + 5% corrección manual = **100% de precisión**

---

**Fecha**: 10 de Febrero de 2026  
**Backend**: ✅ COMPLETADO  
**Frontend**: 🚧 PENDIENTE  
**Precisión objetivo**: 100%
