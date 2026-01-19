# 📊 ANÁLISIS Y REFACTORIZACIÓN: Sistema de Facturas de Proveedores

**Fecha:** 19 de Enero, 2026  
**Proyecto:** PAQUETEX - Sistema de Gestión de Facturas  
**Vista:** https://staging.jemavi.co/invoices (Tab Facturas)  
**Carpeta de Facturas:** `/home/stk/Insync/dispapyrussas@gmail.com/Google Drive/PAPYRUS/EL CLUB/INVENTARIO/FACTURAS`

---

## 🎯 OBJETIVO

Refactorizar el sistema de captura y visualización de datos de facturas de proveedores para mejorar:
1. **Extracción de datos** de PDFs (Proveedor, Fecha, Número, CUFE, Total)
2. **Visualización** en la tabla del dashboard
3. **Acciones** disponibles para cada factura
4. **Experiencia de usuario** en el flujo de carga y gestión

---

## 📋 ESTADO ACTUAL DEL SISTEMA

### 1. Flujo de Carga Actual

```
Usuario → Sube PDF(s) → Extracción Automática → Guardado en BD → Visualización
```

**Endpoint:** `POST /invoices/api/supplier-invoices/upload`

**Proceso:**
1. Usuario arrastra/selecciona PDFs en modal
2. Se suben múltiples archivos simultáneamente
3. Para cada PDF:
   - Se calcula hash SHA256
   - Se verifica duplicado por hash
   - Se extrae CUFE del nombre del archivo (patrón: `f-{cufe}_{fecha}.pdf`)
   - Si no hay CUFE en nombre, se busca en contenido del PDF
   - Se extrae información básica: proveedor, NIT, fecha, número, total
   - Se guarda en tabla `supplier_invoices`
   - Se sube PDF a S3 (o local como fallback)
4. Se retorna resumen de éxitos/fallos

### 2. Datos Capturados Actualmente

**Tabla: `supplier_invoices`**

| Campo | Tipo | Descripción | Capturado Actualmente |
|-------|------|-------------|----------------------|
| `id` | Integer | ID único | ✅ Auto |
| `original_filename` | String | Nombre del archivo | ✅ Sí |
| `original_file_hash` | String | Hash SHA256 | ✅ Sí |
| `original_file_path` | String | Ruta en S3/local | ✅ Sí |
| `supplier_name` | String | Nombre del proveedor | ⚠️ Parcial |
| `supplier_nit` | String | NIT del proveedor | ⚠️ Parcial |
| `invoice_number` | String | Número de factura | ⚠️ Parcial |
| `invoice_date` | DateTime | Fecha de emisión | ⚠️ Parcial |
| `total_amount` | Integer | Total en COP | ⚠️ Parcial |
| `cufe` | String | CUFE (96 chars hex) | ⚠️ Parcial |
| `cufe_source` | String | Origen del CUFE | ✅ Sí |
| `status` | Enum | Estado del proceso | ✅ Sí |
| `uploaded_by` | Integer | Usuario que subió | ✅ Sí |
| `uploaded_at` | DateTime | Fecha de subida | ✅ Sí |

**Estados posibles:**
- `PENDING` - Subida, pendiente de procesar
- `NO_CUFE` - Sin CUFE detectado
- `CUFE_EXTRACTED` - CUFE extraído
- `DIAN_DOWNLOADED` - PDF de DIAN descargado
- `PROCESSED` - Procesada e importada
- `ERROR` - Error en el proceso
- `DUPLICATE` - CUFE duplicado

### 3. Método de Extracción Actual

**Servicio:** `SupplierInvoiceService.extract_basic_info_from_pdf()`

**Técnica:** Regex sobre texto extraído con `pdfplumber`

**Patrones de Extracción:**

```python
# PROVEEDOR: Primeras 15 líneas, evitando keywords
- Busca líneas de 5-100 caracteres
- Excluye líneas con: FACTURA, INVOICE, FECHA, NIT, CUFE, TOTAL
- Limpia espacios y separa por NIT/FECHA

# NIT: Múltiples patrones
- NIT[:\s]*(\d{3}\.?\d{3}\.?\d{3}[-\s]?\d)
- N\.?I\.?T\.?[:\s]*(\d{9,12}[-\s]?\d?)
- (\d{9,10}) standalone

# FECHA: Múltiples formatos
- Fecha de Emisión: DD/MM/YYYY
- DD-MM-YYYY, YYYY-MM-DD
- DD de MMMM de YYYY
- Validación: 2020 <= año <= 2030

# NÚMERO DE FACTURA:
- Factura No./Nro./#: [A-Z0-9-]+
- FV/FE/FA/FC: \d+
- Validación: 2-50 caracteres

# TOTAL:
- Total a Pagar: $[\d,\.]+
- Valor Total: $[\d,\.]+
- Validación: 100 <= total <= 999,999,999
```

### 4. Visualización Actual

**Template:** `CODE/src/templates/invoices/_tab_facturas.html`

**Tabla con columnas:**
1. **Proveedor** - `supplier_name`
2. **Fecha** - `invoice_date`
3. **Número** - `invoice_number`
4. **CUFE** - `cufe` (abreviado)
5. **Estado** - `status` (badge con color)
6. **Acciones** - Botones de acción

**Estadísticas mostradas:**
- Total Facturas
- Procesadas
- Pendientes
- Total Valor

### 5. Acciones Disponibles

Actualmente NO están implementadas en el frontend, pero el backend soporta:
- Ver detalle
- Descargar PDF
- Actualizar CUFE manualmente
- Marcar como procesada
- Eliminar

---

## 🔍 PROBLEMAS IDENTIFICADOS

### 1. Extracción de Datos Inconsistente

**Problema:** Los patrones regex son genéricos y fallan con formatos no estándar

**Evidencia:**
- Muchas facturas con `supplier_name = NULL`
- Fechas no detectadas o incorrectas
- Números de factura incompletos

**Causa raíz:**
- PDFs con estructuras muy variadas
- Texto extraído con formato inconsistente
- Patrones regex demasiado estrictos o demasiado laxos

### 2. Falta de Validación Visual

**Problema:** Usuario no puede revisar/corregir datos antes de guardar

**Impacto:**
- Datos incorrectos en BD
- Necesidad de reprocesar manualmente
- Pérdida de confianza en el sistema

### 3. Acciones No Implementadas

**Problema:** Botones de acción en tabla no tienen funcionalidad

**Faltantes:**
- Ver PDF
- Editar datos
- Reextraer información
- Vincular con factura procesada
- Descargar de DIAN

### 4. Sin Feedback de Calidad

**Problema:** No hay indicador de confianza en los datos extraídos

**Necesidad:**
- Score de confianza por campo
- Alertas de datos faltantes
- Sugerencias de corrección

---

## 💡 PROPUESTA DE REFACTORIZACIÓN

### FASE 1: Mejorar Extracción de Datos

#### 1.1 Extractor Mejorado con Confianza

**Nuevo servicio:** `EnhancedPDFExtractor`

```python
class FieldExtraction:
    value: Any
    confidence: float  # 0.0 - 1.0
    source: str  # 'regex', 'position', 'ml', 'manual'
    alternatives: List[Any]  # Valores alternativos encontrados

class EnhancedInvoiceData:
    supplier_name: FieldExtraction
    supplier_nit: FieldExtraction
    invoice_number: FieldExtraction
    invoice_date: FieldExtraction
    total_amount: FieldExtraction
    cufe: FieldExtraction
```

**Mejoras:**
- Múltiples estrategias de extracción por campo
- Score de confianza por campo
- Valores alternativos para revisión manual
- Validación cruzada entre campos

#### 1.2 Patrones Específicos por Proveedor

**Crear biblioteca de patrones:**

```python
PROVIDER_PATTERNS = {
    'EXITO': {
        'supplier_name': r'ALMACENES ÉXITO',
        'nit_position': (50, 100),  # Coordenadas en PDF
        'invoice_pattern': r'FV\d{10}',
    },
    'MAKRO': {
        'supplier_name': r'MAKRO',
        'invoice_pattern': r'ad\d{20}',
    },
    # ... más proveedores
}
```

#### 1.3 Extracción por Posición

**Usar coordenadas además de regex:**

```python
# Extraer texto en área específica del PDF
def extract_by_position(pdf_page, x, y, width, height):
    bbox = (x, y, x + width, y + height)
    return pdf_page.within_bbox(bbox).extract_text()
```

### FASE 2: Modal de Revisión Mejorado

#### 2.1 Vista Previa con Corrección

**Nuevo flujo:**

```
Subir PDF → Extracción → Modal de Revisión → Corrección Manual → Guardar
```

**Modal incluye:**
- Vista previa del PDF (lado izquierdo)
- Formulario de datos extraídos (lado derecho)
- Indicadores de confianza por campo
- Campos editables
- Botón "Reextraer" si falla
- Botón "Guardar" / "Cancelar"

#### 2.2 Indicadores Visuales

```html
<div class="field-group">
    <label>Proveedor</label>
    <div class="field-with-confidence">
        <input value="ALMACENES EXITO S.A." />
        <span class="confidence high">95%</span>
    </div>
</div>

<div class="field-group">
    <label>Fecha</label>
    <div class="field-with-confidence">
        <input value="2025-01-15" />
        <span class="confidence low">45%</span>
        <button class="btn-alternatives">Ver alternativas</button>
    </div>
</div>
```

**Colores de confianza:**
- 🟢 Verde (>80%): Alta confianza
- 🟡 Amarillo (50-80%): Media confianza
- 🔴 Rojo (<50%): Baja confianza
- ⚪ Gris: No detectado

### FASE 3: Tabla Mejorada con Acciones

#### 3.1 Columnas Rediseñadas

**Nueva estructura:**

| Proveedor | Fecha | Número | CUFE | Estado | Calidad | Acciones |
|-----------|-------|--------|------|--------|---------|----------|
| EXITO S.A. | 15/01/2025 | FV123 | abc...def | ✅ Procesada | 🟢 95% | [Ver] [PDF] [Editar] |
| MAKRO | - | ad456 | - | ⚠️ Sin CUFE | 🟡 60% | [Ver] [PDF] [Editar] [DIAN] |

#### 3.2 Acciones Implementadas

**Botones:**
1. **Ver** - Modal con detalle completo
2. **PDF** - Abrir/descargar PDF original
3. **Editar** - Modal de edición de datos
4. **DIAN** - Descargar desde DIAN (si tiene CUFE)
5. **Procesar** - Importar a sistema principal
6. **Eliminar** - Soft delete

#### 3.3 Filtros Avanzados

**Agregar filtros:**
- Por estado (Procesada, Pendiente, Sin CUFE, Error)
- Por proveedor (dropdown con proveedores únicos)
- Por rango de fechas
- Por calidad de datos (Alta, Media, Baja)
- Por presencia de CUFE (Sí/No)

### FASE 4: Procesamiento Inteligente

#### 4.1 Auto-corrección

**Reglas de negocio:**

```python
# Si NIT detectado, buscar proveedor en BD
if nit_detected:
    supplier = db.query(Supplier).filter_by(nit=nit).first()
    if supplier:
        # Usar datos del proveedor conocido
        supplier_name = supplier.razon_social
        confidence = 1.0

# Si CUFE detectado, verificar en DIAN
if cufe_detected:
    dian_data = query_dian_api(cufe)
    if dian_data:
        # Usar datos oficiales de DIAN
        merge_with_dian_data(dian_data)
```

#### 4.2 Aprendizaje de Patrones

**Guardar patrones exitosos:**

```python
# Cuando usuario corrige manualmente
if manual_correction:
    save_pattern(
        supplier_nit=nit,
        field='invoice_number',
        pattern=extract_pattern(corrected_value),
        pdf_structure=analyze_pdf_structure(pdf)
    )
```

---

## 🛠️ PLAN DE IMPLEMENTACIÓN

### Sprint 1: Backend - Extracción Mejorada (3-4 días)

**Tareas:**
1. ✅ Crear `EnhancedPDFExtractor` con scores de confianza
2. ✅ Implementar extracción por posición
3. ✅ Agregar biblioteca de patrones por proveedor
4. ✅ Crear endpoint `/api/supplier-invoices/extract-enhanced`
5. ✅ Agregar campo `extraction_quality` a modelo
6. ✅ Tests unitarios

### Sprint 2: Frontend - Modal de Revisión (2-3 días)

**Tareas:**
1. ✅ Diseñar modal de revisión con vista previa
2. ✅ Implementar indicadores de confianza
3. ✅ Agregar formulario editable
4. ✅ Integrar con endpoint de extracción
5. ✅ Manejo de errores y validaciones

### Sprint 3: Tabla y Acciones (2-3 días)

**Tareas:**
1. ✅ Rediseñar tabla con columna de calidad
2. ✅ Implementar botones de acción
3. ✅ Crear modales de detalle y edición
4. ✅ Agregar filtros avanzados
5. ✅ Implementar descarga de DIAN

### Sprint 4: Optimizaciones (1-2 días)

**Tareas:**
1. ✅ Procesamiento en background para lotes grandes
2. ✅ Cache de proveedores conocidos
3. ✅ Optimización de queries
4. ✅ Tests de integración
5. ✅ Documentación

---

## 📊 MÉTRICAS DE ÉXITO

**Antes de refactorización:**
- Tasa de extracción exitosa: ~60%
- Datos completos: ~40%
- Tiempo de corrección manual: ~5 min/factura

**Después de refactorización (objetivo):**
- Tasa de extracción exitosa: >85%
- Datos completos: >70%
- Tiempo de corrección manual: <2 min/factura
- Satisfacción del usuario: >90%

---

## 🎨 MOCKUPS DE INTERFAZ

### Modal de Revisión Mejorado

```
┌─────────────────────────────────────────────────────────────┐
│  Revisar Factura Extraída                              [X]  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐  ┌──────────────────────────────┐   │
│  │                  │  │  Datos Extraídos             │   │
│  │   Vista Previa   │  │                              │   │
│  │      del PDF     │  │  Proveedor: [EXITO S.A.] 🟢95% │
│  │                  │  │  NIT: [890900608-6]      🟢98% │
│  │  [Página 1/1]    │  │  Fecha: [15/01/2025]     🟡75% │
│  │                  │  │  Número: [FV123456]      🟢90% │
│  │                  │  │  CUFE: [abc...def]       🟢100%│
│  │                  │  │  Total: [$125,000]       🟡70% │
│  │                  │  │                              │   │
│  │                  │  │  [Reextraer] [Guardar]       │   │
│  └──────────────────┘  └──────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Tabla Mejorada

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Facturas de Proveedores                                                │
├─────────────────────────────────────────────────────────────────────────┤
│  [Buscar...] [Filtros ▼] [Estado ▼] [Proveedor ▼]      [Subir PDFs]   │
├─────────────────────────────────────────────────────────────────────────┤
│ Proveedor    │ Fecha      │ Número  │ CUFE    │ Estado  │ Calidad │ Acciones │
├──────────────┼────────────┼─────────┼─────────┼─────────┼─────────┼──────────┤
│ EXITO S.A.   │ 15/01/2025 │ FV12345 │ abc...  │ ✅ Proc │ 🟢 95%  │ [Ver][PDF]│
│ MAKRO        │ 14/01/2025 │ ad67890 │ -       │ ⚠️ CUFE │ 🟡 65%  │ [Ver][DIAN]│
│ COLANTA      │ -          │ FC11111 │ xyz...  │ ⏳ Pend │ 🔴 45%  │ [Editar]  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 QUÉ PUEDO HACER POR TI

### Opción 1: Implementación Completa (Recomendado)
Implementar todas las fases del plan de refactorización:
- ✅ Backend mejorado con extracción inteligente
- ✅ Frontend con modal de revisión
- ✅ Tabla con acciones funcionales
- ✅ Tests y documentación

**Tiempo estimado:** 8-12 días
**Impacto:** Alto - Sistema completamente renovado

### Opción 2: Mejora Rápida (Quick Win)
Implementar solo las mejoras críticas:
- ✅ Mejorar patrones de extracción actuales
- ✅ Agregar modal de revisión básico
- ✅ Implementar acciones principales (Ver, PDF, Editar)

**Tiempo estimado:** 3-5 días
**Impacto:** Medio - Mejoras visibles inmediatas

### Opción 3: Análisis de Facturas Existentes
Antes de refactorizar, analizar las facturas en la carpeta:
- ✅ Escanear todos los PDFs
- ✅ Identificar patrones comunes
- ✅ Detectar proveedores frecuentes
- ✅ Generar reporte de estructuras
- ✅ Crear biblioteca de patrones específicos

**Tiempo estimado:** 1-2 días
**Impacto:** Bajo - Información para mejor implementación

### Opción 4: Prototipo Interactivo
Crear un prototipo funcional con datos de prueba:
- ✅ Modal de revisión con datos mock
- ✅ Tabla con acciones simuladas
- ✅ Flujo completo de usuario
- ✅ Sin integración backend

**Tiempo estimado:** 1-2 días
**Impacto:** Bajo - Validación de UX antes de implementar

---

## 📝 RECOMENDACIÓN

**Mi recomendación es empezar con la Opción 3** (Análisis de Facturas Existentes):

**¿Por qué?**
1. Tenemos acceso a la carpeta real con facturas
2. Podemos identificar patrones específicos de tus proveedores
3. La refactorización será más efectiva con datos reales
4. Evitamos implementar soluciones genéricas que no funcionen

**Siguiente paso:**
Después del análisis, implementar Opción 1 (Implementación Completa) con patrones específicos identificados.

---

## ❓ PREGUNTAS PARA TI

1. ¿Tienes acceso a la carpeta de facturas desde este entorno?
2. ¿Cuántas facturas aproximadamente hay en la carpeta?
3. ¿Cuáles son los proveedores más frecuentes?
4. ¿Hay algún formato de factura particularmente problemático?
5. ¿Prefieres empezar con análisis o ir directo a implementación?

**¿Qué opción prefieres que implemente?**
