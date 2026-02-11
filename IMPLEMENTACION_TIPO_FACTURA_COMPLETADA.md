# IMPLEMENTACIÓN: Tipo de Factura (Reventa vs Consumo)

## ✅ IMPLEMENTACIÓN COMPLETADA

Se implementó exitosamente el sistema para clasificar facturas y filtrar productos de reventa vs consumo.

---

## 🎯 PROBLEMA RESUELTO

**Necesidad:** Separar productos para reventa de productos/servicios de consumo interno, sin afectar el flujo actual.

**Solución:** Campo `tipo_factura` a nivel de factura con filtro en TAB Productos.

---

## 🔧 CAMBIOS IMPLEMENTADOS

### 1. Base de Datos

#### Nueva Columna
```sql
ALTER TABLE invoices_v2 
ADD COLUMN tipo_factura VARCHAR(20) DEFAULT 'reventa' NOT NULL;

CREATE INDEX idx_invoices_tipo_factura ON invoices_v2(tipo_factura);
```

#### Valores Permitidos
- `reventa` - Productos para revender (DEFAULT)
- `consumo` - Consumo interno (oficina, operaciones)
- `servicio` - Servicios contratados
- `otro` - Otros tipos

---

### 2. Modelo (Python)

**Archivo:** `CODE/src/app/models/invoice_v2.py`

```python
class InvoiceV2(Base):
    # ... campos existentes ...
    
    # Tipo de factura (para filtrar productos de reventa vs consumo)
    tipo_factura = Column(String(20), default='reventa', nullable=False, index=True)
    # Tipos: reventa, consumo, servicio, otro
```

---

### 3. API Backend

**Archivo:** `CODE/src/app/routes/invoices_v2_routes.py`

#### Endpoint de Productos con Filtro
```python
@router.get("/productos")
def list_products(
    tipo_factura: Optional[str] = Query('reventa'),  # ← NUEVO
    ...
):
    # Filtrar por tipo de factura
    if tipo_factura and tipo_factura != 'all':
        query = query.filter(InvoiceV2.tipo_factura == tipo_factura)
```

#### Schema Actualizado
```python
class InvoiceResponse(BaseModel):
    # ... campos existentes ...
    tipo_factura: Optional[str] = 'reventa'  # ← NUEVO
```

---

### 4. Frontend - TAB Productos

**Archivo:** `CODE/src/templates/invoices_v2/productos.html`

#### Filtro Visual
```html
<select id="tipo-factura-filter" onchange="loadProducts()">
    <option value="reventa" selected>Solo reventa</option>
    <option value="consumo">Solo consumo</option>
    <option value="servicio">Solo servicios</option>
    <option value="all">Todos los tipos</option>
</select>
```

#### JavaScript
```javascript
const params = new URLSearchParams({
    search: document.getElementById('search').value || '',
    tipo_factura: document.getElementById('tipo-factura-filter').value || 'reventa',
    skip: skip,
    limit: itemsPerPage
});
```

---

### 5. Frontend - TAB Facturas

**Archivo:** `CODE/src/templates/invoices_v2/facturas.html`

#### Campo en Modal de Edición
```html
<div>
    <label>Tipo de Factura</label>
    <select id="edit-tipo-factura">
        <option value="reventa">Productos para reventa</option>
        <option value="consumo">Consumo interno</option>
        <option value="servicio">Servicios</option>
        <option value="otro">Otro</option>
    </select>
</div>
```

---

## 📊 FLUJO DE USO

### Escenario 1: Clasificar Factura Nueva

1. Usuario carga factura de proveedor
2. Sistema asigna `tipo_factura = 'reventa'` por defecto
3. Usuario puede cambiar el tipo si es necesario

### Escenario 2: Reclasificar Factura Existente

1. Usuario va al TAB FACTURAS
2. Click en "Editar" (ícono de lápiz)
3. Cambia el campo "Tipo de Factura"
4. Guarda cambios
5. Los productos de esa factura ahora se filtran según el nuevo tipo

### Escenario 3: Ver Solo Productos de Reventa

1. Usuario va al TAB PRODUCTOS
2. Por defecto ve solo productos de facturas tipo "reventa"
3. Puede cambiar el filtro a "consumo", "servicios" o "todos"

---

## 🎨 INTERFAZ VISUAL

### TAB Productos - Filtro

```
┌────────────────────────────────────────────────────────┐
│ TAB PRODUCTOS                                          │
├────────────────────────────────────────────────────────┤
│ [Búsqueda...] [🔽 Solo reventa ▼]                     │
│                                                        │
│ Opciones del filtro:                                   │
│ • Solo reventa      ← Muestra solo productos reventa  │
│ • Solo consumo      ← Muestra solo consumo interno    │
│ • Solo servicios    ← Muestra solo servicios          │
│ • Todos los tipos   ← Muestra todo                    │
│                                                        │
│ Total: 150 productos (de 200 totales)                 │
└────────────────────────────────────────────────────────┘
```

### TAB Facturas - Modal de Edición

```
┌────────────────────────────────────────────────────────┐
│ Editar Factura                                         │
├────────────────────────────────────────────────────────┤
│ Proveedor: [DISTRIBUIDORA ABC S.A.]                   │
│ NIT: [900123456-7]                                     │
│ Número: [FAC-001]                                      │
│ Fecha: [2026-02-11 09:00]                             │
│ Total: [1500000]                                       │
│ Estado: [Completo ▼]                                   │
│                                                        │
│ Tipo de Factura: [Productos para reventa ▼]           │
│                  • Productos para reventa              │
│                  • Consumo interno                     │
│                  • Servicios                           │
│                  • Otro                                │
│                                                        │
│ Notas: [...]                                           │
│                                                        │
│ [Cancelar] [Guardar Cambios]                          │
└────────────────────────────────────────────────────────┘
```

---

## 🚀 CÓMO APLICAR LA MIGRACIÓN

### Opción 1: SQL Manual (Recomendado)

```bash
# Conectar a la base de datos
psql -U usuario -d nombre_bd

# Ejecutar el script
\i CODE/add_tipo_factura_field.sql
```

### Opción 2: Alembic (Si lo usan)

```bash
cd CODE
alembic upgrade head
```

### Opción 3: Desde Python

```python
from CODE.src.app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("""
        ALTER TABLE invoices_v2 
        ADD COLUMN IF NOT EXISTS tipo_factura VARCHAR(20) DEFAULT 'reventa' NOT NULL
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_invoices_tipo_factura 
        ON invoices_v2(tipo_factura)
    """))
    conn.commit()
```

---

## 📝 CASOS DE USO

### Caso 1: Proveedor de Productos para Reventa

```
Proveedor: DISTRIBUIDORA ABC S.A.
Factura: FAC-001
Productos: 50 items (arroz, aceite, café, etc.)
Tipo: reventa ✅

Resultado: Aparecen en TAB PRODUCTOS con filtro "Solo reventa"
```

### Caso 2: Proveedor de Servicios

```
Proveedor: SERVICIOS CONTABLES XYZ
Factura: FAC-002
Productos: 1 item (Servicio de contabilidad)
Tipo: servicio ✅

Resultado: NO aparecen en TAB PRODUCTOS con filtro "Solo reventa"
```

### Caso 3: Compra de Consumo Interno

```
Proveedor: PAPELERÍA LA OFICINA
Factura: FAC-003
Productos: 10 items (papel, lapiceros, folders)
Tipo: consumo ✅

Resultado: NO aparecen en TAB PRODUCTOS con filtro "Solo reventa"
```

---

## 🔍 VERIFICACIÓN

### 1. Verificar que la columna existe

```sql
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'invoices_v2' 
AND column_name = 'tipo_factura';
```

**Resultado esperado:**
```
column_name  | data_type         | column_default
-------------+-------------------+----------------
tipo_factura | character varying | 'reventa'
```

### 2. Verificar distribución de tipos

```sql
SELECT 
    tipo_factura,
    COUNT(*) as total_facturas,
    SUM((SELECT COUNT(*) FROM invoice_products_v2 WHERE cufe = invoices_v2.cufe)) as total_productos
FROM invoices_v2
GROUP BY tipo_factura
ORDER BY total_facturas DESC;
```

### 3. Probar filtro en API

```bash
# Solo reventa (default)
curl "http://localhost:8000/api/v2/invoices/productos?limit=10"

# Solo consumo
curl "http://localhost:8000/api/v2/invoices/productos?tipo_factura=consumo&limit=10"

# Todos
curl "http://localhost:8000/api/v2/invoices/productos?tipo_factura=all&limit=10"
```

---

## ⚠️ NOTAS IMPORTANTES

### Facturas Existentes

- ✅ Todas las facturas existentes quedan como `tipo_factura = 'reventa'` por defecto
- ✅ Puedes reclasificarlas manualmente desde el TAB FACTURAS
- ✅ No se pierden datos ni se afecta el flujo actual

### Compatibilidad

- ✅ Compatible con facturas antiguas
- ✅ No requiere reprocesar productos
- ✅ El filtro es opcional (puede ver "todos")

### Performance

- ✅ Índice creado para búsquedas rápidas
- ✅ No afecta velocidad de carga
- ✅ Filtro se aplica a nivel de query SQL

---

## 📁 ARCHIVOS MODIFICADOS

1. **Migración:**
   - `CODE/alembic/versions/20260211_092552_add_tipo_factura.py`
   - `CODE/add_tipo_factura_field.sql`

2. **Backend:**
   - `CODE/src/app/models/invoice_v2.py`
   - `CODE/src/app/routes/invoices_v2_routes.py`

3. **Frontend:**
   - `CODE/src/templates/invoices_v2/productos.html`
   - `CODE/src/templates/invoices_v2/facturas.html`

4. **Documentación:**
   - `IMPLEMENTACION_TIPO_FACTURA_COMPLETADA.md` (este archivo)

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

- [x] Migración de base de datos creada
- [x] Modelo actualizado con nuevo campo
- [x] API backend con filtro implementado
- [x] Frontend TAB Productos con selector
- [x] Frontend TAB Facturas con campo editable
- [x] Índice para performance
- [x] Valores por defecto configurados
- [x] Documentación completa
- [x] Scripts SQL para aplicar cambios
- [x] Sin afectar flujo actual

---

## 🎉 RESULTADO FINAL

**IMPLEMENTACIÓN COMPLETADA Y LISTA PARA USAR**

Ahora puedes:
1. ✅ Clasificar facturas como reventa, consumo, servicio u otro
2. ✅ Filtrar productos en el TAB PRODUCTOS por tipo
3. ✅ Ver solo productos de reventa (por defecto)
4. ✅ Reclasificar facturas existentes manualmente
5. ✅ Mantener el flujo actual sin cambios

**Próximo paso:** Aplicar la migración SQL y probar el sistema.
