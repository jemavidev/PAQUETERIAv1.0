# 📊 Resumen: Plan de Extracción de Productos del TAB

## 🎯 ¿Qué quieres lograr?

Mostrar en el **TAB de PRODUCTOS** todos los datos que se extraen de los archivos CUFE de la DIAN, sin dañar lo que ya funciona en los tabs FACTURAS y CUFE.

---

## ✅ Lo que YA funciona

1. **TAB FACTURAS**: Carga PDFs de proveedores, extrae datos básicos
2. **TAB CUFE**: Asocia archivos DIAN, extrae TODOS los datos (emisor, adquiriente, totales, **productos**)
3. **TAB PRODUCTOS**: Vista HTML lista, endpoint API funcionando, modelo de BD completo

---

## ❌ El problema

Los productos **SÍ se extraen** del archivo DIAN y **SÍ se guardan** en la base de datos, pero:
- La vista actual no los muestra correctamente
- Faltan columnas importantes (U/M, IVA%, Subtotal)
- El endpoint no retorna paginación completa
- Falta visualización de datos de trazabilidad

---

## 🔍 ¿Qué datos se extraen del CUFE?

Cuando cargas un archivo DIAN en el TAB CUFE, el sistema extrae:

```python
{
    'codigo_producto': '7706616340433',        # EAN/UPC
    'descripcion': 'BANDERITAS ADH 5X20H...',  # Descripción completa
    'cantidad': 6.0,                           # Cantidad comprada
    'unidad_medida': 'NIU',                    # Unidad (NIU, PK, BX, etc.)
    'precio_unitario': 1600.0,                 # Precio por unidad
    'iva_porcentaje': 19.0,                    # % de IVA
    'total_item': 8067.0,                      # Total de la línea
    
    # Trazabilidad (calculada automáticamente)
    'precio_anterior': 1520.0,                 # Última compra
    'variacion_precio': 5.26,                  # % de cambio
    'variacion_tipo': 'subio',                 # subio/bajo/igual
    'precio_promedio': 1580.0,                 # Promedio histórico
    'total_compras_producto': 12,              # Veces comprado
    'ultimo_proveedor': 'PAPELERIA X',         # Proveedor anterior
}
```

---

## 🚀 Plan de Acción (3 Fases)

### FASE 1: Diagnóstico (30 min) ⏱️

**Objetivo**: Verificar que todo funciona correctamente

**Acción**:
```bash
cd CODE
python3 test_productos_diagnostico.py
```

**Qué verifica**:
- ✅ Productos se extraen del PDF DIAN
- ✅ Productos se guardan en BD
- ✅ Campos de trazabilidad se calculan
- ✅ Datos están completos

---

### FASE 2: Mejoras Básicas (2 horas) ⏱️

**Objetivo**: Mostrar TODOS los datos extraídos

**Cambios necesarios**:

1. **Actualizar endpoint API** (`invoices_v2_routes.py`):
   - Retornar paginación completa (total, páginas)
   - Incluir todos los campos de trazabilidad

2. **Mejorar tabla HTML** (`productos.html`):
   - Agregar columnas: U/M, IVA%, Subtotal
   - Mejorar visualización (tooltips, badges)
   - Agregar filtros: IVA%, U/M, rango de precios

3. **Mejorar modal de historial**:
   - Gráfica de evolución de precios
   - Tabla comparativa de proveedores
   - Estadísticas detalladas

**Resultado esperado**:
```
┌──────────┬─────────────────┬────────┬─────┬────────┬─────┬──────┬──────────┬──────────┬──────────┐
│ Código   │ Descripción     │ Cant.  │ U/M │ Precio │ IVA │ Sub  │ Total    │ Variación│ Compras  │
├──────────┼─────────────────┼────────┼─────┼────────┼─────┼──────┼──────────┼──────────┼──────────┤
│ 77066163 │ BANDERITAS ADH  │ 6.00   │ NIU │ $1,600 │ 19% │$9,600│ $11,424  │ ↑ 5.2%   │ 12x      │
│ 5676     │ PERIODICO TAY   │ 2.00   │ PK  │ $5,520 │ 19% │$11K  │ $13,138  │ → 0.1%   │ 8x       │
└──────────┴─────────────────┴────────┴─────┴────────┴─────┴──────┴──────────┴──────────┴──────────┘
```

---

### FASE 3: Funcionalidades Avanzadas (3 horas) ⏱️

**Objetivo**: Análisis y reportes

**Nuevas funcionalidades**:
1. Exportación CSV/Excel
2. Dashboard de productos (top 10, gráficas)
3. Análisis de precios (alertas, oportunidades)
4. Comparativa de proveedores

---

## 📝 Checklist Rápido

### Para empezar AHORA:

- [ ] Ejecutar diagnóstico: `python3 CODE/test_productos_diagnostico.py`
- [ ] Verificar que hay productos en BD
- [ ] Ir a http://localhost:8000/invoices/productos
- [ ] Verificar qué se muestra actualmente

### Si NO hay productos:

1. Ir al TAB CUFE
2. Seleccionar una factura
3. Cargar archivo PDF de la DIAN
4. Verificar logs: "✅ Extraídos X productos del PDF"
5. Volver al TAB PRODUCTOS y refrescar

### Si SÍ hay productos pero no se ven bien:

1. Revisar endpoint `/api/v2/invoices/productos`
2. Verificar que retorna datos correctos
3. Actualizar vista HTML con columnas faltantes
4. Mejorar visualización de datos

---

## 🔧 Comandos Útiles

### Ver productos en BD:
```bash
cd CODE
python3 -c "
from src.app.database import SessionLocal
from src.app.models.invoice_v2 import InvoiceProductV2
db = SessionLocal()
print(f'Total productos: {db.query(InvoiceProductV2).count()}')
"
```

### Ver últimos productos:
```bash
cd CODE
python3 -c "
from src.app.database import SessionLocal
from src.app.models.invoice_v2 import InvoiceProductV2
db = SessionLocal()
productos = db.query(InvoiceProductV2).order_by(InvoiceProductV2.id.desc()).limit(5).all()
for p in productos:
    print(f'{p.codigo_producto}: {p.descripcion[:40]}... - \${p.precio_unitario}')
"
```

---

## 💡 Mi Análisis

Basándome en el código que revisé:

1. **El parser funciona bien**: El método `_extract_productos()` en `pdf_parser_service.py` extrae correctamente los datos del PDF DIAN

2. **Los datos se guardan**: El método `process_dian_document()` en `invoice_v2_service.py` guarda los productos en BD

3. **La trazabilidad se calcula**: El método `calculate_product_traceability()` calcula variaciones de precio automáticamente

4. **El problema es la visualización**: La vista HTML y el endpoint API necesitan mejoras para mostrar TODOS los datos

---

## 🎯 Recomendación

**Empezar con FASE 1 (Diagnóstico)**:
```bash
cd CODE
python3 test_productos_diagnostico.py
```

Esto te dirá:
- ✅ Cuántos productos hay en BD
- ✅ Si los datos están completos
- ✅ Qué falta por mejorar
- ✅ Próximos pasos específicos

Luego, según los resultados, decidir si:
- Necesitas cargar más archivos DIAN (si no hay productos)
- Necesitas mejorar la visualización (si hay productos pero no se ven bien)
- Necesitas agregar funcionalidades avanzadas (si todo funciona bien)

---

## 📚 Documentos Relacionados

- **Plan completo**: `PLAN_EXTRACCION_PRODUCTOS_TAB.md`
- **Script diagnóstico**: `CODE/test_productos_diagnostico.py`
- **Parser de productos**: `CODE/src/app/services/pdf_parser_service.py` (línea ~597)
- **Servicio de facturas**: `CODE/src/app/services/invoice_v2_service.py`
- **Vista HTML**: `CODE/src/templates/invoices_v2/productos.html`

---

**Creado**: 2026-02-08  
**Estado**: Listo para implementar  
**Tiempo estimado**: 5-6 horas total (3 fases)
