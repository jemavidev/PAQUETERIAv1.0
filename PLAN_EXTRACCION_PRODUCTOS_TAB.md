# 📊 PLAN: Extracción de Datos del TAB PRODUCTOS desde Archivos CUFE DIAN

## 🎯 Objetivo
Mostrar en el TAB de PRODUCTOS todos los datos extraídos de los archivos CUFE de la DIAN, sin dañar la funcionalidad existente de los tabs FACTURAS y CUFE.

---

## 📋 Análisis del Sistema Actual

### ✅ Lo que YA funciona:

1. **TAB FACTURAS**: 
   - Carga de PDFs de proveedores
   - Extracción básica de datos (proveedor, fecha, total)
   - Generación de CUFE temporal si no se encuentra
   - Almacenamiento en tabla `invoices_v2`

2. **TAB CUFE**:
   - Asociación de archivos DIAN a facturas existentes
   - Extracción completa de datos DIAN (emisor, adquiriente, totales)
   - Validación y actualización de estado a "completo"
   - Extracción de productos con método `_extract_productos()`

3. **TAB PRODUCTOS** (Parcialmente implementado):
   - Vista HTML con tabla responsive ✅
   - Endpoint API `/api/v2/invoices/productos` ✅
   - Modelo `InvoiceProductV2` con campos de trazabilidad ✅
   - Búsqueda, filtros y paginación ✅
   - Modal de historial de compras ✅

### ❌ Lo que FALTA:

1. **Los productos NO se muestran en la tabla** porque:
   - El parser `_extract_productos()` extrae los datos del PDF DIAN
   - Los productos se guardan en la BD cuando se procesa el archivo DIAN
   - PERO la vista actual no está mostrando los datos correctamente

2. **Campos que se extraen pero no se visualizan bien**:
   - Código de producto (EAN/UPC)
   - Descripción completa
   - Cantidad y unidad de medida
   - Precio unitario
   - IVA porcentaje y valor
   - Subtotal y total del item
   - Datos de trazabilidad (variación de precio, compras anteriores, etc.)

---

## 🔍 Análisis del Parser Actual

### Método `_extract_productos()` en `pdf_parser_service.py`

**Ubicación**: Línea ~597-803

**Formatos soportados**:
1. **CUFE (Factura Electrónica)**: Descripción en múltiples líneas
2. **CUDE (Documento Equivalente POS)**: Formato tabular

**Datos que extrae**:
```python
{
    'codigo_producto': str,      # EAN/UPC o código interno
    'descripcion': str,           # Descripción completa del producto
    'cantidad': float,            # Cantidad comprada
    'unidad_medida': str,         # NIU, PK, BX, UND, etc.
    'precio_unitario': float,     # Precio por unidad
    'iva_porcentaje': float,      # % de IVA (0, 5, 19)
    'total_item': float,          # Total de la línea
}
```

**Estrategias de extracción**:
- Busca sección de productos con múltiples patrones regex
- Detecta líneas con formato: `Nro Código Descripción U/M Cantidad Precio...`
- Maneja descripciones en múltiples líneas
- Calcula totales si no están explícitos
- Límite de 200 productos por factura

---

## 🎯 PLAN DE IMPLEMENTACIÓN

### FASE 1: Verificar Extracción de Productos (DIAGNÓSTICO)

**Objetivo**: Confirmar que los productos se están extrayendo y guardando correctamente

**Acciones**:
1. Revisar logs del servidor cuando se carga un archivo DIAN
2. Verificar que `process_dian_document()` llama a `_extract_productos()`
3. Confirmar que los productos se insertan en `invoice_products_v2`
4. Verificar que los campos de trazabilidad se calculan correctamente

**Script de diagnóstico**:
```bash
# Verificar productos en BD
python3 -c "
from CODE.src.app.database import SessionLocal
from CODE.src.app.models.invoice_v2 import InvoiceProductV2

db = SessionLocal()
count = db.query(InvoiceProductV2).count()
print(f'Total productos en BD: {count}')

# Mostrar últimos 5 productos
productos = db.query(InvoiceProductV2).order_by(InvoiceProductV2.id.desc()).limit(5).all()
for p in productos:
    print(f'- {p.codigo_producto}: {p.descripcion[:50]}... (${p.precio_unitario})')
"
```

---

### FASE 2: Mejorar Visualización en TAB PRODUCTOS

**Objetivo**: Mostrar TODOS los datos extraídos de forma clara y útil

#### 2.1 Actualizar Endpoint API

**Archivo**: `CODE/src/app/routes/invoices_v2_routes.py`

**Cambios necesarios**:

```python
@router.get("/productos", response_model=List[ProductResponse])
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None),
    codigo_producto: Optional[str] = Query(None),
    fecha_desde: Optional[str] = Query(None),
    fecha_hasta: Optional[str] = Query(None),
    proveedor: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    TAB PRODUCTOS: Lista todos los productos con filtros avanzados
    MEJORADO: Retorna paginación completa con total de items
    """
    # ... (código existente)
    
    # AGREGAR: Contar total de productos
    total = query.count()
    
    # AGREGAR: Obtener productos paginados
    productos = query.offset(skip).limit(limit).all()
    
    # Enriquecer con datos de la factura
    result = []
    for prod in productos:
        prod_dict = prod.to_dict()
        prod_dict['proveedor_nombre'] = prod.factura.proveedor_nombre
        prod_dict['numero_factura'] = prod.factura.numero_factura
        result.append(ProductResponse(**prod_dict))
    
    # RETORNAR con paginación
    return {
        'items': result,
        'total': total,
        'page': (skip // limit) + 1,
        'page_size': limit,
        'total_pages': (total + limit - 1) // limit
    }
```

#### 2.2 Actualizar Vista HTML

**Archivo**: `CODE/src/templates/invoices_v2/productos.html`

**Mejoras necesarias**:

1. **Agregar columnas faltantes**:
   - Unidad de medida
   - IVA %
   - Subtotal (sin IVA)
   - Código interno (si existe)

2. **Mejorar visualización de datos**:
   - Tooltip con descripción completa
   - Badge para unidad de medida
   - Indicador visual de IVA (0%, 5%, 19%)
   - Formato de moneda consistente

3. **Agregar filtros adicionales**:
   - Filtro por rango de precios
   - Filtro por IVA %
   - Filtro por unidad de medida
   - Ordenamiento por columnas

**Ejemplo de columnas mejoradas**:
```html
<th>Código</th>
<th>Descripción</th>
<th>Proveedor</th>
<th>Factura</th>
<th>Fecha</th>
<th>Cantidad</th>
<th>U/M</th>          <!-- NUEVO -->
<th>Precio Unit.</th>
<th>IVA %</th>        <!-- NUEVO -->
<th>Subtotal</th>     <!-- NUEVO -->
<th>Total</th>
<th>Variación</th>
<th>Compras</th>
<th>Acciones</th>
```

#### 2.3 Mejorar Modal de Historial

**Mejoras**:
1. Mostrar gráfica de evolución de precios (Chart.js)
2. Tabla comparativa de proveedores
3. Estadísticas detalladas:
   - Precio mínimo/máximo histórico
   - Precio promedio
   - Desviación estándar
   - Frecuencia de compra
   - Mejor proveedor (precio/calidad)

---

### FASE 3: Agregar Funcionalidades Avanzadas

#### 3.1 Exportación de Datos

**Endpoint nuevo**:
```python
@router.get("/productos/export")
async def export_products(
    format: str = Query("csv", regex="^(csv|excel)$"),
    # ... filtros
):
    """
    Exporta productos a CSV o Excel
    """
    # Generar archivo
    # Retornar como descarga
```

#### 3.2 Análisis de Precios

**Endpoint nuevo**:
```python
@router.get("/productos/price-analysis")
async def analyze_prices(
    codigo_producto: Optional[str] = None,
    proveedor: Optional[str] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
):
    """
    Análisis de variación de precios
    - Productos con mayor variación
    - Alertas de precios anormales
    - Oportunidades de ahorro
    """
```

#### 3.3 Dashboard de Productos

**Nueva vista**: `/invoices/productos/dashboard`

**Contenido**:
- Top 10 productos más comprados
- Top 10 con mayor variación de precio
- Gráfica de evolución de precios (últimos 6 meses)
- Alertas de precios anormales
- Comparativa de proveedores

---

## 📝 CHECKLIST DE IMPLEMENTACIÓN

### ✅ Fase 1: Diagnóstico (30 min)
- [ ] Verificar que productos se extraen del PDF DIAN
- [ ] Confirmar que productos se guardan en BD
- [ ] Revisar logs de extracción
- [ ] Contar productos en BD
- [ ] Verificar campos de trazabilidad

### ⏳ Fase 2: Mejoras Básicas (2 horas)
- [ ] Actualizar endpoint `/productos` con paginación completa
- [ ] Agregar columnas faltantes en tabla HTML
- [ ] Mejorar visualización de datos (tooltips, badges)
- [ ] Agregar filtros adicionales (IVA, U/M, rango precios)
- [ ] Implementar ordenamiento por columnas
- [ ] Mejorar modal de historial con gráficas

### ⏳ Fase 3: Funcionalidades Avanzadas (3 horas)
- [ ] Implementar exportación CSV/Excel
- [ ] Crear endpoint de análisis de precios
- [ ] Crear dashboard de productos
- [ ] Agregar alertas de precios anormales
- [ ] Implementar comparativa de proveedores

---

## 🔧 COMANDOS RÁPIDOS

### Verificar productos en BD:
```bash
cd CODE
python3 -c "
from src.app.database import SessionLocal
from src.app.models.invoice_v2 import InvoiceProductV2
db = SessionLocal()
print(f'Total productos: {db.query(InvoiceProductV2).count()}')
"
```

### Ver últimos productos extraídos:
```bash
cd CODE
python3 -c "
from src.app.database import SessionLocal
from src.app.models.invoice_v2 import InvoiceProductV2
db = SessionLocal()
productos = db.query(InvoiceProductV2).order_by(InvoiceProductV2.id.desc()).limit(10).all()
for p in productos:
    print(f'{p.codigo_producto}: {p.descripcion[:40]}... - ${p.precio_unitario} ({p.cantidad} {p.unidad_medida})')
"
```

### Probar extracción de productos de un PDF:
```bash
cd CODE
python3 -c "
from src.app.services.pdf_parser_service import PDFParserService
parser = PDFParserService()
data = parser.parse_dian_document('ruta/al/archivo.pdf')
print(f'Productos extraídos: {len(data.get(\"productos\", []))}')
for p in data.get('productos', [])[:5]:
    print(f'- {p.get(\"codigo_producto\")}: {p.get(\"descripcion\")[:40]}...')
"
```

---

## 🎨 MOCKUP DE MEJORAS VISUALES

### Tabla de Productos Mejorada:

```
┌─────────────┬──────────────────────┬─────────────┬──────────┬────────┬─────────┬─────┬────────────┬──────┬──────────┬──────────┬──────────┬─────────┬─────────┐
│ Código      │ Descripción          │ Proveedor   │ Factura  │ Fecha  │ Cant.   │ U/M │ Precio U.  │ IVA  │ Subtotal │ Total    │ Variación│ Compras │ Acciones│
├─────────────┼──────────────────────┼─────────────┼──────────┼────────┼─────────┼─────┼────────────┼──────┼──────────┼──────────┼──────────┼─────────┼─────────┤
│ 7706616340  │ BANDERITAS ADH 5X... │ PAPELERIA X │ FV-12345 │ 15/01  │ 6.00    │ NIU │ $1,600     │ 19%  │ $9,600   │ $11,424  │ ↑ 5.2%   │ 12x     │ 📊 🗑️  │
│ 5676        │ PERIODICO TAYDEM...  │ PAPELERIA X │ FV-12345 │ 15/01  │ 2.00    │ PK  │ $5,520     │ 19%  │ $11,040  │ $13,138  │ → 0.1%   │ 8x      │ 📊 🗑️  │
│ 8934        │ CINTA TRANSPARENTE...│ PAPELERIA Y │ FV-67890 │ 10/01  │ 12.00   │ NIU │ $2,100     │ 19%  │ $25,200  │ $29,988  │ ↓ 3.8%   │ 15x     │ 📊 🗑️  │
└─────────────┴──────────────────────┴─────────────┴──────────┴────────┴─────────┴─────┴────────────┴──────┴──────────┴──────────┴──────────┴─────────┴─────────┘
```

### Modal de Historial Mejorado:

```
┌────────────────────────────────────────────────────────────────────────────────┐
│ 📊 Historial de Compras - Código: 7706616340433                               │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  📈 Gráfica de Evolución de Precios                                           │
│  ┌──────────────────────────────────────────────────────────────────┐        │
│  │                                                    ●               │        │
│  │                                          ●                         │        │
│  │                                ●                                   │        │
│  │                      ●                                             │        │
│  │            ●                                                       │        │
│  │  ●                                                                 │        │
│  └──────────────────────────────────────────────────────────────────┘        │
│    Ene    Feb    Mar    Abr    May    Jun    Jul    Ago    Sep    Oct        │
│                                                                                │
│  📊 Estadísticas                                                               │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐              │
│  │ Total Compras│ Precio Prom. │ Precio Min.  │ Precio Max.  │              │
│  │     12x      │   $1,580     │   $1,450     │   $1,680     │              │
│  └──────────────┴──────────────┴──────────────┴──────────────┘              │
│                                                                                │
│  📋 Historial Detallado                                                        │
│  ┌────┬────────────┬─────────────────┬────────────┬──────────┬──────────┐  │
│  │ #  │ Fecha      │ Proveedor       │ Precio U.  │ Cantidad │ Variación│  │
│  ├────┼────────────┼─────────────────┼────────────┼──────────┼──────────┤  │
│  │ 12 │ 15/01/2026 │ PAPELERIA X     │ $1,600     │ 6.00     │ ↑ 5.2%   │  │
│  │ 11 │ 28/12/2025 │ PAPELERIA X     │ $1,520     │ 12.00    │ ↓ 2.1%   │  │
│  │ 10 │ 15/12/2025 │ PAPELERIA Y     │ $1,553     │ 6.00     │ ↑ 1.8%   │  │
│  └────┴────────────┴─────────────────┴────────────┴──────────┴──────────┘  │
│                                                                                │
│  [Cerrar]                                                    [Exportar CSV]   │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 PRÓXIMOS PASOS RECOMENDADOS

### Paso 1: Diagnóstico (AHORA)
```bash
# Ejecutar script de diagnóstico
cd CODE
python3 test_productos_diagnostico.py
```

### Paso 2: Mejoras Básicas (SIGUIENTE)
1. Actualizar endpoint `/productos` con paginación completa
2. Agregar columnas faltantes en tabla
3. Mejorar visualización de datos

### Paso 3: Funcionalidades Avanzadas (FUTURO)
1. Exportación CSV/Excel
2. Dashboard de productos
3. Análisis de precios

---

## 📚 DOCUMENTACIÓN RELACIONADA

- `ANALISIS_PARSER_PRODUCTOS.md` - Análisis del parser de productos
- `PRODUCTOS_TRAZABILIDAD_PLAN.md` - Plan de trazabilidad
- `CODE/docs/PRODUCTOS_IMPLEMENTACION_COMPLETADA.md` - Implementación actual
- `CODE/src/app/services/pdf_parser_service.py` - Parser de PDFs
- `CODE/src/app/services/invoice_v2_service.py` - Servicio de facturas
- `CODE/src/app/routes/invoices_v2_routes.py` - Endpoints API
- `CODE/src/templates/invoices_v2/productos.html` - Vista HTML

---

**Creado**: 2026-02-08  
**Estado**: Plan completo listo para implementación  
**Prioridad**: Alta (funcionalidad core del sistema)
