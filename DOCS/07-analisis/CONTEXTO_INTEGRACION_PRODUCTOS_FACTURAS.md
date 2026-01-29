# 📋 Contexto de Integración: Productos y Facturas

**Fecha de creación:** 2026-01-13  
**Propósito:** Documentar el estado actual de los sistemas de Productos y Facturas para su futura integración  
**Estado:** Ambos sistemas operativos, pendiente integración

---

## 🎯 Objetivo de la Integración

Conectar el sistema de **Gestión de Productos** (sincronizado desde DynamiaERP) con el sistema de **Facturas CUFE** (importadas desde PDFs) para:

1. Vincular productos de facturas con el catálogo de DynamiaERP
2. Enriquecer datos de productos con información de compras
3. Análisis de precios y proveedores
4. Detección de discrepancias entre facturas y catálogo
5. Gestión unificada de inventario y compras

---

## 📦 Sistema 1: Gestión de Productos

### Estado Actual
- **Progreso:** 60% completado (funcionalidad core completa)
- **Estado:** ✅ Operativo y listo para producción
- **Última actualización:** 2026-01-13

### Arquitectura

#### Base de Datos
**Tablas:**
- `products` - 60+ campos sincronizados desde DynamiaERP
- `product_column_config` - Configuración de columnas por usuario
- `product_sync_log` - Historial de sincronizaciones

**Campos clave para integración:**
- `codigo` - Código único del producto
- `referencia` - Referencia alternativa
- `nombre` - Nombre del producto
- `codigo_barra` - Código de barras
- `precio_venta` - Precio de venta actual
- `costo_aproximado` - Costo aproximado
- `existencias_totales` - Stock actual
- `tipo_nombre`, `marca_nombre`, `linea_nombre` - Clasificación

#### Archivos Principales
```
CODE/src/app/models/product.py              # 3 modelos
CODE/src/app/services/product_sync_service.py  # Sincronización DynamiaERP
CODE/src/app/routes/products.py             # 7 endpoints API
CODE/src/templates/products/list.html       # Vista principal
CODE/src/app/routes/protected.py            # Ruta /products
```

#### Endpoints API
```
GET  /api/products                    # Listar con filtros
GET  /api/products/{id}               # Ver detalle
POST /api/products/sync               # Sincronizar desde DynamiaERP
GET  /api/products/search/advanced    # Búsqueda avanzada
GET  /api/products/sync/history       # Historial
GET  /api/products/columns/config     # Configuración columnas
POST /api/products/columns/config     # Guardar configuración
```

#### Funcionalidades
- ✅ Sincronización desde DynamiaERP
- ✅ Búsqueda con índice de texto completo
- ✅ Filtros múltiples (estado, vendible, destacado)
- ✅ Paginación (50 productos por página)
- ✅ Configuración de columnas personalizable
- ✅ Formateo automático de valores
- ✅ Historial de sincronizaciones

#### Limitaciones Actuales
- Solo lectura (no hay edición de productos)
- Sincronización completa (no incremental)
- No hay exportación/importación CSV
- No hay vista de detalle individual
- **No hay vínculo con facturas de compra**

### Documentación
- `CODE/docs/COMO_RETOMAR_CONTEXTO.md` - Guía para retomar trabajo
- `CODE/docs/PRODUCTOS_IMPLEMENTACION_COMPLETADA.md` - Estado de implementación
- `CODE/docs/PRODUCTOS_GUIA_USO.md` - Guía de uso
- `CODE/INSTRUCCIONES_PRODUCTOS.md` - Instrucciones de activación

---

## 📄 Sistema 2: Gestión de Facturas CUFE

### Estado Actual
- **Progreso:** 95% completado (sistema funcional en producción)
- **Estado:** ✅ Operativo y completo
- **Última actualización:** 2026-01-13

### Arquitectura

#### Base de Datos
**Tablas:**
- `suppliers` - Proveedores
- `invoices` - Facturas/Documentos (CUFE/CUDE)
- `invoice_items` - Items/Productos de facturas
- `invoice_irregularities` - Irregularidades detectadas
- `invoice_rejected_files` - Archivos rechazados

**Campos clave para integración:**
- `invoice_items.codigo` - Código del producto (puede estar vacío)
- `invoice_items.descripcion` - Descripción del producto
- `invoice_items.precio_unitario` - Precio de compra
- `invoice_items.cantidad` - Cantidad comprada
- `invoice_items.iva_porcentaje` - IVA aplicado
- `invoice_items.iva_incluido` - Si IVA está incluido
- `invoices.supplier_id` - Proveedor
- `invoices.fecha_emision` - Fecha de compra

#### Archivos Principales
```
CODE/src/app/models/invoice.py              # 5 modelos
CODE/src/app/services/invoice_service.py    # Lógica de negocio
CODE/src/app/services/pdf_extractor_service.py  # Extracción PDFs
CODE/src/app/routes/invoices.py             # 30+ endpoints API
CODE/src/templates/invoices/                # 7 vistas HTML
```

#### Endpoints API (30+)
**Vistas:**
```
GET /invoices                         # Dashboard
GET /invoices/upload                  # Carga de PDFs
GET /invoices/list                    # Lista con filtros
GET /invoices/detail/{id}             # Detalle
GET /invoices/irregularities          # Irregularidades
GET /invoices/rejected                # Archivos rechazados
GET /invoices/products                # Búsqueda global productos
```

**CRUD:**
```
POST   /invoices/api/extract          # Extraer PDF
POST   /invoices/api/save             # Guardar factura
DELETE /invoices/api/{id}             # Eliminar
POST   /invoices/api/{id}/restore     # Restaurar
```

**Análisis:**
```
GET /invoices/api/search              # Búsqueda avanzada
GET /invoices/api/product/{codigo}    # Info producto
GET /invoices/api/supplier/{nit}      # Resumen proveedor
GET /invoices/api/search/products     # Búsqueda global
```

**Exportación:**
```
POST /invoices/api/export             # Exportar CSV
```

**Re-procesamiento:**
```
POST /invoices/api/{id}/reprocess           # Re-procesar una
POST /invoices/api/reprocess-all-errors     # Re-procesar todas
```

#### Funcionalidades
- ✅ Extracción automática de PDFs
- ✅ Detección de 11 tipos de irregularidades
- ✅ Gestión de duplicados (CUFE y hash)
- ✅ Sistema de reemplazo de facturas
- ✅ Búsqueda y filtros avanzados
- ✅ Análisis de productos y proveedores
- ✅ Exportación CSV personalizable
- ✅ Re-procesamiento de errores
- ✅ Gestión de IVA (incluido/no incluido)

#### Limitaciones Actuales
- **No hay vínculo automático con catálogo de productos**
- Extracción de código de producto puede fallar
- No hay validación contra catálogo DynamiaERP
- No actualiza existencias de productos

### Documentación
- `CODE/RESUMEN_FIX_IVA.md` - Fix de validación de IVA

---

## 🔗 Puntos de Integración Identificados

### 1. Vinculación de Productos

**Problema actual:**
- Los items de facturas tienen `codigo` que puede estar vacío o ser incorrecto
- No hay validación contra el catálogo de productos
- No se puede saber si un producto de factura existe en DynamiaERP

**Solución propuesta:**
```python
# Vincular invoice_items con products
# Estrategias de matching:
# 1. Por código exacto
# 2. Por código de barras
# 3. Por referencia
# 4. Por similitud de descripción (fuzzy matching)
# 5. Manual por usuario
```

**Campos a agregar:**
```sql
ALTER TABLE invoice_items 
ADD COLUMN product_id INTEGER REFERENCES products(id),
ADD COLUMN match_confidence DECIMAL(3,2),  -- 0.00 a 1.00
ADD COLUMN match_method VARCHAR(50),       -- 'codigo', 'barcode', 'fuzzy', 'manual'
ADD COLUMN needs_review BOOLEAN DEFAULT FALSE;

CREATE INDEX idx_invoice_items_product_id ON invoice_items(product_id);
CREATE INDEX idx_invoice_items_needs_review ON invoice_items(needs_review);
```

### 2. Análisis de Precios

**Funcionalidad:**
- Comparar precio de compra (factura) vs precio de venta (catálogo)
- Calcular margen de ganancia
- Detectar anomalías de precios
- Historial de precios de compra por proveedor

**Endpoints nuevos:**
```
GET /api/products/{id}/purchase-history    # Historial de compras
GET /api/products/{id}/price-analysis      # Análisis de precios
GET /api/products/{id}/suppliers           # Proveedores del producto
GET /api/analysis/margins                  # Análisis de márgenes
GET /api/analysis/price-anomalies          # Anomalías de precios
```

### 3. Gestión de Proveedores

**Funcionalidad:**
- Ver qué productos compra de cada proveedor
- Comparar precios entre proveedores
- Productos más comprados por proveedor
- Análisis de gasto por proveedor

**Endpoints nuevos:**
```
GET /api/suppliers/{nit}/products          # Productos del proveedor
GET /api/suppliers/{nit}/price-comparison  # Comparación de precios
GET /api/suppliers/ranking                 # Ranking de proveedores
```

### 4. Detección de Discrepancias

**Tipos de discrepancias:**
- Producto en factura no existe en catálogo
- Código de producto incorrecto
- Descripción no coincide
- Precio de compra > precio de venta (alerta)
- Producto inactivo pero se sigue comprando

**Nueva tabla:**
```sql
CREATE TABLE product_invoice_discrepancies (
    id SERIAL PRIMARY KEY,
    invoice_item_id INTEGER REFERENCES invoice_items(id),
    product_id INTEGER REFERENCES products(id),
    discrepancy_type VARCHAR(50),  -- 'not_found', 'price_alert', 'inactive', etc.
    severity VARCHAR(20),           -- 'info', 'warning', 'error'
    description TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_by INTEGER REFERENCES users(id),
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 5. Dashboard Unificado

**Métricas combinadas:**
- Total de productos en catálogo
- Total de productos comprados (facturas)
- Productos sin vincular
- Productos con alertas de precio
- Proveedores activos
- Gasto total por categoría de producto
- Margen promedio por línea/tipo

**Vista nueva:**
```
GET /analysis/dashboard                    # Dashboard unificado
```

### 6. Sincronización Bidireccional

**Flujo:**
1. Usuario importa factura PDF
2. Sistema extrae items
3. Sistema intenta vincular con productos del catálogo
4. Si no encuentra match, sugiere productos similares
5. Usuario confirma o corrige vinculación
6. Sistema guarda vinculación para futuras facturas

**Endpoints:**
```
POST /api/invoice-items/{id}/link-product     # Vincular manualmente
GET  /api/invoice-items/{id}/suggest-products # Sugerir productos
POST /api/invoice-items/bulk-link             # Vinculación masiva
```

---

## 📊 Tablas de Mapeo

### Campos Comunes

| Campo Factura | Campo Producto | Tipo Match |
|---------------|----------------|------------|
| `invoice_items.codigo` | `products.codigo` | Exacto |
| `invoice_items.codigo` | `products.codigo_barra` | Exacto |
| `invoice_items.codigo` | `products.referencia` | Exacto |
| `invoice_items.descripcion` | `products.nombre` | Fuzzy |
| `invoice_items.descripcion` | `products.descripcion` | Fuzzy |

### Análisis de Precios

| Métrica | Cálculo |
|---------|---------|
| Precio Compra | `invoice_items.precio_unitario` |
| Precio Venta | `products.precio_venta` |
| Costo Catálogo | `products.costo_aproximado` |
| Margen Bruto | `(precio_venta - precio_compra) / precio_venta * 100` |
| Diferencia Costo | `precio_compra - costo_aproximado` |

---

## 🚀 Plan de Integración Sugerido

### Fase 1: Vinculación Básica (1-2 días)
- [ ] Agregar campos de vinculación a `invoice_items`
- [ ] Crear servicio de matching de productos
- [ ] Implementar matching por código exacto
- [ ] Crear endpoint de vinculación manual
- [ ] Agregar indicador visual en detalle de factura

### Fase 2: Matching Inteligente (2-3 días)
- [ ] Implementar fuzzy matching por descripción
- [ ] Sistema de sugerencias de productos
- [ ] Interfaz de revisión de vinculaciones
- [ ] Vinculación masiva
- [ ] Aprendizaje de vinculaciones previas

### Fase 3: Análisis de Precios (2-3 días)
- [ ] Endpoint de historial de compras por producto
- [ ] Análisis de márgenes
- [ ] Detección de anomalías de precios
- [ ] Comparación entre proveedores
- [ ] Gráficos de evolución de precios

### Fase 4: Dashboard Unificado (2-3 días)
- [ ] Vista combinada de productos y facturas
- [ ] Métricas de integración
- [ ] Alertas de discrepancias
- [ ] Reportes de análisis
- [ ] Exportación de datos combinados

### Fase 5: Detección de Discrepancias (1-2 días)
- [ ] Tabla de discrepancias
- [ ] Detección automática
- [ ] Sistema de resolución
- [ ] Alertas y notificaciones

### Fase 6: Optimizaciones (1-2 días)
- [ ] Índices de base de datos
- [ ] Cache de vinculaciones
- [ ] Procesamiento en background
- [ ] Tests de integración

**Tiempo total estimado:** 10-15 días

---

## 🔧 Consideraciones Técnicas

### Performance
- Usar índices en campos de búsqueda
- Cache de vinculaciones frecuentes
- Procesamiento asíncrono para matching masivo
- Paginación en listados combinados

### Seguridad
- Validar permisos en endpoints de vinculación
- Auditoría de cambios en vinculaciones
- Logs de matching automático

### UX
- Indicadores visuales de estado de vinculación
- Sugerencias en tiempo real
- Confirmación de vinculaciones masivas
- Feedback de progreso en operaciones largas

### Datos
- Backup antes de vinculaciones masivas
- Reversión de vinculaciones incorrectas
- Historial de cambios
- Validación de integridad referencial

---

## 📝 Notas Importantes

### Productos
- Solo usuarios ADMIN pueden sincronizar productos
- Sincronización es completa (no incremental)
- Configuración de columnas es por usuario
- Búsqueda usa índice de texto completo en PostgreSQL

### Facturas
- Extracción de PDF puede fallar en formatos no estándar
- Sistema detecta automáticamente IVA incluido/no incluido
- Duplicados se detectan por CUFE y hash de archivo
- Re-procesamiento disponible para corregir errores

### Integración
- Matching automático puede tener falsos positivos
- Requiere revisión manual inicial
- Aprendizaje mejora con el tiempo
- Importante mantener catálogo actualizado

---

## 🎯 Métricas de Éxito

### Vinculación
- [ ] >90% de items vinculados automáticamente
- [ ] <5% de vinculaciones incorrectas
- [ ] Tiempo de vinculación <2 segundos por item

### Análisis
- [ ] Detección de 100% de anomalías de precio
- [ ] Cálculo de márgenes en tiempo real
- [ ] Historial completo de compras por producto

### UX
- [ ] Interfaz intuitiva de vinculación
- [ ] Feedback claro de estado
- [ ] Proceso de revisión eficiente

---

## 📚 Referencias

### Archivos de Contexto
- `CODE/docs/COMO_RETOMAR_CONTEXTO.md` - Productos
- `CODE/docs/PRODUCTOS_IMPLEMENTACION_COMPLETADA.md` - Productos
- `CODE/RESUMEN_FIX_IVA.md` - Facturas

### Código Principal
- `CODE/src/app/models/product.py` - Modelos de productos
- `CODE/src/app/models/invoice.py` - Modelos de facturas
- `CODE/src/app/services/product_sync_service.py` - Sincronización
- `CODE/src/app/services/invoice_service.py` - Lógica de facturas
- `CODE/src/app/routes/products.py` - API de productos
- `CODE/src/app/routes/invoices.py` - API de facturas

### Migraciones
- `CODE/alembic/versions/add_products_table.py` - Productos
- `CODE/alembic/versions/create_invoice_tables.py` - Facturas
- `CODE/alembic/versions/enhance_invoice_system.py` - Mejoras facturas

---

## ✅ Checklist Pre-Integración

### Productos
- [x] Migración ejecutada
- [x] Modelos funcionando
- [x] Sincronización operativa
- [x] API completa
- [x] Vista funcional
- [ ] Tests de integración
- [ ] Documentación API

### Facturas
- [x] Migraciones ejecutadas
- [x] Modelos funcionando
- [x] Extracción de PDF operativa
- [x] API completa
- [x] Vistas funcionales
- [x] Sistema de validación
- [ ] Tests de integración
- [ ] Documentación API

### Integración
- [ ] Análisis de campos comunes
- [ ] Diseño de tablas de vinculación
- [ ] Estrategia de matching definida
- [ ] Endpoints planificados
- [ ] Vistas diseñadas
- [ ] Plan de migración de datos
- [ ] Tests planificados

---

**Última actualización:** 2026-01-13  
**Próxima revisión:** Cuando ambos sistemas estén al 100%  
**Responsable:** Equipo de Desarrollo

---

## 🎯 Próximos Pasos

1. **Completar Productos al 100%:**
   - Agregar vista de detalle individual
   - Implementar exportación CSV
   - Agregar tests de integración
   - Documentar API completa

2. **Completar Facturas al 100%:**
   - Agregar tests de integración
   - Documentar API completa
   - Optimizar extracción de PDFs

3. **Iniciar Integración:**
   - Revisar este documento
   - Validar plan de integración
   - Crear branch de integración
   - Comenzar Fase 1

---

**FIN DEL DOCUMENTO**
