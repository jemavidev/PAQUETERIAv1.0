# ✅ Funcionalidad: Actualizar Facturas Existentes (No Duplicar)

## 🎯 Objetivo

**NUNCA crear registros duplicados**. Si un CUFE ya existe, siempre intentar actualizar el registro existente en lugar de crear uno nuevo.

## 🔧 Comportamiento

### Lógica Principal

```
Si CUFE existe en BD:
    Si overwrite = False:
        ❌ Rechazar: "Ya existe (activa overwrite para actualizar)"
    
    Si overwrite = True:
        Si estado = "completo":
            ❌ Rechazar: "Factura completa (protegida)"
        Sino:
            ✅ ACTUALIZAR registro existente (NO crear nuevo)

Si CUFE NO existe:
    ✅ CREAR nuevo registro
```

### Diferencia Clave

**ANTES** (incorrecto):
```python
if existing and overwrite:
    # Actualizar
else:
    # Crear nuevo ← PROBLEMA: podría crear duplicados
```

**AHORA** (correcto):
```python
if existing:
    if overwrite and estado != 'completo':
        # ACTUALIZAR registro existente
    else:
        # RECHAZAR (no crear duplicado)
else:
    # CREAR nuevo (solo si no existe)
```

## 📋 Reglas de Actualización

### ✅ SE PUEDE Actualizar

| Estado | ¿Se puede actualizar? | Acción |
|--------|----------------------|--------|
| 🟡 `pendiente_dian` | ✅ SÍ | Actualiza datos del proveedor |
| 🔴 `error` | ✅ SÍ | Actualiza y corrige datos |
| ⚪ `sin_dian` | ✅ SÍ | Actualiza datos del proveedor |
| 🟠 `sin_cufe` | ✅ SÍ | Actualiza datos |

### ❌ NO SE PUEDE Actualizar

| Estado | ¿Se puede actualizar? | Acción |
|--------|----------------------|--------|
| 🟢 `completo` | ❌ NO | Rechaza: "Factura completa (protegida)" |

## 🎨 Interfaz de Usuario

### Modal de Carga

```
┌─────────────────────────────────────────────┐
│ Cargar Facturas de Proveedor               │
├─────────────────────────────────────────────┤
│                                             │
│ Archivos PDF (múltiples)                   │
│ [Seleccionar archivos...]                  │
│                                             │
│ ┌─────────────────────────────────────────┐│
│ │ ☑ Sobreescribir facturas existentes    ││
│ │                                         ││
│ │ Si una factura con el mismo CUFE ya     ││
│ │ existe y NO está en estado "Completo",  ││
│ │ se ACTUALIZARÁN sus datos (no se crea   ││
│ │ un registro duplicado).                 ││
│ │                                         ││
│ │ ⚠️ Las facturas en estado "Completo"    ││
│ │ NO se actualizarán (protegidas).        ││
│ └─────────────────────────────────────────┘│
│                                             │
│ [Cancelar]  [Cargar Facturas]              │
└─────────────────────────────────────────────┘
```

### Mensajes de Resultado

**Con checkbox DESACTIVADO** (comportamiento por defecto):
```
✓ factura1.pdf (nueva)
⚠ factura2.pdf: Ya existe (activa "Sobreescribir" para actualizar)
✓ factura3.pdf (nueva)
```

**Con checkbox ACTIVADO**:
```
✓ factura1.pdf (nueva)
✓ factura2.pdf (actualizada - NO duplicada)
✗ factura3.pdf: No se puede actualizar: factura COMPLETA
✓ factura4.pdf (actualizada - NO duplicada)
```

## 🔄 Flujos de Uso

### Caso 1: Cargar Facturas Nuevas (Normal)

```
1. Usuario selecciona PDFs nuevos
2. Checkbox "Sobreescribir" DESACTIVADO
3. Click en "Cargar Facturas"
4. Sistema:
   - Crea facturas nuevas ✅
   - Rechaza duplicados ❌ (no crea registros duplicados)
```

### Caso 2: Actualizar Facturas Existentes

```
1. Usuario selecciona PDFs (algunos ya existen)
2. Checkbox "Sobreescribir" ACTIVADO ✓
3. Click en "Cargar Facturas"
4. Sistema:
   - Crea facturas nuevas ✅
   - ACTUALIZA facturas existentes ✅ (NO crea duplicados)
   - Rechaza facturas completas ❌ (protegidas)
```

### Caso 3: Carga Masiva con Duplicados

```
Escenario: 100 PDFs, 30 ya están en BD

Con checkbox DESACTIVADO:
- 70 nuevas creadas ✅
- 30 rechazadas ⚠️ (ya existen)
- 0 duplicados ✅

Con checkbox ACTIVADO:
- 70 nuevas creadas ✅
- 30 actualizadas ✅ (NO duplicadas)
- 0 duplicados ✅
```

## 📊 Qué se Actualiza

Cuando se actualiza una factura existente:

### ✅ Datos que SE actualizan:
- Proveedor (nombre y NIT) - solo si el nuevo valor no es null
- Fecha de emisión - solo si el nuevo valor no es null
- Número de factura - solo si el nuevo valor no es null
- Total de factura - solo si el nuevo valor no es null
- Archivo PDF en S3 (se elimina el antiguo y se sube el nuevo)
- Datos raw del proveedor
- Timestamp de actualización

### ❌ Datos que NO se actualizan:
- CUFE (se usa para identificar la factura)
- Estado (se mantiene el actual)
- Datos DIAN (se mantienen si ya existen)
- Productos (se mantienen si ya existen)
- ID de la factura (mismo registro)

### 🔒 Protección de Datos

```python
# Solo actualiza si el nuevo valor no es null
existing.proveedor_nombre = data.get('proveedor_nombre') or existing.proveedor_nombre
existing.proveedor_nit = data.get('proveedor_nit') or existing.proveedor_nit
existing.fecha_emision = data.get('fecha_emision') or existing.fecha_emision
existing.numero_factura = data.get('numero_factura') or existing.numero_factura
existing.total_factura = data.get('total_factura') or existing.total_factura
```

Esto significa: **Si el nuevo PDF no tiene un dato, se mantiene el valor anterior**.

## 🛡️ Protecciones Implementadas

### 1. NO Crear Duplicados
```python
if existing:
    # NUNCA crear nuevo registro
    # Solo actualizar o rechazar
    if overwrite and estado != 'completo':
        # Actualizar registro existente
    else:
        # Rechazar (no crear duplicado)
```

### 2. Protección de Facturas Completas
```python
if existing.estado == 'completo':
    raise ValueError('No se puede actualizar: factura COMPLETA')
```

### 3. Protección de Datos Existentes
```python
# Mantener datos anteriores si los nuevos son null
existing.campo = nuevo_valor or existing.campo
```

### 4. Eliminación de Archivo Antiguo
```python
if existing.archivo_proveedor_s3_key:
    self.s3_service.delete_file(existing.archivo_proveedor_s3_key)
```

## 💡 Casos de Uso Reales

### Caso 1: Evitar Duplicados Accidentales
**Problema**: Usuario carga el mismo PDF dos veces por error.

**Solución**:
- Sin checkbox: Rechaza el segundo (no crea duplicado)
- Con checkbox: Actualiza el existente (no crea duplicado)

### Caso 2: Mejorar Datos Incompletos
**Problema**: Primera carga extrajo mal el proveedor (quedó null).

**Solución**:
1. Activa "Sobreescribir"
2. Carga PDF de mejor calidad
3. Sistema actualiza solo los campos que mejoraron
4. Mantiene los datos que ya estaban bien

### Caso 3: Carga Masiva Segura
**Problema**: Tienes 100 PDFs y no sabes cuáles ya están cargados.

**Solución**:
1. Activa "Sobreescribir"
2. Carga todos los 100 PDFs
3. Sistema:
   - Crea los nuevos
   - Actualiza los existentes
   - **NUNCA crea duplicados**

## ⚠️ Advertencias Importantes

### Para el Usuario:
- ⚠️ **NO se crean duplicados**: Si el CUFE existe, se actualiza (no se crea nuevo)
- ⚠️ **Facturas completas protegidas**: No se pueden actualizar
- ⚠️ **Datos se preservan**: Si el nuevo PDF no tiene un dato, se mantiene el anterior
- ⚠️ **Archivo se reemplaza**: El PDF antiguo se elimina y se sube el nuevo

### Para el Desarrollador:
- ⚠️ **Mismo registro**: Se actualiza el registro existente (mismo ID)
- ⚠️ **Transacciones**: La actualización es atómica (todo o nada)
- ⚠️ **Logs**: Se registra cada actualización
- ⚠️ **S3**: Se elimina el archivo antiguo antes de subir el nuevo

## 🧪 Testing

### Test 1: No Crear Duplicados
```
1. Cargar factura con CUFE "ABC123"
2. Intentar cargar misma factura (sin checkbox)
3. Verificar:
   - Se rechaza ✅
   - NO se crea duplicado ✅
   - Solo hay 1 registro en BD ✅
```

### Test 2: Actualizar Sin Duplicar
```
1. Cargar factura con CUFE "ABC123"
2. Activar checkbox "Sobreescribir"
3. Cargar misma factura con datos diferentes
4. Verificar:
   - Se actualiza ✅
   - NO se crea duplicado ✅
   - Solo hay 1 registro en BD ✅
   - Datos se actualizaron ✅
```

### Test 3: Protección de Completas
```
1. Cargar factura (estado: completo)
2. Activar checkbox "Sobreescribir"
3. Intentar cargar misma factura
4. Verificar:
   - Se rechaza ✅
   - NO se actualiza ✅
   - NO se crea duplicado ✅
```

## 📝 Logs del Sistema

Cuando se actualiza una factura (NO se crea duplicado):

```
🔄 Actualizando factura existente: 8cf8ec5366fa9eac... (estado: pendiente_dian)
🗑️ Archivo antiguo eliminado de S3: invoices/provider/8cf8ec5366fa9eac....pdf
✅ Nuevo archivo subido a S3: invoices/provider/8cf8ec5366fa9eac....pdf
✅ Factura actualizada: 8cf8ec5366fa9eac... - PAPYRUS SOLUCIONES INTEGRALES SAS
```

## ���� Resumen

| Característica | Valor |
|----------------|-------|
| **Comportamiento** | NUNCA crear duplicados |
| **Si CUFE existe** | Actualizar o rechazar (NO crear nuevo) |
| **Si CUFE NO existe** | Crear nuevo registro |
| **Protección** | Facturas "completo" NO se actualizan |
| **Datos** | Se preservan si el nuevo valor es null |
| **Archivo** | Se reemplaza en S3 |

**Garantía**: El sistema NUNCA creará registros duplicados con el mismo CUFE. ✅

## 🔧 Implementación

### Backend

**Archivo**: `CODE/src/app/routes/invoices_v2_routes.py`

Nuevo parámetro en el endpoint de carga:

```python
@router.post("/facturas/upload")
async def upload_provider_invoice(
    file: UploadFile = File(...),
    allow_without_cufe: bool = Query(default=True),
    overwrite: bool = Query(default=False),  # ← NUEVO
    db: Session = Depends(get_db)
):
```

**Archivo**: `CODE/src/app/services/invoice_v2_service.py`

Lógica de sobreescritura:

```python
def create_invoice_from_provider_pdf(
    self, 
    pdf_path: str, 
    file_obj=None, 
    allow_without_cufe: bool = False, 
    overwrite: bool = False  # ← NUEVO
) -> InvoiceV2:
    # ... extracción de datos ...
    
    existing = self.db.query(InvoiceV2).filter_by(cufe=cufe).first()
    if existing:
        if overwrite:
            # ✅ Verificar que NO esté completa
            if existing.estado == 'completo':
                raise ValueError('No se puede sobreescribir: factura COMPLETA')
            
            # ✅ Actualizar datos
            existing.proveedor_nombre = data.get('proveedor_nombre')
            existing.proveedor_nit = data.get('proveedor_nit')
            existing.fecha_emision = data.get('fecha_emision')
            existing.numero_factura = data.get('numero_factura')
            existing.total_factura = data.get('total_factura')
            
            # ✅ Eliminar archivo antiguo de S3
            # ✅ Subir nuevo archivo a S3
            
            return existing
        else:
            raise ValueError('Ya existe una factura con este CUFE')
```

### Frontend

**Archivo**: `CODE/src/templates/invoices_v2/facturas.html`

Checkbox en el modal de carga:

```html
<div class="mb-4 bg-blue-50 border-l-4 border-blue-400 p-4 rounded">
    <div class="flex items-start">
        <input id="overwrite-checkbox" type="checkbox">
        <label>Sobreescribir facturas existentes</label>
        <p>Si una factura con el mismo CUFE ya existe y NO está en estado "Completo", 
           se actualizarán sus datos.</p>
        <p>⚠️ Las facturas en estado "Completo" NO se sobreescribirán.</p>
    </div>
</div>
```

JavaScript actualizado:

```javascript
const overwrite = document.getElementById('overwrite-checkbox').checked;
const url = `/api/v2/invoices/facturas/upload?overwrite=${overwrite}`;

const response = await fetch(url, {
    method: 'POST',
    body: formData
});
```

## 📋 Reglas de Sobreescritura

### ✅ SE PUEDE Sobreescribir

| Estado | ¿Se puede sobreescribir? | Razón |
|--------|--------------------------|-------|
| 🟡 `pendiente_dian` | ✅ SÍ | Aún no tiene documento DIAN |
| 🔴 `error` | ✅ SÍ | Necesita corrección |
| ⚪ `sin_dian` | ✅ SÍ | No tiene documento DIAN |
| 🟠 `sin_cufe` | ✅ SÍ | Tiene CUFE temporal |

### ❌ NO SE PUEDE Sobreescribir

| Estado | ¿Se puede sobreescribir? | Razón |
|--------|--------------------------|-------|
| 🟢 `completo` | ❌ NO | Ya tiene TODA la información (protegida) |

## 🎨 Interfaz de Usuario

### Modal de Carga

```
┌─────────────────────────────────────────────┐
│ Cargar Facturas de Proveedor               │
├─────────────────────────────────────────────┤
│                                             │
│ Archivos PDF (múltiples)                   │
│ [Seleccionar archivos...]                  │
│                                             │
│ ┌─────────────────────────────────────────┐│
│ │ ☑ Sobreescribir facturas existentes    ││
│ │                                         ││
│ │ Si una factura con el mismo CUFE ya     ││
│ │ existe y NO está en estado "Completo",  ││
│ │ se actualizarán sus datos.              ││
│ │                                         ││
│ │ ⚠️ Las facturas en estado "Completo"    ││
│ │ NO se sobreescribirán (protegidas).     ││
│ └─────────────────────────────────────────┘│
│                                             │
│ [Cancelar]  [Cargar Facturas]              │
└─────────────────────────────────────────────┘
```

### Mensajes de Resultado

**Con checkbox DESACTIVADO** (comportamiento por defecto):
```
✓ factura1.pdf
✗ factura2.pdf: Ya existe una factura con este CUFE
⚠ factura3.pdf: Ya existe (activa "Sobreescribir" para actualizar)
```

**Con checkbox ACTIVADO**:
```
✓ factura1.pdf (nueva)
✓ factura2.pdf (actualizada)
✗ factura3.pdf: No se puede sobreescribir: factura COMPLETA
```

## 🔄 Flujos de Uso

### Caso 1: Cargar Facturas Nuevas (Normal)

```
1. Usuario selecciona PDFs
2. Checkbox "Sobreescribir" DESACTIVADO
3. Click en "Cargar Facturas"
4. Sistema carga solo facturas nuevas
5. Si encuentra duplicados, muestra error
```

### Caso 2: Actualizar Facturas Existentes

```
1. Usuario selecciona PDFs (algunos ya existen)
2. Checkbox "Sobreescribir" ACTIVADO ✓
3. Click en "Cargar Facturas"
4. Sistema:
   - Carga facturas nuevas
   - Actualiza facturas existentes (si NO están completas)
   - Rechaza facturas completas (protegidas)
```

### Caso 3: Corregir Factura con Error

```
1. Factura tiene estado "error" 🔴
2. Usuario descarga el PDF correcto
3. Activa checkbox "Sobreescribir" ✓
4. Carga el PDF corregido
5. Sistema actualiza la factura con datos correctos
6. Estado cambia a "pendiente_dian" 🟡
```

## 📊 Qué se Actualiza

Cuando se sobreescribe una factura, se actualizan:

### ✅ Datos que SE actualizan:
- Proveedor (nombre y NIT)
- Fecha de emisión
- Número de factura
- Total de factura
- Archivo PDF en S3 (se elimina el antiguo y se sube el nuevo)
- Datos raw del proveedor
- Timestamp de actualización

### ❌ Datos que NO se actualizan:
- CUFE (se usa para identificar la factura)
- Datos DIAN (solo si ya existen)
- Productos (solo si ya existen)
- Estado "completo" (protegido)

## 🛡️ Protecciones Implementadas

### 1. Protección de Facturas Completas
```python
if existing.estado == 'completo':
    raise ValueError('No se puede sobreescribir: factura COMPLETA')
```

### 2. Eliminación de Archivo Antiguo
```python
if existing.archivo_proveedor_s3_key:
    self.s3_service.delete_file(existing.archivo_proveedor_s3_key)
```

### 3. Validación de CUFE
```python
# Solo se sobreescribe si el CUFE coincide exactamente
existing = self.db.query(InvoiceV2).filter_by(cufe=cufe).first()
```

## 💡 Casos de Uso Reales

### Caso 1: Factura con Datos Incorrectos
**Problema**: Cargaste una factura pero el proveedor o total están mal.

**Solución**:
1. Activa "Sobreescribir"
2. Carga el PDF correcto
3. Los datos se actualizan automáticamente

### Caso 2: Factura con PDF de Mala Calidad
**Problema**: El PDF original no se lee bien (OCR malo).

**Solución**:
1. Consigue un PDF de mejor calidad
2. Activa "Sobreescribir"
3. Carga el nuevo PDF
4. Se extraen mejor los datos

### Caso 3: Carga Masiva con Duplicados
**Problema**: Tienes 100 PDFs y algunos ya están cargados.

**Solución**:
1. Selecciona todos los PDFs
2. Activa "Sobreescribir"
3. Carga todos
4. Sistema:
   - Carga los nuevos
   - Actualiza los existentes (si no están completos)
   - Ignora los completos

## ⚠️ Advertencias

### Para el Usuario:
- ⚠️ **Facturas completas están protegidas**: No se pueden sobreescribir
- ⚠️ **El archivo antiguo se elimina**: Se reemplaza por el nuevo
- ⚠️ **Los datos DIAN se mantienen**: Si ya existen, no se pierden

### Para el Desarrollador:
- ⚠️ **Transacciones**: La actualización es atómica (todo o nada)
- ⚠️ **Logs**: Se registra cada sobreescritura
- ⚠️ **S3**: Se elimina el archivo antiguo antes de subir el nuevo

## 🧪 Testing

### Test 1: Sobreescribir Factura Pendiente
```
1. Cargar factura (estado: pendiente_dian)
2. Activar "Sobreescribir"
3. Cargar mismo PDF con datos diferentes
4. Verificar que se actualizó
```

### Test 2: Protección de Factura Completa
```
1. Cargar factura (estado: completo)
2. Activar "Sobreescribir"
3. Intentar cargar mismo PDF
4. Verificar que se rechaza con error
```

### Test 3: Carga Masiva Mixta
```
1. Preparar 10 PDFs (5 nuevos, 5 existentes)
2. Activar "Sobreescribir"
3. Cargar todos
4. Verificar:
   - 5 nuevos creados
   - 5 existentes actualizados (si no están completos)
```

## 📝 Logs del Sistema

Cuando se sobreescribe una factura:

```
🔄 Sobreescribiendo factura existente: 8cf8ec5366fa9eac... (estado: pendiente_dian)
🗑️ Archivo antiguo eliminado de S3: invoices/provider/8cf8ec5366fa9eac....pdf
✅ Nuevo archivo subido a S3: invoices/provider/8cf8ec5366fa9eac....pdf
✅ Factura sobreescrita: 8cf8ec5366fa9eac... - PAPYRUS SOLUCIONES INTEGRALES SAS
```

## 🎯 Resumen

| Característica | Valor |
|----------------|-------|
| **Parámetro** | `overwrite=true/false` |
| **Por defecto** | `false` (no sobreescribe) |
| **Protección** | Facturas "completo" NO se sobreescriben |
| **Actualiza** | Proveedor, Fecha, Número, Total, PDF |
| **Mantiene** | CUFE, Datos DIAN, Productos |
| **UI** | Checkbox en modal de carga |

La funcionalidad está lista para usar! 🎉
